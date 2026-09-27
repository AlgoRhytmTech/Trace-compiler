# TRACE

**Translational Runtime Analysis and Compilation Engine**

TRACE is a lightweight programming language and compiler project designed to make the stages between source code and execution explicit.

Instead of translating TRACE into another programming language, TRACE processes its own source language through a compiler pipeline and executes the resulting bytecode on the TRACE virtual machine.

> Current release: **v0.1.0**

---

## Overview

TRACE is built around a traditional language-processing pipeline:

```text
TRACE Source
     │
     ▼
   Lexer
     │
     ▼
  Parser
     │
     ▼
    AST
     │
     ▼
Semantic Analysis
     │
     ▼
Intermediate Rep.
     │
     ▼
  Bytecode
     │
     ▼
 TRACE VM
     │
     ▼
  Output
```

The project is intended primarily as a learning-oriented compiler and language implementation while still following a real compiler architecture.

---

## Features

TRACE v0.1.0 currently includes:

- Variables
- Integers and floating-point numbers
- Strings
- Booleans
- `null`
- Arithmetic expressions
- Comparisons
- Equality operators
- Assignment and compound assignment
- Increment and decrement operators
- `if`, `elif`, and `else`
- `while` loops
- `for` loops
- `range()`
- User-defined functions
- `return`
- Built-in functions
- Lexical analysis
- Parsing
- Abstract Syntax Tree
- Scope and symbol analysis
- Type checking
- Intermediate representation
- Bytecode generation
- Bytecode virtual machine
- Source-location-aware diagnostics
- Standalone executable builds

---

# Installation

Download the appropriate binary from the latest GitHub Release.

Available builds currently include:

```text
macOS ARM64
Linux x86_64
Windows x86_64
```

After downloading the binary, make it executable on Unix-like systems:

```bash
chmod +x trace
```

You can then run TRACE with:

```bash
./trace program.trc
```

---

# Your First TRACE Program

Create a file named:

```text
hello.trc
```

Add:

```trc
output("Hello, Kem Cho!");
```

Run it:

```bash
trace hello.trc
```

Output:

```text
Hello, Kem Cho!
```

---

# Language Syntax

## Variables

Variables are declared using `let`.

```trc
let x = 10;
let y = 20;

output(x);
output(y);
```

Variables can also be declared without an initial value: 

```trc
let x;
x = 10;

output(x);
```

TRACE infers the variable type from its value.

---

## Data Types

TRACE currently has the following basic types:

| Type | Example |
|------|---------|
| Integer | `10` |
| Float | `3.14` |
| String | `"TRACE"` |
| Boolean | `true` / `false` |
| Null | `null` |

Examples:

```trc
let age = 38;
let price = 67.67;
let name = "Anurag";
let active = true;
let value = null;
```

---

# Numbers

TRACE supports integer and floating-point arithmetic.

```trc
let a = 10;
let b = 3;

output(a + b);
output(a - b);
output(a * b);
output(a / b);
output(a % b);
```

The arithmetic operators are:

```text
+    Addition
-    Subtraction
*    Multiplication
/    Division
%    Modulo
```

Parentheses can be used to control precedence:

```trc
let result = (10 + 5) * 2;

output(result);
```

---

# Strings

Strings are written using double quotes.

```trc
let name = "TRACE";
output(name);
```

Strings can be concatenated using `+`:

```trc
let first = "Hello";
let second = "TRACE";

output(first + " " + second);
```

String repetition is also supported: (WOW)

```trc
let text = "TRACE";

output(text * 3);
```

---

# Booleans

TRACE provides:

```text
true
false
```

Example:

```trc
let isSunday = true;

output(isSunday);
```

Boolean values can be used in conditions:

```trc
let x = 10;

if x > 5 {
    output("x is greater than 5");
}
```

---

# Comparisons

TRACE supports:

```text
==    Equal
!=    Not equal
>     Greater than
<     Less than
>=    Greater than or equal
<=    Less than or equal
```

Example:

```trc
let x = 10;

if x == 10 {
    output("equal");
}

if x > 5 {
    output("greater");
}
```

---

# Assignment

Normal assignment:

```trc
let x = 10;

x = 20;
```

Compound assignment:

```trc
let x = 10;

x += 5;
x -= 2;
x *= 3;
x /= 2;
x %= 4;
```

Supported operators:

```text
= 
+=
-=
*=
/=
%=
```

---

# Increment and Decrement

TRACE supports prefix and postfix increment/decrement.

```trc
let x = 10;

x++;
output(x);
```

Prefix form:

```trc
let x = 10;

++x;
output(x);
```

Decrement:

```trc
let x = 10;

x--;
--x;

output(x);
```

---

# Conditional Statements

## if

```trc
let x = 10;

if x > 5 {
    output("x is greater than 5");
}
```

## if / else

```trc
let x = 3;

if x > 5 {
    output("greater");
} else {
    output("smaller or equal");
}
```

## if / elif / else

```trc
let x = 10;

if x > 10 {
    output("greater");
} elif x == 10 {
    output("equal");
} else {
    output("smaller");
}
```

---

# While Loops

TRACE supports `while` loops.

```trc
let x = 0;

while x < 5 {
    output(x);
    x++;
}
```

---

# For Loops

TRACE supports iteration using `for` and `in`. (Cant think of unique Syntax so......)

```trc
for i in range(1, 6) {
    output(i);
}
```

This produces:

```text
1
2
3
4
5
```

---

# range()

`range()` can be used to generate integer iteration ranges. (Again Cant think of Unique name )

```trc
range(1, 6)
```

Example:

```trc
for i in range(1, 6) {
    output(i);
}
```

The current implementation supports the range form used by the compiler's built-in:

```text
range(start, end)
```

---

# Functions

Functions are declared using `fxn`.  (Silly right ? but Unique)

```trc
fxn add(a, b) {
    return a + b;
}
```

Functions can be called like normal expressions:

```trc
fxn add(a, b) {
    return a + b;
}

let result = add(10, 20);

output(result);
```

Output:

```text
30
```

Functions can also contain control flow:

```trc
fxn check(x) {
    if x > 10 {
        return true;
    }

    return false;
}

output(check(20));
```

---

# return

`return` exits a function and optionally provides a value.

```trc
fxn square(x) {
    return x * x;
}
```

A function may also return without a value: 

```trc
fxn printValue(x) {
    output(x);
    return;
}
```

---

# Built-in Functions

TRACE currently provides several built-in functions.

## input()

Reads input and returns a string.

```trc
let name = input();

output(name);
```

## output()

Prints a value.

```trc
output("Hello");
output(42);
```

## len()

Returns the length of a supported value.

```trc
let name = "TRACE";

output(len(name));
```

## range()

Creates a range used by `for` loops.

```trc
for i in range(1, 6) {
    output(i);
}
```

---

# Comments

Comments are **not currently part of the TRACE language syntax**. Because they are damn Hard to do so

They will be introduced in a future language version. Coming Soon

---

# Operators (All pretty standard stuff)

## Arithmetic

| Operator | Meaning |
|----------|---------|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `%` | Modulo |

## Comparison

| Operator | Meaning |
|----------|---------|
| `==` | Equal |
| `!=` | Not equal |
| `>` | Greater than |
| `<` | Less than |
| `>=` | Greater than or equal |
| `<=` | Less than or equal |

## Assignment

| Operator | Meaning |
|----------|---------|
| `=` | Assignment |
| `+=` | Add and assign |
| `-=` | Subtract and assign |
| `*=` | Multiply and assign |
| `/=` | Divide and assign |
| `%=` | Modulo and assign |

## Increment / Decrement

| Operator | Meaning |
|----------|---------|
| `++x` | Prefix increment |
| `x++` | Postfix increment |
| `--x` | Prefix decrement |
| `x--` | Postfix decrement |

---

# Statement Terminators

Semicolons can be used to terminate statements. (wanted to use something else but that would make it stupid instead of unique)

```trc
let x = 10;
let y = 20;

output(x + y);
```

TRACE also accepts statements without semicolons in the parser: (OUT of Respect for python)

```trc
let x = 10
let y = 20

output(x + y)
```

Using semicolons is recommended.

---

# Compiler Architecture

TRACE is implemented as a multi-stage compiler pipeline.

## 1. Lexer

The lexer converts source characters into tokens.

```text
Source Code
     ↓
   Tokens
```

For example:

```trc
let x = 10;
```

is converted into a sequence containing tokens such as:

```text
LET
IDENTIFIER
EQ
NUMBER
SEMICOLON
```

---

## 2. Parser

The parser consumes tokens and constructs an Abstract Syntax Tree.

```text
Tokens
  ↓
Parser
  ↓
AST
```

The AST represents the structure of the program rather than the original text.

---

## 3. Semantic Analysis

The semantic analyzer performs checks such as:

- Variable lookup
- Scope handling
- Function lookup
- Function argument count
- Type checking
- Assignment compatibility
- Expression validation

Example:

```trc
let x = 10;

x = "hello";
```

The semantic stage can detect that the assignment is incompatible with the variable's inferred type.

---

## 4. Intermediate Representation

The AST is lowered into TRACE's intermediate representation.

Example:

```trc
let x = 10;
output(x + 5);
```

is represented internally using IR instructions rather than source-level syntax.

The IR provides a lower-level representation between the AST and bytecode.

---

## 5. Bytecode

TRACE converts the IR into bytecode instructions.

The bytecode contains operations required by the TRACE virtual machine.

---

## 6. TRACE Virtual Machine

The TRACE VM executes the generated bytecode.

```text
Source
  ↓
Lexer
  ↓
Parser
  ↓
AST
  ↓
Semantic Analysis
  ↓
Intermediate Rep.
  ↓
Bytecode
  ↓
TRACE VM
  ↓
Program Output
```

This allows TRACE to execute its own compiled representation without translating the program into C, C++, JavaScript, or another language.

---

# Project Structure

```text
Trace-compiler/
│
├── .github/
│   └── workflows/
│
├── examples/
│   └── *.trc
│
├── src/
│   ├── lexer.py
│   ├── parser.py
│   ├── ast.py
│   ├── semantics.py
│   ├── codegen.py
│   ├── bytecode.py
│   ├── bytecode_compiler.py
│   ├── vm.py
│   └── cli.py
│
├── test/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Building from Source

TRACE is implemented in Python.

Clone the repository:

```bash
git clone https://github.com/AlgoRhytmTech/Trace-compiler.git
cd Trace-compiler
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install PyInstaller if you want to build a standalone executable:

```bash
pip install pyinstaller
```

Build TRACE:

```bash
pyinstaller --onefile --name trace src/__main__.py
```

The resulting executable will be placed in:

```text
dist/
```

---

# Development

The compiler is currently under active development. by @SrvGopal and @anuragyadav999

The implementation is intentionally structured around separate compiler stages so that new language features can be introduced through the appropriate parts of the pipeline.

When adding a new language feature, the typical path is:

```text
Syntax
  ↓
Lexer
  ↓
Parser
  ↓
AST
  ↓
Semantic Analysis
  ↓
IR
  ↓
Bytecode
  ↓
VM
  ↓
Tests
```

---

# Testing

TRACE includes tests for compiler components and language behavior.

Run the test suite with:

```bash
pytest
```

New language features should include tests covering both valid programs and invalid programs where appropriate.

---

# Current Limitations

TRACE v0.1.0 is an early language release, because it was fun to release it.

The following are not currently part of the stable language:

- Arrays
- Maps / dictionaries
- Structs
- User-defined composite types
- Modules
- Imports
- Classes
- Generics
- Standard library
- Comments
- A mature package manager

These features may be introduced in future releases. Very Soon

---

# Roadmap

The language is expected to evolve incrementally.

Possible future work includes:

### Data structures

- Arrays
- Maps
- Tuples
- User-defined structures

### Language features

- Comments
- More complete boolean operators
- Better type declarations
- More expressive function types
- Pattern matching
- Modules and imports

### Compiler

- Improved diagnostics
- More optimization passes
- Better IR
- Bytecode improvements
- Runtime improvements

### Tooling

- Language server
- Formatter
- Debugger
- Better CLI tooling
- Package management

The roadmap is subject to change as the language architecture develops.

---

# Versioning

TRACE uses versioned releases.

For example:

```text
v0.1.0
v0.2.0
v0.3.0
...
v1.0.0
```

Each release represents a specific state of the compiler and language.

New language features can be introduced in later versions without changing previous releases.

---

# Contributing

Contributions, bug reports, and ideas are welcome. PLEASE DO IT 

Before contributing a language feature, consider how the feature affects the complete compiler pipeline:

```text
Lexer
Parser
AST
Semantic Analysis
IR
Bytecode
VM
Tests
```

---

# Project Status

TRACE is an experimental compiler and programming language project under active development.

The current focus is building a clear and extensible compiler pipeline while gradually expanding the language.

**TRACE**

> Understand what happens between source code and execution...because why should C++, Python, Java have all the fun 😂
