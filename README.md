# 1wire
Monitor and control fridge with 3 Dallas 1 wire temperature sensors and the fridge light

rrdrool-init.sh   initializes the rrdtool database
templogger.py      run every minute to control the light & update rrd 
temp_sensor.py    python library to read temp sensors
gpio_sensor.py    python library to toggle gpio bits (and read, untested)
crontab-templogger  example crontab to call templogger.py every minute
code.py          python web.py app for displaying temperature graphs
rc.local	set up GPIO 22&27 in /sys directory
socketserver.py  server that returns all temp values and GPIO states
socketclient.py  client to connect to the above server
read_all.py      read all temps and return on command line
light_on.py      manually turn on light
light_off.py     manually turn off light
controller.py    latest implementation of control + server
controller_cayenne.py    latest implementation of control + server + cayenne mqtt
other files are some tests, alternate methods of reading dallas 1-wire temp

install python-webpy, python-rrdtool, rrdtool using apt-get

GPIO 27 controls the fridge light
GPIO 4 is the dallas 1wire bus
GPIO 22 may some day be the fridge door open sensor
GPIO 23 may some day be the freezer door open sensor

Raspberry Pi wiring
pin 1, 3V3 for dallas 1wire
pin 7, GPIO 4 for dallas wire
pin 9, GND for dallas 1wire
pin 13, GPIO 27 for fridge light solid state relay
pin 14, GND for fridge light SSR

there is a pullup resistor between 3V3 and the D1W signal (GPIO 4)

