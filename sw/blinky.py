#!/usr/bin/env python

#
# Blink some lights, but with Python! (and the STM32F407 discovery board)
#

import sys
import time
from silta import stm32f4bridge

BLUE_LED = 'PD15'

if len(sys.argv) < 2:
    print 'Usage: ', sys.argv[0], '/path/to/serial/device'
    sys.exit()

stream_file = sys.argv[1]

bridge = stm32f4bridge(stream_file)

# Enable the blue LED
bridge.gpiocfg(BLUE_LED, 'output')

for dummy in range(25):
    time.sleep(0.05)
    bridge.gpio(BLUE_LED, 1)
    time.sleep(0.05)
    bridge.gpio(BLUE_LED, 0)

bridge.close()
