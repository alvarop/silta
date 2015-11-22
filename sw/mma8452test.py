#!/usr/bin/env python

#
# Test python-to-i2c bridge with STM32F407
#

import sys
import time
from silta import stm32f4bridge
import matplotlib.pyplot as plt

def readRegs(bridge, reg, count):
	rval = bridge.i2c(MMA_I2C_ADDR, count, [reg])
	if isinstance(rval, list):
		return rval
	else:
		print('readReg Error ' + str(rval))
		return None

def readReg(bridge, reg):
	rval = bridge.i2c(MMA_I2C_ADDR, 1, [reg])
	if isinstance(rval, list):
		return rval[0]
	else:
		print('readReg Error ' + str(rval))
		return None

def writeReg(bridge, reg, val):
	rval = bridge.i2c(MMA_I2C_ADDR, 0, [reg, val])
	if isinstance(rval, list):
		return []
	else:
		print('writeReg Error ' + str(rval))
		return None

def accel(bridge):
	regs = readRegs(bridge, OUT_X_MSB, 6)
	rval = []
	if regs:
		for byte in range(0,6,2):

			# ((MSB << 8) | LSB) >> 4 to right align
			val = ((regs[byte] << 8) | regs[byte + 1]) >> 4

			# Check if number is negative
			if regs[byte] > 0x7F:
				val -= 0x1000

			rval.append(val)

	return rval

MMA_I2C_ADDR = 0x3A

OUT_X_MSB = 0x01
XYZ_DATA_CFG = 0x0E
WHO_AM_I = 0x0D
CTRL_REG1 = 0x2A

connected = False

if len(sys.argv) < 2:
	print 'Usage: ', sys.argv[0], '/path/to/serial/device'
	sys.exit()

stream_file = sys.argv[1]

bridge = stm32f4bridge(stream_file)

whoami = readReg(bridge, WHO_AM_I)

if whoami == 0x2A:
	print('Device found!')
	connected = True
else:
	print('Could not find device :(')

# 
# Initialize!
# 

# Set standby mode
reg1 = readReg(bridge, CTRL_REG1)
writeReg(bridge, CTRL_REG1, (reg1 & ~0x01))

# 0 = +- 2G scale, 1 = +-4G, 2 = +- 8G
writeReg(bridge, XYZ_DATA_CFG, 1)

# Exit standby mode
reg1 = readReg(bridge, CTRL_REG1)
writeReg(bridge, CTRL_REG1, (reg1 | 0x01))

points = {'x':[], 'y':[], 'z':[]}

for i in range(1000):
	values = accel(bridge)
	points['x'].append(values[0])
	points['y'].append(values[1])
	points['z'].append(values[2])

	time.sleep(0.001)

f, plots = plt.subplots(3, sharex=True)
plots[0].plot(points['x'])
plots[0].set_title('X')
plots[1].plot(points['y'])
plots[1].set_title('Y')
plots[2].plot(points['z'])
plots[2].set_title('Z')

plt.show()

bridge.close()
