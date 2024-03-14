## 准备工作
下载了lab仓库中的benchmark程序。其中有几个程序需要用到一些随机数作为输入，这通过py脚本实现。不过脚本里面的代码可能需要做一些修改，因为我用的是python3，所以把makefile和py脚本中的**python**全部替换成了**python3**，还有把rand_spmv_arrs.py这个文件中的xrange函数替换成了range，前者似乎是python2专有的

## 配置步骤：

这次使用的是内置的se.py这个配置脚本，他的功能比较完善。可以去configs/common/Options.py
观察脚本的用法，去里面搜索发现大部分需要的参数都可以直接配置，只有Issue width这一项不支持配置，默认一直是8。处理起来可能稍微麻烦一些。

我想到的是在Options.py中找个地方(183行)添加了Issue width的配置选项:
```
parser.add_argument("--issue_width", type=int, default=8)
```
但是这还只是解析了参数，要使该参数生效，还需要在se.py中添加相应的代码。于是我在se.py的199行添加了：
```
if args.cpu_type == "DerivO3CPU":
	cpu.issueWidth = args.issue_width
```

可以使用以下方法测试配置是否生效：
```
./build/X86/gem5.opt configs/example/se.py --cmd=tests/test-progs/hello/bin/x86/linux/hello --cpu-type=DerivO3CPU --caches --issue_width=2
```
然后：
```
cat m5out/config.ini | grep issue
```
观察输出的issueWidth是否等于2。如果是2应该就是成功了。
(只有DerivO3CPU支持issue width选项，并且DerivO3CPU还必须开启cache)
 ## 需要测试的配置列表
   
  | CPU-type   | Issue width | CPU-clock | L2 cache |
  | ---------- | ----------- | --------- | -------- |
  | DerivO3CPU | 8           | 1GHz      | No       |
  | MinorCPU   | -           | 1GHz      | No       |
  | DerivO3CPU | 2           | 1GHz      | No       |
  | DerivO3CPU | 8           | 4GHz      | No       |
  | DerivO3CPU | 8           | 1GHz      | 256kB    |
  | DerivO3CPU | 8           | 1GHz      | 2MB      |
  | DerivO3CPU | 8           | 1GHz      | 16MB     |

  公共参数：
  -   Memory: DDR3_1600_8x8
 -   2-level cache hierarchy (64KB L1 icache, 64KB L1 dcache, L2可变)

为方便起见编写了一个Makefile 脚本来完成测试工作
##  统计指标说明：

**memory regularity:** $$ \frac{\text{system.cpu.dcache.overallHits::total}}{\text{system.cpu.dcache.overallMisses::total}+\text{system.cpu.dcache.overallHits::total}} $$

该式约大，说明数据访问越规整，越可被预测，越有规律性，可以大致表征该workload具有memory regularity；

**control regularity:** $$ 1-\frac{\text{system.cpu.branchPred.condIncorrect}}{\text{system.cpu.branchPred.condPredicted}} $$ 该式越大，说明branch被预测正确的概率越大，即指令的流动越有规律性，可以大致表征该workload具有control regularity；

**memory locality:** $$ \frac{\text{system.cpu.dcache.overallHits::total}}{\text{system.cpu.dcache.overallMisses::total}+\text{system.cpu.dcache.overallHits::total}} $$ 该式越大，也说明了数据访问的时间局部性和空间局部性越强，可以大致表征该workload具有memory locality。

这三个指标的表达式我不知道是怎么得来的，后来发现原来是要自己设计。我参考的是[这里](https://github.com/xjh389336645/calab-gem5/blob/master/lab2/lab2.md)的解释。由于手动统计的话过程会比较麻烦，我也编写了脚本来辅助进行。
## 统计结果
###   hostSeconds，单位：秒：

|	      |   mm  | lfsr | merge | sieve  |  spmv  |
|---------|-------|------|-------|--------|--------|
| config1 | 60.81 | 0.24 | 28.59 | 165.35 | 208.40 |
| config2 | 73.55 | 0.17 | 20.39 | 169.36 | 200.44 |
| config3 | 79.40 | 0.27 | 34.17 | 170.46 | 214.04 |
| config4 | 71.81 | 0.27 | 28.76 | 315.46 | 312.72 |
| config5 | 70.86 | 0.25 | 28.61 | 210.14 | 196.39 |
| config6 | 62.99 | 0.25 | 28.76 | 117.65 | 185.64 |
| config7 | 61.11 | 0.26 | 28.65 | 117.61 | 175.46 |

 - 当时我的电脑开启了低性能模式，所以如果其他人自己动手测试的话数据可能会比这个好看一些
 - 这个时间是模拟环境下的时间，虽然很直观但是不能反映真实情况。因为有时候cpu本身的性能很棒，但是模拟它需要花费很多时间。所以还是要看simTicks或者simSeconds

###   simSeconds，单位：秒：

|	      |    mm    |   lfsr   |   merge  |  sieve   |   spmv   |
|---------|----------|----------|----------|----------|----------|
| config1 | 0.003554 | 0.000032 | 0.001768 | 0.053448 | 0.029377 |
| config2 | 0.020403 | 0.000058 | 0.004668 | 0.055777 | 0.120218 |
| config3 | 0.007382 | 0.000034 | 0.003070 | 0.054133 | 0.028985 |
| config4 | 0.001322 | 0.000022 | 0.000476 | 0.041358 | 0.025823 |
| config5 | 0.003386 | 0.000049 | 0.001805 | 0.081513 | 0.026104 |
| config6 | 0.003386 | 0.000049 | 0.001805 | 0.025130 | 0.017587 |
| config7 | 0.003386 | 0.000049 | 0.001805 | 0.025130 | 0.012821 |

### memory regularity

|	      |  mm  | lfsr | merge | sieve |  spmv  |
|---------|------|------|-------|-------|--------|
| config1 | 0.950 | 0.919 | 0.997  | 0.640  | 0.513 |
| config2 | 0.987 | 0.906 | 0.996  | 0.577 | 0.781 |
| config3 | 0.950 | 0.903 | 0.995  | 0.640 | 0.480 |
| config4 | 0.949 | 0.916 | 0.996  | 0.640 | 0.479 |
| config5 | 0.951 | 0.918 | 0.997  | 0.640 | 0.387 |
| config6 | 0.951 | 0.918 | 0.997  | 0.640 | 0.318 |
| config7 | 0.951 | 0.918 | 0.997  | 0.640 | 0.480 |

### control regularity

|	      |  mm  | lfsr | merge | sieve |  spmv  |
|---------|------|------|-------|-------|--------|
| config1 | 0.997 | 0.768 | 0.926 | 1.00  | 0.985 |
| config2 |  0/0  |  0/0 |  0/0  |  0/0 |  0/0 |
| config3 | 0.997 | 0.803 | 0.947 | 1.00 | 0.986 |
| config4 | 0.997 | 0.767 | 0.926  | 1.00 | 0.985 |
| config5 | 0.997 | 0.767 | 0.926  | 1.00 | 0.985 |
| config6 | 0.997 | 0.767 | 0.926  | 1.00 | 0.985 |
| config7 | 0.997 | 0.767 | 0.926  | 1.00 | 0.985 |

 - sieve的测试结果实际上是0.9996
 - config2中的CPU不支持分支预测，因此无法根据给出公式统计memory regularity指标

### memory locality
表达式和memory regularity一样

除此之外还额外编写了一个经典的双重循环访问二维数组的程序，在内层和外层循环中采取不同的循环变量，采用config7中的配置，代码如下：
```
#include <stdio.h>
#include <stdlib.h>     /* malloc, free, rand */

#define N 256

int main(int argc, char* argv[]) {
	int a[N][N];
	for (int i = 0; i < N; i++) {
		for (int j = 0; j < N; j++)
			a[i][j] = rand();	// 在这里修改访问方式
	}
	return 0;
}

```
简单测试了一下它的执行时间，结果如下：

|	      |   ij  |   ji  |
|---------|-------|-------|
| gcc -O3 | 53.06 | 51.65 | 
| gcc -O0 | 64.71 | 75.57 |

可以发现gcc -O3的时候两者差距不大，甚至以ji方式访问的执行时间还要更短。这里应该是编译器自动进行了优化。但是到了-O0的时候差距就体现出来了。

感觉这里可以测试的地方还有很多，例如循环展开，修改N，分块访问等。不过我就没有继续往下做了。

## 问题解答：
1.  应该使用什么指标来比较不同系统配置之间的性能？为什么？
我认为运行时间 (时钟周期数)是个不错的选择，因为它便于统计，而且比较客观，对于所有的程序和系统来说都是公平的
2.  是否有任何基准测试受益于删除 L2 缓存？请说明理由。
有，主要是拿config1的数据和后面三个作比较，可以发现lfsr在移除L2 cache后的simSeconds更短。这可能是因为该程序的规模较小，而且局部性不错，L1 cache已经完全够用。引入L2 cache反而带来了额外的开销。
3.  在讨论程序的运行行为时，我们会遇到a) memory regularity，b) control regularity，和 c) memory locality，请谈一谈你对他们的理解。
上面已经有了
4.  对于这三个程序属性——a) memory regularity，b) control regularity，和 c) memory locality——从 stats.txt 中举出一个统计指标（或统计指标的组合），通过该指标你可以区分一个workload是否具有上述的某一个属性。 （例如，对于control regularity，它与分支指令的数量成反比。但你一定可以想到一个更好的）。
上面已经有了
5.  对于每一个实验中用到的benchmark，描述它的a) memory regularity, b) control regularity, c) memory locality；解释该benchmark对哪个微架构参数最敏感（换句话说，你认为“瓶颈”是什么），并使用推理或统计数据来证明其合理性。

6.  选择一个benchmark，提出一种你认为对该benchmark非常有效的应用程序增强、ISA 增强和微体系结构增强。

选择mm。
**应用程序增强：**
把第21行的：
```
i_row = i * row_size;
```
移动到循环的外面。因为每次迭代k的时候，i和row_size都是固定的，所以i_row的值并不会改变。没必要每次都计算，可以减少执行的指令数量。同理24行的
```
m1[i_row + k + kk]
```
也可以提到外面。
**ISA增强：**
例如设计更强大的向量指令，提升数据级并行
**体系结构增强：**
调整cache，issue width，cpu type等信息。优化电路中的关键路径
