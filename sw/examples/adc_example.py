#!/usr/bin/env python

#
# Read PA1 value and print it out
#

import sys
from silta import silta

ADC_PIN = 'PA1'

if len(sys.argv) < 2:
    print('Usage: ' + sys.argv[0] + '/path/to/serial/device')
    sys.exit()

stream_file = sys.argv[1]

bridge = silta.stm32f4bridge(stream_file)

# Configure pin as an analog input
bridge.gpiocfg(ADC_PIN, 'analog')

value = bridge.adc(ADC_PIN)

print('PA1 Voltage: ' + str(value))

bridge.close()
