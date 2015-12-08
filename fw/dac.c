#include "dac.h"

#include "stm32f4xx_conf.h"
#include "stm32f4xx.h"

#define MAX_VALUE (4095)

void dacInit() {
	DAC_InitTypeDef dacConfig;

	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
	GPIO_Init(GPIOA, &(GPIO_InitTypeDef){GPIO_Pin_4, GPIO_Mode_AN, GPIO_OType_PP, GPIO_Speed_100MHz, GPIO_PuPd_NOPULL});
	GPIO_Init(GPIOA, &(GPIO_InitTypeDef){GPIO_Pin_5, GPIO_Mode_AN, GPIO_OType_PP, GPIO_Speed_100MHz, GPIO_PuPd_NOPULL});

	RCC_APB1PeriphClockCmd(RCC_APB1Periph_DAC, ENABLE);

	DAC_DeInit();

	dacConfig.DAC_Trigger = DAC_Trigger_Software;
	dacConfig.DAC_WaveGeneration = DAC_WaveGeneration_None;
	dacConfig.DAC_LFSRUnmask_TriangleAmplitude = DAC_TriangleAmplitude_4095;
	dacConfig.DAC_OutputBuffer = DAC_OutputBuffer_Enable;

	DAC_Init(DAC_Channel_1, &dacConfig);
	DAC_Init(DAC_Channel_2, &dacConfig);

	DAC_Cmd(DAC_Channel_1, ENABLE);
	DAC_Cmd(DAC_Channel_2, ENABLE);
}

int32_t dacSet(uint8_t dac, uint16_t val) {
	if(val > MAX_VALUE) {
		val = MAX_VALUE;
	} else if(val < 0 ) {
		val = 0;
	}

	if(dac == 0) {
		DAC_SetChannel1Data(DAC_Align_12b_R, (uint16_t)val);
		DAC_SoftwareTriggerCmd(DAC_Channel_1, ENABLE);
	} else if(dac == 1) {
		DAC_SetChannel2Data(DAC_Align_12b_R, (uint16_t)val);
		DAC_SoftwareTriggerCmd(DAC_Channel_2, ENABLE);
	}

	return 0;
}
