#!/bin/bash
odir="out"
mkdir -p $odir


python generate_current_results.py --output out/results-current.json

for e in primary irv condorcet custom; do
	skew=0.0
	candidates=3
	uncertainty=0.5
	voters=1000
	variance=.2
	seed=10


	echo "skew $skew variance $variance candidates $candidates uncertainty $uncertainty voters $voters" > $odir/parameters
	python main.py \
		--candidate-generator normal-partisan  \
		--election-type $e \
		--output $odir/results-$e.json \
		--seed $seed  \
		--nvoters $voters  \
		--uncertainty $uncertainty  \
		--ideology-variance $variance  \
		--condorcet-variance .05 \
		--candidates $candidates  \
		--primary-skew $skew  \
		--spread=.2 \
		--plot-dir $odir/$e  > $odir/$e.out 2>&1 &
done
wait

make_plots.sh

twin_test.sh
grep succeeded $odir/tt/*.out
