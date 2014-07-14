#!/usr/bin/env python
"""
Convert a childes CHA filter into a cleaned-up version.

This should really be rewritten to use the XML version of the CHILDES
data instead as it's much easier to work with.

"""

# Copyright 2011-2013 Constantine Lignos
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

FOREIGN_RE = re.compile(r"\[- \w+\]")
BADWORDS_RE = re.compile('xxx|xx|www|yyy|yy')
GUESS_RE = re.compile(r"\[.*\]|<.*>|\S+@\S+|&\S+")
DELETE_CHARS_RE = re.compile(r'[\^0,:;().?!<>\[\]"/]')
SPACE_CHARS_RE = re.compile(r'[_+]')
EXTRA_SPACE_RE = re.compile(r'\s+')
GOOD_RE = re.compile(r"[0-9a-z\-' ]*$")


def clean_file(in_path, out_path, filters, clean, invert_filters):
    """Process a file, keeping only utterances that match the filter and cleaning if selected."""
    print "Reading from {}".format(in_path)
    in_file = open(in_path, 'rU')
    print "Writing to {}".format(out_path)
    out_file = open(out_path, 'w')
    print ("Including only" if not invert_filters else "Excluding"), \
        "speakers:", ", ".join(filters)
    speakers = set()
    n_in = 0
    n_out = 0

    # Sample line: "*CHI:    big drum ."
    # Sample line: "%trn:    qn|more n|cookie ."
    # For some reason, there's garbage preceded by /x15 at the end of the line in newer
    # versions of the CHA files
    pattern = '[*%](\\w+):\\s+([^\x15]+)'
    line_re = re.compile(pattern)
    for line in in_file:
        line = line.rstrip()
        match = line_re.match(line)
        if not match:
            continue
        else:
            speaker = match.group(1)
            # If speaker isn't in all caps, skip
            if not all(char.isupper() for char in speaker):
                continue
            n_in += 1
            # XOR between invert_filters and speaker in filters
            if invert_filters == (speaker in filters):
                continue
            if clean:
                utterance = clean_utterance(match.group(2))
            else:
                utterance = match.group(2)
            if utterance:
                speakers.add(speaker)
                print >> out_file, utterance
                n_out += 1

    print "Speakers in output:", ", ".join(speakers)
    print "Lines in input:", n_in
    print "Lines in output:", n_out


def clean_utterance(utt):
    """Return a cleaned up version of an utterance"""
    # First, force to ascii
    utt_unicode = utt.decode('utf-8')
    utt = utt_unicode.encode('ascii', 'ignore')

    # Toss foreign stuff
    if FOREIGN_RE.match(utt):
        return ""

    utt = BADWORDS_RE.sub("", utt)
    utt = GUESS_RE.sub("", utt)
    utt = SPACE_CHARS_RE.sub(" ", utt)
    utt = DELETE_CHARS_RE.sub("", utt)

    # Delete any extra space
    utt = EXTRA_SPACE_RE.sub(" ", utt)
    utt = utt.lower().strip()

    # Sanity check
    if not GOOD_RE.match(utt):
        print >> sys.stderr, "Unexpected characters in utterance:", repr(utt)
        return ""

    return utt


def usage():
    """Print usage to stderr."""
    print >> sys.stderr, "Usage clean_childes in_file out_file filters clean/raw"


def main():
    """Parse arguments and call the cleaner."""
    try:
        in_path = sys.argv[1]
        out_path = sys.argv[2]
        filter_str = sys.argv[3]
        raw_clean = sys.argv[4]
    except IndexError:
        usage()
        sys.exit(64)

    invert_filters = "^" in filter_str
    filters = set(filter_str.replace('^', '').split(','))
    if raw_clean == "clean":
        clean = True
    else:
        clean = False

    clean_file(in_path, out_path, filters, clean, invert_filters)


if __name__ == "__main__":
    main()
