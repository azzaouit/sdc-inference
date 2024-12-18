HPCG=hpcg-3.1
HPCG_BIN=$(HPCG)/build/bin/xhpcg
PMU=libpmu

all: pmu hpcg

pmu:
	sudo make CC=g++ -C $(PMU) install
	sudo make -C $(PMU) kernel

hpcg:
	mkdir $(HPCG)/build
	cd $(HPCG)/build && ../configure Linux_Serial && make

clean:
	rm -rf $(HPCG) $(PMU)
