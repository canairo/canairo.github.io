---
layout: post
title: profcane's c revision
date: 2025-11-20 05:40:00 +0800
---
<style>
  
  .quiz-options {
    list-style: none;
    padding: 0;
    margin-top: 15px;
  }

  .option {
    padding: 10px 15px;
    margin-bottom: 8px;
    cursor: pointer;
    border: 1px solid gray;
    transition: all 0.2s ease;
  }

  .option:hover {
    border: 1px solid white;
  }

  .quiz-block.answered .option {
    cursor: default;
    pointer-events: none;
  }

  .quiz-block.answered .option.correct {
    background-color: #1c1c1c;
    color: green;
    font-weight: bold;
  }

  .quiz-block.answered .option:not(.correct) {
    color: #86181d;
    opacity: 0.7;
  }

  .explanation {
    display: none;
    margin-top: 25px;
    padding-inline: 15px;
    border-left: 2px solid #b8bb26;
  }

  .quiz-block.answered .explanation {
    display: block;
    animation: fadeIn 0.5s;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
</style>

recommended listening for this post is [cirnos perfect math class](https://www.youtube.com/watch?v=5wFDWP5JwSM). these questions are a bit tricky and should test your knowledge well for the upcoming test.

![wow](https://i.imgur.com/VKLzjgy.png)
<div class="quiz-block" markdown="1">
### question 1

what will the following code output?

```c
int main(void) {
  char c = 'a';
  printf("%d", c);
  return 0;
}
```

<ul class="quiz-options">
  <li class="option">a</li>
  <li class="option correct">97</li>
  <li class="option">compiler error</li>
  <li class="option">undefined behaviour</li>
</ul>


<div class="explanation" markdown=1>
<b>explanation</b>: this is about format specifiers. `%d` is the format specifier for an integer, so when we pass the char `a` into the format specifier, it gets converted into its integer representation (aka its ascii code, <b>97</b>). 
</div>

</div>
<hr>
<!-- QUESTION 2 -->
<div class="quiz-block" markdown="1">
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

<ul class="quiz-options">
  <li class="option">no way of knowing, a is uninitialized and could be any value</li>
  <li class="option">it won't compile because you can't add a to b</li>
  <li class="option correct">it won't compile because &a is a pointer to an int, but you're initializing it as just an int</li>
  <li class="option">1</li>
</ul>

<div class="explanation" markdown=1>
<b>explanation</b>: an integer and a pointer to an integer are two different things and cannot be implicitly cast from one to the other. we can do `int b = (int)&a`, but this results in its own problems.

</div>
</div>

<hr>
<div class="quiz-block" markdown="1">
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

<ul class="quiz-options">
  <li class="option">0.1337</li>
  <li class="option">0</li>
  <li class="option correct">0.0000</li>
  <li class="option">compiler error, can't cast int to float.</li>
</ul>
<div class="explanation" markdown="1">
<b>explanation:</b> this one's about truncation, the initial bug is in the first line `int a = 0.1337;`, an `int` cannot have a decimal value so it gets rounded down to 0. note that option 2 is wrong because we're still printing it as a float w/ the `%lf` specifier.
</div>
</div>
<hr>


<div class="quiz-block" markdown="1">
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

<ul class="quiz-options">
  <li class="option">Bird *bird_catalog = malloc(sizeof(Bird), 10)</li>
  <li class="option">Bird *bird_catalog = malloc(sizeof(*Bird) * 10)</li>
  <li class="option">Bird bird_catalog = malloc(sizeof(*Bird) * 10)</li>
  <li class="option correct">Bird *bird_catalog = malloc(sizeof(Bird) * 10)</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> the syntax for `malloc()` is that it takes a single param `size_t size`, that rules out the first option. `malloc()` also returns a pointer - the third option initializes it as an _instance_ of the Bird struct, so that's out. finally, we're initialising a pointer to a contiguous array of `Bird` structs, so we need the actual size of the `Bird` structs and not the size of their pointers.
</div>
</div>
<hr>
<!-- QUESTION 5 -->
<div class="quiz-block" markdown="1">
### question 5

what's the size of the Bird struct?

```c
typedef struct {
  char *name;
  float wingspan;
} Bird;
```

<ul class="quiz-options">
  <li class="option">no way of knowing, char is a 
dynamic array and can be any length</li>
  <li class="option correct">8 (char*) + 4 (float) + struct padding = 16</li>
  <li class="option">8 (char*) + 4 (float) = 12</li>
  <li class="option">no way of knowing, float is arbitrary precision and can be either 8, 32, or 64 depending on what value you pass to it</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> ok this question is kind of tricky if you don't know about struct padding, but most structs have to be 8-byte aligned due to compiler optimisations. however you can automatically rule out the first and last options because `char*` is a pointer _to_ some array (which can be dynamically sized ofc), and pointers are always the same size. the last option is also wrong because a `float` is always the same size (given you're using the same compiler for everything). 
  </div>
</div>
<hr>
<!-- QUESTION 6 -->
<div class="quiz-block" markdown="1">
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

<ul class="quiz-options">
  <li class="option">the compiler will error, as you're writing to a read-only file</li>
  <li class="option">the program will segfault, as you're writing to a read-only file</li>
  <li class="option correct">the file will remain empty</li>
  <li class="option">the file will contain `meow meow`</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> it'll just fail silently. ofc, the compiler doesn't actually do a check to see if the file exists at compiletime, that's crazy.

_optional info_ so programs will actually segfault if they try to write to read only pages of memory, such as a binary's Global Offset Table when the program is compiled w/ full Relocation Read-Only. this is relevant in the beautiful field of binary exploitation, which i dearly love, but is absolutely beyond the scope of a first year C class. please message me if you'd love to learn more
</div>
</div>
<hr>
<!-- QUESTION 7 -->
<div class="quiz-block" markdown="1">
### question 7

which of the following commands cannot be used to get input from `stdin`?

<ul class="quiz-options">
  <li class="option">fgets()</li>
  <li class="option">read()</li>
  <li class="option">getc()</li>
  <li class="option correct" >strstr()</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b>
`fgets()` reads from a FILE* ptr, and stdin is a FILE* ptr. `read()` reads from file descriptors, and stdin is also a file descriptor. `getc()` takes an argument for a FILE* ptr. the only thing here is `strstr()`, which is essentially python's `.find()` method for strings. either way, `strstr()` can't read from file pointers or file descriptors, just compare two strings.
</div>
</div>
<hr>
<!-- QUESTION 8 -->
<div class="quiz-block" markdown="1">
### question 8

what is the output of the following program? (assume `long` is 64-bit, and assume we're on a 64-bit machine too)

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

<ul class="quiz-options">
  <li class="option">[3 large, unknown numbers]</li>
  <li class="option correct">10 [some large unknown number] 10</li>
  <li class="option">10 10 10</li>
  <li class="option">0 0 0</li>
</ul>
<div class="explanation" markdown=1><b>explanation:</b> in C, this is perfectly valid - we're casting the value of the _pointer_ to `a` as if it were a `long`. we're on a 64-bit machine so pointers are also 64-bit, the cast works out nice. the important thing here is that you don't actually lose any information as long as you're casting back and forth between the same sizes, hence the original value of `int a` remains at 10.
</div>
</div>
<hr>

<!-- question 9 -->
<div class="quiz-block" markdown="1">
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

<ul class="quiz-options">
  <li class="option correct">what's so good about picking up the pieces?</li>
  <li class="option">what's so good about picking up the pieces?\00</li>
  <li class="option">each character will be on a different newline</li>
  <li class="option">the loop won't terminate</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> for loops consist of three parts: the initialization, the condition, and the update. typically we see the standard format for a for loop as `int i = 0; i<SOME_BOUND; i++` but that condition can really be anything! recall that all strings (char bufs) are nullterminated, and a nullterminator is just a 0 byte which is falsy.
</div>
</div>
<hr>
<!-- QUESTION 10 -->
<div class="quiz-block" markdown="1">
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

<ul class="quiz-options">
  <li class="option">BcDeFg</li>
  <li class="option correct">BcDeFgHi</li>
  <li class="option">BcDeF</li>
  <li class="option">aBcDeFgHi</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> ok yeah soz this is _really_ tricky. we know that chars are just ints, but lowercase chars are also greater than uppercase chars, so when the xor 0x20 flips the case, the loop doesn't terminate. we also have to keep in mind that the loop modifies the char _BEFORE_ printing the string, which is why the initial 'a' value doesn't get printed. finally, the conditional is `c <= 'g'`, NOT `c < g`; so if `c == 'g'` then the while loop still continues.
</div>
</div>
<hr>

<div class="quiz-block" markdown="1">
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

<ul class="quiz-options">
  <li class="option correct">raw</li>
  <li class="option">rawr\00\00\00\00\00</li>
  <li class="option">rawr\00sdlfkjsdlkfjsdkfl</li>
  <li class="option">rawr</li>
</ul>
<div class="explanation" markdown="1">
<b>explanation</b>: again, strings are all null terminated. `strncmp` only checks at _MAX_ the first n bytes (in this case, 7) but if both strings are null terminated _before_ n then it just exits out. in this case, only `raw` would fail the check because `strncmp` would try to compare raw's null terminator with rawr's last 'r' character.</div>
</div>
</div>
<hr>
<!-- QUESTION 12 -->
<div class="quiz-block" markdown="1">
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

<ul class="quiz-options">
  <li class="option">getc() doesn't take an argument</li>
  <li class="option">atoi() returns a char, breaking the format string</li>
  <li class="option correct">getc() returns a char, `atoi()` expects a char*</li>
  <li class="option">it works just fine</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> honestly the answer explains it better than i can here. we just have to remember that a char and char* are distinct. also, `atoi()` returns an integer.
  </div>
</div>
<hr>
<!-- QUESTION 13 -->
<div class="quiz-block" markdown="1">
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

<ul class="quiz-options">
  <li class="option">`awww.`, when `fopen` fails it is undefined behaviour.</li>
  <li class="option correct">`yay!`, when `fopen` fails it returns a nullptr.</li>
  <li class="option">this program won't compile as you can't compare a pointer with an integer.</li>
  <li class="option">this program won't compile because `doesnotexist.txt` does not exist.</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation</b>a null pointer is just the value 0, and you can compare the two perfectly fine. fopen will always return a null pointer when it fails.
</div>
</div>
<hr>
<!-- QUESTION 14 -->
<div class="quiz-block" markdown="1">
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

<ul class="quiz-options">
  <li class="option">snprintf(student->name, 16, "cane");</li>
  <li class="option" style="padding: 0px;">{%highlight c%}
char name[] = "cane";
for (int i = 0; name[i]; i++) {
  student->name[i] = name[i];
}{%endhighlight%}
</li>
  <li class="option correct">student->name = "cane";</li>
  <li class="option">memmove(student->name, "cane", 4);</li>
</ul>
<div class="explanation">
<b>explanation:</b> yeah no you just cant write assign arrays like this. everything else is perfectly valid (using snprintf, writing the char array byte by byte, and moving the actual memory w/ memmove) but array assignment is invalid.
</div>
</div>
<hr>
<!-- QUESTION 15 (BONUS) -->
<div class="quiz-block" markdown="1">
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

<ul class="quiz-options">
  <li class="option correct">a user can input `"%p"` and leak addresses on the stack</li>
  <li class="option">`fgets` does not account for the null terminator, the null byte will overflow</li>
  <li class="option">`sizeof(buf)` actually corresponds to the size of a `char*` pointer, only 8 bytes of input will be read</li>
    <li class="option">nothing is wrong it's completely fine</li>

</ul>
<div class="explanation">
<b>explanation:</b> do this year's cyberblitz in december to find out how you can pop a shell w/ just a format string exploit :p
</div>
</div>
<script>
document.addEventListener('DOMContentLoaded', function() {
  var options = document.querySelectorAll('.option');
  options.forEach(function(option) {
    option.addEventListener('click', function() {
      var block = event.currentTarget.closest('.quiz-block');
      console.log(block);
      if (block.classList.contains('answered')) return;
      block.classList.add('answered');
    });
  });
});
</script>
