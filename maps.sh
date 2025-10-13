#!/bin/bash

out=maps
mkdir -p $out

for t in current custom primary irv condorcet ; do 
	python draw_us_map.py --results=out/results-$t.json --colorization=representation --output $out/$t-representation.png &
done

wait
open $out/*-representation.png
