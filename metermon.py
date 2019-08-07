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
RTL_TCP_SERVER    = os.getenv('RTL_TCP_SERVER',"127.0.0.1")
RTLAMR_MSGTYPE    = os.getenv('RTLAMR_MSGTYPE',"scm, scm+")
RTLAMR_FILTERID   = os.getenv('RTLAMR_FILTERID',"")
METERMON_SEND_RAW = os.getenv('METERMON_SEND_RAW',"False")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# set up mqtt client
client = mqtt.Client(client_id=MQTT_CLIENT_ID)
if MQTT_USERNAME and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USERNAME,MQTT_PASSWORD)
client.on_connect = on_connect

# connect to broker
client.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
client.loop_start()
client.publish(MQTT_TOPIC_PREFIX+"/status","Online")

# start RTLAMR
proc = subprocess.Popen(['rtlamr', '-server='+RTL_TCP_SERVER,'-msgtype='+RTLAMR_MSGTYPE, '-filterid='+RTLAMR_FILTERID,'-format=json','-unique=true'],stdout=subprocess.PIPE)

# read output of RTLAMR
while True:
    line = proc.stdout.readline()
    if not line:
        break
    data=json.loads(line)
    msg=json.loads('{"Protocol":"Unknown","Type":"Unknown","ID":"Unknown","Consumption":0,"Unit":"Unknown"}')

    # read data, create json, and publish MQTT message for every meter message received
    # SCM messages
    if data['Type'] == "SCM":
        msg['Protocol'] = "SCM"
        msg['Type'] = str(data['Message']['Type'])
        msg['ID'] = str(data['Message']['ID'])
        if data['Message']['Type'] in (4,5,7,8): # electric meter
            msg['Consumption'] = data['Message']['Consumption'] / 100.0 # convert to kWh
            msg['Unit'] = "kWh"
        elif data['Message']['Type'] in (7,9,12): # gas meter
            msg['Consumption'] = data['Message']['Consumption']
            msg['Unit'] = "ft^3"
    # SCM+ messages
    elif data['Type'] == "SCM+":
        msg['Protocol'] = "SCM+"
        msg['Type'] = str(data['Message']['EndpointType'])
        msg['ID'] = str(data['Message']['EndpointID'])
        if data['Message']['EndpointType'] in (4,5,7,8): # electric meter
            msg['Consumption'] = data['Message']['Consumption'] / 100.0 # convert to kWh
            msg['Unit'] = "kWh"
        elif data['Message']['EndpointType'] in (7,9,12): # gas meter
            msg['Consumption'] = data['Message']['Consumption']
            msg['Unit'] = "ft^3"
    # filter out cases where consumption value is negative        
    if msg['Consumption'] > 0:        
        client.publish(MQTT_TOPIC_PREFIX+"/output",json.dumps(msg)) # publish
        print(json.dumps(msg)) # also print
    # send raw json message if enabled
    if METERMON_SEND_RAW.lower() == "true":
        client.publish(MQTT_TOPIC_PREFIX+"/raw",json.dumps(data)) # publish