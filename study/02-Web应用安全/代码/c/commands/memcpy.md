# memcpy

> **分类**：内存操作
> **说明**：从源内存复制指定字节数到目标内存
> **头文件**：`<string.h>`

---

## 语法

```c
void *memcpy(void *dest, const void *src, size_t n);
```

## 相关函数

- memset - 设置内存值
- memcmp - 比较内存
- memmove - 安全复制（处理重叠）

## ⚠️ 注意事项

memcpy 不处理内存重叠，重叠时使用 memmove

## 示例代码

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main() {
    // memcpy - 内存复制
    int src[] = {1, 2, 3, 4, 5};
    int dest[5];
    memcpy(dest, src, sizeof(src));

    for (int i = 0; i < 5; i++) {
        printf("%d ", dest[i]);
    }
    printf("\n");

    // 结构体复制
    struct Point { int x; int y; };
    struct Point p1 = {10, 20};
    struct Point p2;
    memcpy(&p2, &p1, sizeof(struct Point));

    // memset - 设置内存
    char buffer[100];
    memset(buffer, 0, sizeof(buffer));    // 清零
    memset(buffer, 'A', 10);             // 前10字节设为 'A'

    // memcmp - 内存比较
    int a[] = {1, 2, 3};
    int b[] = {1, 2, 4};
    int cmp = memcmp(a, b, sizeof(a));
    if (cmp == 0) {
        printf("相等\n");
    } else if (cmp < 0) {
        printf("a < b\n");
    } else {
        printf("a > b\n");
    }

    // memmove - 处理重叠的安全复制
    char arr[] = "abcdef";
    memmove(arr + 2, arr, 4);  // 从arr复制4字节到arr+2
    printf("%s\n", arr);  // "ababcd"

    // 注意：memcpy 在重叠时结果未定义
    // memmove 保证正确处理重叠

    return 0;
}
```
