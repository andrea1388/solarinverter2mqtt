#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import serial
import time
from crc import crc
from inverterParam import inverterParam
import sys
from param import *


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,"solarinverter2mqtt")

prevparam = inverterParam()
serialport = serial.Serial(None, 2400, timeout=0.5)
debug=False
badresp=0
noresp=0
numreadings=0

def main():
    global debug
    if(len(sys.argv)>1):
        arg = sys.argv[1]
        if(arg=="d"): debug=True
    print("debug=",debug)
    serialport.port=serialdev
    serialport.open()
    serialport.reset_input_buffer()

    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect
    mqttc.on_message = on_message
    mqttc.on_connect_fail = on_connect_fail
    if(debug): mqttc.on_log = on_log
    mqttc.username_pw_set(mqttuser, mqttpwd)
    print (mqttuser, mqttpwd)
    mqttc.tls_set(certpath)
    mqttc.tls_insecure_set(True)
    mqttc.connect_timeout=60
    mqttc.connect_async(mqttserver, mqttserverport, 60)

    #mqttc.loop_forever()
    mqttc.loop_start()
    mainLoop()
    mqttc.loop_stop()
    serialport.close


def mainLoop():
    global debug, numreadings
    param = inverterParam()
    global prevparam
    lastSentTime=0
    numreadings=0
    while(True):
        numreadings=numreadings+1
        poll(param)
        if((time.time()-lastSentTime)>tSendInterval):
            if(debug): print("send time")
            if(mqttc.is_connected()):
                txData2broker(param,prevparam)
            numreadings=0
            lastSentTime = time.time()

        #prevparam.loadwatt=param.loadwatt
        time.sleep(3)


def txData2broker(param,prev):
    global numreadings
    if(debug): print("numreadings: ",numreadings)
    param.loadwatt=int(param.loadwatt/numreadings)  
    mqttc.publish(loadwatttopic, param.loadwatt, qos=1)
    param.loadwatt=0

    param.batterydischargingcurrent=int(param.batterydischargingcurrent/numreadings)  
    mqttc.publish(dischargecurrtopic, param.batterydischargingcurrent, qos=1)
    param.batterydischargingcurrent=0

    param.batterychargingcurrent=int(param.batterychargingcurrent/numreadings)  
    mqttc.publish(chargecurrtopic, param.batterychargingcurrent, qos=1)
    param.batterychargingcurrent=0

    param.batteryvoltage=int(param.batteryvoltage/numreadings)  
    mqttc.publish(battvolttopic, param.batteryvoltage, qos=1)
    param.batteryvoltage=0

    param.pvchargingpower=int(param.pvchargingpower/numreadings)  
    mqttc.publish(pvpowertopic, param.pvchargingpower, qos=1)
    param.pvchargingpower=0

    mqttc.publish(invertermodetopic, param.invertermode, qos=1)





def validate(resp,explen):
    global badresp,noresp
    if(len(resp)>0):
        r=resp[0]
        if(len(r)==explen):
            return True
        else:
            badresp=badresp+1
    else:
        noresp=noresp+1
    return False

def poll(param):
    global debug, numreadings
    serialport.reset_input_buffer()
    tx("QMOD")
    response = serialport.readlines(None)
    if validate(response,qmodlen):
        r=response[0]
        if(debug): print("qmod: len=",len(r)," r=",r)
        param.invertermode=chr(r[1])

    tx("QPIGS")
    response = serialport.readlines(None)
    if validate(response,qpigslen):
        r=response[0]
        if(debug): print("qpigs: len=",len(r)," r=",r)
        param.loadwatt=param.loadwatt+float(r[28:32].decode())
        param.outputvoltage=param.outputvoltage+float(r[12:17].decode())
        param.batteryvoltage=param.batteryvoltage+float(r[41:46].decode())
        param.batterychargingcurrent=param.batterychargingcurrent+float(r[47:50].decode())
        param.batterycapacity=float(r[51:54].decode())
        param.pvinputcurrent=param.pvinputcurrent+float(r[60:64].decode())
        param.pvinputvoltage=param.pvinputvoltage+float(r[65:70].decode())
        param.batterydischargingcurrent=param.batterydischargingcurrent+float(r[77:82].decode())
        param.pvchargingpower=param.pvchargingpower+float(r[98:103].decode())
        if(debug):
            print("param.invertermode",param.invertermode)
            print("param.loadwatt",param.loadwatt/numreadings)
            print("param.outputvoltage",param.outputvoltage/numreadings)
            print("param.batteryvoltage",param.batteryvoltage/numreadings)
            print("param.batterychargingcurrent",param.batterychargingcurrent/numreadings)
            print("param.batterycapacity",param.batterycapacity)
            print("param.pvinputcurrent",param.pvinputcurrent/numreadings)
            print("param.pvinputvoltage",param.pvinputvoltage/numreadings)
            print("param.batterydischargingcurrent",param.batterydischargingcurrent/numreadings)
            print("param.pvchargingpower",param.pvchargingpower/numreadings)
    
        

def tx(c):
    cmd=bytearray()
    cmd.extend(map(ord, c))
    crc_high, crc_low = crc(cmd)
    cmd.append(crc_high)
    cmd.append(crc_low)
    cmd.append(13)
    #print(cmd.hex())
    serialport.write(cmd)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to mqtt broker with result code {reason_code} {flags} {properties}")
    global mqttIsConnected
    
    if reason_code=="Success":
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        #client.subscribe("$SYS/#")
        print("Connected")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def on_connect_fail(client, userdata):
    print("connect fail")
    mqttc.reconnect()

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print("disconnect event")
    
def on_log(client, userdata, level, buf):
    print(buf)


if __name__ == "__main__":
    main()
