#!/usr/bin/env python
"""Create a wordlist with frequencies from a file or standard input."""

# Copyright 2013 Constantine Lignos
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
import argparse
from collections import Counter


def count_words(input_file):
    """Return a counter of the words in the input."""
    return Counter(word.lower() for line in input_file
                   for word in line.strip().split())


def main():
    """Parse arguments, open the input, and write the ouput."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_file', help='input file, or - for stdin')
    args = parser.parse_args()
    input_path = args.input_file
    input_file = (open(input_path, 'U') if input_path != '-' else
                  sys.stdin)

    # Count and print output
    counter = count_words(input_file)
    for word, count in counter.most_common():
        print "{}\t{}".format(count, word)

    input_file.close()


if __name__ == "__main__":
    main()
