#!/usr/bin/python3

import time
import sys
import rrdtool
import paho.mqtt.client as mqtt
import json
from secret import * 

LOCAL_BROKER_ADDRESS='10.0.0.2'

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
      print("update rrdtool succeeded")
  except Exception as e:
      print("update rrdtool failure: {}".format(e))

def to_int(s):
    if s:
      return 1
    else:
      return 0

current = {}
    
if __name__ == "__main__":
    paho = mqtt.Client('fridge-consumer')
    paho.on_message = on_message
    paho.username_pw_set(PAHO_USERNAME,PAHO_PASSWORD)
    paho.connect(LOCAL_BROKER_ADDRESS)
    paho.loop_start()
    paho.subscribe('fridge')  # subscribe to fridge status


    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    while True:
       time.sleep(300)

