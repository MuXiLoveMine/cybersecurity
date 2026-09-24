# printf

> **分类**：输入输出
> **说明**：格式化输出到标准输出
> **头文件**：`<stdio.h>`

---

## 语法

```c
int printf(const char *format, ...);
```

## 格式化说明符

- %d - 十进制整数
- %f - 浮点数
- %c - 字符
- %s - 字符串
- %x - 十六进制
- %p - 指针
- %% - 百分号本身

## 示例代码

```c
#include <stdio.h>

int main() {
    // 基本输出
    printf("Hello, World!\n");

    // 整数
    int age = 25;
    printf("年龄: %d\n", age);

    // 浮点数
    float pi = 3.14159;
    printf("π = %.2f\n", pi);  // 保留两位小数

    // 字符和字符串
    char grade = 'A';
    char name[] = "Alice";
    printf("%s 的成绩是 %c\n", name, grade);

    // 十六进制
    int hex_val = 255;
    printf("0x%x  0x%X\n", hex_val, hex_val);  // 0xff  0xFF

    // 宽度和对齐
    printf("%10s\n", "right");   // 右对齐，宽度10
    printf("%-10s\n", "left");   // 左对齐，宽度10
    printf("%05d\n", 42);        // 补零: 00042

    // 多个参数
    printf("%s 今年 %d 岁，身高 %.1fm\n", "Bob", 30, 1.75);

    return 0;
}
```
