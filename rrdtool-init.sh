#!/bin/sh

mkdir /var/1w_files

rrdtool create /var/1w_files/templog.rrd --step 60   \
DS:ambient:GAUGE:300:-55:125  \
DS:freezer:GAUGE:300:-55:125  \
DS:fridge:GAUGE:300:-55:125  \
DS:light:GAUGE:300:0:1 \
DS:switch:GAUGE:300:0:1 \
RRA:AVERAGE:0.5:1:1440  \
RRA:AVERAGE:0.5:3:3360   \
RRA:AVERAGE:0.5:10:4464  \
RRA:AVERAGE:0.5:60:8760  


