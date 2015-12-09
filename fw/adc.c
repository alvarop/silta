#include <stdio.h>

#include "stm32f4xx_conf.h"
#include "stm32f4xx.h"
#include "adc.h"

typedef struct {
	GPIO_TypeDef* adcPort;
	uint8_t adcPin;
	ADC_TypeDef* adc;
	uint8_t adcChannel;
} adcChannel_t;

static adcChannel_t adcs[] = {
	{GPIOA, 0,  ADC1,   0},
	{GPIOA, 1,  ADC1,   1},
	{GPIOA, 2,  ADC1,   2},
	{GPIOA, 3,  ADC1,   3},
	{GPIOA, 4,  ADC1,   4},
	{GPIOA, 5,  ADC1,   5},
	{GPIOA, 6,  ADC1,   6},
	{GPIOA, 7,  ADC1,   7},

	{GPIOB, 0,  ADC1,   8},
	{GPIOB, 1,  ADC1,   9},

	{GPIOC, 0,  ADC1,   10},
	{GPIOC, 1,  ADC1,   11},
	{GPIOC, 2,  ADC1,   12},
	{GPIOC, 3,  ADC1,   13},
	{GPIOC, 4,  ADC1,   14},
	{GPIOC, 5,  ADC1,   15},
};

int32_t adcInit() {
	ADC_InitTypeDef adcConfig;

	RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC1, ENABLE); 

	ADC_DeInit();
	ADC_StructInit(&adcConfig);
	ADC_Init(ADC1, &adcConfig);
	ADC_Cmd(ADC1, ENABLE);

	return 0;
}

int32_t adcGetPin(GPIO_TypeDef *port, uint8_t pin) {
	int32_t adcPin = -1;
	for(uint32_t index = 0; index < (sizeof(adcs)/sizeof(adcChannel_t)); index++) {
		if((port == adcs[index].adcPort) && (pin == adcs[index].adcPin)) {
			adcPin = index;
			break;
		}
	}

	return adcPin;
}

int32_t adcRead(uint8_t adc) {
	int32_t rval = -1;

	if(adc < sizeof(adcs)/sizeof(adcChannel_t)) {
		ADC_RegularChannelConfig(adcs[adc].adc, adcs[adc].adcChannel, 1, ADC_SampleTime_144Cycles);
		ADC_SoftwareStartConv(adcs[adc].adc);
		while(ADC_GetFlagStatus(adcs[adc].adc, ADC_FLAG_EOC) == RESET){
			// do nothing
		}
		rval = ADC_GetConversionValue(adcs[adc].adc);
	}

	return rval;
}
