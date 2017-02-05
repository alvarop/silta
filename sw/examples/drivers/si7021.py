'''
 Si7021 Temp/Humidity Sensor Driver (using Silta bridge)
'''

import time
import tca9548a
import time

SI7021_ADDR = 0x40 << 1

CMD = {
    'MEASRH_HOLD': 0xE5,
    'MEASRH_NOHOLD': 0xF5,
    'MEASTEMP_HOLD': 0xE3,
    'MEASTEMP_NOHOLD': 0xF3,
    'READPREVTEMP': 0xE0,
    'RESET': 0xFE,
    'WRITERHT_REG': 0xE6,
    'READRHT_REG': 0xE7,
    'WRITEHEATER_REG': 0x51,
    'READHEATER_REG': 0x11
    }

class SI7021:
    def __init__(self, bridge, mux_channel=0):
        self.bridge = bridge
        self.mux = tca9548a.TCA9548A(bridge)
        self.mux_channel = mux_channel
        self.reset()
        time.sleep(0.05)

        self.mux.set_channel(self.mux_channel)
        rval = self.bridge.i2c(SI7021_ADDR, 1, [CMD['READRHT_REG']])
        if isinstance(rval, list):
            # Make sure this is the default value (0x3A)
            if rval[0] != 0x3A:
                return None
        else:
            raise IOError('Error reading from SI7021 ({})'.format(rval))

        self.read_info()

    def reset(self):
        self.mux.set_channel(self.mux_channel)
        rval = self.bridge.i2c(SI7021_ADDR, 0, [CMD['RESET']])
        if isinstance(rval, list):
            return
        else:
            raise IOError('Error resetting SI7021 ({})'.format(rval))

    def read_info(self):
        self.mux.set_channel(self.mux_channel)
        self.id = 0
        self.fw_version = 0.0
        try:
            self.id += self.bridge.i2c(SI7021_ADDR, 1, [0xFA, 0x0F])[0] << 8
            self.id += self.bridge.i2c(SI7021_ADDR, 1, [0xFC, 0xC9])[0] & 0xFF
            fw = self.bridge.i2c(SI7021_ADDR, 1, [0x84, 0xB8])[0]

            if fw == 0xFF:
                self.fw_version = 1.0
            elif fw == 0x20:
                self.fw_version = 2.0

        except TypeError, IOError:
            print('Error reading information from SI7021')
            raise

    def read_temp(self):
        self.mux.set_channel(self.mux_channel)
        rval = self.bridge.i2c(SI7021_ADDR, 0, [CMD['MEASTEMP_NOHOLD']])
        time.sleep(0.025)
        rval = self.bridge.i2c(SI7021_ADDR, 2)
        if isinstance(rval, list) and (len(rval) == 2):
            tempcode = rval[0] << 8 | rval[1]
            temp = (175.72 * tempcode)/65536 - 46.85
        else:
            raise IOError('Error reading from SI7021 ({})'.format(rval))

        return round(temp,1)

    def read_humidity(self):
        self.mux.set_channel(self.mux_channel)
        rval = self.bridge.i2c(SI7021_ADDR, 0, [CMD['MEASRH_NOHOLD']])
        time.sleep(0.025)
        rval = self.bridge.i2c(SI7021_ADDR, 2)
        if isinstance(rval, list) and (len(rval) == 2):
            rhcode = rval[0] << 8 | rval[1]
            humidity = (125.0 * rhcode)/65536 - 6
        else:
            raise IOError('Error reading from SI7021 ({})'.format(rval))

        return round(humidity, 0)

    def read(self):
        return self.read_humidity(), self.read_temp()
