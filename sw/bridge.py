#!/usr/bin/env python
#
# Test python-to-i2c bridge with STM32F407
#

import serial
import sys

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

		cmd += '\n'

		self.stream.write(cmd)

		line = self.stream.readline()

		result = line.strip().split(' ')

		if result[0] == 'OK':
			for byte in result[1:]:
				r_bytes.append(int(byte, 16))

		else:
			r_bytes = int(result[1])

		return r_bytes
