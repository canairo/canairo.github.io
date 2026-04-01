---
layout: post
title: the worst pwn challenges ever written (lnc26 author writeups)
date: 2026-03-20 05:40:00 +0800
draft: true
---

[!img](https://i.imgur.com/cwdsObm.png)

### THIS IS NOT COMPLETED AND I DOUBT I WILL EVER FINISH IT

recommended listening for this post is [stella was a diver and she was always down](https://www.youtube.com/watch?v=nc-Xc-CFAiY).

to inaugurate my official retirement from ctf (real) (not really i'll be doing this stupid fucking shit again in like 2 months (my thousand-year curse as destined by sun wu kong)) i wrote 2 of the worst pwns ever written for beautiful interpoly competition lag and crash six point oh. they didnt get a lot of solves during the comp because they are the worst pwns ever written. one is a python pwn and the other is a musl pwn and they are both quite 'minimal'. all things aside im really happy with how they turned out and i think they are Cool Challenges (that no one really bothered to solve aside from like 3 people xd)

### misc/hyperboros

this is the python pwn, the source is a simple script that runs a loop giving single-byte relative write to the python code object

```py
import ctypes

def hyperboros():
    offset = int(input('offset\n>> '))
    char = bytes.fromhex(input('char\n>> '))
    assert len(char) == 1
    ctypes.memmove(id(hyperboros.__code__) + offset, char, len(char))

for i in range(1, 1000):
    hyperboros()
```

the goal is to use the single-byte write and eventually get code execution. before we get started we should learn more about the python bytecode format ( i have a [few](https://slight-smile.com/writeups/infobahn-ctf-25/) posts about this already, this is an ongoing interest of mine ), as well as code objects in general. on runtime, each python function (such as our `hyperboros` function) gets compiled into a code object with a few different related objects / structs, see this example, where we define some random function `a`. we can see that it has that `__code__` attribute that the `hyperboros` function references.

```py
>>> a = lambda x: x
>>> a
<function <lambda> at 0x7f4132d5c4a0>
>>> a.__code__
<code object <lambda> at 0x7f4132d21620, file "<python-input-8>", line 1>
```

the `__code__` function is actually what's important here, so we can further look at its associated objects `co_names`, `co_varnames`, etc. let's look at what the `hyperboros` function has:

```c
>>> hyperboros.__code__.co_names
('int', 'input', 'bytes', 'fromhex', 'len', 'ctypes', 'memmove', 'id', 'hyperboros', '__code__')
>>> hyperboros.__code__.co_varnames
('offset', 'char')
>>> hyperboros.__code__.co_consts
(None, 'offset\n>> ', 'char\n>> ', 1)
>>>
```

each func stores a tuple of strings to globals that it wants to reference in `co_names`. if the function wants to call `id`, the python interpreter will load `id` by using the string reference in `co_names`, using this to eventually find a pointer to `id`. 
