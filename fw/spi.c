#include <stdio.h>
#include <stdint.h>

#include "stm32f4xx_conf.h"
#include "stm32f4xx.h"
#include "spi.h"

#define CS_PIN (3)

void spiSetup(SPI_TypeDef *SPIx, uint32_t speed, uint8_t cpol, uint8_t cpha) {
	SPI_InitTypeDef spiConfig;

	RCC_APB2PeriphClockCmd(RCC_APB2Periph_SPI1, ENABLE);

	// PA5 - SCK
	// PA6 - MOSI
	// PA7 - MISO
	GPIO_Init(GPIOA, &(GPIO_InitTypeDef){GPIO_Pin_5, GPIO_Mode_AF, GPIO_Speed_50MHz, GPIO_OType_PP, GPIO_PuPd_NOPULL});
	GPIO_Init(GPIOA, &(GPIO_InitTypeDef){GPIO_Pin_6, GPIO_Mode_AF, GPIO_Speed_50MHz, GPIO_OType_PP, GPIO_PuPd_NOPULL});
	GPIO_Init(GPIOA, &(GPIO_InitTypeDef){GPIO_Pin_7, GPIO_Mode_AF, GPIO_Speed_50MHz, GPIO_OType_PP, GPIO_PuPd_NOPULL});
	
	// TODO: Hardcoding CS for now. Will make configurable later
	// PE3 - CS
	GPIO_Init(GPIOE, &(GPIO_InitTypeDef){GPIO_Pin_3, GPIO_Mode_OUT, GPIO_Speed_50MHz, GPIO_OType_OD, GPIO_PuPd_UP});

	GPIO_PinAFConfig(GPIOA, GPIO_PinSource5, GPIO_AF_SPI1);
	GPIO_PinAFConfig(GPIOA, GPIO_PinSource6, GPIO_AF_SPI1);
	GPIO_PinAFConfig(GPIOA, GPIO_PinSource7, GPIO_AF_SPI1);

	GPIO_SetBits(GPIOE, (1 << CS_PIN)); // Disable CS, since it's active low

	//
	// SPI Config
	//
	SPI_StructInit(&spiConfig);

	spiConfig.SPI_Direction = SPI_Direction_2Lines_FullDuplex;
	spiConfig.SPI_Mode = SPI_Mode_Master;
	spiConfig.SPI_CPOL = cpol;
	spiConfig.SPI_CPHA = cpha;
	spiConfig.SPI_NSS = SPI_NSS_Soft;

	// TODO - compute prescaler from speed. Hardcoding for now
	spiConfig.SPI_BaudRatePrescaler = SPI_BaudRatePrescaler_64; // (APB2PCLK == 84MHz)/64 = 1312500 Hz

	SPI_I2S_DeInit(SPIx);

	SPI_Init(SPIx, &spiConfig);

	SPI_Cmd(SPIx, ENABLE);
}

int32_t spi(SPI_TypeDef *SPIx, uint32_t rwLen, uint8_t *wBuff, uint8_t *rBuff) {
	GPIO_ResetBits(GPIOE, (1 << CS_PIN));

	for(int32_t byte = 0; byte < rwLen; byte++){
		
		SPIx->DR = wBuff[byte];
		while(!(SPIx->SR & SPI_I2S_FLAG_TXE));
		while(SPI3->SR & SPI_I2S_FLAG_BSY);
		rBuff[byte] = SPIx->DR;
	}

	GPIO_SetBits(GPIOE, (1 << CS_PIN));

	return 0;
}
