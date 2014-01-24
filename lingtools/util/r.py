"""
R interface utility methods

"""

# Copyright 2013-2014 Constantine Lignos
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

NA = "NA"


def na_none(value):
    """Return 'NA' if a value is None, or the value otherwise.

    >>> na_none(None)
    'NA'
    >>> na_none(1)
    1
    >>> na_none(1.0)
    1.0
    >>> na_none('foo')
    'foo'
    >>> na_none('NA')
    'NA'

    """
    return value if value is not None else NA


def na_null(value):
    """Return 'NA' if a value is 'NULL', or the value otherwise.

    >>> na_null('NULL')
    'NA'
    >>> na_null(1)
    1
    >>> na_null(1.0)
    1.0
    >>> na_null('foo')
    'foo'
    >>> na_null('NA')
    'NA'

    """

    return value if value != "NULL" else NA


def convert_r_bool(boolean):
    """Convert a boolean value to the string format required by R and None to NA.

    >>> convert_r_bool(True)
    'TRUE'
    >>> convert_r_bool(False)
    'FALSE'
    >>> convert_r_bool(None)
    'NA'
    >>> convert_r_bool('foo')
    Traceback (most recent call last):
        ...
    ValueError: invalid boolean: 'foo'

    """
    if boolean is None:
        return na_none(boolean)
    else:
        # Strict type check as we are relying on bool's __str__
        if type(boolean) != bool:
            raise ValueError("invalid boolean: %s" % repr(boolean))
        else:
            return str(boolean).upper()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
