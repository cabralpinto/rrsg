Readable Random String Generation for Python

Features
--------
- Generates randomized strings from a generator string.
- Easy-to-use and intuitive syntax.

Usage
-----
.. code-block:: python

    print(random_string('''
        &age = (15, 18)

        $name
        Mark {age += 2}
        Sally
        Pocahontas {1%, age = 22}

        >[Hi! | Hey! | Good morning.] My name is $name. I am &age years old.
    ''')[0])

Motivation
----------
The code above is the equivalent of

About rrsg
----------
:Author: João Cabral Pinto
:Version: 0.1 released 22/02/2019
:Inspiration: Orteil's RandomGen.
