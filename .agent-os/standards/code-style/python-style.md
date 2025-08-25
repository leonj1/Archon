# Python Style Guide: The Elements of Code

## I. Elementary Rules of Usage

### 1. Use four spaces for indentation.
Wrong:
```python
def calculate():
  return 42  # Two spaces
```
Wrong:
```python
def calculate():
	return 42  # Tab
```
Right:
```python
def calculate():
    return 42  # Four spaces
```

Python's indentation is syntax. Be consistent. Four spaces have won.

### 2. Name according to convention.
- Functions and variables: `snake_case`
- Classes: `PascalCase`  
- Constants: `UPPER_SNAKE_CASE`

Wrong: `getUserName()`, `MaxRetries`, `defaultTimeout`  
Right: `get_user_name()`, `MAX_RETRIES`, `DEFAULT_TIMEOUT`

Python has spoken. Follow its conventions.

### 3. Use is for None comparisons.
Wrong: `if value == None:`  
Right: `if value is None:`

`None` is a singleton. Test identity, not equality.

### 4. Handle imports properly.
Wrong:
```python
from module import *
import sys, os, json
```
Right:
```python
import os
import sys
import json

from typing import Optional, List
from mypackage import specific_function
```

Import explicitly. Order matters: standard library, third-party, local. Alphabetize within groups.

## II. Elementary Principles of Composition

### 5. Make the function the unit of composition: one function, one purpose.
Wrong:
```python
def process_data(users):
    # Validate, transform, save, and notify
    for user in users:
        if not user.get('email'):
            raise ValueError()
        user['name'] = user['name'].upper()
        db.save(user)
        send_email(user)
    return users
```
Right:
```python
def validate_users(users):
    for user in users:
        if not user.get('email'):
            raise ValueError(f"Invalid email for user: {user}")

def transform_users(users):
    return [{'name': u['name'].upper(), **u} for u in users]

def save_users(users):
    for user in users:
        db.save(user)
```

Each function does one thing well.

### 6. Use list comprehensions judiciously.
Right for simple cases:
```python
squares = [x**2 for x in range(10)]
```
Wrong when it obscures intent:
```python
result = [process(x) for x in items if validate(x) and x > threshold for x in transform(x)]
```
Better:
```python
result = []
for item in items:
    if validate(item) and item > threshold:
        transformed = transform(item)
        result.append(process(transformed))
```

Clarity trumps cleverness.

### 7. Prefer explicit over implicit.
Wrong:
```python
def save(data, flag=True, mode=2):
    # What do flag and mode mean?
    pass
```
Right:
```python
def save(data, *, create_backup=True, compression_level=2):
    # Intent is clear
    pass
```

Python's Zen has spoken: "Explicit is better than implicit."

### 8. Use context managers for resource handling.
Wrong:
```python
file = open('data.txt')
content = file.read()
file.close()
```
Right:
```python
with open('data.txt') as file:
    content = file.read()
```

Context managers guarantee cleanup.

## III. A Few Matters of Form

### 9. Limit line length to 79 characters.
Wrong:
```python
result = some_function_with_a_long_name(first_argument, second_argument, third_argument, fourth_argument)
```
Right:
```python
result = some_function_with_a_long_name(
    first_argument, 
    second_argument,
    third_argument, 
    fourth_argument
)
```

Ancient terminals were 80 characters wide. The constraint remains useful.

### 10. Use type hints.
Wrong:
```python
def calculate(x, y):
    return x + y
```
Right:
```python
def calculate(x: float, y: float) -> float:
    return x + y
```

Modern Python is typed Python. Help your tools help you.

### 11. Document with docstrings.
Wrong:
```python
def calculate(x: float, y: float) -> float:
    # This calculates the sum
    return x + y
```
Right:
```python
def calculate(x: float, y: float) -> float:
    """Calculate the sum of two numbers.
    
    Args:
        x: First number
        y: Second number
        
    Returns:
        The sum of x and y
    """
    return x + y
```

Docstrings are documentation. Comments are clarification. Know the difference.

### 12. Use f-strings for formatting.
Wrong: `'Hello, ' + name + '!'`  
Wrong: `'Hello, {}!'.format(name)`  
Wrong: `'Hello, %s!' % name`  
Right: `f'Hello, {name}!'`

Python 3.6 gave us f-strings. The old ways are obsolete.

## IV. Words and Expressions Commonly Misused

### 13. == vs is
`==` tests equality of value. `is` tests identity of object.

Wrong: `if result is True:`  
Right: `if result:` or `if result == True:` (if you must)

Wrong: `if value == None:`  
Right: `if value is None:`

### 14. tuple vs list
Lists are mutable sequences. Tuples are immutable. Choose deliberately.

Wrong: `coordinates = [x, y]`  # Will never change  
Right: `coordinates = (x, y)`

Wrong: `point = (0, 0); point[0] = 1`  # Cannot modify  
Right: `point = [0, 0]; point[0] = 1`

### 15. Exception handling specificity
Wrong:
```python
try:
    process()
except:
    pass
```
Right:
```python
try:
    process()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
```

Catch only what you can handle. Never silence errors blindly.

## V. An Approach to Style

### 16. Omit needless code.
Wrong:
```python
if condition == True:
    return True
else:
    return False
```
Right:
```python
return condition
```

Wrong:
```python
result = []
for x in items:
    result.append(x * 2)
return result
```
Right:
```python
return [x * 2 for x in items]
```

Every line should earn its place.

### 17. Use Python's built-in functions.
Wrong:
```python
result = []
for item in items:
    if condition(item):
        result.append(item)
```
Right:
```python
result = filter(condition, items)
```

Wrong:
```python
total = 0
for x in numbers:
    total += x
```
Right:
```python
total = sum(numbers)
```

Python provides. Use what is given.

### 18. Guard against None.
Wrong:
```python
def process(data):
    return data.upper()
```
Right:
```python
def process(data: Optional[str]) -> Optional[str]:
    if data is None:
        return None
    return data.upper()
```
Or better:
```python
def process(data: Optional[str]) -> str:
    if data is None:
        raise ValueError("Data cannot be None")
    return data.upper()
```

Fail fast and explicitly.

### 19. Prefer composition over inheritance.
Wrong:
```python
class EmailSender(Logger, Validator, Formatter):
    # Multiple inheritance complexity
    pass
```
Right:
```python
class EmailSender:
    def __init__(self):
        self.logger = Logger()
        self.validator = Validator()
        self.formatter = Formatter()
```

Inheritance is not always the answer. Often it is the problem.

### 20. Be Pythonic.
Wrong:
```python
index = 0
while index < len(items):
    print(items[index])
    index += 1
```
Right:
```python
for item in items:
    print(item)
```

Wrong:
```python
if len(items) == 0:
    return None
```
Right:
```python
if not items:
    return None
```

Python has idioms. Learn them. Use them.

## VI. Final Reminders

**Trust the standard library.** Before you write, check if Python already provides.

**Read PEP 8, then read PEP 20.** The style guide and The Zen of Python are your foundations.

**Use a linter.** Tools like `ruff` and `mypy` catch what humans miss.

**Write for Python 3.** Python 2 is dead. Let it rest.
