#!/bin/bash
odir="out"
mkdir -p $odir

. .venv/bin/activate

python generate_current_results.py --output out/results-current.json > out/current-results.out 2>&1

election_types="primary irv condorcet custom top-2"

candidates=2
uncertainty=0.5
skew=0.0
voters=10000
variance=.2
seed=1
verbose="--verbose"

for e in $election_types; do
	python run_sim.py \
		$verbose \
		--iterations 1\
		--candidate-generator normal-partisan  \
		--election-type $e \
		--output $odir/results-$e.json \
		--seed $seed  \
		--nvoters $voters  \
		--uncertainty $uncertainty  \
		--ideology-variance $variance  \
		--condorcet-variance .05 \
		--candidates $candidates  \
		--primary-skew $skew > $odir/$e-sim.out 2>&1 &
done

for i in $election_types; do
	toxic_tests.py --test-type=toxic     --uncertainty $uncertainty --candidates $candidates --election-type $i > out/$i-toxic-test.out 2>&1 &
	toxic_tests.py --test-type=non-toxic --uncertainty $uncertainty --candidates $candidates --election-type $i > out/$i-non-toxic-test.out 2>&1 &
done

wait

radius=6

python ideology_histogram.py --xlabel 'Distribution of Member Ideology (Nominate-dim1)'    --radius $radius --title "Current Congressional Ideology" --nominate --output $odir/current-ideology.png $odir/results-current.json > $odir/current-hist.out 2>&1 &
python ideology_histogram.py --xlabel 'Distribution of Member Ideology (Population Sigma)' --radius $radius --title "Simulated Congressional Ideology With Closed Primaries" --output $odir/primary-ideology.png $odir/results-primary.json > $odir/primary-hist.out 2>&1&
python ideology_histogram.py --xlabel 'Distribution of Member Ideology (Population Sigma)' --radius $radius --title "Simulated Congressional Ideology Under Current Rules" --output $odir/custom-ideology.png $odir/results-custom.json > $odir/custom-hist.out 2>&1&
python ideology_histogram.py --xlabel 'Distribution of Member Ideology (Population Sigma)' --radius $radius --title "Simulated Congressional Ideology With Top-2" --output $odir/top-2-ideology.png $odir/results-top-2.json > $odir/top-2-hist.out 2>&1&
python ideology_histogram.py --xlabel 'Distribution of Member Ideology (Population Sigma)' --radius $radius --title "Simulated Congressional Ideology With Top-5 Instant Runoff" --output $odir/irv-ideology.png $odir/results-irv.json > $odir/irv-hist.out 2>&1&
python ideology_histogram.py --xlabel 'Distribution of Member Ideology (Population Sigma)' --radius $radius --title "Simulated Congressional Ideology With Condorcet" --output $odir/condorcet-ideology.png $odir/results-condorcet.json > $odir/condorcet-hist.out 2>&1&


for t in $election_types;  do 
	python draw_us_map.py --results=out/results-$t.json --colorization=representation --output $odir/$t-map.png & > out/$i-map.out 2>&1
done

wait
 
grep -h success out/*toxic*
grep -h 'average voter satisfaction' out/*-sim.out
