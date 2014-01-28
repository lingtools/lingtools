#!/bin/sh -e

# This is an example of how to prepare data for cohort analysis. You
# will want to change the stimuli variable to point to a folder of
# your stimuli, or leave it set to empy if you don't want time-aligned
# stimulus information.
out=output
# You'll need to get the elp word item information and set the path to it here.
elp=elp_words.csv
subtlex=SUBTLEXus74286wordstextversion.txt
stimuli=
sample_rate=300

# Make output directory
mkdir -p $out

echo "Extracting pronunciations..."
./extract_elp_prons.py $elp $out/elp_prons.csv
echo "Writing ELP entropy information..."
./cohort_info.py $out/elp_prons.csv $subtlex $out/elp_ent
if test -n "$stimuli"; then
    echo "Writing aligned entropy information..."
    ./align_cohort.py $stimuli $out/elp_ent_prefix.csv $out/stimuli_ent_short.csv
    ./align_cohort.py $stimuli $out/elp_ent_prefix.csv $out/stimuli_ent_long.csv $sample_rate
    echo "Writing aligned duration..."
    ./extract_aligned_duration.py stimuli $out/stimuli_duration.csv
fi
