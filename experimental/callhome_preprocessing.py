#!/usr/bin/env python
"""Simple pre-processing for CALLHOME transcripts."""

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
#pylint: disable-msg=W0402
import string

COMMENT_CHAR = "#"
LINE_EXP = re.compile(r"[\d.]+ [\d.]+ \w\d?: (.+)$")
NON_SPEECH_EXP = re.compile(r"(?:\[{1,2}|\{).+?(?:\]{1,2}|\})")
REMOVE_ANNOTATION_EXP = re.compile(r"&|\(|\)|(?:<\w+)|>|\*|(?://)|(?:\\\\)")
REMOVE_TOKEN_START_CHAR = "%"
REMOVE_TOKEN_STARTEND_CHAR = "-"
PUNC_EXP = re.compile(r"(\.|,|\?|!)")
ENDLINE_EXP = re.compile(r"\.$")

PERIOD_WORDS = set(("Mr.", "Mrs.", "Dr.", "Jr.", "Sr."))


def usage():
    """Print usage instructions."""
    print "Usage: callhome_preprocessing file"


def clean_file(in_path):
    """Clean the file at the given path, outputting to stdout"""
    in_file = open(in_path, "rU")
    
    for line in in_file:
        line = line.rstrip()

        # Skip comments and blank lines
        if not line or line.startswith(COMMENT_CHAR):
            continue
        
        # Extract the main part of the line
        line_match = LINE_EXP.match(line)
        if not line_match:
            print >> sys.stderr, "Couldn't parse line:", repr(line)
            continue
        else:
            utterance = line_match.group(1)
            clean_utt = clean_utterance(utterance)
            if clean_utt and not clean_utt in string.punctuation:
                print clean_utt.strip()
    

def clean_utterance(utterance):
    """Return a cleaned version of an utterance."""
    # Remove non-speech items
    cleaned = NON_SPEECH_EXP.sub("", utterance)
    
    # Remove punctuation that should be deleted
    cleaned = REMOVE_ANNOTATION_EXP.sub("", cleaned)
    
    # Break off punctuation and split
    cleaned = PUNC_EXP.sub(r" \1", cleaned)
    tokens = cleaned.split()
    
    # Clean tokens
    clean_tokens = [clean_token(token) for token in tokens]
    
    # Rejoin tokens, removing empty ones
    cleaned = " ".join([token for token in clean_tokens if token])
    
    # Fix double whitespace
    cleaned = cleaned.replace("\n ", "\n")
    
    return cleaned


def clean_token(token):
    """Return a cleaned version of a token."""
    # Remove disfluency tokens
    if (token.startswith(REMOVE_TOKEN_START_CHAR) or token.startswith(REMOVE_TOKEN_STARTEND_CHAR) or
        token.endswith(REMOVE_TOKEN_STARTEND_CHAR)):
        return None
    
    # Add a newline to endline characters
    if ENDLINE_EXP.match(token) and token not in PERIOD_WORDS:
        token += "\n"
        
    # Lowercase and return
    return token.lower()


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
