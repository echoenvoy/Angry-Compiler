import ast
import sys
import io
import os
import random
import tokenize
import traceback
import argparse
import textwrap
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass
from typing import Optional


INSULTS = {
    "syntax": [
        "Did you fall asleep on the keyboard and call it code?",
        "My cat has walked across my keyboard and produced better syntax.",
        "I've seen better structure in a bag of Skittles.",
        "Were you trying to write Python or just expressing your feelings?",
        "Congratulations. You've invented a new language. It's called WRONG.",
        "This isn't even wrong. It's beyond wrong. It's art.",
        "I don't know what this is, but it isn't Python.",
        "The syntax highlighter cried. Actual tears.",
        "Have you considered a career that doesn't involve typing?",
        "You're not writing code. You're writing a cry for help.",
        "The indentation alone is a human rights violation.",
        "I'm going to need a moment. This really hurt me personally.",
    ],
    "name_error": [
        "You're using variables you never defined. Bold strategy. Did it pay off?",
        "Where did you think '{name}' was coming from? Narnia?",
        "Oh, '{name}'? Never heard of her.",
        "NameError. As in, you don't know the NAME of the thing you're using. Classic.",
        "'{name}' is undefined. Much like your understanding of Python.",
        "You referenced '{name}' with the confidence of someone who has no idea what they're doing.",
        "'{name}' doesn't exist. Neither does your attention to detail.",
        "Hm. '{name}'. Where do you think this comes from? The void? The void doesn't do assignment.",
    ],
    "type_error": [
        "You can't add those two things together. Not now. Not ever. Not in any universe.",
        "A string and an integer walk into a bar. You tried to add them. The bar exploded.",
        "TypeError. You've confused Python. I didn't think that was possible.",
        "These types are incompatible. Like you and professional software development.",
        "You're mixing types like you're making a smoothie. This is not a smoothie.",
        "Python is strongly typed. You are not strongly anything.",
        "The types here make no sense. Much like this code as a whole.",
    ],
    "index_error": [
        "You're reaching past the end of the list. Ambition I admire. Execution I despise.",
        "Index out of range. The list ended. You didn't notice. Story of your life.",
        "There is no item at that index. There never was. There never will be.",
        "You indexed out of bounds. The bounds were right there. You walked past them.",
        "The list has {length} items. You asked for index {index}. I can't help you.",
        "Lists are zero-indexed. This is not news. This should not be news.",
    ],
    "attribute_error": [
        "'{obj}' doesn't have '{attr}'. You made that up.",
        "You assumed '{attr}' existed. It does not. Assumptions are the mother of all bugs.",
        "AttributeError. You've been accessing properties that don't exist like a ghost in your own codebase.",
        "'{attr}' is not a thing. On '{obj}' or anywhere else you'll ever look.",
        "Did you just autocomplete your way into a wrong attribute and not check? You did, didn't you.",
    ],
    "zero_division": [
        "You divided by zero. Congratulations. You've broken mathematics.",
        "Dividing by zero. The programming equivalent of 'what if I just don't think about it.'",
        "Zero division. I cannot even. And apparently neither can your denominator.",
        "You divided by zero on purpose, didn't you. I know you did.",
        "Math says no. Python says no. I say no. Everyone says no.",
    ],
    "import_error": [
        "'{module}' isn't installed. pip install your life choices.",
        "You're importing '{module}' like it grows on trees. It does not. pip install it.",
        "ModuleNotFoundError. The module wasn't found because you didn't install it. Or spelled it wrong. Or both.",
        "'{module}' doesn't exist. Either install it or check your spelling. Or both. Definitely both.",
        "ImportError. At least you're consistent in your failures.",
    ],
    "runtime": [
        "Your code compiled. Then it ran. Then it exploded. Growth.",
        "It passed syntax check. That was the only victory you'll get today.",
        "The code ran! ...And then crashed. Don't get excited.",
        "Runtime error. Your logic is valid Python. It just makes no sense.",
        "Your program started, panicked, and quit. Relatable, honestly.",
        "The interpreter tried its best. Your code did not.",
        "A runtime error means the computer understood you and still refused.",
    ],
    "warning": [
        "This isn't wrong enough to crash but wrong enough to judge.",
        "Python is warning you. I'm warning you. Nobody is listening.",
        "It works. Technically. But look at it. Just look at it.",
        "This is fine. The room is fine. Everything is fine. It isn't fine.",
    ],
    "success_but": [
        "It ran. Surprising. Don't get used to it.",
        "No errors. I'm suspicious. This feels like a trap.",
        "It works. I'm almost proud of you. Almost.",
        "Compiled and executed successfully. You've reached the floor, not the ceiling.",
        "Clean run. First time for everything, I suppose.",
        "No errors detected. Code quality, on the other hand...",
        "It runs. Whether it does what you INTENDED is a different question entirely.",
    ],
    "indentation": [
        "Indentation error. Spaces and tabs are not interchangeable. This is known.",
        "IndentationError. The one thing Python is picky about. The ONE thing.",
        "You mixed tabs and spaces. You monster.",
        "Python's indentation rules have been the same since 1991. Today is not the day they changed.",
        "The indentation here looks like you styled it with your elbow.",
    ],
    "general": [
        "I've reviewed worse. No I haven't.",
        "This code is brave. Brave and wrong.",
        "There's a special place in code review hell for this.",
        "I need a minute. This is a lot.",
        "You've done it again. Somehow.",
        "The audacity of this code is genuinely impressive.",
        "At least you tried. Unfortunately.",
        "I'm not angry. I'm just deeply, profoundly disappointed.",
        "Every line of this is a choice. Every choice is wrong.",
        "You wrote this with your full chest, and that's almost admirable.",
    ],
}

ENCOURAGING_FAILURES = [
    "But hey — you ran the file. That's technically progress.",
    "The error is descriptive. You can fix this. Whether you will is another matter.",
    "Stack trace provided above. It's a map to your mistake. Follow it.",
    "Debugging builds character. Allegedly.",
    "The computer is rooting for you. Sort of.",
]

LOADING_PHRASES = [
    "Bracing for impact...",
    "Reading your code (and judging it)...",
    "Parsing tokens with barely concealed contempt...",
    "Analysing... oh no...",
    "Compiling your mistakes...",
    "Running static analysis (this won't take long)...",
]


# ─────────────────────────────────────────────
#  COLOUR OUTPUT  (works on any ANSI terminal)
# ─────────────────────────────────────────────

class C:
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    GREEN  = "\033[92m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RESET  = "\033[0m"
    SKULL  = "💀"
    FIRE   = "🔥"
    CHECK  = "✓"
    WARN   = "⚠"

    @staticmethod
    def red(s):    return f"{C.RED}{s}{C.RESET}"
    @staticmethod
    def yellow(s): return f"{C.YELLOW}{s}{C.RESET}"
    @staticmethod
    def green(s):  return f"{C.GREEN}{s}{C.RESET}"
    @staticmethod
    def cyan(s):   return f"{C.CYAN}{s}{C.RESET}"
    @staticmethod
    def bold(s):   return f"{C.BOLD}{s}{C.RESET}"
    @staticmethod
    def dim(s):    return f"{C.DIM}{s}{C.RESET}"


def get_insult(category: str, **kwargs) -> str:
    pool = INSULTS.get(category, INSULTS["general"])
    insult = random.choice(pool)
    try:
        return insult.format(**kwargs)
    except KeyError:
        return insult


def get_encouragement() -> str:
    return random.choice(ENCOURAGING_FAILURES)


def get_loading() -> str:
    return random.choice(LOADING_PHRASES)

def categorise_exception(exc: Exception) -> tuple[str, dict]:
    """Map an exception to an insult category + format kwargs."""
    name = type(exc).__name__

    if isinstance(exc, SyntaxError):
        return "syntax", {}
    if isinstance(exc, IndentationError):
        return "indentation", {}
    if isinstance(exc, NameError):
        varname = str(exc).split("'")[1] if "'" in str(exc) else "it"
        return "name_error", {"name": varname}
    if isinstance(exc, TypeError):
        return "type_error", {}
    if isinstance(exc, IndexError):
        return "index_error", {"index": "?", "length": "?"}
    if isinstance(exc, AttributeError):
        parts = str(exc).split("'")
        obj  = parts[1] if len(parts) > 1 else "object"
        attr = parts[3] if len(parts) > 3 else "attribute"
        return "attribute_error", {"obj": obj, "attr": attr}
    if isinstance(exc, ZeroDivisionError):
        return "zero_division", {}
    if isinstance(exc, (ImportError, ModuleNotFoundError)):
        mod = str(exc).split("'")[1] if "'" in str(exc) else "that module"
        return "import_error", {"module": mod}

    return "runtime", {}


def print_banner():
    banner = r"""
  _   _  _  _  _  _ ___  _  _     __  ___  __  _  _ ___ _    ___ ___
 | |_| || \| || \/ ||   || \| |   / _|| _ \/  \| \| |_ _| |  | __| _ \
 |  _  || \  || \/ ||  _|| \  |  | |  | _ \ () |  ' || || |__| _||   /
 |_| |_||_|\_||_||_||___||_|\_|   \__||___/\__/|_|\_||_||____|___|_|_\
                                        ⚡ ANGRY EDITION ⚡
"""
    print(C.red(C.bold(banner)))
    print(C.dim("  A Python compiler that evaluates your code. And your life choices.\n"))


def print_separator(char="─", width=60, color=C.DIM):
    print(f"{color}{char * width}{C.RESET}")


def print_error_block(lineno: Optional[int], error_type: str, message: str, insult: str, encouragement: str):
    print_separator()
    if lineno:
        print(f"  {C.red(C.SKULL)} {C.bold(C.red(f'Error on line {lineno}'))}  {C.dim(f'({error_type})')}")
    else:
        print(f"  {C.red(C.SKULL)} {C.bold(C.red(f'{error_type}'))}")
    print()
    print(f"  {C.yellow('Message:')}  {message}")
    print()
    print(f"  {C.red(C.FIRE + '  ' + C.bold(insult))}")
    print()
    print(f"  {C.dim(encouragement)}")
    print_separator()


def print_success_block(output: str, insult: str):
    print_separator(char="─", color=C.GREEN)
    print(f"  {C.green(C.CHECK)}  {C.bold(C.green('Execution complete.'))}")
    print()
    if output.strip():
        print(f"  {C.cyan('Output:')}")
        for line in output.strip().splitlines():
            print(f"    {line}")
        print()
    print(f"  {C.yellow(C.FIRE + '  ' + insult)}")
    print_separator(char="─", color=C.GREEN)


def print_source_snippet(source: str, lineno: int, context: int = 2):
    """Print lines around the error with a pointer arrow."""
    lines = source.splitlines()
    start = max(0, lineno - 1 - context)
    end   = min(len(lines), lineno + context)

    print(f"\n  {C.cyan('Source snippet:')}")
    for i, line in enumerate(lines[start:end], start=start + 1):
        prefix = f"  {i:>4} │ "
        if i == lineno:
            print(C.red(f"{prefix}{line}"))
            print(C.red(f"       {'─' * (len(prefix) - 7)}^"))
        else:
            print(C.dim(f"{prefix}{line}"))
    print()


@dataclass
class Nit:
    line: int
    message: str
    category: str  # 'style' | 'logic' | 'suspicious'


def static_nits(source: str) -> list[Nit]:
    """Very lightweight style / smell detection."""
    nits = []
    lines = source.splitlines()

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip()

        # Long lines
        if len(line) > 120:
            nits.append(Nit(i, f"Line is {len(line)} characters long. PEP 8 says 79. Just saying.", "style"))

        # Bare except
        if line.strip() == "except:":
            nits.append(Nit(i, "Bare `except:` block detected. You're catching *everything*, including your own shame.", "suspicious"))

        # == None
        if "== None" in line:
            nits.append(Nit(i, "`== None` should be `is None`. This is not optional. This is Python.", "style"))

        # != None
        if "!= None" in line:
            nits.append(Nit(i, "`!= None` should be `is not None`. Basic Python. Very basic.", "style"))

        # print with no arguments in a loop (suspicious)
        if "print()" in line and any(kw in "".join(lines[max(0,i-3):i]) for kw in ["for ", "while "]):
            nits.append(Nit(i, "Empty `print()` inside what looks like a loop. Debugging by print, are we.", "suspicious"))

        # mutable default argument
        if "def " in line and ("=[]" in line or "={}" in line or "=[]" in line.replace(" ", "")):
            nits.append(Nit(i, "Mutable default argument detected. A classic Python trap. You stepped right in.", "logic"))

        # TODO / FIXME
        if any(tag in line.upper() for tag in ["# TODO", "# FIXME", "# HACK", "# XXX"]):
            nits.append(Nit(i, "Technical debt commented in code. This will never be fixed. We both know it.", "style"))

        # wildcard import
        if line.strip().startswith("from ") and "import *" in line:
            nits.append(Nit(i, "Wildcard import. Polluting the namespace like it owes you money.", "style"))

    return nits


def print_nits(nits: list[Nit]):
    if not nits:
        return
    print(f"\n  {C.yellow(C.WARN + '  Style and Logic Complaints:')}")
    for nit in nits:
        icon = {"style": "○", "logic": "◉", "suspicious": "●"}.get(nit.category, "○")
        print(f"  {C.yellow(f'  {icon} Line {nit.line:>3}:')} {nit.message}")
    print()


class AngryCompiler:

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    # --- parse stage ---

    def parse(self, source: str, filename: str = "<string>") -> Optional[ast.AST]:
        try:
            tree = ast.parse(source, filename=filename)
            return tree
        except IndentationError as e:
            insult = get_insult("indentation")
            print_error_block(e.lineno, "IndentationError", str(e), insult, get_encouragement())
            print_source_snippet(source, e.lineno or 1)
            return None
        except SyntaxError as e:
            insult = get_insult("syntax")
            print_error_block(e.lineno, "SyntaxError", str(e), insult, get_encouragement())
            print_source_snippet(source, e.lineno or 1)
            return None

    # --- execute stage ---

    def execute(self, source: str, filename: str = "<string>") -> bool:
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        try:
            code = compile(source, filename, "exec")
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, {"__name__": "__main__", "__file__": filename})  # noqa: S102

            output = stdout_capture.getvalue()
            err_out = stderr_capture.getvalue()

            insult = get_insult("success_but")
            print_success_block(output, insult)

            if err_out.strip():
                print(f"\n  {C.yellow('Stderr output (from your code):')}")
                for line in err_out.strip().splitlines():
                    print(f"    {C.dim(line)}")
                print()

            return True

        except Exception as exc:
            category, kwargs = categorise_exception(exc)
            insult = get_insult(category, **kwargs)

            tb = traceback.extract_tb(exc.__traceback__)
            lineno = tb[-1].lineno if tb else None

            print_error_block(lineno, type(exc).__name__, str(exc), insult, get_encouragement())

            if lineno:
                print_source_snippet(source, lineno)

            if self.verbose:
                print(f"\n  {C.dim('Full traceback:')}")
                for line in traceback.format_exc().strip().splitlines():
                    print(f"  {C.dim(line)}")
                print()

            return False

    # --- public compile method ---

    def compile_and_run(self, source: str, filename: str = "<string>") -> bool:
        print(f"\n  {C.dim(get_loading())}\n")

        # static analysis first
        nits = static_nits(source)

        # parse
        tree = self.parse(source, filename)
        if tree is None:
            return False

        # print nits after successful parse
        print_nits(nits)

        # execute
        return self.execute(source, filename)


DEMO_SNIPPETS = [
    ("syntax_error.py", """
# Classic syntax error
def greet(name)
    print("Hello " + name)
"""),
    ("name_error.py", """
# Using undefined variable
result = x + 10
print(result)
"""),
    ("type_error.py", """
# Type mismatch
age = "twenty"
print(age + 5)
"""),
    ("zero_div.py", """
# Dividing by zero
a = 100
b = 0
print(a / b)
"""),
    ("index_error.py", """
# Index out of range
numbers = [1, 2, 3]
print(numbers[10])
"""),
    ("clean_code.py", """
# Perfectly valid code (mostly)
def add(a, b):
    return a + b

result = add(3, 7)
print(f"3 + 7 = {result}")
"""),
    ("nit_code.py", """
# Code with style issues
from os import *

def process(data=[]):
    try:
        x = data[0] == None
        return x
    except:
        pass

# TODO: fix this later
process()
"""),
]


def run_demo():
    compiler = AngryCompiler(verbose=False)
    print_banner()
    print(C.bold(C.cyan("  ── DEMO MODE: Showcasing all failure types ──\n")))

    for filename, source in DEMO_SNIPPETS:
        print(f"\n{C.bold(C.cyan(f'  ▶  {filename}'))}")
        print(C.dim(textwrap.indent(textwrap.dedent(source).strip(), "    ")))
        print()
        compiler.compile_and_run(textwrap.dedent(source), filename)
        print()
        input(C.dim("  [press Enter for next example] "))
        print()



def run_repl():
    compiler = AngryCompiler(verbose=True)
    print_banner()
    print(C.bold(C.cyan("  Interactive mode. Type Python code. Type 'exit' or Ctrl-C to quit.")))
    print(C.dim("  Multiline: end a line with \\ to continue. Empty line runs the block.\n"))

    while True:
        try:
            lines = []
            prompt = C.yellow("  >>> ")
            line = input(prompt)

            if line.strip().lower() in ("exit", "quit"):
                print(C.dim("\n  Leaving so soon? Fine. Go debug somewhere else.\n"))
                break

            while line.endswith("\\"):
                lines.append(line[:-1])
                line = input(C.yellow("  ... "))

            lines.append(line)
            source = "\n".join(lines)

            if source.strip():
                print()
                compiler.compile_and_run(source, "<repl>")
                print()

        except (KeyboardInterrupt, EOFError):
            print(C.dim("\n\n  Fine. Goodbye.\n"))
            break



def main():
    parser = argparse.ArgumentParser(
        prog="angry_compiler",
        description="A Python compiler that insults the programmer.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python angry_compiler.py my_script.py
          python angry_compiler.py --demo
          python angry_compiler.py --repl
          echo "print(1/0)" | python angry_compiler.py --stdin
          python angry_compiler.py my_script.py --verbose
        """),
    )
    parser.add_argument("file", nargs="?", help="Python file to compile and run")
    parser.add_argument("--stdin",   action="store_true", help="Read code from stdin")
    parser.add_argument("--demo",    action="store_true", help="Run built-in demo examples")
    parser.add_argument("--repl",    action="store_true", help="Start interactive REPL")
    parser.add_argument("--verbose", action="store_true", help="Show full tracebacks")
    parser.add_argument("--quiet",   action="store_true", help="Skip the banner")

    args = parser.parse_args()

    if args.demo:
        run_demo()
        return

    if args.repl:
        run_repl()
        return

    compiler = AngryCompiler(verbose=args.verbose)

    if not args.quiet:
        print_banner()

    if args.stdin:
        source = sys.stdin.read()
        filename = "<stdin>"
    elif args.file:
        if not os.path.exists(args.file):
            print(C.red(f"\n  {C.SKULL}  File not found: '{args.file}'"))
            print(C.yellow("  Did you even check the path? Classic.\n"))
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as fh:
            source = fh.read()
        filename = args.file
    else:
        parser.print_help()
        print(C.dim("\n  You gave me nothing. Nothing to judge. That's almost impressive.\n"))
        sys.exit(0)

    success = compiler.compile_and_run(source, filename)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
