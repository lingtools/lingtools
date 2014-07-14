#!/usr/bin/env python
"""
Output information on prefix cohorts

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
from collections import defaultdict
from itertools import takewhile

from lingtools.corpus import subtlexreader
from lingtools.lex.cohort import prefixes, uniqueness_point, make_prefix_dict
from lingtools.prob.probability import entropy, normalize_counts, surprisal

# All vowels in the converted representation, used to identify onsets.
# These should be checked against your stimuli list; these were
# generated in an ad-hoc fashion and may not be complete.
VOWELS = set([
    "8",
    "@",
    "o",
    "O",
    "Y",
    "W",
    "8",
    "a",
    "A",
    "e",
    "E",
    "i",
    "I",
    "V",
    "u",
    "U",
    "R",
    ])


def _get_initial(phones):
    """Return the first onset or first segment in the nucleus if no onset.

    >>> _get_initial('ab@k@s')
    'a'

    >>> _get_initial('zIGk')
    'z'

    >>> _get_initial('klasp')
    'kl'

    >>> _get_initial('strIG')
    'str'

    """
    onset = ''.join(takewhile(lambda x: x not in VOWELS, phones))
    if onset:
        return onset
    else:
        return phones[0]


def _get_onsetnuc(phones):
    """Return the onset and nucleus of the first syllable.

    >>> _get_onsetnuc('ab@k@s')
    'a'

    >>> _get_onsetnuc('zIGk')
    'zI'

    >>> _get_onsetnuc('klasp')
    'kla'

    >>> _get_onsetnuc('strIG')
    'strI'

    >>> _get_onsetnuc('lY@n')
    'lY'

    >>> _get_onsetnuc('ple')
    'ple'

    >>> _get_onsetnuc('pleR')
    'ple'

    """
    onset = ''.join(takewhile(lambda x: x not in VOWELS, phones))
    try:
        nuc = phones[len(onset)]
    except IndexError:
        raise ValueError("Could not correctly compute onset length in {}.".format(phones))
    return onset + nuc


def _mean(seq):
    """Return the arithmetic mean of a sequence."""
    if not seq:
        raise ValueError("Cannot take mean of empty sequence")
    else:
        return sum(seq) / float(len(seq))


def cohort_info(word_path, freq_path, output_base):
    """Write cohort information."""
    print "Reading frequencies..."
    subtlex = subtlexreader.SubtlexDict(freq_path)
    # The choice between using freq_count (covers more items, but most
    # of the additional ones are proper nouns) versus freq_count_low
    # (higher accuracy frequency estimates) is not
    # obvious. Empirically, using freq_count_low results in a better
    # fit for the one study examined, a semantic priming study. It's
    # also the one more likely to be selected a priori based on its
    # better correlation with behavioral measures found in previous
    # studies.
    word_freqs = {word: subtlex[word].freq_count_low for word in subtlex}

    print "Reading pronunciations..."
    with open(word_path, 'rU') as word_file:
        word_reader = csv.reader(word_file)
        word_prons = {row[0]: row[1] for row in word_reader}

    # Add up frequencies for each pronunciation
    pron_freqs = defaultdict(int)
    nofreq_count = 0
    # Laplace smoothing over word counts
    for word, pron in word_prons.iteritems():
        if word in word_freqs and word_freqs[word]:
            freq = word_freqs[word] + 1
        else:
            freq = 1
            # Note smoothed frequencies
            nofreq_count += 1
        pron_freqs[pron] += freq

    print "{} words did not have frequency information".format(nofreq_count)

    print "Creating prefix tree..."
    prefix_prons = make_prefix_dict(set(word_prons.values()))

    # Compute the number of words and counts within each prefix
    prefix_counts = {}
    prefix_freqs = {}
    for prefix, prons in prefix_prons.iteritems():
        prefix_counts[prefix] = len(prons)
        prefix_freqs[prefix] = [pron_freqs[pron] for pron in prons]

    # Put in a special null prefix for computing surprisal on initial
    # phonemes.
    prefix_counts[""] = len(word_prons)
    prefix_freqs[""] = [pron_freqs[pron] for pron in word_prons.itervalues()]

    # Compute entropy and surprisal for each prefix
    print "Computing entropy..."
    prefix_uniform_entropy = {}
    prefix_freq_entropy = {}
    prefix_uniform_surprisal = {}
    prefix_freq_surprisal = {}
    for prefix in prefix_prons:
        # Make a uniform distribution using a count of 1 for each item
        prefix_uniform_entropy[prefix] = \
            entropy(normalize_counts([1 for _ in range(prefix_counts[prefix])]))
        prefix_freq_entropy[prefix] = \
            entropy(normalize_counts(prefix_freqs[prefix]))
        # Prefix surprisal
        prefix_uniform_surprisal[prefix] = \
            surprisal(len(prefix_freqs[prefix]), len(prefix_freqs[prefix[:-1]]))
        prefix_freq_surprisal[prefix] = \
            surprisal(sum(prefix_freqs[prefix]), sum(prefix_freqs[prefix[:-1]]))

    # Compute entropy and surprisal at each position for each pronunciation
    pron_uniform_entropy = {}
    pron_freq_entropy = {}
    pron_uniform_surprisal = {}
    pron_freq_surprisal = {}
    pron_uniqueness = {}
    for pron in pron_freqs:
        pron_uniform_entropy[pron] = [prefix_uniform_entropy[prefix]
                                      for prefix in prefixes(pron)]
        pron_freq_entropy[pron] = [prefix_freq_entropy[prefix]
                                   for prefix in prefixes(pron)]
        # Because surprisal isn't defined for the first phoneme, put
        # None in its place
        pron_uniform_surprisal[pron] = ([None] +
                                        [prefix_uniform_surprisal[prefix]
                                         for prefix in prefixes(pron)[1:]])
        pron_freq_surprisal[pron] = ([None] +
                                     [prefix_freq_surprisal[prefix]
                                      for prefix in prefixes(pron)[1:]])
        pron_uniqueness[pron] = uniqueness_point([prefix_counts[prefix]
                                                  for prefix in prefixes(pron)])

    # Compute initial and onsetnuc entropy
    pron_initials = {pron: _get_initial(pron) for pron in pron_freqs}
    pron_onsetnucs = {pron: _get_onsetnuc(pron) for pron in pron_freqs}

    # Write out information about each prefix
    print "Writing output..."
    prefix_path = output_base + "_prefix.csv"
    with open(prefix_path, 'wb') as prefix_file:
        writer = csv.writer(prefix_file)
        writer.writerow(['prefix', 'ent.unweight', 'ent.freq', 'sur.unweight',
                         'sur.freq'])
        for prefix in sorted(prefix_freq_entropy):
            writer.writerow([prefix, prefix_uniform_entropy[prefix],
                             prefix_freq_entropy[prefix],
                             prefix_uniform_surprisal[prefix],
                             prefix_freq_surprisal[prefix]])

    # Write out information about each word
    word_path = output_base + "_word.csv"
    with open(word_path, 'wb') as word_file:
        writer = csv.writer(word_file)
        writer.writerow([
            'word', 'freq', 'pron', 'length', 'unique',
            'first', 'initial', 'onsetnuc',
            'ent.mean.uniform', 'ent.mean.freq',
            'ent.min.uniform', 'ent.min.freq',
            'ent.max.uniform', 'ent.max.freq',
            'ent.first.uniform', 'ent.first.freq',
            'ent.initial.uniform', 'ent.initial.freq',
            'ent.onsetnuc.uniform', 'ent.onsetnuc.freq',
            'ent.final.uniform', 'ent.final.freq',
            'sur.mean.uniform', 'sur.mean.freq',
            'sur.min.uniform', 'sur.min.freq',
            'sur.max.uniform', 'sur.max.freq',
            ])
        for word in sorted(word_prons):
            freq = word_freqs[word] if word in word_freqs else 0
            pron = word_prons[word]
            first = pron[0]
            initial = pron_initials[pron]
            onsetnuc = pron_onsetnucs[pron]
            # Entropy
            ent_uniform = [prefix_uniform_entropy[prefix] for prefix in prefixes(pron)]
            ent_freq = [prefix_freq_entropy[prefix] for prefix in prefixes(pron)]
            first_ent_uniform = prefix_uniform_entropy[first]
            first_ent_freq = prefix_freq_entropy[first]
            initial_ent_uniform = prefix_uniform_entropy[initial]
            initial_ent_freq = prefix_freq_entropy[initial]
            onsetnuc_ent_uniform = prefix_uniform_entropy[onsetnuc]
            onsetnuc_ent_freq = prefix_freq_entropy[onsetnuc]
            final_ent_uniform = prefix_uniform_entropy[pron]
            final_ent_freq = prefix_freq_entropy[pron]
            # Surprisal
            sur_uniform = [prefix_uniform_surprisal[prefix] for prefix in prefixes(pron)]
            sur_freq = [prefix_freq_surprisal[prefix] for prefix in prefixes(pron)]

            writer.writerow([
                word.lower(), freq, pron, len(pron),
                # Offset the uniqueness point by one as it's zero-indexed
                pron_uniqueness[pron] + 1,
                first, initial, onsetnuc,
                _mean(ent_uniform), _mean(ent_freq),
                min(ent_uniform), min(ent_freq),
                max(ent_uniform), max(ent_freq),
                first_ent_uniform, first_ent_freq,
                initial_ent_uniform, initial_ent_freq,
                onsetnuc_ent_uniform, onsetnuc_ent_freq,
                final_ent_uniform, final_ent_freq,
                _mean(sur_uniform), _mean(sur_freq),
                min(sur_uniform), min(sur_freq),
                max(sur_uniform), max(sur_freq),
                ])

    # Write out the long-format entropy for each word at each position
    ent_path = output_base + "_phoneme.csv"
    with open(ent_path, 'wb') as ent_file:
        writer = csv.writer(ent_file)
        writer.writerow(['word', 'pron', 'prefix', 'pos', 'ent.unweight',
                         'ent.freq', 'sur.unweight', 'sur.freq'])
        for word in sorted(word_prons):
            pron = word_prons[word]
            for idx, prefix in enumerate(prefixes(pron)):
                # Offset the pos by one as it's zero-indexed
                writer.writerow([
                    word, pron, prefix, idx + 1,
                    prefix_uniform_entropy[prefix],
                    prefix_freq_entropy[prefix],
                    prefix_uniform_surprisal[prefix],
                    prefix_freq_surprisal[prefix],
                ])

    print "Entropy and surprisal information written for {} words".format(len(word_prons))


def main():
    """Parse arguments and call the cohort computer."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('words', help='pronunciation CSV')
    parser.add_argument('freqs', help='SUBTLEX frequency CSV')
    parser.add_argument('output_base', help=' CSV file')
    args = parser.parse_args()
    word_path = args.words
    freq_path = args.freqs
    output_base = args.output_base
    cohort_info(word_path, freq_path, output_base)


if __name__ == "__main__":
    main()
