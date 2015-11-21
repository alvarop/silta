#include <stdio.h>
#include <stdint.h>

#include "stm32f4xx_conf.h"
#include "stm32f4xx.h"
#include "i2c.h"

void i2cSetup() {
	I2C_InitTypeDef i2cConfig;

	// GPIO Init
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB, ENABLE);

	GPIO_Init(GPIOB, &(GPIO_InitTypeDef){GPIO_Pin_6, GPIO_Mode_AF, GPIO_Speed_50MHz, GPIO_OType_OD, GPIO_PuPd_NOPULL});
	GPIO_Init(GPIOB, &(GPIO_InitTypeDef){GPIO_Pin_9, GPIO_Mode_AF, GPIO_Speed_50MHz, GPIO_OType_OD, GPIO_PuPd_NOPULL});

	GPIO_PinAFConfig(GPIOB, GPIO_PinSource6, GPIO_AF_I2C1);
	GPIO_PinAFConfig(GPIOB, GPIO_PinSource9, GPIO_AF_I2C1);

	// I2C init
	I2C_StructInit(&i2cConfig);

	i2cConfig.I2C_ClockSpeed = 100000;

	I2C_DeInit(I2C1);

	I2C_Init(I2C1, &i2cConfig);

	I2C_Cmd(I2C1, ENABLE);
}

int32_t i2c(I2C_TypeDef* I2Cx, uint8_t addr, uint16_t wLen, uint8_t *wBuff, uint16_t rLen, uint8_t rBuff) {
	int32_t rval = 0;
	uint8_t reg;
	// TODO - busy check

	do {
		// Generate start condition
		I2Cx->CR1 |= I2C_CR1_START;

		// Wait for start condition to be generated
		while(!(I2Cx->SR1 & I2C_SR1_SB)) {

		}

		// Write address
		I2Cx->DR = addr & 0xFE;

		// Wait for address to be sent
		do {
			reg = I2Cx->SR1;
		} while(!(reg & (I2C_SR1_ADDR | I2C_SR1_AF)));

		if(reg & I2C_SR1_AF) {
			I2Cx->SR1 |= I2C_SR1_AF; // Clear ack failure bit
			rval = I2C_ANACK;
			break;
		}

		reg = I2Cx->SR2; // Clear ADDR bit

		while(wLen--) {
			I2Cx->DR = *wBuff++;

			// Wait for address to be sent
			do {
				reg = I2Cx->SR1;
			} while(!(reg & (I2C_SR1_BTF | I2C_SR1_AF)));

			if(reg & I2C_SR1_AF) {
				I2Cx->SR1 |= I2C_SR1_AF; // Clear ack failure bit
				rval = I2C_DNACK;
				break;
			}
		}

		// Some error occurred
		if(rval) {
			break;
		}

		// Generate stop condition
		I2Cx->CR1 |= I2C_CR1_STOP;

	} while(0);

	
	return rval;
}