# Python script to read data from solar inverter and send to a mqtt broker
## Works For Axpert/Voltronic or similar inverter that implements the serial protocol QMOD QPIGS

I use Home assistant to see reported data.

To install just clone this repo. Copy param.orig.py to param.py and edit this file.
Fill with your parameters: server name, port, mqtt user and password, certificate file and serial port device
Adjust mqtt topics with the ones used in Home assistant. 

After that try it.
```
python3 inv2mqtt.py d
```
d stands for debug

If everithing works fine launch the script as a service.
Look at openrc.initscript.sh for a starting point (for openrc).