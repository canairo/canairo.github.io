#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

int main(void) {
  const char *command = "ls -alps";
  uint64_t ptr = (uint64_t)&printf - 0x59900 + 0x53110;
  int (*rawr)(const char *command) = (int (*)(const char *)) ptr;
  rawr(command);
  return 0;
  }
