// ============================================================
// 01_hello.cpp —— Hello World、变量、数据类型、输入输出
// 编译命令：g++ 01_hello.cpp -o 01_hello
// 运行命令：./01_hello（Linux/Mac） 或 01_hello.exe（Windows）
// ============================================================

#include <iostream>   // 输入输出流头文件
#include <string>     // 字符串头文件
using namespace std;  // 使用标准命名空间，避免每次写 std::

int main() {
    // ---------- 1. Hello World ----------
    cout << "========== Hello World ==========" << endl;
    cout << "Hello, World!" << endl;       // cout 输出，endl 换行
    cout << "你好，C++！" << endl;


    // ---------- 2. 变量与基本数据类型 ----------
    cout << "\n========== 变量与数据类型 ==========" << endl;

    // 整数类型
    int age = 20;                   // 整型，4 字节
    short height = 175;             // 短整型，2 字节
    long population = 8000000L;     // 长整型
    long long big_num = 1234567890LL; // 长长整型，8 字节

    cout << "int 整数 age = " << age << endl;
    cout << "short 短整数 height = " << height << endl;
    cout << "long 长整数 population = " << population << endl;
    cout << "long long 大整数 big_num = " << big_num << endl;

    // 浮点类型
    float pi_float = 3.14f;         // 单精度浮点数，4 字节
    double pi_double = 3.1415926535; // 双精度浮点数，8 字节

    cout << "float 单精度 pi_float = " << pi_float << endl;
    cout << "double 双精度 pi_double = " << pi_double << endl;

    // 字符类型
    char grade = 'A';               // 字符，1 字节
    cout << "char 字符 grade = " << grade << endl;

    // 布尔类型（C++）
    bool is_student = true;         // 布尔值：true 或 false
    cout << "bool 布尔 is_student = " << (is_student ? "true" : "false") << endl;

    // 无符号类型
    unsigned int positive = 4000000000u;  // 无符号整数
    cout << "unsigned int 无符号数 positive = " << positive << endl;


    // ---------- 3. 常量 ----------
    cout << "\n========== 常量 ==========" << endl;

    const int MAX_SIZE = 100;       // const 常量，不能修改
    cout << "const 常量 MAX_SIZE = " << MAX_SIZE << endl;
    // MAX_SIZE = 200;  // 错误：不能修改 const 变量

    #define PI 3.14159              // 宏定义常量（C 风格）
    cout << "宏定义常量 PI = " << PI << endl;


    // ---------- 4. sizeof 查看大小 ----------
    cout << "\n========== 数据类型大小（字节） ==========" << endl;
    cout << "int: " << sizeof(int) << " 字节" << endl;
    cout << "short: " << sizeof(short) << " 字节" << endl;
    cout << "long: " << sizeof(long) << " 字节" << endl;
    cout << "long long: " << sizeof(long long) << " 字节" << endl;
    cout << "float: " << sizeof(float) << " 字节" << endl;
    cout << "double: " << sizeof(double) << " 字节" << endl;
    cout << "char: " << sizeof(char) << " 字节" << endl;
    cout << "bool: " << sizeof(bool) << " 字节" << endl;


    // ---------- 5. 运算符 ----------
    cout << "\n========== 运算符 ==========" << endl;

    int a = 10, b = 3;

    // 算术运算符
    cout << "a = " << a << ", b = " << b << endl;
    cout << "a + b = " << (a + b) << endl;    // 加
    cout << "a - b = " << (a - b) << endl;    // 减
    cout << "a * b = " << (a * b) << endl;    // 乘
    cout << "a / b = " << (a / b) << endl;    // 除（整数除法）
    cout << "a % b = " << (a % b) << endl;    // 取余

    // 自增自减
    int x = 5;
    cout << "x = " << x << endl;
    cout << "x++ = " << x++ << "（后自增，表达式值为原值）" << endl;
    cout << "此时 x = " << x << endl;
    cout << "++x = " << ++x << "（前自增，表达式值为新值）" << endl;

    // 关系运算符
    cout << "\na > b ? " << (a > b ? "是" : "否") << endl;
    cout << "a == b ? " << (a == b ? "是" : "否") << endl;
    cout << "a != b ? " << (a != b ? "是" : "否") << endl;

    // 逻辑运算符
    bool c = true, d = false;
    cout << "\nc = true, d = false" << endl;
    cout << "c && d = " << (c && d ? "true" : "false") << "  （逻辑与）" << endl;
    cout << "c || d = " << (c || d ? "true" : "false") << "  （逻辑或）" << endl;
    cout << "!c = " << (!c ? "true" : "false") << "  （逻辑非）" << endl;

    // 位运算
    int m = 6;  // 二进制 0110
    int n = 3;  // 二进制 0011
    cout << "\nm = 6(0110), n = 3(0011)" << endl;
    cout << "m & n = " << (m & n) << "  （按位与：0010=2）" << endl;
    cout << "m | n = " << (m | n) << "  （按位或：0111=7）" << endl;
    cout << "m ^ n = " << (m ^ n) << "  （按位异或：0101=5）" << endl;
    cout << "m << 1 = " << (m << 1) << "  （左移：1100=12）" << endl;
    cout << "m >> 1 = " << (m >> 1) << "  （右移：0011=3）" << endl;

    // 赋值运算符
    int p = 10;
    p += 5;  // 等价于 p = p + 5
    cout << "\np += 5 后 p = " << p << endl;

    // 三目运算符（条件运算符）
    int score = 85;
    string result = (score >= 60) ? "及格" : "不及格";
    cout << "score = " << score << "，结果：" << result << endl;


    // ---------- 6. 输入输出 ----------
    cout << "\n========== 输入输出 ==========" << endl;

    string name;
    int user_age;

    cout << "请输入你的名字：";
    cin >> name;                                    // 输入字符串

    cout << "请输入你的年龄：";
    cin >> user_age;                                // 输入整数

    cout << "\n你好，" << name << "！你今年 " << user_age << " 岁。" << endl;

    // 一次输入多个值
    int num1, num2;
    cout << "\n请输入两个整数（用空格分隔）：";
    cin >> num1 >> num2;
    cout << num1 << " + " << num2 << " = " << (num1 + num2) << endl;


    // ---------- 安全小贴士 ----------
    cout << "\n========== 安全小贴士 ==========" << endl;
    cout << "C/C++ 直接操作内存，效率高但需要程序员手动管理内存。" << endl;
    cout << "不安全的函数（如 gets、strcpy）可能导致缓冲区溢出漏洞。" << endl;
    cout << "在安全领域，理解这些底层机制是漏洞挖掘与逆向分析的基础。" << endl;

    return 0;
}
