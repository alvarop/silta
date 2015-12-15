#ifndef __PWM_H__
#define __PWM_H__

#include <stdint.h>

void pwmInit();
int32_t pwmSetCCR(uint8_t channel, uint16_t position);

#endif
