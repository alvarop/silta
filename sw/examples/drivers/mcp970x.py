'''
 MCP970x Thermistor Driver (using Silta bridge)

'''

import time

V0 = (.4)  # .400 V
TC = (.0195)  # (19.5 mV/C)

class MCP9701:
    def __init__(self, bridge, pin, samples=50):
        self.bridge = bridge
        self.pin = pin
        self.samples = samples
        self.bridge.gpiocfg(pin, 'analog')

    def read(self):
        values = []
        for _ in range(self.samples):
            values.append(self.bridge.adc(self.pin))

        avg = sum(values)/float(len(values))
        temp = (avg - V0)/TC
        return round(temp,1)
