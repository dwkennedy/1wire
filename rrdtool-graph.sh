#!/bin/sh

rrdtool graph /var/www/html/temp_graph.png \
-w 1024 -h 400 -a PNG --slope-mode \
--start -1h --end now \
--vertical-label "temperature (°C)" \
DEF:ambient=/var/1w_files/templog.rrd:ambient:AVERAGE \
DEF:freezer=/var/1w_files/templog.rrd:freezer:AVERAGE \
DEF:fridge=/var/1w_files/templog.rrd:fridge:AVERAGE \
LINE2:ambient#00ff00:"ambient" \
LINE2:freezer#0000ff:"freezer" \
LINE2:fridge#ff0000:"fridge"
