''' Silta STM32F407 Discovery Bridge

--- Supported Pins
I2C:
* PB6 - I2C1 SCL
* PB7 - I2C1 SDA (optional)
* PB8 - I2C1 SCL (optional)
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

import re
import string

import serial
PIN_RE = re.compile(r'P([A-E])([0-9]+)', re.IGNORECASE)


def _get_pin(raw_str):
    ''' Parse and validate pin definition
    Args:
        raw_str: string of the form PXY
    Returns:
        str, int
    '''
    match = PIN_RE.search(raw_str)
    if not match:
        raise ValueError(
            'Invalid pin definition. Pins are defined as '
            'PXY where X is A-E and Y is 0-15 (e.g. PB5)')
    port, pin = match.groups()
    pin = int(pin)
    if pin > 15:
        raise ValueError('Invalid pin. Should be a number from 0-15')
    return port, pin


class bridge(object):
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

    PIN = [1 << i for i in range(15)]

    def __init__(self, serial_device, baud_rate=None):
        ''' Initialize Silta STM32F407 Bridge

            Args:
                USB serial device path (e.g. /dev/ttyACMX)
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
            raise RuntimeError('Command string too long')

        self.stream.write('{}\n'.format(cmd).encode())
        if self.DEBUG is True:
            print('CMD : {}'.format(cmd))

        line = self.stream.readline()
        if self.DEBUG is True:
            print('RESP: {}'.format(line))

        return line.decode()

    def i2c_speed(self, speed):
        ''' Alias of i2c1_speed method '''
        return self.i2c1_speed(speed)

    # Set I2C Speed
    def i2c1_speed(self, speed):
        ''' Set I2C speed in Hz. '''
        cmd = 'config i2cspeed ' + str(speed)

        line = self.__send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            return True
        else:
            return False

    # Set I2C pins
    def i2c1_pins(self, pins):
        ''' Set I2C1 pins on GPIOB
        Args:
            pins: A 32 bit integer, bitwise selection of pins to use for i2c1
                peripheral

        Example:
            Select PB6 and PB9:
                my_bridge.i2c1_pins(my_bridge.PIN[6] + my_bridge.PIN[9])
            Select PB7 and PB8:
                my_bridge.i2c1_pins(my_bridge.PIN[7] | my_bridge.PIN[8])
                OR
                my_bridge.i2c1_pins(128 | 256)
                OR
                my_bridge.i2c1_pins(0x180)
        '''
        cmd = 'config i2cpins ' + str(pins)

        line = self.__send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            return True
        else:
            return False

    def i2c(self, addr, rlen, wbytes=[]):
        ''' Alias of i2c1 method '''
        return self.i2c1(addr, rlen, wbytes)

    # I2C Transaction (wbytes is a list of bytes to tx)
    def i2c1(self, addr, rlen, wbytes=[]):
        ''' I2C Transaction (write-then-read)

            Args:
                addr: 8 bit I2C address
                rlen: Number of bytes to read
                wbytes: List of bytes to write

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

            port, pin = _get_pin(cspin)

            cmd = 'spics ' + port + ' ' + str(pin)

            line = self.__send_cmd(cmd)

            result = line.strip().split(' ')

            if result[0] != 'OK':
                raise ValueError('Unable to configure SPI CS pin')

    # SPI Transaction (wbytes is list of bytes)
    def spi(self, cspin, wbytes=[]):
        ''' SPI Transaction

            Args:
                cspin: Chip/Slave select pin for transaction
                wbytes: List of bytes to write out

            Returns:
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

            Args:
                speed: SPI Speed in Hz
                    Supported speeds: 42000000, 21000000, 10500000, 5250000,
                                        2625000, 1312500, 656250, 328125
                cpol: Clock polarity
                cpha: Clock phase

            Returns:
                True for success
                or
                False for failure
        '''

        cmd = 'spicfg {} {} {}'.format(speed, int(cpol) & 1, int(cpha) & 1)
        line = self.__send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            return True
        else:
            return False

    # Configure GPIO as input/output/etc
    def gpiocfg(self, name, mode='input', pull=None):
        ''' GPIO Configuration

            Args:
                name: Pin name with format P<port><pin> (e.g. PA3, PD11, PB0)
                mode: Pin mode
                    Available modes:
                    input - Digital Input
                    output - Push-pull output
                    output-od - Open drain output
                    analog - Analog input
                pull: Pull-resistor
                    None (default) - No pull
                    up - Pull-up
                    down - Pull-down
        '''
        port, pin = _get_pin(name)

        if mode not in self.__pinModes:
            raise ValueError('Invalid pin mode. Valid modes: <' + string.join(
                self.__pinModes.keys(), '|') + '>')

        if pull is not None and pull not in self.__pullModes:
            raise ValueError('Invalid pull mode. Valid modes: <' + string.join(
                self.__pullModes.keys(), '|') + '>')

        cmd = 'gpiocfg ' + port + ' ' + str(pin) + ' ' + self.__pinModes[mode]

        if pull is not None:
            cmd += ' ' + self.__pullModes[pull]

        line = self.__send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] != 'OK':
            print("Error configuring pin")

    # Read/write gpio value
    def gpio(self, name, value=None):
        ''' Read/Write GPIO (Digital only for now)

            Args:
                name: Pin name (e.g. PA3, PD11, PB0)
                value: (If setting) - 0 or 1

            Returns:
                None - if set was succesful
                None - if get failed
                Integer - pin value
        '''
        port, pin = _get_pin(name)

        cmd = 'gpio ' + port + ' ' + str(pin)

        if value is not None:
            cmd += ' ' + str(value)

        line = self.__send_cmd(cmd)

        result = line.strip().split(' ')

        if result[0] == 'OK':
            if value is not None:
                return
            else:
                return int(result[1])
        else:
            return None

    # 'Private' function to get an ADC number from a port + pin combination
    def __adc_get_num(self, name):
        ''' Get ADC number from pin name '''

        port, pin = _get_pin(name)

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

            Args:
                name: Pin name

            Returns:
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
            Returns:
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

            Args:
                name: DAC pin
                voltage: Voltage setting for pin

            Returns:
                None - Failed setting DAC value
                True - Value set successfully
        '''

        name = name.upper()

        if name not in self.__dacs:
            raise ValueError('Not a DAC pin')

        if voltage > self.__DAC_MAX_VOLTAGE:
            voltage = self.__DAC_MAX_VOLTAGE

        dac_val = int(voltage/self.__DAC_MAX_VOLTAGE * self.__DAC_MAX_VAL)

        line = self.__send_cmd('dac {} {}'.format(self.__dacs[name], dac_val))

        result = line.strip().split(' ')

        if result[0] == 'OK':
            return True
        else:
            return None

    # Set PWM output for pin
    def pwm(self, name, duty_cycle):
        ''' Set PWM Output

            Args:
                name: PWM pin
                duty_cycle: Value from 0-1

            Returns:
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

        line = self.__send_cmd('pwm {} {}'.format(self.__pwms[name], val))

        result = line.strip().split(' ')

        if result[0] == 'OK':
            return True
        else:
            return None
