from enum import Enum
import math
import sys
import logging
from quantities import *

logger = logging.getLogger(__name__)

#debug = False

class TokenType(Enum):
    NUMBER = 0
    OP = 1
    UNARY_OP = 2
    BRACKET = 3
    UNIT = 4
    POWERED_UNIT = 5

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
    elif tree.value.type == TokenType.POWERED_UNIT:
        return UNITS[tree.children[0].value.name] ** compute_tree(tree.children[1]) * tree.children[2].value.value
    else:
        return tree.value.func(compute_tree(tree.children[0]), compute_tree(tree.children[1]))

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

        elif self.type == TokenType.POWERED_UNIT:
            pass
        
        else:
            raise Exception(f"unkown token type {token_type}")
        
    def __eq__(self, value):
        return self.name == value.name and self.type == value.type

    def __repr__(self):
        return f"Token(\"{self.name}\", {self.type})"

def parse(tokens):
    logger.debug("PARSING NOW")
    
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
    
    logger.debug("processing operators")
    
    for neighbour_ops in ops:
        i = 0
        logger.debug(f"processing {neighbour_ops}" if neighbour_ops != UNIT_TOKENS else "UNITS")
        logger.debug(tree.to_string())
        while i < len(tree.children):
            if tree.children[i].value in neighbour_ops:
                if tree.children[i].value.type == TokenType.OP and len(tree.children[i].children) == 0:
                    if i > 0 and i < len(tree.children) - 1:
                        if tree.children[i].value.name == "**":
                            stored_i = i
                            while i < len(tree.children):
                                if not (not (tree.children[i].value.type == TokenType.OP and len(tree.children[i].children) == 0) or tree.children[i].value.name == "**"):
                                    i -= 1
                                    break
                                i += 1
                            end = i + 1
                            i = stored_i
                            
                            tree.children[i].children = [tree.children[i-1], parse(tree.children[i+1:end])]
                            if tree.children[i-1].value.type == TokenType.UNIT:
                                tree.children[i].value.type = TokenType.POWERED_UNIT
                            del tree.children[i+1:end]
                            del tree.children[i-1]
                            i -= 1
                        else:
                            tree.children[i].children = [tree.children[i-1], tree.children[i+1]]
                            del tree.children[i+1]
                            del tree.children[i-1]
                            
                            i -= 1
                    else:
                        if not i > 0:
                            raise Exception(f"Missing left operand for operator {tree.children[i].value.name}")
                        else:
                            raise Exception(f"Missing right operand for operator {tree.children[i].value.name}")
                elif tree.children[i].value.type == TokenType.UNIT:
                    if i > 0: # there is a token to the left
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
                elif tree.children[i].value.type == TokenType.POWERED_UNIT:
                    logger.debug("helloo")
                    if i > 0: # there is a token to the left
                        # if the token on the left is (not an operator) or (has children)
                        if (not tree.children[i-1].value.type in [TokenType.OP, TokenType.UNARY_OP] or not len(tree.children[i-1].children) == 0):
                            tree.children[i].children.append(tree.children[i-1])
                            del tree.children[i-1]
                            i -= 1
                        else: # operator without children
                            if len(tree.children[i].children) < 3:
                                tree.children[i].children.append(Tree(Token(1.0, TokenType.NUMBER), []))
                            else:
                                logger.debug("nothing")
                    else:
                        tree.children[i].children.append(Tree(Token(1.0, TokenType.NUMBER), []))
                elif tree.children[i].value.type == TokenType.UNARY_OP:
                    if i < len(tree.children) - 1:
                        tree.children[i].children = [tree.children[i+1]]
                        del tree.children[i+1]

            i += 1
        logger.debug(tree.to_string())
        logger.debug("dunzo")
    logger.debug(f"RETURNING")
    
    return tree.children[0]

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
    [Token("**", TokenType.POWERED_UNIT)],
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