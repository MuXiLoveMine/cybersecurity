# ARM指令集基础

### 4.1 ARM架构概述

ARM（Advanced RISC Machines）是一种精简指令集（RISC）架构，广泛应用于移动设备、嵌入式系统和IoT设备。

**ARM架构特点：**
- Load/Store架构：数据处理指令不能直接操作内存，必须先加载到寄存器
- 固定长度指令：ARM模式32位，Thumb模式16/32位
- 大量通用寄存器：R0-R15
- 多数指令可条件执行
- 偏移寻址：支持前后索引和自动更新

**ARM架构版本：**

| 版本 | 说明 | 典型应用 |
|------|------|---------|
| ARMv7-A | 32位ARM | Cortex-A系列（旧手机） |
| ARMv8-A | 64位ARM(AArch64) | Cortex-A53/A72等（现代手机） |
| ARMv7-M | 微控制器 | Cortex-M系列（IoT设备） |
| ARMv6-M | 超低功耗 | Cortex-M0 |

### 4.2 寄存器与异常模式

**ARM寄存器组（ARM模式）：**

| 寄存器 | 名称 | 说明 |
|--------|------|------|
| R0-R7 | 通用寄存器 | 所有模式下可用 |
| R8-R12 | 通用寄存器 | 部分模式下有影子寄存器 |
| R13 | SP | 栈指针（各模式有独立副本） |
| R14 | LR | 链接寄存器（保存返回地址） |
| R15 | PC | 程序计数器 |
| CPSR | | 当前程序状态寄存器 |
| SPSR | | 保存的程序状态寄存器 |

**ARM处理器模式：**

| 模式 | 说明 |
|------|------|
| User | 用户模式（普通程序运行） |
| FIQ | 快速中断模式 |
| IRQ | 普通中断模式 |
| Supervisor | 超级用户模式（系统调用） |
| Abort | 存储访问异常模式 |
| Undefined | 未定义指令异常模式 |
| System | 系统模式（与User共享寄存器） |

### 4.3 ARM指令详解

**数据处理指令：**

```asm
MOV R0, #42        ; 立即数加载
MOV R0, R1         ; 寄存器间传送
ADD R0, R1, R2     ; R0 = R1 + R2
SUB R0, R1, R2     ; R0 = R1 - R2
MUL R0, R1, R2     ; R0 = R1 * R2
AND R0, R1, R2     ; R0 = R1 & R2
ORR R0, R1, R2     ; R0 = R1 | R2
EOR R0, R1, R2     ; R0 = R1 ^ R2 (XOR)
CMP R0, R1         ; 比较 R0 和 R1
```

**条件执行（ARM独特特性）：**

```asm
; 每条指令可附带条件后缀
MOVEQ R0, #1       ; 如果相等(Zero标志)，R0 = 1
MOVNE R0, #0       ; 如果不等，R0 = 0
ADDGT R0, R1, R2   ; 如果大于，R0 = R1 + R2
SUBLE R0, R1, R2   ; 如果小于等于，R0 = R1 - R2
```

**条件后缀表：**

| 后缀 | 含义 | 标志条件 |
|------|------|---------|
| EQ | Equal | Z=1 |
| NE | Not Equal | Z=0 |
| GT | Greater Than (signed) | Z=0, N=V |
| LT | Less Than (signed) | N!=V |
| GE | Greater or Equal | N=V |
| LE | Less or Equal | Z=1 or N!=V |
| HI | Higher (unsigned) | C=1, Z=0 |
| LS | Lower or Same | C=0 or Z=1 |
| CS/HS | Carry Set/Higher or Same | C=1 |
| CC/LO | Carry Clear/Lower | C=0 |

**内存访问指令（Load/Store）：**

```asm
LDR R0, [R1]         ; R0 = *(R1)  从内存加载到R0
STR R0, [R1]         ; *(R1) = R0  将R0存储到内存
LDR R0, [R1, #4]     ; R0 = *(R1+4)  带偏移加载
STR R0, [R1, #4]     ; *(R1+4) = R0  带偏移存储

; 前索引（带更新）
LDR R0, [R1, #4]!    ; R0 = *(R1+4), R1 = R1+4  (!表示更新基址)
STR R0, [R1, #4]!    ; *(R1+4) = R0, R1 = R1+4

; 后索引
LDR R0, [R1], #4     ; R0 = *R1, R1 = R1+4  (先用后更新)
STR R0, [R1], #4     ; *R1 = R0, R1 = R1+4

; 批量加载/存储
LDM R1, {R0, R2, R3}     ; 批量加载
STM R1, {R0, R2, R3}     ; 批量存储
LDMIA R1!, {R0-R3}       ; Increment After, 批量加载后R1自增
STMFD SP!, {R0-R3, LR}   ; Full Descending, 入栈（保存现场）
LDMFD SP!, {R0-R3, PC}   ; Full Descending, 出栈并返回（恢复现场+返回）

; PUSH/POP（等价于STMFD/LDMFD）
PUSH {R0-R3, LR}     ; 入栈
POP {R0-R3, PC}      ; 出栈，PC=R14(LR)实现返回
```

**分支指令：**

```asm
B label             ; 无条件跳转
BL label            ; 带链接跳转（LR=返回地址）
BX R0               ; 间接跳转（切换ARM/Thumb模式）
BLX R0              ; 带链接间接跳转
BEQ label           ; 条件跳转（相等）
BNE label           ; 条件跳转（不等）
```

### 4.4 Thumb指令集

Thumb指令集是ARM的16/32位混合编码指令集，主要用于减小代码体积。

**Thumb特点：**
- 16位指令编码（Thumb-1），部分指令为32位（Thumb-2）
- 寄存器使用受限（通常R0-R7可直接访问）
- 不支持条件执行（Thumb-1中，Thumb-2通过IT指令支持）
- 代码密度更高，适合存储受限场景

**ARM/Thumb模式切换：**
```asm
; 通过BX指令的最低位决定模式
BX R0              ; R0[0]=0: 切换到ARM模式, R0[0]=1: 切换到Thumb模式
; 当跳转地址的最低位为1时，处理器切换到Thumb模式
```

**AArch64（ARMv8 64位）变化：**
- 寄存器扩展为64位：X0-X30, SP, PC
- 32位视图为W0-W30
- 参数传递：X0-X7
- 返回值：X0
- LR为X30，SP独立寄存器

---

---

## 📋 内容审核与补充建议

> 针对「ARM指令集基础」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
