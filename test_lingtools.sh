#!/bin/sh
pylint lingtools
flake8 lingtools
nosetests --with-doctest
