# AFL使用指南

### 2.1 AFL安装与配置

**安装AFL++（推荐使用增强版）：**

```bash
# Ubuntu/Debian
sudo apt install build-essential git python3 cmake automake texinfo \
    flex bison libglib2.0-dev libpixman-1-dev python3-setuptools \
    cargo libgtk-3-dev

# 克隆AFL++
git clone https://github.com/AFLplusplus/AFLplusplus.git
cd AFLplusplus

# 编译
make distrib
sudo make install

# 验证安装
afl-fuzz --version
```

**安装Python支持：**

```bash
pip3 install afl-fred
# 或使用AFL++自带的Python工具
```

### 2.2 编译插桩

AFL支持多种插桩方式，以适应不同场景：

**方式1: 源码插桩（afl-clang/afl-gcc）**

```bash
# 使用afl编译器替代标准编译器
export CC=afl-clang-fast
export CXX=afl-clang-fast++
export AFL_USE_ASAN=1  # 启用AddressSanitizer（可选）

# 编译目标项目
cd target_project
./configure --disable-shared  # 建议禁用动态库
make -j$(nproc)

# 编译后的二进制已包含覆盖率插桩
```

**方式2: LLVM LTO模式（最佳覆盖率）**

```bash
export AFL_LLVM_LTO=1
export CC=afl-clang-lto
export CXX=afl-clang-lto++
make -j$(nproc)
```

**方式3: 二进制插桩（无源码）**

```bash
# 使用afl-qemu-trace对闭源程序进行插桩
# 需要先编译QEMU模式
cd AFLplusplus
make source-only
cd qemu_mode
./build_qemu_support.sh

# 使用方法
afl-fuzz -Q -i input/ -o output/ -- ./binary @@
# -Q: 启用QEMU模式
# @@: 被替换为输入文件路径
```

**编译插桩验证：**

```bash
# 检查二进制是否包含AFL插桩
afl-showmap -o /dev/null -- ./binary /dev/null
# 如果有输出说明插桩成功
```

### 2.3 语料库构建

语料库（种子文件）是模糊测试的起点，直接影响测试效果。

**语料库构建原则：**
1. **多样性**：包含不同类型和大小的输入
2. **最小化**：每个种子应尽量小（减少无效变异）
3. **有效性**：种子应该是目标程序能正常解析的输入
4. **覆盖率**：种子应覆盖不同的代码路径

**语料库整理工具：**

```bash
# 使用afl-cmin最小化语料库
afl-cmin -i raw_corpus/ -o minimized_corpus/ -- ./binary @@

# 使用afl-tmin进一步最小化单个种子
afl-tmin -i single_input -o minimized_input -- ./binary @@

# 示例：最小化PNG语料库
afl-cmin -i png_raw/ -o png_min/ -- ./png_parser @@

# 单个文件最小化
afl-tmin -i sample.png -o sample_min.png -- ./png_parser @@

# 设置超时（毫秒）
afl-tmin -t 1000 -i sample.png -o sample_min.png -- ./png_parser @@
```

**自动语料库生成脚本：**

```python
#!/usr/bin/env python3
"""
自动生成初始语料库
针对不同文件类型生成有效种子
"""
import os
import struct
import random

def generate_png_corpus(output_dir, count=10):
    """生成最小PNG文件作为种子"""
    os.makedirs(output_dir, exist_ok=True)
    
    # PNG文件头
    png_sig = b'\x89PNG\r\n\x1a\n'
    # IHDR chunk (1x1像素)
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)  # width, height, bitdepth, colortype
    ihdr_crc = struct.pack('>I', 0)  # CRC (简化)
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + ihdr_crc
    # IEND chunk
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', 0xAE426082)
    
    for i in range(count):
        filepath = os.path.join(output_dir, f'seed_{i:03d}.png')
        with open(filepath, 'wb') as f:
            f.write(png_sig + ihdr + iend)
    
    print(f"生成 {count} 个PNG种子到 {output_dir}")

def generate_elf_corpus(output_dir, count=10):
    """生成最小ELF头作为种子"""
    os.makedirs(output_dir, exist_ok=True)
    
    for i in range(count):
        filepath = os.path.join(output_dir, f'seed_{i:03d}.elf')
        with open(filepath, 'wb') as f:
            # ELF魔数 + 变长随机数据
            f.write(b'\x7fELF')
            f.write(bytes([random.randint(1, 2)]))  # class: 32/64
            f.write(bytes([random.randint(1, 2)]))  # data: LE/BE
            f.write(bytes(random.randint(0, 255) for _ in range(random.randint(10, 100))))
    
    print(f"生成 {count} 个ELF种子到 {output_dir}")

def generate_json_corpus(output_dir, count=20):
    """生成JSON种子"""
    os.makedirs(output_dir, exist_ok=True)
    
    templates = [
        '{"key": "value"}',
        '{"num": 12345}',
        '{"arr": [1, 2, 3]}',
        '{"nested": {"a": {"b": {"c": 1}}}}',
        '{"null": null, "bool": true, "float": 3.14}',
        '{"unicode": "\\u00e9\\u4e2d\\u6587"}',
        '{"empty_str": "", "empty_arr": [], "empty_obj": {}}',
        '[]',
        '{}',
        '"string"',
        '42',
        'null',
        'true',
        '3.14159',
    ]
    
    for i in range(count):
        filepath = os.path.join(output_dir, f'seed_{i:03d}.json')
        template = templates[i % len(templates)]
        with open(filepath, 'w') as f:
            f.write(template)
    
    print(f"生成 {count} 个JSON种子到 {output_dir}")

if __name__ == '__main__':
    generate_png_corpus('corpus/png', 10)
    generate_elf_corpus('corpus/elf', 10)
    generate_json_corpus('corpus/json', 20)
```

### 2.4 字典使用

字典提供格式特定的关键字，帮助模糊测试器生成更有效的输入。

**字典文件格式：**

```
# AFL字典文件示例

# PNG字典
keyword_png_sig = "\x89PNG\r\n\x1a\n"
keyword_ihdr = "IHDR"
keyword_idat = "IDAT"
keyword_iend = "IEND"
keyword_plte = "PLTE"
keyword_trns = "tRNS"
keyword_gama = "gAMA"
keyword_chrm = "cHRM"
keyword_phys = "pHYs"
keyword_text = "tEXt"
keyword_ztxt = "zTXt"
keyword_itxt = "iTXt"
keyword_iccp = "iCCP"
keyword_time = "tIME"

# HTTP字典
keyword_get = "GET "
keyword_post = "POST "
keyword_http = " HTTP/1.1"
keyword_host = "Host: "
keyword_content_type = "Content-Type: "
keyword_content_length = "Content-Length: "
keyword_cookie = "Cookie: "
keyword_connection = "Connection: close"
```

**使用字典：**

```bash
# 使用内置字典
afl-fuzz -i input/ -o output/ -x /usr/share/afl/dictionaries/png.dict -- ./png_parser @@

# 使用自定义字典
afl-fuzz -i input/ -o output/ -x custom.dict -- ./parser @@
```

**自动生成字典：**

```bash
# 从现有种子中提取字典
# 使用AFL++的afl-cc -xaf模式
afl-cc -xaf corpus/* > extracted.dict

# 或使用第三方工具
# https://github.com/adrianherrera/afl_utils
```

### 2.5 AFL进阶配置

**关键环境变量：**

| 变量 | 说明 | 示例 |
|------|------|------|
| AFL_MAP_SIZE | 共享内存大小 | export AFL_MAP_SIZE=262144 |
| AFL_FORKSRV | fork server | 默认开启 |
| AFL_CC | 编译器 | export AFL_CC=clang |
| AFL_USE_ASAN | 启用ASAN | export AFL_USE_ASAN=1 |
| AFL_USE_MSAN | 启用MSAN | export AFL_USE_MSAN=1 |
| AFL_USE_UBSAN | 启用UBSAN | export AFL_USE_UBSAN=1 |
| AFL_USE_TSAN | 启用TSAN | export AFL_USE_TSAN=1 |
| AFL_USE_CFISAN | 启用CFI | export AFL_USE_CFISAN=1 |
| AFL_TMPDIR | 临时目录 | export AFL_TMPDIR=/tmp |
| AFL_IOTASAN | IoT安全 | - |

**afl-fuzz命令行参数：**

```bash
# 基本用法
afl-fuzz -i input/ -o output/ -- ./target @@

# 并行模糊（多核）
afl-fuzz -i input/ -o output/ -M main -- ./target @@    # 主节点
afl-fuzz -i input/ -o output/ -S sub1 -- ./target @@    # 从节点1
afl-fuzz -i input/ -o output/ -S sub2 -- ./target @@    # 从节点2

# 超时设置
afl-fuzz -t 500 -i input/ -o output/ -- ./target @@
# -t 500: 超时500ms

# 内存限制
afl-fuzz -m 512 -i input/ -o output/ -- ./target @@
# -m 512: 内存限制512MB

# 字典
afl-fuzz -x dict.txt -i input/ -o output/ -- ./target @@

# 不确定性阶段跳过
afl-fuzz -d -i input/ -o output/ -- ./target @@
# -d: 跳过确定性阶段（适合大型语料库）

# 延迟forkserver
afl-fuzz -L 0 -i input/ -o output/ -- ./target @@
# -L: 延迟forkserver模式（支持持久化模式）

# 快速模式（MOpt）
afl-fuzz -i input/ -o output/ -L 0 -- ./target @@
```

**AFL持久化模式（Persistent Mode）：**

持久化模式大幅提升模糊测试效率，避免每次都fork进程：

```c
// target_persistent.c
#include <stdio.h>
#include <stdlib.h>

// 需要定义 AFL_PERSISTENT
#ifdef __AFL_COMPILER
  #ifndef AFL_PERSISTENT
    #define AFL_PERSISTENT
  #endif
#endif

// 目标函数
void parse_input(const unsigned char *data, size_t size) {
    // 解析逻辑
    if (size < 4) return;
    if (data[0] == 'A' && data[1] == 'F' && data[2] == 'L') {
        // 处理...
    }
}

int main() {
    // 持久化循环
#ifdef AFL_PERSISTENT
    while (__AFL_LOOP(1000)) {  // 循环1000次后重启进程
        unsigned char buf[4096];
        int len = read(0, buf, sizeof(buf));
        if (len > 0) {
            parse_input(buf, len);
        }
    }
#else
    // 非持久化模式
    unsigned char buf[4096];
    int len = read(0, buf, sizeof(buf));
    if (len > 0) {
        parse_input(buf, len);
    }
#endif
    return 0;
}
```

**AFL共享内存模式（Shared Memory / Deferred Forkserver）：**

```c
#include <sys/shm.h>
#include <sys/wait.h>

// 使用共享内存传递输入数据
// 避免文件I/O开销
#ifdef __AFL_SHM_ID
    // AFL提供了共享内存ID
    unsigned char *afl_area = shmat(__AFL_SHM_ID, 0, 0);
#endif
```

**监控面板解读：**

```
┌─── AFL++ 进程监控 ────────────────────────────┐
│                                                │
│  策略: explore | 状态: running | 进程: 12345  │
│                                                │
│  执行时间: 5h 30m | 活跃种子: 152             │
│                                                │
│  ┌─ 整体 ─────────────────────────────────┐    │
│  │ 已执行: 12.3M | 速度: 8500/sec        │    │
│  │ 找到崩溃: 23 | 找到挂起: 5            │    │
│  │ 唯一路径: 3487 | 唯一边: 15234       │    │
│  └────────────────────────────────────────┘    │
│                                                │
│  ┌─ 各阶段 ───────────────────────────────┐    │
│  │ 确定性: 100% (已完成)                  │    │
│  │ Havoc:  23% (进行中)                   │    │
│  │ 拼接:   0% (等待)                      │    │
│  └────────────────────────────────────────┘    │
│                                                │
│  ┌─ 覆盖率 ───────────────────────────────┐    │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░ 67%           │    │
│  │ 代码路径覆盖: 67% | 基本块: 4521/6732 │    │
│  └────────────────────────────────────────┘    │
│                                                │
│  ┌─ 最新发现 ─────────────────────────────┐   │
│  │ [5h28m] 新崩溃: ASAN_WRITE of size 8    │   │
│  │ [5h25m] 新路径: depth=12, tc=15         │   │
│  │ [5h20m] 新路径: depth=8, tc=10          │   │
│  └────────────────────────────────────────┘    │
│                                                │
└────────────────────────────────────────────────┘
```

---

---

