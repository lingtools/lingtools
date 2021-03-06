#!/usr/bin/env python
"""
Extract pronunciations from the ELP items.

Outputs a CSV with the orthographic and phonological form on each
line. The phonological form is stripped of syllabification and stress
markers.

"""

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

import argparse

from lingtools.corpus.elp import ELP, NULL

# " is primary stress, % is secondary, . is syllable boundary
DELETION_CHARS = '"%.'
# These represent a reasonable attempt to map the phonemes to
# one-character versions. The distinction between @` and 3` is
# removed; it is not present in most standard phone sets. Flap (4) is
# left alone as it cannot be mapped back to its underlying form.
PHON_REPLACEMENTS = (
    # R-colored schwa
    ("@`", "R"),
    ("3`", "R"),
    # In the ELP it is always `, but some hand output uses '
    ("3'", "R"),
    ("@'", "R"),
    # Syllabic l
    ("l=", "L"),
    # Move engma to G to leave N for syllabic n.
    ("N", "G"),
    # Syllabic n. Note that N is engma in the original.
    ("n=", "N"),
    # Syllabic m
    ("m=", "M"),
    # dZ to J (like JH in Arpabet)
    ("dZ", "J"),
    # tS to C (like CH in Arpabet)
    ("tS", "C"),
    # aI to Y (like AY in Arpabet)
    ("aI", "Y"),
    # aU to W (like AW in Arpabet)
    ("aU", "W"),
    # OI to 8 (cannot use O like OY in Arpabet, as O is in use)
    ("OI", "8"),
)


def replace_phons(pron):
    """Replace phonemes using the PHON_REPLACEMENTS table."""
    for replacement in PHON_REPLACEMENTS:
        pron = pron.replace(*replacement)
    return pron


def extract(input_path, output_path, mono_only, cmudict_format, target_sylls):
    """Extract words from the input path and write them to the output."""
    with open(output_path, 'wb') as output_file:
        elp = ELP(input_path)

        # Sort by lowercase version of entry
        words = sorted(elp.keys(), key=lambda s: s.lower())

        count = 0
        for word in words:
            entry = elp[word]
            # Extract orthography and pron
            pron = entry.pron
            nsyll = entry.nsyll
            # Match syllable numbers if specified
            if target_sylls is not None and nsyll != target_sylls:
                continue

            # Skip non-monomorphs if specified
            if mono_only and not entry.monomorph:
                continue

            # Skip NULL prons, get the length if there is a pron.
            if pron == NULL:
                continue
            else:
                n_phon = entry.nphon

            # Perform phoneme replacement on the pron
            pron = replace_phons(pron)

            # Remove stress/syllable markers
            pron = pron.translate(None, DELETION_CHARS)

            # Check that length matches
            if len(pron) != n_phon:
                print "Bad pronunciation for {!r}:".format(word)
                print "Pron. {!r} of length {}, expected {}.".format(
                    pron, len(pron), n_phon)
                continue

            out_line = ("{},{}".format(word, pron) if not cmudict_format else
                        "{}  {}".format(word.upper(), " ".join(pron)))
            print >> output_file, out_line
            count += 1

    print "{} pronunciations written to {}".format(count, output_path)


def main():
    """Parse arguments and call the extractor."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='input CSV file')
    parser.add_argument('output', help='output CSV file')
    parser.add_argument('-m', '--mono', action='store_true',
                        help='output only monomorphemic items')
    parser.add_argument('-s', '--sylls', nargs='?', type=int, metavar='n',
                        help='output only items with n syllables')
    parser.add_argument('-c', '--cmudict', action='store_true',
                        help='output in CMUDict format')
    args = parser.parse_args()
    extract(args.input, args.output, args.mono, args.cmudict, args.sylls)


if __name__ == "__main__":
    main()
