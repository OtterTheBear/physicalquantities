from enum import Enum
import math
import sys
import logging

logger = logging.getLogger(__name__)

debug = False

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
    def to_string(self, indent_level=0):
        ans = " " * 4 * indent_level + f"value: {self.value}\n" + " " * 4 * indent_level + "children: [\n"
        for child in self.children: 
            ans += child.to_string(indent_level+1)
        return ans + " " * 4 * indent_level + "]\n"

def compute_tree(tree):
    if tree.value.type == TokenType.NUMBER:
        return tree.value.value
    elif tree.value.type == TokenType.UNARY_OP:
        return tree.value.func(compute_tree(tree.children[0]))
    elif tree.value.type == TokenType.UNIT:
        return UNITS[tree.value.name] * compute_tree(tree.children[0])
    else:
        return tree.value.func(compute_tree(tree.children[0]), compute_tree(tree.children[1]))

class Token:
    def __init__(self, name, token_type):
        self.name = name
        self.type = token_type
        self.unit_like = False
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
                raise Exception(f"unkown operator \"{name}\"")
        elif self.type == TokenType.BRACKET:
            pass
        elif self.type == TokenType.UNARY_OP:
            if name == "-":
                self.func = lambda x: -x
            else:
                raise Exception(f"Unkown unary operator \"{name}\"")
        elif self.type == TokenType.UNIT:
            self.value = UNITS[self.name]
        else:
            raise Exception(f"unkown token type {token_type}")
    def __eq__(self, value):
        return self.name == value.name and self.type == value.type
    def __repr__(self):
        return f"Token(\"{self.name}\", {self.type})"

def parse(tokens):
    logger.debug("\nPARSING NOW")
    logger.debug(Tree(None, tokens).to_string())
    yes = False
    bracket_level = 0
    new_tokens = []
    for i, child in enumerate(tokens):
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
                logger.debug(f"{to_parse=}")

        else:
            if child.value.name == "(":
                logger.debug("AAAAA")
                yes = True
                to_parse = []
                bracket_level = 1
            else:
                new_tokens.append(child)


    tree = Tree(None, new_tokens)
    
    logger.debug("\nprocessing operators")
    
    for neighbour_ops in ops:
        i = 0
        logger.debug(f"processing {neighbour_ops}" if neighbour_ops != UNIT_TOKENS else "UNITS")
        while i < len(tree.children):
            if tree.children[i].value in neighbour_ops:
                if tree.children[i].value.type == TokenType.OP:
                    if i > 0 and i < len(tree.children) - 1:
                        tree.children[i].children = [tree.children[i-1], tree.children[i+1]]
                        del tree.children[i+1]
                        del tree.children[i-1]
                        
                        i -= 1
                elif tree.children[i].value.type == TokenType.UNIT:
                    if (i > 0): # there is a token to the left
                        # if the token on the left is (not an operator) or (has children)
                        if (not tree.children[i-1].value.type in [TokenType.OP, TokenType.UNARY_OP] or not len(tree.children[i-1].children) == 0):
                            tree.children[i].children = [tree.children[i-1]]
                            del tree.children[i-1]
                            i -= 1
                        else: # operator without children
                            if len(tree.children[i].children) == 0:
                                tree.children[i].children = [Tree(Token(1.0, TokenType.NUMBER), [])]
                            else:
                                logger.debug("nothing")
                    else:
                        if len(tree.children[i].children) == 0:
                            tree.children[i].children = [Tree(Token(1.0, TokenType.NUMBER), [])]

                    
                    
                else:
                    if i < len(tree.children) - 1:
                        tree.children[i].children = [tree.children[i+1]]
                        del tree.children[i+1]

            i += 1
    logger.debug(f"RETURNING")
    return tree.children[0]
               



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

    def __eq__(self, other):
        return self.value == other.value and self.dimension == other.dimension

    def __repr__(self):
        return f"Quantity({self.value}, mass={self.dimension[0]}, length={self.dimension[1]}, time={self.dimension[2]}, current={self.dimension[3]}, temperature={self.dimension[4]}, n={self.dimension[5]}, j={self.dimension[6]})"

    def to_string(self, method="base"):
        if method == "base":
            ans = f"{self.value}"
            for dimension in self.dimension:
                if dimension != 0:
                    ans += " "
                    break
            return ans + " ".join([f"{QSTRINGS[i]}" + (f"^{dimension}" if dimension != 1 else "") for i, dimension in enumerate(self.dimension) if dimension])
        elif method == "derived":
            self_unit = Quantity(1.0, *self.dimension)
            for unit_name, unit in UNITS.items():
                if unit == self_unit:
                    return f"{self.value} {unit_name}"
            return self.to_string()
        else:
            raise Exception(f"Unkown string conversion method for Quantity: \"{method}\"")
           


    

QSTRINGS = ["kg", "m", "s", "A", "K", "mol", "cd"]

kg = Quantity(1, mass=1.0)
m = Quantity(1, length=1.0)
s = Quantity(1, time=1.0)
A = Quantity(1, current=1.0)
K = Quantity(1, temperature=1.0)
mol = Quantity(1, n=1.0)
cd = Quantity(1, j=1.0)

lb = Quantity(0.45359237) * kg
inch = Quantity(0.0254) * m
ft = Quantity(0.3048) * m
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
    "in": inch,
    "ft": ft,
    "yd": yd,
    "mi": mi,

    "min": minute,
    "hr": hr,
    "day": day,

    "N": N,
    "J": J,
    "W": W,
    "Pa": N / m / m,
    "V": V,
    "ohm": ohm,
    "C": C,
    "F": F,
    "H": H,

    "gravity": earth_gravity,
    "pi": Quantity(math.pi),

    "lbf": lbf,
    "hp": horsepower,
    "g": Quantity(1e-3) * kg,
    "km": Quantity(1e3) * m,
    "L": Quantity(1e-3) * m ** Quantity(3)
}

UNIT_TOKENS = [Token(x, TokenType.UNIT) for x in UNITS.keys()]
char_categories = {
    TokenType.OP: lambda x: x in "+-*/",
    TokenType.NUMBER: lambda x: x in "1234567890.",
    TokenType.BRACKET: lambda x: x in "()",
    TokenType.UNIT: lambda x: x.isalpha()
}

categories_char = {value: key for key, value in char_categories.items()}

ops = [
    [Token("**", TokenType.OP)],
    [Token("-", TokenType.UNARY_OP)],
    UNIT_TOKENS,
    [Token("*", TokenType.OP), Token("/", TokenType.OP)],
    [Token("+", TokenType.OP), Token("-", TokenType.OP)],
]
READY = 9

def process_input(calc_input):
    state = READY
    buffer = ""
    tokens = []
    for char in calc_input:
        logger.debug(f"{buffer=}, {char=}, {state=}")
        if state == READY:
            happened = False
            for token, func in char_categories.items():
                if func(char):
                    state = token
                    logger.debug(f"{state=}")
                    happened = True
            assert happened
            buffer += char
        else:
            happened = True
            if char_categories[TokenType.BRACKET](char) or not char_categories[state](char):
                if state == TokenType.OP and (len(tokens) == 0 or tokens[-1].value.type == TokenType.UNARY_OP or tokens[-1].value.type == TokenType.OP or tokens[-1].value == Token("(", TokenType.BRACKET)):
                    #state = TokenType.UNARY_OP
                    if buffer != "":
                        tokens.append(Tree(Token(buffer, TokenType.UNARY_OP), []))
                else:
                    if buffer != "":
                        logger.debug(f"yoo {buffer=}")
                        tokens.append(Tree(Token(buffer, state), []))

                happened = False
                for token, func in char_categories.items():
                    if func(char):
                        state = token
                        happened = True
                logger.debug(f"{happened=}")
                buffer = ""
            if happened:
                buffer += char
            
        
        logger.debug(f"{tokens=}")

    if buffer != "":
        tokens.append(Tree(Token(buffer, state), []))
    logger.debug(f"{tokens=}")
    return compute_tree(parse(tokens))

def main():
    while True:
        print(process_input(input("> ")).to_string("derived"))

if __name__ == "__main__":
    if "-v" in sys.argv:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)
    main()