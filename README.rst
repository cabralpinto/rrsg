Readable Random String Generation for Python

Features
--------
- Generates randomized strings from a generator string.
- Easy-to-use and intuitive syntax.
- No external dependencies.

Instalation
-----------
As it is early days for this python module and many things are subject to change, an instalation method as not been arranged.

Usage
-----
Simple example:

.. code-block:: python

    string = generate("""
        &age = (18, 20)
        
        $name
        Mark {age += 2}
        Sally
        
        $adj
        wacky {1%}
        cool
        
        >[Hi! | Hey! | Good morning.] My name is $adj $name. I am &age years old.
    """).strings()
    
    print(string) #Example output: Hey! My name is cool Mark. I am 21 years old.

Motivation
----------
The code above is the equivalent of

.. code-block:: python

    #vars
    age = random.randint(18, 20)

    #categories
    names = ('Mark', 'Sally')
    adjs = ('wacky', 'cool')
    adjs_probability_map = (0.1, 0.99)
    hellos = ('Hi!', 'Hey!', 'Good morning.')
    hellos_probability_map = (0.5, 0.25, 0.25)

    #calculation
    name = random.choice(names)
    if name is 'Mark':
        age += 2
    adj = random.choices(adjs, adjs_probability_map)[0]
    hello = random.choices(hellos, hellos_probability_map)[0]

    #string
    print(f'{hello} My name is {adj} {name}. I am {age} years old')
    
if to be made readable. Having worked in python projects where random string generation was often required, I decided to create rrsg to simplify the task.

About rrsg
----------
:Author: João Cabral Pinto
:Version: 0.1 released 25/02/2019
:Inspiration: Orteil's RandomGen_

.. _RandomGen: http://orteil.dashnet.org/randomgen/
