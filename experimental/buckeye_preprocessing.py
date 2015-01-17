#!/usr/bin/env python
"""Simple pre-processing for Buckeye corpus files."""

# Copyright 2012 Constantine Lignos
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
import string

ACTION_KEEP = "keep" # Keep the text
ACTION_REMOVE = "remove" # Remove any text
ACTION_KILL = "kill" # Remove the entire utterance

TAG_SILENCE = "SIL"
TAG_VOCNOISE = "VOCNOISE"
TAG_INTERVIEWER = "IVER"
TAG_LAUGH = "LAUGH"
TAG_NOISE = "NOISE"
TAG_LENGTHEN = "EXT"
TAG_HESITATION = "HES"
TAG_CUTOFF = "CUTOFF"
TAG_ERROR = "ERROR"
TAG_VOICE = "VOICE"
TAG_UNKNOWN = "UNKNOWN"
TAG_EXCLUDE = "EXCLUDE"

WORD_UNKNOWN = "UNKNOWN"

BAD_TOKENS = set([
                  'um-hum',
                  'mm-hmm',
                  'hm',
                  'mm',
                  'hum-um'
                  ])

ACTION_MAP = {
    TAG_SILENCE: ACTION_REMOVE,
    TAG_VOCNOISE: ACTION_KEEP,
    TAG_INTERVIEWER: ACTION_REMOVE,
    TAG_LAUGH: ACTION_KEEP,
    TAG_NOISE: ACTION_KEEP,
    TAG_LENGTHEN: ACTION_KEEP,
    TAG_HESITATION: ACTION_KEEP,
    TAG_CUTOFF: ACTION_KEEP,
    TAG_ERROR: ACTION_KEEP,
    TAG_VOICE: ACTION_REMOVE,
    TAG_UNKNOWN: ACTION_REMOVE,
    TAG_EXCLUDE: ACTION_KILL
    }

_TAG_PATTERN = re.compile(r"^<(?P<tag>\w+)(?:-(?P<arg1>.+?))?(?:=(?P<arg2>.+?))?>$")
_ARG_TRANS = string.maketrans("_+", "  ")

class TokenizationError(ValueError):
    pass


class TagParsingError(ValueError):
    pass


def _clean_argument(arg):
    """Clean up a tag argument."""
    if arg == WORD_UNKNOWN:
        return ""
    else:
        return arg.translate(_ARG_TRANS).replace("?", "")


def replace_tag_match(match):
    """Return the replacement for a tag match."""
    tag = match.group('tag')
    # Uppercase tags, because sometimes they appear as lowercase
    try:
        action = ACTION_MAP[tag.upper()]
    except KeyError:
        raise TagParsingError("Unknown tag %s in match %r" % (tag, match.groups(0)))
    if action == ACTION_REMOVE:
        return ""
    elif action == ACTION_KILL:
        return None
    else:
        arg1 = match.group('arg1')
        arg2 = match.group('arg2')
        # Get rid of any ? and put in spaces on the way out. If ? was the only thing, this
        # can return empty string which is okay.
        if arg2:
            _clean_argument(arg2)
        elif arg1:
            _clean_argument(arg1)
        else:
            # Nothing to keep
            return ""


def tokenize_line(line):
    """Return tokens from a line."""
    # In general, spaces split tokens. The only reason
    # to have a tokenizer is to get reasonable <> matching
    # for cases where things are screwed up. This implementation is 
    # overkill, but it works.
    tokens = []
    chars = []
    tagdepth = 0
    for char in line:
        # Track parse depth
        if char == "<":
            tagdepth += 1
        elif char == ">":
            tagdepth -= 1
            # If we've closed out a tag, write it out
            if tagdepth == 0:
                chars.append(char)
                tokens.append("".join(chars))
                chars = []
                continue

        # If we're not in a tag, we're just splitting on spaces
        if not tagdepth:
            if char == " ":
                if chars:
                    tokens.append("".join(chars))
                    chars = []
                # Skip adding the char
                continue

        chars.append(char)

    # Add any leftover chars
    if chars:
        tokens.append("".join(chars))

    # Check that the tags closed
    if tagdepth != 0:
        raise TokenizationError("Still at depth %d at end:\n%s" % (tagdepth, line))

    return tokens


def process(infile, outfile):
    """Process Buckeye transcriptions."""
    bad_lines = []
    for linenum, line in enumerate(infile):
        # Tokenize
        line = line.strip()
        try:
            tokens = tokenize_line(line)
        except TokenizationError as error:
            # Lines are 1-indexed, so adjust
            bad_lines.append(linenum + 1)
            continue
        
        # Clean up tags
        clean_tokens = []
        for token in tokens:
            if token in BAD_TOKENS:
                continue

            try:
                clean_token, nsubs = _TAG_PATTERN.subn(replace_tag_match, token)
            except TagParsingError as error:
                print >> sys.stderr, error
                continue

            # Sanity check that all tags matched
            if token.count("<") != nsubs:
                print >> sys.stderr, "Failed to replace all tags: %s" % token
                continue

            if clean_token is None:
                # This line should be killed, escape!
                break
            elif clean_token:
                clean_tokens.append(clean_token)

        if any(clean_tokens):
            print " ".join(clean_tokens)
        
    print >> sys.stderr, "Skipped misformatted lines:", \
        ", ".join(str(linenum) for linenum in bad_lines)


def main():
    process(sys.stdin, sys.stdout)


if __name__ == "__main__":
    main()


