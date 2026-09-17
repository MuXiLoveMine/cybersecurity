# CTF逆向解题实战

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

---

## 📋 内容审核与补充建议

> 针对「CTF逆向解题实战」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
