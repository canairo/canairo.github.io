#include <stdio.h>
#include <stdlib.h>

int main(void) {
    FILE *f = fopen("/proc/self/maps", "r");
    if (!f) {
        perror("fopen");
        return 1;
    }

    int c;
    while ((c = fgetc(f)) != EOF) {
        if (c != '\n')      // skip newlines
            putchar(c);
    }

    printf(" %p %p %p %p %p %p %p %p %p ", malloc, printf, puts, geteuid, uname, ulimit, tmpfile, );
    fclose(f);
    return 0;
}
