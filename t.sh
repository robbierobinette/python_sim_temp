#!/bin/bash

for voters in 100 1000 3000 10000 ; do
	for e in primary irv condorcet ; do
		skew=0.25
		variance=0.15
		candidates=3	
		uncertainty=0.5

		odir="out/$voters-$skew-$variance-$candidates-$uncertainty"
		mkdir -p $odir

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

