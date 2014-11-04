#!/usr/bin/env python3

import sys
from io import BytesIO
from parser import parse

def main():
    if len(sys.argv) < 2:
        print("Usage: %s sourcefile" % sys.argv[0], file=sys.stderr)
        exit(1)
    AST = parse(open(sys.argv[1], 'rb'))

if __name__ == "__main__":
    main()
