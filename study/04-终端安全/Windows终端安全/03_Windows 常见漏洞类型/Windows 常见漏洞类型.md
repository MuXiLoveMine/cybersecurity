# Windows 常见漏洞类型

### 3.1 缓冲区溢出

**原理**

缓冲区溢出是指程序向缓冲区写入数据时超出了缓冲区的大小，导致覆盖了相邻的内存区域。攻击者可以利用这种漏洞覆盖函数返回地址，从而控制程序执行流程。

**栈溢出示例（C 代码）**

```c
#include <stdio.h>
#include <string.h>

void vulnerable_function(char *input) {
    char buffer[64];  // 64字节缓冲区
    strcpy(buffer, input);  // 不安全的字符串复制，无长度检查
}

int main(int argc, char *argv[]) {
    if (argc > 1) {
        vulnerable_function(argv[1]);
    }
    return 0;
}
```

**漏洞分析**

- `strcpy` 函数不检查目标缓冲区大小
- 当输入超过 64 字节时，会覆盖栈上的返回地址
- 攻击者可以构造特定输入，将返回地址指向 shellcode

**内存布局（栈）**

```
高地址
┌───────────────┐
│   返回地址    │  ← 被覆盖
├───────────────┤
│   旧的 EBP    │  ← 可能被覆盖
├───────────────┤
│               │
│   buffer[64]  │  ← 用户输入写入这里
│               │
└───────────────┘
低地址
```

**防护措施**

- 使用安全的字符串函数（`strncpy`、`strlcpy`、`snprintf`）
- 启用编译器安全选项（/GS 栈保护、ASLR、DEP）
- 代码审计和静态分析
- 使用现代编程语言（Rust、Go 等内存安全语言）

**实际案例**：MS08-067 是 Windows Server 服务中的一个经典缓冲区溢出漏洞。攻击者通过向 `NetprPathCanonicalize` 函数发送精心构造的请求，触发栈溢出，从而以 SYSTEM 权限执行任意代码。该漏洞被 Conficker 蠕虫大规模利用。

### 3.2 释放后使用（UAF）

**原理**

释放后使用（Use-After-Free）是指程序在释放内存后仍然使用指向该内存的指针。如果攻击者能够在内存释放后重新分配该内存块并控制其内容，就可以实现任意代码执行。

**UAF 示例（C 代码）**

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    void (*callback)(void);
    int data;
} Object;

Object *global_obj;

void init_object() {
    global_obj = (Object *)malloc(sizeof(Object));
    global_obj->callback = NULL;
    global_obj->data = 0;
}

void free_object() {
    free(global_obj);  // 释放内存
    // 注意：没有将 global_obj 置为 NULL
}

void use_object() {
    if (global_obj->callback) {  // 释放后仍使用指针
        global_obj->callback();  // 调用虚函数/回调
    }
}

int main() {
    init_object();
    free_object();  // 释放对象
    // ... 攻击者在此期间分配内存覆盖 global_obj 指向的区域
    use_object();   // 触发 UAF
    return 0;
}
```

**漏洞分析**

- `free_object` 释放了 `global_obj` 指向的内存
- 但没有将指针置为 NULL
- `use_object` 仍然使用该指针
- 如果攻击者能在释放和使用之间重新分配并控制该内存，就可以控制 `callback` 函数指针

**UAF 利用步骤**

1. 创建一个包含虚函数指针的对象
2. 释放该对象（但指针未置空）
3. 攻击者分配相同大小的内存，覆盖虚函数指针
4. 程序调用虚函数时，执行攻击者控制的代码

**防护措施**

- 释放内存后将指针置为 NULL
- 使用智能指针（C++ shared_ptr/unique_ptr）
- 使用内存安全语言
- 启用堆保护机制（Heap Cookie、DEP、ASLR）

**实际案例**：CVE-2021-31956 是 Windows 内核中的一个 UAF 漏洞，存在于 win32k.sys 驱动中。攻击者可以通过创建和操作特定的窗口对象触发 UAF，从而实现本地权限提升。该漏洞在野被积极利用。

### 3.3 整数溢出

**原理**

整数溢出是指当算术运算的结果超出了整数类型所能表示的范围时发生的溢出。这可能导致意外的行为，例如分配过少的内存，进而导致缓冲区溢出。

**整数溢出示例（C 代码）**

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void vulnerable_copy(int count, char *input) {
    // 整数溢出：count * sizeof(int) 可能溢出
    int size = count * sizeof(int);
    int *buffer = (int *)malloc(size);
    
    if (buffer == NULL) return;
    
    // 实际复制 count * sizeof(int) 字节到 buffer
    // 如果 size 溢出（变成很小的数），malloc 分配的内存不够
    memcpy(buffer, input, count * sizeof(int));
    
    free(buffer);
}

int main() {
    // count = 0x40000001 (1073741825)
    // count * 4 = 0x100000004 → 32位溢出后为 4
    // malloc(4) 只分配4字节，但 memcpy 复制大量数据 → 堆溢出
    return 0;
}
```

**整数溢出类型**

1. **有符号整数溢出**：有符号整数超出表示范围（undefined behavior）
2. **无符号整数回绕**：无符号整数超出表示范围（定义为模运算）
3. **截断**：将大整数赋值给小整数类型
4. **符号扩展**：有符号整数向更宽类型转换时符号位扩展

**整数溢出检测**

```c
// 安全的整数加法检查
int safe_add(int a, int b, int *result) {
    if ((b > 0 && a > INT_MAX - b) ||
        (b < 0 && a < INT_MIN - b)) {
        return -1;  // 溢出
    }
    *result = a + b;
    return 0;
}

// 安全的整数乘法检查
int safe_mul(int a, int b, int *result) {
    if (a == 0 || b == 0) {
        *result = 0;
        return 0;
    }
    if (a > 0) {
        if (b > 0) {
            if (a > INT_MAX / b) return -1;
        } else {
            if (b < INT_MIN / a) return -1;
        }
    } else {
        if (b > 0) {
            if (a < INT_MIN / b) return -1;
        } else {
            if (b != 0 && a < INT_MAX / b) return -1;
        }
    }
    *result = a * b;
    return 0;
}
```

**防护措施**

- 在进行算术运算前检查边界
- 使用安全整数库（如 SafeInt）
- 编译器警告和静态分析
- 代码审计

---

---

