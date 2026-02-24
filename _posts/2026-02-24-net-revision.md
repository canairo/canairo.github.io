---
layout: post
title: profcane's networking revision
date: 2026-02-20 05:40:00 +0800
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

[recommended listening for this post is do it (yves remix)](https://www.youtube.com/watch?v=kvhVECfGsw8)

apparently wing keong is like an insane crackpot conspiracy theorist? either way the man's a good professor and makes hard tests so if he says that vlan tags cause 9/11 then fuck it man `encapsulation dot1q 9/11` my ass

![meow](https://i.imgur.com/Fu1lazS.png)

<div class="quiz-block" markdown="1">
### question 1

![network topo](https://i.imgur.com/Al4m38h.png)

consider the following setup. i have setup the trunk between `S1` and `S2`, VLAN 10 on `G1/0/6 S1` and `G1/0/11 S2`, and VLAN 20 on `G1/0/18` as per the diagram i have also correctly set the router's ip addresses on their interfaces. pc A can ping pc B, but no pcs can ping the router. this is because


<ul class="quiz-options">
  <li class="option">STP detects a loop between the router and switches and shuts the network down.</li>
  <li class="option correct">the connections R1-S1 and R2-S2 also need VLANs configured.</li>
  <li class="option">nothing is wrong with the configuration as described, it is most likely a physical layer issue.</li>
  <li class="option">if the trunk was configured without explicitly stating which VLANs are allowed, the default option is to only allow VLAN 1, hence neither VLAN can actually use the trunk.</li>
</ul>


<div class="explanation" markdown=1>
<b>explanation</b> STP does not come into play here, and the default for a trunk is to allow <i>all</i> VLANs. the default for an interface on a switch is ONLY VLAN 1, so the switch cannot send packets from PC A to R1 (the VLAN has not been properly configured). 
</div>

</div>
<hr>
<!-- QUESTION 2 -->
<div class="quiz-block" markdown="1">
### question 2

which of these is possible to do on a CISCO router?


<ul class="quiz-options">
  <li class="option">setting multiple VLANs on a LAN subinterface</li>
  <li class="option">setting an IP address on a LAN subinterface before its VLAN is configured</li>
  <li class="option correct">setting a VLAN on a LAN subinterface before its IP address is configured</li>
  <li class="option">all of these are possible</li>
</ul>

<div class="explanation" markdown=1>
<b>explanation</b> one VLAN+IP address per LAN subinterface. the key thing here is that an IP address is 'more specific' than a VLAN, and the router requires you to set the VLAN (with the `encapsulation dot1q ..`) command before configuring the IP address. (you'll note that in each example in the labs, the `encapsulation` command is performed before setting the IP).
</div>
</div>

<hr>
<div class="quiz-block" markdown="1">
### question 3

LAN subinterface `G0/0/1.10` is currently configured to `192.168.1.10/28`. i want to configure LAN subinterface `G0/0/1.20` - which address + subnet mask would the router let me configure it to?

<ul class="quiz-options">
  <li class="option">192.168.1.3 255.255.255.252</li>
  <li class="option">192.168.1.24 255.255.255.0</li>
  <li class="option correct">192.168.2.1 255.255.254.0</li>
  <li class="option">192.168.1.14 255.255.255.254</li>
</ul>
<div class="explanation" markdown="1">
<b>explanation:</b> the only constraint that the router enforces is that no subinterface must overlap (when it receives a packet destined for a specific subnet, it _must_ know which interface to send it to, there cannot be any 'ambiguities'). for each IP address above starting with `192.168.1.x`, the `192.168.1.10/28` will necessarily overlap (because that subnet covers every single `192.168.1.x` addr). `192.168.2.0 255.255.254.0` covers from `192.168.2.0 - 192.168.3.255`, hence no overlap.</div>
</div>
<hr>


<div class="quiz-block" markdown="1">
### question 4

![network topo](https://www.ciscopress.com/content/images/chap4_9780136729358/elementLinks/04fig05_alt.jpg)

consider the network topology, noting that `PC1` and `PC2` are on separate VLANs. `PC1` sends `PC2` an ICMP ping request. assuming that all ARP tables are empty, which of the following is true?

<ul class="quiz-options">
  <li class="option">from S2 to PC2, the packet has a VLAN tag.</li>
  <li class="option">the source MAC address of the packet stays constant throughout the entire lifecycle of the packet.</li>
  <li class="option">when S2 forwards the packet to PC2, it will add PC2's MAC address to its MAC address table.</li>
  <li class="option correct">the packet starts with no VLAN tag, then S1 adds one, then R1 removes and adds another one, then S2 finally removes it.</li>
</ul>

<div class="explanation" markdown=1>
<b>explanation:</b> PCs are 'VLAN unaware', the PC only sends an ethernet packet. VLAN tags are a layer 2 thing, so they are mainly dealt with by switches (as well as layer 3 routers, which need to decapsulate the packet to check its IP, then reapply the next VLAN tag during encapsulation). switches only learn MAC addresses from _source_ MAC addresses and not destinations, and when the router decapsulates the packet, it modifies the source MAC address of the packet to be the router's.
</div>
</div>
<hr>
<!-- QUESTION 5 -->
<div class="quiz-block" markdown="1">
### question 5

same question as above - which of the following is true? (remember the assumption that all ARP, MAC address, and routing tables are empty).

<ul class="quiz-options">
  <li class="option">PC1 will first send an ARP request to PC2 to know which MAC address to send its ICMP packet to.</li>
  <li class="option correct">PC2 will eventually send an ARP response addressed to R1.</li>
  <li class="option">when S1 receives an ARP request, it will flood it out of all 3 ports.</li>
  <li class="option">three ARP requests are sent throughout the process of sending the ICMP request.</li>

</ul>
<div class="explanation" markdown=1>
<b>explanation:</b>PC1 cannot send an ARP request to PC2 because they are on different subnets! PC1 would send it to the default gateway (the router), and the router would _then send its own ARP request_ to PC2, and PC2 would respond. throughout this process only two ARP requests would be sent (PC1 would need to ARP for its default gateway, and the router would need to ARP for PC2). third option is wrong because a switch floods a broadcast packet out of all ports _except_ ingress, so it would only send 2 packets max (if that).
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
