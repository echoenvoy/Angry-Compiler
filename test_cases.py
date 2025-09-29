# test_cases.py
# A collection of deliberately broken scripts to test the Angry Compiler.
# Run: python angry_compiler.py test_cases.py
# Or use the individual files in the tests/ directory.

# --- Uncomment ONE block at a time to test ---

# 1. SYNTAX ERROR
# def greet(name)
#     print("hello")

# 2. NAME ERROR
# print(undefined_variable)

# 3. TYPE ERROR
# result = "hello" + 42

# 4. ZERO DIVISION
a = 100
b = 0
print(a / b)

# 5. INDEX ERROR
# items = [1, 2, 3]
# print(items[99])

# 6. ATTRIBUTE ERROR
# x = 42
# print(x.upper())

# 7. IMPORT ERROR
# import totally_real_module

# 8. Clean (no errors)
# def square(n):
#     return n * n
# print(square(7))
