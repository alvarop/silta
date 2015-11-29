# Silta - Python to STM32F4 Bridge Project

Python library and STM32F4 Discovery firmware to control the microcontroller's GPIOs and serial interfaces directly from python. This allows for intefacing with external devices quickly without having to write any firmware!

Currently supported interfaces: I2C1, GPIOs (A-E), SPI1
Future support (hopefully): ADC, DAC, UART, I2C2-3, SPI2+

## Local Python Module Installation for Development

I recommend using virtualenv while working on Silta. See: http://the-hitchhikers-guide-to-packaging.readthedocs.org/en/latest/pip.html

From the root silta directory, run:
`pip install -e sw`
