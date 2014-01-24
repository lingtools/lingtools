"""
Tools for reading from the CELEX lexical database.
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

import sys
import os
import re
from collections import defaultdict

DUTCH = "dutch"
ENGLISH = "english"
GERMAN = "german"
SUPPORTED_LANGS = (ENGLISH, DUTCH)
ROOT_RE = re.compile(r"\(([^()]+)\)\[[^|.]+\]")
USAGE = "Usage: celexreader celex_root lang [infl|deriv|freq]"

# Constants used only by doctests
_TEST_CELEX_PATH = "celex2"
_TEST_LANG = ENGLISH


class CelexDB(object):

    """Representation of the CELEX lexical database for a particular language.

    Sample usage:
    >>> cdb = CelexDB(_TEST_CELEX_PATH, _TEST_LANG)
    >>> cdb.lemma_map['abandon']
    ['abandon', 'abandoning', 'abandoned', 'abandons']
    >>> cdb.root_map['abandon']
    ['abandon', 'abandoning', 'abandonment', 'abandoned', 'abandons']

    """

    def __init__(self, celex_root, lang):
        """Load the lexical database from the specified root and language."""
        if lang not in SUPPORTED_LANGS:
            raise ValueError("Language {!r} is not supported by CelexDB.".format(lang))
        self.lang = lang  # Language being read

        # Core data structures
        self.word_lemmas = defaultdict(set)  # key: word, value: set of its lemma ids
        self.lemma_words = defaultdict(set)  # key: lemma id, value: set of words in the base
        self.lemma_heads = {}  # key: lemma id, value: head word of lemma
        self.root_lemmas = defaultdict(set)  # key: root, value: lemmas that contain this root
        self.lemma_roots = {}  # key: lemma id, value: root of lemma
        self.word_freqs = defaultdict(int)  # key word, value: total frequency

        # Load
        self._load_celex(celex_root)

        # Make more readable data structures
        self.lemma_map = {head: list(self.lemma_words[lemma])
                          for lemma, head in self.lemma_heads.iteritems()}
        self.root_map = {root: list(set.union(*[self.lemma_words[lemma] for lemma in lemmas]))
                         for root, lemmas in self.root_lemmas.iteritems()}

    def _load_celex(self, celex_root):
        """Read in all the word forms in the gold standard and parse each one."""
        # Form the filenames from the language
        pre = self.lang[0]
        mw_filename = os.path.join(celex_root, self.lang, pre + 'mw', pre + 'mw.cd')
        ml_filename = os.path.join(celex_root, self.lang, pre + 'ml', pre + 'ml.cd')

        # First pass for inflectional morphology from morphological words
        for line in open(mw_filename, 'rU'):
            # pylint: disable=W0612
            word, frequency, lemma, features, analysis = self._parse_mw(line.strip())
            self.word_lemmas[word].add(lemma)
            self.lemma_words[lemma].add(word)
            self.word_freqs[word] += frequency

        # Now get lemma information and derivational info
        for line in open(ml_filename, 'rU'):
            lemma, word, roots = self._parse_ml(line.strip())

            # TODO: Decide what to do about compounds. For now they are skipped by this.
            # Skip if there are multiple roots
            if roots and len(roots) > 1:
                continue

            # TODO: Decide what to do about multi-word entries. For now they are skipped by this.
            # Skip if there is a space in the word itself
            if ' ' in word:
                continue

            # Otherwise, there's just one root or none. Extract it if there is one, otherwise
            # call it its own root
            root = roots[0] if roots else word

            # Store this lemma
            self.lemma_heads[lemma] = word
            self.root_lemmas[root].add(lemma)

    def _parse_mw(self, line):
        """Return a word and its analysis from a line of the MW data file"""
        # Parse the line
        # pylint: disable=W0612
        if self.lang == ENGLISH:
            # From the README:
            # The emw.cd file contains the following fields:
            # 1.    IdNum
            # 2.    Word
            # 3.    Cob
            # 4.    IdNumLemma
            # 5.    FlectType
            # 6.    TransInfl
            word_id, word, frequency, lemma, features, analysis = line.split('\\')
        elif self.lang == DUTCH:
            # From the README:
            # The dmw.cd file contains the following fields:
            # 1.   Idnum
            # 2.   Word
            # 3.   Inl
            # 4.   IdNumLemma
            # 5.   FlectType
            word_id, word, frequency, lemma, features = line.split('\\')
            analysis = None

        return (word, int(frequency), lemma, features, analysis)

    def _parse_ml(self, line):
        """Return a word and its analysis from a line of the ML data file"""
        # Parse the line
        fields = line.split('\\')
        if self.lang == ENGLISH:
            # pylint: disable=C0301
            # English sample:
            # 14\abandonment\94\C\\1\N\N\N\N\Y\abandon+ment\2x\SA\N\N\N\#\N\N\SA\((abandon)[V],(ment)[N|V.])[N]\N\N\N
            # From the README:
            # The eml.cd file contains the following fields:
            #    1.     IdNum
            #    2.     Head
            #    3.     Cob
            #    4.     MorphStatus
            #    5.     Lang
            #    6.     MorphCnt
            #    7.     NVAffComp
            #    8.     Der
            #    9.     Comp
            #   10.     DerComp
            #   11.     Def
            #   12.     Imm
            #   13.     ImmSubCat
            #   14.     ImmSA
            #   15.     ImmAllo
            #   16.     ImmSubst
            #   17.     ImmOpac
            #   18.     TransDer
            #   19.     ImmInfix
            #   20.     ImmRevers
            #   21      FlatSA
            #   22.     StrucLab
            #   23.     StrucAllo
            #   24.     StrucSubst
            #   25.     StrucOpac
            lemma = fields[0]
            word = fields[1]
            derivation = fields[21]
        elif self.lang == DUTCH:
            # pylint: disable=C0301
            # Dutch sample:
            # 19\aalbessengelei\7\C\1\Y\Y\Y\aalbes+en+gelei\NxN\N\N\(((aal)[N],(bes)[N])[N],(en)[N|N.N],(gelei)[N])[N]\N\N\N
            # The dml.cd file contains the following fields:
            #   1.     IdNum
            #   2.     Head
            #   3.     Inl
            #   4.     MorphStatus
            #   5.     MorphCnt
            #   6.     DerComp
            #   7.     Comp
            #   8.     Def
            #   9.     Imm
            #   10.    ImmSubCat
            #   11.    ImmAllo
            #   12.    ImmSubst
            #   13.    StrucLab
            #   14.    StruAcAllo
            #   15.    StrucSubst
            #   16.    Sepa
            lemma = fields[0]
            word = fields[1]
            derivation = fields[12]

        # Skip multi-word entries for roots
        roots = self._get_root(derivation) if " " not in word else None
        return (lemma, word, roots)

    def _get_root(self, derivation):
        """Get the root from a representation of a derivation."""
        # Sample derivation: (((ab)[A|.A],((norm)[N],(al)[A|N.])[A])[A],(ity)[N|A.])[N]
        # First, remove the POS tags
        roots = ROOT_RE.findall(derivation)
        return roots


def dump():
    """Dump basic information from the database."""
    celex_root = sys.argv[1]
    lang = sys.argv[2]
    mode = sys.argv[3]

    creader = CelexDB(celex_root, lang)

    if mode == "infl":
        print 'Inflectional word sets:'
        for head, words in sorted(creader.lemma_map.items(), key=lambda x: x[0].lower()):
            print "%s: %s" % (head, ', '.join(words))
    elif mode == "deriv":
        print 'Inflectional/Derivational word sets:'
        for root, words in sorted(creader.root_map.items(), key=lambda x: x[0].lower()):
            print "%s: %s" % (root, ', '.join(words))
    elif mode == "freq":
        sorted_word_freqs = sorted(creader.word_freqs.items(), key=lambda x: x[1], reverse=True)
        maxlen = None
        for word, freq in sorted_word_freqs:
            if not maxlen:
                maxlen = len(str(freq))
            print ("%" + str(maxlen) + "d") % freq, word
    else:
        print >> sys.stderr, "Unknown testing mode:", mode
        sys.exit(64)


if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print >> sys.stderr, USAGE
        sys.exit(64)
    elif len(sys.argv) == 3:
        import doctest
        doctest.testmod()
    else:
        # Dump database
        dump()
