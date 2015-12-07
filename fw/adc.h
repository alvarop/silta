#include <stdint.h>
#include <stdbool.h>

int32_t adcInit();
bool isAdcPin(GPIO_TypeDef *port, uint8_t pin);
uint16_t adcRead(uint8_t adc);
