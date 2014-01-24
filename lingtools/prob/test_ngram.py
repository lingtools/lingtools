#!/usr/bin/env python
"""
Test the ngram module.
"""

# Copyright 2012-2014 Constantine Lignos
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
from collections import Counter

from nltk import FreqDist, ConditionalFreqDist

from lingtools.prob.ngram import NgramModel, NoSuchContextException


TEST_PASSAGE = \
    """The celebration had a long way to go and even in the silent depths of
Multivac's underground chambers, it hung in the air.
If nothing else, there was the mere fact of isolation and silence. For
the first time in a decade, technicians were not scurrying about the
vitals of the giant computer, the soft lights did not wink out their
erratic patterns, the flow of information in and out had halted.
It would not be halted long, of course, for the needs of peace would be
pressing. Yet now, for a day, perhaps for a week, even Multivac might
celebrate the great time, and rest.
Lamar Swift took off the military cap he was wearing and looked down
the long and empty main corridor of the enormous computer. He sat down
rather wearily in one of the technician's swing-stools, and his
uniform, in which he had never been comfortable, took on a heavy and
wrinkled appearance.
He said, "I'll miss it all after a grisly fashion. It's hard to
remember when we weren't at war with Deneb, and it seems against nature
now to be at peace and to look at the stars without anxiety."
The two men with the Executive Director of the Solar Federation were
both younger than Swift. Neither was as gray. Neither looked quite as
tired."""
TEST_TOKENS = [token.lower() for token in
               TEST_PASSAGE.replace("\n", " ").translate(None, '",.').split(" ")]


class TestBasic(unittest.TestCase):
    """Test non-probability functions."""

    def test_order(self):
        """Be able to initialize up to some reasonable N."""
        for order in range(10):
            model = NgramModel(order)
            self.assertEqual(model.order, order)


class TestUnigram(unittest.TestCase):
    """Test unigram models."""

    def setUp(self):
        """Initialize a model with the test data."""
        self.model = NgramModel(1)
        self.model.update(TEST_TOKENS)

    def test_count_counter(self):
        """Counts are indentical to using Counter."""
        counter = Counter(TEST_TOKENS)
        for word_type in set(TEST_TOKENS):
            self.assertEqual(self.model.count(word_type, None),
                             counter[word_type])

    def test_count_freqdist(self):
        """Counts are indentical to using FreqDist."""
        freqdist = FreqDist(TEST_TOKENS)
        for word_type in set(TEST_TOKENS):
            self.assertEqual(self.model.count(word_type, None),
                             freqdist[word_type])

    def test_freq_freqdist(self):
        """Probabilities are indentical to using FreqDist."""
        freqdist = FreqDist(TEST_TOKENS)
        for word_type in set(TEST_TOKENS):
            self.assertEqual(self.model.prob(word_type, None),
                             freqdist.freq(word_type))


class TestNgram(unittest.TestCase):
    """Test bigram and higher order models."""

    def test_bigram(self):
        """Bigram model behaves like a CFD."""
        model = NgramModel(2)
        model.update(TEST_TOKENS)

        # Naive implementation of getting contexts, intentionally
        # different from that used by class.
        bigrams = zip(TEST_TOKENS, TEST_TOKENS[1:])
        cfd = ConditionalFreqDist()
        for context, event in bigrams:
            cfd[context].inc(event)

        for context in set(TEST_TOKENS):
            for word in set(TEST_TOKENS):
                # Skip zero count contexts as they raise exceptions
                if not model.context_count(context):
                    continue
                self.assertEqual(model.prob(word, (context,)),
                                 cfd[context].freq(word))
                self.assertEqual(model.count(word, (context,)),
                                 cfd[context][word])

    def test_unseen_context(self):
        """An unseen context raises an exception."""
        model = NgramModel(2)
        model.update(TEST_TOKENS)
        with self.assertRaises(NoSuchContextException):
            model.prob("said", ("UNSEEN",))

    def test_context_count(self):
        """Context counts for seen contexts are correct."""
        model = NgramModel(2)
        model.update(TEST_TOKENS)
        self.assertEqual(model.context_count(("the",)), 19)
        self.assertEqual(model.context_count(("long",)), 3)
        self.assertEqual(model.context_count(("decade",)), 1)

    # TODO: Add tests for higher-order models


if __name__ == '__main__':
    unittest.main()
