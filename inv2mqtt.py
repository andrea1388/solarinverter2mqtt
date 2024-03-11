import paho.mqtt.client as mqtt
import serial
import time
from crc import crc
from inverterParam import inverterParam
import sys
from param import *


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

mqttIsConnected=False
prevparam = inverterParam()
serialport = serial.Serial(None, 2400, timeout=0.5)

def main():
    arg = sys.argv[1]
    serialport.port=serialdev
    serialport.open()
    serialport.reset_input_buffer()
    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect
    mqttc.on_message = on_message
    mqttc.on_connect_fail = on_connect_fail
    mqttc.username_pw_set(mqttuser, mqttpwd)
    mqttc.tls_set(certpath)
    mqttc.tls_insecure_set(True)
    #mqttc.connect_async(mqttserver, mqttserverport, 60)
    print("a")
    mqttc.loop_start()
    loop
    mqttc.loop_stop()
    serialport.close


def loop():
    param = inverterParam()
    print("b")
    while(True):
        #poll(inverterParam)
        #if(mqttIsConnected):
            #txData2broker(param,prevparam)
        prevparam=param
        print("loop")
        time.sleep(3)


def txData2broker(param,prev):
    if abs(1-(param.loadwatt/prev.loadwatt)) > 0.01:
        mqttc.publish(topic, param.loadwatt, qos=1)


def poll(param):
    tx("QPIRI")
    response = serialport.readlines(None)
    param.loadwatt=response[4:4]

def tx(cmd):
    cmd=bytearray(cmd)
    crc_high, crc_low = crc(cmd)
    cmd.append(crc_high)
    cmd.append(crc_low)
    cmd.append(13)
    serialport.write(cmd)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to mqtt broker with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")
    mqttIsConnected=True

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def on_connect_fail(client, userdata):
    print("connect fail")
    mqttc.reconnect()

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print("disconnect")
    
if __name__ == "__main__":
    main()