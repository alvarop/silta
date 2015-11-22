#ifndef __SPI_H__
#define __SPI_H__

#include <stdint.h>

void spiSetup(SPI_TypeDef *SPIx, uint32_t speed, uint8_t cpol, uint8_t cpha);
int32_t spi(SPI_TypeDef *SPIx, uint32_t rwLen, uint8_t *wBuff, uint8_t *rBuff);

#endif
