#!/bin/bash

      FILES=`ls /sys/bus/w1/devices/w1_bus_master1/ | grep '^28'`
      for file in $FILES
         do
            #echo `date +"%Y-%m-%d %H:%M:%S "; cat /sys/bus/w1/devices/w1_bus_master1/$file/w1_slave | grep t= | sed -n 's/.*t=//;p'` >> /var/1w_files/$file
            echo `date +"%Y-%m-%d %H:%M:%S "; cat /sys/bus/w1/devices/w1_bus_master1/$file/w1_slave | grep t= | sed -n 's/.*t=//;p'` 
         done
      exit 0


