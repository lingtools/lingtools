#!/bin/sh
pylint *.py lingtools
flake8 *.py lingtools
nosetests --with-doctest
