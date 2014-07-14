#!/usr/bin/env python
"""Search over a lexicon of pronunciations."""

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
import re

from lingtools.corpus.cmudictreader import CMUDict
from lingtools.phon import syllabify
from lingtools.phon.arpabet import arpabet_arpaone, remove_stress

SYLL_MARKER = "-"


def _convert_prondict(prondict):
    """Convert a pronunciation dictionary to a more searchable format.

    Phonemes are converted to the one character representation and
    periods are placed between syllables.
    """
    # TODO: Figure out a way to do this without removing stress information
    new_prondict = {}
    for word, pron in prondict.iteritems():
        # Syllabify pron
        try:
            syll_pron = [onset + nucleus + coda for onset, nucleus, coda in
                         syllabify.syllabify(pron)]
        except ValueError:
            # Word could not be syllabified
            continue
        # Remove stress in each syllable
        new_sylls = ["".join(arpabet_arpaone([remove_stress(phoneme) for phoneme in syll]))
                     for syll in syll_pron]
        new_pron = SYLL_MARKER + SYLL_MARKER.join(new_sylls) + SYLL_MARKER
        new_prondict[word] = new_pron

    return new_prondict


def _match_pron_re(regex, prondict):
    """Match a regex against a prons and return a generator (word, pron) tuples of matches."""
    return ((word, pron) for word, pron in prondict.iteritems() if regex.search(pron))


def _match_word_re(regex, prondict):
    """Match a regex against a words and return a generator (word, pron) tuples of matches."""
    return ((word, pron) for word, pron in prondict.iteritems() if regex.search(word))


def main():
    """Provide a search interface to the user."""
    # Parse arguments
    try:
        dict_path = sys.argv[1]
        wordlist_path = sys.argv[2] if len(sys.argv) == 3 else None
    except IndexError:
        print >> sys.stderr, "Usage: search_lex dictionary [filter_wordlist]"
        sys.exit(64)

    # Load lexicon and convert it to the format we need
    print "Loading dictionary..."
    prondict = _convert_prondict(CMUDict(dict_path))

    if wordlist_path:
        print "Loading filter wordlist..."
        filter_words = set(line.strip().split()[1]
                           for line in open(wordlist_path, 'U'))
    else:
        filter_words = None

    # Take interactive queries
    print "Enter a regular expression to match. Enter Ctrl+C to exit."
    while True:
        try:
            query = raw_input("> ")
        except KeyboardInterrupt:
            break

        # Ignore blank queries
        if not query:
            continue

        # Compile into a regex and match
        results = list(_match_word_re(re.compile(query[1:]), prondict) if query.startswith("?") else
                       _match_pron_re(re.compile(query), prondict))
        for word, pron in sorted(results):
            # Skip words not in filter
            if filter_words and word not in filter_words:
                continue
            print '{}: {}'.format(word, pron)
        if not results:
            print "No matches found."


if __name__ == "__main__":
    main()
