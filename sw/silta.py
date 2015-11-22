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
		'output-od': 'outod'
	}

	pullModes = {
		'up': 'pullup',
		'down': 'pulldown',
		'none': 'nopull'
	}

	def __init__(self, serial_device):
		self.stream = None

		try:
			self.stream = serial.Serial(serial_device, timeout=0.1)
		except OSError:
			raise IOError('could not open ' + serial_device)
		
		if self.stream:
			self.stream.flush()

	def close(self):
		self.stream.close()

	def i2c(self, addr, rlen, wbytes):
		rbytes = []
		cmd = 'i2c ' + format(addr, '02X') + ' ' + str(rlen)
		
		for byte in wbytes:
			cmd += format(byte, ' 02X')

		self.stream.write(cmd + '\n')

		line = self.stream.readline()

		result = line.strip().split(' ')

		if result[0] == 'OK':
			for byte in result[1:]:
				rbytes.append(int(byte, 16))

		else:
			rbytes = int(result[1])

		return rbytes

	def spi(self, wbytes):
		rbytes = []
		cmd = 'spi'
		
		for byte in wbytes:
			cmd += format(byte, ' 02X')

		self.stream.write(cmd + '\n')

		line = self.stream.readline()

		result = line.strip().split(' ')

		if result[0] == 'OK':
			for byte in result[1:]:
				rbytes.append(int(byte, 16))

		else:
			rbytes = int(result[1])

		return rbytes

	def gpiocfg(self, name, mode='input', pull=None):
		m = re.search('[Pp]([A-Ea-e])([0-9]+)', name)

		if m is None:
			raise ValueError('Invalid gpio name. Should be of the form PX.Y where X is A-E and Y is 0-15')	

		port = m.group(1)
		pin = int(m.group(2))

		if pin > 15:
			raise ValueError('Invalid pin. Should be a number from 0-15')

		if mode not in self.pinModes:
			raise ValueError('Invalid pin mode. Valid modes: <' + string.join(self.pinModes.keys(), '|') + '>')

		if pull != None and pull not in self.pullModes:
			raise ValueError('Invalid pull mode. Valid modes: <' + string.join(self.pullModes.keys(), '|') + '>')			

		cmd = 'gpiocfg ' + port + ' ' + str(pin) + ' ' + self.pinModes[mode]

		if pull != None:
			cmd += ' ' + self.pullModes[pull]

		self.stream.write(cmd + '\n')

		line = self.stream.readline()
		result = line.strip().split(' ')

		if result[0] != 'OK':
			print("Error configuring pin")

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

		self.stream.write(cmd + '\n')

		line = self.stream.readline()
		result = line.strip().split(' ')

		if result[0] == 'OK':
			if value != None:
				return
			else:
				return int(result[1])
		else:
			return None

