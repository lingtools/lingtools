"""
A simple N-gram model class.

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

from itertools import product, izip, islice
from operator import itemgetter

from nltk import ConditionalFreqDist


class Smoothing(object):
    """Define constants for smoothing selection."""
    # The value for none should evaluate to False in boolean context.
    NONE = None
    LAPLACE = "Laplace"
    ELE = "Expected Likelihood Estimate"


class NoSuchContextException(Exception):
    """Raised when information is requested from an unobserved context."""
    pass


class NgramModel(object):
    """A simple N-gram model."""

    def __init__(self, n, training_data=None):
        """Create an n order model using training_data."""
        # Set n and train
        self._order = n
        self._cfd = None
        self.reset()

        if training_data:
            self.update(training_data)

    def reset(self):
        """Clear all trained data structures."""
        self._cfd = ConditionalFreqDist()

    @property
    def order(self):
        """Return the order (1 = unigram, 2 = bigram, etc.)  of the model."""
        return self._order

    def update(self, training_data):
        """Train on iterable training data."""
        if self._order == 1:
            # In the unigram case, the context is always None
            train_iter = product((None,), training_data)
        else:
            # Skip the first n-1 events
            events = islice(training_data, self._order - 1, None)
            # Each iterable in context represents the trailing
            # history. For example, the first context starts from
            # index zero of the data, the second starts from index 1,
            # etc. Note that the number of things in contexts is
            # O(self._order), so making it a list instead of a generator
            # is not a problem.
            contexts = [islice(training_data, offset, None)
                        for offset in range(self._order - 1)]
            # Pair each event with each trailing context, thus for an
            # event with index i ((..., i-2, i-1), i).
            train_iter = izip(izip(*contexts), events)
        # Update on the data
        for context, event in train_iter:
            self._cfd[context].inc(event)

    def prob(self, event, context, smoothing=Smoothing.NONE):
        """Return the probability for an event in the provided context"""
        # Sanitize context since it may accidentally be a list
        if context is not None:
            context = tuple(context)

        # Explicitly test for presence of the context, as it will be
        # automatically created if we try to get it.
        if context not in self._cfd:
            # Unknown contexts are not smoothed. It's pretty hard to
            # figure out how you would smooth them anyway; that's what
            # backoff is for. It's up to the caller to decide what to
            # do in this scenario.
            raise NoSuchContextException

        estimator = self._cfd[context]

        if smoothing:
            if smoothing == Smoothing.LAPLACE:
                add = 1
            elif smoothing == Smoothing.ELE:
                add = 0.5
            else:
                raise ValueError("Uknown smoothing: {}".format(smoothing))
            count = estimator.count(event)
            total_count = estimator.N()
            event_count = estimator.B()
            return (count + add) / (total_count + (event_count * add))
        else:
            return estimator.freq(event)

    def count(self, event, context):
        """Return the count for an event in the provided context."""
        # Sanitize context since it may accidentally be a list
        if context is not None:
            context = tuple(context)
        try:
            estimator = self._cfd[context]
        except KeyError:
            return 0

        return estimator[event]

    def context_count(self, context):
        """Return the total count for a given context."""
        # Sanitize context since it may accidentally be a list
        if context is not None:
            context = tuple(context)
        try:
            estimator = self._cfd[context]
        except KeyError:
            return 0

        return estimator.N()

    def allngrams(self):
        """Return all N-grams observed by the model and their probabilities."""
        ngram_probs = ((event, context, self.prob(event, context))
                       for context, dist in self._cfd.items()
                       for event in dist)
        return sorted(ngram_probs, key=itemgetter(1))
