#!/usr/bin/python

import re

class TempSensor():
    """
    Read data from DS18B20 Temperature sensor via 1-wire interface.
    """
    _DRIVER = "/sys/bus/w1/devices/%s/w1_slave"
    _TEMP_PATTERN = re.compile("t=(-?\d+)")
    _NOERROR_PATTERN = re.compile("YES")

    def __init__(self, sensor_id):
        self._id = sensor_id

    def _read_data(self):
        data_file = open(self._DRIVER % (self._id, ), "r")
        try:
            return data_file.read()
        finally:
            data_file.close()

    def get_temperature(self):
        data = self._read_data()
        # data should contain 2 lines of text like this:
        # 86 01 4b 46 7f ff 0a 10 5e : crc=5e YES
        # 86 01 4b 46 7f ff 0a 10 5e t=24375
        #
        # Temperature reading is value of t= in milli-degrees C
        m = self._NOERROR_PATTERN.search(data)
        if not m:
            raise IOError("Invalid CRC for sensor " + self._id)
        m = self._TEMP_PATTERN.search(data)
        if not m:
            raise IOError("Invalid data for sensor " + self._id)
        return float(m.group(1)) / 1000.0

if __name__ == '__main__':
    import sys
    for sensor_id in sys.argv[1:]:
        sensor = TempSensor(sensor_id)
        print sensor.get_temperature()
