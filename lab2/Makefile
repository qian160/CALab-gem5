TESTS_SRC = $(shell ls benchmark | grep \\.c)
TESTS = $(patsubst %.c,%,$(TESTS_SRC))
GEM5 = build/X86/gem5.fast
CONFIG_FILE = configs/example/se.py

COMMON_FLAGS = --l1d_size=64kB --l1i_size=64kB --caches --mem-type=DDR3_1600_8x8
echo:
	echo $(TESTS)

all:
	@mkdir -p result
	@for file in $(TESTS);do\
		mkdir -p result/$$file; \
		$(GEM5) $(CONFIG_FILE) --cmd=benchmark/$$file \
			$(COMMON_FLAGS) \
			--cpu-type=DerivO3CPU --issue_width=8 \
			--sys-clock=1GHz --cpu-clock=1GHz; \
		mkdir -p result/$$file/config1; \
		cp -r -t ./result/$$file/config1 m5out/*; \
		\
		$(GEM5) $(CONFIG_FILE) --cmd=benchmark/$$file \
			$(COMMON_FLAGS) \
			--cpu-type=MinorCPU \
			--sys-clock=1GHz --cpu-clock=1GHz; \
		mkdir -p result/$$file/config2; \
		cp -r -t ./result/$$file/config2 m5out/*; \
		\
		$(GEM5) $(CONFIG_FILE) --cmd=benchmark/$$file \
			$(COMMON_FLAGS) \
			--cpu-type=DerivO3CPU --issue_width=2 \
			--sys-clock=1GHz --cpu-clock=1GHz; \
		mkdir -p result/$$file/config3; \
		cp -r -t ./result/$$file/config3 m5out/*; \
		\
		$(GEM5) $(CONFIG_FILE) --cmd=benchmark/$$file \
			$(COMMON_FLAGS) \
			--cpu-type=DerivO3CPU --issue_width=8 \
			--sys-clock=4GHz --cpu-clock=4GHz; \
		mkdir -p result/$$file/config4; \
		cp -r -t ./result/$$file/config4 m5out/*; \
		\
		$(GEM5) $(CONFIG_FILE) --cmd=benchmark/$$file \
			$(COMMON_FLAGS) \
			--cpu-type=DerivO3CPU --issue_width=8 \
			--sys-clock=1GHz --cpu-clock=1GHz \
			--l2cache --l2_size=256kB; \
		mkdir -p result/$$file/config5; \
		cp -r -t ./result/$$file/config5 m5out/*; \
		\
		$(GEM5) $(CONFIG_FILE) --cmd=benchmark/$$file \
			$(COMMON_FLAGS) \
			--cpu-type=DerivO3CPU --issue_width=8 \
			--sys-clock=1GHz --cpu-clock=1GHz \
			--l2cache --l2_size=2MB; \
		mkdir -p result/$$file/config6; \
		cp -r -t ./result/$$file/config6 m5out/*; \
		\
		$(GEM5) $(CONFIG_FILE) --cmd=benchmark/$$file \
			$(COMMON_FLAGS) \
			--cpu-type=DerivO3CPU --issue_width=8 \
			--sys-clock=1GHz --cpu-clock=1GHz \
			--l2cache --l2_size=16MB; \
		mkdir -p result/$$file/config7; \
		cp -r -t ./result/$$file/config7 m5out/*; \
		\
		echo test $$file finished!; \
	done
