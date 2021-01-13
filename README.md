# Silta - Python to STM32F4 Bridge Project

Python library and STM32F4 Discovery firmware to control the microcontroller's GPIOs and serial interfaces directly from python. This allows for intefacing with external devices quickly without having to write any firmware!

Currently supported interfaces: I2C1, GPIOs (A-E), SPI1, ADCs, DACs, PWM (2 channels)

Future support (hopefully): UART, I2C2-3, SPI2+

For examples, see: https://github.com/alvarop/silta/tree/main/sw/examples

For firmware download/build/update instructions, see: https://github.com/alvarop/silta/tree/main/fw

For python module build instructions, see: https://github.com/alvarop/silta/tree/main/sw

### Hardware References
* [STM32F407 Datasheet](https://www.st.com/resource/en/datasheet/stm32f407vg.pdf)
* [STM32F407 Reference Manual](https://www.st.com/resource/en/reference_manual/dm00031020-stm32f405415-stm32f407417-stm32f427437-and-stm32f429439-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)

### Installation Instructions

You should be able to use pip to get the silta python module using:
`pip install silta`

### Pins

#### I2C
* PB6 - I2C1 SCL (default)
* PB7 - I2C1 SDA (optional)
* PB8 - I2C1 SCL (optional)
* PB9 - I2C1 SDA (default)

#### SPI
* PA5 - SPI1 SCK
* PA6 - SPI1 MISO
* PA7 - SPI1 MOSI

#### ADC
* PA0 - ADC1_0
* PA1 - ADC1_1
* PA2 - ADC1_2
* PA3 - ADC1_3
* PA4 - ADC1_4 (Will disable DAC)
* PA5 - ADC1_5 (Will disable DAC and/or SPI1 SCK)
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

#### DAC
Must be enabled separately, since it disables SPI1 SCK
* PA4 - DAC1
* PA5 - DAC2

#### PWM
NOTE: PWM is currently locked at 10ms period, mainly for use with servos.
* PE5
* PE6

#### GPIO
Most other pins in ports A-E should work as GPIOs
Notable/useful ones:
* PD12 - Green LED
* PD13 - Orange LED
* PD14 - Red LED
