#!/usr/bin/python

import argparse
import datetime
import logging

from timewatch import TimeWatch, Override


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Automatic work hours reporting for timewatch.co.il')

    parser.add_argument('company', type=int, help='Company ID')
    parser.add_argument('user', help='user name/id')
    parser.add_argument('password', help='user password')

    today = datetime.date.today()
    parser.add_argument('-y', '--year', default=today.year, type=int, help='Year number to fill')
    parser.add_argument('-m', '--month', default=today.month, help='Month number or name')
    parser.add_argument('-v', '--verbose', default=0, action='count', help='increase logging level')
    parser.add_argument('-o', '--override', default=Override.unreported.value, type=int,
                        choices=[o.value for o in Override],
                        help=f'Control override behavior: {Override.describe()}')

    parser.add_argument('-s', '--start_time', default='10:00', help='punch-in time')
    parser.add_argument('-j', '--jitter', default=0, type=int, help='extra random minutes to add to duration.')
    parser.add_argument('-d', '--duration', default=9.0, type=float, help='hours duration (override preset default of timewatch)')

    args = parser.parse_args()

    verbosity_levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    verbosity = min(args.verbose, len(verbosity_levels) - 1)
    logging_level = verbosity_levels[verbosity]

    tw = TimeWatch(loglevel=logging_level,
                   override=args.override,
                   start_time=args.start_time,
                   jitter=args.jitter,
                   duration=args.duration)
    tw.login(args.company, args.user, args.password)
    tw.edit_month(args.year, args.month)
