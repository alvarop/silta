#!/usr/bin/env python

#
# Read PA1 value (NUM_SAMPLES) times and plot it
#

import sys
import time
from silta import stm32f407
import matplotlib.pyplot as plt

ADC_PIN = 'PA1'

NUM_SAMPLES = 1000

if len(sys.argv) < 2:
    print('Usage: ' + sys.argv[0] + '/path/to/serial/device')
    sys.exit()

stream_file = sys.argv[1]

bridge = stm32f407.bridge(stream_file)

# Configure pin as an analog input
bridge.gpiocfg(ADC_PIN, 'analog')

values = []
for i in range(NUM_SAMPLES):
    values.append(bridge.adc(ADC_PIN))
    time.sleep(0.001)

plt.plot(values)
plt.title(ADC_PIN)
plt.show()

bridge.close()
