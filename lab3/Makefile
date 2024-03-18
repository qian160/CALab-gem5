GEM5 = build/X86/gem5.opt
CONFIG_FILE = configs/example/se.py
COMMON_FLAGS = --caches --l2cache --cpu-type=DerivO3CPU \
		--l1d_size=4kB --l1i_size=4kB --l2_size=2MB \
		--sys-clock=2GHz --cpu-clock=2GHz --mem-type=DDR3_1600_8x8
policies = RandomRP NMRURP LIPRP

all:
	@mkdir -p task1
	@for policy in $(policies); do\
		for assoc in 4 8 16; do\
			mkdir -p task1/assoc$$assoc;\
			$(GEM5) $(CONFIG_FILE) --cmd=benchmark/mm $(COMMON_FLAGS) \
				--l1d_assoc=$$assoc \
				--l1i_replacement_policy=$$policy \
				--l1d_replacement_policy=$$policy \
				--l2_replacement_policy=$$policy; \
			mkdir task1/assoc$$assoc/$$policy; \
			cp -r -t task1/assoc$$assoc/$$policy m5out/*; \
		done;\
	done;

	@echo 'task1 done'
	@mkdir -p task2
	@mkdir -p task2/config1 task2/config2 task2/config3
	@$(GEM5) $(CONFIG_FILE) --cmd=benchmark/mm \
		$(COMMON_FLAGS) \
		--l1d_assoc=16 \
		--l1d_tag_latency=2 \
		--l1i_tag_latency=2 \
		--l1i_replacement_policy=RandomRP \
		--l1d_replacement_policy=RandomRP \
		--l2_replacement_policy=RandomRP 
	cp -r -t task2/config1 m5out/*

	@$(GEM5) $(CONFIG_FILE) --cmd=benchmark/mm \
		$(COMMON_FLAGS) \
		--l1d_assoc=8 \
		--l1d_tag_latency=10 \
		--l1i_tag_latency=10 \
		--l1i_replacement_policy=NMRURP \
		--l1d_replacement_policy=NMRURP \
		--l2_replacement_policy=NMRURP 
	cp -r -t task2/config2 m5out/*

	@$(GEM5) $(CONFIG_FILE) --cmd=benchmark/mm \
		$(COMMON_FLAGS) \
		--l1d_assoc=8 \
		--l1d_tag_latency=11 \
		--l1i_tag_latency=11 \
		--l1i_replacement_policy=LIPRP \
		--l1d_replacement_policy=LIPRP \
		--l2_replacement_policy=LIPRP 
	cp -r -t task2/config3 m5out/*
