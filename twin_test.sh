#!/bin/bash
. .venv/bin/activate

uncertainty=0.5
candidates=2

for i in primary condorcet irv custom; do
	mkdir -p out/tt
	twin_test.py --uncertainty $uncertainty --candidates $candidates --election-type $i > out/tt/$i-$candidates-$uncertainty.out 2>&1 &
done

wait

