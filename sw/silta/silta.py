#!/usr/bin/env python
#
# Test python-to-i2c bridge with STM32F407
#

import serial
import string
import sys
import re

class stm32f4bridge:
    pinModes = {
        'input': 'in',
        'output': 'outpp',
        'output-od': 'outod',
        'analog': 'analog'
    }

    pullModes = {
        'up': 'pullup',
        'down': 'pulldown',
        'none': 'nopull'
    }

    adcs = {}

    dacs = {
        'PA4': 0,
        'PA5': 1
    }

    ADC_MAX_VOLTAGE = 3.0
    ADC_MAX_VAL = 4095

    DAC_MAX_VOLTAGE = 3.0
    DAC_MAX_VAL = 4095

    DEBUG = False

    def __init__(self, serial_device):
        self.stream = None

        self.lastcspin = None

        try:
            self.stream = serial.Serial()
            self.stream.port = serial_device
            self.stream.timeout = 0.1
            self.stream.open()
        except OSError:
            raise IOError('could not open ' + serial_device)

        if self.stream:
            self.stream.flush()

    def close(self):
        self.stream.close()

    # Send terminal command and wait for response
    def send_cmd(self, cmd):
        self.stream.write(cmd + '\n')
        if self.DEBUG is True:
            print 'CMD : ' + cmd

        line = self.stream.readline()
        if self.DEBUG is True:
            print 'RESP: ' + line,

        return line

    # Set I2C Speed
    def i2c_speed(self, speed):
        rbytes = []
        cmd = 'config i2cspeed ' + str(speed)

        line = self.send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            return True

        else:
            return False

    # I2C Transaction (wbytes is a list of bytes to tx)
    def i2c(self, addr, rlen, wbytes = []):
        rbytes = []
        cmd = 'i2c ' + format(addr, '02X') + ' ' + str(rlen)

        for byte in wbytes:
            cmd += format(byte, ' 02X')

        line = self.send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            for byte in result[1:]:
                rbytes.append(int(byte, 16))
        else:
            rbytes = int(result[1])

        return rbytes

    # Set the spi CS line to use on the next transaction
    def set_spi_cs(self, cspin):
        # Only configure CS if we haven't already
        if self.lastcspin != cspin:
            self.lastcspin = cspin

            pinmatch = re.search('[Pp]([A-Ea-e])([0-9]+)', cspin)

            if pinmatch is None:
                raise ValueError('Invalid CS gpio name. Should be of the form PX.Y where X is A-E and Y is 0-15')

            port = pinmatch.group(1)
            pin = int(pinmatch.group(2))

            if pin > 15:
                raise ValueError('Invalid pin. Should be a number from 0-15')

            cmd = 'spics ' + port + ' ' + str(pin)

            line = self.send_cmd(cmd)

            result = line.strip().split(' ')

            if result[0] != 'OK':
                raise ValueError('Unable to configure SPI CS pin')

    # SPI Transaction (wbytes is list of bytes)
    def spi(self, cspin, wbytes = []):
        rbytes = []

        # Make sure the CS pin is selected
        self.set_spi_cs(cspin)

        cmd = 'spi'

        for byte in wbytes:
            cmd += format(byte, ' 02X')

        line = self.send_cmd(cmd)


        result = line.strip().split(' ')

        if result[0] == 'OK':
            for byte in result[1:]:
                rbytes.append(int(byte, 16))

        else:
            rbytes = int(result[1])

        return rbytes

    # Configure GPIO as input/output/etc
    def gpiocfg(self, name, mode='input', pull=None):
        pinmatch = re.search('[Pp]([A-Ea-e])([0-9]+)', name)

        if pinmatch is None:
            raise ValueError('Invalid gpio name. Should be of the form PX.Y where X is A-E and Y is 0-15')

        port = pinmatch.group(1)
        pin = int(pinmatch.group(2))

        if pin > 15:
            raise ValueError('Invalid pin. Should be a number from 0-15')

        if mode not in self.pinModes:
            raise ValueError('Invalid pin mode. Valid modes: <' + string.join(self.pinModes.keys(), '|') + '>')

        if pull != None and pull not in self.pullModes:
            raise ValueError('Invalid pull mode. Valid modes: <' + string.join(self.pullModes.keys(), '|') + '>')

        cmd = 'gpiocfg ' + port + ' ' + str(pin) + ' ' + self.pinModes[mode]

        if pull != None:
            cmd += ' ' + self.pullModes[pull]

        line = self.send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] != 'OK':
            print("Error configuring pin")

    # Read/write gpio value
    def gpio(self, name, value = None):
        m = re.search('[Pp]([A-Ea-e])([0-9]+)', name)

        if m is None:
            raise ValueError('Invalid gpio name. Should be of the form PX.Y where X is A-E and Y is 0-15')

        port = m.group(1)
        pin = int(m.group(2))

        if pin > 15:
            raise ValueError('Invalid pin. Should be a number from 0-15')

        cmd = 'gpio ' + port + ' ' + str(pin)

        if value != None:
            cmd += ' ' + str(value)

        line = self.send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            if value != None:
                return
            else:
                return int(result[1])
        else:
            return None

    # 'Private' function to get an ADC number from a port + pin combination
    def __adc_get_num(self, name):
        m = re.search('[Pp]([A-Ea-e])([0-9]+)', name)

        if m is None:
            raise ValueError('Invalid gpio name. Should be of the form PX.Y where X is A-E and Y is 0-15')

        port = m.group(1)
        pin = int(m.group(2))

        if pin > 15:
            raise ValueError('Invalid pin. Should be a number from 0-15')

        cmd = 'adcnum ' + port + ' ' + str(pin)

        line = self.send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            self.adcs[name] = int(result[1])
        else:
            self.adcs[name] = None

    # Read adc pin
    def adc(self, name):

        name = name.upper()

        # Get adc number from port+pin and save it
        if name not in self.adcs:
            self.__adc_get_num(name)

        if self.adcs[name] is None:
            raise ValueError('Not an ADC pin')

        cmd = 'adc ' + str(self.adcs[name])

        line = self.send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            return int(result[1]) * self.ADC_MAX_VOLTAGE/self.ADC_MAX_VAL
        else:
            return None

    # Set DAC output for pin
    def dac(self, name, voltage):
        
        name = name.upper()

        if name not in self.dacs:
            raise ValueError('Not a DAC pin')

        if voltage > self.DAC_MAX_VOLTAGE:
            voltage = self.DAC_MAX_VOLTAGE

        dac_val = int(voltage/self.DAC_MAX_VOLTAGE * self.DAC_MAX_VAL)

        line = self.send_cmd('dac ' + str(self.dacs[name]) + ' ' + str(dac_val))

        result = line.strip().split(' ')

        if result[0] == 'OK':
            return True
        else:
            return None
