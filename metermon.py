#!/usr/bin/python
import os
import sys
import json
import subprocess
import time
import paho.mqtt.client as mqtt

# read in needed env variables
MQTT_BROKER_HOST  = os.getenv('MQTT_BROKER_HOST',"127.0.0.1")
MQTT_BROKER_PORT  = int(os.getenv('MQTT_BROKER_PORT',1883))
MQTT_CLIENT_ID    = os.getenv('MQTT_CLIENT_ID',"metermon")
MQTT_USERNAME     = os.getenv('MQTT_USERNAME',"")
MQTT_PASSWORD     = os.getenv('MQTT_PASSWORD',"")
MQTT_TOPIC_PREFIX = os.getenv('MQTT_TOPIC_PREFIX',"metermon")
RTL_TCP_SERVER    = os.getenv('RTL_TCP_SERVER',"127.0.0.1:1234")
RTLAMR_MSGTYPE    = os.getenv('RTLAMR_MSGTYPE',"all")
RTLAMR_FILTERID   = os.getenv('RTLAMR_FILTERID',"")
METERMON_SEND_RAW = os.getenv('METERMON_SEND_RAW',"False")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # print connection statement
    print(f"Connected to broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT} with result code {rc}: "+mqtt.connack_string(rc))

    # set mqtt status message
    client.publish(MQTT_TOPIC_PREFIX+"/status",payload="Online",qos=1,retain=True)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Unexpected disconnection from broker (RC={rc}). Attempting to reconnect...")

# set up mqtt client
client = mqtt.Client(client_id=MQTT_CLIENT_ID)
if MQTT_USERNAME and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USERNAME,MQTT_PASSWORD)
    print("Username and password set.")
client.will_set(MQTT_TOPIC_PREFIX+"/status", payload="Offline", qos=1, retain=True) # set LWT     
client.on_connect = on_connect # on connect callback
client.on_disconnect = on_disconnect # on disconnect callback

# connect to broker
client.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
client.loop_start()

# start RTLAMR
if RTLAMR_FILTERID:
    proc = subprocess.Popen(['rtlamr', '-server='+RTL_TCP_SERVER,'-msgtype='+RTLAMR_MSGTYPE, '-filterid='+RTLAMR_FILTERID,'-format=json','-unique=true'],stdout=subprocess.PIPE)
else:
    proc = subprocess.Popen(['rtlamr', '-server='+RTL_TCP_SERVER,'-msgtype='+RTLAMR_MSGTYPE, '-format=json','-unique=true'],stdout=subprocess.PIPE)

# read output of RTLAMR
while True:
    line = proc.stdout.readline()
    if not line:
        break
    data=json.loads(line)
    msg=json.loads('{"Protocol":"Unknown","Type":"Unknown","ID":"Unknown","Consumption":0,"Unit":"Unknown"}')

    # read data, create json objects, and publish MQTT message for every meter message received

    # set Protocol
    msg['Protocol'] = data['Type']

    # SCM messages
    if msg['Protocol'] == "SCM":
        msg['ID'] = str(data['Message']['ID'])
        if data['Message']['Type'] in (4,5,7,8): # electric meter
            msg['Type'] = "Electric"
            msg['Consumption'] = data['Message']['Consumption'] / 100.0 # convert to kWh
            msg['Unit'] = "kWh"
        elif data['Message']['Type'] in (2,9,12): # gas meter
            msg['Type'] = "Gas"
            msg['Consumption'] = data['Message']['Consumption']
            msg['Unit'] = "ft^3"
        elif data['Message']['Type'] in (3,11,13): # water meter
            msg['Type'] = "Water"
            msg['Consumption'] = data['Message']['Consumption'] / 10.0 # convert to gal
            msg['Unit'] = "gal"
    # SCM+ messages
    elif msg['Protocol'] == "SCM+":
        msg['ID'] = str(data['Message']['EndpointID'])
        if data['Message']['EndpointType'] in (4,5,7,8): # electric meter
            msg['Type'] = "Electric"
            msg['Consumption'] = data['Message']['Consumption'] / 100.0 # convert to kWh
            msg['Unit'] = "kWh"
        elif data['Message']['EndpointType'] in (2,9,12): # gas meter
            msg['Type'] = "Gas"
            msg['Consumption'] = data['Message']['Consumption']
            msg['Unit'] = "ft^3"
        elif data['Message']['EndpointType'] in (3,11,13): # water meter
            msg['Type'] = "Water"
            msg['Consumption'] = data['Message']['Consumption'] / 10.0 # convert to gal
            msg['Unit'] = "gal"
    # IDM messages
    elif msg['Protocol'] == "IDM":
        msg['Type'] = "Electric"
        msg['ID'] = str(data['Message']['ERTSerialNumber'])
        msg['Consumption'] = data['Message']['LastConsumptionCount'] / 100.0 # convert to kWh
        msg['Unit'] = "kWh"      
    # NetIDM messages
    elif msg['Protocol'] == "NetIDM":
        msg['Type'] = "Electric"
        msg['ID'] = str(data['Message']['ERTSerialNumber'])
        msg['Consumption'] = data['Message']['LastConsumptionNet'] / 100.0 # convert to kWh
        msg['Unit'] = "kWh"
    # R900 messages
    elif msg['Protocol'] == "R900":
        msg['Type'] = "Water"
        msg['ID'] = str(data['Message']['ID'])
        msg['Consumption'] = data['Message']['Consumption'] / 10.0 # convert to gal
        msg['Unit'] = "gal"
    # R900bcd messages
    elif msg['Protocol'] == "R900BCD":
        msg['Type'] = "Water"
        msg['ID'] = str(data['Message']['ID'])
        msg['Consumption'] = data['Message']['Consumption'] / 10.0 # convert to gal
        msg['Unit'] = "gal"
    # filter out cases where consumption value is negative        
    if msg['Consumption'] > 0:        
        client.publish(MQTT_TOPIC_PREFIX+"/output",json.dumps(msg)) # publish
        print(json.dumps(msg)) # also print
    # send raw json message if enabled
    if METERMON_SEND_RAW.lower() == "true":
        client.publish(MQTT_TOPIC_PREFIX+"/raw",json.dumps(data)) # publish