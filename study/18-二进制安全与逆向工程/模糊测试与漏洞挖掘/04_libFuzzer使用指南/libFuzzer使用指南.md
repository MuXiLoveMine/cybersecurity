# libFuzzer使用指南

### 3.1 libFuzzer基础

libFuzzer是LLVM项目内置的模糊测试引擎，与AddressSanitizer等工具深度集成，适合对C/C++库进行白盒模糊测试。

**libFuzzer特点：**
- 集成在LLVM/Clang中，无需额外安装
- 支持进程内模糊测试（in-process），效率高
- 与ASan/MSan/UBSan无缝配合
- 支持自定义变异器和字典
- 支持语料库合并和最小化

**安装与编译：**

```bash
# libFuzzer包含在LLVM中
# 确保安装了clang
sudo apt install clang

# 验证
clang --version
```

### 3.2 编写Fuzz Target

libFuzzer要求用户提供一个`LLVMFuzzerTestOneInput`函数作为模糊测试入口：

**基本Fuzz Target：**

```c
// fuzz_target.c
#include <stdint.h>
#include <stddef.h>

// 目标函数声明
void parse_data(const uint8_t *data, size_t size);

// libFuzzer入口点
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 调用需要测试的函数
    parse_data(data, size);
    return 0;
}
```

**编译与运行：**

```bash
# 编译（启用ASan）
clang -g -O1 -fsanitize=fuzzer,address -o fuzz_target fuzz_target.c parse_data.c

# 运行
./fuzz_target

# 指定语料库目录
./fuzz_target corpus/

# 指定最大运行时间（秒）
./fuzz_target -max_total_time=3600

# 指定最大输入长度
./fuzz_target -max_len=4096

# 指定字典
./fuzz_target -dict=parse.dict corpus/
```

**高级Fuzz Target示例：**

```c
// fuzz_json_parser.c
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

// 模拟的JSON解析器
typedef enum {
    JSON_NULL, JSON_BOOL, JSON_NUMBER,
    JSON_STRING, JSON_ARRAY, JSON_OBJECT
} JsonType;

typedef struct {
    JsonType type;
    // ... 其他字段
} JsonValue;

// 模拟解析函数（实际应替换为真实的JSON库）
int json_parse(const uint8_t *data, size_t size, JsonValue *result) {
    if (size == 0) return -1;
    
    // 检查各种JSON类型
    if (size >= 4 && memcmp(data, "null", 4) == 0) {
        result->type = JSON_NULL;
        return 0;
    }
    if (size >= 4 && memcmp(data, "true", 4) == 0) {
        result->type = JSON_BOOL;
        return 0;
    }
    if (size >= 5 && memcmp(data, "false", 5) == 0) {
        result->type = JSON_BOOL;
        return 0;
    }
    if (data[0] == '{') {
        result->type = JSON_OBJECT;
        // 模拟对象解析
        size_t pos = 1;
        while (pos < size) {
            if (data[pos] == '}') return 0;
            pos++;
        }
        return -1; // 未闭合
    }
    if (data[0] == '[') {
        result->type = JSON_ARRAY;
        size_t pos = 1;
        while (pos < size) {
            if (data[pos] == ']') return 0;
            pos++;
        }
        return -1;
    }
    if (data[0] == '"') {
        result->type = JSON_STRING;
        size_t pos = 1;
        while (pos < size) {
            if (data[pos] == '\\') { pos += 2; continue; }
            if (data[pos] == '"') return 0;
            pos++;
        }
        return -1;
    }
    
    // 数字
    result->type = JSON_NUMBER;
    return 0;
}

// Fuzz Target
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    JsonValue result;
    json_parse(data, size, &result);
    return 0;
}
```

**自定义变异器：**

```c
// custom_mutator.c
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>

// 自定义变异器
size_t LLVMFuzzerCustomMutator(
    uint8_t *data,           // 原始数据（会被修改）
    size_t size,             // 原始大小
    size_t max_size,         // 最大大小
    unsigned int seed        // 随机种子
) {
    // 确保数据是有效的JSON格式
    // 例如：确保以{或[开头，以}或]结尾
    
    if (max_size < 2) return 0;
    
    // 随机选择变异策略
    srand(seed);
    int strategy = rand() % 3;
    
    switch (strategy) {
        case 0: // 替换为合法JSON
            if (max_size >= 4) {
                memcpy(data, "{}", 2);
                return 2;
            }
            break;
        case 1: // 添加嵌套
            if (size + 2 <= max_size) {
                memmove(data + 1, data + 1, size - 1);
                data[0] = '{';
                data[size] = '}';
                return size + 1;
            }
            break;
        case 2: // 随机修改
            if (size > 0) {
                data[rand() % size] = rand() % 256;
                return size;
            }
            break;
    }
    
    return size;
}

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 测试目标
    return 0;
}
```

### 3.3 与Sanitizer配合

libFuzzer与Sanitizer的配合是发现内存安全漏洞的关键。

**Sanitizer类型：**

| Sanitizer | 检测内容 | 编译选项 | 性能开销 |
|-----------|---------|---------|---------|
| ASan | 内存错误（溢出、UAF等） | -fsanitize=address | ~2x |
| MSan | 未初始化内存使用 | -fsanitize=memory | ~3x |
| UBSan | 未定义行为 | -fsanitize=undefined | ~1.2x |
| TSan | 线程数据竞争 | -fsanitize=thread | ~5x |
| CFI | 控制流完整性 | -fsanitize=cfi | ~1.1x |

**编译示例：**

```bash
# ASan + libFuzzer（最常用组合）
clang -g -O1 -fsanitize=fuzzer,address -o fuzz_asan target.c

# MSan + libFuzzer
clang -g -O1 -fsanitize=fuzzer,memory -o fuzz_msan target.c

# UBSan + libFuzzer
clang -g -O1 -fsanitize=fuzzer,undefined -o fuzz_ubsan target.c

# ASan + UBSan + libFuzzer
clang -g -O1 -fsanitize=fuzzer,address,undefined -o fuzz_combined target.c
```

**ASan崩溃报告示例：**

```
==12345==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x602000000018
READ of size 8 at 0x602000000018 thread T0
    #0 0x4f5b28 in parse_data target.c:25:12
    #1 0x4f5c10 in LLVMFuzzerTestOneInput fuzz_target.c:15:5
    #2 0x456789 in fuzzer::Fuzzer::ExecuteCallback fuzzer_loop.cpp:...
    
0x602000000018 is located 0 bytes to the right of 8-byte region [0x602000000010,0x602000000018)
allocated by thread T0 here:
    #0 0x4b6a90 in malloc
    #1 0x4f5a00 in parse_data target.c:20:15

SUMMARY: AddressSanitizer: heap-buffer-overflow
```

---

---

## 📋 内容审核与补充建议

> 针对「libFuzzer使用指南」部分的内容审核结果：

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
