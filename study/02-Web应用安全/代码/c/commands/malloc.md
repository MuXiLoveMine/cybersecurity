# malloc

> **分类**：内存管理
> **说明**：动态分配指定大小的堆内存
> **头文件**：`<stdlib.h>`

---

## 语法

```c
void *malloc(size_t size);
```

## 相关函数

- free - 释放内存
- calloc - 分配并清零
- realloc - 重新分配

## 示例代码

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    // 分配内存
    int *arr = (int *)malloc(10 * sizeof(int));
    if (arr == NULL) {
        printf("内存分配失败！\n");
        return 1;
    }

    // 使用内存
    for (int i = 0; i < 10; i++) {
        arr[i] = i * i;
    }

    // 打印
    for (int i = 0; i < 10; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");

    // 重新分配（扩容）
    int *new_arr = (int *)realloc(arr, 20 * sizeof(int));
    if (new_arr != NULL) {
        arr = new_arr;
        // 新内存可以使用到第20个元素
    }

    // 释放内存
    free(arr);
    arr = NULL;  // 避免野指针

    // calloc：分配并初始化为0
    int *zero_arr = (int *)calloc(5, sizeof(int));
    // 所有元素都是0
    free(zero_arr);

    // 字符串动态分配
    char *str = (char *)malloc(100);
    strcpy(str, "Hello");
    free(str);

    return 0;
}
```
