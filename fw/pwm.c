#include "stm32f4xx_conf.h"
#include "stm32f4xx.h"
#include "pwm.h"

typedef struct {
	GPIO_TypeDef* port;
	uint8_t pin;
	TIM_TypeDef* TIMx;
	uint32_t period;
	uint8_t ccr;
} pwmChannel_t;

static pwmChannel_t channels[] = {
	{GPIOE, 5, TIM9, 10000, 1},
	{GPIOE, 6, TIM9, 10000, 2},
};

void pwmInit() {
	TIM_TimeBaseInitTypeDef timerConfig;
	TIM_OCInitTypeDef ocConfig;

	// TODO - Remove pin specific configs
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOE, ENABLE);
	GPIO_PinAFConfig(GPIOE, GPIO_PinSource5, GPIO_AF_TIM9);
	GPIO_PinAFConfig(GPIOE, GPIO_PinSource6, GPIO_AF_TIM9);
	GPIO_Init(GPIOE, &(GPIO_InitTypeDef){GPIO_Pin_5, GPIO_Mode_AF, GPIO_OType_PP, GPIO_Speed_50MHz, GPIO_PuPd_NOPULL});
	GPIO_Init(GPIOE, &(GPIO_InitTypeDef){GPIO_Pin_6, GPIO_Mode_AF, GPIO_OType_PP, GPIO_Speed_50MHz, GPIO_PuPd_NOPULL});

	// Power the timer
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_TIM9, ENABLE);

	//
	// Configure timer for 10ms period and 1.5ms pulses (centered)
	//
	TIM_TimeBaseStructInit(&timerConfig);

	timerConfig.TIM_Period = 10000;
	timerConfig.TIM_Prescaler = 168;
	timerConfig.TIM_ClockDivision = 0;
	timerConfig.TIM_CounterMode = TIM_CounterMode_Up;

	TIM_TimeBaseInit(TIM9, &timerConfig);

	//
	// Configure output compare stuff
	//
	TIM_OCStructInit(&ocConfig);

	ocConfig.TIM_OCMode = TIM_OCMode_PWM1;
	ocConfig.TIM_OutputState = TIM_OutputState_Enable;
	ocConfig.TIM_Pulse = 1500;
	ocConfig.TIM_OCPolarity = TIM_OCPolarity_High;

	TIM_OC1Init(TIM9, &ocConfig);
	TIM_OC2Init(TIM9, &ocConfig);

	TIM_ARRPreloadConfig(TIM9, ENABLE);

	// Enable the timer!
	TIM_Cmd(TIM9, ENABLE);
}

int32_t pwmSetCCR(uint8_t channel, uint16_t position) {
	volatile uint32_t *ccr;
	int32_t rval = -1;

	if(channel < sizeof(channels)/sizeof(pwmChannel_t)) {
		ccr = (&channels[channel].TIMx->CCR1 + (channels[channel].ccr - 1));
		*ccr = position;
		rval = 0;
	}

	return rval;
}
