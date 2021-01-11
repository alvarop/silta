#ifndef __I2C_H__
#define __I2C_H__

#include <stdint.h>
#include "stm32f4xx.h"
#include "stm32f4xx_conf.h"
#define I2C1_PINS ((uint16_t) GPIO_Pin_6 | GPIO_Pin_7 | GPIO_Pin_8 | GPIO_Pin_9)

typedef enum {
	I2C_OK = 0,
	I2C_ANACK = -1,
	I2C_DNACK = -2,
	I2C_TIMEOUT = -3,
	I2C_ERR
} i2cReturn_t;

void i2cSetup();
void i2cSetSpeed(uint32_t speed);

// pins is one a bitwise ORed selection of GPIO_Pin_X in GPIOB. All pins not in
// i2c1SelectPins will be set as GPIO. Setting pins to 0 will disable I2C1.
void i2c1SelectPins(uint32_t GPIO_Pins);
int32_t i2c(I2C_TypeDef* I2Cx, uint8_t addr, uint16_t wLen, uint8_t *wBuff, uint16_t rLen, uint8_t *rBuff);

#endif
