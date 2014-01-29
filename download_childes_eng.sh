#!/bin/bash
OUTPUT=childes_eng_na
URLS=("http://childes.psy.cmu.edu/data/Eng-NA-MOR/" "http://childes.psy.cmu.edu/data/Eng-NA/")

for item in ${URLS[@]}; do
    ./download_linked_files.py $item $OUTPUT
done
