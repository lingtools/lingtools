#!/usr/bin/env python
"""Randomly sample items from a list of items with their frequencies."""

# Copyright 2012-2013 Constantine Lignos
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
import random
from operator import itemgetter


def parse_countword_line(line):
    """Parse a line of the form '<count> <word>' into a tuple (word, count)."""
    # Floats are rounded to the nearest integer
    try:
        count, word = line.split()
        return (word, int(round(float(count))))
    except ValueError:
        print >> sys.stderr, \
            "Error: line does not match expected <count> <word> " \
            "format: {!r}".format(line.strip())
        sys.exit(1)


def load_word_counts(path):
    """Load a wordlist file into a dictionary of form {word: count}."""
    with open(path, 'rU') as wordlist:
        return dict(parse_countword_line(line) for line in wordlist)


def counts_to_freqs(countdict):
    """Convert a dictionary with counts as values to frequencies."""
    # Convert total to float so dividing by it will produce a float
    total = float(sum(countdict.itervalues()))
    # Convert counts to frequencies
    return {word: (count / total) for word, count in countdict.iteritems()}


def sample_n_keys(freq_dict, numkeys):
    """Sample numkeys keys from freq_dict, whose values are frequencies.

    Uses Shannon-Miller-Selfridge sampling. It may be possible to speed
    up sampling by using bisection instead of summing, but this is fast
    enough."""

    # Sort into word and freq lists. Sorting speeds up sampling by
    # putting frequent items first.
    words, freqs = zip(*sorted(freq_dict.items(), key=itemgetter(1),
                               reverse=True))
    # Sampling loop, run numkeys times
    for _ in range(numkeys):
        # Draw a random number and sum frequencies until we hit it
        rand = random.random()
        freq_sum = 0.0
        for idx, freq in enumerate(freqs):
            freq_sum += freq
            if freq_sum > rand:
                yield words[idx]
                # After yielding, return to the sampling loop
                break


def main():
    """Parse arguments, get the frequencies, and print the samples."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('wordlist', help='input wordlist')
    parser.add_argument('nsamples', help='number of samples to produce',
                        type=int)
    parser.add_argument('seed', help='random seed to use', nargs='?', type=int)
    args = parser.parse_args()
    wordlist_path = args.wordlist
    n_samples = args.nsamples
    seed = args.seed
    if seed is not None:
        random.seed(seed)

    word_freqs = counts_to_freqs(load_word_counts(wordlist_path))
    for key in sample_n_keys(word_freqs, n_samples):
        print key


if __name__ == "__main__":
    main()
