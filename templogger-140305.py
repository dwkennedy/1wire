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

def do_update():
# grab temperature data. in case of error, retry after brief pause
  for retry in (5, 1):
    try:
      timestamp = time.time()
      ambient = temp_sensor.TempSensor("28-0000052f7386")
      freezer = temp_sensor.TempSensor("28-0000055fc26e")
      fridge = temp_sensor.TempSensor("28-0000052f91b1")
      ambient_temp = ambient.get_temperature()
      freezer_temp = freezer.get_temperature()
      fridge_temp = fridge.get_temperature()
    except:
      logging.exception("retry in %is because of: ", retry)
      time.sleep(1)

  # control section


  # if fridge exceeds emergency hi-temp, turn off light (5.0C)
  if fridge_temp > 5.0:
    light.put_value("0")
  else:
    # if fridge < 0.5C turn on light
    if fridge_temp < 0.5:
      light.put_value("1")
    else:
      # if fridge is warm enough and freezer is cold enough turn off light
      # compressor may still be running
      if fridge_temp > 1.6 and freezer_temp < -18.0:
        light.put_value("0")
      else:
        if freezer_temp > -6.0: 
        # if freezer > -6.0C, defrost cycle, turn off light
          light.put_value("0")
        else:
          if freezer_temp > -18.0:
          # if freezer > -18.0 C turn on light (warm the fridge to start compressor)
             light.put_value("1")
          else:
            if freezer_temp < -22.0 and fridge_temp > 1.6:
              # if freezer < -22C turn off light  (compressor running, temp will drift down to -23.5 or so)
              light.put_value("0")

  # finish logging with new light values

  light_state = light.get_value()
  switch_state = switch.get_value()
  rrdtool.update("/var/1w_files/templog.rrd",
                     "%d:%s:%s:%s:%s:%s" % (timestamp,
                                     ambient_temp,
                                     freezer_temp,
                                     fridge_temp,
                                     light_state,
                                     switch_state))
  # return
  return


# set up logging to syslog to avoid output being captured by cron
syslog = logging.handlers.SysLogHandler(address="/dev/log")
syslog.setFormatter(logging.Formatter("templogger: %(levelname)s %(message)s"))
logging.getLogger().addHandler(syslog)

do_update()
