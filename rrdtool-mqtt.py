#!/usr/bin/python3

import time
import sys, os
import rrdtool
import paho.mqtt.client as mqtt
import json
from secret import * 

# LOCAL_BROKER_ADDRESS defined in secret.py

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("fridge")

# The callback for when a message is received from mqtt
# message received: {}
def on_message(client, userdata, message):

  print("Message received: " + str(message.payload.decode('UTF-8')))

  #update rrdtool database.  rrdtool is used for webpage graphics
  try:
      current = json.loads(message.payload.decode('UTF-8'))
      rrdtool.update("/var/1w_files/templog.rrd", \
                 "%d:%s:%s:%s:%s:%s" % (current['time'],  \
                                     current['ambient'],  \
                                     current['freezer'],  \
                                     current['fridge'],   \
                                     current['light'],   \
                                     current['switch']))
      #print("update rrdtool succeeded")
  except Exception as e:
      print("update rrdtool failure: {}".format(e))

def main():    
    paho = mqtt.Client('fridge-consumer-%s',(os.getpid()))
    paho.on_message = on_message
    paho.on_connect = on_connect
    paho.username_pw_set(PAHO_USERNAME,PAHO_PASSWORD)
    paho.connect(LOCAL_BROKER_ADDRESS)
    paho.subscribe('fridge')  # subscribe to fridge status


    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    # blocking call to dispatch callbacks, handle reconnecting, etc.
    paho.loop_forever();

if __name__ == "__main__":
    main()
