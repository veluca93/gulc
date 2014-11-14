#!/usr/bin/env python3

from syntax import *
import tokenize
import token
import glob

class AST:
    def __init__(self):
        self.rootnodes = []
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
symbols['in'] = Keyword('in')
symbols['if'] = Keyword('if')
symbols['for'] = Keyword('for')
symbols['else'] = Keyword('else')
symbols['while'] = Keyword('while')
symbols['struct'] = Keyword('struct')
symbols['void'] = FooType('void')
symbols['int'] = BaseType('int')
symbols['long'] = BaseType('long')
symbols['float'] = BaseType('float')
left_binding_power = {
    "unary": 1000,
    "*": 900,
    "/": 900,
    "%": 900,
    "+": 800,
    "-": 800,
    ">>": 700,
    "<<": 700,
    "<": 610,
    "<=": 610,
    ">": 610,
    ">=": 610,
    "==": 600,
    "!=": 600,
    "&": 510,
    "^": 505,
    "|": 500,
    "and": 410,
    "or": 400,
    "=": 300,
    "+=": 300,
    "-=": 300,
    "*=": 300,
    "/=": 300,
    "%=": 300,
    "&=": 300,
    "^=": 300,
    "|=": 300,
    "<<=": 300,
    ">>=": 300
}
token_iter = None
tok = None
DEBUG = False

def debug(fn):
    def dfn(*args, **kwargs):
        print("Start %s" % (fn.__name__))
        ret = fn(*args, **kwargs)
        print("End %s" % (fn.__name__))
        return ret
    return dfn if DEBUG else fn

def nt():
    global tok
    tok = next(token_iter)
    if DEBUG:
        print(tok)
    return tok.type != tokenize.ENDMARKER

@debug
def get_symbol(string = None):
    if string is None:
        string = tok.string
    if string not in symbols:
        raise NameError("Unknown name %s" % tok.string + lineerr())
    return symbols[tok.string]

@debug
def add_symbol(var):
    if var.name in symbols:
        raise NameError("Name %s already used" % var.name + lineerr())
    symbols[var.name] = var

def lineerr():
    nspaces = 0
    for c in tok.line[:tok.start[1]]:
        if c == '\t':
            nspaces = (nspaces//8)*8 + 8
        else:
            nspaces += 1
    return " on line %d position %d\n%s%s^" % (tok.start[0], tok.start[1], tok.line, " " * nspaces)

def expect(val):
    if isinstance(val, Keyword):
        expect(tokenize.NAME)
        if tok.string != val.name:
            raise SyntaxError("Expected %s, got %s" % (val.name, tok.string) + lineerr())
    elif tok.type != val and tok.exact_type != val:
        raise SyntaxError("Expected %s, got %s" % (token.tok_name[val], token.tok_name[tok.exact_type]) + lineerr())

def advance(val):
    expect(val)
    nt()

@debug
def parse_name():
    if isinstance(get_symbol(), FunctionDef):
        val = FunctionCall(get_symbol())
        nt()
        advance(tokenize.LPAR)
        while tok.exact_type != tokenize.RPAR:
            val.addparam(parse_expr())
            if tok.exact_type != tokenize.RPAR:
                advance(tokenize.COMMA)
        nt()
    elif isinstance(get_symbol(), Variable):
        val = get_symbol()
        nt()
        if tok.exact_type == tokenize.DOT:
            if not isinstance(val.type, StructType):
                raise NameError("Symbol %s is not a struct" % val.name + lineerr())
            nt()
            if tok.string not in val.type.fieldNames:
                raise NameError("Struct %s has no field named %s" % (val.name, tok.string) + lineerr())
            else:
                val = BinaryOperator(".", val, val.type.fieldTypes[val.type.fieldNames.index(tok.string)])
                nt()
        elif tok.exact_type == tokenize.LSQB:
            nt()
            idx = parse_expr()
            val = BinaryOperator("[]", val, idx)
            advance(tokenize.RSQB)
    else:
        raise NameError("Symbol %s is not a variable or function" % tok.string + lineerr())
    return val


@debug
def parse_expr(right_binding_power=0):
    val = None
    nbp = right_binding_power + 1
    while nbp >= right_binding_power:
        #TODO: string, array and struct literals
        if val is None and tok.exact_type in [token.PLUS, token.MINUS, token.TILDE] or tok.type == token.NAME and tok.string == "not":
            name = tok.string
            nt()
            val = UnaryOperator(name, parse_expr(left_binding_power["unary"]))
        elif tok.exact_type == token.LPAR:
            val = parse_expr(0)
            advance(token.RPAR)
        elif tok.type == token.NUMBER:
            try:
                val = Value(symbols["int"], int(tok.string))
            except:
                val = Value(symbols["float"], float(tok.string))
            nt()
        elif tok.type == token.NAME:
            val = parse_name()

        if tok.exact_type not in [token.RSQB, token.RPAR, token.RBRACE] and (tok.type == token.OP or tok.string in ["and", "or"]):
            try:
                nbp = left_binding_power[tok.string]
            except:
                raise SyntaxError("Unexpected operator %s" % tok.string + lineerr())
        else:
            nbp = -1

        if nbp >= right_binding_power:
            name = tok.string
            nt()
            right = parse_expr(nbp)
            val = BinaryOperator(name, val, right)

    return val

@debug
def parse_type():
    expect(tokenize.NAME)
    base_type = get_symbol()
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
    # TODO: fix the case in which the struct field has the same name as an already-defined symbol
    nt()
    struct = StructType(tok.string)
    advance(tokenize.NAME)
    if struct.name in symbols:
        raise NameError("Name %s already used" % struct.name + lineerr())
    advance(tokenize.COLON)
    advance(tokenize.NEWLINE)
    advance(tokenize.INDENT)
    extra_names = set()
    while tok.type != tokenize.DEDENT:
        if tok.type == tokenize.NL:
            nt()
            continue
        type = parse_type()
        name = tok.string
        expect(tokenize.NAME)
        extra_names.add(name)
        var = Variable(type, name)
        add_symbol(var)
        struct.add(type, name)
        nt()
        advance(tokenize.NEWLINE)
    for n in extra_names:
        del symbols[n]
    symbols[struct.name] = struct
    return struct

@debug
def parse_block():
    extra_names = set()
    block = Block()
    advance(tokenize.INDENT)
    while tok.type != tokenize.DEDENT:
        if tok.type == tokenize.NL:
            nt()
        elif tok.type == tokenize.NAME and tok.string == "for":
            nt()
            var = Variable(None, tok.string)
            advance(tokenize.NAME)
            advance(Keyword("in"))
            expr = parse_expr()
            advance(tokenize.COLON)
            advance(tokenize.NEWLINE)
            add_symbol(var)
            block = parse_block()
            nt()
            del symbols[var.name]
            block.add(ForStatement(var, expr, block))
        elif tok.type == tokenize.NAME and tok.string == "if":
            nt()
            expr = parse_expr()
            advance(tokenize.COLON)
            advance(tokenize.NEWLINE)
            block = parse_block()
            nt()
            if tok.string == "else":
                nt()
                advance(tokenize.COLON)
                advance(tokenize.NEWLINE)
                other = parse_block()
                nt()
                block.add(IfStatement(expr, block, other))
            else:
                block.add(IfStatement(expr, block))
        elif tok.type == tokenize.NAME and tok.string == "while":
            nt()
            expr = parse_expr()
            advance(tokenize.COLON)
            advance(tokenize.NEWLINE)
            block = parse_block()
            nt()
            block.add(WhileStatement(expr, block))
        elif tok.type == tokenize.NAME and isinstance(get_symbol(), Type):
            type = parse_type()
            var = Variable(type, tok.string)
            advance(tokenize.NAME)
            if var.name in symbols:
                raise NameError("Name %s already used" % var.name + lineerr())
            if tok.exact_type == tokenize.EQUAL:
                nt()
                val = parse_expr()
                block.add(Declaration(var, val))
            else:
                block.add(Declaration(var))
            extra_names.add(var.name)
            symbols[var.name] = var
            advance(tokenize.NEWLINE)
        else:
            block.add(parse_expr())
            advance(tokenize.NEWLINE)
    for n in extra_names:
        del symbols[n]
    return block

@debug
def parse_function():
    type = parse_type()
    fn = FunctionDef(type, tok.string)
    advance(tokenize.NAME)
    advance(tokenize.LPAR)
    while tok.exact_type != tokenize.RPAR:
        type = parse_type()
        fn.addparam(Variable(type, tok.string))
        advance(tokenize.NAME)
        if tok.exact_type != tokenize.RPAR:
            advance(tokenize.COMMA)
    advance(tokenize.RPAR)
    add_symbol(fn)
    if tok.exact_type == tokenize.NEWLINE:
        return fn
    advance(tokenize.COLON)
    advance(tokenize.NEWLINE)
    for v in fn.params:
        add_symbol(v)
    block = parse_block()
    for v in fn.params:
        del symbols[v]
    return Function(fn, block)

def _parse(f, ast):
    global token_iter
    token_iter = tokenize.tokenize(open(f, "rb").readline)
    while nt():
        if tok.type == tokenize.ENCODING:
            ast.set_encoding(tok.string)
        elif tok.type == tokenize.NEWLINE or tok.type == tokenize.NL:
            pass
        elif tok.type == tokenize.NAME and tok.string == "struct":
            ast.add_node(parse_struct())
        elif tok.type == tokenize.NAME and isinstance(get_symbol(), Type):
            ast.add_node(parse_function())
        else:
            if tok.type == tokenize.NAME:
                raise NameError("Unknown name %s" % tok.string + lineerr())
            raise SyntaxError("Unexpected %s" % token.tok_name[tok.exact_type] + lineerr())
    return ast

def parse(f):
    libast = AST()
    for i in glob.glob("headers/*.gul"):
        _parse(i, libast)
    ast = AST()
    _parse(f, ast)
    print(libast)
    print(ast)
    return libast, ast
