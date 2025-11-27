---
layout: post
title: comarch
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

i fucking hate this mod

![wow](https://i.imgur.com/Fke3ugE.png)

### theory section

<div class="quiz-block" markdown="1">
### question 1

select the correct statement about frames and pages.

<ul class="quiz-options">
  <li class="option">a page is a section of physical memory, while a frame is a section of virtual memory.</li>
  <li class="option correct">at any given point in time, the actual data stored in a page could either lie in the memory or on the secondary memory.</li>
  <li class="option">when a program is split into pages, the pages may not form a contiguous section, but the corresponding frames always form a contiguous section.</li>
  <li class="option">you can have more frames than pages, but not more pages than frames.</li>
</ul>


<div class="explanation" markdown=1>
<b>explanation:</b><br>
opt 1: tembalik<br>
opt 2: correct, this is the reason why you can have more pages than frames (i.e. more logical memory than physical memory. logical memory can also correspond to secondary memory when its not currently being used)<br>
opt 3: neither the frames nor the pages form a contiguous section that's what paging is for<br>
opt 4: tembalik
</div>

</div>
<hr>
<!-- QUESTION 2 -->
<div class="quiz-block" markdown="1">
### question 2

which of the following is true?

<ul class="quiz-options">
  <li class="option">an advantage that parallel ports have over serial interfaces is that parallel ports can have crosstalk.</li>
  <li class="option">half-duplex transmission implies that a device can receive input and output simultaneously.</li>
  <li class="option correct">if an asynchronous transmission of a single ascii character with odd parity has exactly two data bits flipped in transmission, the parity bit cannot be used to detect there was an error.</li>
  <li class="option">if an interface is asynchronous, it cannot be full-duplex.</li>
</ul>

<div class="explanation" markdown=1>
<b>explanation</b><br>
opt 1: crosstalk is an _undesirable_ artifact of transmission, it cannot be advantageous.<br>
opt 2: the devices involved in a half duplex transmission can receive input and output, just _not_ simultaneously<br>
opt 3: the parity bit can only detect if an odd number of bits were flipped during transmission.<br> 
opt 4: you can treat each of the following characteristics as entirely separate dimensions: simplex-duplex, synchronous-asynchronous, and parallel-serial. they're entirely separate things. 

</div>
</div>

<hr>
<div class="quiz-block" markdown="1">
### question 3

which of the following is true?

  <ul class="quiz-options">
  <li class="option">compaction is a technique used in paging.</li>
  <li class="option">external fragmentation is a complication introduced by fixed-size partitioning.</li>
  <li class="option">swapping occurs between secondary memory and cache memory.</li>
  <li class="option correct">the cpu will always read from cache memory, never from primary memory.</li>
</ul>
<div class="explanation" markdown="1">
<b>explanation:</b><br>
opt 1: it's a technique used in dynamic partioning<br>
opt 2: fixed-size partitioning's problem is internal fragmentation and not external<br>
opt 3: swapping occurs between secondary memory and primary memory not cache memory<br>
opt 4: true - if the memory being requested isnt present in cache, the cache controller will first pull it from the cache, and then the cpu will read it from there.
</div>
</div>
<hr>


<div class="quiz-block" markdown="1">
### question 4

select the option which correctly pairs the following:

<ul class="quiz-options">
  <li class="option">keyboard: CPU-polled</li>
  <li class="option">usb: simplex</li>
  <li class="option"></li>
  <li class="option correct"></li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> very tricky question. in SQL the syntax of '=' indicates that the subquery only returns one row, and if it did, it would error out, but the question states that it executes successfully.
</div>
</div>
<hr>
<!-- QUESTION 5 -->
<div class="quiz-block" markdown="1">

### question 5

a music fan wants to create an entity-relationship diagram of their favorite bands. assume a band can create many albums, an album can contain many songs, and a song can 'feature' exactly one other band. which of the following is an incorrect assumption, based off of the information provided?

<ul class="quiz-options">
  <li class="option">we can create a Feature table to model the relation, using the primary key of Band and the primary key of Song as foreign keys</li>
  <li class="option correct">we can add a Feature column to the Songs table to model the relation, specifying that the Feature column must not be NULL</li>
  <li class="option">the cardinality of the Feature relation is many to one</li>
  <li class="option">a Band can Feature in multiple songs off of the same Album</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> note that we say a song _can_ feature another Band, not that it _must_. therefore, our Feature column can be NULL.
  </div>
</div>
<hr>

<!-- QUESTION 6 -->
<div class="quiz-block" markdown="1">
### question 6

which of the following algorithms would have exponential time complexity?

<ul class="quiz-options">
  <li class="option correct">iterating through all memory addresses on an N-bit processor</li>
  <li class="option">iterating through all I rows and J columns of a database with K tables</li>
  <li class="option">iterating through each number less than N to test for the primality of N</li>
  <li class="option">locating an element in a hashmap with 2^N elements</li>
</ul>

<div class="explanation" markdown=1>
<b>explanation:</b> remember your comarch! an N-bit processor will have 2^N memory addresses.
</div>
</div>
<hr>

<!-- QUESTION 7 -->
<div class="quiz-block" markdown="1">
### question 7

alice wants to send bob a message, and both alice and bob have valid RSA keypairs. alice and bob also share a secret K which no other people know. eve is a malicious eavesdropper who can read their transmissions. which of the following is true?

<ul class="quiz-options">
  <li class="option">if alice encrypts her message with her private key and transmits it, eve cannot read it but bob can.</li>
  <li class="option">if eve receives a message digitally signed with the secret K, she can be sure it is from alice.</li>
  <li class="option">if alice encrypts her message with her public key and transmits it, only bob can read it.</li>
  <li class="option correct" >if bob is able to decrypt a received message with alice's public key, he can be sure it is from alice.</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> option 1 is wrong because eve can decrypt with alice's public key. option 2 is wrong because the message could be from bob too (both share the secret K). option 3 is wrong because nobody except alice would be able to decrypt it. option 4 is correct because if bob can decrypt the message with alice's public key, that means the message was encrypted with alice's private key.
</div>
</div>
<hr>

<!-- QUESTION 8 -->
<div class="quiz-block" markdown="1">
### question 8

program A takes 10 seconds to compute 100 inputs, 50 seconds to compute 500 inputs, and 200 seconds to compute 2000 inputs. program B takes 1 second to compute 100 inputs, 4 seconds to compute 200 inputs. and 16 seconds to compute 400 inputs. for what number of inputs will their running times coincide? (ignore the trivial solution of 0 inputs)

<ul class="quiz-options">
  <li class="option">it will never coincide</li>
  <li class="option correct">1000</li>
  <li class="option">10000</li>
  <li class="option">500</li>
</ul>
<div class="explanation" markdown=1><b>explanation:</b>
program A is linear while program B is quadratic. running time of each program can be expressed as some f_i(n) where n is the number of inputs. f_a(n) = n/10, f_b(n) = n^2/10000. you can solve this as a quadratic or whatever but option 2 is correct here
</div>
</div>
<hr>

<!-- question 9 -->
<div class="quiz-block" markdown="1">
### question 9

which of these is true (assume that we want our resulting scheme to be secure and functional)?

<ul class="quiz-options">
  <li class="option">you can pick any size matrix to use as a hill cipher key, as long as it is square</li>
  <li class="option correct">you cannot pick any plaintext to encrypt for RSA</li>
  <li class="option">you can pick any number N to use in RSA, as long as it is above what can be feasibly factored (typically >512 bit)</li>
  <li class="option">you can pick any length of key for AES or DES, as long as it is at least 64 bit</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> option 1 is wrong - the key must be an invertible matrix. option 3 is wrong - N must consist of two large primes, (consider the case where N is 2x3x5x7... very trivially factorable). option 4 is wrong - it has to be 64 bit. option 2 is correct, because if the plaintext is larger than the modulus, you lose data.
</div>
</div>
<hr>
<!-- QUESTION 10 -->
<div class="quiz-block" markdown="1">
### question 10

what is the time complexity of the following program? take m as the length of the string, and n as the length of the substring.

```python
def find_substr(substring, string, index):
    if len(substring) + index > len(string): return False
    else:
        for i in range(len(substring)):
            if substring[i] != string[index+i]:
                return find_substr(substring, string, index+1)
    return True

```

<ul class="quiz-options">
  <li class="option">O(mn^2)</li>
  <li class="option correct">O(n*m)</li>
  <li class="option">O(nm^2)</li>
  <li class="option">O(n+m)</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> it will iterate through the inner loop of length m at worst n times, so the answer is O(n*m).
</div>
</div>

<hr>

### asm related questions

<div class="quiz-block" markdown="1">
### question 11

here is a layout of memory + some registers. which of the following statements is true?

```asm
0x4000: 0x1024
0x4002: 0x0000
0x4004: 0x2346
0x4006: 0x2355
0x4008: 0xdead
0x4010: 0xbeef

R1: 0x4006
```
```
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
3. the program counter is a register! `nop` will increase it.<br>
4. by right the stack pointer _should_ be word aligned but its not enforced on the hardware level the same way that the program counter's alignment is (if you try to do something like `mov.w 0x4555, PC`, PC will end up being 0x4554).
</div>
</div>

<div class="quiz-block" markdown="1">
### question 12

here are four pairs of commands. which of these pairs of commands will result in the exact same register states at the end of execution?

  <ul class="quiz-options">
  <li class="option correct">pop r9, and mov.w @sp+, r9</li>
  <li class="option">xor r9, r9 and mov r9, r8; sub r9, r8</li>
  <li class="option">mov.b r9, r8; xor.b r8, r9 and xor.b r9, r9</li>
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
