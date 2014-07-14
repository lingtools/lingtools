#!/bin/sh
echo "Running pylint..."
pylint *.py lingtools --ignore=syllabify.py,textgrid.py
echo "Running flake8..."
flake8 *.py lingtools --exclude=syllabify.py,textgrid.py
nosetests --with-doctest
