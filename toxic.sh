#!/bin/bash

for e in primary irv condorcet custom ; do
	candidates=2	
	condorcet_variance=.01
	skew=0.0
	toxic_bonus=.25
	toxic_penalty=-1
	uncertainty=0.5
	variance=0.10
	voters=1000

	odir="tt-out/xx"
	mkdir -p $odir

	if [[ $e == "foo-condorcet" ]] ; then 
		candidate_generator="condorcet"
		condorcet_variance=.1
	else
		candidate_generator="normal-partisan"
	
	fi
	echo "$e candidates: $candidate_generator"

	python toxicity_tests.py \
		--toxic-bonus $toxic_bonus \
		--toxic-penalty $toxic_penalty \
		--candidate-generator $candidate_generator  \
		--election-type $e \
		--output $odir/results-$e.json \
		--seed 42  \
		--nvoters $voters  \
		--uncertainty $uncertainty  \
		--ideology-variance $variance  \
		--condorcet-variance $condorcet_variance \
		--candidates $candidates  \
		--primary-skew $skew  \
		--plot-dir $odir/$e  > $odir/$e.out 2>&1 &

done

wait
grep succeeded $odir/*.out

