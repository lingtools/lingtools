"""
Functions for managing data.
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

import urllib2
import posixpath
import zipfile


def download(url, path=None):
    """Download a url, save under the same filename or the specified path, and return the path."""
    print "Downloading %s..." % url
    try:
        url_file = urllib2.urlopen(url)
    except urllib2.HTTPError:
        raise IOError("Couldn't open URL %s." % repr(url))

    # Use the provided path, or default to the basename
    filename = path if path else posixpath.basename(url)
    try:
        local_file = open(filename, 'wb')
        local_file.write(url_file.read())
        local_file.close()
    except IOError:
        raise IOError("Couldn't write filename %s." % repr(filename))

    return filename


def unzip(filepath, destpath='.'):
    """Unzip a file."""
    print "Unzipping %s..." % repr(filepath)
    try:
        zfile = zipfile.ZipFile(filepath, 'r')
    except (IOError, zipfile.BadZipfile):
        raise IOError("The zip file %s could not be opened." % repr(filepath))

    zfile.extractall(destpath)
