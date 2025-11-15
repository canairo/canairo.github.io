---
layout: post
title: tuctf25 - misc/giovanna's microwave
date: 2025-11-15 05:40:00 +0800
---

recommended listening for this post is [aoi koi no daidaiiro no hi](https://www.youtube.com/watch?v=JK_hBk2f01k) by masudore


![func](/assets/functional.png)

it's an ocaml binary.

```
giovannas_microwave.exe: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=42a3344430e6a4ca6ae88c5b9ccb9928a4028dbd, for GNU/Linux 3.2.0, stripped
```

handwaving away around 4 hours of painful, clueless reversing of me just fumbling around blindly we isolate the important checks here, in the `evaluate_2083` function:

```bash
----------------------------------- code: x86:64 (gdb-native) ----
    0x5555557d0963 4889c7                <camlGiovannas_microwave__Recipe.evaluate_2083+0x23>   mov    rdi, rax
    0x5555557d0966 48897c2410            <camlGiovannas_microwave__Recipe.evaluate_2083+0x26>   mov    QWORD PTR [rsp+0x10], rdi
    0x5555557d096b 488b5c2408            <camlGiovannas_microwave__Recipe.evaluate_2083+0x2b>   mov    rbx, QWORD PTR [rsp+0x8]
*-> 0x5555557d0970 480fb643f8            <camlGiovannas_microwave__Recipe.evaluate_2083+0x30>   movzx  rax, BYTE PTR [rbx - 0x8]
    0x5555557d0975 488d15b4f63900        <camlGiovannas_microwave__Recipe.evaluate_2083+0x35>   lea    rdx, [rip + 0x39f6b4] # 0x555555b70030
    0x5555557d097c 48630482              <camlGiovannas_microwave__Recipe.evaluate_2083+0x3c>   movsxd rax, DWORD PTR [rdx + rax * 4]
    0x5555557d0980 4801c2                <camlGiovannas_microwave__Recipe.evaluate_2083+0x40>   add    rdx, rax
    0x5555557d0983 ffe2                  <camlGiovannas_microwave__Recipe.evaluate_2083+0x43>   jmp    rdx
    0x5555557d0985 0f1f00                <camlGiovannas_microwave__Recipe.evaluate_2083+0x45>   nop    DWORD PTR [rax]
```

the checker iterates 112 times, and performs an operation according to these values near rbx:

```bash
------------------------------- memory access: $rbx-0x8 = 0x555555c60238 ----
      0x555555c60238|+0x0000|+000: 0x0000000000000b02
$rbx  0x555555c60240|+0x0008|+001: 0x0000000000000001
      0x555555c60248|+0x0010|+002: 0x000000000000001f
      0x555555c60250|+0x0018|+003: 0x0000000000000b00
```

the value at `$rbx-0x8` is an opcode mapping, and the other two values are indices. due to strange ocaml nonsense (i'm still not sure why), the indices need to be integer divided by 2 beforehand (so `0x01` actually becomes `0x00`, `0x1f` becomes `0xf`).

there are six possible values of `$rbx-0x8`:

```
- b00 : add
- b01 : subtract
- b02 : multiply
- b03 : divide 
- b04 : xor 
- b05 : ??? (i actually never figured this one out)
```

the flag checker operates like so: we read our opcode given the mapping at `$rbp-0x8`, index into our flag at the specified indices, perform the operation, and then compare against... what exactly?

a further 2 hours of painful annoying reversing through fucking ocaml (WHY IS IT IN OCAML) we isolate the compare check somewhere here in the `fun_2710` func:

```
    0x5555557d0c4f 488b1c24              <camlGiovannas_microwave__Recipe.fun_2710+0x1f>   mov    rbx, QWORD PTR [rsp]
*-> 0x5555557d0c53 4839d8                <camlGiovannas_microwave__Recipe.fun_2710+0x23>   cmp    rax, rbx
    0x5555557d0c56 0f94c0                <camlGiovannas_microwave__Recipe.fun_2710+0x26>   sete   al
    0x5555557d0c59 480fb6c0              <camlGiovannas_microwave__Recipe.fun_2710+0x29>   movzx  rax, al
    0x5555557d0c5d 488d440001            <camlGiovannas_microwave__Recipe.fun_2710+0x2d>   lea    rax, [rax + rax * 1 + 0x1]
    0x5555557d0c62 4883c408              <camlGiovannas_microwave__Recipe.fun_2710+0x32>   add    rsp, 0x8
    0x5555557d0c66 c3                    <camlGiovannas_microwave__Recipe.fun_2710+0x36>   ret
```

`rbx` is the value we compare to, and `rax` is the result of our opcode (also due to ocaml nonsense, before we get to this point we do a `shl`, an `inc`, and a `idiv` (which just takes it mod `0x100`) on our `rax` value).

if `rax` isn't equal to `rbx` at any point in time, the program prematurely exits out, i am assuming once again due to ocaml nonsense. anyways so we need to place two breakpoints at both of those checks, dump the values we need, and also we need to set `rax` = `rbx` at the `cmp` check to continue execution

we do this with the following gdb script:

```py
import gdb

mapping = [
    '+', '-', '*', '%', '^', '???'
]

class CaptureRbxValues(gdb.Breakpoint):
    def __init__(self):
        super().__init__("*0x5555557d0c53", internal=True)
        self.iteration = 0
        self.rbx_values = []

    def stop(self):
        rbx_value = int(gdb.parse_and_eval("$rbx")) // 2
        self.rbx_values.append(rbx_value)
        self.iteration += 1
        print(f"expected value: {self.iteration}: $rbx = 0x{rbx_value:x} ({rbx_value})")
        gdb.execute(f"set $rax = $rbx", to_string=True)
        return False  # continue silently

class DumpNearbyRbx(gdb.Breakpoint):
    def __init__(self):
        super().__init__("*0x5555557d0970", internal=True)

    def stop(self):
        rbx = int(gdb.parse_and_eval("$rbx"))
        vals = []
        for off in (-8, 0, 8):
            addr = rbx + off
            val = int(gdb.parse_and_eval(f"*(long*){addr:#x}"))
            vals.append(val)
        func, op1, op2 = vals
        func = mapping[func%0x100]
        op1, op2 = op1//2, op2//2
        print(f'flag[{op1}] {func} flag[{op2}] % 0x100')
        return False 

bp_main = CaptureRbxValues()
bp_dump = DumpNearbyRbx()
```

running this script gives us the following output, which we just dump into z3.

```bash
flag[0] * flag[15] % 0x100
expected value: 1: $rbx = 0xf0 (240)
flag[1] ^ flag[24] % 0x100
expected value: 2: $rbx = 0x26 (38)
flag[2] + flag[31] % 0x100
expected value: 3: $rbx = 0x75 (117)
flag[3] * flag[28] % 0x100
expected value: 4: $rbx = 0x9c (156)
flag[4] + flag[8] % 0x100
expected value: 5: $rbx = 0x88 (136)
```

and below is our z3 script

```py
from z3 import *

s = Solver()
flag = [BitVec(f'flag_{i}', 8) for i in range(56)]
known_prefix = "TUDCTF{"
known_suffix = "}"

for i, char in enumerate(known_prefix):
    s.add(flag[i] == ord(char))
s.add(flag[55] == ord(known_suffix))

for i in range(7, 55):
    s.add(flag[i] >= 32)
    s.add(flag[i] <= 126)

constraints = [
    (flag[0] * flag[15], 0xf0),
    (flag[1] ^ flag[24], 0x26),
    (flag[2] + flag[31], 0x75),
    (flag[3] * flag[28], 0x9c),
    (flag[4] + flag[8], 0x88),
    (flag[5] * flag[42], 0xfa),
    (flag[6] + flag[7], 0xc7),
    (flag[7] + flag[23], 0x80),
    (flag[8] % flag[48], 0x1),
    (flag[9] % flag[15], 0x2d),
    (flag[10] + flag[33], 0x9b),
    (flag[11] % flag[28], 0xa),
    (flag[12] + flag[27], 0xa1),
    (flag[13] - flag[30], 0xed),
    (flag[14] * flag[20], 0x4c),
    (flag[15] ^ flag[29], 0x13),
    (flag[16] - flag[55], 0xb4),
    (flag[17] * flag[19], 0xb5),
    (flag[18] + flag[19], 0x92),
    (flag[19] * flag[45], 0x1c),
    (flag[20] % flag[8], 0x0),
    (flag[21] - flag[12], 0x2c),
    (flag[22] * flag[18], 0x24),
    (flag[23] - flag[31], 0x3),
    (flag[24] - flag[37], 0x10),
    (flag[25] + flag[5], 0x7a),
    (flag[26] - flag[12], 0x34),
    (flag[27] + flag[46], 0xcd),
    (flag[29] ^ flag[41], 0x6b),
    (flag[30] % flag[40], 0x3),
    (flag[31] - flag[21], 0xd2),
    (flag[34] ^ flag[37], 0x3c),
    (flag[35] - flag[29], 0xf3),
    (flag[36] + flag[4], 0x85),
    (flag[37] ^ flag[53], 0x50),
    (flag[38] + flag[24], 0xa3),
    (flag[39] % flag[28], 0xc),
    (flag[40] - flag[7], 0x28),
    (flag[41] - flag[28], 0x0),
    (flag[42] * flag[5], 0xfa),
    (flag[44] + flag[45], 0xd2),
    (flag[45] ^ flag[7], 0x28),
    (flag[46] * flag[24], 0xad),
    (flag[47] - flag[3], 0xff),
    (flag[48] ^ flag[26], 0x54),
    (flag[49] * flag[42], 0xbd),
    (flag[50] % flag[41], 0x0),
    (flag[51] ^ flag[48], 0x7),
    (flag[52] - flag[26], 0x6),
    (flag[53] * flag[44], 0xea),
    (flag[54] + flag[55], 0xe9),
    (flag[55] - flag[32], 0x9),
    (flag[0] % flag[33], 0x54),
    (flag[1] + flag[3], 0x98),
    (flag[2] ^ flag[31], 0x75),
    (flag[3] * flag[49], 0xe9),
    (flag[4] * flag[46], 0x2c),
    (flag[5] + flag[10], 0x79),
    (flag[6] * flag[35], 0x66),
    (flag[7] ^ flag[14], 0x13),
    (flag[8] - flag[52], 0xc7),
    (flag[9] * flag[29], 0xe7),
    (flag[10] - flag[16], 0x2),
    (flag[12] + flag[17], 0x9e),
    (flag[13] * flag[22], 0xb0),
    (flag[14] * flag[2], 0x3c),
    (flag[17] ^ flag[40], 0x1f),
    (flag[18] - flag[41], 0xff),
    (flag[19] + flag[38], 0x8f),
    (flag[20] % flag[27], 0x34),
    (flag[21] ^ flag[51], 0x6b),
    (flag[22] ^ flag[42], 0x13),
    (flag[23] - flag[10], 0x1),
    (flag[24] ^ flag[28], 0x47),
    (flag[25] * flag[42], 0x4c),
    (flag[26] + flag[29], 0xc6),
    (flag[27] ^ flag[24], 0x1d),
    (flag[28] - flag[9], 0xbb),
    (flag[29] + flag[28], 0x93),
    (flag[30] + flag[21], 0xd6),
    (flag[32] % flag[31], 0x12),
    (flag[34] * flag[50], 0x98),
    (flag[35] ^ flag[26], 0x35),
    (flag[36] - flag[37], 0xce),
    (flag[37] % flag[32], 0x63),
    (flag[39] ^ flag[51], 0x40),
    (flag[40] + flag[26], 0xdb),
    (flag[41] - flag[45], 0xd0),
    (flag[42] + flag[47], 0xa1),
    (flag[43] + flag[13], 0x98),
    (flag[44] ^ flag[54], 0x2),
    (flag[45] ^ flag[54], 0x8),
    (flag[46] - flag[18], 0x2c),
    (flag[47] % flag[35], 0x42),
    (flag[49] % flag[9], 0x63),
    (flag[51] - flag[53], 0x1),
    (flag[52] + flag[23], 0xa1),
    (flag[53] - flag[50], 0xcb),
    (flag[54] + flag[55], 0xe9),
    (flag[55] + flag[38], 0xad),
]

for expr, expected in constraints:
    s.add((expr & 0xFF) == expected)

if s.check() == sat:
    m = s.model()
    result = ''.join(chr(m[flag[i]].as_long()) for i in range(56))
    print(f"Flag: {result}")

```
anyways run it to get the flag

`Flag: TUDCTF{L4y3r3d_L1k3_4_L4s4gn4_w1th_R1c0tt4_4nd_B3ch4m3l}`
