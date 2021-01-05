#ifndef __GPIO_H__
#define __GPIO_H__

#include <stdint.h>

void gpioInit();
int32_t gpioSet(GPIO_TypeDef *GPIOx, uint8_t pin, uint8_t value);
int32_t gpioGet(GPIO_TypeDef *GPIOx, uint8_t pin);
void gpioSelectPin(GPIO_TypeDef *GPIOx, uint8_t pin);

#endif
