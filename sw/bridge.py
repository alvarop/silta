#!/usr/bin/env python
#
# Test python-to-i2c bridge with STM32F407
#

import serial
import sys
import re

class Bridge:
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

	def i2c(self, addr, r_len, w_bytes):
		r_bytes = []
		cmd = 'i2c ' + format(addr, '02X') + ' ' + str(r_len)
		
		for byte in w_bytes:
			cmd += format(byte, ' 02X')

		self.stream.write(cmd + '\n')

		line = self.stream.readline()

		result = line.strip().split(' ')

		if result[0] == 'OK':
			for byte in result[1:]:
				r_bytes.append(int(byte, 16))

		else:
			r_bytes = int(result[1])

		return r_bytes

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

