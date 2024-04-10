import logging

import cmdline
from log import log_exception

logger = logging.getLogger('cmd')


@log_exception(logger)
def main():
    opts, args, parser = cmdline.parse_args((
        ('-d', '--date', 'Date for calculation', 'P'),
        ('-f', '--flag', 'Flag-only option with default', False, 'store_true'),
        ('-a', '--address', 'Email address list', 'bissli'),
    ), 'usage: %prog [options]')
    if args:
        parser.error('Unknown arguments: ' + ', '.join(args))

    logger.info(f'Example: date={opts.date},flag={opts.flag},address={opts.address}')


if __name__ == '__main__':
    main()
