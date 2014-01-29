#!/usr/bin/env python
"""Download all linked files from a webpage.

This is particularly handy for dowloading data from CHILDES.

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

import sys
import os
import argparse
import errno
import urllib2
from urlparse import urljoin
from HTMLParser import HTMLParser

from lingtools.util import datamanager

DEFAULT_EXTENSION = ".zip"


class LinkDownloader(HTMLParser):
    """A parser that downloads files with the specified exension."""

    def __init__(self, ext):
        self.last_tag = None
        self.files = []
        self.ext = ext
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        self.last_tag = tag

    def handle_endtag(self, tag):
        self.last_tag = None

    def handle_data(self, data):
        if self.last_tag == "a" and data.endswith(self.ext):
            self.files.append(data)

    def download_files(self, url, path):
        """Download all the files of the given extension linked from a URL."""
        listing = urllib2.urlopen(url).read()
        self.feed(listing)
        self._download(url, path)

    def _download(self, base_url, path):
        """Download and unzip all files we found."""
        for afile in self.files:
            file_url = urljoin(base_url, afile)
            file_path = datamanager.download(file_url,
                                             os.path.join(path, afile))
            datamanager.unzip(file_path, path)


def main():
    """Parse arguments and call the extractor."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url', help='url to download zips from')
    parser.add_argument('output', help='output directory to save files to')
    parser.add_argument('-e', '--ext', nargs=1, default=DEFAULT_EXTENSION,
                        help='extension of files to download')
    args = parser.parse_args()

    # Clean up URL if needed
    url = args.url
    if not url.startswith("http://"):
        url = "http://" + url

    # Make output dir if needed
    try:
        os.makedirs(args.output)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(args.output):
            pass
        else:
            print >> sys.stderr, \
                "Error opening output directory {!r}".format(args.output)
            sys.exit(1)

    parser = LinkDownloader(args.ext)
    parser.download_files(url, args.output)


if __name__ == "__main__":
    main()
