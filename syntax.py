#!/usr/bin/env python3

class SyntaxElement:
    def convert(self):
        raise NotImplementedError("Please override this method")
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
    name = None
    def __init__(self, name):
        self.name = name

class Type(SyntaxElement):
    name = None
    def __init__(self, name):
        self.name = name

class BaseType(Type):
    pass

class FooType(Type):
    pass

class Valued(SyntaxElement):
    pass

class Variable(Valued):
    type = None
    name = None
    def __init__(self, type, name):
        assert isinstance(type, Type)
        self.type = type
        self.name = name

class Value(Valued):
    type = None
    value = None
    def __init__(self, type, value):
        assert isinstance(type, Type)
        self.type = type
        self.value = value

class Operator(SyntaxElement):
    name = None
    def __init__(self, name):
        self.name = name

class Expression(Valued):
    left = None
    right = None
    op = None
    def __init__(self, left, op, right):
        assert (isinstance(left, Valued) and isinstance(right, Valued) and isinstance(op, Operator)) or \
               (left is None and isinstance(op, Operator) and isinstance(right, Valued)) or \
               (left is None and op is None and isinstance(right, Valued))
        self.left = left
        self.op = op
        self.right = right

class ArrayType(Type):
    baseType = FooType("void")
    size = None
    def __init__(self, base, size):
        assert isinstance(base, BaseType)
        assert isinstance(size, Valued) or size is None
        self.baseType = base
        self.size = size
        self.name = self.baseType.name + "[]"

class StructType(Type):
    def __init__(self, name):
        self.name = name
        self.fieldNames = []
        self.fieldTypes = []

    def add(self, type, name):
        assert isinstance(type, (BaseType, ArrayType, StructType))
        self.fieldNames.append(name)
        self.fieldTypes.append(type)

