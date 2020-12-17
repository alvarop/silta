#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "config.h"
#include "stm32f4xx.h"
#include "i2c.h"

typedef struct {
	char *name;
	int32_t (*getFn)(char *buff, size_t buffSize);
	int32_t (*setFn)(char* val);
	char *description;
} configKey_t;

static char getBuff[256];

static int32_t i2cSpeedSet(char *speedStr) {
	uint32_t speed = strtoul(speedStr, NULL, 10);
	int32_t rval = 0;
	if (speed > 400000) {
		rval = -1;
	} else {
		i2cSetSpeed(speed);
	}

	return rval;
}

//Set I2C Pins
static int32_t i2cPinSet(char *pinsStr) {
        uint32_t pins = strtoul(pinsStr, NULL, 10);
	int32_t rval = 0;
	if (pins > 1){
		rval = -1;
	} else {
		i2cSetPin(pins);
	}
	
	return rval;
}

static uint32_t testVal;
static int32_t testSet(char *value) {
	testVal = strtoul(value, NULL, 10);
	return 0;
}

static int32_t testGet(char *buff, size_t buffSize) {
	return snprintf(buff, buffSize, "%ld", testVal);
}

static configKey_t keys[] = {
	{"i2cspeed", NULL, i2cSpeedSet, "i2c speed in Hz (default=100000)"},
	{"i2cpins", NULL, i2cPinSet, "i2c pin set"},
	{"test", testGet, testSet, "test value"},
	{NULL, NULL, NULL, NULL}
};

static void cfgGet(configKey_t *key) {
	int32_t rval = -1;

	if(key->getFn) {
		rval = key->getFn(getBuff, sizeof(getBuff));
	}

	if(rval < 0) {
		printf("ERR\n");
	} else {
		printf("OK %s\n", getBuff);
	}
}

static void cfgSet(configKey_t *key, char *val) {
	int32_t rval = -1;

	if(key->setFn) {
		rval = key->setFn(val);
	}

	if(rval < 0) {
		printf("ERR\n");
	} else {
		printf("OK\n");
	}
}

void cfgCmd(uint32_t argc, char *argv[]) {
	if(argc > 0) {
		configKey_t *key = keys;
		while(key->name != NULL) {
			if(strcmp(key->name, argv[1]) == 0) {
				if (argc == 2) {
					cfgGet(key);
				} else {
					cfgSet(key, argv[2]);
				}
				break;
			}
			key++;
		}

		if(key->name == NULL) {
			printf("ERR Unknown key '%s'\n", argv[0]);
		}
	}
}
