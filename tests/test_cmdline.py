import argparse
import os
import site
import sys

import pytest
import wrapt
from opendate import Date


@wrapt.patch_function_wrapper('cmdline', 'parse_args')
def patch_mail_send_mail(wrapped, instance, args, kwargs):
    """Patch parse args with our config

    **One example of how to patch-in config**
    """
    HERE = os.path.dirname(os.path.abspath(__file__))
    site.addsitedir(HERE)
    import config
    kwargs['config'] = config
    return wrapped(*args, **kwargs)


import cmdline


def test_default_options():
    sys.argv = ['test_cmdline.py']
    opts, args, parser = cmdline.parse_args([], 'usage: foo')
    assert len(args) == 0
    assert opts.environment is None
    assert opts.loglevel is None
    assert opts.logsetup == 'job'
    with pytest.raises(AttributeError):
        opts.badarg

    sys.argv = ['test_cmdline.py',
                '--environment', 'dev',
                '--loglevel', 'info',
                '--logsetup', 'cmd',
                'foo',
                'bar']
    opts, args, parser = cmdline.parse_args([], 'usage: foo')
    assert len(args) == 2
    assert args[0] == 'foo'
    assert args[1] == 'bar'
    assert opts.environment == 'dev'
    assert opts.loglevel == 'info'
    assert opts.logsetup == 'cmd'


def test_custom_options():
    """Test default, action, and destination options.
    """
    sys.argv = ['test_cmdline.py',
                '-b',
                '--dest',
                '--value', '10',
                '-s', 'short',
                '--long', 'long',
                'foo',
                'bar']
    opts, args, parser = cmdline.parse_args((
            ('-b', '--boolean', 'A boolean option', False, 'store_true'),
            ('-f', '--default', 'A boolean option', False, 'store_true'),
            ('-d', '--dest', 'An option with different name', True, 'store_false', 'destination'),
            ('-v', '--value', 'A value option'),
            ('-s', None, 'Only a short option'),
            (None, '--long', 'Only a long option'),
            ))
    assert len(args) == 2
    assert args[0] == 'foo'
    assert args[1] == 'bar'
    assert opts.boolean is True
    assert opts.default is False
    assert opts.value == '10'
    assert opts.s == 'short'
    assert opts.long == 'long'


def test_option_custom_boolean():
    """Test custom boolean option with store_true action.
    """
    sys.argv = ['test_cmdline.py', '-b']
    args = [('-b', '--boolean', 'A boolean option', False, 'store_true')]
    opts, args, parser = cmdline.parse_args(args)
    assert len(args) == 0
    assert opts.boolean is True


class FooAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError('nargs not allowed')
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print(f'{namespace!r} {values!r} {option_string!r}')
        setattr(namespace, self.dest, values)


def test_option_custom_action():
    """Test custom argparse action.
    """
    sys.argv = ['test_cmdline.py', '-a', 'value']
    args = [('-a', '--action', 'A custom action', None, FooAction)]
    opts, args, parser = cmdline.parse_args(args)
    assert len(args) == 0
    assert opts.action == 'value'


def test_date_action():
    """Verify DateAction parses date strings using opendate.
    """
    sys.argv = ['test_cmdline.py', '-d', '2024-01-15']
    args = [('-d', '--date', 'A date option', None, cmdline.DateAction)]
    opts, args, parser = cmdline.parse_args(args)
    assert len(args) == 0
    assert isinstance(opts.date, Date)
    assert opts.date.year == 2024
    assert opts.date.month == 1
    assert opts.date.day == 15


def test_date_action_default():
    """Verify DateAction handles default string values.
    """
    sys.argv = ['test_cmdline.py']
    args = [('-d', '--date', 'A date option', '2023-12-25', cmdline.DateAction)]
    opts, args, parser = cmdline.parse_args(args)
    assert len(args) == 0
    assert isinstance(opts.date, Date)
    assert opts.date.year == 2023
    assert opts.date.month == 12
    assert opts.date.day == 25


if __name__ == '__main__':
    pytest.main([__file__])
