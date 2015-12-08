#include <stdio.h>
#include <stdint.h>

#include "stm32f4xx_conf.h"
#include "stm32f4xx.h"
#include "i2c.h"

#define I2C_TIMEOUT_MS (50)

extern volatile uint32_t tickMs;
static volatile uint32_t i2cErr = 0;

void I2C1_EV_IRQHandler(void) {

}

void I2C1_ER_IRQHandler(void) {
	uint32_t sr1 = I2C1->SR1;
	uint32_t sr2 = I2C1->SR2;

	i2cErr = sr1 | (sr2 << 16);
	I2C_ITConfig(I2C1, I2C_IT_ERR, DISABLE);
}

void i2cSetup(uint32_t speed) {
	I2C_InitTypeDef i2cConfig;

	// GPIO Init
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB, ENABLE);

	GPIO_PinAFConfig(GPIOB, GPIO_PinSource6, GPIO_AF_I2C1);
	GPIO_PinAFConfig(GPIOB, GPIO_PinSource9, GPIO_AF_I2C1);

	GPIO_Init(GPIOB, &(GPIO_InitTypeDef){GPIO_Pin_6, GPIO_Mode_AF, GPIO_Speed_50MHz, GPIO_OType_OD, GPIO_PuPd_NOPULL});
	GPIO_Init(GPIOB, &(GPIO_InitTypeDef){GPIO_Pin_9, GPIO_Mode_AF, GPIO_Speed_50MHz, GPIO_OType_OD, GPIO_PuPd_NOPULL});

	RCC_APB1PeriphClockCmd(RCC_APB1Periph_I2C1, ENABLE);

	// I2C init
	I2C_StructInit(&i2cConfig);

	// TODO - Figure out why the speed isn't being set porperly
	i2cConfig.I2C_ClockSpeed = speed;

	i2cConfig.I2C_DutyCycle = I2C_DutyCycle_16_9;

	I2C_DeInit(I2C1);

	I2C_Init(I2C1, &i2cConfig);

	I2C_ITConfig(I2C1, I2C_IT_ERR, ENABLE);
	NVIC_EnableIRQ(I2C1_ER_IRQn);

	I2C_Cmd(I2C1, ENABLE);
}

int32_t i2c(I2C_TypeDef* I2Cx, uint8_t addr, uint16_t wLen, uint8_t *wBuff, uint16_t rLen, uint8_t *rBuff) {
	int32_t rval = 0;
	uint8_t reg;
	uint32_t timeout;

	do {
		i2cErr = 0;

		timeout = tickMs + I2C_TIMEOUT_MS;
		while((I2Cx->SR2 & I2C_SR2_BUSY) && (tickMs < timeout)) {
		}

		if (tickMs > timeout) {
			i2cErr = I2C_TIMEOUT;
			break;
		}

		I2C_ITConfig(I2C1, I2C_IT_ERR, ENABLE);

		if(wLen > 0) {
			// Generate start condition
			I2Cx->CR1 |= I2C_CR1_START;

			// Wait for start condition to be generated
			while(!(I2Cx->SR1 & I2C_SR1_SB) && (tickMs < timeout)) {

			}

			if (tickMs > timeout) {
				i2cErr = I2C_TIMEOUT;
				break;
			}

			// Write address
			I2Cx->DR = addr & 0xFE;

			// Wait for address to be sent
			do {
				reg = I2Cx->SR1;
			} while(!(reg & I2C_SR1_ADDR) && !i2cErr);

			if((reg & I2C_SR1_AF) || (i2cErr & I2C_SR1_AF)) {
				I2Cx->SR1 &= ~I2C_SR1_AF; // Clear ack failure bit
				rval = I2C_ANACK;
				break;
			}

			reg = I2Cx->SR2; // Clear ADDR bit

			while(wLen--) {
				I2Cx->DR = *wBuff++;

				// Wait for address to be sent
				do {
					reg = I2Cx->SR1;
				} while(!(reg & (I2C_SR1_BTF | I2C_SR1_AF)) && !i2cErr);

				if(reg & I2C_SR1_AF || (i2cErr & I2C_SR1_AF)) {
					I2Cx->SR1 &= ~I2C_SR1_AF; // Clear ack failure bit
					rval = I2C_DNACK;
					break;
				}
			}

			// Some error occurred
			if(rval) {
				break;
			}
		}

		if(rLen > 0) {
			// Generate start condition
			I2Cx->CR1 |= I2C_CR1_START;

			// Wait for start condition to be generated
			while(!(I2Cx->SR1 & I2C_SR1_SB) && (tickMs < timeout)) {
			}

			if (tickMs > timeout) {
				i2cErr = I2C_TIMEOUT;
				break;
			}

			// Write address
			I2Cx->DR = addr | 1;

			// Wait for address to be sent
			do {
				reg = I2Cx->SR1;
			} while(!(reg & I2C_SR1_ADDR) && !i2cErr);

			if((reg & I2C_SR1_AF) || (i2cErr & I2C_SR1_AF)) {
				I2Cx->SR1 &= ~I2C_SR1_AF; // Clear ack failure bit
				rval = I2C_ANACK;
				break;
			}

			if(rLen > 1) {
				I2Cx->CR1 |= I2C_CR1_ACK;
			} else {
				I2Cx->CR1 &= ~I2C_CR1_ACK;
				// I2Cx->CR1 |= I2C_CR1_POS;
			}

			reg = I2Cx->SR1;
			reg = I2Cx->SR2; // Clear ADDR bit

			while(rLen--) {
				do {
					reg = I2Cx->SR1;
				} while(!(reg & (I2C_SR1_RXNE)) && !i2cErr);

				if(reg & I2C_SR1_AF || (i2cErr & I2C_SR1_AF)) {
					I2Cx->SR1 &= ~I2C_SR1_AF; // Clear ack failure bit
					rval = I2C_DNACK;
					break;
				}

				if(rLen == 1) {
					I2Cx->CR1 &= ~I2C_CR1_ACK;
				}

				*rBuff++ = I2Cx->DR;
			}
		}

	} while(0);

	// Generate stop condition
	I2Cx->CR1 |= I2C_CR1_STOP;

	I2C_ITConfig(I2C1, I2C_IT_ERR, DISABLE);

	return rval;
}