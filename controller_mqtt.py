#!/usr/bin/python

import SocketServer
import temp_sensor
import gpio_sensor
import time
import sys
import threading
import Queue
import rrdtool
import cayenne.client
import paho.mqtt.client as mqtt
import json
from secret import * 
from subprocess import Popen, PIPE

C_TO_F = (9/5)  # constant used in converting C to F

# Cayenne authentication info. This is obtained from the Cayenne Dashboard.
# moved to secret.py
CAYENNE = True
PAHO = True
LOCAL_BROKER_ADDRESS='10.0.0.2'

# The callback for when a message is received from Cayenne.
# message received: {'topic': u'cmd', 'value': u'0', 'msg_id': u'zKsHGw1HIqnKyKM', 'channel': 4, 'client_id': u'2d40b6a0-0faf-11e9-810f-075d38a26cc9'}
def on_message(message):
  print("Message received: " + str(message))
  #print("channel %s, topic %s, value %s" % (message.channel, message.topic, message.value))

  # If there is an error processing the message return an error string, otherwise return nothing.
  #if (True):
  if (message["channel"]=="4") & (message["topic"]=="cmd"):
    light_state = message.value
    print("Set light to %s" % (message.value))
    light.put_value(light_state)
    client.virtualWrite(4, light_state, dataType="digital_actuator", dataUnit="d")
    client.responseWrite(message.msg_id)
    client.loop()

def to_int(s):
    if s:
      return 1
    else:
      return 0

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):

        current = q.get(True)
        foo = ("%d,%s,%s,%s,%s\r\n") % ( current["time"], current["freezer"], current["fridge"], current["ambient"], current["light"] )
        self.request.sendall(foo)
        return 0

def produceData():
    global current
    global client
    global light

    # email configuration
    sender_email = "Your Fridge <root@fridge.kennedygang.com>"
    receiver_email = "doug@kennedygang.com"

    # threshold temp in C
    EMAIL_FRIDGE_THRESH = 7 
    EMAIL_FREEZER_THRESH = -12
    # time in seconds that threshold must be exceeded
    EMAIL_THRESHOLD_TIME = 1200
    # min alert email interval in seconds
    EMAIL_ALERT_INTERVAL = 86400 


    # informative message template
    text = """\
From: {}
To: {}
Subject: HIGH TEMPERATURE ALERT

Hi,

On {}, the fridge was {} deg C and the freezer was {} deg C.

Click http://10.0.0.8:8080/view?scale=day for more information.

"""
    """
    thread to aquire samples continuously
    """
    
    #file = open("/var/1w_files/log.csv", "a")

    # bootstrap timers (take/send readings immediately on start)
    timestamp = time.time() - 5
    cayenne_timestamp = time.time() - 280

    # create sensor/control objects, GPIO and 1wire
    light = gpio_sensor.Gpio("gpio27")
    switch = gpio_sensor.Gpio("gpio22")
    ambient = temp_sensor.TempSensor("28-0000052f7386")
    freezer = temp_sensor.TempSensor("28-0000055fc26e")
    fridge = temp_sensor.TempSensor("28-0000052f91b1")

    # timers for alarm threshold & alert rate limiting
    threshold_timestamp = time.time()
    last_alert_timestamp = 0  # send alert immediately after threshold time

    while(True):

      if (time.time()-timestamp) > 5.0 :
        timestamp = time.time()
        # grab temperature data. skip sensor in case of error
        try:
            ambient_temp = ambient.get_temperature()
        except Exception:
            pass

        try:
            freezer_temp = freezer.get_temperature()
        except Exception:
            pass

        try:
            # fridge thermometer has offset
            #fridge_temp = fridge.get_temperature() - 3.333
            # fridge temp offset changed 12/25/2019
            fridge_temp = fridge.get_temperature() + 2.000
        except Exception:
            pass

        light_state = light.get_value()
        switch_state = switch.get_value()

        # light control logic
        FDefrost = freezer_temp >= -6.0  # defrost mode in freezer
        FHigh = (freezer_temp < -6.0) & (freezer_temp > -15.0)  # "high"
        FLow = freezer_temp <= -15.0   # freezer temp is "low"

        RHigh = fridge_temp > 8.0          # fridge temp is "high"
        RBand = (fridge_temp <= 8.0) & (fridge_temp >= 1.5)  # "band"
        RLow = fridge_temp < 1.5          # fridge temp is "low"

        Door = switch_state == 1

        control = (FHigh & RBand) | RLow | Door
        light_state = to_int(control)
        light.put_value(light_state)

        current = {
          "time": timestamp,
          "ambient": ambient_temp,
          "freezer": freezer_temp,
          "fridge": fridge_temp,
          "light": light_state,
          "switch": switch_state,
        }

        print("Producer: "), 
        print(current)

        #update rrdtool database.  rrdtool is used for webpage graphics
        rrdtool.update("/var/1w_files/templog.rrd", \
                 "%d:%s:%s:%s:%s:%s" % (timestamp,  \
                                     ambient_temp,  \
                                     freezer_temp,  \
                                     fridge_temp,   \
                                     light_state,   \
                                     switch_state))

        # update element in queue for socketserver
        try:
          q.get(False)  # empty the old queue element
        except Exception:
          pass          # queue was empty already

        q.put(current, False)  # insert new element

        # log all data to file
        #foo = ("%d,%s,%s,%s,%s\n") % ( current["time"], current["freezer"], current["fridge"], current["ambient"], current["light"] )
        #file.write(foo)
        #file.flush()

	# update local paho mqtt every time
	paho.publish('fridge',json.dumps(current))

        # update cayenne about every 5 minutes
        if ((time.time() - cayenne_timestamp) > 300):
          print("Publish to cayenne")
          cayenne_timestamp = time.time()
          client.celsiusWrite(1, ambient_temp)
          client.celsiusWrite(2, freezer_temp)
          client.celsiusWrite(3, fridge_temp)
          client.virtualWrite(4, light_state, dataType="digital_actuator", dataUnit="d")
          client.loop()

        # check for alarm condition and possibly send email
        if ( (freezer_temp < EMAIL_FREEZER_THRESH) and (fridge_temp < EMAIL_FRIDGE_THRESH) ):
          # everything normal, reset threshold exceeded time to current time
          threshold_timestamp = time.time()

        else:
          # we have a problem, maybe send email
          if (( (time.time() - threshold_timestamp) > EMAIL_THRESHOLD_TIME) and (( time.time() - last_alert_timestamp) > EMAIL_ALERT_INTERVAL) ):
            # send email, threshold exceeded and alert interval exceeded
            print("Send alert email now!");
            proc = Popen(['/usr/sbin/sendmail','-t','-oi'], stdin=PIPE)
            print(text.format(sender_email,receiver_email,time.strftime("%c"),fridge_temp,(fridge_temp*C_TO_F+32),freezer_temp,(freezer_temp*C_TO_F+32)).encode('utf8'))
            proc.communicate(text.format(sender_email,receiver_email,time.strftime("%c"),fridge_temp,freezer_temp).encode('utf8'))
            proc.wait()
            # we sent an alert, so reset rate-limiting timer 
            last_alert_timestamp = time.time()

# end of while(True)



      else:
        # check for cayenne publish or commands
        client.loop()
        time.sleep(0.1)

current = {}

paho = mqtt.Client('fridge-producer')
#paho.on_message = on_message_wxt
paho.username_pw_set(PAHO_USERNAME,PAHO_PASSWORD)
paho.connect(LOCAL_BROKER_ADDRESS)
paho.loop_start()
#paho.subscribe('wxt/{}/cmd'.format(WXT_SERIAL))  # subscribe to command channel

client = cayenne.client.CayenneMQTTClient()
client.on_message = on_message
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID)
# For a secure connection use port 8883 when calling client.begin:
# client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, port=8883)

q = Queue.Queue(1)
t1 = threading.Thread(target=produceData)
t1.start()

if __name__ == "__main__":
    #HOST, PORT = "localhost", 9999
    HOST, PORT = "0.0.0.0", 9999

    # Create the server, binding to localhost on port 9999
    for i in range(0,50):
      try:
        server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
        print("SocketServer started on port %d" % (PORT))
      except Exception:
        print("SocketServer failed, retry in 10 seconds")
        time.sleep(10)
        continue
      break

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
