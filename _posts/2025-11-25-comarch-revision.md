---
layout: post
title: profcane's comarch revision
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

this module got hands i fear

![nunu](https://i.imgur.com/UtAhZPq.png)

### theory questions
<!--
<div class="quiz-block" markdown=1>
### question n

  <ul class='quiz-options'>
    <li class='option'></li>
    <li class='option'></li>
    <li class='option'></li>
    <li class='option'></li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  
  </div>
</div>
-->
<div class="quiz-block" markdown=1>
### question 1 

select the correct option about SRAM and DRAM.

  <ul class='quiz-options'>
    <li class='option'>SRAM is a lot less space efficient as it uses 1 capacitor and 1 transistor, compared to how DRAM uses 6 transistors.</li>
    <li class='option'>DRAM's read operations are destructive because the memory is stored as charge in the transistor, which gets drained whenever it is accessed.</li>
    <li class='option correct'>SRAM's read operations are not destructive because the latch does not get its energy drained when it is read.</li>
    <li class='option'>to read from SRAM or DRAM, we first activate the memory cell via the bitline, and then read the data from the word line.</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  <b>opt 1:</b> tembalik<br>
  <b>opt 2:</b> charge is stored in the capacitor<br>
  <b>opt 3:</b> correct - if the latch remains powered, then the latch retains its state.<br>
  <b>opt 4:</b> tembalik
  </div>
</div>

<hr>

<div class="quiz-block" markdown=1>
### question 2 

a sensor has to send readings to a remote computer. the sensor sends the data bits, 4 error-correction bits and 2 stop bits. the baud rate is 284 000. if the remote computer is able to receive 240 000 data values a minute, then: 
  <ul class='quiz-options'>
    <li class='option'>65 data bits are used.</li>
    <li class='option'>63 data bits are used.</li>
    <li class='option correct'>64 data bits are used.</li>
    <li class='option'>it's impossible to tell.</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
240 000 values a minute is 4 000 a second. this means that 284 000 bits are used to transmit 4 000 "frames" of valid data, meaning that a frame has 71 bits in total. we subtract the non-data bits:<br>
71 total bits - 1 start bit - 4 error-correction bits - 2 stop bits = 64 data bits.<br>
tricky part here is that this is a serial communication so a stop bit necessarily implies the existence of a start bit.
  </div>
</div>


<div class="quiz-block" markdown=1>
### question 3 

which of the following is true about serial / parallel communications?

  <ul class='quiz-options'>
    <li class='option'>a disadvantage of serial communications is that serial communications do not have crosstalk, while parallel communications do.</li>
    <li class='option'>a parallel communication necessarily cannot be full-duplex.</li>
    <li class='option'>for a parallel communication to transmit all of its bits, it must be synchronized with a shared clock signal.</li>
    <li class='option correct'>data transfer within the data bus on an MSP430 is parallel.</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  opt 1: crosstalk is a _disadvantage_ of parallel communication (it is when the parallel signals interfere with one another)<br>
  opt 2: parallel communications can be simplex, half-duplex, full-duplex, whatever, it dont matter<br>
  opt 3: this assumes that parallel communications must be synchronised, they can also be asynchronous<br>
  opt 4: this is correct, if it were serial it wouldnt need to have a certain 'bit-width'
  </div>
</div>

<hr>

<div class="quiz-block" markdown=1>
### question 4

select the correct option about memory access on a hard-drive.

  <ul class='quiz-options'>
    <li class='option'>seek time is the amount of time it takes for the disk to rotate until the head reaches the correct track.</li>
    <li class='option'>rotational delay is the amount of time it takes for the head to move until the head reaches the start of the correct sector.</li>
    <li class='option'>access time is the amount of time taken from the start of the request, to all the data being transferred.</li>
    <li class='option correct'>rotational delay can be calculated as 60/2N, where N is rotations per minute.</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  remember that tracks are arranged in concentric rings, and that sectors are small circular 'sections' of each ring. seek time requires the head to move up and down along the diameter of the disk to reach the correct track, and rotational delay requires the disk to rotate such that the head is along the correct sector. access time is seek time + rotational delay, not counting transfer time. rotational delay is indeed 60/2N (the math checks out)
  </div>
</div>

<hr>

<div class="quiz-block" markdown=1>
### question 5 

a disk capable of storing 6 144 000 000 bytes can rotate 250 times in one second, has 6000 cylinders with 2 surfaces on each of its 4 platters, and a sector density of 128 bytes per sector. we can therefore assume: 
  <ul class='quiz-options'>
    <li class='option'>a track contains 1024 sectors.</li>
    <li class='option correct'>a track contains 1000 sectors.</li>
    <li class='option'>a track contains 512 sectors.</li>
    <li class='option'>nothing, as there's not enough information to determine anything about the tracks.</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  first we calculate the number of tracks per cylinder, which is just 4x2 = 8 tracks per cylinder.
  then we have 6000 cylinders, meaning 6000*8 = 48 000 tracks on the disk in total. then, we calculate bytes per track, which is 6 144 000 000 bytes total / 48 000 tracks = 128 000 bytes per track. finally, we calculate sectors per track, which is 128 000 bytes/track / 128bytes/sector = 1 000 sectors. the 250RPS figure is actually entirely irrelevant here.
  </div>
</div>

<hr>

<div class="quiz-block" markdown=1>
### question 6 

a computer has 128 frames numbered {0... 127} and 256 pages numbered {0... 255}. consider the following relation f that maps all page numbers to frame numbers at some fixed point in time. this relation is:

  <ul class='quiz-options'>
    <li class='option'>an injective function. at a fixed point in time, all pages map to distinct frames.</li>
    <li class='option'>surjective. at a fixed point in time, all frames are mapped onto by a corresponding page.</li>
    <li class='option'>bijective. it is both injective and surjective.</li>
      <li class='option correct'>not a function at all, as some pages do not map to frame numbers.</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  functions jumpscare!!! the key concept here is that when a page is on the disk, it does not have a corresponding frame number. therefore, there exists some X within our defined range {0...255} such that f(x) is undefined, breaking the definition of a function. 
  </div>
</div>

<hr>

<div class="quiz-block" markdown=1>
### question 7

i have a hard drive that rotates at 60000RPM, with 4096 bytes per sector and 1024 sectors per track. due to my poor memory management habits, my 128MB Neon Genesis Evangelion - Episode 24.mp4 file is _extremely_ fragmented, with each sector being randomly distributed across a single surface of my hard drive (assume that the surface is big enough to hold all 128Mb). assume that the average seek time is 5ms, and i want to watch that Evangelion episode to get clips for my Kawoshin AMV - how long will it take for the episode to be transferred in full?

  <ul class='quiz-options'>
    <li class='option correct'>around 3 minutes</li>
    <li class='option'>around 30 seconds</li>
    <li class='option'>around 1 minute</li>
    <li class='option'>around 2 minutes and 30 seconds</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  first we calculate the average access time for a random sector. we do this by adding seek time, rotational delay, and transfer time. rotational delay is 60/2N = 0.005 seconds = 0.5ms. transfer time is time taken to rotate 1/1024th of the disk, so that is 60/1024N = 0.97 _microseconds_, which is negligible but we account for it anyway. // total time is 5 + 0.5 + 0.0009 = 5.5009. then we calculate the number of sectors needed to store the file, which is 128MB / 4096B per sector = 32768 sectors.
  we multiply the two values: 32768 sectors * 5.5009ms to locate each sector = 180.224seconds, which is around 3 minutes.
  </div>
</div>


<div class="quiz-block" markdown=1>
### question 8 

select the correct option about a RAID system.
  <ul class='quiz-options'>
    <li class='option'>RAID 10 has faster write times than RAID 0.</li>
    <li class='option'>a RAID 0 system with 6 drives (with a total storage of 60GB) is only able to effectively use 10GB of storage</li>
    <li class='option'>a RAID 1 system uses 10 drives, with the smallest drive having a capacity of 6GB and the biggest drive having a capacity of 1TB. the effective storage is 1TB.</li>
    <li class='option correct'>a RAID 10 system uses 10 drives of size 1GB. the effective storage is 5GB.</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  <b>opt 1:</b> RAID 10 needs to also write to its mirrors, so the write times are slower.<br>
  <b>opt 2:</b> RAID 0 uses all the storage via striping, so it can store all 60GB.<br>
  <b>opt 3:</b> in mirroring, you are limited by thes smallest size - the effective storage is 6GB.<br>
  <b>opt 4:</b> 10 drives -> 5 mirrors, each w/ 1GB, so 5*1 = 5GB (correct).
  </div>
</div>
<hr>

<div class="quiz-block" markdown=1>
### question 9 

the Gameowboy is a simple TinyScreen based console able to connect to a server. twenty times every second, the console requests for the current game state from the server, and then renders the game state to the screen. at any point in time, the user can press any of the buttons on the controls, which triggers the Gameowboy to send a corresponding input packet to the server. which of the following is true?

  <ul class='quiz-options'>
    <li class='option'>both the server and the controls are being polled by the Gameowboy.</li>
    <li class='option'>the Gameowboy processes the server game state based on interrupts, and polls the control system.</li>
    <li class='option'>both the server and the controls are interrupt-based.</li>
    <li class='option correct'>the Gameowboy polls the server, and handles controls based on interrupts.</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  'at any point in time' indicates that the button controls are being handled asynchronously, indicating an interrupt-based system. the server is requested for the Game State twenty times a second, indicating a poll-based system.
  </div>
</div>

<hr>

<div class="quiz-block" markdown=1>
### question 10 

two bluetooth devices are communicating to each other in a room. inside the room is a ham radio that interferes with any 2.3Ghz signal. the implications of this are:
  <ul class='quiz-options'>
    <li class='option'>a small percentage of bluetooth packets will be interfered with.</li>
    <li class='option'>all bluetooth packets will be interfered with.</li>
    <li class='option correct'>no bluetooth packets will be interfered with.</li>
    <li class='option'>impossible to tell.</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  bluetooth transmits at 2.4GHz, which is a frequency that the radio will not interfere with. 
  </div>
</div>

<hr>

<div class="quiz-block" markdown=1>
### question 11
  
regarding calling conventions on the msp430, which one is true?
  <ul class='quiz-options'>
    <li class='option'>if i want to pass variables through the registers, i must do so by reference and not by value in all cases.</li>
    <li class='option'>if i want to pass variables through the registers, my upper bound for variables i can pass is the number of registers on the msp430 (which is 16).</li>
    <li class='option'>if i want to pass variables through the stack, my subroutine must push them onto the stack for my caller to pop from the stack during the subroutine itself.</li>
    <li class='option correct'>if i want to pass variables through memory, i can pass in arbitrary length parameters, as long as it fits within the amount of memory i have allocated.</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  <b>opt 1</b> still can pass by value just as long as the value can fit in the register<br>
  <b>opt 2</b> cant use the reserved registers (r0 - r3)<br>
  <b>opt 3</b> tembalik (subroutine pop, caller push)<br>
  <b>opt 4</b> correct for the reasons listed in the answer
  </div>
</div>

<hr>


<div class="quiz-block" markdown=1>
### question 12 

my brand new operating system based entirely on cat meows, RawrOS, allocates memory as follows: given a request for memory, it finds a contiguous region of physical memory of the correct size that can fit the request, and then marks off that chunk of contiguous memory accordingly. which of the following is true about RawrOS?
  <ul class='quiz-options'>
    <li class='option'>RawrOS would need to manage a page table.</li>
    <li class='option correct'>every once in a while, RawrOS should compact allocated chunks of physical memory to prevent fragmentation.</li>
    <li class='option'>RawrOS employs fixed partitioning.</li>
    <li class='option'>to manage memory, RawrOS has to translate logical addresses into physical addresses.</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  the scheme that RawrOS is described as using is _dynamic partitioning_, which is vulnerable to external fragmentation. only option 2 is confirmed to apply (RawrOS might be so simple that it would just use physical addresses directly, e.g.)   
  </div>
</div>

<hr>

<div class="quiz-block" markdown=1>
### question 13

the following stream of bits is received over a serial communication.

```
111110000011111001001110101111011010011001101011000110101000011110011101111010100110111
```

the receiver correctly decodes this message as 'profcane' in ASCII. which of the following specifications is true?

  <ul class='quiz-options'>
    <li class='option'>LSB first, 7 data bits, odd parity, 1 stop bit</li>
    <li class='option'>MSB first, 8 data bits, even parity, 1 stop bit</li>
    <li class='option'>LSB first, 8 data bits, even parity, 2 stop bits</li>
    <li class='option correct'>LSB first, 7 data bits, even parity, 1 stop bit</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  idk how to explain this in a way that isnt just 'eyepower'. we can just break down the packet format: first `11111` is idle, then `0` start, then `0000111` (p in ASCII w/ LSB first), then parity bit is `1` so we know its even parity, then 1 stop bit until we go again. 
  </div>
</div>

<hr>

<div class="quiz-block" markdown=1>
### question 14 

which of the following is true about bluetooth classic?

  <ul class='quiz-options'>
    <li class='option'>you can have a maximum of 255 slave devices sending and receiving data to a master device.</li>
    <li class='option correct'>if the master takes 200 microseconds to transmit a packet from the beginning of the timeslot, the slave will wait 425 microseconds before sending its own.</li>
    <li class='option'>TDD is the mechanism used by bluetooth devices to prevent interference by other transmitters on the same frequency.</li>
    <li class='option'>bluetooth communication is full duplex as a device can both transmit and receive data within the timeframe of a second.</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  <b>opt 1</b>: an active device is one that is sending data, and a master can only support 7 active slave devices.<br>
  <b>opt 2</b>: slots are 625 microseconds long so this is true<br>
  <b>opt 3</b>: this is frequency hopping and not TDD<br>
  <b> opt 4</b>: bluetooth is half duplex, it cannot transmit and receive at the same _instant_ (hence the division of transmissions into 625 microsecond slots)
  </div>
</div>

<hr>

<div class="quiz-block" markdown=1>
### question 15

on the MSP430, `P1IN` is initially `10110100`. afterwards, `P1DIR` is set to `00111100`, and `P1OUT` is set to `10101010`. `P1IN` is now:
  <ul class='quiz-options'>
    <li class='option correct'>10101000</li>
    <li class='option'>10101010</li>
    <li class='option'>10111110</li>
    <li class='option'>11111111</li>
  </ul>

  <div class='explanation' markdown=1>
  <b>explanation:</b><br>
  that P1DIR setting now means the middle 4 bits of P1IN will now be changed according to P1OUT, while the rest stay the same. this means that P1IN is now 10(1010)00, where parentheses mark the bits affected by the new P1OUT values, and everything outside of that is unaffected.
  </div>
</div>

<hr>

### asm related questions

<div class="quiz-block" markdown="1">
### question 16

here is a layout of memory + some registers. which of the following statements is true?

```
0x4000: 0x1024
0x4002: 0x0000
0x4004: 0x2346
0x4006: 0x2355
0x4008: 0xdead
0x4010: 0xbeef

R1: 0x4006
R9: 0xcafe
  ```

  <ul class="quiz-options">
  <li class="option">after `pop r9; pop r9`, r9 will contain `0x0000`</li>
  <li class="option correct">after `push r9;` the byte at 0x4005 will be 0xca</li>
  <li class="option">after `nop;`, no register content will change</li>
  <li class="option">after `add.w #0x01h, R1`, the MSP430 detects that R1 should be word aligned and does not increment it</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b>

recall a few things: that the stack grows downward, that r0 is the program counter, that r1 is the stack pointer, and finally, that the msp430 is little endian. we can then conclude:<br>
1. sp will _increase_ and not decrease when `pop` instrs occur, so popping into r9 twice will decrement SP from 0x4006 to 0x4008. the value at r9 will actually be `0xdead`.<br>
2. push r9 will push the value `0xcafe` onto the stack, and given endianness, the byte at `0x4004` will be the LSB `0xfe`, and the byte at `0x4005` will be the MSB `0xca`. correct!<br>
3. the program counter is a register! `nop` will increase it. (`nop` is actually just an emulated instruction that performs `mov.w #0, R3`)<br>
4. by right the stack pointer _should_ be word aligned but its not enforced on the hardware level the same way that the program counter's alignment is (if you try to do something like `mov.w 0x4555, PC`, PC will end up being 0x4554).
</div>
</div>
<hr>

<div class='quiz-block' markdown="1">

### question 17

which of the following is a true statement about this following code? (assume Vdata is defined.)

```
start:
  mov.w #Vdata, r8
  xor.w r9, r9
loop:
  cmp.w #10h, r9
  je start
  xor.w #0042h, @r8+
  inc.w r9
  jmp loop
```


<ul class='quiz-options'>
  <li class='option'>this will correctly execute, xoring the first 16 words in Vdata by 0x42.</li>
  <li class='option correct'>this won't compile because of the xor.w #0042h, @r8+ instruction.</li>
  <li class='option'>this will loop infinitely within the `loop` label and never go back to start.</li>
  <li class='option'>this won't compile because of the mov.w #Vdata, r8 instruction.</li>
</ul>
<div class="explanation">
<b>explanation</b><br>
register indirect mode is only valid for src, not for dst. if we replace those instructions w/ a `xor.w #0042h, 0(r8)`, and an `incd.w r8` then the loop will run correctly (xoring the first 16 words in Vdata by 0x42)
</div>
</div>
<div class="quiz-block" markdown="1">

### question 18

here are four pairs of commands. which of these pairs of commands will result in the exact same register states at the end of execution (disregarding PC)?

  <ul class="quiz-options">
  <li class="option correct">pop r9, and mov.w @sp+, r9</li>
  <li class="option">xor r9, r9 and mov r9, r8; sub r9, r8</li>
  <li class="option">mov.b r9, r8; xor.w r8, r9 and xor.b r9, r9</li>
  <li class="option">mov @sp-, pc and ret</li>
</ul>
  <div class="explanation" markdown=1>
  <b>explanation:</b><br>
  1. recall that pop takes the value at (sp), moves it to the destination, and then increments sp by 2. that's what mov.w @sp+ does, indirect autoincrement will increment by 2 due the instruction being a word instruction (and not a byte instruction).<br>
  2. xor r9, r9 zeroes out the r9 register while sub r9, r8 (when r9 and r8 are the same) zeroes out the r8 register, as r8 is the destination and r9 is the source. r9 remains unaffected, of course.<br>
  3. xor.b r9, r9 will zero out the whole register. in general, byte-operations on registers will completely zero out the top byte of the register.<br>
  4. almost: mov @sp+, pc; not mov @sp-, pc :P
  </div>
</div>

<hr>

<div class="quiz-block" markdown="1">
### question 19

the program counter is at `0x4400`, and the disassembler has interpreted the instruction at `0x4400` as `mov @r10, 2(r11)`. the byte at `0x4401` is:

  <ul class="quiz-options">
  <li class="option correct">4a</li>
  <li class="option">02</li>
  <li class="option">ab</li>
  <li class="option">00</li>
</ul>
  <div class="explanation" markdown=1>
  <b>explanation:</b><br>
the mapping is as follows:

```
--------------------------------------------------
 DOUBLE OP   	mov.w @r10, X(r11)
--------------------------------------------------
 BINARY MAP  	0100101010101011
--------------------------------------------------
[OPCODE]   	0100............	mov
[SRC_REG]  	....1010........	r10 -> register indirect
[AD_MODE]  	........1.......	bit:1 -> indexed
[B/W]      	.........0......	word
[AS_MODE]  	..........10....	bits:10 -> register indirect
[DST_REG]  	............1011	r11
```

in bytes, this is `0x4aab`. but due to endianness, the byte at `0x4400` will be `ab`, and the byte at `0x4401` will be `4a`. (the next word at `0x4402` will be the value `0x0002`.)
  </div>
</div>

<hr>

<div class="quiz-block" markdown="1">
### question 20

which of the following incorrectly maps the emulated instruction to its 'actual' instruction?

  <ul class="quiz-options">
  <li class="option correct">incd.w r11 and add.b #2, r11</li>
  <li class="option">mov.w @r1+, r11 and pop r11</li>
  <li class="option">rla.w r11 and add.w r11, r11</li>
  <li class="option">mov.w r11, r0 and br r11;</li>
</ul>
  <div class="explanation" markdown=1>
  <b>explanation:</b><br>
byte/word mismatch :p the rest are correct:<br>
opt 2: to pop off the stack you first move the value at the addr ref'd by the stack ptr, then increment the stack pointer.<br>
opt 3: a rotate-left without carry bit equivalent to multiplying by two. the msp430 does not have multiplication instructions.<br>
a branch statement is equivalent to just modifying the PC to whatever value you want.<br>
  </div>
</div>

<hr>

<div class="quiz-block" markdown="1">
### question 21

the word at the address referenced by the program counter is currently `0x3ff9`. this is a:
  <ul class="quiz-options">
  <li class="option">jump backwards by 14 words</li>
  <li class="option">jump forwards by 14 bytes</li>
  <li class="option">jump forwards by 14 words</li>
  <li class="option correct">jump backwards by 14 bytes</li>
</ul>
  <div class="explanation" markdown=1>
  <b>explanation:</b><br>

```
--------------------------------------------------
JUMP OP     	jmp $ -14
--------------------------------------------------
BINARY MAP  	0011111111111001
--------------------------------------------------
[PREFIX]   	001.............	(fixed)
[COND]     	...111..........	jmp
[OFFSET]   	......1111111001	Decimal: -7
```

the last 10 bits of the 16-byte instruction are a twos complement number referring to the number of _words_ in the jmp instruction. in this case, that number is -7, so -7 words is -14 bytes, and negative means a backwards jump.
  </div>
</div>

<hr>

<div class="quiz-block" markdown="1">
### question 22

assume .data starts at `0xc008`. which statement is true?

```
.data
Vdata  .word 0xdead, 0xbeef, 0xcafe, 0xdeed
```

  <ul class="quiz-options">
  <li class="option">the byte at 0xc008 is 0xde.</li>
  <li class="option">the byte at 0xc00a is 0xbe.</li>
  <li class="option">the byte at 0xc00c is 0xbe.</li>
  <li class="option correct">the byte at 0xc00e is 0xed.</li>
</ul>
  <div class="explanation" markdown=1>
  <b>explanation:</b><br>

```
(mspdebug) md 0xc008
0c008: ad de ef be fe ca ed de
```

just be careful with endianness and count properly.
  </div>
</div>

<hr>

<div class="quiz-block" markdown="1">
### question 23

consider the following ASM code, where X is an arbitrary 4 bit integer.

```
    mov.w [X], r4
    xor.w r5, r5
    xor.w r6, r6
loop_start:
    add.w r4, r6
    inc.w r5
    cmp r5, r4
    jne loop_start
  ```

after the program finishes execution, which of the following will be true? 

  <ul class="quiz-options">
  <li class="option">r6 will contain X.</li>
  <li class="option">the loop will never terminate.</li>
  <li class="option">r6 will contain 2X.</li>
  <li class="option correct">r6 will contain X^2.</li>
</ul>
  <div class="explanation" markdown=1>
  <b>explanation:</b><br>
we can just convert this into the following python code:

```py
def func(r4):
  r5 = 0
  r6 = 0
  while r5 != r4:
    r6 += r4
    r5 += 1
  return r4
```

note that r4 remains unchanged, and we are repeatedly adding r6 to r4, r4 times. so, indeed, we are _squaring_ r4.
  </div>
</div>

<hr>

<div class="quiz-block" markdown="1">
### question 24

which of the following is true about subroutine calls on the MSP430?

  <ul class="quiz-options">
  <li class="option">assuming that a subroutine returns to the correct address, the value of SP just before the subroutine call and just after the subroutine call must always be the same.</li>
  <li class="option">for a subroutine with only one word-sized parameter, the best choice (in terms of saving clock cycles) is to pass the parameter through memory.</li>
  <li class="option">subroutines can never call other subroutines because the RET address on the stack will be altered.</li>
  <li class="option correct">a RET takes less clock cycles than a RETI.</li>
</ul>
  <div class="explanation" markdown=1>
  <b>explanation:</b><br>
opt 1: a function call necessitates pushing the return address onto the stack, and a function return necessitates popping that same return address off of the stack. consider the following asm:

```
main:
    call #subroutine

subroutine:
    mov.w @sp, R10
    push R10
    ret
    ```

this will still return to the correct address because the top of the stack _still_ contains the correct return address. of course, this is highly unconventional but it's still within the bounds of defined MSP430 behaviour.<br>
opt 2: just pass by register. memory access will waste a clock cycle.<br>
opt 3: u can nest subroutine calls it wont break anything. the return addresses will keep getting saved, just as long as you dont nest like 5000 subroutine calls and overflow the memory allocated to the stack<br>
opt 4: a RETI has to save SR on the stack, RETI doesnt. (correct)
  </div>
</div>

<div class="quiz-block" markdown="1">
### question 25
which of these takes the fewest amount of clock cycles?

  <ul class="quiz-options">
  <li class="option">cmp.w 2(r9), r10</li>
  <li class="option">mov.w #1234h, 0(R10)</li>
  <li class="option correct">add.w @R10+, R11</li>
  <li class="option">add.w @R10, &3500h</li>
</ul>
  <div class="explanation" markdown=1>
  <b>explanation:</b><br>
opt 3 takes 2 clock cycles, 1 clock cycle to fetch the instr and 1 clock cycle to increment the value in the register while simultaneously reading from the address stored at R10. everything else takes more. (in the interest of honesty i'm actually not sure as to the clock cycle counts for the rest, i just know that it's More)
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
