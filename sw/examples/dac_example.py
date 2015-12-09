#!/usr/bin/env python

#
# Output a sin wave through DAC1 (PA4)
#

import sys
import time
import math
from silta import silta

DAC_PIN = 'PA5'

if len(sys.argv) < 2:
    print('Usage: ' + sys.argv[0] + '/path/to/serial/device')
    sys.exit()

stream_file = sys.argv[1]

bridge = silta.stm32f4bridge(stream_file)

# Configure pin as DAC (TODO, currently always a DAC)
# bridge.gpiocfg(DAC_PIN, 'analog')

for i in range(500):
    voltage = math.sin(2 * math.pi * i/100 - math.pi/2 ) *  3.0/2 + 3.0/2
    bridge.dac(DAC_PIN, voltage)
    time.sleep(0.002)

bridge.close()
