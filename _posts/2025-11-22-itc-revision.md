---
layout: post
title: itc revision
date: 2025-11-20 05:40:00 +0800
---
<style>
  
  .quiz-options {
    list-style: none;
    padding: 0;
    margin-top: 15px;
  }

  .option {
    padding: 10px 15px;
    margin-bottom: 8px;
    cursor: pointer;
    border: 1px solid gray;
    transition: all 0.2s ease;
  }

  .option:hover {
    border: 1px solid white;
  }

  .quiz-block.answered .option {
    cursor: default;
    pointer-events: none;
  }

  .quiz-block.answered .option.correct {
    background-color: #1c1c1c;
    color: green;
    font-weight: bold;
  }

  .quiz-block.answered .option:not(.correct) {
    color: #86181d;
    opacity: 0.7;
  }

  .explanation {
    display: none;
    margin-top: 25px;
    padding-inline: 15px;
    border-left: 2px solid #b8bb26;
  }

  .quiz-block.answered .explanation {
    display: block;
    animation: fadeIn 0.5s;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
</style>

i fucking hate this mod

![wow](https://i.imgur.com/Fke3ugE.png)

<div class="quiz-block" markdown="1">
### question 1

consider the UML diagram below. which of the following statements is true? (DEVICE points to SIMULATE, AGENT points to LOGIN and SIMULATE).

![uml](https://i.imgur.com/bJn4KBL.png)

<ul class="quiz-options">
  <li class="option">an AGENT cannot CREATE SCHEMA.</li>
  <li class="option correct">an AGENT can SYNTHESISE DATA, but they must FILE RECORD too.</li>
  <li class="option">a DEVICE can LOG IN, and they can decide whether or not they want to EXECUTE ACTION.</li>
  <li class="option">a DEVICE cannot LOG IN, but they can SIMULATE without CREATING SCHEMA.</li>
</ul>


<div class="explanation" markdown=1>
<b>explanation:</b> for include / extends relations, the arrow is always pointing towards the base case. in the case of SYNTHESISE DATA, its base is LOG IN, so you need to LOG IN before you can SYNTHESISE DATA, but to LOG IN you must FILE RECORD.
</div>

</div>
<hr>
<!-- QUESTION 2 -->
<div class="quiz-block" markdown="1">
### question 2

two algorithms are implemented. one of them is constant time, and the other is linear time. both are executed on the same input, on the same computer. which of the following is true, assuming both will eventually terminate?

<ul class="quiz-options">
  <li class="option">the constant time algorithm will always finish before the linear time algorithm.</li>
  <li class="option">the linear time algorithm will always finish before the constant time algorithm.</li>
  <li class="option correct">it is impossible to tell which one will finish first based on the given information</li>
  <li class="option">both will take the same amount of time</li>
</ul>

<div class="explanation" markdown=1>
<b>explanation</b> there are indeed algorithms which are "theoretically" constant time but the constant term is so large that other non-constant time algorithms will outperform it, but in the majority of cases constant time will outperform linear time. you can't say for sure, though. [more info](https://en.wikipedia.org/wiki/Galactic_algorithm)

</div>
</div>

<hr>
<div class="quiz-block" markdown="1">
### question 3

what time complexity is the following algorithm?

```py
def func(n):
  for i in range(4):
    for j in range(n):
        for k in range(n):
          print([i*j*k*l for l in range(n)])
```

<ul class="quiz-options">
  <li class="option">O(4n^2)</li>
  <li class="option">O(4n^3)</li>
  <li class="option">O(n^2)</li>
  <li class="option correct">O(n^3)</li>
</ul>
<div class="explanation" markdown="1">
<b>explanation:</b> it's three nested loops reliant on `n`, the constant scaling factor of `4` doesn't matter.
</div>
</div>
<hr>


<div class="quiz-block" markdown="1">
### question 4

consider the following query. assuming the query executes successfully, which of these statements can be assumed to be true with 100% certainty?

```c
SELECT student_id FROM students WHERE module_id in 
(SELECT module_id FROM modules WHERE professor_id = 
(SELECT professor_id FROM professors WHERE years_experience > 10); 
```

<ul class="quiz-options">
  <li class="option">if you delete a given professor_id, all modules they teach will be removed from the modules table.</li>
  <li class="option">more than 3 tables exist in the schema.</li>
  <li class="option">module_id is the primary key of the modules table.</li>
  <li class="option correct">only one professor has more than ten years of experience.</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> very tricky question. in SQL the syntax of '=' indicates that the subquery only returns one row, and if it did, it would error out, but the question states that it executes successfully.
</div>
</div>
<hr>
<!-- QUESTION 5 -->
<div class="quiz-block" markdown="1">

### question 5

a music fan wants to create an entity-relationship diagram of their favorite bands. assume a band can create many albums, an album can contain many songs, and a song can 'feature' exactly one other band. which of the following is an incorrect assumption, based off of the information provided?

<ul class="quiz-options">
  <li class="option">we can create a Feature table to model the relation, using the primary key of Band and the primary key of Song as foreign keys</li>
  <li class="option correct">we can add a Feature column to the Songs table to model the relation, specifying that the Feature column must not be NULL</li>
  <li class="option">the cardinality of the Feature relation is many to one</li>
  <li class="option">a Band can Feature in multiple songs off of the same Album</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> note that we say a song _can_ feature another Band, not that it _must_. therefore, our Feature column can be NULL.
  </div>
</div>
<hr>

<!-- QUESTION 6 -->
<div class="quiz-block" markdown="1">
### question 6

which of the following algorithms would have exponential time complexity?

<ul class="quiz-options">
  <li class="option correct">iterating through all memory addresses on an N-bit processor</li>
  <li class="option">iterating through all I rows and J columns of a database with K tables</li>
  <li class="option">iterating through each number less than N to test for the primality of N</li>
  <li class="option">locating an element in a hashmap with 2^N elements</li>
</ul>

<div class="explanation" markdown=1>
<b>explanation:</b> remember your comarch! an N-bit processor will have 2^N memory addresses.
</div>
</div>
<hr>

<!-- QUESTION 7 -->
<div class="quiz-block" markdown="1">
### question 7

alice wants to send bob a message, and both alice and bob have valid RSA keypairs. alice and bob also share a secret K which no other people know. eve is a malicious eavesdropper who can read their transmissions. which of the following is true?

<ul class="quiz-options">
  <li class="option">if alice encrypts her message with her private key and transmits it, eve cannot read it but bob can.</li>
  <li class="option">if eve receives a message digitally signed with the secret K, she can be sure it is from alice.</li>
  <li class="option">if alice encrypts her message with her public key and transmits it, only bob can read it.</li>
  <li class="option correct" >if bob is able to decrypt a received message with alice's public key, he can be sure it is from alice.</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> option 1 is wrong because eve can decrypt with alice's public key. option 2 is wrong because the message could be from bob too (both share the secret K). option 3 is wrong because nobody except alice would be able to decrypt it. option 4 is correct because if bob can decrypt the message with alice's public key, that means the message was encrypted with alice's private key.
</div>
</div>
<hr>

<!-- QUESTION 8 -->
<div class="quiz-block" markdown="1">
### question 8

program A takes 10 seconds to compute 100 inputs, 50 seconds to compute 500 inputs, and 200 seconds to compute 2000 inputs. program B takes 1 second to compute 100 inputs, 4 seconds to compute 200 inputs. and 16 seconds to compute 400 inputs. for what number of inputs will their running times coincide? (ignore the trivial solution of 0 inputs)

<ul class="quiz-options">
  <li class="option">it will never coincide</li>
  <li class="option correct">1000</li>
  <li class="option">10000</li>
  <li class="option">500</li>
</ul>
<div class="explanation" markdown=1><b>explanation:</b>
program A is linear while program B is quadratic. running time of each program can be expressed as some f_i(n) where n is the number of inputs. f_a(n) = n/10, f_b(n) = n^2/10000. you can solve this as a quadratic or whatever but option 2 is correct here
</div>
</div>
<hr>

<!-- question 9 -->
<div class="quiz-block" markdown="1">
### question 9

which of these is true (assume that we want our resulting scheme to be secure and functional)?

<ul class="quiz-options">
  <li class="option">you can pick any size matrix to use as a hill cipher key, as long as it is square</li>
  <li class="option correct">you cannot pick any plaintext to encrypt for RSA</li>
  <li class="option">you can pick any number N to use in RSA, as long as it is above what can be feasibly factored (typically >512 bit)</li>
  <li class="option">you can pick any length of key for AES or DES, as long as it is at least 64 bit</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> option 1 is wrong - the key must be an invertible matrix. option 3 is wrong - N must consist of two large primes, (consider the case where N is 2x3x5x7... very trivially factorable). option 4 is wrong - it has to be 64 bit. option 2 is correct, because if the plaintext is larger than the modulus, you lose data.
</div>
</div>
<hr>
<!-- QUESTION 10 -->
<div class="quiz-block" markdown="1">
### question 10

what is the time complexity of the following program? take m as the length of the string, and n as the length of the substring.

```python
def find_substr(substring, string, index):
    if len(substring) + index > len(string): return False
    else:
        for i in range(len(substring)):
            if substring[i] != string[index+i]:
                return find_substr(substring, string, index+1)
    return True

```

<ul class="quiz-options">
  <li class="option">O(mn^2)</li>
  <li class="option correct">O(n*m)</li>
  <li class="option">O(nm^2)</li>
  <li class="option">O(n+m)</li>
</ul>
<div class="explanation" markdown=1>
<b>explanation:</b> it will iterate through the inner loop of length m at worst n times, so the answer is O(n*m).
</div>
</div>
<script>
document.addEventListener('DOMContentLoaded', function() {
  var options = document.querySelectorAll('.option');
  options.forEach(function(option) {
    option.addEventListener('click', function() {
      var block = event.currentTarget.closest('.quiz-block');
      console.log(block);
      if (block.classList.contains('answered')) return;
      block.classList.add('answered');
    });
  });
});
</script>
