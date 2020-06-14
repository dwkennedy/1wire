#!/usr/bin/python
# this code runs every minute to collect stats and control the light buld

import logging
import logging.handlers
#import rrdtool
import temp_sensor
import gpio_sensor
import time
import sys

light = gpio_sensor.Gpio("gpio27")
switch = gpio_sensor.Gpio("gpio22")

def do_update():
# grab temperature data. in case of error, retry after brief pause
#  for retry in (5, 1):
#    try:
#      timestamp = time.time()
#      ambient = temp_sensor.TempSensor("28-0000052f7386")
#      freezer = temp_sensor.TempSensor("28-0000055fc26e")
#      fridge = temp_sensor.TempSensor("28-0000052f91b1")
#      ambient_temp = ambient.get_temperature()
#      freezer_temp = freezer.get_temperature()
#      fridge_temp = fridge.get_temperature()
#    except:
#      logging.exception("retry in %is because of: ", retry)
#      time.sleep(1)

  # control section
  light.put_value("0")

  # return
  return


# set up logging to syslog to avoid output being captured by cron
syslog = logging.handlers.SysLogHandler(address="/dev/log")
syslog.setFormatter(logging.Formatter("templogger: %(levelname)s %(message)s"))
logging.getLogger().addHandler(syslog)

do_update()
