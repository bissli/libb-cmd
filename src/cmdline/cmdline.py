"""Commandline alternative to `click` (https://github.com/pallets/click)
"""
import importlib
import logging
import os
import sys
from optparse import OptionParser

from libb import replacekey
from log import configure_logging

logger = logging.getLogger(__name__)

__all__ = ['parse_args']


def patch_environment(opts, config):
    if config is None:
        logger.error('Parser missing config module parameter')
        return
    with replacekey(os.environ, opts.environment, '1'):
        importlib.reload(config)
    try:
        assert opts.environment == config.ENVIRONMENT
        logger.info(f'Patched config.ENVIRONMENT = {opts.environment}')
    except AssertionError:
        logger.error(f'Failed to patch config.ENVIRONMENT = {opts.environment}')


def parse_args(options, usage=None, config=None):
    parser = create_parser(options, usage)
    opts, args = parser.parse_args()
    configure_logging(opts.logsetup)
    if opts.environment is not None:
        patch_environment(opts, config)
    logger.info(' '.join(sys.argv))
    return opts, args, parser


def create_parser(options, usage=None):
    """We parse each option: short, long, help, [default, [action, [dest]]]
    """
    from libb import scriptname
    parser = OptionParser(usage)
    for opt in options:
        opt = list(opt)
        shortopt, longopt, helptxt = opt.pop(0), opt.pop(0), opt.pop(0)
        default, action, dest = None, 'store', None
        if opt:
            default = opt.pop(0)
        if opt:
            action = opt.pop(0)
        if opt:
            dest = opt.pop(0)
        if shortopt and longopt:
            parser.add_option(shortopt, longopt, help=helptxt, action=action, default=default, dest=dest)
        else:
            parser.add_option(shortopt or longopt, help=helptxt, action=action, default=default, dest=dest)
    parser.add_option('-E', '--environment', dest='environment', default=None, help='set configuration environment')
    parser.add_option('-A', '--logapp', dest='logapp', default=scriptname(), help='set script name')
    parser.add_option('-S', '--logsetup', dest='logsetup', default='job', help='set logging setup type')
    parser.add_option('-V', '--loglevel', dest='loglevel', default=None, help='set logging level')
    return parser
