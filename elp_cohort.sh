#!/bin/bash -eu

# This is an example of how to prepare data for cohort analysis. You
# will want to change the stimuli variable to point to a folder of
# your stimuli or set to empty if you don't want time-aligned
# stimulus information.
out=output
# You'll need to get the elp word item information and set the path to it here.
elp=elp_words.csv
# Set to 1 if you want to add stimuli prons to the lexicon
add_stim_prons=0

subtlex=SUBTLEXus74286wordstextversion.txt
stimuli=stimuli
sample_rate=200

# Make output directory
mkdir -p $out

echo "Extracting pronunciations..."
# You can add he -m flag to restrict the lexicon to monomorphs, which is a pretty
# loose definition in the ELP.
./extract_elp_prons.py $elp $out/elp_prons.csv
# If there are stimuli not in your dictionary add their pronunciations to the list. This
# will add any non-words and allow overriding the ELP pronunciations
# for these items if needed.
if [[ add_stim_prons -eq 1  && -d "$stimuli" ]]; then
    ./extract_aligned_prons.py stimuli $out/stimuli_prons.csv
    ./combine_csvs.py concat $out/elp_prons.csv $out/stimuli_prons.csv $out/all_prons.csv 1
else
    cp $out/elp_prons.csv $out/all_prons.csv
fi

echo "Writing ELP entropy information..."
./cohort_info.py $out/all_prons.csv $subtlex $out/elp_ent
if [[ -d "$stimuli" ]]; then
    echo "Writing aligned entropy information..."
    ./align_cohort.py $stimuli $out/elp_ent_prefix.csv $out/stimuli_ent_short.csv
    ./align_cohort.py $stimuli $out/elp_ent_prefix.csv $out/stimuli_ent_long.csv $sample_rate
    echo "Writing aligned duration..."
    ./extract_aligned_duration.py stimuli $out/stimuli_duration.csv
fi
