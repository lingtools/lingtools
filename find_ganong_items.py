#!/usr/bin/env python
"""Search over a lexicon for Ganong effect items."""

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

import argparse

from lingtools.corpus.cmudictreader import CMUDict
from lingtools.phon import syllabify
from lingtools.phon.arpabet import remove_stress

VOICING_PAIRS = {
    'K': 'G',
    'T': 'D',
    'P': 'B',
    }

BAD_CHARACTERS = set((
    "'",
    '-',
    '"',
    '.',
    '(',
    ')',
    '}',
    '{',
    ))

VOWELS = syllabify.vowels


def find_ganong(cmudict_path, max_sylls):
    """Find Ganong effect items a dictionary with <= max_sylls syllables."""
    word_prons = CMUDict(cmudict_path)

    # Add the reverse mapping for voicing pairs
    for key, val in VOICING_PAIRS.items():
        VOICING_PAIRS[val] = key

    # Filter to words that start with the right segment and have a
    # simplex onset
    eligible_word_prons = {word: pron for word, pron in word_prons.iteritems()
                           if (pron[0] in VOICING_PAIRS and
                               remove_stress(pron[1]) in VOWELS)}

    # Count number of syllables in every word, deleting any that
    # cannot be syllabified.
    word_nsylls = {}
    for word, pron in word_prons.items():
        try:
            nsylls = len(syllabify.syllabify(pron))
        except ValueError:
            del word_prons[word]
            continue
        else:
            word_nsylls[word] = nsylls

    # Set all of prons for checking if a pron is in the lexicon
    all_prons = set(tuple(value) for value in word_prons.itervalues())

    # Find the pairs. If max_sylls is None, skip the syllable length check.
    ganong_words = [word for word, pron in word_prons.iteritems()
                    if (word_nsylls[word] <= max_sylls and True and
                        not _exclude_word(word) and
                        is_ganong_pron(pron, all_prons, VOICING_PAIRS))]
                    
    return ganong_words


def _exclude_word(word):
    """Return whether a word should be excluded."""
    return any(char in BAD_CHARACTERS for char in word)


def is_ganong_pron(pron, all_prons, voicing_pairs):
    """Return whether an item is a Ganong effect item."""
    first = pron[0]
    # Skip things that don't start with the right segment
    if first not in voicing_pairs:
        return False
    # Make the new pronunciation
    new_pron = [voicing_pairs[first]] + pron[1:]
    # Return true if the new pron is not a word
    return tuple(new_pron) not in all_prons


def main():
    """Parse arguments and call the extractor."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cmudict', help='input CSV file')
    parser.add_argument('-s', '--syll', nargs='?', default=None, type=int,
                        help='maximum number of syllables')
    args = parser.parse_args()
    items = find_ganong(args.cmudict, args.syll)
    for word in sorted(items):
        print word


if __name__ == "__main__":
    main()
