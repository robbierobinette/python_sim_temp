#!/bin/bash

for adjust in none dominant both ; do 
	for e in primary irv condorcet ; do
		skew=0.25
		variance=0.15
		candidates=2	
		uncertainty=0.5
		voters=10000

		odir="out/$voters-$skew-$variance-$candidates-$uncertainty-$adjust"
		mkdir -p $odir

		python main.py \
			--candidate-generator normal-partisan  \
			--election-type $e \
			--output $odir/results-$e.json \
			--seed 42  \
			--nvoters $voters  \
			--uncertainty $uncertainty  \
			--adjust-for-centrist $adjust \
			--ideology-variance $variance  \
			--condorcet-variance .01 \
			--candidates $candidates  \
			--primary-skew $skew  \
			--plot-dir $odir/$e  > $odir/$e.out 2>&1 &

	done
done

wait

