#!/bin/bash


for variance in .2 .3 .4 ; do
	for e in primary irv condorcet actual; do
		skew=0.0
		candidates=2	
		uncertainty=0.5
		voters=1000

		odir="out/xx3-v$variance"
		mkdir -p $odir

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
done
wait

