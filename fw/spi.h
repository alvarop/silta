#ifndef __SPI_H__
#define __SPI_H__

#include <stdint.h>

int32_t spiInit(uint32_t device);
int32_t spiConfig(uint32_t device, uint32_t speed, uint8_t cpol, uint8_t cpha);
int32_t spi(uint32_t device, uint32_t rwLen, uint8_t *wBuff, uint8_t *rBuff);

#endif
