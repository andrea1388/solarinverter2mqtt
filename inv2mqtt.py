import paho.mqtt.client as mqtt
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttserver="mqtt.ac.cloudns.ph" 
mqttserverport=7352

def main
    mqttIsConnected=false
    startMqttConn
    if(serialConn)
        mqttc.loop_start()
        pollLoop
        mqttc.loop_stop()
        ser.close
    print("serial dev not responding")

def pollLoop
    while True
        poll(param)
        if(mqttIsConnected)
            txData(param,prev)
        prev=param


def txData(param,prev)
    if (param.loadwatt/prev.loadwatt) > perc 
        mqttc.publish(topic, param.loadwatt, qos=1)


def poll(param)
    tx("QPIRI")
    r=readresp
    param.loadwatt=r[4:4]

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")
    mqttIsConnected=true

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    
def startMqttConn
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect("mqtt.eclipseprojects.io", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqttc.loop_forever()