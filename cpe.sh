#!/bin/bash
odir="out"
mkdir -p $odir

for e in primary irv condorcet actual; do
	skew=0.0
	candidates=2	
	uncertainty=0.5
	voters=1000
	variance=.2


	echo "skew $skew variance $variance candidates $candidates uncertainty $uncertainty voters $voters" > $odir/parameters
	python main.py \
		--candidate-generator normal-partisan  \
		--election-type $e \
		--output $odir/results-$e.json \
		--seed 42  \
		--nvoters $voters  \
		--uncertainty $uncertainty  \
		--ideology-variance $variance  \
		--condorcet-variance .01 \
		--candidates $candidates  \
		--primary-skew $skew  \
		--plot-dir $odir/$e  > $odir/$e.out 2>&1 &
done
wait

for i in $odir/*.json ; do 
	python ideology_histogram.py --radius 8 --output ${i/json/png} $i&  
done
wait

twin_test.sh
grep succeeded $odir/tt/*.out
