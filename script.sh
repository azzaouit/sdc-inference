#!/bin/bash
BIN=$(realpath hpcg-3.1/build/bin/xhpcg)
OUT=~

for ((i = 1; i < 6; i += 1)); do
	G=$((2 ** $i))
	mkdir -p $OUT/grid-$G && cd $OUT/grid-$G
	for ERR_RATE  in $(seq 0.1 0.1 1); do
		for INJ_RATE in $(seq 0.01 0.01 0.1); do
			echo "Grid size = ${G}, Error rate = ${ERR_RATE}, Injection rate = ${INJ_RATE}"
			sudo HPCG_ERR_RATE=$ERR_RATE HPCG_INJ_RATE=$INJ_RATE LD_LIBRARY_PATH=/usr/local/lib $BIN $G $G $G
		done
	done
done
