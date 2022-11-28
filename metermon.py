#!/usr/bin/python
import json
import subprocess
import paho.mqtt.client as mqtt
from python_settings import settings

# read in needed env variables
MQTT_BROKER_HOST = settings.MQTT_HOST
MQTT_BROKER_PORT = settings.MQTT_PORT
MQTT_CLIENT_ID = settings.MQTT_CLIENT_ID
MQTT_USERNAME = settings.MQTT_USER
MQTT_PASSWORD = settings.MQTT_PASSWORD
MQTT_TOPIC_PREFIX = settings.MQTT_TOPIC_PREFIX
RTL_TCP_SERVER = settings.RTL_TCP_SERVER
RTLAMR_MSGTYPE = settings.RTLAMR_MSGTYPE
RTLAMR_UNIQUE = settings.RTLAMR_UNIQUE
METERMON_SEND_RAW = settings.METERMON_SEND_RAW
METERMON_SEND_BY_ID = settings.METERMON_SEND_BY_ID
METERMON_ELECTRIC_DIVISOR = settings.METERMON_ELECTRIC_DIVISOR
#METERMON_GAS_DIVISOR = settings.METERMON_GAS_DIVISOR
METERMON_WATER_DIVISOR = settings.METERMON_WATER_DIVISOR
METERS_FILTER = settings.METERS_FILTER
BYPASS_METER_FILTER = settings.BYPASS_METER_FILTER


R900_LOOKUP = {
    "HISTORY": {
        0: "0",
        1: "1-2",
        2: "3-7",
        3: "8-14",
        4: "15-21",
        5: "22-34",
        6: "35+",
    },
    "INTENSITY": {
        0: "None",
        1: "Low",
        2: "High",
    }
}
R900_ATTRIBS = {
    "Leak": "HISTORY",
    "NoUse": "HISTORY",
    "BackFlow": "INTENSITY",
    "LeakNow": "INTENSITY",
}

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
cmdargs = [
    'rtlamr',
    '-format=json',
    f'-server={RTL_TCP_SERVER}',
    f'-msgtype={RTLAMR_MSGTYPE}',
    f'-unique={RTLAMR_UNIQUE}',
]

proc = subprocess.Popen(cmdargs, stdout=subprocess.PIPE)

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
            msg['Consumption'] = data['Message']['Consumption'] / METERMON_ELECTRIC_DIVISOR # convert to kWh
            msg['Unit'] = "kWh"
        elif data['Message']['Type'] in (2,9,12): # gas meter
            msg['Type'] = "Gas"
            msg['Consumption'] = data['Message']['Consumption']
            msg['Unit'] = "ft^3"
        elif data['Message']['Type'] in (3,11,13): # water meter
            msg['Type'] = "Water"
            msg['Consumption'] = data['Message']['Consumption'] / METERMON_WATER_DIVISOR # convert to gal
            msg['Unit'] = "gal"
    # SCM+ messages
    elif msg['Protocol'] == "SCM+":
        msg['ID'] = str(data['Message']['EndpointID'])
        if data['Message']['EndpointType'] in (4,5,7,8): # electric meter
            msg['Type'] = "Electric"
            msg['Consumption'] = data['Message']['Consumption'] / METERMON_ELECTRIC_DIVISOR # convert to kWh
            msg['Unit'] = "kWh"
        elif data['Message']['EndpointType'] in (2,9,12,156,188,220): # gas meter
            msg['Type'] = "Gas"
            msg['Consumption'] = data['Message']['Consumption']
            msg['Unit'] = "ft^3"
        elif data['Message']['EndpointType'] in (3,11,13,171): # water meter
            msg['Type'] = "Water"
            msg['Consumption'] = data['Message']['Consumption'] / METERMON_WATER_DIVISOR # convert to gal
            msg['Unit'] = "gal"
    # IDM messages
    elif msg['Protocol'] == "IDM":
        msg['Type'] = "Electric"
        msg['ID'] = str(data['Message']['ERTSerialNumber'])
        msg['Consumption'] = data['Message']['LastConsumptionCount'] / METERMON_ELECTRIC_DIVISOR # convert to kWh
        msg['Unit'] = "kWh"
    # NetIDM messages
    elif msg['Protocol'] == "NetIDM":
        msg['Type'] = "Electric"
        msg['ID'] = str(data['Message']['ERTSerialNumber'])
        msg['Consumption'] = data['Message']['LastConsumptionNet'] / METERMON_ELECTRIC_DIVISOR # convert to kWh
        msg['Unit'] = "kWh"
    # R900 messages
    elif msg['Protocol'] == "R900":
        msg['Type'] = "Water"
        msg['ID'] = str(data['Message']['ID'])
        msg['Consumption'] = data['Message']['Consumption'] / METERMON_WATER_DIVISOR # convert to gal
        msg['Unit'] = "gal"
        for attr, kind in R900_ATTRIBS.items():
            value = data['Message'].get(attr)
            if value is not None:
                try:
                    msg[attr] = R900_LOOKUP[kind][value]
                except KeyError:
                    print(f"Could not process R900 value ({attr}: {value})")

    # R900bcd messages
    elif msg['Protocol'] == "R900BCD":
        msg['Type'] = "Water"
        msg['ID'] = str(data['Message']['ID'])
        msg['Consumption'] = data['Message']['Consumption'] / METERMON_WATER_DIVISOR # convert to gal
        msg['Unit'] = "gal"
    # filter meter ID
    if BYPASS_METER_FILTER or msg['ID'] in METERS_FILTER:
        # filter out cases where consumption value is negative
        if msg['Consumption'] > 0:
            client.publish(MQTT_TOPIC_PREFIX+"/output",json.dumps(msg)) # publish
            if METERMON_SEND_BY_ID.lower() == "true":
                client.publish(MQTT_TOPIC_PREFIX+"/"+msg['ID'],json.dumps(msg)) # also publish by ID if enabled
            print(json.dumps(msg)) # also print
        # send raw json message if enabled
        if METERMON_SEND_RAW.lower() == "true":
            client.publish(MQTT_TOPIC_PREFIX+"/raw",json.dumps(data)) # publish
