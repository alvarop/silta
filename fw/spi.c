#include <stdio.h>
#include <stdint.h>

#include "stm32f4xx_conf.h"
#include "stm32f4xx.h"
#include "spi.h"

#define CS_PIN (3)

typedef struct {
	SPI_TypeDef *SPIx;
	uint32_t speed;
	GPIO_TypeDef* csPort;
	uint16_t csPin;
	uint8_t cpol;
	uint8_t cpha;
} spiConfig_t;

typedef struct {
	uint32_t speed;
	uint32_t prescaler;
} spiSpeedLUT_t;

// 
// Baud rate prescaler LUT (generated in python!)
// for i in range(1,9):
//     print '{' + str(84000000/(1 << i)) + ', SPI_BaudRatePrescaler_' + str((1 << i)) + '},'
//
// NOTE: This only applies to SPI1. SPI2 and SPI3 have slower clocks
// 
spiSpeedLUT_t speedLUT[] = {
	{42000000, SPI_BaudRatePrescaler_2},
	{21000000, SPI_BaudRatePrescaler_4},
	{10500000, SPI_BaudRatePrescaler_8},
	{5250000, SPI_BaudRatePrescaler_16},
	{2625000, SPI_BaudRatePrescaler_32},
	{1312500, SPI_BaudRatePrescaler_64},
	{656250, SPI_BaudRatePrescaler_128},
	{328125, SPI_BaudRatePrescaler_256},
};

spiConfig_t spiConfigs[] = {{SPI1, 1000000, GPIOE, 3, 1, 1}};

static uint32_t spiPrescalerFromSpeed(uint32_t device, uint32_t speed) {
	uint32_t prescaler = SPI_BaudRatePrescaler_256; // Slow default
	
	// TODO devices SPI2 and SPI3
	if(device == 0) {
		for(uint8_t setting = 0; setting < sizeof(speedLUT)/sizeof(spiSpeedLUT_t); setting++) {
			prescaler = speedLUT[setting].prescaler;

			if(speed >= speedLUT[setting].speed) {
				break;
			}
		}
	}

	return prescaler;
}

int32_t spiInit(uint32_t device) {
	int32_t rval = -1;

	if(device < sizeof(spiConfigs)/sizeof(spiConfig_t)) {
		SPI_InitTypeDef spiConfigStruct;
		SPI_TypeDef *SPIx = spiConfigs[device].SPIx;

		RCC_APB2PeriphClockCmd(RCC_APB2Periph_SPI1, ENABLE);

		// PA5 - SCK
		// PA6 - MOSI
		// PA7 - MISO
		GPIO_Init(GPIOA, &(GPIO_InitTypeDef){GPIO_Pin_5, GPIO_Mode_AF, GPIO_Speed_50MHz, GPIO_OType_PP, GPIO_PuPd_NOPULL});
		GPIO_Init(GPIOA, &(GPIO_InitTypeDef){GPIO_Pin_6, GPIO_Mode_AF, GPIO_Speed_50MHz, GPIO_OType_PP, GPIO_PuPd_NOPULL});
		GPIO_Init(GPIOA, &(GPIO_InitTypeDef){GPIO_Pin_7, GPIO_Mode_AF, GPIO_Speed_50MHz, GPIO_OType_PP, GPIO_PuPd_NOPULL});
		
		GPIO_PinAFConfig(GPIOA, GPIO_PinSource5, GPIO_AF_SPI1);
		GPIO_PinAFConfig(GPIOA, GPIO_PinSource6, GPIO_AF_SPI1);
		GPIO_PinAFConfig(GPIOA, GPIO_PinSource7, GPIO_AF_SPI1);

		if(spiConfigs[0].csPort) {
			// TODO - remove this and leave configuration up to the app
			// PE3 - CS
			GPIO_Init(GPIOE, &(GPIO_InitTypeDef){GPIO_Pin_3, GPIO_Mode_OUT, GPIO_Speed_50MHz, GPIO_OType_PP, GPIO_PuPd_NOPULL});

			// Disable CS, since it's active low
			GPIO_SetBits(spiConfigs[0].csPort, (1 << spiConfigs[0].csPin));
		}

		//
		// SPI Config
		//
		SPI_StructInit(&spiConfigStruct);

		spiConfigStruct.SPI_Direction = SPI_Direction_2Lines_FullDuplex;
		spiConfigStruct.SPI_Mode = SPI_Mode_Master;
		spiConfigStruct.SPI_CPOL = spiConfigs[0].cpol ? SPI_CPOL_High : SPI_CPOL_Low;
		spiConfigStruct.SPI_CPHA = spiConfigs[0].cpha ? SPI_CPHA_2Edge : SPI_CPHA_1Edge;
		spiConfigStruct.SPI_NSS = SPI_NSS_Soft;

		// TODO - compute prescaler from speed. Hardcoding for now
		spiConfigStruct.SPI_BaudRatePrescaler = spiPrescalerFromSpeed(0, spiConfigs[0].speed);

		SPI_I2S_DeInit(SPIx);

		SPI_Init(SPIx, &spiConfigStruct);

		SPI_Cmd(SPIx, ENABLE);
		
		rval = 0;
	} 

	return rval;
}

int32_t spiConfig(uint32_t device, uint32_t speed, uint8_t cpol, uint8_t cpha) {
	int32_t rval = -1;
	if(device < sizeof(spiConfigs)/sizeof(spiConfig_t)) {
		spiConfigs[device].speed = speed;
		spiConfigs[device].cpol = cpol;
		spiConfigs[device].cpha = cpha;
		rval = 0;
	}

	return rval;
}

int32_t spiSetCS(uint32_t device, GPIO_TypeDef* csPort, uint16_t csPin) {
	int32_t rval = -1;
	
	if(device < sizeof(spiConfigs)/sizeof(spiConfig_t)) {
		spiConfigs[device].csPort = csPort;
		spiConfigs[device].csPin = csPin;
		rval = 0;
	}

	return rval;
}

int32_t spi(uint32_t device, uint32_t rwLen, uint8_t *wBuff, uint8_t *rBuff) {
	int32_t rval = -1;

	if(device < sizeof(spiConfigs)/sizeof(spiConfig_t)) {
		SPI_TypeDef *SPIx = spiConfigs[device].SPIx;

		if(spiConfigs[0].csPort) {
			// Disable CS, since it's active low
			GPIO_ResetBits(spiConfigs[0].csPort, (1 << spiConfigs[0].csPin));
		}

		for(int32_t byte = 0; byte < rwLen; byte++){
			
			SPIx->DR = wBuff[byte];
			while(!(SPIx->SR & SPI_I2S_FLAG_TXE));
			while(!(SPIx->SR & SPI_I2S_FLAG_RXNE));
			while(SPIx->SR & SPI_I2S_FLAG_BSY);
			rBuff[byte] = SPIx->DR;
		}

		if(spiConfigs[0].csPort) {
			// Disable CS, since it's active low
			GPIO_SetBits(spiConfigs[0].csPort, (1 << spiConfigs[0].csPin));
		}

		rval = 0;
	}
	
	return rval;
}
