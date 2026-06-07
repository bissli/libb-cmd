import logging

import cmdline
import log

logger = logging.getLogger('cmd')


@log.job()
def main():
    opts, args, parser = cmdline.parse_args((
        ('-d', '--date', 'Date for calculation', 'P', cmdline.DateAction),
        ('-f', '--flag', 'Flag-only option with default', False, 'store_true'),
        ('-a', '--address', 'Email address list', 'bissli'),
    ), 'usage: %prog [options]')
    if args:
        parser.error('Unknown arguments: ' + ', '.join(args))

    logger.info(f'Example: date={opts.date},flag={opts.flag},address={opts.address}')


if __name__ == '__main__':
    main()
