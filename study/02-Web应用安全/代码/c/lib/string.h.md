# string.h - C 字符串库

> C 标准库头文件，提供字符串操作函数。也是缓冲区溢出漏洞的高发区。

---

## 一、引入

```c
#include <string.h>
```

---

## 二、常用函数

### 2.1 字符串长度与复制

```c
// strlen - 计算字符串长度（不含结束符 '\0'）
size_t strlen(const char *s);

char *str = "hello";
printf("%zu\n", strlen(str));  // 5

// strcpy - 字符串复制（不安全，可能溢出）
char *strcpy(char *dest, const char *src);

char buf[10];
strcpy(buf, "hello world");  // ❌ 溢出！源串 11 字节 > 目标 10 字节

// strncpy - 指定长度复制（安全但有坑）
char *strncpy(char *dest, const char *src, size_t n);

char buf[10];
strncpy(buf, "hello", sizeof(buf) - 1);  // 复制最多 n 个字节
buf[sizeof(buf) - 1] = '\0';             // ⚠️ 手动加结束符！strncpy 不保证 '\0' 结尾

// strdup - 复制字符串到新分配的内存（POSIX, 非标准 C）
char *strdup(const char *s);
// 需要 free() 释放
char *copy = strdup("hello");
free(copy);
```

### 2.2 字符串拼接

```c
// strcat - 字符串拼接（不安全）
char *strcat(char *dest, const char *src);

char buf[20] = "hello";
strcat(buf, " world");  // "hello world"

// strncat - 指定长度拼接
char *strncat(char *dest, const char *src, size_t n);

char buf[20] = "hello";
strncat(buf, " world", sizeof(buf) - strlen(buf) - 1);
```

### 2.3 字符串比较

```c
// strcmp - 字符串比较
int strcmp(const char *s1, const char *s2);
// 返回值：<0 (s1<s2), =0 (相等), >0 (s1>s2)

if (strcmp("abc", "abc") == 0) {
    printf("相等\n");
}

// strncmp - 比较前 n 个字符
int strncmp(const char *s1, const char *s2, size_t n);

if (strncmp("hello world", "hello", 5) == 0) {
    printf("前5个字符相等\n");
}

// strcasecmp / strncasecmp - 忽略大小写比较（POSIX）
int strcasecmp(const char *s1, const char *s2);
int strncasecmp(const char *s1, const char *s2, size_t n);

strcasecmp("Hello", "hello");  // 0（相等）
```

### 2.4 字符串查找

```c
// strchr - 查找字符（从左往右）
char *strchr(const char *s, int c);

char *p = strchr("hello world", 'l');
printf("%s\n", p);  // "llo world"

// strrchr - 查找字符（从右往左）
char *strrchr(const char *s, int c);

p = strrchr("hello world", 'l');
printf("%s\n", p);  // "ld"

// strstr - 查找子串
char *strstr(const char *haystack, const char *needle);

char *p = strstr("hello world", "world");
printf("%s\n", p);  // "world"

// strpbrk - 查找任一字符
char *strpbrk(const char *s, const char *accept);

p = strpbrk("hello world", "aeiou");
// 找到第一个元音字母 'e'
```

### 2.5 其他常用函数

```c
// memset - 内存设置
void *memset(void *s, int c, size_t n);

char buf[100];
memset(buf, 0, sizeof(buf));      // 清零
memset(buf, 'A', 10);             // 前 10 字节设为 'A'

// memcpy - 内存拷贝
void *memcpy(void *dest, const void *src, size_t n);

int src[5] = {1, 2, 3, 4, 5};
int dest[5];
memcpy(dest, src, sizeof(src));

// memmove - 内存移动（可处理重叠）
void *memmove(void *dest, const void *src, size_t n);

char buf[] = "hello world";
memmove(buf + 2, buf, 5);  // 重叠区域也安全
// memcpy 处理重叠是未定义行为

// memcmp - 内存比较
int memcmp(const void *s1, const void *s2, size_t n);

int a[5] = {1, 2, 3, 4, 5};
int b[5] = {1, 2, 3, 4, 6};
memcmp(a, b, sizeof(a));  // < 0

// memchr - 内存中查找字符
void *memchr(const void *s, int c, size_t n);
```

---

## 三、安全相关内容

### 3.1 缓冲区溢出风险

```c
/*
    危险函数（易导致缓冲区溢出）：
    ❌ strcpy    - 无长度限制的字符串复制
    ❌ strcat    - 无长度限制的字符串拼接
    ❌ sprintf   - 无长度限制的格式化输出
    ❌ gets      - 无限读取（已被移除 C11）
    ❌ scanf("%s") - 无长度限制的输入
    
    安全替代：
    ✅ strncpy   - 但需手动加 '\0'
    ✅ strncat   - 指定长度
    ✅ snprintf  - 指定缓冲区大小
    ✅ fgets     - 指定长度读取
    ✅ strlcpy / strlcat - BSD 扩展，自动加 '\0'（非标准）
*/

// ===== 危险示例 =====
void dangerous_function(char *input) {
    char buffer[64];
    strcpy(buffer, input);  // ❌ 如果 input > 64 字节，溢出！
    printf("%s\n", buffer);
}

// ===== 安全写法 =====
void safe_function(char *input) {
    char buffer[64];
    strncpy(buffer, input, sizeof(buffer) - 1);  // 留一个字节给 '\0'
    buffer[sizeof(buffer) - 1] = '\0';           // ✅ 确保结束符
    printf("%s\n", buffer);
}

// 或使用 snprintf
void safer_function(char *input) {
    char buffer[64];
    snprintf(buffer, sizeof(buffer), "%s", input);  // ✅ 自动截断并加 '\0'
}
```

### 3.2 格式化字符串漏洞

```c
/*
    格式化字符串函数：
    printf, sprintf, fprintf, snprintf, vprintf...
    
    漏洞成因：用户输入作为格式字符串使用
    利用：
    %x  - 读取栈内存
    %s  - 读取字符串（可能崩溃）
    %n  - 写入内存（严重！）
*/

// ===== 危险代码 =====
void vulnerable(char *user_input) {
    printf(user_input);  // ❌ 用户输入作为格式串
}

// 攻击：user_input = "%x.%x.%x.%x" 泄露栈内容
// 攻击：user_input = "%n" 写入内存

// ===== 安全写法 =====
void safe(char *user_input) {
    printf("%s", user_input);  // ✅ 作为参数，不是格式串
}

/*
    %n 说明：
    - %n 不输出任何东西
    - 将已输出的字符数写入对应参数指向的地址
    - 可用于任意地址写，严重漏洞
*/

#include <stdio.h>

void format_string_demo() {
    int count = 0;
    printf("hello%n world\n", &count);
    printf("count = %d\n", count);  // count = 5 ("hello" 的长度)
}
```

### 3.3 off-by-one 漏洞

```c
/*
    off-by-one：只差一个字节的溢出
    常见场景：循环条件错误、长度计算错误
*/

// 示例：错误的循环边界
void off_by_one_example(char *src) {
    char buf[16];
    int i;
    
    // ❌ i <= 15 会写入 16 字节，覆盖 buf[16]（越界）
    for (i = 0; i <= 15; i++) {
        buf[i] = src[i];
    }
    
    // ✅ 正确：i < 15，留最后一字节给 '\0'
    for (i = 0; i < 15; i++) {
        buf[i] = src[i];
    }
    buf[15] = '\0';
}

// strncpy 相关的 off-by-one
void strncpy_pitfall(char *src) {
    char buf[8];
    
    // ❌ 直接用 sizeof(buf)，如果 src >= 8 字节，没有 '\0'
    strncpy(buf, src, sizeof(buf));
    
    // ✅ 正确：sizeof(buf) - 1，然后手动加 '\0'
    strncpy(buf, src, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';
}
```

---

## 四、安全函数对照表

| 危险函数 | 安全替代 | 注意事项 |
|---------|---------|---------|
| `strcpy(d, s)` | `strncpy(d, s, n)` | 需手动加 '\0' |
| `strcat(d, s)` | `strncat(d, s, n)` | n 是最多追加字符数 |
| `sprintf(d, fmt, ...)` | `snprintf(d, n, fmt, ...)` | 返回值是应写入的长度 |
| `gets(buf)` | `fgets(buf, n, stdin)` | fgets 包含换行符 |
| `scanf("%s", buf)` | `scanf("%Ns", buf)` | N 是最大字符数（不含 '\0'） |
| `strlen(s)` | `strnlen_s(s, n)` | C11 可选，指定最大长度 |

---

## 五、内存操作注意事项

| 函数 | 重叠安全 | 用途 |
|------|---------|------|
| `memcpy` | ❌ 不安全 | 不重叠的内存拷贝 |
| `memmove` | ✅ 安全 | 可能重叠的内存拷贝 |
| `memset` | - | 内存初始化/清零 |
| `memcmp` | - | 内存比较 |
| `memchr` | - | 内存查找 |
