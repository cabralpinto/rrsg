import re, random as rnd

class _Compiler:

    def __init__(self, generator):
        self.generator = generator

    def _compile_var(self, var_b):
        """
        var_b = 'var = 1'        TURNS INTO    var_c = (var, (1, 1))
        var_b = 'var = (3,4)'    TURNS INTO    var_c = (var, (3, 4))
        """

        var_name = re.search('.+(?==)', var_b).group()
        range_value, absolute_value = re.search('(?<==)\((\d+),(\d+)\)', var_b), re.search('(?<==)((\d+))', var_b)
        if range_value: # range declaration
            var_c = (var_name, tuple(int(num) for num in range_value.group(1, 2)))
        elif absolute_value: # absolute declaration
            var_c = (var_name, tuple(int(num) for num in absolute_value.group(1, 2)))
        else:
            raise RandomGenerationError('Faulty variable atribution.')
        return var_c

    def _compile_datatag(self, datatag_b):
        """
        datatag_b = '{75%,var+=2}'    TURNS INTO    datatag_c = {'prob': 0.75, 'var': ('+', 2)}
        """
        datatag_c = {}

        for prop in datatag_b[1:-1].split(','): # e.g. ['50%', 'var+=3']
            if '%' in prop: # e.g. 'prob': 0.5
                datatag_c['prob'] = int(re.search('[0-9]{1,2}?(?=%)', prop).group()) * 0.01
            elif '=' in prop: # e.g. 'var': ('+', 3)
                datatag_c[re.search('.*?(?=\+=|-=|=)', prop).group()] = (re.search('\+|-|=', prop).group(), int(re.search('(?<==)[0-9]+', prop).group()))
            else:
                raise RandomGenerationError('Faulty datatag.')

        return datatag_c

    def _compile_items(self, items_b):
        """
        items_b = ['a', 'b{75%,var+=2}']    TURNS INTO    items_c = {'a': {'prob': 0.25}, 'b': {'prob': 0.75, 'var': ('+', 2)}}
        """
        items_c = {}

        for item_b in items_b:
            datatag = re.search('{.*?}', item_b)
            if datatag:
                items_c[re.search('.+?(?={)', item_b).group()] = self._compile_datatag(datatag.group()) # e.g. b: {'prob': 0.75, 'var': ('+', 2)}
            else:
                items_c[item_b] = {} # e.g. a: {}

        #complete probabilities
        unassigned_prob = (1 - sum(datatag.get('prob', 0) for datatag in items_c.values())) / [datatag.get('prob') for datatag in items_c.values()].count(None)
        for item, datatag in items_c.items():
            if not datatag.get('prob'):
                items_c[item]['prob'] = unassigned_prob

        return items_c

    def _compile_string(self, string_b, categories_c, vars_c):
        """
        string_b = [Hi! | Hey! | Good morning.] My name is $adj $name. I am &age years old.
                                          TURNS INTO
        string_c = [
            {'Hi!': {'prob': 0.33}, 'Hey!': {'prob': 0.33}, 'Good morning.': {'prob': 0.33}},
            ' My name is ',
            {'cool': 'prob': 0.99, 'wacky': 'prob': 0.01},
            ' ',
            {'Sally': {'prob': 0.5}, 'Mark': {'prob': 0.5, 'age': ('+', 2)}},
            '. I am ',
            ('age', (18, 20)),
            ' years old.'
        ]
        """

        string_c = []

        while string_b:
            category, bitesized, var, text = re.search('(?<=\$)[a-zA-Z]+', string_b), re.search('\[.*?\]', string_b), re.search('(?<=\&)[a-zA-Z]+', string_b), re.search('[^\&\[\]|\$]+', string_b)
            if category and category.start() is 1:
                string_c += [categories_c[category.group()]]
                string_b = string_b.replace('$' + category.group(), '', 1)
            elif bitesized and bitesized.start() is 0:
                string_c += [self._compile_items(bitesized.group()[1:-1].split('|'))]
                string_b = string_b.replace(bitesized.group(), '', 1)
            elif var and var.start() is 1:
                string_c += [[var_c for var_c in vars_c if var_c[0] == var.group()][-1]]
                string_b = string_b.replace(f'&{var.group()}', '', 1)
            elif text:
                string_c += [text.group()]
                string_b = string_b.replace(text.group(), '', 1)

        return string_c

    def _compile(self):
        """
        Compiles a generator. Returns a list of compiled strings (strings_c).
        """

        vars, categories, strings, querying = [], {}, [], False

        for line in self.generator.split('\n'):
            # remove comments
            line = re.sub('//.*', '', line)
            # remove unnecessary spaces
            # region
            line = line.lstrip(' ').rstrip(' ')                     # remove spaces before and after line
            line = re.sub('\&(?: +)?', '&', line)                   # remove spaces after '&'
            line = re.sub('\$(?: +)?', '$', line)                   # remove spaces after '$'
            line = re.sub('\>(?: +)?', '>', line)                   # remove spaces after '>'
            line = re.sub('(?: +)?=(?: +)?', '=', line)             # remove spaces before and after '='
            line = re.sub('(?: +)?(?:\+=)(?: +)?', '+=', line)      # remove spaces before and after '+='
            line = re.sub('(?: +)?(?:-=)(?: +)?', '-=', line)       # remove spaces before and after '-='
            line = re.sub('(?: +)?\|(?: +)?', '|', line)            # remove spaces before and after '|'
            line = re.sub('(?: +)?,(?: +)?', ',', line)             # remove spaces before and after ','
            line = re.sub('\[(?: +)?', '[', line)                   # remove spaces after '['
            line = re.sub('(?: +)?\]', ']', line)                   # remove spaces before ']'
            line = re.sub('(?: +)?\{(?: +)?', '{', line)            # remove spaces before and after '{'
            line = re.sub('(?: +)?\}(?: +)?', '}', line)            # remove spaces before and after '}'
            # endregion
            # ignore empty lines
            if line is '': continue
            # iterpret line
            if line[0] is '&':
                # stop querying for category values and compile last category
                if querying:
                    querying = False
                    categories[category_name] = self._compile_items(categories[category_name])
                # create a new compiled var
                var_s = re.search('(?<=&).+', line).group()
                vars += [self._compile_var(var_s)]
            elif line[0] is '$':
                # start querying for category values and compile last category
                if querying:
                    categories[category_name] = self._compile_items(categories[category_name])
                else:
                    querying = True
                # add a new empty category
                category_name = re.search('(?<=\$)[^ \n]+', line).group()
                categories[category_name] = []
            elif line[0] is '>':
                # stop querying for category values and compile last category
                if querying:
                    querying = False
                    categories[category_name] = self._compile_items(categories[category_name])
                # add phrase to results
                string_b = re.search('(?<=>).+', line).group()
                strings += [self._compile_string(string_b, categories, vars)]
            elif querying:
                # add raw item to category being queried
                categories[category_name] += [line]
        
        return Compiled(strings)
    pass

class Compiled:

    def __init__(self, strings_c):
        self.strings_c = strings_c

    def _generate_value(self, value_c):
        """
        value_c = (1,4)    TURNS INTO, E.G.    value_f = 3
        """
        return rnd.randint(*value_c)

    def _generate_item(self, category_c):
        """
        category_c = {'Sally': {'prob': 0.5}, 'Mark': {'prob': 0.5, 'age': ('+', 2)}}    TURNS INTO, E.G.    item_f = ('Mark', ('age', ('+', 2)))
        """
        item = rnd.choices(list(category_c.keys()), [datatag['prob'] for datatag in category_c.values()])[0]
        return (item, list(attr for attr in category_c[item].items() if attr[0] is not 'prob'))
    
    def _generate_string(self, string_c):
        """
        string_c = [
            {'Hi!': {'prob': 0.33}, 'Hey!': {'prob': 0.33}, 'Good morning.': {'prob': 0.33}},
            ' My name is ',
            {'cool': 'prob': 0.99, 'wacky': 'prob': 0.01},
            ' ',
            {'Sally': {'prob': 0.5}, 'Mark': {'prob': 0.5, 'age': ('+', 2)}},
            '. I am ',
            ('age', (18, 20)),
            ' years old.'
        ]
                                          TURNS INTO
        string_f = 'Hi! My name is cool Mark. I am 21 years old.'
        """

        var_changes = []


        for i, category_c in (obj_c for obj_c in list(enumerate(string_c)) if type(obj_c[1]) is dict):
            item_f = self._generate_item(category_c)
            string_c[i] = item_f[0]
            if item_f[1]: var_changes += item_f[1]

        for i, var_c in (obj_c for obj_c in enumerate(string_c) if type(obj_c[1]) is tuple):
            var_f = self._generate_value(var_c[1])

            for var, operation in (var_change for var_change in var_changes if var_change[0] == var_c[0]):
                var_f = {'=': lambda x, y: y,
                         '+': lambda x, y: x + y,
                         '-': lambda x, y: x - y}[operation[0]](var_f, operation[1])

            string_c[i] = str(var_f)
        
        return ''.join(string_c)


    def generate(self):
        """
        Returns a Results object containing all final strings.
        """
        strings_f = []
        for string_c in self.strings_c:
            strings_f += [self._generate_string(string_c)]
        return Results(strings_f)

class Results:
    def __init__(self, strings_f):
        self.strings_f = strings_f

    def strings(self):
        return self.strings_f

def compile(generator):
    """Returns a Compiled object useful when generating multiple times from the same generator."""
    return _Compiler(generator)._compile()

def generate(generator):
    """Returns a Results object containing the generation results and the output data."""
    return compile(generator).generate()

print(_Compiler("""
        &age = (18, 20)
        
        $name
        Mark {age += 2}
        Sally
        
        $adj
        wacky {1%}
        cool
        
        >[Hi! | Hey! | Good morning.] My name is $adj $name. I am &age years old.
    """)._compile().strings_c[0])

print('\n\n\n')

print(generate("""
        &age = (18, 20)
        
        $name
        Mark {age += 3}
        Sally
        
        $adj
        wacky {1%}
        cool
        
        >[Hi! | Hey! | Good morning.] My name is $adj $name. I am &age years old.

    """).strings())