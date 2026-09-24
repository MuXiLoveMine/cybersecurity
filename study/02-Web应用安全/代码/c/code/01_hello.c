// ============================================================
// 01_hello.c —— Hello World、变量、数据类型、输入输出
// 编译命令：gcc 01_hello.c -o 01_hello
// 运行命令：./01_hello（Linux/Mac） 或 01_hello.exe（Windows）
// ============================================================

#include <stdio.h>   // 标准输入输出头文件
#include <stdlib.h>  // 标准库头文件

int main() {
    // ---------- 1. Hello World ----------
    printf("========== Hello World ==========\n");
    printf("Hello, World!\n");
    printf("你好，C语言！\n");


    // ---------- 2. 变量与基本数据类型 ----------
    printf("\n========== 变量与数据类型 ==========\n");

    // 整数类型
    int age = 20;                          // 整型，通常4字节
    short height = 175;                    // 短整型，通常2字节
    long population = 8000000L;            // 长整型
    long long big_num = 1234567890LL;      // 长长整型，8字节

    printf("int 整数 age = %d\n", age);
    printf("short 短整数 height = %hd\n", height);
    printf("long 长整数 population = %ld\n", population);
    printf("long long 大整数 big_num = %lld\n", big_num);

    // 浮点类型
    float pi_float = 3.14f;                // 单精度浮点数，4字节
    double pi_double = 3.1415926535;       // 双精度浮点数，8字节

    printf("float 单精度 pi_float = %f\n", pi_float);
    printf("double 双精度 pi_double = %lf\n", pi_double);

    // 字符类型
    char grade = 'A';                      // 字符，1字节
    printf("char 字符 grade = %c\n", grade);

    // 无符号类型
    unsigned int positive = 4000000000u;   // 无符号整数
    printf("unsigned int 无符号数 positive = %u\n", positive);


    // ---------- 3. 常量 ----------
    printf("\n========== 常量 ==========\n");

    const int MAX_SIZE = 100;              // const 常量，不能修改
    printf("const 常量 MAX_SIZE = %d\n", MAX_SIZE);
    // MAX_SIZE = 200;  // 错误：不能修改 const 变量

#define PI 3.14159                         // 宏定义常量
    printf("宏定义常量 PI = %f\n", PI);


    // ---------- 4. sizeof 查看大小 ----------
    printf("\n========== 数据类型大小（字节） ==========\n");
    printf("int: %zu 字节\n", sizeof(int));
    printf("short: %zu 字节\n", sizeof(short));
    printf("long: %zu 字节\n", sizeof(long));
    printf("long long: %zu 字节\n", sizeof(long long));
    printf("float: %zu 字节\n", sizeof(float));
    printf("double: %zu 字节\n", sizeof(double));
    printf("char: %zu 字节\n", sizeof(char));


    // ---------- 5. 运算符 ----------
    printf("\n========== 运算符 ==========\n");

    int a = 10, b = 3;

    // 算术运算符
    printf("a = %d, b = %d\n", a, b);
    printf("a + b = %d\n", a + b);     // 加
    printf("a - b = %d\n", a - b);     // 减
    printf("a * b = %d\n", a * b);     // 乘
    printf("a / b = %d\n", a / b);     // 除（整数除法）
    printf("a %% b = %d\n", a % b);    // 取余

    // 自增自减
    int x = 5;
    printf("x = %d\n", x);
    printf("x++ = %d（后自增，表达式值为原值）\n", x++);
    printf("此时 x = %d\n", x);
    printf("++x = %d（前自增，表达式值为新值）\n", ++x);

    // 关系运算符
    printf("\na > b ? %s\n", (a > b) ? "是" : "否");
    printf("a == b ? %s\n", (a == b) ? "是" : "否");
    printf("a != b ? %s\n", (a != b) ? "是" : "否");

    // 逻辑运算符
    int c = 1, d = 0;  // C 语言中 0 表示假，非 0 表示真
    printf("\nc = 1(真), d = 0(假)\n");
    printf("c && d = %d  （逻辑与）\n", c && d);
    printf("c || d = %d  （逻辑或）\n", c || d);
    printf("!c = %d  （逻辑非）\n", !c);

    // 位运算
    int m = 6;  // 二进制 0110
    int n = 3;  // 二进制 0011
    printf("\nm = 6(0110), n = 3(0011)\n");
    printf("m & n = %d  （按位与：0010=2）\n", m & n);
    printf("m | n = %d  （按位或：0111=7）\n", m | n);
    printf("m ^ n = %d  （按位异或：0101=5）\n", m ^ n);
    printf("m << 1 = %d  （左移：1100=12）\n", m << 1);
    printf("m >> 1 = %d  （右移：0011=3）\n", m >> 1);

    // 赋值运算符
    int p = 10;
    p += 5;  // 等价于 p = p + 5
    printf("\np += 5 后 p = %d\n", p);

    // 三目运算符（条件运算符）
    int score = 85;
    char *result = (score >= 60) ? "及格" : "不及格";
    printf("score = %d，结果：%s\n", score, result);


    // ---------- 6. 输入输出 ----------
    printf("\n========== 输入输出 ==========\n");

    char name[50];
    int user_age;

    printf("请输入你的名字：");
    scanf("%s", name);                       // 输入字符串

    printf("请输入你的年龄：");
    scanf("%d", &user_age);                  // 输入整数（注意取地址符 &）

    printf("\n你好，%s！你今年 %d 岁。\n", name, user_age);

    // 一次输入多个值
    int num1, num2;
    printf("\n请输入两个整数（用空格分隔）：");
    scanf("%d %d", &num1, &num2);
    printf("%d + %d = %d\n", num1, num2, num1 + num2);


    // ---------- 安全小贴士 ----------
    printf("\n========== 安全小贴士 ==========\n");
    printf("C 语言直接操作内存，效率高但需要程序员手动管理内存。\n");
    printf("不安全的函数（如 gets、strcpy）可能导致缓冲区溢出漏洞。\n");
    printf("在安全领域，理解这些底层机制是漏洞挖掘与逆向分析的基础。\n");

    return 0;
}
