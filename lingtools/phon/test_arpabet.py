"""
Test of arpabet conversion.

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

import unittest

from lingtools.corpus.cmudictreader import DEFAULT_PATH, CMUDict
from lingtools.phon import arpabet


class TestArpabet(unittest.TestCase):
    """Test ARPABET conversions."""

    def setUp(self):  # pylint: disable=C0103
        self.cmudict = CMUDict(DEFAULT_PATH)

    def test_arpaone(self):
        """Test conversion of pronunciations to one character ARPABET."""
        # We want to convert every entry without an exception
        for pron in self.cmudict.values():
            arpabet.arpabet_arpaone(pron)

    def test_ipa(self):
        """Test conversion of pronunciations to IPA."""
        # We want to convert every entry without an exception
        for pron in self.cmudict.values():
            arpabet.arpabet_ipa(pron)


if __name__ == '__main__':
    unittest.main()
