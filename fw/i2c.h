#include <stdint.h>
#include "stm32f4xx.h"

typedef enum {
	I2C_OK = 0,
	I2C_ANACK = -1,
	I2C_DNACK = -2,
	I2C_ERR
} i2cReturn_t;

void i2cSetup();
int32_t i2c(I2C_TypeDef* I2Cx, uint8_t addr, uint16_t wLen, uint8_t *wBuff, uint16_t rLen, uint8_t *rBuff);
