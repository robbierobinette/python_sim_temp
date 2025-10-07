#!/bin/bash
. .venv/bin/activate

mkdir -p out/tt
for i in primary condorcet irv actual; do
	twin_test.py --candidates 2 --election-type $i > out/tt/$i.out 2>&1 &
done
wait
