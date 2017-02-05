'''
 HTU21D Temp/Humidity Sensor Driver (using Silta bridge)
'''

import time
import tca9548a
import time

HTU21D_ADDR = 0x40 << 1

CMD = {
    'MEASTEMP_HOLD': 0xE3,
    'MEASRH_HOLD': 0xE5,
    'MEASTEMP_NOHOLD': 0xF3,
    'MEASRH_NOHOLD': 0xF5,
    'WRITE_USER_REG': 0xE6,
    'READ_USER_REG': 0xE7,
    'RESET': 0xFE,
    }

class HTU21D:
    def __init__(self, bridge, mux_channel=1):
        self.bridge = bridge
        self.mux = tca9548a.TCA9548A(bridge)
        self.mux_channel = mux_channel
        self.reset()
        time.sleep(0.15)

        self.mux.set_channel(self.mux_channel)
        rval = self.bridge.i2c(HTU21D_ADDR, 1, [CMD['READ_USER_REG']])
        if isinstance(rval, list):
            # Make sure this is the default value (0x02)
            if rval[0] != 0x02:
                return None
        else:
            raise IOError('Error reading from HTU21D ({})'.format(rval))

    def reset(self):
        self.mux.set_channel(self.mux_channel)
        rval = self.bridge.i2c(HTU21D_ADDR, 0, [CMD['RESET']])
        if isinstance(rval, list):
            return
        else:
            raise IOError('Error resetting HTU21D ({})'.format(rval))

    def read_temp(self):
        self.mux.set_channel(self.mux_channel)
        rval = self.bridge.i2c(HTU21D_ADDR, 0, [CMD['MEASTEMP_NOHOLD']])
        time.sleep(0.050)
        rval = self.bridge.i2c(HTU21D_ADDR, 2)
        if isinstance(rval, list) and (len(rval) == 2):
            tempcode = rval[0] << 8 | rval[1]
            temp = (175.72 * tempcode)/65536 - 46.85
        else:
            raise IOError('Error reading from HTU21D ({})'.format(rval))

        return round(temp,1)

    def read_humidity(self):
        self.mux.set_channel(self.mux_channel)
        rval = self.bridge.i2c(HTU21D_ADDR, 0, [CMD['MEASRH_NOHOLD']])
        time.sleep(0.050)
        rval = self.bridge.i2c(HTU21D_ADDR, 2)
        if isinstance(rval, list) and (len(rval) == 2):
            rhcode = rval[0] << 8 | rval[1]
            humidity = (125.0 * rhcode)/65536 - 6
        else:
            raise IOError('Error reading from HTU21D ({})'.format(rval))

        return round(humidity, 0)

    def read(self):
        return self.read_humidity(), self.read_temp()
