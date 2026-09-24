# angr入门

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

---

