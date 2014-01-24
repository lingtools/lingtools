"""
Tools for reading from the CMU Pronouncing Dictionary.
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

import re
import sys

from lingtools.util import datamanager


DEFAULT_PATH = "cmudict.0.7a"
CMUDICT_URL = "http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict.0.7a"


class CMUDict(dict):

    """A representation of the CMU Pronouncing Dictionary."""

    ALT_RE = re.compile(r".+\(\d+\)$")

    def __init__(self, dict_path):
        dict.__init__(self)
        self._load_pron_dict(dict_path)

    def _load_pron_dict(self, dict_path):
        """Load a dictionary in CMUdict format to a word->pronunciation dictionary.

        Only the first pronunciation is kept for each word. Keys are lowercased.
        Values contain the pronunciation as a list of phonemes. The data and information
        about the phoneme set used are at:
        https://cmusphinx.svn.sourceforge.net/svnroot/cmusphinx/trunk/cmudict/

        Sample usage, assuming a current CMUDict file is available in the working dir,
        which you can ensure by running download():
        >>> CMUDict(DEFAULT_PATH)["constantine"]
        ['K', 'AA1', 'N', 'S', 'T', 'AH0', 'N', 'T', 'IY2', 'N']
        """

        # Read in the dictionary
        try:
            dict_file = open(dict_path, 'rU')
        except IOError:
            raise IOError("The CMUDict file %s could not be found. You can run "
                          "cmudictreader.download() to download a copy of the dictionary." %
                          dict_path)

        for line in dict_file:
            # Skip comments
            if line.startswith(";;;"):
                continue

            # Split the line on double space
            try:
                (word, pron) = line.rstrip().split("  ")
            except ValueError:
                print >> sys.stderr, "Unreadable line in dictionary:", repr(line.rstrip())
                continue

            # If the word is an alternate pron, skip it
            if CMUDict.ALT_RE.match(word):
                continue

            # Reformat
            word = word.lower()
            pron = pron.split()

            # Store the word
            self[word] = pron

        dict_file.close()


def download():
    """Download a current version of CMUDict to the working directory."""
    datamanager.download(CMUDICT_URL)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
