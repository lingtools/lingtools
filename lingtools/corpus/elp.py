"""
Classes for representing items in the English Lexicon Project database.

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


import sys
import re
import csv

NULL = "NULL"
MISANALYSIS_MARKER = "--"
ANALYSIS_RE = re.compile(r'^(.+<)*-?(\{.+\})(>.+)*$')
SEP_RE = re.compile(r'[<>{}]+')

_INFLECTIONAL_SUFFIXES = set(('s', 'ed', 'ing'))


class AnalysisParseError(Exception):
    """An analysis string could not be parsed."""
    pass


class Word(object):
    """Representation of data for a word, including frequency and RT data."""
    __slots__ = ("text", "length", "freq_hal", "freq_kf", "freq_sbtlx", "freq_celex",
                 "prefixes", "suffixes", "root", "inflectional", "derivational", "analysis",
                 "nphon", "nsyll", "pron", "roots", "compound", "orig_analysis", "analyzed",
                 "fake")

    def __init__(self, text, length, freq_hal, freq_kf, freq_sbtlx, freq_celex, analysis,
                 nphon, nsyll, pron, fake=False):
        """Set basic information about the word and parse the analysis."""
        self.text = text
        self.length = length
        self.freq_kf = freq_kf
        self.freq_hal = freq_hal
        self.freq_sbtlx = freq_sbtlx
        self.freq_celex = freq_celex
        self.nphon = nphon
        self.nsyll = nsyll
        self.pron = pron
        self.orig_analysis = analysis
        self.fake = fake

        # This may raise a AnalysisParseError, which is passed on to the caller.
        self.prefixes, roots, self.suffixes = (parse_analysis(analysis) if analysis != NULL else
                                               ([], [], []))
        # If there's more than one root, flag it
        self.compound = len(roots) > 1
        self.roots = roots
        if roots:
            self.root = roots[0]
            self.analyzed = True
        else:
            self.root = None
            self.analyzed = False

        # Store the updated analysis
        self.analysis = format_analysis(self.prefixes, self.roots, self.suffixes)

        # Mark inflectional/derivational
        self.inflectional = self.derivational = False
        if self.suffixes:
            if self.suffixes[-1] in _INFLECTIONAL_SUFFIXES:
                self.inflectional = True
                # If it's inflected but also has more than one suffix
                # or has any prefixes, mark derivational.
                if len(self.suffixes) > 1 or self.prefixes:
                    self.derivational = True
            else:
                self.derivational = True
        elif self.prefixes:
            self.derivational = True

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return self.text

    def __repr__(self):
        return "<Word: " + repr(self.text) + ">"

    @property
    def monomorph(self):
        """Return whether the root is monomorphemic."""
        return (self.analyzed and
                not self.compound and not self.prefixes and not self.suffixes)


class ELP(dict):
    """Representation of the ELP database items."""

    def __init__(self, path):
        # Initialize the lexicon
        super(ELP, self).__init__()

        # Open the file and process each line
        try:
            in_file = open(path, 'rU')
            reader = csv.DictReader(in_file)
        except IOError:
            print >> sys.stderr, "Couldn't open input file at", path
            sys.exit(1)

        for row in reader:
            # Parse the word and store it if it was good
            word = parse_word(row)
            if word:
                # Store it
                self[word.text] = word

        # Clean up
        in_file.close()


def parse_word(adict):
    """Parse a word from a dict of the ELP fields for the word."""
    # Clean up the KF frequency, putting zero where needed
    if adict['Freq_KF'] == NULL:
        adict['Freq_KF'] = 0
    # Make unspecified NSyll and NPhon -1
    if adict['NSyll'] == NULL:
        adict['NSyll'] = -1
    if adict['NPhon'] == NULL:
        adict['NPhon'] = -1

    # Catch any parsing errors by returning None
    try:
        # Put in None for the SUBTLEX/CELEX frequency as we can't get it out of the ELP data
        return Word(adict['Word'], adict['Length'], int(adict['Freq_HAL']),
                    int(adict['Freq_KF']), None, None, adict['MorphSp'],
                    int(adict['NPhon']), int(adict['NSyll']), adict['Pron'])
    except AnalysisParseError as err:
        print "ELP entry parsing error:", err
        return None


def parse_analysis(analysis):
    """Parse a morphological analyses into lists of morphs."""
    # Parse out prefixes, roots, and suffixes. Roots will not be None,
    # but prefixes and suffixes might be.
    try:
        prefixes, roots, suffixes = ANALYSIS_RE.match(analysis).groups()
    except AttributeError:
        # No match
        raise AnalysisParseError("Could not match analysis {!r} to regex".format(analysis))

    prefixes = ([item for item in SEP_RE.split(prefixes) if item]
                if prefixes else None)
    suffixes = ([item for item in SEP_RE.split(suffixes) if item]
                if suffixes else None)
    roots = [item.replace(MISANALYSIS_MARKER, '')
             for item in SEP_RE.split(roots) if item]

    return (prefixes, roots, suffixes)


def format_analysis(prefixes, roots, suffixes):
    """Format an analysis in the ELP convention."""
    prefix_str = ("".join("<{}<".format(prefix) for prefix in prefixes) if prefixes else
                  "")
    root_str = "".join("{{{}}}".format(root) for root in roots)
    suffix_str = ("".join(">{}>".format(suffix) for suffix in suffixes) if suffixes else
                  "")
    return "".join((prefix_str, root_str, suffix_str))
