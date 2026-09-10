// ============================================================
// 03_methods.cs - 方法定义、参数、返回值、重载、可选参数、扩展方法
// 运行方式：dotnet run --project .  或  csc 03_methods.cs && 03_methods.exe
// ============================================================

using System;

// ---------- 1. 方法的基本定义 ----------
Console.WriteLine("========== 1. 方法基本定义 ==========");

// 调用无返回值方法
PrintHello();
PrintMessage("C# 方法学习");

// 调用有返回值方法
int sum = Add(10, 20);
Console.WriteLine($"10 + 20 = {sum}");

int maxNum = Max(15, 25);
Console.WriteLine($"Max(15, 25) = {maxNum}");

Console.WriteLine();

// ---------- 2. 方法参数类型 ----------
Console.WriteLine("========== 2. 方法参数类型 ==========");

// 2.1 值参数（默认）
Console.WriteLine("值参数：");
int x = 10;
ChangeValue(x);
Console.WriteLine($"  调用 ChangeValue 后，x = {x}（值参数不影响原变量）");

// 2.2 引用参数 ref
Console.WriteLine("\n引用参数 ref：");
int y = 10;
ChangeByRef(ref y);
Console.WriteLine($"  调用 ChangeByRef 后，y = {y}（ref 参数影响原变量）");

// 2.3 输出参数 out
Console.WriteLine("\n输出参数 out：");
int quotient, remainder;
Divide(17, 5, out quotient, out remainder);
Console.WriteLine($"  17 / 5 = 商 {quotient}，余 {remainder}");

// C# 7.0+ 可以在调用时声明 out 变量
Divide(23, 4, out int q, out int r);
Console.WriteLine($"  23 / 4 = 商 {q}，余 {r}");

// 2.4 输入参数 in（只读引用）
Console.WriteLine("\n输入参数 in：");
int bigNum = 1000000;
PrintInValue(in bigNum);

// 2.5 可变参数 params
Console.WriteLine("\n可变参数 params：");
int total = Sum(1, 2, 3, 4, 5);
Console.WriteLine($"  Sum(1,2,3,4,5) = {total}");
int total2 = Sum(10, 20, 30);
Console.WriteLine($"  Sum(10,20,30) = {total2}");

// 也可以传数组
int[] nums = { 100, 200, 300, 400, 500 };
int total3 = Sum(nums);
Console.WriteLine($"  Sum(数组) = {total3}");

Console.WriteLine();

// ---------- 3. 可选参数与命名参数 ----------
Console.WriteLine("========== 3. 可选参数与命名参数 ==========");

// 可选参数（带默认值）
Console.WriteLine("可选参数：");
Greet("张三");                        // 使用默认问候语
Greet("李四", "早上好");               // 指定问候语
Greet("王五", greeting: "晚上好");     // 命名参数

// 多个可选参数
Console.WriteLine("\n多个可选参数：");
PrintInfo("赵六");
PrintInfo("钱七", age: 30);
PrintInfo("孙八", city: "上海");
PrintInfo("周九", age: 28, city: "深圳");

// 命名参数（不按顺序传参）
Console.WriteLine("\n命名参数（调整顺序）：");
PrintInfo(city: "北京", name: "吴十", age: 35);

Console.WriteLine();

// ---------- 4. 方法重载 ----------
Console.WriteLine("========== 4. 方法重载 ==========");

// 同名方法，参数列表不同（类型或数量不同）
Console.WriteLine("方法重载：");
Console.WriteLine($"  Add(3, 4) = {Add(3, 4)}");                    // int 版本
Console.WriteLine($"  Add(3.5, 4.5) = {Add(3.5, 4.5)}");            // double 版本
Console.WriteLine($"  Add(1, 2, 3) = {Add(1, 2, 3)}");              // 三个 int
Console.WriteLine($"  Add(\"Hello\", \" World\") = {Add("Hello", " World")}");  // string 版本

Console.WriteLine();

// ---------- 5. 本地函数（C# 7.0+） ----------
Console.WriteLine("========== 5. 本地函数 ==========");

// 在方法内部定义的函数，只能在内部访问
int CalculateFactorial(int n)
{
    // 本地函数：递归辅助函数
    int Factorial(int num)
    {
        if (num <= 1) return 1;
        return num * Factorial(num - 1);
    }

    return Factorial(n);
}

Console.WriteLine($"  5 的阶乘：{CalculateFactorial(5)}");
Console.WriteLine($"  7 的阶乘：{CalculateFactorial(7)}");

// 本地函数捕获外部变量（闭包）
int counter = 0;
void Increment()
{
    counter++;
    Console.WriteLine($"  counter = {counter}");
}

Console.WriteLine("\n本地函数捕获变量：");
Increment();
Increment();
Increment();

Console.WriteLine();

// ---------- 6. 元组返回多值（C# 7.0+） ----------
Console.WriteLine("========== 6. 元组返回多值 ==========");

// 使用 ValueTuple 返回多个值
(int min, int max) FindMinMax(int[] arr)
{
    if (arr == null || arr.Length == 0)
        return (0, 0);

    int min = arr[0];
    int max = arr[0];
    foreach (int num in arr)
    {
        if (num < min) min = num;
        if (num > max) max = num;
    }
    return (min, max);
}

int[] numbers = { 45, 12, 78, 23, 56, 9, 67 };
var result = FindMinMax(numbers);
Console.WriteLine($"数组的最小值：{result.min}，最大值：{result.max}");

// 解构元组
var (minVal, maxVal) = FindMinMax(numbers);
Console.WriteLine($"解构后：min={minVal}, max={maxVal}");

// 使用不同的变量名
(int smallest, int largest) = FindMinMax(numbers);
Console.WriteLine($"smallest={smallest}, largest={largest}");

// 返回字符串和数字的元组
(string name, int age, string city) GetPersonInfo()
{
    return ("张三", 25, "北京");
}

var person = GetPersonInfo();
Console.WriteLine($"\n人员信息：{person.name}，{person.age}岁，{person.city}");

Console.WriteLine();

// ---------- 7. 扩展方法 ----------
Console.WriteLine("========== 7. 扩展方法 ==========");

// 扩展方法可以像调用实例方法一样调用静态方法
string email = "test@example.com";
Console.WriteLine($"\"{email}\" 是邮箱吗？{email.IsEmail()}");

string notEmail = "hello world";
Console.WriteLine($"\"{notEmail}\" 是邮箱吗？{notEmail.IsEmail()}");

// 字符串扩展：判断是否为数字
string numStr = "12345";
Console.WriteLine($"\"{numStr}\" 是数字吗？{numStr.IsNumeric()}");

string alphaStr = "abc";
Console.WriteLine($"\"{alphaStr}\" 是数字吗？{alphaStr.IsNumeric()}");

// int 扩展：判断是否为质数
int prime = 17;
int notPrime = 15;
Console.WriteLine($"{prime} 是质数吗？{prime.IsPrime()}");
Console.WriteLine($"{notPrime} 是质数吗？{notPrime.IsPrime()}");

// 字符串扩展：反转
string original = "Hello World";
Console.WriteLine($"\"{original}\" 反转后：\"{original.ReverseString()}\"");

Console.WriteLine();

// ---------- 8. 表达式体方法（Lambda 风格） ----------
Console.WriteLine("========== 8. 表达式体方法 ==========");

// 简单方法可以用 => 表达式体语法
int Square(int n) => n * n;
bool IsEven(int n) => n % 2 == 0;
string GreetShort(string name) => $"你好，{name}！";

Console.WriteLine($"Square(5) = {Square(5)}");
Console.WriteLine($"IsEven(4) = {IsEven(4)}");
Console.WriteLine($"GreetShort(\"小明\") = {GreetShort("小明")}");

Console.WriteLine();
Console.WriteLine("========== 程序结束 ==========");

// ============================================================
// 方法定义（作为顶级语句方法）
// ============================================================

// 无返回值方法
void PrintHello()
{
    Console.WriteLine("Hello!");
}

void PrintMessage(string message)
{
    Console.WriteLine($"消息：{message}");
}

// 有返回值方法
int Add(int a, int b)
{
    return a + b;
}

int Max(int a, int b)
{
    return a > b ? a : b;
}

// 值参数
void ChangeValue(int x)
{
    x = 100;  // 只修改副本，不影响调用方
}

// 引用参数 ref
void ChangeByRef(ref int x)
{
    x = 100;  // 直接修改调用方的变量
}

// 输出参数 out
void Divide(int a, int b, out int quotient, out int remainder)
{
    quotient = a / b;
    remainder = a % b;
}

// 输入参数 in（只读引用，避免值拷贝，不能修改）
void PrintInValue(in int value)
{
    // value = 200;  // 错误：in 参数不能修改
    Console.WriteLine($"  in 参数值：{value}");
}

// 可变参数 params
int Sum(params int[] numbers)
{
    int total = 0;
    foreach (int n in numbers)
    {
        total += n;
    }
    return total;
}

// 可选参数
void Greet(string name, string greeting = "你好")
{
    Console.WriteLine($"  {greeting}，{name}！");
}

// 多个可选参数
void PrintInfo(string name, int age = 18, string city = "北京")
{
    Console.WriteLine($"  姓名：{name}，年龄：{age}，城市：{city}");
}

// 方法重载 - double 版本
double Add(double a, double b)
{
    return a + b;
}

// 方法重载 - 三个 int
int Add(int a, int b, int c)
{
    return a + b + c;
}

// 方法重载 - string 版本
string Add(string a, string b)
{
    return a + b;
}

// ============================================================
// 扩展方法所在的静态类
// ============================================================

public static class StringExtensions
{
    // 扩展方法：判断字符串是否像邮箱
    public static bool IsEmail(this string str)
    {
        if (string.IsNullOrEmpty(str)) return false;
        return str.Contains("@") && str.Contains(".");
    }

    // 扩展方法：判断字符串是否全是数字
    public static bool IsNumeric(this string str)
    {
        if (string.IsNullOrEmpty(str)) return false;
        foreach (char c in str)
        {
            if (!char.IsDigit(c)) return false;
        }
        return true;
    }

    // 扩展方法：反转字符串
    public static string ReverseString(this string str)
    {
        if (string.IsNullOrEmpty(str)) return str;
        char[] chars = str.ToCharArray();
        Array.Reverse(chars);
        return new string(chars);
    }
}

public static class IntExtensions
{
    // 扩展方法：判断整数是否为质数
    public static bool IsPrime(this int n)
    {
        if (n <= 1) return false;
        if (n == 2) return true;
        if (n % 2 == 0) return false;
        for (int i = 3; i * i <= n; i += 2)
        {
            if (n % i == 0) return false;
        }
        return true;
    }
}
