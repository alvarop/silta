#ifndef __DAC_H__
#define __DAC_H__

#include <stdint.h>

void dacInit();
int32_t dacSet(uint8_t dac, uint16_t val);

#endif
