"""
Tools for reading from the SUBTLEX word frequency database.
"""

# Copyright 2011-2013 Constantine Lignos
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
from collections import defaultdict

from lingtools.util import datamanager

DEFAULT_PATH = "SUBTLEXus74286wordstextversion.txt"
SUBTLEX_URL = "http://expsy.ugent.be/subtlexus/SUBTLEXus74286wordstextversion.zip"
UK_BIGRAMS_DEFAULT_PATH = "SUBTLEX-UK_bigrams.csv"
UK_BIGRAMS_URL = "http://crr.ugent.be/papers/SUBTLEX-UK_bigrams.csv"


class SubtlexUSEntry(object):

    """Container class for information about each word as given in SUBTLEX."""
    __slots__ = ("word", "freq_count", "cd_count", "freq_count_low", "cd_count_low", "freq_million",
                 "log10_freq_count", "cd_percent", "log10_cd")

    def __init__(self, word, freq_count, cd_count, freq_count_low, cd_count_low, freq_million,
                 log10_freq_count, cd_percent, log10_cd):
        self.word = word
        self.freq_count = freq_count
        self.cd_count = cd_count
        self.freq_count_low = freq_count_low
        self.cd_count_low = cd_count_low
        self.freq_million = freq_million,
        self.log10_freq_count = log10_freq_count
        self.cd_percent = cd_percent
        self.log10_cd = log10_cd


# TODO: This should eventually be renamed to have "US" in the name.
class SubtlexDict(dict):

    """
    Representation of SUBTLEX US word information.

    This reads information for SUBTLEX US word information from the plain text version of database.
    The data file is available as the "Zipped Text version with all 74,286 words in the corpus" from
    http://subtlexus.lexique.org/. At the time of development, that file was located at the url
    given in SUBTLEX_PATH.

    The information loaded from the database is defined as follows:

    Word. This starts with a capital when the word more often starts with an uppercase letter than
    with a lowercase letter.

    FREQcount. This is the number of times the word appears in the corpus (i.e., on the total of 51
    million words).

    CDcount. This is the number of films in which the word appears (i.e., it has a maximum value of
    8,388).

    FREQlow. This is the number of times the word appears in the corpus starting with a lowercase
    letter. This allows users to further match their stimuli.

    CDlow. This is the number of films in which the word appears starting with a lowercase letter.

    SUBTLWF. This is the word frequency per million words. It is the measure you would preferably
    use in your manuscripts, because it is a standard measure of word frequency independent of the
    corpus size. It is given with two digits precision, in order not to lose precision of the
    frequency counts.

    Lg10WF. This value is based on log10(FREQcount+1) and has four digit precision. Because
    FREQcount is based on 51 million words, the following conversions apply for SUBTLEXUS:
    Lg10WF  SUBTLWF
    1.00    0.2
    2.00    2
    3.00    20
    4.00    200
    5.00    2000

    SUBTLCD indicates in how many percent of the films the word appears. This value has two-digit
    precision in order not to lose information.

    Lg10CD. This value is based on log10(CDcount+1) and has four digit precision. It is the best
    value to use if you want to match words on word frequency. As CDcount is based on 8388 films,
    the following conversions apply:
    Lg10CD  SUBTLCD
    0.95    0.1
    1.93    1
    2.92    10
    3.92    100

    Sample usage, assuming a current SUBTLEX file is available in the working dir,
    which you can ensure by running download():
    >>> SubtlexDict(DEFAULT_PATH)["the"].freq_count
    1501908
    """

    def __init__(self, subtlex_path):
        """Load the SUBTLEX database from the specified file."""
        # Set up dict first
        dict.__init__(self)

        # Fill it in
        try:
            subtlex = open(subtlex_path, 'rU')
        except IOError:
            raise IOError("Could not open SUBTLEX database at %s." % subtlex_path)

        subtlex_reader = csv.DictReader(subtlex, delimiter='\t')
        for row in subtlex_reader:
            self[row['Word']] = \
                SubtlexUSEntry(row['Word'], int(row['FREQcount']), int(row['CDcount']),
                               int(row['FREQlow']), int(row['Cdlow']), float(row['SUBTLWF']),
                               float(row['Lg10WF']), float(row['SUBTLCD']), float(row['Lg10CD']))


class SubtlexUKBigram(object):

    """Representation of a single bigram in Subtlex UK."""
    __slots__ = ("word1", "word2", "freq", "cd", "cdcount")

    def __init__(self, word1, word2, freq, cd, cdcount):
        self.word1 = word1
        self.word2 = word2
        self.freq = freq
        self.cd = cd
        self.cdcount = cdcount


class SubtlexUKBigramDict(dict):

    """Representation of SUBTLEX-UK bigram information."""

    def __init__(self, subtlex_path):
        """Load the SUBTLEX database from the specified file."""
        # Track total counts in each context, which can be useful for
        # excluding sparse data.
        self.context_counts = defaultdict(int)

        # Set up dict
        dict.__init__(self)

        # Fill it in
        try:
            subtlex = open(subtlex_path, 'rU')
        except IOError:
            raise IOError("Could not open SUBTLEX database at %s." % subtlex_path)

        # DictReader would be convenient, but given the size of the
        # file, efficiency is key. Using a standard reader appears to
        # be 30% faster. Fields: spelling, spelling1, freq, cd,
        # cdcount, separator, separatorfreq, separatorcd
        subtlex_reader = csv.reader(subtlex, delimiter='\t')
        # Skip header
        subtlex_reader.next()
        # Read the data
        for word1, word2, freq, cd, cdcount, _, _, _ in subtlex_reader:
            freq = int(freq)
            cd = float(cd)
            cdcount = int(cdcount)
            self[(word1, word2)] = \
                SubtlexUKBigram(word1, word2, freq, cd, cdcount)
            self.context_counts[word1] += freq


def download():
    """Download and unzip a current version of SUBTLEX to the working directory."""
    path = datamanager.download(SUBTLEX_URL)
    datamanager.unzip(path)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
