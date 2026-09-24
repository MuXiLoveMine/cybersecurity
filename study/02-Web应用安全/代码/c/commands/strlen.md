# strlen

> **分类**：字符串操作
> **说明**：返回字符串的长度（不包括终止符）
> **头文件**：`<string.h>`

---

## 语法

```c
size_t strlen(const char *s);
```

## 示例代码

```c
#include <stdio.h>
#include <string.h>

int main() {
    char str[] = "Hello, World!";

    // 基本用法
    size_t len = strlen(str);
    printf("字符串: '%s'\n", str);
    printf("长度: %zu\n", len);  // 13

    // 空字符串
    char empty[] = "";
    printf("空串长度: %zu\n", strlen(empty));  // 0

    // 注意：strlen 不包括结尾的 \0
    char s[100] = "test";
    printf("字符串长度: %zu\n", strlen(s));     // 4
    printf("数组大小: %zu\n", sizeof(s));      // 100

    // 常见用法：拼接前检查空间
    char dest[50] = "Hello";
    char src[] = ", World!";
    if (strlen(dest) + strlen(src) < sizeof(dest)) {
        strcat(dest, src);
    }

    // 实现原理（简单版）
    size_t my_strlen(const char *s) {
        const char *p = s;
        while (*p != '\0') p++;
        return p - s;
    }

    return 0;
}
```
