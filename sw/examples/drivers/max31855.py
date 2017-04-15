#!/usr/bin/env python

#
# SPI example (using the STM32F407 discovery board)
#

import sys
import time
import ctypes
from silta import stm32f407

def bytes_to_int(byte_list):
    num = 0

    for byte in range(len(byte_list)):
        num += byte_list[byte] << ((len(byte_list) - 1 - byte) * 8)

    return num

class MAX31855(object):
    def __init__(self, bridge, cs_pin):
        self.bridge = bridge
        self.cs_pin = cs_pin
        self.last_fault = 0

        # Set the CS line as an output
        self.bridge.gpiocfg(self.cs_pin, 'output')

        # Configure ~1.05MHz clock with CPOL=0,CPHA=0
        self.bridge.spicfg(10500000, 0, 0)

        # CS is active low in this case
        self.bridge.gpio(self.cs_pin, 1)

    def read(self):
        # Read 32 bits
        txbuff = [0x00, 0x00, 0x00, 0x00]

        rval = self.bridge.spi(self.cs_pin, txbuff)

        if isinstance(rval, list):
            reg = bytes_to_int(rval)

            fault = ((reg >> 16) & 1) == 1

            if fault:
                temperature = None
                last_fault = reg & 0x7
            else:
                temperature = ctypes.c_int16((reg >> 16) & 0xFFFC).value >> 2
                temperature = temperature * 0.25

            return temperature
        else:
            print('SPI Error: ' + str(rval))
            return None

    def get_last_fault(self):
        return last_fault
