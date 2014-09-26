"""Module with function decorator to register functions as commandline
commands and to generate a commandline help text.

Adapted from @uniphil's code for Qcumber API
https://github.com/Queens-Hacks/qcumber-api/blob/master/manage.py
Copyright 2005, 2014 jameh and other contributors
 * Released under the MIT license
 * https://github.com/jameh/celery/blob/master/LICENSE

Usage:
.. code-block::
    from celery import command, parse_args, help

    @command
    def my_func(arg_1, arg_2):
        \"\"\"does something cool\"\"\"
        return int(arg_1) ^ int(arg_2)

    if __name__ == '__main__':
        parse_args()
"""

from functools import wraps
import sys
import inspect
import __main__


def command(func, _funcs={}):
    """Decorate functions with this to register them as commands"""

    # register the command
    func_name = func.__name__.lower()
    if func_name in _funcs:
        raise Exception('Duplicate definition for command {}'.format(func_name))
    if func.__module__ not in _funcs:
        _funcs[func.__module__] = {}

    _funcs[func.__module__][func_name] = func

    # play nice and leave the command where it was in this script
    @wraps(func)
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapped


def parse_args():
    """Get the command, or run 'help' if no command is provided
    .. note::
        The "=" sign is reserved to indicate keyword arguments e.g.

    .. code::
        python my_file.py my_func kw_1=3 lala
        python my_file.py my_func --kw_1 3 lala
        python my_file.py my_func -kw_1 3 lala
        python my_file.py my_func --kw_1=3 lala
        python my_file.py my_func -kw_1=3 lala

    Here, "lala" is the first positional argument, kw_1 is a
    keyword argument with value "3"
    """
    if len(sys.argv) < 2:
        cmd, raw_args = 'help', []
    else:
        cmd, raw_args = sys.argv[1].lower(), sys.argv[2:]

    # Parse raw_args into *args and **kwargs
    args = []
    kwargs = {}
    iter_args = iter(raw_args)
    for arg in iter_args:
        if arg[:2] == "--":
            if len(arg.split("=")) == 1:
                # eat the next arg for value
                kwargs[arg[2:]] = next(iter_args, "")
            elif len(arg[2:].split("=")) == 2:
                # use the rhs of "=" as value
                kwargs[arg[2:].split("=")[0]] = arg[2:].split("=")[1]
            else:
                raise Exception('Invalid kwarg format "{}"'.format(arg))
        elif arg[:1] == "-":
            if len(arg.split("=")) == 1:
                # eat the next arg for value
                kwargs[arg[1:]] = next(iter_args, "")
            elif len(arg[1:].split("=")) == 2:
                # use the rhs of "=" as value
                kwargs[arg[1:].split("=")[0]] = arg[1:].split("=")[1]
            else:
                raise Exception('Invalid kwarg format "{}"'.format(arg))
        elif len(arg.split("=")) == 2:
            kwargs[arg.split("=")[0]] = arg.split("=")[1]
        else:
            # positional arguments
            args.append(arg)

    # Map the command to a function, falling back to 'help' if it's not found
    funcs = command.__defaults__[0]['__main__']  # _funcs={}
    if cmd == 'help':
        output = command.__defaults__[0][__name__]['help']()
        print(output)
        return
    elif cmd not in funcs:
        output = command.__defaults__[0][__name__]['help'](cmd)
        print(output)
        return

    # do it!
    try:
        output = funcs[cmd](*args, **kwargs)
        # (and print the output)
        if output:
            print(output)
    except Exception as e:
        help()
        raise e


def _signature(name, func):
    """Return string repr of function signature"""
    defaults = inspect.getfullargspec(func).defaults or []
    args = inspect.getfullargspec(func).args or []
    arg_str_list = []

    n_positional_args = len(args) - len(defaults)

    for i in range(n_positional_args):
        # positional arguments
        arg_str_list.append('<' + args[i] + '>')

    for i in range(len(defaults)):
        # keyword arguments
        arg_str_list.append('[' + args[i + n_positional_args] + '=' + str(defaults[i]) + ']')

    return '{} {}'.format(name, ' '.join(arg_str_list))


def _indent(string, spaces=4, bullet='|'):
    lines = string.splitlines()
    for i, line in enumerate(lines):
        if line[:4] == ' ' * len(line[:4]):
            # starts with 4 spaces, indent and add a '|'
            lines[i] = ' ' * spaces + bullet + ' ' + line[4:]
        else:
            lines[i] = ' ' * spaces + bullet + ' ' + line

    return '\n'.join(lines)


@command
def help(*args, **kwargs):
    """Get usage information about this script
    Multiple lines!"""

    text = ""
    for i, f_name in enumerate(args):
        # Find f_name in available commands
        try:
            func = command.__defaults__[0]['__main__'][f_name]
            text += "Usage: {} {}\n".format(sys.argv[0],
                                            _signature(f_name, func))
            if func.__doc__:
                text += _indent(func.__doc__.strip(), spaces=2) + '\n'
            return text
        except KeyError:
            text += help() + '\n'
            text += 'Command "{}" not found :('.format(f_name)
            return text.strip()

    text += 'Usage: {} [command]\n'.format(sys.argv[0])

    # print module help here
    if __main__.__doc__ is not None:
        text += _indent(__main__.__doc__.strip(), spaces=2)

    text += '\n'
    text += 'Available commands:\n'
    for name, func in sorted(command.__defaults__[0]['__main__'].items()):  # _funcs={}
        text += _indent(_signature(name, func), 2, '*') + '\n'
        if func.__doc__:
            text += _indent(func.__doc__.strip(), 4, '|') + '\n'
    return text.strip()

if __name__ == '__main__':
    parse_args()
