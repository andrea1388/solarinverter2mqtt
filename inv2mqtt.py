import paho.mqtt.client as mqtt
import serial
import time
from crc import crc
from inverterParam import inverterParam
import sys
from param import *


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,"solarinverter2mqtt")

mqttIsConnected=False
prevparam = inverterParam()
serialport = serial.Serial(None, 2400, timeout=0.5)

def main():
    #arg = sys.argv[1]
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
    param = inverterParam()
    global prevparam
    while(True):
        poll(param)
        if(mqttIsConnected):
            txData2broker(param,prevparam)
        prevparam.loadwatt=param.loadwatt
        time.sleep(3)


def txData2broker(param,prev):
    try:
        if abs(1-(param.loadwatt/prev.loadwatt)) > 0.01:
            mqttc.publish(loadwatttopic, param.loadwatt, qos=1)
            #print("published ",loadwatttopic," ",param.loadwatt)
    except Exception as e:
        a=0

def poll(param):
    #tx("QPIRI")
    #response = serialport.readlines(None)
    #print(response)
    #param.loadwatt=float(response[4:4].decode())
    #r=response[0]
    #r=r[12:17]
    #s=r.decode()
    

    tx("QPIGS")
    response = serialport.readlines(None)
    r=response[0]
    #print(response)
    try:
        param.loadwatt=float(r[28:32].decode())
        param.outputvoltage=float(r[12:17].decode())
    except Exception as e:
        a=0

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
        mqttIsConnected=True
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
    global mqttIsConnected
    print("disconnect event")
    mqttIsConnected=False
    
def on_log(client, userdata, level, buf):
    print(buf)


if __name__ == "__main__":
    main()