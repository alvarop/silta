''' Silta STM32F407 Discovery Bridge '''

import serial
import string
import sys
import re

class Silta:
    ''' Silta Bridge Base Class '''

    DEBUG = False

    def __init__(self, serial_device, baud_rate=None):
        ''' Initialize Silta Bridge

            Arguments:
            USB serial device path (e.g. /dev/ttyACMX, /dev/cu.usbmodemXXXXX)
        '''

    def close(self):
        ''' Disconnect from USB-serial device. '''

    # Set I2C Speed
    def i2c_speed(self, speed):
        ''' Set I2C speed in Hz. '''

        return False

    # I2C Transaction (wbytes is a list of bytes to tx)
    def i2c(self, addr, rlen, wbytes = []):
        ''' I2C Transaction (write-then-read)

            Arguments:
            addr - 8 bit I2C address
            rlen - Number of bytes to read
            wbytes - List of bytes to write

            Return value:
            Integer with error code
            or
            List with read bytes (or empty list if write-only command)
        '''

        return None

    # SPI Transaction (wbytes is list of bytes)
    def spi(self, cspin, wbytes = []):
        ''' SPI Transaction

            Arguments:
            cspin - Chip/Slave select pin for transaction
            wbytes - List of bytes to write out

            Return Values:
            Integer error code
            or
            List of read bytes
        '''

        return None

    # Configure GPIO as input/output/etc
    def gpiocfg(self, name, mode='input', pull=None):
        ''' GPIO Configuration

            Arguments:
            name - Pin name with format P<port><pin>
            mode - Pin mode
                Available modes:
                input - Digital Input
                output - Push-pull output
                output-od - Open drain output
                analog - Analog input
            pull -
                None (default) - No pull
                up - Pull-up
                down - Pull-down
        '''

    # Read/write gpio value
    def gpio(self, name, value = None):
        ''' Read/Write GPIO (Digital only for now)

            name - Pin name
            value (If setting) - 0 or 1

            Return Values:
            None - if set was succesful
            None - if get failed
            Integer - pin value
        '''
        return None

    # Read adc pin
    def adc(self, name):
        ''' Read ADC pin

            Arguments:
            name - Pin name

            Return Values:
            None - if read failed
            float - Pin value in volts
        '''

        return None

    # Set DAC output for pin
    def dac(self, name, voltage):
        ''' Set DAC Output

            Arguments:
            name - DAC pin
            voltage - Voltage setting for pin

            Return Values:
            None - Failed setting DAC value
            True - Value set successfully
        '''

        return None

    def pwm(self, name, duty_cycle):
        ''' Set PWM Output

            Arguments:
            name - PWM pin
            duty_cycle - Value from 0-1

            Return Values:
            None - Failed setting PWM value
            True - Value set successfully
        '''

        return None
