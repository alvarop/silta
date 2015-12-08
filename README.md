#Silta - Python to STM32F4 Bridge Project

Python library and STM32F4 Discovery firmware to control the microcontroller's GPIOs and serial interfaces directly from python. This allows for intefacing with external devices quickly without having to write any firmware!

Currently supported interfaces: I2C1, GPIOs (A-E), SPI1

Future support (hopefully): ADC, DAC, UART, I2C2-3, SPI2+

For examples, see: https://github.com/alvarop/silta/tree/master/sw/examples

For firmware build instructions, see: https://github.com/alvarop/silta/tree/master/fw

For python module build instructions, see: https://github.com/alvarop/silta/tree/master/sw

### Installation Instructions

You should be able to use pip to get the silta python module using:
`pip install silta`
