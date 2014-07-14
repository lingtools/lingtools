# -*- coding: utf-8 -*-
# pylint: disable=W1402
"""
Tools for working with ARPABET.

Basic usage:
>>> arpabet_arpaone(['D', 'AO', 'G'])
['d', 'c', 'g']

# dɔg
>>> ipa_arpabet(u'd\u0254g')
['D', 'AO', 'G']
>>> u''.join(arpabet_ipa(['D', 'AO', 'G']))
u'd\u0254g'

# beɪk
>>> ipa_arpabet(u'be\u026ak')
['B', 'EY', 'K']
>>> u''.join(arpabet_ipa(['B', 'EY', 'K']))
u'be\u026ak'

# baɪk
>>> ipa_arpabet(u'ba\u026ak')
['B', 'AY', 'K']
>>> u''.join(arpabet_ipa(['B', 'AY', 'K']))
u'ba\u026ak'

# bæk
>>> ipa_arpabet(u'b\u00e6k')
['B', 'AE', 'K']
>>> ipa_arpabet(u'baek')
['B', 'AE', 'K']

# biːk
>>> ipa_arpabet(u'bi\u02d0k')
['B', 'IY', 'K']
>>> ipa_arpabet(u'bi:k')
['B', 'IY', 'K']
>>> u''.join(arpabet_ipa(['B', 'IY', 'K']))
u'bi\u02d0k'

# Schwa/wedge
# but
>>> ipa_arpabet(u'b\u0259t')
['B', 'AH0', 'T']
>>> u''.join(arpabet_ipa(['B', 'AH0', 'T']))
u'b\u0259t'

# butt
>>> ipa_arpabet(u'b\u028ct')
['B', 'AH1', 'T']
>>> u''.join(arpabet_ipa(['B', 'AH1', 'T']))
u'b\u028ct'

# Internal tests:
# ARPABET to ARPAONE is 1:1
>>> _double_reverse_map(_ARPABET_ARPAONE) == _ARPABET_ARPAONE
True

# Basic phone conversion
>>> _convert_phone('IY', _ARPABET_ARPAONE)
'i'

>>> _convert_phone('IY', _ARPABET_IPA)
u'i\u02d0'

# Cover the right symbols. Only expected difference is around schwa/wedge
>>> sorted(set(_ARPABET_ARPAONE) ^ set(_ARPABET_IPA))
['AH1', 'AH2']

# Check that AH2 is only problem in ELPONE -> ARPABET mapping
>>> set(_double_reverse_map(_ARPABET_ELPONE)) ^ set(_ARPABET_ELPONE)
set(['AH2'])

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

# Map from two character to one character version of ARPABET. This uses the map
# found at http://www.laps.ufpa.br/aldebaro/papers/ak_arpabet01.pdf but reduces
# it to phonemes actually used in CMUDict.

import re

_ARPABET_ARPAONE = \
    {
        'IY': 'i',
        'IH': 'I',
        'EY': 'e',
        'EH': 'E',
        'AE': '@',
        'AA': 'a',
        'AH': 'A',
        'AO': 'c',
        'OW': 'o',
        'UH': 'U',
        'UW': 'u',
        'ER': 'R',
        'AW': 'W',
        'AY': 'Y',
        'OY': 'O',
        'Y': 'y',
        'W': 'w',
        'R': 'r',
        'L': 'l',
        'M': 'm',
        'N': 'n',
        'NG': 'G',
        'P': 'p',
        'T': 't',
        'K': 'k',
        'B': 'b',
        'D': 'd',
        'G': 'g',
        'HH': 'h',
        'F': 'f',
        'TH': 'T',
        'S': 's',
        'SH': 'S',
        'V': 'v',
        'DH': 'D',
        'Z': 'z',
        'ZH': 'Z',
        'CH': 'C',
        'JH': 'J',
    }

_ARPAONE_ARPA = dict((val, key) for key, val in _ARPABET_ARPAONE.iteritems())

_ARPABET_IPA = \
    {
        'AO': u'ɔ',
        'AA': u'ɑ',
        'IY': u'iː',
        'UW': u'u',
        'EH': u'ɛ',
        'IH': u'ɪ',
        'UH': u'ʊ',
        # All stressed (primary or secondary) AH is mapped to wedge.
        'AH2': u'ʌ',
        'AH1': u'ʌ',
        'AH': u'ə',
        'AE': u'æ',
        'EY': u'eɪ',
        'AY': u'aɪ',
        'OW': u'oʊ',
        'AW': u'aʊ',
        'OY': u'ɔɪ',
        'ER': u'ɚ',
        'P': u'p',
        'B': u'b',
        'T': u't',
        'D': u'd',
        'K': u'k',
        'G': u'g',
        'CH': u'tʃ',
        'JH': u'dʒ',
        'F': u'f',
        'V': u'v',
        'TH': u'θ',
        'DH': u'ð',
        'S': u's',
        'Z': u'z',
        'SH': u'ʃ',
        'ZH': u'ʒ',
        'HH': u'h',
        'M': u'm',
        'N': u'n',
        'NG': u'ŋ',
        'R': u'r',
        'Y': u'j',
        'W': u'w',
        'L': u'l',
    }

_IPA_ARPABET = dict((val, key) for key, val in _ARPABET_IPA.iteritems())
# Clean up wedge since both AH1 and AH2 map to it
_IPA_ARPABET[u'ʌ'] = 'AH1'
# Make it clear that schwa is unstressed
_IPA_ARPABET[u'ə'] = 'AH0'

_IPA_REPLACEMENTS = \
    (
        (u'ae', u'æ'),
        (u':', u'ː'),
    )

# TODO: Use these as last resort in IPA lookup
_IPA_REPAIRS = \
    (
        (u'ɑ', u'a'),
        (u'i', u'ɪ'),
    )

# Map between arpabet and the ELP one phone set
_ARPABET_ELPONE = \
    {
        'AO': 'O',
        'AA': 'A',
        'IY': 'i',
        'UW': 'u',
        'EH': 'E',
        'IH': 'I',
        'UH': 'U',
        # All stressed (primary or secondary) AH is mapped to wedge.
        'AH2': 'V',
        'AH1': 'V',
        'AH': '@',
        'AE': 'a',
        'EY': 'e',
        'AY': 'Y',
        'OW': 'o',
        'AW': 'W',
        'OY': '8',
        'ER': 'R',
        'P': 'p',
        'B': 'b',
        'T': 't',
        'D': 'd',
        'K': 'k',
        'G': 'g',
        'CH': 'C',
        'JH': 'J',
        'F': 'f',
        'V': 'v',
        'TH': 'T',
        'DH': 'D',
        'S': 's',
        'Z': 'z',
        'SH': 'S',
        'ZH': 'Z',
        'HH': 'h',
        'M': 'm',
        'N': 'n',
        'NG': 'G',
        'R': 'r',
        'Y': 'j',
        'W': 'w',
        'L': 'l',
    }
_ELPONE_ARPABET = dict((val, key) for key, val in _ARPABET_ELPONE.iteritems())
# Ensure 'V' always maps to AH1 since both AH1 and AH2 map to it
_ELPONE_ARPABET['V'] = 'AH1'

_STRESS_RE = re.compile(r"\d")


def remove_stress(phone):
    """Remove any stress markings from a phone."""
    return _STRESS_RE.sub("", phone)


def remove_stresses(phones):
    """Remove any stress markings from a sequences of phones."""
    return [remove_stress(phone) for phone in phones]


def _convert_phone(phone, mapping, stress_marked=False):
    """Convert a phone using a mapping between old and new forms."""
    clean_phone = (phone if (not stress_marked or phone in mapping) else
                   remove_stress(phone))
    try:
        return mapping[clean_phone]
    except KeyError:
        raise ValueError("Unknown phone: " + repr(phone))


def arpabet_arpaone(phones):
    """Convert a sequence of two char ARPABET phones to one char versions."""
    return [_convert_phone(phone, _ARPABET_ARPAONE, True) for phone in phones]


def arpabet_elpone(phones):
    """Convert a sequence of two char ARPABET phones to ELP one char versions."""
    return [_convert_phone(phone, _ARPABET_ELPONE, True) for phone in phones]


def elpone_arpabet(phones):
    """Convert a sequence of one char ELP phones to ARPABET two char versions."""
    return [_convert_phone(phone, _ELPONE_ARPABET, False) for phone in phones]


def _first_ipa_phone(phones):
    """Return the largest IPA phone from the beginning of sequence."""
    onechar = unicode(phones[0])
    twochar = u''.join(phones[:2])
    if twochar in _IPA_ARPABET:
        phone = twochar
    elif onechar in _IPA_ARPABET:
        phone = onechar
    else:
        raise ValueError("Cannot find IPA phone in {!r} or {!r}"
                         .format(onechar, twochar))
    return phone


def ipa_arpabet(phones):
    """Convert a phone sequence from IPA to ARPABET."""
    # Parse greedily, taking two character sequences if they work
    output = []
    phones = _clean_ipa(phones)
    while phones:
        phone = _first_ipa_phone(phones)
        output.append(_convert_phone(phone, _IPA_ARPABET))
        phones = phones[len(phone):]

    return output


def _clean_ipa(phones):
    """Convert and IPA sequence into the standard form we expect."""
    # Coerce to a unicode string
    phones = u''.join(phones)
    # Perform all replacements
    for old, new in _IPA_REPLACEMENTS:
        # Inefficient, but gets the job done
        phones = phones.replace(old, new)
    return phones


def arpabet_ipa(phones):
    """Convert a phone sequence from two-character ARPABET to IPA."""
    return [_convert_phone(phone, _ARPABET_IPA, True) for phone in phones]


def _double_reverse_map(adict):
    """Map entries through a dictionary twice to test they are 1:1."""
    return {val2: key2 for key2, val2 in
            {val1: key1 for key1, val1 in adict.iteritems()}.iteritems()}


if __name__ == "__main__":
    import doctest
    doctest.testmod()
