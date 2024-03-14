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
    #mqttc.on_log = on_log
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
    global debug
    param = inverterParam()
    global prevparam
    while(True):
        poll(param)
        if(mqttc.is_connected()):
            txData2broker(param,prevparam)
        prevparam.loadwatt=param.loadwatt
        time.sleep(3)


def txData2broker(param,prev):
    if abs(param.loadwatt-prev.loadwatt) > 20:
            mqttc.publish(loadwatttopic, param.loadwatt, qos=1)
    if abs(param.pvvoltage-prev.pvvoltage) > 10:
            mqttc.publish(pvvoltagetopic, param.pvvoltage, qos=1)


def poll(param):
    global debug
    tx("QMOD")
    response = serialport.readlines(None)
    r=response[0]
    if(debug): print("qmod: ",r)
    param.inverterstatus=chr(r[1])
    

    tx("QPIGS")
    response = serialport.readlines(None)
    r=response[0]
    if(debug): print("qpigs: ",r)
    param.loadwatt=float(r[28:32].decode())
    param.outputvoltage=float(r[12:17].decode())
    param.batteryvoltage=float(r[41:46].decode())
    param.batterychargingcurrent=float(r[47:50].decode())
    param.batterycapacity=float(r[51:54].decode())
    param.pvinputcurrent=float(r[60:64].decode())
    param.pvinputvoltage=float(r[65:70].decode())
    param.batterydischargingcurrent=float(r[77:82].decode())
    param.pvchargingpower=float(r[98:103].decode())
    if(debug):
        print("param.inverterstatus",param.inverterstatus)
        print("param.loadwatt",param.loadwatt)
        print("param.outputvoltage",param.outputvoltage)
        print("param.batteryvoltage",param.batteryvoltage)
        print("param.batterychargingcurrent",param.batterychargingcurrent)
        print("param.batterycapacity",param.batterycapacity)
        print("param.pvinputcurrent",param.pvinputcurrent)
        print("param.pvinputvoltage",param.pvinputvoltage)
        print("param.batterydischargingcurrent",param.batterydischargingcurrent)
        print("param.pvchargingpower",param.pvchargingpower)
    
        

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