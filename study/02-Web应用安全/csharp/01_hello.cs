// ============================================================
// 01_hello.cs - Hello World、变量、数据类型、类型转换、运算符
// 运行方式：dotnet run --project .  或  csc 01_hello.cs && 01_hello.exe
// ============================================================

using System;

// ---------- 1. Hello World ----------
Console.WriteLine("========== 1. Hello World ==========");
Console.WriteLine("Hello, C# World!");
Console.WriteLine();

// ---------- 2. 变量声明与赋值 ----------
Console.WriteLine("========== 2. 变量 ==========");

// 基本语法：类型 变量名 = 值;
int age = 25;
string name = "张三";
double height = 1.75;
bool isStudent = true;
char grade = 'A';

Console.WriteLine($"姓名：{name}");
Console.WriteLine($"年龄：{age}");
Console.WriteLine($"身高：{height} 米");
Console.WriteLine($"是否学生：{isStudent}");
Console.WriteLine($"成绩等级：{grade}");
Console.WriteLine();

// ---------- 3. 常量 ----------
Console.WriteLine("========== 3. 常量 ==========");
const double PI = 3.1415926;
const string AppName = "安全测试工具";

Console.WriteLine($"圆周率：{PI}");
Console.WriteLine($"应用名称：{AppName}");
// PI = 3.14;  // 错误：常量不能修改
Console.WriteLine();

// ---------- 4. 类型推断 var ----------
Console.WriteLine("========== 4. 类型推断 var ==========");
// 使用 var 关键字，编译器自动推断类型
var number = 100;          // 推断为 int
var message = "你好";       // 推断为 string
var price = 19.99m;        // 推断为 decimal
var flag = true;           // 推断为 bool

Console.WriteLine($"number 类型：{number.GetType().Name}，值：{number}");
Console.WriteLine($"message 类型：{message.GetType().Name}，值：{message}");
Console.WriteLine($"price 类型：{price.GetType().Name}，值：{price}");
Console.WriteLine($"flag 类型：{flag.GetType().Name}，值：{flag}");
Console.WriteLine();

// ---------- 5. 数据类型 ----------
Console.WriteLine("========== 5. 数据类型 ==========");

// 整型
sbyte sb = 127;          // 有符号字节 -128~127
byte b = 255;            // 无符号字节 0~255
short s = 32767;         // 短整型 -32768~32767
ushort us = 65535;       // 无符号短整型 0~65535
int i = 2147483647;      // 整型
uint ui = 4294967295;    // 无符号整型
long l = 9223372036854775807;      // 长整型
ulong ul = 18446744073709551615;   // 无符号长整型

Console.WriteLine($"整型范围：int.MinValue={int.MinValue}, int.MaxValue={int.MaxValue}");
Console.WriteLine($"长整型范围：long.MinValue={long.MinValue}, long.MaxValue={long.MaxValue}");

// 浮点型
float f = 3.14f;         // 单精度浮点（约7位有效数字）
double d = 3.1415926535; // 双精度浮点（约15-16位有效数字）
decimal dec = 9999.99m;  // 高精度十进制（适用于金融计算）

Console.WriteLine($"float: {f}");
Console.WriteLine($"double: {d}");
Console.WriteLine($"decimal: {dec}");

// 布尔型
bool trueVal = true;
bool falseVal = false;
Console.WriteLine($"布尔值：{trueVal}, {falseVal}");

// 字符型
char ch = 'A';
Console.WriteLine($"字符：{ch}，ASCII码：{(int)ch}");
Console.WriteLine();

// ---------- 6. 可空类型 ----------
Console.WriteLine("========== 6. 可空类型 ==========");

// 值类型默认不能为 null，使用 ? 声明可空类型
int? nullableInt = null;
Console.WriteLine($"nullableInt 初始值：{nullableInt}，HasValue：{nullableInt.HasValue}");

nullableInt = 42;
Console.WriteLine($"赋值后：{nullableInt}，HasValue：{nullableInt.HasValue}");

// 空合并运算符 ??
int safeValue = nullableInt ?? 0;   // 如果为 null 则返回 0
Console.WriteLine($"安全取值：{safeValue}");

string? nullableStr = null;  // C# 8.0+ 可空引用类型
string result = nullableStr ?? "默认字符串";
Console.WriteLine($"字符串空合并：{result}");

// 空条件运算符 ?.
int? len = nullableStr?.Length;  // 如果为 null 则返回 null，不抛异常
Console.WriteLine($"空条件运算符结果：{len}");
Console.WriteLine();

// ---------- 7. 类型转换 ----------
Console.WriteLine("========== 7. 类型转换 ==========");

// 隐式转换（安全，自动进行）
int intVal = 100;
long longVal = intVal;       // int -> long
double doubleVal = intVal;   // int -> double
Console.WriteLine($"隐式转换：int={intVal} -> long={longVal}, double={doubleVal}");

// 显式转换（强制转换，可能丢失数据）
double pi = 3.14159;
int intPi = (int)pi;         // 截断小数部分
Console.WriteLine($"显式转换：double={pi} -> int={intPi}");

// 使用 Convert 类
string numStr = "12345";
int converted = Convert.ToInt32(numStr);
double convertedDbl = Convert.ToDouble("3.14");
Console.WriteLine($"Convert：\"{numStr}\" -> {converted}, \"3.14\" -> {convertedDbl}");

// 使用 Parse 方法
int parsed = int.Parse("6789");
Console.WriteLine($"int.Parse：{parsed}");

// 使用 TryParse（安全，不抛异常）
string badInput = "abc";
bool success = int.TryParse(badInput, out int tryResult);
Console.WriteLine($"int.TryParse(\"{badInput}\")：成功={success}，结果={tryResult}");

string goodInput = "2024";
success = int.TryParse(goodInput, out tryResult);
Console.WriteLine($"int.TryParse(\"{goodInput}\")：成功={success}，结果={tryResult}");
Console.WriteLine();

// ---------- 8. 运算符 ----------
Console.WriteLine("========== 8. 运算符 ==========");

int a = 10;
int b = 3;

// 算术运算符
Console.WriteLine($"算术运算：a={a}, b={b}");
Console.WriteLine($"  a + b = {a + b}");
Console.WriteLine($"  a - b = {a - b}");
Console.WriteLine($"  a * b = {a * b}");
Console.WriteLine($"  a / b = {a / b} (整数除法)");
Console.WriteLine($"  a % b = {a % b} (取余)");
Console.WriteLine($"  a++   = {a++} (后置递增，先使用后加)");
Console.WriteLine($"  递增后 a = {a}");
Console.WriteLine($"  ++a   = {++a} (前置递增，先加后使用)");

// 比较运算符
int x = 5, y = 10;
Console.WriteLine($"\n比较运算：x={x}, y={y}");
Console.WriteLine($"  x == y : {x == y}");
Console.WriteLine($"  x != y : {x != y}");
Console.WriteLine($"  x > y  : {x > y}");
Console.WriteLine($"  x < y  : {x < y}");
Console.WriteLine($"  x >= y : {x >= y}");
Console.WriteLine($"  x <= y : {x <= y}");

// 逻辑运算符
bool p = true, q = false;
Console.WriteLine($"\n逻辑运算：p={p}, q={q}");
Console.WriteLine($"  p && q : {p && q} (与)");
Console.WriteLine($"  p || q : {p || q} (或)");
Console.WriteLine($"  !p     : {!p} (非)");

// 位运算符
int m = 6;  // 二进制 0110
int n = 3;  // 二进制 0011
Console.WriteLine($"\n位运算：m={m}(0110), n={n}(0011)");
Console.WriteLine($"  m & n = {m & n} (0010 = {Convert.ToString(m & n, 2)})");
Console.WriteLine($"  m | n = {m | n} (0111 = {Convert.ToString(m | n, 2)})");
Console.WriteLine($"  m ^ n = {m ^ n} (0101 = {Convert.ToString(m ^ n, 2)})");
Console.WriteLine($"  ~m    = {~m} (按位取反)");
Console.WriteLine($"  m << 1 = {m << 1} (左移)");
Console.WriteLine($"  m >> 1 = {m >> 1} (右移)");

// 赋值运算符
int c = 10;
c += 5;   // 等价于 c = c + 5
Console.WriteLine($"\n赋值运算：c += 5 后 c = {c}");
c -= 3;
Console.WriteLine($"  c -= 3 后 c = {c}");
c *= 2;
Console.WriteLine($"  c *= 2 后 c = {c}");
c /= 4;
Console.WriteLine($"  c /= 4 后 c = {c}");

// 三元运算符
int score = 85;
string resultStr = score >= 60 ? "及格" : "不及格";
Console.WriteLine($"\n三元运算符：分数={score}，结果={resultStr}");

Console.WriteLine();
Console.WriteLine("========== 程序结束 ==========");
