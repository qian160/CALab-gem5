## 前言
官方教程后面部分感觉写的有些太复杂了，而且讲解也不是很好。仅做实验来说的话好像只看[这一部分](https://www.gem5.org/documentation/learning_gem5/part2/helloobject/)，了解**修改源码所需的流程**就足够了。

关于对NMRU策略的介绍，我复制了网上的一段话：

## What’s NMRU policy ?

The NMRU policy is just slightly different from the LRU (Least Recently Used) policy. In fact, you can complete this task with only a few line changes on the original LRU source code in gem5.

Just as you learned in class, the LRU policy uses a queue to track the usage of cache block by moving the last accessed block to the head of the queue. When a miss happens and a replacement must be done, the last block in the queue will be dropped to accommodate the newly accessed block.

The NMRU differs from LRU only in the choice of the block to be replaced. In NMRU, instead of always dropping the last block in the queue, we randomly choose a block after the first one in the queue. That is, we want to keep the most recently used block.

See, very simple, right?

## 配置步骤

进入/src/mem/cache/replacement_policies/，然后
```
cp lru_rp.cc nmru_rp.cc
cp lru_rp.hh nmru_rp.hh
```
lru和nmru策略具有较大的相似性，所以之后的修改可以直接基于lru，改的部分也不是很多。之后的操作都是在这个目录下进行。

### nmru_rp.hh的修改

```
%s/LRU/NMRU/g
```
就是把名字改了一下。

### nmru_rp.cc的修改
首先也要改名字。然找到里面的于getVictim函数，我把它改成了：
```
ReplaceableEntry*
NMRU::getVictim(const ReplacementCandidates& candidates) const
{
	// There must be at least one replacement candidate
	assert(candidates.size() > 0);

	uint64_t mru_idx = 0, i = 0;
	// Visit all candidates to find MRU first
	ReplaceableEntry* mru = candidates[0];
	for (const auto& candidate : candidates) {
		// Update victim entry if necessary
		if (std::static_pointer_cast<NMRUReplData>(
				candidate->replacementData)->lastTouchTick >
				std::static_pointer_cast<NMRUReplData>(
					mru->replacementData)->lastTouchTick) {
			mru = candidate;
			mru_idx = i;
		}
		i++;
	}
	
	uint64_t idx;
	do {
		idx = random_mt.random<unsigned>(0, candidates.size() - 1);
	} while(idx == mru_idx);

	return candidates[idx];
}
```
因为用到了random_mt.random，头文件部分还需要：
```
#include "base/random.hh"
```
具体用法可以参考random_rp.cc

我的处理方法是先找出上次用（时间戳最大）的cache块MRU，标记索引值mru_idx。然后随便产生一个和他不同的随机数，对应的块就作为被淘汰的块

### 编辑`ReplacementPolicies.py`，添加：

```
class NMRURP(BaseReplacementPolicy):
    type = 'NMRURP'
    cxx_class = 'gem5::replacement_policy::NMRU'
    cxx_header = "mem/cache/replacement_policies/nmru_rp.hh"
```

### 编辑SConscript
向scons编译系统注册我们新添加的文件。把SConscript修改为：（改动了两个地方）
```
Import('*')

SimObject('ReplacementPolicies.py', sim_objects=[
    'BaseReplacementPolicy', 'DuelingRP', 'FIFORP', 'SecondChanceRP',
    'LFURP', 'LRURP', 'BIPRP', 'MRURP', 'RandomRP', 'BRRIPRP', 'SHiPRP',
    'SHiPMemRP', 'SHiPPCRP', 'TreePLRURP', 'WeightedLRURP', 'NMRURP'])	#1

Source('bip_rp.cc')
Source('brrip_rp.cc')
Source('dueling_rp.cc')
Source('fifo_rp.cc')
Source('lfu_rp.cc')
Source('lru_rp.cc')
Source('mru_rp.cc')
Source('random_rp.cc')
Source('second_chance_rp.cc')
Source('ship_rp.cc')
Source('tree_plru_rp.cc')
Source('weighted_lru_rp.cc')

Source('nmru_rp.cc')	#2
```
整个操作过程中注意不要有拼写错误，nmru这个词我一开始就拼错了，之后才发现的。

做完这些步骤后就可以重新编译了。

## 使配置生效

### 修改configs/common/Options.py

新增cache替换策略和tag latency（后面的题目要用到）的解析
我是在addNoISAOptions函数的最后添加了以下代码：
```
# Add common options that assume a non-NULL ISA.
    parser.add_argument("--l1i_tag_latency", type=int, default=2)
    parser.add_argument("--l1d_tag_latency", type=int, default=2)
    parser.add_argument("--l2_tag_latency", type=int, default=20)
    parser.add_argument("--l1i_replacement_policy", type=str, default="LRURP",
                        choices=ObjectList.rp_list.get_names())
    parser.add_argument("--l1d_replacement_policy", type=str, default="LRURP",
                        choices=ObjectList.rp_list.get_names())
    parser.add_argument("--l2_replacement_policy", type=str, default="LRURP",
                        choices=ObjectList.rp_list.get_names())

```

### 修改configs/common/CacheConfig.py

在_get_cache_opts函数的最后添加了：

```
    latency_attr = '{}_tag_latency'.format(level)
    if hasattr(options, latency_attr):
        opts['tag_latency'] = getattr(options, latency_attr)

    rp_attr = '{}_replacement_policy'.format(level)
    if hasattr(options, rp_attr):
        if level == "l1d":
            opts['replacement_policy'] = ObjectList.rp_list.get(options.l1d_replacement_policy)()
        if level == "l1i":
            opts['replacement_policy'] = ObjectList.rp_list.get(options.l1i_replacement_policy)()
        if level == "l2":
            opts['replacement_policy'] = ObjectList.rp_list.get(options.l2_replacement_policy)()

```

初始化l1和l2cache的时候都会调用这个函数，所以我就直接在这里做解析了。替换策略部分的代码我感觉写的不是很好，但也不知道怎么改，现在这个将就这能用。

完成这些后，应该可以通过:
```
./build/X86/gem5.opt configs/example/se.py --cmd=tests/test-progs/hello/bin/x86/linux/hello --caches --l2cache --l1d_replacement_policy=MRURP --l1i_replacement_policy=NMRURP --l2_replacement_policy=RandomRP --l2_tag_latency=114514
```
这样的方式来运行程序了。

然后打开m5out/config.ini，去里面搜索关键词RP和114514，可以验证我们的配置策略是否生效。

## 性能测试

### 设计基于乱序 O3CPU 处理器的 cache
使用实验二的测试程序，`mm.c`。基本参数假设：使用O3CPU，L1D、L1I大小为64kB，L2为2MB。系统频率和CPU频率2GHz，issuewidth = 8。
1.  L1D和L2的替换策略一致，从三种缓存替换策略中进行选择：Random、NMRU、LIP（BIP的特例，gem5已经实现）。L1D Cache的相联度可取4、8、16。其他参数使用默认值。
    请至少完成上面要求的替换策略、相联度的模拟。描述你模拟的所有配置和结果，讨论变量的影响。给出性能最佳的配置，分析性能提升原因。<br>
    
    模拟结果如下所示（simTicks）：

|      | LIPRP      | NMRURP     | RandomRP   |
| ---- | ---------- | ---------- | ---------- |
| 4    | 1748661000 | 1748657500 | 1748662000 |
| 8    | 1748661500 | 1748652500 | 1748646500 |
| 16   | 1748684500 | 1748657000 | 1748663500 |
    
assoc和cache替换策略在这里对性能的影响似乎不大。应该是cache本身大小足够，而且mm程序的局部性优秀，导致给这些策略的表现机会不多。我去stats.txt里面看了下发现每个测试发生的置换次数都是差不多的。而在gem5，虽然有这么多种替换策略，但似乎并没有模拟出每种处理策略带来延迟的不同？

对于assoc指标，通常增大相联度可以提升cache命中率，但有时候也不一定。assoc越高，lookup time或者说tag_latency也会越长。不过这些测试输出的config.ini中的tag_latency都是一样的。

为了能给替换策略更多的表现机会，我把l1和l2的size减小到1kB，重新进行了实验：

|      | LIPRP      | NMRURP     | RandomRP   |
| ---- | ---------- | ---------- | ---------- |
| 4    | 2157901000 | 2109152000 | 2113613000 |
| 8    | 1995274500 | 1815302500 | 1819480500 |
| 16   | 1980882500 | 1780644500 | 1785497000 |

不过差别好像还是不怎么大。。。assoc的优势倒是体现出来了。

2.  考虑一个实际情况，O3CPU， 2GHz，issuewidth = 8。三种策略限制如下：
    |                       | Random |  NMRU |     LIP   |
    | ---------------| ---------- | --------- | -------- |
    |  Max assoc   |      16      |      8       |      8     |
    | Lookup time |    100ps  |   500ps |  555ps |
    | Tag Latency  |        2       |      10    |    11    |
<br>
    *注意lookup time（ps）和tag_latency（cycles，取整）的转化。*（1ps = 1E-12s）
    哪一种替换策略更优？说明理由。

题目似乎没说清楚？不明白这个latency是l1的还是l2的。我看源码中l1的默认值是2，l2的是20，而且感觉修改l1可能产生的影响会更大一些，就当他是l1的latency来处理好了，结果如下

|         | RP     | assoc. | tag_latency | simTicks   |
| ------- | ------ | ------ | ----------- | ---------- |
| config1 | Random | 16     | 2           | 1748663500 |
| config2 | NMRU   | 8      | 10          | 5082746500 |
| config3 | LIP    | 8      | 11          | 5501477000 |

在该情况下，Random策略那一组的表现最好。因为待测程序的局部性优秀，cache命中率高，所以每次查阅cache时的tag_latency成为了关键因素。这里Random策略的latency较小，所以体现出了优势。
