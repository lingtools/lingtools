#!/bin/sh
echo "Running pylint..."
pylint *.py lingtools
echo "Running flake8..."
flake8 *.py lingtools
nosetests --with-doctest
