'''
 AM2315 Temp/Humidity Sensor Driver (using Silta bridge)
 Based on the Adafruite Arduino driver
 https://github.com/adafruit/Adafruit_AM2315
'''

import time
import tca9548a

AM2315_ADDR = 0xB8

class AM2315:
    def __init__(self, bridge, mux_channel=3):
        self.bridge = bridge
        self.mux = tca9548a.TCA9548A(bridge)
        self.mux_channel = mux_channel

    def read(self):

        self.mux.set_channel(self.mux_channel)

        # Make sure we're running at 100kHz
        self.bridge.i2c_speed(100000)

        # 'wake up' the sensor (it clock stretches so transaction fails)
        self.bridge.i2c(AM2315_ADDR, 0, [0])

        # Read(cmd 0x03) 4 bytes from address 0x00
        self.bridge.i2c(AM2315_ADDR, 0, [0x03, 0x00, 4])

        # Wait ~10ms for measurement
        time.sleep(0.01)

        # Get measurement data
        reply = self.bridge.i2c(AM2315_ADDR, 8, [])


        if not isinstance(reply, list) or (reply[1] != 4):
            raise IOError('Invalid AM2315 response')

        # Convert bytes to humidity
        humidity = ((reply[2] << 8) + reply[3])/10.0

        # Convert bytes to temperature
        temperature = (((reply[4] & 0x7F) << 8) + reply[5])/10.0

        if (reply[4] >> 7) == 1:
            temperature = -temperature

        return humidity, temperature
