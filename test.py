#!/usr/bin/python

import logging
import logging.handlers
import rrdtool
import temp_sensor
import gpio_sensor
import time
import sys

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
rrdtool.update("/var/1w_files/templog.rrd",
                     "%d:%s:%s:%s:%s:%s" % (timestamp,
                                     ambient_temp,
                                     freezer_temp,
                                     fridge_temp,
                                     light_state,
                                     switch_state))
print "time: %d  ambient: %s  freezer: %s  fridge: %s  light: %s  switch: %s\n" % (timestamp,
                                     ambient_temp,
                                     freezer_temp,
                                     fridge_temp,
                                     light_state,
                                     switch_state)



