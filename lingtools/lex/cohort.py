"""
Compute information for lexical competitors.
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

from collections import defaultdict


def prefixes(word):
    """Return all prefixes of a word, including the word itself.
    >> prefixes('cat')
    ['c', 'ca', 'cat']
    >> prefixes('a')
    ['a']
    >> prefixes('')
    []

    """
    return [word[:idx] for idx in range(1, len(word) + 1)]


def make_prefix_dict(words):
    """Return a dictionary of prefix characters to the words they begin.

    >>> words = ("cat", "cats", "in", "into")
    >>> sorted(make_prefix_dict(words).items())  # doctest: +NORMALIZE_WHITESPACE
    [('c', ['cat', 'cats']), ('ca', ['cat', 'cats']),
    ('cat', ['cat', 'cats']), ('cats', ['cats']), ('i', ['in', 'into']),
    ('in', ['in', 'into']), ('int', ['into']), ('into', ['into'])]

    """
    prefix_dict = defaultdict(list)
    for word in words:
        for prefix in prefixes(word):
            prefix_dict[prefix].append(word)
    return prefix_dict


def uniqueness_point(prefix_counts):
    """Return the uniqueness point from a sequence of word counts at each point.

    The uniqueness point is the first index that the number of words
    with that prefix is one or the last index if there is no such
    index. -1 is returned if the input is empty.

    >>> uniqueness_point([5, 4, 3, 2, 1])
    4
    >>> uniqueness_point([1])
    0
    >>> uniqueness_point([1, 1, 1, 1, 1])
    0
    >>> uniqueness_point([2, 1])
    1
    >>> uniqueness_point([2, 2])
    1
    >>> uniqueness_point([2, 2, 2])
    2
    >>> uniqueness_point([])
    -1

    """
    try:
        return prefix_counts.index(1)
    except ValueError:
        return len(prefix_counts) - 1


if __name__ == "__main__":
    import doctest
    doctest.testmod()
