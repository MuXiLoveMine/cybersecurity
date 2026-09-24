# angr插件与生态

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

---

