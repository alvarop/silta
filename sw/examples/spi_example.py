#!/usr/bin/env python

#
# SPI example (using the STM32F407 discovery board)
#

import sys
import time
from silta import stm32f407

CS_PIN = 'PE3'

if len(sys.argv) < 2:
    print('Usage: ' + sys.argv[0] + '/path/to/serial/device')
    sys.exit()

stream_file = sys.argv[1]

bridge = stm32f407.bridge(stream_file)

# Set the CS line as an output
bridge.gpiocfg(CS_PIN, 'output')

# Configure ~1.05MHz clock with CPOL=0,CPHA=0
bridge.spi_cfg(10500000, 0, 0)

# CS is active low in this case
bridge.gpio(CS_PIN, 1)

# Try reading the WHO_AM_I register from the LIS3DSH on teh discovery board
txbuff = [0x8F, 0x00]

rval = bridge.spi(CS_PIN, txbuff)

if isinstance(rval, list):
    print('WHO_AM_I register is: 0x' + format(rval[1], '02X') + ' (it should be 0x3F btw)')
else:
    print('SPI Error: ' + str(rval))

# we're done!
bridge.close()
