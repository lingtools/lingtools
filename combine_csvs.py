#!/usr/bin/env python
"""
Combine CSVs.

Currently the only operations supported are pure concatenation and
concatentation while filtering duplicates.
"""

# Copyright 2013-2014 Constantine Lignos
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

import csv
import argparse

# TODO: Add support for more actions
CONCAT = "concat"
ACTIONS = (CONCAT,)


def concatenate(csv1_path, csv2_path, output_path, key, numeric_key):
    """Concatenate two CSVs, filtering duplicates if a key is specified."""
    with open(csv1_path, 'rb') as csv1, open(csv2_path, 'rb') as csv2:
        # TODO: Explain errors to the user here
        reader1 = csv.reader(csv1)
        reader2 = csv.reader(csv2)

        # If key is not numeric, read the headers
        if not numeric_key:
            headers1 = next(reader1)
            try:
                key_idx = headers1.index(key)
            except ValueError:
                raise ValueError("Key field {} is not in the headers of csv1".format(key))
        else:
            key_idx = key

        with open(output_path, 'wb') as output:
            writer = csv.writer(output)
            # TODO: Headers should be written here

            # Pass all of reader1 to the output
            csv1_keys = set()
            for row in reader1:
                csv1_keys.add(row[key_idx])
                writer.writerow(row)

            # Pass reader2 rows to the output if they don't conflict
            for row in reader2:
                row_key = row[key_idx]
                if row_key not in csv1_keys:
                    writer.writerow(row)


def main():
    """Parse arguments and call the combiner."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', help='action to take', choices=ACTIONS)
    parser.add_argument('csv1', help='first CSV')
    parser.add_argument('csv2', help='other CSV')
    parser.add_argument('output', help='output CSV')
    parser.add_argument('key', nargs='?', default=None,
                        help='field column name or number to use as a key')
    args = parser.parse_args()

    # Check for key and what kind it is
    key = args.key
    numeric_key = False
    if args.key is not None:
        try:
            key = int(args.key)
            # Offset by 1 since CSV rows are zero-indexed but input is
            # one-indexed
            key -= 1
        except TypeError:
            pass
        else:
            numeric_key = True

    if args.action == CONCAT:
        concatenate(args.csv1, args.csv2, args.output, key, numeric_key)

if __name__ == "__main__":
    main()
