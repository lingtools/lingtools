"""
Probability utility methods

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

import math
from collections import defaultdict, Counter

PROB_TOLERANCE = 0.000001


def entropy(probs, base=2):
    """Return the entropy over a sequence of outcome probabilities.

    >>> entropy([1.0])
    0.0
    >>> entropy([.5, .5])
    1.0
    >>> entropy([.5, .5], 2)
    1.0
    >>> entropy([.5, .5], 4)
    0.5
    >>> entropy([.5, .49])
    Traceback (most recent call last):
    ValueError: Sum of probabilities is not 1.0

    """
    if not (1.0 - PROB_TOLERANCE) < sum(probs) <= (1.0 + PROB_TOLERANCE):
        raise ValueError("Sum of probabilities is not 1.0")
    elif len(probs) == 1:
        # Special case to avoid returning -0.0, which is not equal to 0.0
        return 0.0
    else:
        return -sum(prob * math.log(prob, base) for prob in probs)


def surprisal(event_prob, context_prob, base=2):
    """Return the surprisal of an event given its conditioning context.

    >>> surprisal(.5, .5)
    0.0

    >>> surprisal(.25, .5)
    1.0

    >>> surprisal(.25, .5, 4)
    0.5

    >>> surprisal(.75, .5)
    Traceback (most recent call last):
    ValueError: Improper conditional probability (event_prob > context_prob)

    """
    if event_prob == context_prob:
        # Special case to avoid returning -0.0, which is not equal to 0.0
        return 0.0
    elif event_prob > context_prob:
        raise ValueError("Improper conditional probability (event_prob > context_prob)")
    else:
        return -(math.log(event_prob, base) - math.log(context_prob, base))


def normalize_counts(counts):
    """Convert a sequence of counts to probabilities.

    >>> normalize_counts([1.0, 1.0])
    [0.5, 0.5]
    >>> normalize_counts([1.0, 2.0, 1.0])
    [0.25, 0.5, 0.25]

    """
    total = sum(counts)
    return [count / float(total) for count in counts]


class FreqDist(object):

    """A frequency distribution.

    While this could more simply inherit from defaultdict/Counter, the
    underlying implementation is intentionally abstracted to allow for
    more complex behavior in the future.

    >>> f = FreqDist()
    >>> f.freq('a')
    Traceback (most recent call last):
    ValueError: No events counted yet
    >>> f.total_count
    0
    >>> f.total_outcomes
    0
    >>> f.inc('a', 2)
    >>> f.inc('b', 8)
    >>> f.count('a')
    2
    >>> f.count('b')
    8
    >>> f.freq('a')
    0.2
    >>> f.freq('b')
    0.8
    >>> f.total_count
    10
    >>> f.total_outcomes
    2

    """

    def __init__(self):
        self._counts = Counter()
        self._total = 0
        super(FreqDist, self).__init__()

    def inc(self, item, amount=1):
        """Increment the count of an item by the given amount."""
        self._total += amount
        self._counts[item] += amount

    def freq(self, item):
        """Return the probability of an item."""
        if self._total <= 0:
            raise ValueError("No events counted yet")
        return self._counts[item] / float(self._total)

    def count(self, item):
        """Return the count of an item."""
        return self._counts[item]

    @property
    def total_count(self):
        """Return the total number of events observed."""
        return self._total

    @property
    def total_outcomes(self):
        """Return the number of possible outcomes."""
        return len(self._counts)

    def outcomes(self):
        """Return the outcomes of the distribution."""
        return self._counts.keys()

    def __contains__(self, item):
        return self._counts.__contains__(item)


class ConditionalFreqDist(defaultdict):

    """A conditional frequency distribution."""

    def __init__(self):
        super(ConditionalFreqDist, self).__init__(FreqDist)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
