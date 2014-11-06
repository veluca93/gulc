#!/usr/bin/env python3

import sys
from io import BytesIO
from parser import parse

def main():
    if len(sys.argv) < 2:
        print("Usage: %s sourcefile" % sys.argv[0], file=sys.stderr)
        exit(1)
    try:
        AST = parse(sys.argv[1])
    except (NameError, SyntaxError):
        print("\033[01;31mError:\033[0m", end=" ", file=sys.stderr)
        print(sys.exc_info()[1], file=sys.stderr)
        exit(2)

if __name__ == "__main__":
    main()
