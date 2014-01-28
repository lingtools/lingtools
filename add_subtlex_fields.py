#!/usr/bin/env python
"""Add SUBTLEX information to a CSV file.

By default, this will add the most useful frequency field from
SUBTLEX, FREQlow. You can specify another field name from the ones
defined in the help for the -f option. However, be warned that
changing this is often a bad idea. See:

Brysbaert, M., & New, B. (2009). Moving beyond Kucera and Francis: A
critical evaluation of current word frequency norms and the
introduction of a new and improved word frequency measure for American
English. Behavior Research Methods, 41(4), 977-990.

"""

# Copyright 2011-2014 Constantine Lignos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import csv
import argparse

from lingtools.corpus.subtlexreader import SubtlexDict, SubtlexEntry

DEFAULT_WORD_FIELD = 'word'
COUNT_LOW_FIELD = 'freq_count_low'
# Make a useful list of the fields available by getting the fields of
# an entry and removing 'word'.
SUBTLEX_FIELDS = fields = list(SubtlexEntry.__slots__)
SUBTLEX_FIELDS.remove("word")


def addsubtlex(in_path, outpath, subtlexpath, wordfield, subtlexfield):
    """Add subltex information, reading a CSV from in_path and writing to outpath."""
    subtlex = SubtlexDict(subtlexpath)

    # Add frequency information to each row. We replace '_' with '.'
    # because of R's historical aversion to underscore.
    output_field_name = subtlexfield.replace('_', '.')
    added_fields = [output_field_name]

    # Open trial input
    try:
        infile = open(in_path, 'rU')
        reader = csv.DictReader(infile)
    except IOError:
        print >> sys.stderr, "Couldn't open input file at", in_path
        sys.exit(1)

    # Open output
    try:
        outfile = open(outpath, 'wb')
        writer = csv.DictWriter(outfile, reader.fieldnames + added_fields)
    except IOError:
        print >> sys.stderr, "Couldn't open output file at", outpath
        sys.exit(1)

    # Write out header and data
    writer.writeheader()

    # Add data for each row
    for row in reader:
        # Try lookup lowercase first, and then capitalize. Since the
        # database only has one entry, lowercase or capitalized, we
        # just need to grab one.
        word = word_key = row[wordfield].lower()
        # If the word is not there as-is, try its capitalized version
        if word_key not in subtlex:
            word_key = word.capitalize()

        try:
            count = getattr(subtlex[word_key], subtlexfield)
        except KeyError:
            # Word is not in SUBTLEX
            count = 0
        except AttributeError:
            # Field requested is not in entries.
            print >> sys.stderr, ("No field {!r} in SUBTLEX entries.\n".format(subtlexfield) +
                                  "The fields in a SUBTLEX entry are:\n" +
                                  ", ".join(SUBTLEX_FIELDS))
            sys.exit(1)

        row.update(((output_field_name, count),))
        writer.writerow(row)

    # Clean up
    infile.close()
    outfile.close()


def main():
    """Parse arguments and call the adder."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('in_path', help='input CSV file')
    parser.add_argument('subtlex_path', help='SUBTLEX file')
    parser.add_argument('out_path', help='output CSV file')
    parser.add_argument('-w', nargs='?', default=DEFAULT_WORD_FIELD,
                        metavar='word_column',
                        help='name of column containing words')
    parser.add_argument('-f', nargs='?', default=COUNT_LOW_FIELD,
                        metavar='SUBTLEX_field',
                        choices=SUBTLEX_FIELDS,
                        help='name of from SUBTLEX to add')
    args = parser.parse_args()
    addsubtlex(args.in_path, args.out_path, args.subtlex_path, args.w, args.f)


if __name__ == "__main__":
    main()
