# TRACE

**TRACE — Translational Runtime Analysis and Compilation Engine**

TRACE is a programming language and compiler/runtime project developed as part of the AlgoRhythm project.

The compiler processes `.trc` source files through its own frontend, intermediate representation, bytecode generation, and runtime execution pipeline.

```text
TRACE Source (.trc)
        │
        ▼
     Lexer
        │
        ▼
     Parser
        │
        ▼
Semantic Analysis
        │
        ▼
       IR
        │
        ▼
 Bytecode Compiler
        │
        ▼
   TRACE Bytecode
        │
        ▼
    TRACE VM
        │
        ▼
     Program
```

---

# Building TRACE for Windows

This guide explains how to build the standalone Windows executable:

```text
trace.exe
```

The resulting executable can be distributed to Windows users without requiring them to install Python.

---

## Requirements

The Windows build requires:

- Windows 10 or later
- Python 3.10 or later
- Git
- Internet connection for installing PyInstaller

You do **not** need Visual Studio or any C/C++ compiler.

---

# 1. Clone the Repository

Open **PowerShell** or **Command Prompt**.

Clone the repository:

```powershell
git clone <REPOSITORY_URL>
```

Replace `<REPOSITORY_URL>` with the actual GitHub repository URL.

For example:

```powershell
git clone https://github.com/YOUR_USERNAME/compiler-srv.git
```

Enter the project directory:

```powershell
cd compiler-srv
```

Verify that the project files are present:

```powershell
dir
```

You should see directories/files similar to:

```text
examples
src
requirements.txt
```

---

# 2. Create a Python Virtual Environment

Create a virtual environment:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

After activation, your terminal should look similar to:

```text
(.venv) PS C:\...\compiler-srv>
```

---

# 3. Install PyInstaller

Install PyInstaller inside the virtual environment:

```powershell
python -m pip install pyinstaller
```

Verify the installation:

```powershell
python -m PyInstaller --version
```

A version number should be displayed.

---

# 4. Build TRACE

From the root of the repository, run:

```powershell
python -m PyInstaller --onefile --name trace src\__main__.py
```

PyInstaller will package the TRACE compiler and runtime into a single Windows executable.

The build may take a short amount of time.

When it finishes successfully, a `dist` directory will be created:

```text
compiler-srv
│
├── build
├── dist
│   └── trace.exe
│
├── examples
├── src
└── ...
```

The file you need is:

```text
dist\trace.exe
```

---

# 5. Test the Executable

Before distributing the executable, verify that it works.

Run:

```powershell
.\dist\trace.exe --version
```

Expected output:

```text
TRACE 0.1.0
```

You can also display the command-line help:

```powershell
.\dist\trace.exe --help
```

---

# 6. Run a TRACE Program

TRACE programs use the `.trc` extension.

An example program can be found in:

```text
examples\first.trc
```

Run it using:

```powershell
.\dist\trace.exe examples\first.trc
```

If the program executes successfully, the TRACE runtime will produce its output in the terminal.

---

# 7. Using TRACE Without Python

The purpose of the standalone build is that the final executable does **not** require Python to be installed on the target machine.

The file:

```text
trace.exe
```

contains the packaged TRACE application.

You can copy:

```text
dist\trace.exe
```

to another Windows machine and run it directly.

For example:

```powershell
.\trace.exe --version
```

or:

```powershell
.\trace.exe program.trc
```

---

# 8. Make TRACE Available Globally

For a normal command-line experience, `trace.exe` should be placed in a directory that is included in the Windows `PATH`.

A simple approach is to create a dedicated directory:

```text
C:\TRACE\
```

Copy:

```text
dist\trace.exe
```

into:

```text
C:\TRACE\trace.exe
```

Then add:

```text
C:\TRACE
```

to the Windows system/user `PATH`.

After restarting PowerShell, verify:

```powershell
trace --version
```

If everything is configured correctly, Windows should find TRACE regardless of the current directory.

You can then run:

```powershell
trace program.trc
```

from anywhere.

---

# 9. Using TRACE with VS Code

TRACE source code can be written in Visual Studio Code like any other text-based programming language.

Create a file:

```text
hello.trc
```

For example:

```trc
output "Hello from TRACE"
```

Open the project or file in VS Code.

Open the integrated terminal:

```text
Terminal → New Terminal
```

Then run:

```powershell
trace hello.trc
```

The TRACE executable handles compilation and execution.

---

# Command-Line Options

TRACE currently provides the following command-line options.

### Run a program

```powershell
trace program.trc
```

### Display lexer tokens

```powershell
trace program.trc --tokens
```

### Display the parsed AST

```powershell
trace program.trc --ast
```

### Run semantic analysis

```powershell
trace program.trc --check
```

### Display TRACE version

```powershell
trace --version
```

### Display help

```powershell
trace --help
```

---

# Build Output

PyInstaller generates several files and directories during the build.

The important output is:

```text
dist\
└── trace.exe
```

`trace.exe` is the standalone Windows executable.

The `build` directory and PyInstaller-generated specification file are build artifacts and are not required to run TRACE after the executable has been created.

---

# Troubleshooting

## `py` is not recognized

If:

```powershell
py --version
```

does not work, Python is either not installed or was not added to PATH.

Install Python and make sure the Python launcher/PATH options are enabled during installation.

Then reopen PowerShell.

---

## `git` is not recognized

If:

```powershell
git --version
```

does not work, Git is not installed or is not available through PATH.

Install Git and reopen PowerShell.

---

## PyInstaller is not recognized

Instead of:

```powershell
pyinstaller ...
```

use:

```powershell
python -m PyInstaller --onefile --name trace src\__main__.py
```

This ensures that the PyInstaller installation inside the active virtual environment is used.

---

## `trace.exe` does not run

First test it directly from the project directory:

```powershell
.\dist\trace.exe --version
```

If this works, but:

```powershell
trace --version
```

does not, the problem is most likely that the directory containing `trace.exe` has not been added to PATH.

---

# Development vs. Distribution

The Python source code is used during development.

The standalone executable is the distribution artifact.

```text
Development
    │
    ├── Python
    ├── src/
    └── PyInstaller
             │
             ▼
       trace.exe
             │
             ▼
       Windows Users
```

End users do not need the repository or Python installation to execute the packaged application.

---

# Project Structure

The main compiler/runtime components are organized approximately as follows:

```text
src/
├── __main__.py
├── ast.py
├── bytecode.py
├── bytecode_compiler.py
├── cli.py
├── codegen.py
├── interpreter.py
├── lexer.py
├── parser.py
├── semantics.py
├── vm.py
│
└── semantic/
    ├── __init__.py
    ├── diagnostics.py
    └── types.py
```

The major compilation stages are:

```text
Lexer
  ↓
Parser
  ↓
AST
  ↓
Semantic Analysis
  ↓
TRACE IR
  ↓
Bytecode
  ↓
TRACE VM
```

---

# Building a Windows Release

For a release build, use:

```powershell
python -m PyInstaller --onefile --name trace src\__main__.py
```

The release executable will be:

```text
dist\trace.exe
```

This is the file that can be distributed to Windows users.

---

# License

Add the project's license information here before public distribution.

---

# Status

TRACE is currently under active development.

The compiler pipeline, command-line interface, bytecode system, and runtime are being developed incrementally toward a complete programming language toolchain.
