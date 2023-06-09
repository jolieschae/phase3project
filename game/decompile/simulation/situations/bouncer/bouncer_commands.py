# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\bouncer\bouncer_commands.py
# Compiled at: 2015-06-16 22:14:21
# Size of source mod 2**32: 1808 bytes
from sims4.utils import create_csv
from situations.bouncer.bouncer import Bouncer
from situations.bouncer.bouncer_types import BouncerExclusivityCategory, BouncerExclusivityOption
import sims4.commands

@sims4.commands.Command('bouncer.print_exclusitivity_options')
def print_exclusivity_options(_connection=None):

    def callback(file):
        file.write('Category,' + ','.join((cat.name for cat in BouncerExclusivityCategory)) + '\n')
        for cat1 in BouncerExclusivityCategory:
            row = [cat1.name]
            for cat2 in BouncerExclusivityCategory:
                rule = Bouncer.are_mutually_exclusive(cat1, cat2)
                if rule is None:
                    row.append('')
                elif rule[2] == BouncerExclusivityOption.NONE:
                    row.append('<' if rule[0] == cat1 else '^')
                elif rule[2] == BouncerExclusivityOption.EXPECTATION_PREFERENCE:
                    row.append('EP')
                elif rule[2] == BouncerExclusivityOption.ALREADY_ASSIGNED:
                    row.append('AR')
                else:
                    row.append('ERROR')

            file.write(','.join(row) + '\n')

        file.write('\n\n')
        file.write('Legend:')
        file.write(',<,left category trumps above category\n')
        file.write(',^,above category trumps left category\n')
        file.write(',EP,expectation preference\n')
        file.write(',AR,already assigned\n')
        file.write(',blank,coexist\n')

    create_csv('bouncer_exclusivity_options', callback=callback, connection=_connection)