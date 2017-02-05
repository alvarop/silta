'''
 SHT31 Temp/Humidity Sensor Driver (using Silta bridge)
'''

import time
import tca9548a
import time

SHT31_ADDR = 0x44 << 1

CMD = {
    'RD_TH_HIGH_HOLD': [0x2c, 0x06],
    'RD_TH_MED_HOLD': [0x2c, 0x0D],
    'RD_TH_LOW_HOLD': [0x2c, 0x10],
    'RD_TH_HIGH_NOHOLD': [0x24, 0x00],
    'RD_TH_MED_NOHOLD': [0x24, 0x0B],
    'RD_TH_LOW_NOHOLD': [0x24, 0x16],
    'HEATER_ENABLE': [0x30, 0x6D],
    'HEATER_DISABLE': [0x30, 0x66],
    'RD_STATUS': [0xF3, 0x2D],
    'CLR_STATUS': [0x30, 0x41],
    'RESET': [0x30, 0xA2],

    }

class SHT31:
    def __init__(self, bridge, mux_channel=2):
        self.bridge = bridge
        self.mux = tca9548a.TCA9548A(bridge)
        self.mux_channel = mux_channel
        self.reset()
        time.sleep(0.5)

        rval = self.bridge.i2c(SHT31_ADDR, 2, CMD['RD_STATUS'])
        if isinstance(rval, list):
            # Make sure reset was detected (0x01)
            if rval[1] != 0x10:
                return None
        else:
            raise IOError('Error reading from SHT31 ({})'.format(rval))

    def reset(self):
        self.mux.set_channel(self.mux_channel)
        rval = self.bridge.i2c(SHT31_ADDR, 0, CMD['RESET'])
        if isinstance(rval, list):
            return
        else:
            raise IOError('Error resetting SHT31 ({})'.format(rval))

    def read(self):
        self.mux.set_channel(self.mux_channel)
        rval = self.bridge.i2c(SHT31_ADDR, 0, CMD['RD_TH_HIGH_NOHOLD'])
        time.sleep(0.015)
        rval = self.bridge.i2c(SHT31_ADDR, 6)
        if isinstance(rval, list) and (len(rval) == 6):
            tempcode = rval[0] << 8 | rval[1]
            temp = -45 + 175 * tempcode/65535.0

            rhcode = rval[3] << 8 | rval[4]
            humidity = 100 * rhcode/65535.0
        else:
            raise IOError('Error reading from SHT31 ({})'.format(rval))

        return round(humidity, 1), round(temp, 1)
