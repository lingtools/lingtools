#!/usr/bin/env python

"""Installer for LingTools"""

# Copyright 2011-2014 Constantine Lignos
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

from distutils.core import setup

DESCRIPTION = \
    ("LingTools provides tools for working with linguistic data.")


setup(name='lingtools',
      version='0.1',
      description='Tools for working with linguistic data.',
      author='Constantine Lignos',
      author_email='constantine.lignos@gmail.com',
      url='https://github.com/lingtools/lingtools',
      packages=['lingtools'],
      license='Apache',
      platforms='any',
      long_description=DESCRIPTION,
      )
