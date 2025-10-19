import dis

def f(obj):
    return obj.a + obj.b + obj.c

print(f.__code__.co_code.hex())

class TestClass:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

dis.dis(f, adaptive=True)

objs = [TestClass(a, a*2, a*3) for a in range(1, 100)]
for obj in objs:
    f(obj)

dis.dis(f, adaptive=True)
input('...')
f(TestClass(1, 2, 3))
