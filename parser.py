#!/usr/bin/env python3

from syntax import *
import tokenize

def parse(f):
    for i in tokenize.tokenize(f.readline):
        print(i)
