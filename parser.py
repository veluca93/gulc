#!/usr/bin/env python3

from syntax import *
import tokenize
import token

class AST:
    encoding = None
    rootnodes = []
    def set_encoding(self, encoding):
        self.encoding = encoding
    def add_node(self, node):
        self.rootnodes.append(node)
    def __repr__(self):
        r = "Encoding: %s\n" % self.encoding
        for i in self.rootnodes:
            r += str(i) + '\n'
        r = r.strip()
        return r

symbols = dict()
token_iter = None
tok = None
DEBUG = False

def debug(fn):
    def dfn(*args, **kwargs):
        print("Start %s" % fn.__name__)
        ret = fn(*args, **kwargs)
        print("End %s" % fn.__name__)
        return ret
    return dfn if DEBUG else fn

def nt():
    global tok
    tok = next(token_iter)
    if DEBUG:
        print(tok)
    return tok.type != tokenize.ENDMARKER

def lineerr():
    nspaces = 0
    for c in tok.line[:tok.start[1]]:
        if c == '\t':
            nspaces = (nspaces//8)*8 + 8
        else:
            nspaces += 1
    return " on line %d position %d\n%s%s^" % (tok.start[0], tok.start[1], tok.line, " " * nspaces)

def expect(val):
    if tok.type != val and tok.exact_type != val:
        raise SyntaxError("Expected %s, got %s" % (token.tok_name[val], token.tok_name[tok.exact_type]) + lineerr())

def advance(val):
    expect(val)
    nt()

@debug
def parse_expr():
    #TODO: implement this
    if tok.type == tokenize.NAME:
        if tok.string not in symbols or not isinstance(symbols[tok.string], Variable):
            raise SyntaxError("Unknown variable %s" % tok.string + lineerr())
        val = symbols[tok.string]
    elif tok.type == tokenize.NUMBER:
        val = Value(BaseType("int"), int(tok.string))
    else:
        raise NotImplementedError("Expression parsing is not complete yet!")
    nt()
    return val

@debug
def parse_type():
    expect(tokenize.NAME)
    if tok.string not in symbols:
        raise SyntaxError("Unknown name %s" % tok.string + lineerr())
    base_type = symbols[tok.string]
    if not isinstance(base_type, Type):
        raise SyntaxError("%s does not represent a type" % tok.string + lineerr())
    nt()
    if isinstance(base_type, StructType):
        return base_type
    if tok.exact_type != tokenize.LSQB:
        return base_type
    nt()
    if tok.exact_type == tokenize.RSQB:
        nt()
        return ArrayType(base_type, None)
    size = parse_expr()
    advance(tokenize.RSQB)
    return ArrayType(base_type, size)

@debug
def parse_struct():
    nt()
    struct = StructType(tok.string)
    advance(tokenize.NAME)
    advance(tokenize.COLON)
    advance(tokenize.NEWLINE)
    advance(tokenize.INDENT)
    extra_names = set()
    while tok.type != tokenize.DEDENT:
        type = parse_type()
        name = tok.string
        expect(tokenize.NAME)
        extra_names.add(name)
        var = Variable(type, name)
        if name in symbols:
            raise SyntaxError("Name %s already used" % tok.string + lineerr())
        symbols[name] = var
        struct.add(type, name)
        nt()
        advance(tokenize.NEWLINE)
    for n in extra_names:
        del symbols[n]
    symbols[struct.name] = struct
    return struct

def parse(f):
    ast = AST()
    symbols['struct'] = Keyword('struct')
    symbols['int'] = BaseType('int')
    symbols['long'] = BaseType('long')
    global token_iter
    token_iter = tokenize.tokenize(f.readline)
    while nt():
        if tok.type == tokenize.ENCODING:
            ast.set_encoding(tok.string)
        elif tok.type == tokenize.NEWLINE or tok.type == tokenize.NL:
            pass
        elif tok.type == tokenize.NAME and tok.string == "struct":
            ast.add_node(parse_struct())
        elif tok.type == tokenize.NAME and isinstance(symbols[tok.string], Type):
            # parse a function declaration
            pass
        else:
            raise SyntaxError("Unexpected %s" % token.tok_name[tok.exact_type] + lineerr())
    print(ast)
    return ast
