'''
 TCA9548A I2C Mux
'''

import time
DEFAULT_TCA9548A_ADDR = (0x70 << 1)

class TCA9548A:
    def __init__(self, bridge, address=DEFAULT_TCA9548A_ADDR):
        self.bridge = bridge
        self.address = address

        # Make sure we're running at 100kHz
        self.bridge.i2c_speed(100000)

    def set_channel(self, channel):
        if channel > 7 or channel < 0:
            raise ValueError('Channel out of range. Must be between 0-7')

        rval = self.bridge.i2c(self.address, 0, [(1 << channel) & 0xFF])

        if isinstance(rval, list):
            return
        else:
            raise IOError('TCA9548A not found. ({})'.format(rval))
