# strcpy

> **分类**：字符串操作
> **说明**：复制字符串（注意：不安全，可能溢出）
> **头文件**：`<string.h>`

---

## 语法

```c
char *strcpy(char *dest, const char *src);
```

## 相关函数

- strncpy - 安全版本（指定长度）
- strlen - 字符串长度
- strcmp - 字符串比较
- strcat - 字符串拼接
- strstr - 查找子串

## ⚠️ 注意事项

危险函数！没有长度检查，容易导致缓冲区溢出。推荐使用 strncpy。

## 示例代码

```c
#include <stdio.h>
#include <string.h>

int main() {
    char src[] = "Hello, World!";
    char dest[50];

    // strcpy（危险！不检查目标大小）
    strcpy(dest, src);
    printf("复制后: %s\n", dest);

    // strncpy（安全版本）
    char safe_dest[20];
    strncpy(safe_dest, src, sizeof(safe_dest) - 1);
    safe_dest[sizeof(safe_dest) - 1] = '\0';  // 手动确保终止

    // 字符串长度
    printf("长度: %zu\n", strlen(src));  // 13

    // 字符串比较
    if (strcmp(src, dest) == 0) {
        printf("字符串相等\n");
    }

    // 字符串拼接
    char buffer[100] = "Hello, ";
    strcat(buffer, "World!");  // 危险！
    printf("%s\n", buffer);

    // 安全拼接
    char safe_buf[100] = "Hello, ";
    strncat(safe_buf, "World!", sizeof(safe_buf) - strlen(safe_buf) - 1);

    // 查找子串
    char *found = strstr(src, "World");
    if (found) {
        printf("找到: %s\n", found);  // "World!"
    }

    // 查找字符
    char *p = strchr(src, 'W');
    if (p) {
        printf("W 在位置: %ld\n", p - src);
    }

    return 0;
}
```
