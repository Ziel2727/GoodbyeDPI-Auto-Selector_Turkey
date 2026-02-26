#!/usr/bin/env python3
"""Auto-fixer: validates Python files for syntax errors."""
import sys
import py_compile

def main():
    if len(sys.argv) < 2:
        print("Usage: python auto_fixer.py <filename.py>")
        sys.exit(1)
    
    filename = sys.argv[1]
    try:
        py_compile.compile(filename, doraise=True)
        print(f"[OK] {filename} - No syntax errors found.")
        sys.exit(0)
    except py_compile.PyCompileError as e:
        print(f"[ERROR] {filename} - Syntax error found:")
        print(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
