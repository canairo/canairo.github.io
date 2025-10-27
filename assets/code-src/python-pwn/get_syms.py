from pwn import *

elf = ELF("python3.11")
print(elf.sym.plt['geteuid'])
print(hex(elf.sym.stderr))
print(hex(elf.sym.plt['fflush']))
