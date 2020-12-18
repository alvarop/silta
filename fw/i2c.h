#ifndef __I2C_H__
#define __I2C_H__

#include <stdint.h>
#include "stm32f4xx.h"

typedef enum {
	I2C_OK = 0,
	I2C_ANACK = -1,
	I2C_DNACK = -2,
	I2C_TIMEOUT = -3,
	I2C_ERR
} i2cReturn_t;

void i2cSetup();
void i2cSetSpeed(uint32_t speed);
void i2cSetPin(uint8_t pins);
void i2cAFConfigSet(uint16_t GPIO_SCL, uint16_t GPIO_SDA, uint8_t mode);
int32_t i2c(I2C_TypeDef* I2Cx, uint8_t addr, uint16_t wLen, uint8_t *wBuff, uint16_t rLen, uint8_t *rBuff);

#endif
