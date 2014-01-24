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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
