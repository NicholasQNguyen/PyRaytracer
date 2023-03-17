base = python3 rayTracer.py
clean = make clean

run:
	$(base) && \
	$(clean)

runAA2:
	$(base) -s 2 && \
	$(clean)

clean:
	rm -rf __pycache__ && \
	rm -rf modules/__pycache__ && \
	rm -rf modules/raytracing/__pycache__ && \
	rm -rf modules/utils/__pycache__

profile:
	python3 -m cProfile -o output.pstats rayTracer.py -f example.png && \
	gprof2dot --colour-nodes-by-selftime -f pstats output.pstats |     dot -Tpng -o output.png && \
	open output.png && \
	$(clean)

pClean:
	rm output.pstats && \
	rm output.png && \
	rm images/example.png
