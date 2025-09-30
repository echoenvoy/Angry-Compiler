# 💀 Angry Compiler

> A Python compiler that insults the programmer.

---

## What is this

`angry_compiler.py` is a Python wrapper that compiles and runs your `.py` files — and then judges you for every mistake you make. It categorises errors, picks a contextually appropriate insult from a curated database, highlights the broken line in your source, and runs lightweight static analysis to complain about your code style before the program even runs.

It's mean. It's thorough. It's oddly useful.

---

## Features

- **Full Python compilation** — parses with `ast`, compiles with `compile()`, executes with `exec()`
- **Categorised insults** — different roasts for `SyntaxError`, `NameError`, `TypeError`, `IndexError`, `AttributeError`, `ZeroDivisionError`, `ImportError`, and generic runtime errors
- **Source snippet display** — highlights the line that broke with context and an arrow
- **Static analysis** — catches bare excepts, `== None`, mutable default args, wildcard imports, TODO comments, and absurdly long lines *before* execution
- **Success mode** — even when your code works, the compiler finds a way to be unimpressed
- **Interactive REPL** — type Python live and get judged in real time
- **Demo mode** — runs built-in broken examples so you can see all the failure categories
- **Stdin support** — pipe code in
- **Verbose mode** — full traceback if you actually want to debug
- **Colour output** — red for errors, yellow for warnings, green for success (dim green)
- **No dependencies** — pure stdlib

---

## Requirements

- Python 3.10 or newer (uses `match`-style type hints in annotations)
- A terminal with ANSI colour support (any modern terminal)
- A willingness to be judged

---

## Installation

No installation needed. Just download `angry_compiler.py`.

```bash
# Clone or download
git clone https://github.com/echoenvoy/Angry-Compiler
cd angry-compiler
```

---

## Usage

```bash
# Compile and run a file
python angry_compiler.py my_script.py

# With full traceback
python angry_compiler.py my_script.py --verbose

# Read from stdin
echo "print(1/0)" | python angry_compiler.py --stdin

# Interactive REPL
python angry_compiler.py --repl

# Demo mode (all error types)
python angry_compiler.py --demo

# Skip the ASCII art banner
python angry_compiler.py my_script.py --quiet
```

---

## Example output

```
  💀  Error on line 14   (SyntaxError)

  Message:  expected ':'
  
  🔥  Did you fall asleep on the keyboard and call it code?

  But hey — you ran the file. That's technically progress.

    12 │  def greet(name)
         ──────────────^
    13 │      print("hello")
```

---

## The insult categories

| Error | Sample insult |
|---|---|
| `SyntaxError` | "I don't know what this is, but it isn't Python." |
| `IndentationError` | "You mixed tabs and spaces. You monster." |
| `NameError` | "Where did you think 'x' was coming from? Narnia?" |
| `TypeError` | "You can't add those two things together. Not now. Not ever." |
| `IndexError` | "You're reaching past the end of the list. The list ended. You didn't notice." |
| `AttributeError` | "You assumed 'upper' existed on int. It does not. Assumptions are the mother of all bugs." |
| `ZeroDivisionError` | "You divided by zero. Congratulations. You've broken mathematics." |
| `ImportError` | "pip install your life choices." |
| Success | "It ran. Surprising. Don't get used to it." |

---

## Static analysis nits

The compiler also checks for:

- Lines longer than 120 characters
- Bare `except:` blocks
- `== None` instead of `is None`
- Mutable default arguments (`def f(x=[])`)
- TODO/FIXME comments (called out specifically)
- Wildcard imports (`from os import *`)

These are printed as warnings before execution.

---

## Running the tests

```bash
# Built-in demo
python angry_compiler.py --demo

# Or test individual files
python angry_compiler.py test_cases.py
```

---

## Project structure

```
angry_compiler/
├── angry_compiler.py   # The whole compiler. One file. Self-contained.
├── test_cases.py       # Sample broken code to test against
└── README.md           # This file
```

---

## Philosophy

This project exists because:

1. Error messages are usually fine. The *tone* is the problem.
2. Getting roasted after a typo is funnier than a wall of traceback.
3. Writing the insult database was extremely cathartic.
4. It's a real compiler. It actually runs your code. The insults are the bonus.

---

## Licence

MIT. Do whatever you want with it. If you make it meaner, share it back.

---

*"I'm not angry. I'm just deeply, profoundly disappointed."*
