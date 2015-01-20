#!/usr/bin/env python3

class SyntaxElement:
    def __repr__(self):
        attrs = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        r = "%s\n" % self.__class__.__name__
        for a in attrs:
            if isinstance(getattr(self, a), list):
                rpr = "\n\t- " + "\n\t- ".join("\n\t\t".join(str(e).split("\n")) for e in getattr(self, a))
            else:
                rpr = str(getattr(self, a))
            r += "\t%s: %s\n" % (a, "\n\t".join(rpr.split("\n")))
        r = r[:-1].replace("\t", "  ")
        return r

class Keyword(SyntaxElement):
    def __init__(self, name):
        self.name = name

class Type(SyntaxElement):
    def __init__(self, name):
        self.name = name

class BaseType(Type):
    pass

class FooType(Type):
    pass

class Statement(SyntaxElement):
    pass

class Expression(Statement):
    pass

class InferredType(Type):
    def init(self, expr):
        assert isinstance(expr, Expression)
        self.name = None
        self.expr = expr

class Variable(Expression):
    def __init__(self, type, name):
        assert isinstance(type, Type)
        self.type = type
        self.name = name

class Value(Expression):
    def __init__(self, type, value):
        assert isinstance(type, Type)
        self.type = type
        self.value = value

class UnaryOperator(Expression):
    def __init__(self, name, arg):
        assert isinstance(arg, Expression)
        self.name = name
        self.arg = arg

class BinaryOperator(Expression):
    def __init__(self, name, left, right):
        assert isinstance(left, Expression) and isinstance(right, Expression)
        self.name = name
        self.left = left
        self.right = right

class Definition(Statement):
    def __init__(self, var, value):
        assert isinstance(var, Variable)
        assert isinstance(value, Value)
        self.var = var
        self.value = value

class ForStatement(Statement):
    def __init__(self, var, array, block):
        assert isinstance(var, Variable)
        assert isinstance(array, Expression)
        assert isinstance(block, Block)
        self.var = var
        self.array = array
        self.block = block

class IfStatement(Statement):
    def __init__(self, condition, block, other=None):
        assert isinstance(condition, Expression)
        assert isinstance(block, Block)
        assert isinstance(other, Block) or other is None
        self.condition = condition
        self.block = block
        self.other = other

class WhileStatement(Statement):
    def __init__(self, condition, block):
        assert isinstance(condition, Expression)
        assert isinstance(block, Block)
        self.condition = condition
        self.block = block

class Declaration(Statement):
    def __init__(self, var, value=None):
        assert isinstance(var, Variable)
        assert isinstance(value, Expression) or value is None
        self.var = var
        self.value = value

class Block(SyntaxElement):
    def __init__(self):
        self.statements = []
    def add(self, statement):
        assert isinstance(statement, Statement)
        self.statements.append(statement)

class FunctionDef(SyntaxElement):
    def __init__(self, rettype, name):
        assert isinstance(rettype, Type)
        self.name = name
        self.rettype = rettype
        self.params = []

    def addparam(self, var):
        assert isinstance(var, Variable)
        self.params.append(var)

class Function(SyntaxElement):
    def __init__(self, fd, body):
        assert isinstance(fd, FunctionDef)
        assert isinstance(body, Block)
        self.fd = fd
        self.body = body

class FunctionCall(Expression):
    def __init__(self, fn):
        assert isinstance(fn, FunctionDef)
        self.fn = fn
        self.paramValues = []

    def addparam(self, value):
        assert isinstance(value, Expression)
        self.paramValues.append(value)

class ArrayType(Type):
    def __init__(self, base, size):
        assert isinstance(base, BaseType) or base is None
        assert isinstance(size, Expression) or size is None
        self.baseType = base
        self.size = size
        if base is not None:
            self.name = self.baseType.name + "[]"
        else:
            self.name = "???[]"

class StructType(Type):
    def __init__(self, name):
        self.name = name
        self.fieldNames = []
        self.fieldTypes = []

    def add(self, type, name):
        assert isinstance(type, (BaseType, ArrayType, StructType, InferredType))
        self.fieldNames.append(name)
        self.fieldTypes.append(type)

