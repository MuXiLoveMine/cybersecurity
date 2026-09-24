# pointer

> **分类**：指针操作
> **说明**：指针是存储内存地址的变量，C语言的核心特性

---

## 语法

```c

```

## 基本操作

- & - 取地址运算符
- * - 解引用运算符
- NULL - 空指针
- void* - 通用指针
- 指针 + 整数 - 指针算术
- 指针 - 指针 - 计算距离

## 示例代码

```c
#include <stdio.h>

int main() {
    // 基本指针
    int x = 42;
    int *p = &x;  // p 指向 x 的地址

    printf("x = %d\n", x);           // 42
    printf("&x = %p\n", (void *)&x);  // x的地址
    printf("p = %p\n", (void *)p);    // p的值（x的地址）
    printf("*p = %d\n", *p);          // 42（解引用）

    // 通过指针修改值
    *p = 100;
    printf("x = %d\n", x);  // 100

    // 指针与数组
    int arr[] = {10, 20, 30, 40, 50};
    int *ptr = arr;  // 数组名是首元素地址

    printf("arr[0] = %d\n", *ptr);     // 10
    printf("arr[1] = %d\n", *(ptr+1)); // 20
    printf("arr[2] = %d\n", ptr[2]);   // 30

    // 指针算术
    ptr = arr;
    printf("%d\n", *ptr++);  // 10，然后ptr指向下一个
    printf("%d\n", *ptr);    // 20

    // 多级指针
    int value = 10;
    int *p1 = &value;
    int **p2 = &p1;
    int ***p3 = &p2;

    printf("%d\n", ***p3);  // 10

    // 函数指针
    int add(int a, int b) { return a + b; }
    int (*func_ptr)(int, int) = add;
    printf("%d\n", func_ptr(3, 4));  // 7

    // NULL 指针
    int *np = NULL;
    // *np = 5;  // 错误！解引用空指针会崩溃

    // void 指针（通用指针）
    void *vp = &x;
    int *ip = (int *)vp;  // 需要强制转换才能解引用

    return 0;
}
```
