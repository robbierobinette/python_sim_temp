#!/bin/bash
set -x
odir="out"
mkdir -p $odir


radius=6

python ideology_histogram.py $args --xlabel 'Distribution of Member Ideology (Nominate-dim1)' --radius $radius --title "Current Congressional Ideology" --nominate --output $odir/results-current.png $odir/results-current.json &
python ideology_histogram.py $args --xlabel 'Distribution of Member Ideology (Population Sigma)' --radius $radius --title "Simulated Congressional Ideology With Closed Primaries" --output $odir/results-primary.png $odir/results-primary.json &
python ideology_histogram.py $args --xlabel 'Distribution of Member Ideology (Population Sigma)' --radius $radius --title "Simulated Congressional Ideology Under Current Rules" --output $odir/results-custom.png $odir/results-custom.json &
python ideology_histogram.py $args --xlabel 'Distribution of Member Ideology (Population Sigma)' --radius $radius --title "Simulated Congressional Ideology With Condorcet" --output $odir/results-condorcet.png $odir/results-condorcet.json &

wait
