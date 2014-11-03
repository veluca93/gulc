#!/usr/bin/env python3

class SyntaxElement:
    def convert(self):
        raise NotImplementedError("Please override this method")

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
        self.name = self.baseType + "[]"

class StructType(Type):
    fieldNames = []
    fieldTypes = []
    def add(self, type, name):
        assert isinstance(type, (BaseType, ArrayType, StructType))
        self.fieldNames.append(name)
        self.fieldType.append(type)

