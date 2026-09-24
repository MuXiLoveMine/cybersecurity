# C 语言基础

## 目录

1. [C 语言概述](#1-c-语言概述)
2. [环境配置与编译](#2-环境配置与编译)
3. [数据类型](#3-数据类型)
4. [运算符](#4-运算符)
5. [控制流](#5-控制流)
6. [函数](#6-函数)
7. [数组](#7-数组)
8. [指针](#8-指针)
9. [字符串](#9-字符串)
10. [结构体与联合体](#10-结构体与联合体)
11. [文件操作](#11-文件操作)
12. [内存管理](#12-内存管理)
13. [编译与调试](#13-编译与调试)
14. [安全编程要点](#14-安全编程要点)

---

## 1. C 语言概述

### 1.1 历史

- **C 语言**：1972 年由 **Dennis Ritchie** 在贝尔实验室设计，用于重写 UNIX 操作系统。
- 前身是 B 语言（Ken Thompson 设计），C 语言在 B 语言基础上增加了数据类型和更丰富的功能。
- **标准演进**：
  - K&R C（1978）：第一版标准，由 Brian Kernighan 和 Dennis Ritchie 合著的《C程序设计语言》定义
  - C89 / ANSI C（1989）：第一个正式标准
  - C99（1999）：增加了 inline、复数、可变长度数组等
  - C11（2011）：增加了多线程、原子操作、静态断言等
  - C17 / C18（2018）：技术修订
  - C23（2023）：最新标准

### 1.2 特点

| 特点 | 说明 |
|------|------|
| **高效** | 直接编译为机器码，执行效率高，接近汇编 |
| **底层能力** | 可直接操作内存、硬件、寄存器 |
| **手动内存管理** | 需要程序员自行管理堆内存（malloc/free） |
| **结构化编程** | 支持函数、模块化设计 |
| **跨平台** | 源码级跨平台，需在各平台重新编译 |
| **指针** | 强大而危险的特性，是 C 语言的灵魂 |
| **标准库精简** | 核心库较小，功能相对基础 |

### 1.3 C 语言与安全

C 语言是网络安全领域最重要的编程语言之一，原因如下：

- **操作系统底层**：Windows、Linux、macOS 内核均由 C 编写
- **逆向分析**：大量软件（尤其是恶意软件）由 C 编译，逆向工程师需要理解 C 代码对应的汇编
- **漏洞挖掘**：内存安全漏洞（缓冲区溢出、Use-After-Free、整数溢出等）主要存在于 C 程序中
- **Exploit 开发**：Shellcode、ROP 链、内存破坏利用均需要深入理解 C 内存模型
- **安全工具开发**：调试器、反汇编器、Fuzzer 常用 C 开发

### 1.4 第一个 C 程序

```c
#include <stdio.h>

int main() {
    printf("Hello, World!\n");
    return 0;
}
```

**代码说明：**
- `#include <stdio.h>`：包含标准输入输出头文件，提供 `printf` 等函数
- `int main()`：主函数，程序入口点
- `printf(...)`：格式化输出函数，`\n` 表示换行
- `return 0`：返回 0 表示程序正常退出

---

## 2. 环境配置与编译

### 2.1 Windows 平台

#### MinGW（GCC 的 Windows 版本）

1. 下载 MinGW-w64：https://www.mingw-w64.org/
2. 安装后将 `bin` 目录加入系统 PATH
3. 验证：打开 cmd，输入 `gcc --version`

#### Visual Studio

1. 下载 Visual Studio Community（免费）
2. 安装 "使用 C++ 的桌面开发" 工作负载
3. 使用 "x86 Native Tools Command Prompt" 编译

### 2.2 Linux 平台

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential
gcc --version

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
```

### 2.3 编译运行

```bash
# 编译 C 程序
gcc hello.c -o hello

# 启用所有警告和调试信息
gcc -Wall -g hello.c -o hello

# 指定 C 标准
gcc -std=c11 hello.c -o hello

# 优化级别（O0~O3）
gcc -O2 hello.c -o hello

# 运行
./hello          # Linux/Mac
hello.exe        # Windows
```

### 2.4 编译过程

C 程序的编译分为四个阶段：

```
源代码(.c) → 预处理 → 编译 → 汇编 → 链接 → 可执行文件
```

1. **预处理（Preprocessing）**：处理 `#include`、`#define`、`#ifdef` 等指令
2. **编译（Compilation）**：将 C 代码编译为汇编代码
3. **汇编（Assembly）**：将汇编代码汇编为目标文件（.o / .obj）
4. **链接（Linking）**：将多个目标文件和库链接成可执行文件

```bash
# 查看各阶段输出
gcc -E hello.c -o hello.i    # 预处理结果
gcc -S hello.c -o hello.s    # 汇编代码
gcc -c hello.c -o hello.o    # 目标文件
gcc hello.o -o hello         # 链接为可执行文件
```

---

## 3. 数据类型

### 3.1 基本数据类型

| 类型 | 大小（典型） | 范围 | 说明 |
|------|-------------|------|------|
| `char` | 1 字节 | -128 ~ 127 | 字符型 |
| `unsigned char` | 1 字节 | 0 ~ 255 | 无符号字符 |
| `short` | 2 字节 | -32768 ~ 32767 | 短整型 |
| `unsigned short` | 2 字节 | 0 ~ 65535 | 无符号短整型 |
| `int` | 4 字节 | -2^31 ~ 2^31-1 | 整型 |
| `unsigned int` | 4 字节 | 0 ~ 2^32-1 | 无符号整型 |
| `long` | 4/8 字节 | 平台相关 | 长整型 |
| `unsigned long` | 4/8 字节 | 平台相关 | 无符号长整型 |
| `long long` | 8 字节 | -2^63 ~ 2^63-1 | 长长整型 |
| `unsigned long long` | 8 字节 | 0 ~ 2^64-1 | 无符号长长整型 |
| `float` | 4 字节 | ~6-7 位有效数字 | 单精度浮点 |
| `double` | 8 字节 | ~15-16 位有效数字 | 双精度浮点 |
| `long double` | 8/10/16 字节 | 平台相关 | 扩展精度浮点 |

> 注意：C 标准只规定了类型的最小范围，实际大小由平台和编译器决定。使用 `sizeof` 查看实际大小。

### 3.2 类型限定符

```c
const int MAX = 100;        // 常量，不能修改
volatile int flag;          // 易变变量，告诉编译器不要优化
static int count = 0;       // 静态变量，生命周期延长
register int i;             // 寄存器变量（建议放入寄存器）
```

### 3.3 类型转换

```c
// 隐式转换（自动进行）
int i = 10;
double d = i;       // int → double，自动提升

// 显式转换（强制类型转换）
double x = 3.14;
int y = (int)x;     // double → int，截断小数部分

// 注意整数提升和类型转换的安全问题
unsigned int a = 10;
int b = -20;
if (a + b > 0) {    // 危险！b 被隐式转换为 unsigned int
    printf("大于0\n");  // 会输出这个！
}
```

### 3.4 sizeof 运算符

```c
#include <stdio.h>

int main() {
    printf("char:     %zu 字节\n", sizeof(char));
    printf("int:      %zu 字节\n", sizeof(int));
    printf("long:     %zu 字节\n", sizeof(long));
    printf("float:    %zu 字节\n", sizeof(float));
    printf("double:   %zu 字节\n", sizeof(double));

    int arr[10];
    printf("int[10]:  %zu 字节\n", sizeof(arr));
    printf("数组长度:  %zu\n", sizeof(arr) / sizeof(arr[0]));

    return 0;
}
```

### 3.5 安全要点

- **整数溢出**：有符号整数溢出是未定义行为，无符号整数溢出会回绕
- **符号不匹配**：有符号和无符号混合运算时，有符号会被转换为无符号
- **截断风险**：从大类型转换为小类型可能丢失数据
- **浮点精度**：浮点数存在精度误差，不要直接比较是否相等

---

## 4. 运算符

### 4.1 算术运算符

| 运算符 | 含义 | 示例 | 结果 |
|--------|------|------|------|
| `+` | 加法 | `10 + 3` | 13 |
| `-` | 减法 | `10 - 3` | 7 |
| `*` | 乘法 | `10 * 3` | 30 |
| `/` | 除法 | `10 / 3` | 3（整数除法） |
| `%` | 取余 | `10 % 3` | 1 |
| `++` | 自增 | `x++` / `++x` | x 加 1 |
| `--` | 自减 | `x--` / `--x` | x 减 1 |

```c
int a = 10, b = 3;
printf("%d + %d = %d\n", a, b, a + b);
printf("%d / %d = %d\n", a, b, a / b);   // 整数除法，截断小数
printf("%d %% %d = %d\n", a, b, a % b);  // 取余

// 自增的前后区别
int x = 5;
printf("x++ = %d, x = %d\n", x++, x);  // 后自增：先取值后加
x = 5;
printf("++x = %d, x = %d\n", ++x, x);  // 前自增：先加后取值
```

### 4.2 关系运算符

| 运算符 | 含义 | 示例 |
|--------|------|------|
| `==` | 等于 | `a == b` |
| `!=` | 不等于 | `a != b` |
| `>` | 大于 | `a > b` |
| `<` | 小于 | `a < b` |
| `>=` | 大于等于 | `a >= b` |
| `<=` | 小于等于 | `a <= b` |

> C 语言中没有布尔类型（C99 之前），关系运算结果为 `int`：**0 表示假，非 0 表示真**。

### 4.3 逻辑运算符

| 运算符 | 含义 | 说明 |
|--------|------|------|
| `&&` | 逻辑与 | 两边都为真才为真（短路） |
| `\|\|` | 逻辑或 | 一边为真就为真（短路） |
| `!` | 逻辑非 | 取反 |

```c
int a = 1, b = 0;
printf("a && b = %d\n", a && b);  // 0
printf("a || b = %d\n", a || b);  // 1
printf("!a = %d\n", !a);          // 0

// 短路特性
int x = 0;
if (x != 0 && 10 / x > 1) {  // 不会执行 10/x，因为 x!=0 已经为假
    printf("不会执行\n");
}
```

### 4.4 位运算符

| 运算符 | 含义 | 示例（a=6=0110, b=3=0011） |
|--------|------|------|
| `&` | 按位与 | `a & b = 0010 = 2` |
| `\|` | 按位或 | `a \| b = 0111 = 7` |
| `^` | 按位异或 | `a ^ b = 0101 = 5` |
| `~` | 按位取反 | `~a = 1001...` |
| `<<` | 左移 | `a << 1 = 1100 = 12` |
| `>>` | 右移 | `a >> 1 = 0011 = 3` |

```c
unsigned char a = 6;   // 00000110
unsigned char b = 3;   // 00000011

printf("a & b = %d\n", a & b);   // 2
printf("a | b = %d\n", a | b);   // 7
printf("a ^ b = %d\n", a ^ b);   // 5
printf("a << 1 = %d\n", a << 1); // 12
printf("a >> 1 = %d\n", a >> 1); // 3
```

### 4.5 赋值运算符

| 运算符 | 示例 | 等价于 |
|--------|------|--------|
| `=` | `a = 10` | - |
| `+=` | `a += 5` | `a = a + 5` |
| `-=` | `a -= 5` | `a = a - 5` |
| `*=` | `a *= 5` | `a = a * 5` |
| `/=` | `a /= 5` | `a = a / 5` |
| `%=` | `a %= 5` | `a = a % 5` |
| `&=` | `a &= 5` | `a = a & 5` |
| `\|=` | `a \|= 5` | `a = a \| 5` |
| `^=` | `a ^= 5` | `a = a ^ 5` |
| `<<=` | `a <<= 2` | `a = a << 2` |
| `>>=` | `a >>= 2` | `a = a >> 2` |

### 4.6 其他运算符

```c
// 三目运算符（条件运算符）
int score = 85;
char *result = (score >= 60) ? "及格" : "不及格";

// sizeof 运算符
size_t s = sizeof(int);

// 逗号运算符
int x = (1 + 2, 3 + 4);  // x = 7，取最后一个表达式的值

// 取地址和解引用
int a = 10;
int *p = &a;     // & 取地址
int b = *p;      // * 解引用
```

### 4.7 运算符优先级

优先级从高到低（部分）：

1. `()` `[]` `->` `.`
2. `!` `~` `++` `--` `*` `&` `sizeof` （一元运算符）
3. `*` `/` `%` （乘除模）
4. `+` `-` （加减）
5. `<<` `>>` （位移）
6. `<` `<=` `>` `>=` （关系）
7. `==` `!=` （相等）
8. `&` （按位与）
9. `^` （按位异或）
10. `|` （按位或）
11. `&&` （逻辑与）
12. `||` （逻辑或）
13. `?:` （三目）
14. `=` `+=` `-=` 等（赋值）

> 不确定优先级时，**使用括号**是最佳实践。

---

## 5. 控制流

### 5.1 if 语句

```c
if (条件) {
    // 条件为真时执行
}

if (条件) {
    // 条件为真
} else {
    // 条件为假
}

if (条件1) {
    // ...
} else if (条件2) {
    // ...
} else if (条件3) {
    // ...
} else {
    // ...
}
```

**示例：**

```c
int score = 85;

if (score >= 90) {
    printf("优秀\n");
} else if (score >= 80) {
    printf("良好\n");
} else if (score >= 60) {
    printf("及格\n");
} else {
    printf("不及格\n");
}
```

### 5.2 switch 语句

```c
switch (表达式) {
    case 常量1:
        // 语句
        break;
    case 常量2:
        // 语句
        break;
    default:
        // 默认情况
        break;
}
```

**注意：**
- `switch` 的表达式必须是整型（int、char、enum 等）
- `case` 标签必须是常量表达式
- 不加 `break` 会发生**穿透**（fall-through），继续执行后续 case

```c
int day = 3;
switch (day) {
    case 1: printf("星期一\n"); break;
    case 2: printf("星期二\n"); break;
    case 3: printf("星期三\n"); break;
    // ...
    default: printf("无效\n"); break;
}
```

### 5.3 while 循环

```c
while (条件) {
    // 循环体，条件为真时重复执行
}
```

```c
int i = 1, sum = 0;
while (i <= 100) {
    sum += i;
    i++;
}
printf("1到100的和 = %d\n", sum);
```

### 5.4 do-while 循环

```c
do {
    // 循环体（至少执行一次）
} while (条件);
```

> do-while 与 while 的区别：do-while **至少执行一次**循环体。

### 5.5 for 循环

```c
for (初始化; 条件; 更新) {
    // 循环体
}
```

```c
// 计算 1 到 100 的和
int sum = 0;
for (int i = 1; i <= 100; i++) {
    sum += i;
}
```

**嵌套 for 循环：**

```c
// 九九乘法表
for (int i = 1; i <= 9; i++) {
    for (int j = 1; j <= i; j++) {
        printf("%d*%d=%-3d", j, i, i * j);
    }
    printf("\n");
}
```

### 5.6 break 与 continue

- **break**：跳出当前循环（或 switch）
- **continue**：跳过本次循环，继续下一次

```c
for (int i = 1; i <= 10; i++) {
    if (i == 5) break;      // 遇到 5 跳出循环
    printf("%d ", i);
}
// 输出: 1 2 3 4

for (int i = 1; i <= 10; i++) {
    if (i % 2 == 0) continue;  // 偶数跳过
    printf("%d ", i);
}
// 输出: 1 3 5 7 9
```

### 5.7 goto 语句

```c
goto 标签;

// ...

标签:
    // 语句
```

> `goto` 可以跳转到同一函数内的任意标签处。虽然备受争议，但在**错误处理和资源清理**场景下非常实用。

```c
int func() {
    int *p1 = NULL, *p2 = NULL;
    int ret = -1;

    p1 = malloc(100);
    if (p1 == NULL) goto cleanup;

    p2 = malloc(100);
    if (p2 == NULL) goto cleanup;

    // 正常操作...
    ret = 0;

cleanup:
    if (p2) free(p2);
    if (p1) free(p1);
    return ret;
}
```

---

## 6. 函数

### 6.1 函数定义与声明

**函数定义：**

```c
返回类型 函数名(参数列表) {
    // 函数体
    return 返回值;
}
```

**示例：**

```c
// 求两个整数的最大值
int max(int a, int b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}
```

**函数声明（原型）：**

```c
// 函数声明，告诉编译器函数的存在
int max(int a, int b);

// 也可以只写类型
int max(int, int);
```

> 函数在使用之前必须声明或定义。通常把声明放在头文件（.h）中，定义放在源文件（.c）中。

### 6.2 函数调用

```c
#include <stdio.h>

int add(int a, int b);  // 函数声明

int main() {
    int result = add(3, 5);  // 函数调用
    printf("3 + 5 = %d\n", result);
    return 0;
}

int add(int a, int b) {   // 函数定义
    return a + b;
}
```

### 6.3 参数传递

#### 值传递

```c
void swap(int a, int b) {
    int temp = a;
    a = b;
    b = temp;
}

int main() {
    int x = 10, y = 20;
    swap(x, y);  // 不会交换 x 和 y！因为传递的是值的副本
    printf("x=%d, y=%d\n", x, y);  // x=10, y=20
    return 0;
}
```

#### 地址传递（指针）

```c
void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int main() {
    int x = 10, y = 20;
    swap(&x, &y);  // 传入地址，可以修改原值
    printf("x=%d, y=%d\n", x, y);  // x=20, y=10
    return 0;
}
```

#### 数组作为参数

数组作为函数参数时，会**退化为指针**，丢失长度信息。

```c
// 这三种写法完全等价，都是指针
void func(int arr[]);
void func(int arr[10]);  // 10 被忽略
void func(int *arr);

// 正确做法：同时传递数组长度
int sum_array(int arr[], int size) {
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += arr[i];
    }
    return sum;
}
```

### 6.4 递归

函数自己调用自己，称为递归。

```c
// 计算阶乘
int factorial(int n) {
    if (n <= 1) {
        return 1;          // 终止条件（基线条件）
    }
    return n * factorial(n - 1);  // 递归调用
}
```

**递归的要素：**
1. **基线条件（Base Case）**：递归终止的条件
2. **递归步骤**：将问题分解为更小的子问题

> 递归深度过大会导致**栈溢出**（Stack Overflow）。

### 6.5 函数指针

函数指针是指向函数的指针。

```c
// 声明一个函数指针变量，指向返回 int、参数为两个 int 的函数
int (*func_ptr)(int, int);

int add(int a, int b) { return a + b; }
int max(int a, int b) { return a > b ? a : b; }

int main() {
    func_ptr = add;
    printf("%d\n", func_ptr(3, 4));  // 7

    func_ptr = max;
    printf("%d\n", func_ptr(3, 4));  // 4

    return 0;
}
```

**函数指针的用途：**
- 回调函数
- 函数表（跳转表）
- 动态库函数调用

### 6.6 作用域与存储类别

| 类别 | 关键字 | 作用域 | 生命周期 |
|------|--------|--------|----------|
| 局部变量 | auto（默认） | 函数/块内 | 进入块时创建，退出时销毁 |
| 静态局部变量 | static | 函数/块内 | 程序整个运行期间 |
| 全局变量 | - | 整个文件及其他文件 | 程序整个运行期间 |
| 静态全局变量 | static | 当前文件 | 程序整个运行期间 |
| 外部全局变量 | extern | 所有文件 | 程序整个运行期间 |

```c
int global_var = 100;    // 全局变量，所有函数都可访问
static int file_var = 50; // 静态全局变量，仅当前文件可访问

void test() {
    int local = 10;          // 局部变量
    static int count = 0;    // 静态局部变量，只初始化一次
    count++;
    printf("count = %d\n", count);
}
```

---

## 7. 数组

### 7.1 一维数组

```c
// 声明：类型 数组名[大小];
int nums[10];

// 初始化
int arr1[5] = {1, 2, 3, 4, 5};   // 全部初始化
int arr2[5] = {1, 2, 3};          // 部分初始化，剩余为 0
int arr3[5] = {0};                // 全部初始化为 0
int arr4[] = {1, 2, 3, 4};        // 由初始化列表确定大小（4个元素）

// 访问元素（下标从 0 开始）
arr1[0] = 100;
printf("%d\n", arr1[2]);  // 3
```

**数组遍历：**

```c
int arr[] = {10, 20, 30, 40, 50};
int len = sizeof(arr) / sizeof(arr[0]);  // 计算数组长度

for (int i = 0; i < len; i++) {
    printf("%d ", arr[i]);
}
```

### 7.2 二维数组

```c
// 声明：类型 数组名[行数][列数];
int matrix[3][4];

// 初始化
int mat[3][4] = {
    {1, 2, 3, 4},
    {5, 6, 7, 8},
    {9, 10, 11, 12}
};

// 访问
printf("%d\n", mat[1][2]);  // 第2行第3列 = 7

// 遍历
for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 4; j++) {
        printf("%3d ", mat[i][j]);
    }
    printf("\n");
}
```

> 二维数组在内存中是**连续存储**的，按**行优先**顺序排列。

### 7.3 数组与指针

数组名是指向数组首元素的**常量指针**（不能修改其指向）。

```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr;   // p 指向 arr[0]

// 以下等价
printf("%d\n", arr[0]);   // 10
printf("%d\n", *arr);     // 10
printf("%d\n", *p);       // 10

printf("%d\n", arr[2]);   // 30
printf("%d\n", *(arr+2)); // 30
printf("%d\n", p[2]);     // 30
```

**指针运算：**

```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr;

printf("%p -> %d\n", (void *)p, *p);
p++;  // 指向下一个元素（地址增加 sizeof(int)）
printf("%p -> %d\n", (void *)p, *p);
```

### 7.4 字符数组

字符数组用于存储字符串，以 `'\0'`（空字符，ASCII 码为 0）结尾。

```c
char str1[10] = "Hello";     // 自动添加 '\0'
char str2[] = "World";       // 大小由编译器确定（6 字节，含 '\0'）
char str3[6] = {'H','e','l','l','o','\0'};  // 手动添加
```

> 注意：`"Hello"` 占 6 字节（5 个字符 + 1 个结束符）。

### 7.5 安全要点

- **数组越界**：C 语言不检查数组下标是否越界，越界访问会导致未定义行为
- **缓冲区溢出**：向数组写入超过其大小的数据，可能覆盖栈上的返回地址
- **数组退化为指针**：作为函数参数时，数组会退化为指针，丢失长度信息
- **变长数组（VLA）**：C99 支持用变量作为数组大小，但可能导致栈溢出

---

## 8. 指针

### 8.1 指针基础

指针是存储**内存地址**的变量。

```c
int x = 42;
int *p;      // 声明一个指向 int 的指针
p = &x;      // & 取地址，将 x 的地址赋给 p

printf("x 的值 = %d\n", x);
printf("x 的地址 = %p\n", (void *)&x);
printf("p 的值 = %p\n", (void *)p);
printf("*p 的值 = %d\n", *p);  // * 解引用，取 p 指向的值

*p = 100;   // 通过指针修改 x 的值
printf("x = %d\n", x);  // 100
```

### 8.2 指针的大小

所有指针的大小都相同，因为存储的都是内存地址。

```c
printf("int*:    %zu 字节\n", sizeof(int *));
printf("char*:   %zu 字节\n", sizeof(char *));
printf("double*: %zu 字节\n", sizeof(double *));
printf("void*:   %zu 字节\n", sizeof(void *));

// 32 位系统：4 字节
// 64 位系统：8 字节
```

### 8.3 指针与数组

```c
int arr[5] = {1, 2, 3, 4, 5};
int *p = arr;

// 用指针遍历数组
for (int i = 0; i < 5; i++) {
    printf("%d ", *(p + i));
}

// 指针自增遍历
int *q = arr;
while (q < arr + 5) {
    printf("%d ", *q);
    q++;
}
```

### 8.4 二级指针

指向指针的指针。

```c
int x = 10;
int *p = &x;    // 一级指针
int **pp = &p;  // 二级指针

printf("x = %d\n", x);
printf("*p = %d\n", *p);
printf("**pp = %d\n", **pp);
```

**用途：**
- 动态分配二维数组
- 修改函数参数中的指针（指针的指针传递）

```c
// 函数中修改指针本身
void allocate(int **p, int size) {
    *p = malloc(size * sizeof(int));
}

int main() {
    int *arr = NULL;
    allocate(&arr, 10);  // 传入指针的地址
    // arr 现在指向分配的内存
    free(arr);
    return 0;
}
```

### 8.5 指针数组

数组的每个元素都是指针。

```c
char *names[4] = {
    "Alice",
    "Bob",
    "Charlie",
    "David"
};

for (int i = 0; i < 4; i++) {
    printf("%s\n", names[i]);
}
```

### 8.6 数组指针

指向数组的指针（注意与指针数组的区别）。

```c
int arr[2][3] = {{1, 2, 3}, {4, 5, 6}};
int (*p)[3];  // 指向包含 3 个 int 的数组的指针

p = arr;
printf("%d\n", p[0][0]);  // 1
printf("%d\n", p[1][2]);  // 6
```

### 8.7 空指针与野指针

| 概念 | 说明 | 危害 |
|------|------|------|
| **空指针** | 值为 `NULL`（0），不指向任何有效地址 | 解引用会导致程序崩溃（段错误） |
| **野指针** | 未初始化或指向已释放内存的指针 | 行为不可预测，可能读取垃圾数据或崩溃 |
| **悬空指针** | 指向已释放内存的指针（Use-After-Free） | 安全漏洞，可能被利用 |

```c
int *p = NULL;    // 空指针
// *p = 10;       // 错误！空指针解引用

int *q;           // 野指针（未初始化，值是随机的）
// *q = 10;       // 错误！

int *r = malloc(sizeof(int));
free(r);
// *r = 10;       // 错误！Use-After-Free（悬空指针）
r = NULL;         // 释放后置 NULL 是好习惯
```

### 8.8 void 指针

`void *` 是通用指针类型，可以指向任何类型的数据。

```c
void *vp;
int x = 10;
double y = 3.14;

vp = &x;     // 可以指向 int
vp = &y;     // 也可以指向 double

// void* 不能直接解引用，需要强制类型转换
printf("%d\n", *(int *)vp);
```

### 8.9 安全要点

- **空指针检查**：使用指针前检查是否为 NULL
- **避免野指针**：声明时初始化，释放后置 NULL
- **指针越界**：确保指针操作不超过分配的内存范围
- **Use-After-Free**：释放后不再访问内存
- **Double-Free**：不要对同一块内存释放两次
- **未初始化指针**：永远不要使用未初始化的指针

---

## 9. 字符串

### 9.1 字符串基础

C 语言中，字符串是以 `'\0'` 结尾的字符数组。

```c
// 几种字符串的定义方式
char str1[] = "Hello";           // 字符数组，可修改
char *str2 = "Hello";            // 字符指针，指向字符串常量（只读）
char str3[6] = {'H','e','l','l','o','\0'};  // 手动初始化

printf("%s\n", str1);  // 用 %s 输出字符串
```

**重要区别：**

| 形式 | 存储位置 | 是否可修改 |
|------|----------|------------|
| `char str[] = "Hello"` | 栈（局部变量）或全局数据区 | 可修改 |
| `char *str = "Hello"` | 字符串常量区（只读） | 不可修改 |

### 9.2 字符串输入输出

```c
#include <stdio.h>

int main() {
    char name[50];

    // scanf 读取（遇到空格、换行结束）
    printf("请输入名字：");
    scanf("%s", name);
    printf("你好，%s\n", name);

    // fgets 读取一行（安全，可读取空格）
    char line[100];
    printf("请输入一行：");
    getchar();  // 吸收换行
    fgets(line, sizeof(line), stdin);
    printf("你输入的是：%s", line);

    // puts 输出（自动换行）
    puts("Hello World");

    return 0;
}
```

> **永远不要使用 `gets()`**，它没有边界检查，一定会导致缓冲区溢出。

### 9.3 字符串库函数

需要包含 `<string.h>` 头文件。

| 函数 | 作用 | 安全性 |
|------|------|--------|
| `strlen(s)` | 计算字符串长度（不含 '\0'） | 安全 |
| `strcpy(dest, src)` | 复制字符串 | 不安全 |
| `strncpy(dest, src, n)` | 最多复制 n 个字符 | 较安全 |
| `strcat(dest, src)` | 拼接字符串 | 不安全 |
| `strncat(dest, src, n)` | 最多追加 n 个字符 | 较安全 |
| `strcmp(s1, s2)` | 比较字符串 | 安全 |
| `strncmp(s1, s2, n)` | 比较前 n 个字符 | 安全 |
| `strchr(s, c)` | 查找字符 | 安全 |
| `strstr(s1, s2)` | 查找子串 | 安全 |
| `strtok(s, delim)` | 分割字符串 | 有状态 |

**示例：**

```c
#include <stdio.h>
#include <string.h>

int main() {
    char s1[50] = "Hello ";
    char s2[] = "World";

    // 字符串长度
    printf("s1 长度 = %zu\n", strlen(s1));

    // 字符串拼接
    strcat(s1, s2);
    printf("拼接后：%s\n", s1);

    // 字符串比较
    printf("比较结果：%d\n", strcmp("abc", "abc"));  // 0
    printf("比较结果：%d\n", strcmp("abc", "abd"));  // < 0

    // 查找子串
    char *p = strstr("Hello World", "World");
    if (p != NULL) {
        printf("找到：%s\n", p);
    }

    // 安全的字符串复制
    char dest[10];
    strncpy(dest, "This is a long string", sizeof(dest) - 1);
    dest[sizeof(dest) - 1] = '\0';  // strncpy 不保证补零
    printf("安全复制：%s\n", dest);

    return 0;
}
```

### 9.4 安全要点

- **永远不要使用 `gets()`**：无边界检查，必然导致溢出
- **使用 `strncpy` 后手动补零**：`strncpy` 在源串长于 n 时不会自动添加 `'\0'`
- **`strcat` 不安全**：使用 `strncat` 替代
- **字符串常量不可修改**：`char *p = "hello"` 指向只读内存
- **输入验证**：处理用户输入时进行长度和格式检查

---

## 10. 结构体与联合体

### 10.1 结构体定义

结构体是用户自定义的数据类型，可以包含多个不同类型的成员。

```c
// 定义结构体类型
struct Student {
    char name[50];
    int age;
    float score;
    int id;
};

// 声明结构体变量
struct Student s1;

// 初始化
struct Student s2 = {"张三", 20, 95.5f, 1001};

// 访问成员
printf("%s\n", s2.name);
s2.age = 21;
```

### 10.2 typedef 简化

使用 `typedef` 可以简化结构体类型名。

```c
typedef struct {
    char name[50];
    int age;
    float salary;
} Employee;

// 直接使用 Employee 作为类型
Employee emp = {"李四", 30, 15000.0f};
```

### 10.3 结构体数组

```c
struct Student class[3] = {
    {"小明", 18, 90.0f, 2001},
    {"小红", 19, 92.5f, 2002},
    {"小刚", 18, 85.0f, 2003}
};

for (int i = 0; i < 3; i++) {
    printf("%s: %.1f\n", class[i].name, class[i].score);
}
```

### 10.4 结构体指针

使用 `->` 运算符访问结构体指针的成员。

```c
struct Student s = {"王五", 22, 88.0f, 1003};
struct Student *p = &s;

printf("%s\n", p->name);   // 使用 -> 访问
printf("%d\n", p->age);

// 三种等价方式
s.name        // 直接访问
(*p).name     // 解引用后用 .
p->name       // 用 -> 运算符
```

### 10.5 嵌套结构体

```c
typedef struct {
    int year;
    int month;
    int day;
} Date;

typedef struct {
    char name[50];
    Date birthday;  // 嵌套的结构体成员
    char address[100];
} Person;

Person p;
p.birthday.year = 1995;
p.birthday.month = 6;
p.birthday.day = 15;
```

### 10.6 内存对齐

结构体的大小可能大于成员大小之和，因为存在**内存对齐**。

```c
struct Example {
    char a;     // 1 字节
    int b;      // 4 字节
    char c;     // 1 字节
};

printf("%zu\n", sizeof(struct Example));
// 输出可能是 12，而不是 6
// 因为编译器会插入填充字节以保证对齐
```

**内存对齐的原因：**
- 提高访问效率：CPU 按字长访问内存，对齐的数据访问更快
- 平台要求：某些架构不支持非对齐访问

### 10.7 联合体（Union）

联合体的所有成员共享同一块内存，大小等于最大成员的大小。

```c
typedef union {
    int i;
    float f;
    char c;
} Data;

Data d;
d.i = 100;
printf("%d\n", d.i);  // 100

d.f = 3.14f;
printf("%f\n", d.f);  // 3.14
printf("%d\n", d.i);  // 值已被覆盖，不再是 100
```

**应用：判断字节序**

```c
union {
    int num;
    char bytes[4];
} endian;

endian.num = 0x12345678;
if (endian.bytes[0] == 0x78) {
    printf("小端序（Little Endian）\n");
} else {
    printf("大端序（Big Endian）\n");
}
```

### 10.8 枚举（Enum）

枚举是一组命名的整型常量。

```c
enum Color {
    RED,    // 0
    GREEN,  // 1
    BLUE,   // 2
    YELLOW  // 3
};

enum Color c = GREEN;
printf("%d\n", c);  // 1

// 可以指定起始值
enum Weekday {
    MONDAY = 1,
    TUESDAY,   // 2
    WEDNESDAY, // 3
    // ...
};
```

### 10.9 安全要点

- **结构体对齐**：了解内存布局对逆向分析和漏洞利用很重要
- **联合体误用**：确保读写的成员类型一致
- **结构体指针 NULL 检查**：使用前检查指针
- **灵活数组成员**：C99 支持结构体末尾的零长度数组，常用于变长数据

---

## 11. 文件操作

### 11.1 文件指针

文件操作通过 `FILE *` 类型的指针进行。

```c
#include <stdio.h>

FILE *fp;
```

### 11.2 打开与关闭文件

```c
// fopen 打开文件
FILE *fp = fopen("file.txt", "r");
if (fp == NULL) {
    perror("打开文件失败");
    return 1;
}

// ... 操作文件 ...

fclose(fp);  // 关闭文件
```

**打开模式：**

| 模式 | 含义 | 文件不存在时 |
|------|------|-------------|
| `"r"` | 只读 | 出错 |
| `"w"` | 只写（覆盖） | 创建新文件 |
| `"a"` | 追加（在末尾写入） | 创建新文件 |
| `"r+"` | 读写 | 出错 |
| `"w+"` | 读写（覆盖） | 创建新文件 |
| `"rb"` | 二进制读 | 出错 |
| `"wb"` | 二进制写 | 创建新文件 |

### 11.3 字符读写

```c
// fputc 写入字符
FILE *fp = fopen("test.txt", "w");
fputc('H', fp);
fputc('e', fp);
fputc('l', fp);
fputc('l', fp);
fputc('o', fp);
fclose(fp);

// fgetc 读取字符
FILE *fp = fopen("test.txt", "r");
int ch;  // 注意用 int，因为 EOF 是 -1
while ((ch = fgetc(fp)) != EOF) {
    printf("%c", ch);
}
fclose(fp);
```

### 11.4 字符串读写

```c
// fputs 写入字符串
FILE *fp = fopen("test.txt", "w");
fputs("Hello, World!\n", fp);
fputs("第二行\n", fp);
fclose(fp);

// fgets 读取一行
char line[100];
FILE *fp = fopen("test.txt", "r");
while (fgets(line, sizeof(line), fp) != NULL) {
    printf("%s", line);
}
fclose(fp);
```

### 11.5 格式化读写

```c
// fprintf 格式化写入
FILE *fp = fopen("data.txt", "w");
fprintf(fp, "姓名：%s\n", "张三");
fprintf(fp, "年龄：%d\n", 20);
fprintf(fp, "分数：%.1f\n", 95.5);
fclose(fp);

// fscanf 格式化读取
char name[50];
int age;
float score;
FILE *fp = fopen("data.txt", "r");
while (fscanf(fp, "姓名：%s\n年龄：%d\n分数：%f\n", name, &age, &score) == 3) {
    printf("%s, %d, %.1f\n", name, age, score);
}
fclose(fp);
```

### 11.6 二进制文件读写

```c
typedef struct {
    char name[50];
    int age;
    float score;
} Student;

// fwrite 二进制写入
Student s = {"小明", 18, 90.0f};
FILE *fp = fopen("stu.dat", "wb");
fwrite(&s, sizeof(Student), 1, fp);
fclose(fp);

// fread 二进制读取
Student s2;
FILE *fp = fopen("stu.dat", "rb");
fread(&s2, sizeof(Student), 1, fp);
printf("%s, %d, %.1f\n", s2.name, s2.age, s2.score);
fclose(fp);
```

### 11.7 文件定位

```c
FILE *fp = fopen("test.txt", "r");

// ftell - 获取当前位置
long pos = ftell(fp);

// fseek - 移动文件指针
fseek(fp, 10, SEEK_SET);   // 从开头移动 10 字节
fseek(fp, 5, SEEK_CUR);    // 从当前位置移动 5 字节
fseek(fp, -10, SEEK_END);  // 从末尾向前移动 10 字节

// rewind - 回到文件开头
rewind(fp);

fclose(fp);
```

### 11.8 文件操作函数

```c
rename("old.txt", "new.txt");  // 重命名
remove("test.txt");            // 删除文件
```

### 11.9 安全要点

- **检查返回值**：`fopen` 可能失败，必须检查返回值
- **及时关闭**：文件使用完毕必须 `fclose`，防止资源泄漏
- **路径遍历**：不要直接使用用户输入作为文件路径，防止 `../` 绕过
- **权限控制**：注意文件权限设置，敏感数据不要明文存储
- **格式化字符串**：`fprintf` 的格式串不要直接使用用户输入

---

## 12. 内存管理

### 12.1 内存分区

C 程序的内存布局（从低地址到高地址）：

```
高地址  ┌─────────────────────┐
        │    栈（Stack）      │  ← 局部变量、函数参数、返回地址
        │                     │     由系统自动分配和释放
        ├─────────────────────┤
        │     共享库映射区     │
        ├─────────────────────┤
        │    堆（Heap）       │  ← 动态分配的内存（malloc/free）
        │                     │     由程序员手动管理
        ├─────────────────────┤
        │   未初始化数据区     │  ← BSS 段，未初始化的全局/静态变量
        ├─────────────────────┤
        │   已初始化数据区     │  ← 已初始化的全局/静态变量
        ├─────────────────────┤
        │   代码区（Text）     │  ← 程序代码（只读）
低地址  └─────────────────────┘
```

### 12.2 malloc 分配内存

```c
#include <stdlib.h>

// 分配指定字节数的内存
int *p = (int *)malloc(sizeof(int));
if (p == NULL) {
    perror("malloc 失败");
    return 1;
}

*p = 42;
printf("%d\n", *p);

free(p);  // 释放内存
p = NULL; // 置空指针，避免野指针
```

### 12.3 calloc 初始化为零

```c
// 分配 n 个 size 大小的内存，并初始化为 0
int *arr = (int *)calloc(10, sizeof(int));
// 等价于：
// int *arr = (int *)malloc(10 * sizeof(int));
// memset(arr, 0, 10 * sizeof(int));
```

### 12.4 realloc 重新分配

```c
int *arr = (int *)malloc(5 * sizeof(int));

// 扩容到 10 个元素
int *temp = (int *)realloc(arr, 10 * sizeof(int));
if (temp == NULL) {
    // realloc 失败时原内存仍然有效
    free(arr);
    return 1;
}
arr = temp;  // 重新赋值

free(arr);
```

> **注意**：`realloc` 可能返回新地址，也可能在原地址扩容。要用临时变量接收返回值，避免失败时丢失原指针。

### 12.5 free 释放内存

```c
int *p = (int *)malloc(sizeof(int));
// 使用...
free(p);
p = NULL;  // 好习惯：释放后置空
```

### 12.6 内存操作函数

需要包含 `<string.h>`。

```c
#include <string.h>

// memcpy - 内存拷贝（不处理重叠）
char src[] = "Hello";
char dest[20];
memcpy(dest, src, strlen(src) + 1);

// memmove - 内存移动（可处理重叠）
char buf[] = "abcdef";
memmove(buf + 2, buf, 3);  // 重叠拷贝

// memset - 内存设置
char buf2[100];
memset(buf2, 0, sizeof(buf2));   // 清零
memset(buf2, 'A', 10);           // 设为字符 'A'

// memcmp - 内存比较
int cmp = memcmp("abc", "abd", 3);

// memchr - 内存查找字符
char *p = memchr("Hello", 'l', 5);
```

### 12.7 常见内存错误

| 错误类型 | 说明 | 后果 |
|----------|------|------|
| **内存泄漏** | 只分配不释放 | 内存持续增长，最终耗尽 |
| **重复释放** | 同一块内存释放两次 | 堆损坏，程序崩溃 |
| **野指针** | 指针未初始化就使用 | 行为未定义 |
| **空指针解引用** | 对 NULL 指针解引用 | 程序崩溃（段错误） |
| **越界访问** | 访问分配范围之外的内存 | 数据损坏、崩溃 |
| **Use-After-Free** | 释放后继续使用 | 安全漏洞，可能被利用 |
| **Double Free** | 对同一块内存释放两次 | 堆损坏，安全漏洞 |

### 12.8 内存调试工具

- **Valgrind**（Linux）：强大的内存调试工具
  ```bash
  valgrind --leak-check=full ./program
  ```
- **AddressSanitizer**（GCC/Clang）：编译时插装
  ```bash
  gcc -fsanitize=address -g program.c -o program
  ```
- **Visual Studio 调试器**（Windows）：内置内存诊断

### 12.9 安全编程实践

```c
// 1. 分配后检查 NULL
int *p = (int *)malloc(size);
if (p == NULL) {
    // 错误处理
    return -1;
}

// 2. 使用前初始化
memset(p, 0, size);

// 3. 操作时注意边界
for (int i = 0; i < count; i++) {
    // 确保 i 不越界
}

// 4. 释放后置 NULL
free(p);
p = NULL;

// 5. 整数溢出检查
if (count > SIZE_MAX / sizeof(int)) {
    return -1;  // 溢出，返回错误
}
size_t total = count * sizeof(int);
```

---

## 13. 编译与调试

### 13.1 GCC 常用编译选项

| 选项 | 作用 |
|------|------|
| `-Wall` | 启用大部分警告 |
| `-Wextra` | 启用更多警告 |
| `-Werror` | 将警告视为错误 |
| `-g` | 生成调试信息 |
| `-O0` | 不优化（调试用） |
| `-O2` | 二级优化（发布用） |
| `-std=c11` | 指定 C 标准 |
| `-o` | 指定输出文件名 |
| `-c` | 只编译不链接 |
| `-I` | 添加头文件搜索路径 |
| `-L` | 添加库文件搜索路径 |
| `-l` | 链接指定库 |
| `-D` | 定义宏 |
| `-fsanitize=address` | 启用 AddressSanitizer |

```bash
# 推荐的调试编译选项
gcc -Wall -Wextra -g -O0 -std=c11 program.c -o program

# 推荐的发布编译选项
gcc -Wall -Wextra -O2 -std=c11 program.c -o program
```

### 13.2 多文件编译

```
project/
├── main.c
├── utils.c
└── utils.h
```

```bash
# 分别编译，再链接
gcc -c main.c -o main.o
gcc -c utils.c -o utils.o
gcc main.o utils.o -o program

# 或者一步完成
gcc main.c utils.c -o program
```

### 13.3 静态库与动态库

**静态库（.a / .lib）：**

```bash
# 编译为目标文件
gcc -c utils.c -o utils.o

# 打包为静态库
ar rcs libutils.a utils.o

# 链接静态库
gcc main.c -L. -lutils -o program
```

**动态库（.so / .dll）：**

```bash
# Linux
gcc -shared -fPIC utils.c -o libutils.so

# Windows (MinGW)
gcc -shared utils.c -o libutils.dll
```

### 13.4 GDB 调试

```bash
# 编译时加 -g 选项
gcc -g program.c -o program

# 启动 GDB
gdb ./program
```

**常用 GDB 命令：**

| 命令 | 缩写 | 作用 |
|------|------|------|
| `run` | `r` | 运行程序 |
| `break` | `b` | 设置断点 |
| `continue` | `c` | 继续运行 |
| `next` | `n` | 单步执行（跳过函数） |
| `step` | `s` | 单步执行（进入函数） |
| `print` | `p` | 打印变量值 |
| `backtrace` | `bt` | 查看调用栈 |
| `list` | `l` | 列出源代码 |
| `quit` | `q` | 退出 |

### 13.5 Makefile 基础

```makefile
CC = gcc
CFLAGS = -Wall -Wextra -g -std=c11
TARGET = program
SRCS = main.c utils.c
OBJS = $(SRCS:.c=.o)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $(TARGET)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: clean
```

---

## 14. 安全编程要点

### 14.1 缓冲区溢出防护

**危险函数 → 安全替代：**

| 危险函数 | 问题 | 安全替代 |
|----------|------|----------|
| `gets()` | 无边界检查 | `fgets(buf, size, stdin)` |
| `strcpy(dest, src)` | 不检查目标大小 | `strncpy` + 手动补零 |
| `strcat(dest, src)` | 不检查剩余空间 | `strncat` |
| `sprintf(buf, ...)` | 不检查缓冲区 | `snprintf` |
| `scanf("%s", buf)` | 不限制长度 | `scanf("%Ns", buf)` |

**安全代码示例：**

```c
// 读取输入
char buf[100];
fgets(buf, sizeof(buf), stdin);

// 字符串复制
char dest[50];
strncpy(dest, src, sizeof(dest) - 1);
dest[sizeof(dest) - 1] = '\0';

// 字符串拼接
strncat(dest, src, sizeof(dest) - strlen(dest) - 1);

// 格式化输出
snprintf(buf, sizeof(buf), "Hello %s", name);
```

### 14.2 整数溢出防护

```c
// 危险：可能溢出
size_t total = count * sizeof(int);
int *p = malloc(total);

// 安全：先检查
if (count == 0 || count > SIZE_MAX / sizeof(int)) {
    return NULL;
}
size_t total = count * sizeof(int);
int *p = malloc(total);
```

### 14.3 格式化字符串漏洞防护

```c
// 危险：用户输入作为格式串
printf(user_input);

// 安全：使用 %s
printf("%s", user_input);
```

### 14.4 指针安全

```c
// 1. 使用前检查 NULL
if (ptr != NULL) {
    *ptr = value;
}

// 2. 释放后置 NULL
free(ptr);
ptr = NULL;

// 3. 数组访问前检查边界
if (index >= 0 && index < size) {
    arr[index] = value;
}
```

### 14.5 编译器安全选项

```bash
# GCC/Clang 安全编译选项
gcc -Wall -Wextra -Werror \
    -fstack-protector-strong \
    -D_FORTIFY_SOURCE=2 \
    -fPIE -pie \
    -z relro -z now \
    -z noexecstack \
    -O2 program.c -o program
```

| 选项 | 作用 |
|------|------|
| `-fstack-protector-strong` | 栈保护（Canary） |
| `-D_FORTIFY_SOURCE=2` | 源级别安全强化 |
| `-fPIE -pie` | 位置无关可执行（配合 ASLR） |
| `-z relro -z now` | 重定位表只读 |
| `-z noexecstack` | 不可执行栈（DEP/NX） |

### 14.6 输入验证

- 永远不要信任用户输入
- 检查输入长度、格式、范围
- 对外部数据进行校验和过滤
- 使用白名单而非黑名单

### 14.7 错误处理

- 检查所有可能失败的函数返回值
- 合理处理错误，不要忽略
- 使用 `goto` 进行统一的资源清理

---

## 参考资源

- **书籍**：《C程序设计语言》(K&R)、《C和指针》、《C专家编程》、《C陷阱与缺陷》
- **在线教程**：cppreference.com、cplusplus.com
- **安全相关**：《C安全编码标准》、《漏洞利用编程》
- **工具**：GCC、Clang、GDB、Valgrind、AddressSanitizer

---

## 学习资源与知识拓展

### 官方资源

- **C语言 官方文档**：各语言官网提供最权威的文档和教程
- **C语言 标准库参考**：官方标准库 API 文档

### 在线教程

- **菜鸟教程 C语言**：https://www.runoob.com/ — 中文入门教程
- **W3Schools**：https://www.w3schools.com/ — 交互式学习平台
- **MDN Web Docs**：https://developer.mozilla.org/ — Web 技术文档（适用于 JS/HTML/CSS）

### 安全编程资源

- **OWASP 速查表系列**：https://cheatsheetseries.owasp.org/ — 各种安全最佳实践
- **CWE 常见弱点枚举**：https://cwe.mitre.org/ — 软件弱点分类体系
- **安全开发指南**：各语言官方安全文档与最佳实践

### 安全工具与库

- 根据语言选择相应的安全库和工具（加密库、HTTP 库、网络库等）
- 关注 GitHub 上的安全开源项目与社区

### 练习平台

- **LeetCode**：https://leetcode.cn/ — 算法练习平台
- **Codewars**：https://www.codewars.com/ — 编程挑战网站
- **Hack The Box**：https://www.hackthebox.com/ — 安全靶场
- **TryHackMe**：https://tryhackme.com/ — 安全学习房间
- **Bugku**：https://ctf.bugku.com/ — 国内 CTF 平台
- **攻防世界**：https://adworld.xctf.org.cn/ — XCTF 竞赛平台

### 推荐书籍

- 《C语言程序设计》— 入门经典教材
- 《C语言高级编程》— 进阶学习指南
- 各类安全相关技术书籍

### 社区与资讯

- **GitHub**：https://github.com/ — 开源项目托管平台
- **Stack Overflow**：https://stackoverflow.com/ — 编程问答社区
- **FreeBuf**：https://www.freebuf.com/ — 安全资讯媒体
- **安全客**：https://www.anquanke.com/ — 安全技术媒体
- **先知社区**：https://xz.aliyun.com/ — 阿里云安全社区

### 学习路线建议

1. **入门阶段**（1-2月）：掌握基本语法、数据类型、控制流
2. **进阶阶段**（2-3月）：函数、面向对象、异常处理、标准库
3. **实战练习**（1-2月）：通过项目巩固知识
4. **安全方向**（持续）：了解语言相关的安全漏洞和防护
5. **持续学习**：关注社区、阅读源码、参与开源
