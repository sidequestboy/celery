celery
======

```python
# my_program.py
from celery import command, parse_args, help

@command
def my_func(arg_1, arg_2, kw=1):
    """Do something cool"""
    return int(arg_1) ^ int(arg_2) + kw

parse_args()
```

```
$ python my_program.py help
Usage: my_program.py [command]

Available commands:
  * help
    ? Get usage information about this script
    ? Multiple lines!
  * my_func <arg_1> <arg_2> [kw=1]
    ? Do something cool

$ python my_program.py my_func 1 2
3
```
