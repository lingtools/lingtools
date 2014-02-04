#!/usr/bin/env python

"""Extract the pronunciations from the aligned portion of a directory of texgrids."""

# Copyright 2014 Constantine Lignos
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

import os
import csv
import argparse

from lingtools.phon.textgrid import TextGrid
from align_cohort import phoneme_tier, textgrid_files
from extract_elp_prons import replace_phons


def align_prons(input_dir, output_path):
    """Output info for each aligned item at the given rate."""
    # Words to their prons
    word_prons = {}

    # Read the textgrids
    for textgrid_path in textgrid_files(input_dir):
        textgrid = TextGrid(textgrid_path)
        textgrid.read(textgrid_path)
        phon_tier = phoneme_tier(textgrid)
        if not phon_tier:
            print "Could not read phoneme tier, skipping {}".format(
                textgrid_path)
            continue
        word = os.path.splitext(os.path.basename(textgrid_path))[0]
        word_prons[word] = "".join(replace_phons(interval.mark) for interval in phon_tier)

    # Write output
    with open(output_path, 'wb') as output_file:
        writer = csv.writer(output_file)
        for word, pron in sorted(word_prons.items()):
            writer.writerow([word, pron])


def main():
    """Parse arguments and call the extractor."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_dir', help='directory containing TextGrid files')
    parser.add_argument('output', help='output CSV file')
    args = parser.parse_args()
    align_prons(args.input_dir, args.output)


if __name__ == "__main__":
    main()
