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
seed=42
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
	candidate_generator="normal-partisan"
	nc=$candidates
	if [[ $i == "condorcet" ]] ; then
		candidate_generator="condorcet"
		nc=5
	fi
	echo "$i $candidate_generator $nc"
	toxic_tests.py --test-type=toxic     --candidate-generator=$candidate_generator --uncertainty $uncertainty --candidates $nc --election-type $i > out/$i-toxic-test.out 2>&1 &
	toxic_tests.py --test-type=non-toxic --candidate-generator=$candidate_generator --uncertainty $uncertainty --candidates $nc --election-type $i > out/$i-non-toxic-test.out 2>&1 &
done

wait

grep -h success out/*toxic*
grep -h 'average voter satisfaction' out/*-sim.out

make_graphs.sh
