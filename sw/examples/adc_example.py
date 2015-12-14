#!/usr/bin/env python

#
# Read PA1 value and print it out
#

import sys
from silta import stm32f407

ADC_PIN = 'PA1'

if len(sys.argv) < 2:
    print('Usage: ' + sys.argv[0] + '/path/to/serial/device')
    sys.exit()

stream_file = sys.argv[1]

bridge = stm32f407.bridge(stream_file)

# Configure pin as an analog input
bridge.gpiocfg(ADC_PIN, 'analog')

value = bridge.adc(ADC_PIN)

print(ADC_PIN + ' Voltage: ' + str(value))

bridge.close()
