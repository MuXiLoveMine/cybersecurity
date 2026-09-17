# angr核心功能

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

---

## 📋 内容审核与补充建议

> 针对「angr核心功能」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
