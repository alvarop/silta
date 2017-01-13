#ifndef __CONSOLE_H__
#define __CONSOLE_H__

#include <stdint.h>

#define CMD_BUFF_SIZE (4096)
#define TX_RX_BUFF_SIZE (2048)
#define ARGV_MAX (1024)

void consoleProcess();

#endif
