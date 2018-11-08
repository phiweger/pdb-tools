#!/usr/bin/env python
#
# Copyright 2018 João Pedro Rodrigues
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Validates the PDB file ATOM/HETATM lines according to the format specifications.
Does not catch all the errors though... people are creative!

Usage:
    python pdb_format.py <pdb file>

Example:
    python pdb_format.py 1CTF.pdb

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import os
import re
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe with default option
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        if not os.path.isfile(args[0]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        fh = open(args[0], 'r')

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    return fh


def check_pdb_format(fhandle):
    """
    Compares each ATOM/HETATM line with the format defined on the official
    PDB website.

    http://deposit.rcsb.org/adit/docs/pdb_atom_format.html
    """

    has_error = False
    _fmt_check = (
        ('Atm. Num.', (slice(6, 11), re.compile('[\d\s]+'))),
        ('Alt. Loc.', (slice(11, 12), re.compile('\s'))),
        ('Atm. Nam.', (slice(12, 16), re.compile('\s*[A-Z0-9]+\s*'))),
        ('Spacer #1', (slice(16, 17), re.compile('[A-Z0-9 ]{1}'))),
        ('Res. Nam.', (slice(17, 20), re.compile('\s*[A-Z0-9]+\s*'))),
        ('Spacer #2', (slice(20, 21), re.compile('\s'))),
        ('Chain Id.', (slice(21, 22), re.compile('[A-Za-z0-9 ]{1}'))),
        ('Res. Num.', (slice(22, 26), re.compile('\s*[\d]+\s*'))),
        ('Ins. Code', (slice(26, 27), re.compile('[A-Z0-9 ]{1}'))),
        ('Spacer #3', (slice(27, 30), re.compile('\s+'))),
        ('Coordn. X', (slice(30, 38), re.compile('\s*[\d\.\-]+\s*'))),
        ('Coordn. Y', (slice(38, 46), re.compile('\s*[\d\.\-]+\s*'))),
        ('Coordn. Z', (slice(46, 54), re.compile('\s*[\d\.\-]+\s*'))),
        ('Occupancy', (slice(54, 60), re.compile('\s*[\d\.\-]+\s*'))),
        ('Tmp. Fac.', (slice(60, 66), re.compile('\s*[\d\.\-]+\s*'))),
        ('Spacer #4', (slice(66, 72), re.compile('\s+'))),
        ('Segm. Id.', (slice(72, 76), re.compile('[\sA-Z0-9\-\+]+'))),
        ('At. Elemt', (slice(76, 78), re.compile('[\sA-Z0-9\-\+]+'))),
        ('At. Charg', (slice(78, 80), re.compile('[\sA-Z0-9\-\+]+'))),
    )

    def _make_pointer(column):
        col_bg, col_en = column.start, column.stop
        pt = ['^' if c in range(col_bg, col_en) else ' ' for c in range(80)]
        return ''.join(pt)

    for iline, line in enumerate(fhandle, start=1):
        line = line.rstrip('\n').rstrip('\r')  # CR/LF
        if not line:
            continue

        # Type check for ATOM/HETATM lines
        if line[0:6] in ('ATOM  ', 'HETATM'):
            linelen = len(line)
            if linelen < 80:
                emsg = '[!] Line {0} is short: {1} < 80\n'
                sys.stderr.write(emsg.format(iline, linelen))
                has_error = True

            elif linelen > 80:
                emsg = '[!] Line {0} is long: {1} > 80\n'
                sys.stderr.write(emsg.format(iline, linelen))
                has_error = True

            for fname, (fcol, fcheck) in _fmt_check:
                field = line[fcol]
                if not fcheck.match(field):
                    pointer = _make_pointer(fcol)
                    emsg = '[!] Offending field ({0}) at line {1}\n'
                    sys.stderr.write(emsg.format(fname, iline))

                    sys.stderr.write(repr(line) + '\n')
                    sys.stderr.write(pointer + '\n')

                    has_error = True
                    break
        else:
            # Do basic line length check
            linelen = len(line)
            if linelen < 80:
                emsg = '[!] Line {0} is short: {1} < 80\n'
                sys.stderr.write(emsg.format(iline, linelen))
                has_error = True
            elif linelen > 80:
                emsg = '[!] Line {0} is long: {1} > 80\n'
                sys.stderr.write(emsg.format(iline, linelen))
                has_error = True

    if has_error:
        msg = '\nTo understand your errors, read the format specification:\n'
        msg += '  http://deposit.rcsb.org/adit/docs/pdb_atom_format.html\n'
        sys.stderr.write(msg)
    else:
        msg = 'It *seems* everything is OK.'
        sys.stdout.write(msg)


if __name__ == '__main__':

    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    check_pdb_format(pdbfh)

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)
