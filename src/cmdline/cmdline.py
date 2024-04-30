"""Wrapper around python default `argparse`
"""
import argparse
import importlib
import logging
import os
import sys

from libb import replacekey, scriptname
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
    opts, args = parser.parse_known_args()
    configure_logging(app=opts.logapp, setup=opts.logsetup, level=opts.loglevel)
    if opts.environment is not None:
        patch_environment(opts, config)
    logger.info(' '.join(sys.argv))
    return opts, args, parser


def create_parser(options, usage=None):
    """We parse each option: short, long, help, [default, [action, [dest]]]
    """
    parser = argparse.ArgumentParser(usage)
    # specified args
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
            parser.add_argument(shortopt, longopt, help=helptxt, action=action, default=default, dest=dest)
        else:
            parser.add_argument(shortopt or longopt, help=helptxt, action=action, default=default, dest=dest)
    # default args
    parser.add_argument('-E', '--environment', dest='environment', default=None, help='set configuration environment')
    parser.add_argument('-A', '--logapp', dest='logapp', default=scriptname(), help='set script name')
    parser.add_argument('-S', '--logsetup', dest='logsetup', default='job', help='set logging setup type')
    parser.add_argument('-V', '--loglevel', dest='loglevel', default=None, help='set logging level')
    return parser
