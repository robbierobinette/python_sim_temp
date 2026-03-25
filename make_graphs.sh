#!/bin/bash
odir="out"
mkdir -p $odir

. .venv/bin/activate

radius=6

python ideology_histogram.py --xlabel 'Distribution of Member Ideology (Nominate-dim1)'    --radius $radius --title "Current Congressional Ideology" --nominate --output $odir/current-ideology.png $odir/results-current.json > $odir/current-hist.out 2>&1 &
python ideology_histogram.py --xlabel 'Distribution of Member Ideology (Population Sigma)' --radius $radius --title "Simulated Congressional Ideology With Closed Primaries" --output $odir/primary-ideology.png $odir/results-primary.json > $odir/primary-hist.out 2>&1&
python ideology_histogram.py --xlabel 'Distribution of Member Ideology (Population Sigma)' --radius $radius --title "Simulated Congressional Ideology Under Current Rules" --output $odir/custom-ideology.png $odir/results-custom.json > $odir/custom-hist.out 2>&1&
python ideology_histogram.py --title-font-size=18 --xlabel 'Distribution of Member Ideology (Population Sigma)' --radius $radius --title "Congressional Ideology With Top-2" --output $odir/top-2-ideology.png $odir/results-top-2.json > $odir/top-2-hist.out 2>&1&
python ideology_histogram.py --title-font-size=18 --xlabel 'Distribution of Member Ideology (Population Sigma)' --radius $radius --title "Congressional Ideology With Top-5 Instant Runoff" --output $odir/irv-ideology.png $odir/results-irv.json > $odir/irv-hist.out 2>&1&
python ideology_histogram.py --xlabel 'Distribution of Member Ideology (Population Sigma)' --radius $radius --title "Simulated Congressional Ideology With Consensus Voting" --output $odir/condorcet-ideology.png $odir/results-condorcet.json > $odir/condorcet-hist.out 2>&1&


python draw_us_map.py --font-size=30 --results=out/results-primary.json --colorization=representation --output $odir/primary-map.png --title "Simulated Representation with Closed Primaries" & > out/$i-map.out 2>&1
python draw_us_map.py --font-size=40 --results=out/results-irv.json --colorization=representation --output $odir/irv-map.png --title "Representation with Top-5 Instant Runoff" & > out/$i-map.out 2>&1
python draw_us_map.py --font-size=30 --results=out/results-condorcet.json --colorization=representation --output $odir/condorcet-map.png --title "Simulated Representation with Consensus Voting" & > out/$i-map.out 2>&1
python draw_us_map.py --font-size=30 --results=out/results-custom.json --colorization=representation --output $odir/custom-map.png --title "Simulated Representation with the Current Rules" & > out/$i-map.out 2>&1
python draw_us_map.py --font-size=40 --results=out/results-top-2.json --colorization=representation --output $odir/top-2-map.png --title "Representation with Top-2" & > out/$i-map.out 2>&1

wait;
open out/*.png
