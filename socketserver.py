#!/usr/bin/python

import SocketServer
import temp_sensor
import gpio_sensor
import time
import sys

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        #self.data = self.request.recv(1024).strip()
        #print "{} wrote:".format(self.client_address[0])
        #print self.data

        light = gpio_sensor.Gpio("gpio27")
        switch = gpio_sensor.Gpio("gpio22")

        timestamp = time.time()
        ambient = temp_sensor.TempSensor("28-0000052f7386")
        freezer = temp_sensor.TempSensor("28-0000055fc26e")
        fridge = temp_sensor.TempSensor("28-0000052f91b1")
        ambient_temp = ambient.get_temperature()
        freezer_temp = freezer.get_temperature()
        fridge_temp = fridge.get_temperature()
        light_state = light.get_value()
        switch_state = switch.get_value()
        foo = "time: %d  ambient: %s  freezer: %s  fridge: %s  light: %s  switch: %s\n" % (timestamp,
                                     ambient_temp,
                                     freezer_temp,
                                     fridge_temp,
                                     light_state,
                                     switch_state)


        #print(foo)
        self.request.sendall(foo)


if __name__ == "__main__":
    #HOST, PORT = "localhost", 9999
    HOST, PORT = "0.0.0.0", 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()


