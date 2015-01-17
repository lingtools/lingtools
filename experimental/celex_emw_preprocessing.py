#!/usr/bin/env python
"""Simple pre-processing for CELEX EMW files."""

# Copyright 2011 Constantine Lignos
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
import re

SEGMENTATION_RE = re.compile(r"@(?:-(\w+))?\+(\w+)$")
NULL_ANALYSES = set(("@", "", "IRR"))
CLEANUP_RE = re.compile(r"(\w)(ed|ing|es|est|er)")

def usage():
    """Print usage instructions."""
    print "Usage: celex_emw_preprocessing file"


def decode_analysis(word, analysis):        
    """Interpret the analysis of a word, outputting (stem, suffix) or None"""
    # If it's just "@", skip the match entirely
    if analysis in NULL_ANALYSES:
        # Null analysis
        return (word, '')
    elif " " in analysis or "@+@" in analysis:
        # Compounds or strange possessives, which we don't understand
        return None
    
    seg_match = SEGMENTATION_RE.match(analysis)
    if seg_match:
        # For now, just use the + part and ignore any subtraction
        suffix = seg_match.group(2)
        return (word[:-len(suffix)], suffix) 
    else:
        raise ValueError("Could not decode analysis " + repr(analysis) + " for word " + word)
    

def clean_segmentation((stem, suffix)):
    """Clean up a CELEX-style segmentation by fixing handling of orthographic geminates"""
    cleanup_match = CLEANUP_RE.match(suffix)
    if cleanup_match:
        # Move the last letter of the suffix back onto the stem
        stem += cleanup_match.group(1)
        suffix = suffix[1:]
    
    return (stem, suffix)


def clean_file(in_path):
    """Clean a file and output it to stdout"""
    in_file = open(in_path, "rU")
    words = set()
    
    for line in in_file:
        line = line.rstrip()
        # Break up the line and parse it
        #pylint: disable-msg=W0612
        (word_id, word, frequency, lemma, features, analysis) = line.split('\\')
        
        # Skip repeats or multi-word compounds
        if word in words or ' ' in word:
            continue
        else:
            words.add(word)
        
        segmentation = decode_analysis(word, analysis)
        if segmentation:
            stem, suffix = clean_segmentation(segmentation)
            if suffix:
                print stem + "|" + suffix
            else:
                print stem
    
    in_file.close()
    
    
def main():
    """Parse arguments and call the cleaner."""
    try:
        in_path = sys.argv[1]
    except IndexError:
        usage()
        sys.exit(2)
    
    clean_file(in_path)
    

if __name__ == "__main__":
    main()
