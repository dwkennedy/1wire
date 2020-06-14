#!/usr/bin/python

import SocketServer
import temp_sensor
import gpio_sensor
import time
import sys
import threading
import Queue
import rrdtool

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
        foo = ("%d,%s,%s,%s,%s\n") % ( current["time"], current["freezer"], current["fridge"], current["ambient"], current["light"] )
        self.request.sendall(foo)

def produceData():
    global current
    """
    thread to aquire samples continuously
    """
    
    file = open("/var/1w_files/log.csv", "a")

    timestamp = time.time() - 5
    light = gpio_sensor.Gpio("gpio27")
    switch = gpio_sensor.Gpio("gpio22")
    ambient = temp_sensor.TempSensor("28-0000052f7386")
    freezer = temp_sensor.TempSensor("28-0000055fc26e")
    fridge = temp_sensor.TempSensor("28-0000052f91b1")

    while(True):
      if (time.time()-timestamp) > 5.0 :
        timestamp = time.time()
        # grab temperature data. in case of error, retry after brief pause
        #for retry in (5, 1):
        try:
            ambient_temp = ambient.get_temperature()
        except Exception:
            pass
            #print("retry %is: ambient", retry)
            #time.sleep(0.5)

        #for retry in (5, 1):
        try:
            freezer_temp = freezer.get_temperature()
        except Exception:
            pass
            #print("retry %is: ambient", retry)
            #time.sleep(0.5)

        #for retry in (5, 1):
        try:
            fridge_temp = fridge.get_temperature()
        except Exception:
            pass
            #print("retry %is: ambient", retry)
            #time.sleep(0.5)

        light_state = light.get_value()
        switch_state = switch.get_value()

        FDefrost = freezer_temp >= 0.0  # defrost mode in freezer
        FHigh = (freezer_temp < 0.0) & (freezer_temp > -12.0)  # "high"
        FLow = freezer_temp <= -12.0   # freezer temp is "low"

        RHigh = fridge_temp > 6.0          # fridge temp is "high"
        RBand = (fridge_temp <= 6.0) & (fridge_temp > 2.0)  # "band"
        RLow = fridge_temp <= 2.0          # fridge temp is "low"

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

        rrdtool.update("/var/1w_files/templog.rrd", \
                 "%d:%s:%s:%s:%s:%s" % (timestamp,  \
                                     ambient_temp,  \
                                     freezer_temp,  \
                                     fridge_temp,   \
                                     light_state,   \
                                     switch_state))

        try:
          q.get(False)  # empty the old queue element
        except Exception:
          pass          # queue was empty already

        q.put(current, False)  # insert new element

        foo = ("%d,%s,%s,%s,%s\n") % ( current["time"], current["freezer"], current["fridge"], current["ambient"], current["light"] )
        file.write(foo)
        file.flush()

      else:
         time.sleep(0.05)

current = {}

q = Queue.Queue(1)
t1 = threading.Thread(target=produceData)
t1.start()

if __name__ == "__main__":
    #HOST, PORT = "localhost", 9999
    HOST, PORT = "0.0.0.0", 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
