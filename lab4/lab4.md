# 实验4 使用gem5探索指令级并行

## 1 改写后的`daxpy`文件

由于`N = 10000`，可对三个函数均手工循环展开10次。对于函数`stencil`，多次循环展开之后的余项不进行展开，按照原来的执行方式进行。

```cpp
#define UNROLL 10

void daxpy_unroll(double *X, double *Y, double alpha, const int N)
{
    for (int i = 0; i < N; i += UNROLL)
    {
        Y[i  ] = alpha * X[i  ] + Y[i  ];
        Y[i+1] = alpha * X[i+1] + Y[i+1];
        Y[i+2] = alpha * X[i+2] + Y[i+2];
        Y[i+3] = alpha * X[i+3] + Y[i+3];
        Y[i+4] = alpha * X[i+4] + Y[i+4];
        Y[i+5] = alpha * X[i+5] + Y[i+5];
        Y[i+6] = alpha * X[i+6] + Y[i+6];
        Y[i+7] = alpha * X[i+7] + Y[i+7];
        Y[i+8] = alpha * X[i+8] + Y[i+8];
        Y[i+9] = alpha * X[i+9] + Y[i+9];
    }
}

void daxsbxpxy_unroll(double *X, double *Y, double alpha, double beta, const int N)
{
    for (int i = 0; i < N; i += UNROLL)
    {
        Y[i  ] = alpha * X[i  ] * X[i  ] + beta * X[i  ] + X[i  ] * Y[i  ];
        Y[i+1] = alpha * X[i+1] * X[i+1] + beta * X[i+1] + X[i+1] * Y[i+1];
        Y[i+2] = alpha * X[i+2] * X[i+2] + beta * X[i+2] + X[i+2] * Y[i+2];
        Y[i+3] = alpha * X[i+3] * X[i+3] + beta * X[i+3] + X[i+3] * Y[i+3];
        Y[i+4] = alpha * X[i+4] * X[i+4] + beta * X[i+4] + X[i+4] * Y[i+4];
        Y[i+5] = alpha * X[i+5] * X[i+5] + beta * X[i+5] + X[i+5] * Y[i+5];
        Y[i+6] = alpha * X[i+6] * X[i+6] + beta * X[i+6] + X[i+6] * Y[i+6];
        Y[i+7] = alpha * X[i+7] * X[i+7] + beta * X[i+7] + X[i+7] * Y[i+7];
        Y[i+8] = alpha * X[i+8] * X[i+8] + beta * X[i+8] + X[i+8] * Y[i+8];
        Y[i+9] = alpha * X[i+9] * X[i+9] + beta * X[i+9] + X[i+9] * Y[i+9];
    }
}

void stencil_unroll(double *Y, double alpha, const int N)
{
    int iter = N / UNROLL - 1;
    for (int i = 0; i < iter; i ++) {
        register int k = i * UNROLL + 1;
        Y[k  ] = alpha * Y[k-1] + Y[k  ] + alpha * Y[k+1];
        Y[k+1] = alpha * Y[k  ] + Y[k+1] + alpha * Y[k+2];
        Y[k+2] = alpha * Y[k+1] + Y[k+2] + alpha * Y[k+3];
        Y[k+3] = alpha * Y[k+2] + Y[k+3] + alpha * Y[k+4];
        Y[k+4] = alpha * Y[k+3] + Y[k+4] + alpha * Y[k+5];
        Y[k+5] = alpha * Y[k+4] + Y[k+5] + alpha * Y[k+6];
        Y[k+6] = alpha * Y[k+5] + Y[k+6] + alpha * Y[k+7];
        Y[k+7] = alpha * Y[k+6] + Y[k+7] + alpha * Y[k+8];
        Y[k+8] = alpha * Y[k+7] + Y[k+8] + alpha * Y[k+9];
        Y[k+9] = alpha * Y[k+8] + Y[k+9] + alpha * Y[k+10];
    }

    for (int i = iter * UNROLL + 1; i < N - 1; i++)
    {
        Y[i] = alpha * Y[i-1] + Y[i] + alpha * Y[i+1];
    }
}

```



## 2 模拟输出结果统计


统计方法：
```
以cpi为例：
cat m5out/stats.txt | grep cpi
然后观察中间的第2-7这几组数据
```


| `simTicks`         | 1st      | 2nd (additional `HPI_FloatSimdFu()`) | 3rd (`-O3` optimization based on 2nd) |
| ------------------ | -------- | ------------------------------------ | ------------------------------------- |
| `daxpy`            | 35563000 | 35563500                             | 18236500                              |
| `daxpy_unroll`     | 35244250 | 35248500                             | 17344000                              |
| `daxsbxpxy`        | 62903250 | 60403500                             | 28323250                              |
| `daxsbxpxy_unroll` | 62241500 | 60184500                             | 17912000                              |
| `stencil`          | 49056250 | 49056250                             | 33130000                              |
| `stencil_unroll`   | 42011750 | 41764250                             | 36155500                              |



| `cpi`              | 1st      | 2nd (additional `HPI_FloatSimdFu()`) | 3rd (`-O3` optimization based on 2nd) |
| ------------------ | -------- | ------------------------------------ | ------------------------------------- |
| `daxpy`            | 1.777839 | 1.777864                             | 1.822648                              |
| `daxpy_unroll`     | 2.202318 | 2.202343                             | 2.887538                              |
| `daxsbxpxy`        | 2.096478 | 2.013165                             | 2.059012                              |
| `daxsbxpxy_unroll` | 2.393559 | 2.314299                             | 1.789947                              |
| `stencil`          | 1.962309 | 1.962309                             | 2.208703                              |
| `stencil_unroll`   | 1.952968 | 1.941462                             | 4.374663                              |

| `committedInst`    | 1st    | 2nd (additional `HPI_FloatSimdFu()`) | 3rd (`-O3` optimization based on 2nd) |
| ------------------ | ------ | ------------------------------------ | ------------------------------------- |
| `daxpy`            | 80014  | 80014                                | 45022                                 |
| `daxpy_unroll`     | 64013  | 64013                                | 30026                                 |
| `daxsbxpxy`        | 120017 | 120017                               | 60023                                 |
| `daxsbxpxy_unroll` | 104015 | 104015                               | 45028                                 |
| `stencil`          | 109995 | 109995                               | 69998                                 |
| `stencil_unroll`   | 86047  | 86047                                | 48054                                 |


| `BP lookups`              | 1st      | 2nd (additional `HPI_FloatSimdFu()`) | 3rd (`-O3` optimization based on 2nd) |
| ------------------ | -------- | ------------------------------------ | ------------------------------------- |
| `daxpy`            | 10025 | 10025                             | 5015                              |
| `daxpy_unroll`     | 1015  | 1015                             | 1014                              |
| `daxsbxpxy`        | 10027 | 10027                             | 5009                              |
| `daxsbxpxy_unroll` | 1013  | 1013                             | 1014                              |
| `stencil`          | 10017 | 10017                             | 10010                              |
| `stencil_unroll`   | 1032  | 1032                             | 1033             


| `dcache miss times`              | 1st      | 2nd (additional `HPI_FloatSimdFu()`) | 3rd (`-O3` optimization based on 2nd) |
| ------------------ | -------- | ------------------------------------ | ------------------------------------- |
| `daxpy`            | 1254 | 1254                             | 1256                              |
| `daxpy_unroll`     | 1562  | 1562                             | 4495                              |
| `daxsbxpxy`        | 1254  | 1254                             | 1257                              |
| `daxsbxpxy_unroll` | 1560  | 1560                             | 3958                              |
| `stencil`          | 621   | 621                             | 621                              |
| `stencil_unroll`   | 776   | 776                             | 777             


总结：

1. 循环展开后，指令条数均发生减少。
2. 循环展开显著减少了分支指令的数量，从而可以降低预测失败时的惩罚；但在本实验中程序的局部性良好，导致分支预测的成功率很高，统计数据中并没有体现出什么明显的区别。
3. 除第三次实验中的`daxsbpxy`函数外，循环展开都使得CPI有一定程度的增大；经过对比输出的统计信息，发现循环展开后dcache的缺失率升高了，这应该是导致CPI增大的其中一个原因。
4. 函数的执行时间同时受指令条数和CPI的影响（在clock cycle大小不变的前提下），故当循环展开带来的指令条数的减小不足以抵消CPI增大的负面影响时，函数的执行时间反而更长；
5. 实验结果显示，编译器优化的效果显著好于手动循环展开。



## 3 问题解答

### 1

**Question:**

如何证明展开循环后的函数产生了正确的结果？


**Answer:**

可以手动再编写一些测试函数，给定同样的输入，对比展开前后的输出结果是否相同。


### 2

**Question:**

对于每一个函数，循环展开是否提升了性能？循环展开减少了哪一种hazard？

**Answer:**

是。循环展开可以在存在data hazard的两条指令之间插入一些无关指令，从而减少潜在的data hazard。并且循环展开还减少了分支指令的数量，从而可以降低control hazard。

但与此同时，循环展开后的cpi通常也会增大。这可能是循环展开让流水线更加紧凑，各执行单元容易同时处于忙碌，增大了structural hazard。

### 3

**Question:**

你应该展开循环多少次？每个循环都一样吗？如果你没有展开足够多或展开太多会影响程序性能吗？

**Answer:**

我展开了10次。对于stencil程序需要两段执行，见展开前面几项，再对剩下的几项做正常的循环处理。总的来说，循环展开可以减少指令的数量，但可能也会增大cpi。如果展开太少，可能效果不明显；如果展开太多，代码规模会增大，可能会影响icache的性能。

### 4

**Question:**

增加硬件对循环展开版本的函数和原函数有什么影响？添加更多硬件会减少哪种或哪些hazard？

**Answer:**

在实验中，增加硬件后函数的指令条数没有发生变化，`daxsbxpxy`、`daxsbxpxy_unroll`和`stencil_unroll`的CPI有少量的下降，导致这三个函数最终的执行时间有小幅度的改善。增加硬件可以减少浮点执行时的structure hazard，即硬件可以允许更多条浮点指令同时执行，而不需要在RS中持续等待。尤其当循环展开次数较多而浮点指令执行时间较长时，该效果更加显著。

### 5

**Question:**

选择你认为合适的指标比较四个版本函数的性能表现，为什么选择该指标？

**Answer:**

**执行时间**(simTicks)。因为他比较客观，对任何一组函数来说都是公平的。而且得出该数据的时候也综合考虑了各种因素。

根据该指标来看，在gcc -O1的条件下，循环展开都略微提升了程序的性能。其中对stencil的提升最明显。

### 6

**Question:**

你认为本次实验中你所进行的手动循环展开优化有意义吗？还是说编译器优化代码就已经足够了？说明理由。

**Answer:**

我认为意义不大。因为现代的编译器已经足够强大，能够做很多优化了，在开启gcc -O3后手工优化的程序和编译器处理的结果相差不大（不过这里的daxsbxpxy似乎是个例外），甚至手工优化的stencil程序，性能还不如编译器自动产生的。而且循环展开会降低代码的可读性和增加代码规模，若处理不当还会导致错误的结果。

我认为很多时候与其手动优化，可能还不如编写一些对编译器友好的代码，然后让编译器自动去做优化。



