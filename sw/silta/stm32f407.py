''' Silta STM32F407 Discovery Bridge

--- Supported Pins
I2C:
* PB6 - I2C1 SCL
* PB9 - I2C1 SDA

SPI:
* PA5 - SPI1 SCK
* PA6 - SPI1 MISO
* PA7 - SPI1 MOSI

ADC:
* PA0 - ADC1_0
* PA1 - ADC1_1
* PA2 - ADC1_2
* PA3 - ADC1_3
* PA4 - ADC1_4 (Will disable DAC)
* PA5 - ADC1_5 (Will disable DAC)
* PA6 - ADC1_6
* PA7 - ADC1_7
* PB0 - ADC1_8
* PB1 - ADC1_9
* PC0 - ADC1_10
* PC1 - ADC1_11
* PC2 - ADC1_12
* PC3 - ADC1_13
* PC4 - ADC1_14
* PC5 - ADC1_15

DAC:
* PA4 - DAC1
* PA5 - DAC2

PWM:
NOTE: PWM is currently locked at 10ms period, mainly for use with servos.
* PE5
* PE6

GPIO:
Most other pins in ports A-E should work as GPIOs
Notable/useful ones:
* PD12 - Green LED
* PD13 - Orange LED
* PD14 - Red LED
'''

import serial
import string
import sys
import re
from silta import Silta

class bridge(Silta):
    ''' Silta STM32F407 Discovery Bridge '''

    __pinModes = {
        'input': 'in',
        'output': 'outpp',
        'output-od': 'outod',
        'analog': 'analog'
    }

    __pullModes = {
        'up': 'pullup',
        'down': 'pulldown',
        'none': 'nopull'
    }

    __adcs = {}

    __dacs = {
        'PA4': 0,
        'PA5': 1
    }

    __pwms = {
        'PE5': 0,
        'PE6': 1
    }

    __ADC_MAX_VOLTAGE = 3.0
    __ADC_MAX_VAL = 4095

    __DAC_MAX_VOLTAGE = 3.0
    __DAC_MAX_VAL = 4095

    DEBUG = False

    # Hardcoding until we can read values back from device
    __CMD_MAX_STR_LEN = 4095
    __SPI_MAX_BYTES = 1024
    __I2C_MAX_BYTES = 1024

    def __init__(self, serial_device, baud_rate=None):
        ''' Initialize Silta STM32F407 Bridge

            Arguments:
            USB serial device path (e.g. /dev/ttyACMX, /dev/cu.usbmodemXXXXX)
        '''

        self.stream = None

        self.lastcspin = None

        try:
            self.stream = serial.Serial()
            self.stream.port = serial_device
            self.stream.timeout = 0.1
            if baud_rate:
                self.stream.baudrate = baud_rate
            self.stream.open()
        except OSError:
            raise IOError('could not open ' + serial_device)

        if self.stream:
            self.stream.flush()

        # Flush any remaining data in the silta's buffer
        self.__send_cmd('\n')

        # Get device serial number and save it
        line = self.__send_cmd('sn\n')
        result = line.strip().split(' ')

        if result[0] == 'OK':
            self.serial_number = ''.join(result[1:])
        else:
            self.serial_number = None
            print('Warning: Could not read device serial number.')
            print('You might want to update firmware on your board')

        # Get device serial number and save it
        line = self.__send_cmd('version\n')
        result = line.strip().split(' ')

        if result[0] == 'OK':
            self.firmware_version = result[1]
        else:
            self.firmware_version = None
            print('Warning: Could not read device firmware version.')
            print('You might want to update firmware on your board')


    def close(self):
        ''' Disconnect from USB-serial device. '''
        self.stream.close()

    # Send terminal command and wait for response
    def __send_cmd(self, cmd):

        if (len(cmd) + 1) > self.__CMD_MAX_STR_LEN:
            raise RuntimeException('Command string too long')

        self.stream.write(cmd + '\n')
        if self.DEBUG is True:
            print 'CMD : ' + cmd

        line = self.stream.readline()
        if self.DEBUG is True:
            print 'RESP: ' + line,

        return line

    # Set I2C Speed
    def i2c_speed(self, speed):
        ''' Set I2C speed in Hz. '''
        rbytes = []
        cmd = 'config i2cspeed ' + str(speed)

        line = self.__send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            return True
        else:
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

        if len(wbytes) > self.__I2C_MAX_BYTES:
            raise ValueError('wbytes too long. Max:', self.__I2C_MAX_BYTES)

        if rlen > self.__I2C_MAX_BYTES:
            raise ValueError('rlen too long. Max:', self.__I2C_MAX_BYTES)

        rbytes = []
        cmd = 'i2c ' + format(addr, '02X') + ' ' + str(rlen)

        for byte in wbytes:
            cmd += format(byte, ' 02X')

        line = self.__send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            for byte in result[1:]:
                rbytes.append(int(byte, 16))
        else:
            rbytes = int(result[1])

        return rbytes

    # Set the spi CS line to use on the next transaction
    def __set_spi_cs(self, cspin):
        ''' Select SPI chip select pin for next transaction '''

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

            line = self.__send_cmd(cmd)

            result = line.strip().split(' ')

            if result[0] != 'OK':
                raise ValueError('Unable to configure SPI CS pin')

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
        if len(wbytes) > self.__SPI_MAX_BYTES:
            raise ValueError('wbytes too long. Max:', self.__SPI_MAX_BYTES)

        rbytes = []

        # Make sure the CS pin is selected
        self.__set_spi_cs(cspin)

        cmd = 'spi'

        for byte in wbytes:
            cmd += format(byte, ' 02X')

        line = self.__send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            for byte in result[1:]:
                rbytes.append(int(byte, 16))

        else:
            rbytes = int(result[1])

        return rbytes

    def spicfg(self, speed, cpol, cpha):
        ''' SPI Configuration

            Arguments:
            speed - SPI Speed in Hz
                Supported speeds: 42000000, 21000000, 10500000, 5250000,
                                    2625000, 1312500, 656250, 328125
            cpol - Clock polarity
            cpha - Clock phase

            Return Values:
            True for success
            or
            False for failure
        '''

        cmd = 'spicfg ' + str(speed) + ' ' + str(int(cpol) & 1) + ' ' + str(int(cpha) & 1)
        line = self.__send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            return True
        else:
            return False

    # Configure GPIO as input/output/etc
    def gpiocfg(self, name, mode='input', pull=None):
        ''' GPIO Configuration

            Arguments:
            name - Pin name with format P<port><pin> (e.g. PA3, PD11, PB0)
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
        pinmatch = re.search('[Pp]([A-Ea-e])([0-9]+)', name)

        if pinmatch is None:
            raise ValueError('Invalid gpio name. Should be of the form PX.Y where X is A-E and Y is 0-15')

        port = pinmatch.group(1)
        pin = int(pinmatch.group(2))

        if pin > 15:
            raise ValueError('Invalid pin. Should be a number from 0-15')

        if mode not in self.__pinModes:
            raise ValueError('Invalid pin mode. Valid modes: <' + string.join(self.__pinModes.keys(), '|') + '>')

        if pull != None and pull not in self.__pullModes:
            raise ValueError('Invalid pull mode. Valid modes: <' + string.join(self.__pullModes.keys(), '|') + '>')

        cmd = 'gpiocfg ' + port + ' ' + str(pin) + ' ' + self.__pinModes[mode]

        if pull != None:
            cmd += ' ' + self.__pullModes[pull]

        line = self.__send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] != 'OK':
            print("Error configuring pin")

    # Read/write gpio value
    def gpio(self, name, value = None):
        ''' Read/Write GPIO (Digital only for now)

            name - Pin name (e.g. PA3, PD11, PB0)
            value (If setting) - 0 or 1

            Return Values:
            None - if set was succesful
            None - if get failed
            Integer - pin value
        '''
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

        line = self.__send_cmd(cmd)

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
        ''' Get ADC number from pin name '''

        m = re.search('[Pp]([A-Ea-e])([0-9]+)', name)

        if m is None:
            raise ValueError('Invalid gpio name. Should be of the form PX.Y where X is A-E and Y is 0-15')

        port = m.group(1)
        pin = int(m.group(2))

        if pin > 15:
            raise ValueError('Invalid pin. Should be a number from 0-15')

        cmd = 'adcnum ' + port + ' ' + str(pin)

        line = self.__send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            self.__adcs[name] = int(result[1])
        else:
            self.__adcs[name] = None

    # Read adc pin
    def adc(self, name):
        ''' Read ADC pin

            Arguments:
            name - Pin name

            Return Values:
            None - if read failed
            float - Pin value in volts
        '''

        name = name.upper()

        # Get adc number from port+pin and save it
        if name not in self.__adcs:
            self.__adc_get_num(name)

        if self.__adcs[name] is None:
            raise ValueError('Not an ADC pin')

        cmd = 'adc ' + str(self.__adcs[name])

        line = self.__send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            return int(result[1]) * self.__ADC_MAX_VOLTAGE/self.__ADC_MAX_VAL
        else:
            return None

    def dac_enable(self):
        ''' Enable DACs
            Return Values:
                None - Failed setting DAC value
                True - Value set successfully
        '''

        line = self.__send_cmd('dacenable')

        result = line.strip().split(' ')

        if result[0] == 'OK':
            return True
        else:
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

        name = name.upper()

        if name not in self.__dacs:
            raise ValueError('Not a DAC pin')

        if voltage > self.__DAC_MAX_VOLTAGE:
            voltage = self.__DAC_MAX_VOLTAGE

        dac_val = int(voltage/self.__DAC_MAX_VOLTAGE * self.__DAC_MAX_VAL)

        line = self.__send_cmd('dac ' + str(self.__dacs[name]) + ' ' + str(dac_val))

        result = line.strip().split(' ')

        if result[0] == 'OK':
            return True
        else:
            return None

    # Set PWM output for pin
    def pwm(self, name, duty_cycle):
        ''' Set PWM Output

            Arguments:
            name - PWM pin
            duty_cycle - Value from 0-1

            Return Values:
            None - Failed setting PWM value
            True - Value set successfully
        '''

        name = name.upper()

        if name not in self.__pwms:
            raise ValueError('Not a PWM pin')

        if duty_cycle < 0 or duty_cycle > 1:
            raise ValueError('Duty cycle must be between 0 and 1')

        period = 10000
        val = int(period * duty_cycle)

        line = self.__send_cmd('pwm ' + str(self.__pwms[name]) + ' ' + str(val))

        result = line.strip().split(' ')

        if result[0] == 'OK':
            return True
        else:
            return None
