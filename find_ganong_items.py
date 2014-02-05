#!/usr/bin/env python
"""
Search over a lexicon for Ganong effect items.

"""

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
import csv

from lingtools.corpus.cmudictreader import CMUDict
from lingtools.corpus.elp import ELP
from lingtools.corpus.subtlexreader import SubtlexDict
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
    ))

VOWELS = syllabify.vowels


def find_ganong(elp_path, cmudict_path, subtlex_path, max_sylls, out_path,
                pair_word):
    """Find Ganong effect items a dictionary with <= max_sylls syllables."""
    # Open corpora
    elp = ELP(elp_path)
    cmudict = CMUDict(cmudict_path)
    subtlex = SubtlexDict(subtlex_path)

    # Collect all monomorphemic words with few enough syllables and no
    # excluded characters
    words = set(word.text for word in elp.itervalues()
                if (word.nsyll <= max_sylls and word.monomorph and
                    not any(char in BAD_CHARACTERS for char in word.text)))

    # Make sure items can be syllabified and record an authoritative syllable count
    word_sylls = {}
    word_prons = {}
    # Iterate over a copy to allow for modification
    for word in words.copy():
        try:
            pron = cmudict[word]
            sylls = syllabify.syllabify(pron)
        except (KeyError, ValueError):
            # Not in CMUDict or could not be syllabified
            words.remove(word)
            continue
        else:
            if len(sylls) > max_sylls:
                words.remove(word)
            else:
                word_prons[word] = pron
                word_sylls[word] = sylls

    # Add the reverse mapping for voicing pairs
    for key, val in VOICING_PAIRS.items():
        VOICING_PAIRS[val] = key

    # Filter to words that start with the right segment and have a
    # simplex onset
    eligible_words = {word for word, pron in word_prons.iteritems()
                      if (pron[0] in VOICING_PAIRS and
                          remove_stress(pron[1]) in VOWELS)}

    # Set all of prons for checking if a pron is in the lexicon
    all_prons = set(tuple(value) for value in cmudict.itervalues())

    # Find the pairs
    ganong_words = set(word for word in eligible_words
                       if is_ganong_pron(word_prons[word], all_prons,
                                         VOICING_PAIRS, pair_word))

    # Get frequency information
    word_freqs = {}
    for word in ganong_words:
        try:
            word_freqs[word] = subtlex[word].freq_count_low
        except KeyError:
            pass

    # Write the output
    with open(out_path, 'wb') as out_file:
        fields = ['word', 'onset', 'nucleus', 'coda', 'sbtlx.freq_low']
        writer = csv.writer(out_file)
        writer.writerow(fields)
        for word, freq in word_freqs.iteritems():
            # Decompose the first syllable
            onset, nucleus, coda = [''.join(item) for item in word_sylls[word][0]]
            # Strip stress off nucleus
            nucleus = remove_stress(nucleus)
            writer.writerow([word, onset, nucleus, coda, freq])


def _exclude_word(word):
    """Return whether a word should be excluded."""
    return any(char in BAD_CHARACTERS for char in word)


def is_ganong_pron(pron, all_prons, voicing_pairs, pair_word=False):
    """Return whether an item is a Ganong effect item."""
    first = pron[0]
    # Skip things that don't start with the right segment
    if first not in voicing_pairs:
        return False
    # Make the new pronunciation
    new_pron = [voicing_pairs[first]] + pron[1:]
    # Return true if the new pron fits the criteria
    result = tuple(new_pron) not in all_prons
    # Reverse the result if we actually want pairs of words
    return result if not pair_word else not result


def main():
    """Parse arguments and call the extractor."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('elp_path', help='ELP item CSV file')
    parser.add_argument('cmudict_path', help='CMUDict file')
    parser.add_argument('subtlex_path', help='SUBTLEX file')
    parser.add_argument('out_path', help='output CSV file')
    parser.add_argument('-s', '--syll', nargs='?', default=None, type=int,
                        help='maximum number of syllables')
    parser.add_argument('-w', '--word', default=False, action='store_true',
                        help='whether to identify word-word pairs')
    args = parser.parse_args()
    find_ganong(args.elp_path, args.cmudict_path, args.subtlex_path,
                args.syll, args.out_path, args.word)


if __name__ == "__main__":
    main()
