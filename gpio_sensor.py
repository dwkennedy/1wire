#!/usr/bin/python

import re

class Gpio():
    """
    Read data from GPIO using /sys/classes/gpio/gpioXX interface
    """
    _DRIVER = "/sys/class/gpio/%s/value"
    _NOERROR_PATTERN = re.compile("[01]")

    def __init__(self, gpio_id):
        self._id = gpio_id

    def _read_data(self):
        data_file = open(self._DRIVER % (self._id, ), "r")
        try:
            return data_file.read()
        finally:
            data_file.close()

    def _write_data(self, value):
        data_file = open(self._DRIVER % (self._id, ), "w")
        try:
            return data_file.write(str(value))
        finally:
            data_file.close()

    def get_value(self):
        data = self._read_data()
        # data should contain 1 or 0
        #
        # 0 is off (0v) 1 is on (3.3v)
        m = self._NOERROR_PATTERN.match(data)
        if not m:
            raise IOError("Invalid value for GPIO " + self._id)
        return m.group(0)

    def put_value(self, value):
        #
        # 0 is off (0v) 1 is on (3.3v)
        m = self._write_data(value)
        #if not m:
        #    raise IOError("Invalid value for GPIO " + self._id)
        return

if __name__ == '__main__':
    import sys
    for gpio_id in sys.argv[1:]:
        gpio = Gpio(gpio_id)
        print gpio.get_value()
