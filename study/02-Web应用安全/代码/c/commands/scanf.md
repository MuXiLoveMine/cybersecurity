# scanf

> **分类**：输入输出
> **说明**：从标准输入读取格式化数据
> **头文件**：`<stdio.h>`

---

## 语法

```c
int scanf(const char *format, ...);
```

## ⚠️ 注意事项

注意：scanf 存在缓冲区溢出风险，推荐使用 fgets + sscanf

## 示例代码

```c
#include <stdio.h>

int main() {
    // 读取整数
    int age;
    printf("输入年龄: ");
    scanf("%d", &age);  // 注意 & 取地址
    printf("年龄: %d\n", age);

    // 读取浮点数
    float score;
    printf("输入分数: ");
    scanf("%f", &score);

    // 读取字符串（危险！可能溢出）
    char name[50];
    printf("输入名字: ");
    scanf("%49s", name);  // 指定最大宽度，防止溢出

    // 读取多个值
    int x, y;
    printf("输入两个数字: ");
    scanf("%d %d", &x, &y);
    printf("%d + %d = %d\n", x, y, x + y);

    // 安全做法：用 fgets
    char buffer[100];
    printf("输入一行: ");
    fgets(buffer, sizeof(buffer), stdin);
    // 然后用 sscanf 解析
    int num;
    if (sscanf(buffer, "%d", &num) == 1) {
        printf("解析到数字: %d\n", num);
    }

    return 0;
}
```
