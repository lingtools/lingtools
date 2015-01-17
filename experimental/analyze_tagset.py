#!/usr/bin/env python
"""Analyze the tagset used in a file. The input is assumed to be in the
format word/tag.

This is an extremely old tool which could be reimplemented much more
simply using the lingtools libraries.

"""

# Copyright 2010 Constantine Lignos
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
from collections import defaultdict
from operator import itemgetter
from math import log
import csv

def calc_word_entropies(word_tags):
    """Return a dictionary of words and their entropies given their tags."""
    return dict((word, calc_entropy(tags)) for word, tags in word_tags.items())
    
def calc_entropy(outcomes):
    """Calculate the entropy in bits of a list of outcomes."""
    total_outcomes = 0
    outcome_counts = defaultdict(int)
    
    # Count each outcome
    for outcome in outcomes:
        outcome_counts[outcome] += 1
        total_outcomes += 1 

    # Compute the entropy
    return -sum(count/float(total_outcomes) * 
                   log(count/float(total_outcomes), 2) for
                   outcome, count in outcome_counts.items())


def count_occurrences(outcomes, possible_outcomes):
    """Count the time each possible outcome occurs, returning the count in the same order."""
    return [outcomes.count(outcome) for outcome in possible_outcomes]


def strip_zeroes(seq):
    """Replace every zero in a sequence with the empty string."""
    return [item if item != 0 else '' for item in seq]


def print_ngrams(ngrams):
    """Print ngrams and their counts in descending order."""
    sorted_ngrams = sorted(ngrams.items(), reverse=True, key=itemgetter(1))
    for ngram, count in sorted_ngrams:
        if count == 1:
            break
        print ' '.join(ngram), count
    print


def analyze(in_file, word_file, ngram_file, tag_file):
    """Analyze the tagset of the input file."""

    # Initialize structures    
    word_tags = defaultdict(list) # Key: words, Value: List of associated tags, including duplicates
    word_bigram_tags = defaultdict(list)
    word_trigram_tags = defaultdict(list) 
    tag_words = defaultdict(list) # Key: tag, Value: List of associated words, including duplicates
    tag_counts = defaultdict(int)
    word_counts = defaultdict(int)
    word_bigrams = defaultdict(int)
    tag_bigrams = defaultdict(int)
    word_trigrams = defaultdict(int)
    tag_trigrams = defaultdict(int)

    # Read the input
    last_tag = None
    last_last_tag = None
    last_word = None
    last_last_word = None
    print "Reading input file..."
    for line in in_file:
        # Skip empty lines
        if not line.strip():
            continue
        
        # Split out words and extract tags
        for item in line.strip().split():
            word, tag = item.split('/')
            
            # Count the occurrence
            tag_counts[tag] += 1
            word_counts[word] += 1
            word_tags[word].append(tag)
            tag_words[tag].append(word)

            # Count ngrams
            if last_tag:
                tag_bigrams[(last_tag, tag)] += 1
                if last_last_tag:
                    tag_trigrams[(last_last_tag, last_tag, tag)] += 1
            if last_word:
                word_bigrams[(last_word, word)] += 1
                word_bigram_tags[(last_word, word)].append((last_tag, tag))
                if last_last_word:
                    word_trigrams[(last_last_word, last_word, word)] += 1
                    word_trigram_tags[(last_last_word, last_word, word)].append((last_last_tag, last_tag, tag))

            last_last_tag = last_tag
            last_tag = tag
            last_last_word = last_word
            last_word = word

        # Reset last word and tag so ngrams don't cross utterances. Note that setting this to None
        # also blocks last_last_tag/word from being used
        last_tag = None
        last_word = None

    # Process word/tag relationships
    # Words to the sorted list of their unique tags
    unique_word_tags = dict((word, sorted(set(tags))) for word, tags in word_tags.items())
    unique_word_bigram_tags = dict((ngram, sorted(set(tags))) for ngram, tags in word_bigram_tags.items())
    unique_word_trigram_tags = dict((ngram, sorted(set(tags))) for ngram, tags in word_trigram_tags.items())
    # Number of tags per word/ngram
    word_tag_counts = dict((word, len(tags)) for word, tags in unique_word_tags.items())
    word_bigram_tag_counts = dict((word, len(tags)) for word, tags in unique_word_bigram_tags.items())
    word_trigram_tag_counts = dict((word, len(tags)) for word, tags in unique_word_trigram_tags.items())
    # Tags in alphabetical order
    alpha_sorted_tags = sorted(tag_counts.keys())
    # Entropies
    word_entropies = calc_word_entropies(word_tags)
    bigram_entropies = calc_word_entropies(word_bigram_tags)
    trigram_entropies = calc_word_entropies(word_trigram_tags)
    
    # Now make a CSV for word stats
    print "Writing word file..."
    writer = csv.writer(word_file)
    writer.writerow(['Word', 'Count', 'Entropy', 'Number of Tags', 'Tags'] + alpha_sorted_tags)
    for word in sorted(word_counts.keys(), key=str.lower):
        writer.writerow([word, word_counts[word], word_entropies[word],
                         word_tag_counts[word], ", ".join(unique_word_tags[word])] +
                        strip_zeroes(count_occurrences(word_tags[word], alpha_sorted_tags)))

    # And another for n-gram stats
    print "Writing n-gram file..."
    writer = csv.writer(ngram_file)
    writer.writerow(['NGram', 'Length', 'Count', 'Entropy', 'Number of Tags', 'Tags'])
    for ngram in sorted(word_bigrams.keys()):
        writer.writerow((' '.join(ngram), 2, word_bigrams[ngram], bigram_entropies[ngram],
                         word_bigram_tag_counts[ngram],
                         ", ".join(' '.join(tags) for tags in unique_word_bigram_tags[ngram])))

    for ngram in sorted(word_trigrams.keys()):
        writer.writerow((' '.join(ngram), 3, word_trigrams[ngram], trigram_entropies[ngram],
                         word_trigram_tag_counts[ngram],
                         ", ".join(' '.join(tags) for tags in unique_word_trigram_tags[ngram])))
    
    # Now finally output tag statistics
    print "Writing tag file..."
    writer = csv.writer(tag_file)
    writer.writerow(['Tag(s)', 'Length', 'Count'])
    for tag, count in sorted(tag_counts.items()):
        writer.writerow([tag, 1, count])

    for tag_ngram, count in sorted(tag_bigrams.items()):
        writer.writerow([' '.join(tag_ngram), 2, count])

    for tag_ngram, count in sorted(tag_trigrams.items()):
        writer.writerow([' '.join(tag_ngram), 3, count])
    
    print 'Done'
    

def usage():
    """Print a usage statement."""
    print \
"""Usage: analyze_tagset tagged_file word_stats ngram_stats tag_ngram_stats

The input tagged_file should be in Penn Treebank tag format (word/TAG).
The other three files are output files, and it is recommended that they
be given the extension .csv for easy opening. They are formatted to
be read by Excel."""


def main():
    """Parse arguments and feed the analyzer."""
    
    # Check arguments
    if len(sys.argv) != 5:
        usage()
        sys.exit(2)
    
    # Open the files and pass them to the analyzer
    try:
        tagged_file = open(sys.argv[1], "Ur")
    except IOError:
        print "Could not open input file '%s'" % sys.argv[1]
        sys.exit(1)
    
    try:
        word_file = open(sys.argv[2], "w")
    except IOError:
        print "Could not open word stats output file '%s'" % sys.argv[2]
        sys.exit(1)

    try:
        ngram_file = open(sys.argv[3], "w")
    except IOError:
        print "Could not open ngram stats output file '%s'" % sys.argv[3]
        sys.exit(1)

    try:
        tag_info_file = open(sys.argv[4], "w")
    except IOError:
        print "Could not open tag ngram stats output file '%s'" % sys.argv[4]
        sys.exit(1)

    analyze(tagged_file, word_file, ngram_file, tag_info_file)
    tagged_file.close()
    word_file.close()
    ngram_file.close()
    tag_info_file.close()
    
    
if __name__ == "__main__":
    main()
