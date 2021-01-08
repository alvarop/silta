#include "stm32f4xx.h"
#include "stm32f4xx_conf.h"
#include "gpio.h"

void gpioInit() {
	// Power on all GPIO blocks!
	// We're using USB, so power shouldn't be as big a deal
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB, ENABLE);
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOC, ENABLE);
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOD, ENABLE);
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOE, ENABLE);
}

int32_t gpioSet(GPIO_TypeDef *GPIOx, uint8_t pin, uint8_t value) {
	if(value == 0) {
		GPIO_ResetBits(GPIOx, (1 << pin));
	} else {
		GPIO_SetBits(GPIOx, (1 << pin));
	}

	return 0;
}

int32_t gpioGet(GPIO_TypeDef *GPIOx, uint8_t pin) {
	return GPIO_ReadInputDataBit(GPIOx, (1 << pin));
}
