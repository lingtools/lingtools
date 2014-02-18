#!/usr/bin/env python
"""Output information about bigrams in SUBTLEX-UK."""

# Copyright 2014 Constantine Lignos
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

from lingtools.corpus.subtlexreader import SubtlexUKBigramDict
from lingtools.prob.probability import ConditionalFreqDist


def bigram_info(subtlex_path, out_path, first_word, second_word):
    """Output information about bigrams."""
    # Check args
    if first_word and second_word:
        print >> sys.stderr, "Specify first or second word, not both."
        sys.exit(1)        

    # Load up bigram data
    print "Reading bigrams..."
    bigrams = SubtlexUKBigramDict(subtlex_path)

    # Compute frequencies
    print "Computing frequencies..."
    freqs = ConditionalFreqDist()
    for (word1, word2), bigram in bigrams.iteritems():
        # We can skip contexts that don't matter if a first word has
        # been specified.
        if first_word and word1 != first_word:
            continue
        freqs[word1].inc(word2, bigram.freq)

    # If a first word was specified, make sure it appears in the data.
    if first_word and first_word not in freqs:
        print >> sys.stderr, "Requested context {!r} does not appear in the data.".format(first_word)
        sys.exit(1)

    # Open output
    print "Writing output..."
    try:
        out_file = open(out_path, 'wb')
    except IOError:
        print >> sys.stderr, "Couldn't open output file at", out_path
        sys.exit(1)

    # Write out header and data
    output_fields = ["word1", "word2", "count", "cond.prob", "context_count"]
    writer = csv.writer(out_file)
    writer.writerow(output_fields)

    # If a single word context is specified, only use that. Otherwise,
    # use all words.
    contexts = [first_word] if first_word else sorted(freqs.keys())

    # Add data for each row
    for context in contexts:
        dist = freqs[context]
        # Restrict to second word if specified, skipping if that word
        # was never observed in this context.
        if second_word:
            if second_word not in dist:
                continue
            else:
                words = [second_word]
        else:
            words = sorted(dist.outcomes())
        context_count = bigrams.context_counts[context]
        # Output all outcomes
        for word in words:
            entry = bigrams[(context, word)]
            writer.writerow([context, word, entry.freq, dist.freq(word), context_count])

    # Clean up
    out_file.close()


def main():
    """Parse arguments and call the adder."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('subtlex_path', help='SUBTLEX file')
    parser.add_argument('out_path', help='output CSV file')
    parser.add_argument('-w1', nargs='?', default=None,
                        metavar='first_word',
                        help='first word of bigram to restrict output to')
    parser.add_argument('-w2', nargs='?', default=None,
                        metavar='second_word',
                        help='second word of bigram to restrict output to')
    args = parser.parse_args()
    bigram_info(args.subtlex_path, args.out_path, args.w1, args.w2)


if __name__ == "__main__":
    main()
