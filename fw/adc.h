#ifndef __ADC_H__
#define __ADC_H__

#include <stdint.h>
#include <stdbool.h>

int32_t adcInit();
int32_t adcGetPin(GPIO_TypeDef *port, uint8_t pin);
int32_t adcRead(uint8_t adc);

#endif
