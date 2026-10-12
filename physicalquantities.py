from enum import Enum

class TokenType(Enum):
    NUMBER = 0
    OP = 1
    UNARY_OP = 2
    BRACKET = 3
    UNIT = 4

class Tree:
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def __repr__(self):
        return f"Tree({str(self.value)}, {self.children})"

def print_tree(tree, indent_level=0):
    print(" " * 4 * indent_level + f"value: {tree.value}")
    print(" " * 4 * indent_level + "children: [")
    for child in tree.children: 
        print_tree(child, indent_level+1)
    print(" " * 4 * indent_level + "]\n")

def compute_tree(tree):
    if tree.value.type == TokenType.NUMBER:
        return tree.value.value
    elif tree.value.type == TokenType.UNARY_OP:
        return tree.value.func(compute_tree(tree.children[0]))
    elif tree.value.type == TokenType.UNIT:
        return UNITS[tree.value.name] * compute_tree(tree.children[0])
    else:
        return tree.value.func(compute_tree(tree.children[0]), compute_tree(tree.children[1]))

def parse(tokens):
    print("\nPARSING NOW")
    yes = False
    bracket_level = 0
    new_tokens = []
    for i, child in enumerate(tokens):
        print(f"\nproccesing child {child}")
        if yes:
            if child.value.name == ")":
                bracket_level -= 1
                if bracket_level == 0:
                    yes = False
                    new_tokens.append(parse(to_parse))
                else:
                    to_parse.append(child)
            else:
                if child.value.name == "(":
                    bracket_level += 1
                to_parse.append(child)
                print(f"{to_parse=}")

        else:
            if child.value.name == "(":
                print("AAAAA")
                yes = True
                #end_index = len(tokens) - next((j for j, end_child in enumerate(tokens[::-1]) if end_child.value == Token(")", TokenType.BRACKET))) - 1
                #print(f"{end_index=}")
                to_parse = []
                bracket_level = 1
            else:
                new_tokens.append(child)


    tree = Tree(None, new_tokens)
    print("\nprocessing units")
    """i = 0
    while i < len(tree.children):
        if tree.children[i].value.type == TokenType.UNIT:
            print("a")
            tree.children[i].children.append(Tree(Token(1.0, TokenType.NUMBER), []))
            if i > 0:
                if tree.children[i-1].value.type not in [TokenType.OP, TokenType.UNARY_OP]:
                   if tree.children[i+1].value.name == "**":
                        tree.children[i] = Tree(Token("*", TokenType.OP), [
                            Tree(Token("**", TokenType.OP), [
                                Tree(tree.children[i].value, [
                                    tree.children[i-1]
                                ])
                            ])
                        ])
                    print(f"{tree.children[i].value=}")
                    tree.children.insert(i, Tree(Token("*", TokenType.OP), []))
                    i += 1
            else:
                raise Exception("unit exception")
            
        i += 1"""
    print(f"new tokens:")
    print_tree(tree)
    print("\nprocessing operators")
    for neighbour_ops in ops:
        i = 0
        print("NEXT OP")
        while i < len(tree.children):
            if tree.children[i].value in neighbour_ops:
                if tree.children[i].value.type == TokenType.OP:
                    if i > 0 and i < len(tree.children) - 1:
                        if tree.children[i].value.name == "**" and tree.children[i-1].value.type == TokenType.UNIT:
                            tree.children[i-1].value.value **= tree.children[i+1].value.value
                            del tree.children[i:i+2]
                            i -= 1
                        else:
                            tree.children[i].children = [tree.children[i-1], tree.children[i+1]]
                            del tree.children[i+1]
                            del tree.children[i-1]
                            
                            i -= 1
                elif tree.children[i].value.type == TokenType.UNIT:
                    print(f"{tree.children[i-1]=}")
                    print("yep")
                    if not (tree.children[i-1].value.type in [TokenType.OP, TokenType.UNARY_OP] and len(tree.children[i-1].children) == 0):
                        tree.children[i].children = [tree.children[i-1]]
                        del tree.children[i-1]
                        i -= 1
                    else:
                        tree.children[i].children = [Tree(Token(1.0, TokenType.NUMBER), [])]
                    
                else:
                    if i < len(tree.children) - 1:
                        tree.children[i].children = [tree.children[i+1]]
                        del tree.children[i+1]

            i += 1
    print(f"RETURNING {tree.children[0]}")
    return tree.children[0]
               

class Token:
    def __init__(self, name, token_type):
        self.name = name
        self.type = token_type
        if self.type == TokenType.NUMBER:
            self.value = Quantity(float(name))
        elif self.type == TokenType.OP:
            if name == "+":
                self.func = lambda x, y: x + y
            elif name == "-":
                self.func = lambda x, y: x - y
            elif name == "*":
                self.func = lambda x, y: x * y
            elif name == "/":
                self.func = lambda x, y: x / y
            elif name == "**":
                self.func = lambda x, y: x ** y
            else:
                raise Exception(f"unkown operator {name}")
        elif self.type == TokenType.BRACKET:
            pass
        elif self.type == TokenType.UNARY_OP:
            if name == "-":
                self.func = lambda x: -x
            else:
                raise Exception(f"Unkown unary operator {name}")
        elif self.type == TokenType.UNIT:
            self.value = UNITS[self.name]
        else:
            raise Exception(f"unkown token type {token_type}")
    def __eq__(self, value):
        #print(f"{value=}")
        return self.name == value.name and self.type == value.type
    def __repr__(self):
        return f"Token(\"{self.name}\", {self.type})"

class Quantity:
    def __init__(self, value, mass=0, length=0, time=0, current=0, temperature=0, n=0, j=0):
        self.value = value
        self.dimension = [mass, length, time, current, temperature, n, j]
        
    def __add__(self, other):
        if self.dimension == other.dimension:
            return Quantity(self.value + other.value, *self.dimension)
        else:
            raise Exception(f"Quantities' dimensions don't match")
    def __sub__(self, other):
        if self.dimension == other.dimension:
            return Quantity(self.value + -other.value, *self.dimension)
        else:
            raise Exception(f"Quantities' dimensions don't match")
    def __mul__(self, other):
        return Quantity(self.value * other.value, *(x + y for x, y in zip(self.dimension, other.dimension)))
    def __truediv__(self, other):
        return Quantity(self.value / other.value, *(x - y for x, y in zip(self.dimension, other.dimension)))
    def __pow__(self, other):
        if other.dimension == [0, 0, 0, 0, 0, 0, 0]:
            return Quantity(self.value ** other.value, *(x * other.value for x in self.dimension))
        raise Exception("Can't raise a quantity to a dimensional power")
    def __neg__(self):
        return Quantity(-self.value, *self.dimension)

    def __repr__(self):
        return f"Quantity({self.value}, mass={self.dimension[0]}, length={self.dimension[1]}, time={self.dimension[2]}, current={self.dimension[3]}, temperature={self.dimension[4]}, n={self.dimension[5]}, j={self.dimension[6]})"

QSTRINGS = ["kg", "m", "s", "A", "K", "mol", "cd"]

def print_quantity(quantity, method="base"):
    if method == "base":
        print(f"{quantity.value} ", end="")
        for i, dimension in enumerate(quantity.dimension):
              if dimension:
                  print(f"{QSTRINGS[i]}" + (f"^{dimension} " if dimension != 1 else ""), end=" ")
        print()

kg = Quantity(1, mass=1)
m = Quantity(1, length=1)
s = Quantity(1, time=1)
A = Quantity(1, current=1)
K = Quantity(1, temperature=1)
mol = Quantity(1, n=1)
cd = Quantity(1, j=1)

lb = Quantity(0.45359237) * kg
inch = Quantity(0.0254) * m
ft = Quantity(12) * inch
yd = Quantity(3) * ft
mi = Quantity(5280) * ft

minute = Quantity(60) * s
hr = Quantity(3600) * s
day = Quantity(24) * hr

N = kg * m / s / s
J = N * m
W = J / s
V = W/A
ohm = V/A
C = A * s
F = C / V
H = V * s / A

earth_gravity = Quantity(9.80665) * m / s / s

lbf = lb * earth_gravity
horsepower = Quantity(550) * lbf * ft / s

UNITS = {
    "kg": kg,
    "m": m,
    "s": s,
    "A": A,
    "K": K,
    "mol": mol,
    "cd": cd,
    "lb": lb,
    "inch": inch,
    "ft": ft,
    "yd": yd,
    "mi": mi,

    "minute": minute,
    "hr": hr,
    "day": day,

    "N": N,
    "J": J,
    "W": W,
    "V": V,
    "ohm": ohm,
    "C": C,
    "F": F,
    "H": H,

    "gravity": earth_gravity,

    "lbf": lbf,
    "horsepower": horsepower,
    "g": Quantity(1e-3) * kg,
    "km": Quantity(1e3) * m,
    "L": Quantity(1e-3) * m ** Quantity(3)
}

UNIT_TOKENS = [Token(x, TokenType.UNIT) for x in UNITS.keys()]

opchars = "+-*/"
numchars = "1234567890."
groupchars = "()"
ops = [
    [Token("**", TokenType.OP)],
    [Token("-", TokenType.UNARY_OP)],
    UNIT_TOKENS,
    [Token("*", TokenType.OP), Token("/", TokenType.OP)],
    [Token("+", TokenType.OP), Token("-", TokenType.OP)],
]
READY = 9

while True:
    state = READY
    t = input("Say something ")
    buffer = ""
    tokens = []
    for char in t:
        print(f"{buffer=}, {char=}, {state=}")
        if char in numchars:
            if state != TokenType.NUMBER:
                if buffer != "":
                    tokens.append(Tree(Token(buffer, state), []))
                buffer = ""
                state = TokenType.NUMBER
            buffer += char

        if char in opchars:
            if state != TokenType.OP and state != TokenType.UNARY_OP:
                if buffer != "":
                    tokens.append(Tree(Token(buffer, state), []))
                
                if state == READY or state == TokenType.UNARY_OP or state == TokenType.OP or tokens[-1].value == Token("(", TokenType.BRACKET):
                    state = TokenType.UNARY_OP
                else:
                    state = TokenType.OP
                buffer = ""
            buffer += char
        if char in groupchars:
            if state != TokenType.BRACKET:
                if buffer != "":
                    tokens.append(Tree(Token(buffer, state), []))
                buffer = ""
                state = TokenType.BRACKET
            tokens.append(Tree(Token(char, state), []))

        if char.isalpha():
            if state != TokenType.UNIT:
                if buffer != "":
                    tokens.append(Tree(Token(buffer, state), []))
                buffer = ""
                state = TokenType.UNIT
            buffer += char
        
        
    tokens.append(Tree(Token(buffer, state), []))
    print(f"{tokens=}")
    
        
    print_quantity(compute_tree(parse(tokens)))             
