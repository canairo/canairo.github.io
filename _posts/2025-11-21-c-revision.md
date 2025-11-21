---
layout: post
title: c revision
date: 2025-11-20 05:40:00 +0800
---

recommended listening for this post is [cirnos perfect math class](https://www.youtube.com/watch?v=5wFDWP5JwSM). these questions are a bit tricky and should test your knowledge well for the upcoming test.

![wow](https://i.imgur.com/VKLzjgy.png)

### question 1

what will the following code output?

```c
int main(void) {
  char c = 'a';
  printf("%d", c);
  return 0;
}
```

1. `a`
2. `97`
3. compiler error
4. undefined behaviour

<hr>

### question 2

what will the following code output?

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
  int a;
  int b = &a;
  int c = a + b;
  printf("%d: ", c);
  return 0;
}
```

1. no way of knowing, a is uninitialized and could be any value
2. it won't compile because you can't add `a` to `b`
3. it won't compile because `&a` is a pointer to an int, but you're initializing it as just an int
4. `1`

<hr>

### question 3

what will the following code output?

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
  int a = 0.1337;
  float b = (float) a;
  printf("%lf", a);
}
```

1. `0.1337`
2. `0`
3. `0.0000`
4. compiler error, can't cast int to float.

<hr>

### question 4

select the correct way to `malloc()` for 10 Birds in the following code:

```c
typedef struct {
  char *name;
  float wingspan;
} Bird;

int main(void) { 
  ...
  return 0;
}
```

1. `Bird *bird_catalog = malloc(sizeof(Bird), 10)`
2. `Bird *bird_catalog = malloc(sizeof(*Bird) * 10)`
3. `Bird bird_catalog = malloc(sizeof(*Bird) * 10)`
4. `Bird *bird_catalog = malloc(sizeof(Bird) * 10)`

<hr>

### question 5

what's the size of the Bird struct?

```c
typedef struct {
  char *name;
  float wingspan;
} Bird;
```

1. no way of knowing, `char` is a 
dynamic array and can be any length
2. 8 (`char*`) + 64 (`float`) = 72
3. 8 (`char*`) + 8 (`float`) = 16
4. no way of knowing, `float` is arbitrary precision and can be either 8, 32, or 64 depending on what value you pass to it

<hr>

### question 6

after this finishes execution, what will the contents of `rawr.txt` be (assuming it starts off blank)?

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
  FILE *fptr = fopen("rawr.txt", "r");
  fprintf(fptr, "meow meow\n");
  return 0;
}
```

1. the compiler will error, as you're writing to a read-only file
2. the program will segfault, as you're writing to a read-only file
3. the file will remain empty
4. the file will contain `meow meow`

<hr>

### question 7

which of the following commands cannot be used to get input from `stdin`?

1. `fgets()` 
2. `read()`
3. `getc()`
4. `strstr()`

<hr>

### question 8

what is the output of the following program?

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
  int a = 10;
  long b = (long)&a;
  int c = *(int*)b;
  printf("%ld %ld %ld\n", a, b, c);
  return 0;
}
```

1. `[3 large, unknown numbers]`
2. `10 [some large unknown number] 10`
3. `10 10 10`
4. `0 0 0`

<hr>

### question 9

what is the output of the following program?

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
  char buf[] = "what's so good about picking up the pieces?";
  for (int i = 0; buf[i]; i++) {
    printf("%c", buf[i]);
  }
  return 0;
}
```

1. `what's so good about picking up the pieces?`
2. `what's so good about picking up the pieces?\00`
3. each character will be on a different newline
4. the loop won't terminate

<hr>

### question 10

what is the output of the following program?

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
  char c = 'a';
  while (c <= 'g') {
    c = (c+1)^0x20;
    printf("%c", c);
  }
  return 0;
}
```

1. `BcDeFg` 
2. `BcDeFgHi` 
3. `BcDeF` 
4. `aBcDeFgHi` 

### question 11

which of the following choices for `b[]` would not result in the program outputting `1`?

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int are_the_same(char* a, char* b, int size) {
  return (strncmp(a, b, size) == 0);
}

int main() {
  char a[7] = "rawr\00xd";
  char b[] = "...";
  printf("%d", are_the_same(a, b, 7));
  return;
}
```

1. `raw`
2. `rawr\00\00\00\00\00`
3. `rawr\00sdlfkjsdlkfjsdkfl`
4. `rawr`

<hr>

### question 12

which of the following correctly explains why this code won't compile?

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
  printf("%d", atoi(getc(stdin)));
  return 0;
}
```

1. `getc()` doesn't take an argument
2. `atoi()` returns a char, breaking the format string
3. `getc()` returns a char, `atoi()` expects a char*
4. it works just fine

<hr>

### question 13

what is the output of the following program? assume that `doesnotexist.txt` does not exist.

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
  FILE *fptr = fopen("doesnotexist.txt", "r");
  int a = 0;
  if (fptr == a) {
    puts("yay!");
  } else {
    puts("awww.");
  }
  return 0;
}
```

1. `awww.`, when `fopen` fails it is undefined behaviour.
2. `yay!`, when `fopen` fails it returns a nullptr.
3. this program won't compile as you can't compare a pointer with an integer.
4. this program won't compile because `doesnotexist.txt` does not exist.

### question 14

which of the following is an invalid way to populate the `name` field of the `Student` struct?

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct {
  char name[16];
  int age;
} Student;

int main(void) {
  Student* student = malloc(sizeof(Student));
  ...
}
```

1. `snprintf(student->name, 16, "cane");`
2. 
```c
char name[] = "cane";
for (int i = 0; name[i]; i++) {
  student->name[i] = name[i];
}
```

3. `student->name = "cane";`
4. `memmove(student->name, "cane", 4);`

### question 15 (bonus)

what's wrong with the following program?

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
  char buf[16];
  fgets(buf, sizeof(buf), stdin);
  printf(buf);
  return 0;
}
```

1. a user can input `"%p"` and leak addresses on the stack
2. `fgets` does not account for the null terminator, the null byte will overflow
3. `sizeof(buf)` actually corresponds to the size of a `char*` pointer, only 8 bytes of input will be read
4. nothing is wrong it's completely fine
