#!/usr/bin/python

import logging
import logging.handlers
import rrdtool
import temp_sensor
import gpio_sensor
import time
import sys

def do_update():
# in case of error, retry after brief pause
  for retry in (3, 1):
    try:
      timestamp = time.time()
      ambient = temp_sensor.TempSensor("28-0000052f7386")
      freezer = temp_sensor.TempSensor("28-0000055fc26e")
      fridge = temp_sensor.TempSensor("28-0000052f91b1")
      ambient_temp = ambient.get_temperature()
      freezer_temp = freezer.get_temperature()
      fridge_temp = fridge.get_temperature()
      rrdtool.update("/var/1w_files/templog.rrd",
                     "%d:%s:%s:%s" % (timestamp,
                                     ambient_temp,
                                     freezer_temp,
                                     fridge_temp))
    except:
      logging.exception("retry in %is because of: ", retry)
      #time.sleep(retry * 1000)
      time.sleep(100)

    # control section
    gpio = gpio_sensor.Gpio("gpio27")

    # if fridge > 4.4C turn off light

    if fridge_temp > 4.4:
        gpio.put_value("0")
   
    else:
 
    # otherwise fridge is < 4.4 C
         if freezer_temp > -15:
            # if freezer > -15C turn on light  (warm fridge to start cooling)
            gpio.put_value("1")
         else:
            if freezer_temp < -20:
            # if freezer < -20C turn off light  (want to drift down to -24 or so)
                gpio.put_value("0")

    # return
    return


# set up logging to syslog to avoid output being captured by cron
syslog = logging.handlers.SysLogHandler(address="/dev/log")
syslog.setFormatter(logging.Formatter("templogger: %(levelname)s %(message)s"))
logging.getLogger().addHandler(syslog)

do_update()
