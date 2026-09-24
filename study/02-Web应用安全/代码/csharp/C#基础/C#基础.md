# C# / .NET 语言基础

---

## 目录

1. [C#/.NET 简介](#1-cnet-简介)
2. [使用场景](#2-使用场景)
3. [环境配置](#3-环境配置)
4. [基础语法](#4-基础语法)
5. [控制流](#5-控制流)
6. [方法（函数）](#6-方法函数)
7. [数组与集合](#7-数组与集合)
8. [字符串操作](#8-字符串操作)
9. [面向对象编程](#9-面向对象编程)
10. [异常处理](#10-异常处理)
11. [委托与事件](#11-委托与事件)
12. [LINQ 基础](#12-linq-基础)
13. [异步编程 async/await](#13-异步编程-asyncawait)
14. [文件操作](#14-文件操作)
15. [网络请求（HttpClient）](#15-网络请求httpclient)
16. [正则表达式（Regex）](#16-正则表达式regex)
17. [C#/.NET 在安全领域的应用](#17-cnet-在安全领域的应用)

---

## 1. C#/.NET 简介

### 1.1 C# 语言

C#（读作 C Sharp）是由微软公司于 2000 年发布的一种现代、面向对象、类型安全的编程语言。它由 Anders Hejlsberg（Turbo Pascal 和 Delphi 的创始人）主导设计。

**主要特点：**
- **类型安全**：强类型语言，编译时进行类型检查
- **面向对象**：支持封装、继承、多态
- **垃圾回收**：自动内存管理，无需手动释放
- **现代语法**：支持 LINQ、异步编程、模式匹配等现代特性
- **跨平台**：通过 .NET 可运行在 Windows、Linux、macOS 上

### 1.2 .NET 框架/平台

.NET 是一个免费、开源、跨平台的开发者平台，包含：
- **运行时（CLR / CoreCLR）**：公共语言运行时，负责执行代码、内存管理、垃圾回收
- **基础类库（BCL）**：提供丰富的系统级 API
- **编译器**：Roslyn（C#/VB 编译器）
- **SDK 和工具链**：dotnet CLI、Visual Studio 等

**.NET 版本演进：**
- **.NET Framework**（2002-2019）：仅限 Windows，已进入维护模式
- **.NET Core**（2016-2020）：跨平台开源版本
- **.NET 5/6/7/8+**（2020至今）：统一平台，长期支持（LTS）版本为 .NET 6、.NET 8

### 1.3 历史版本

| 版本 | 发布年份 | 主要特性 |
|------|----------|----------|
| C# 1.0 | 2002 | 托管代码、面向对象 |
| C# 2.0 | 2005 | 泛型、匿名方法、迭代器 |
| C# 3.0 | 2007 | LINQ、Lambda、匿名类型 |
| C# 4.0 | 2010 | dynamic、可选参数、命名参数 |
| C# 5.0 | 2012 | async/await 异步编程 |
| C# 6.0 | 2015 | 字符串插值、空值传播 |
| C# 7.0 | 2017 | 元组、模式匹配、本地函数 |
| C# 8.0 | 2019 | 可空引用类型、接口默认方法 |
| C# 9.0 | 2020 | 记录（record）、顶级语句、模式匹配增强 |
| C# 10.0 | 2021 | 全局 using、文件范围命名空间 |
| C# 11.0 | 2022 | 原始字符串、必需成员、泛型数学 |
| C# 12.0 | 2023 | 主构造函数、集合表达式 |

---

## 2. 使用场景

### 2.1 Windows 桌面应用
- **WPF**（Windows Presentation Foundation）：现代化桌面 UI 框架
- **WinForms**：传统 Windows 窗体应用
- **MAUI**：跨平台 UI 框架（Windows/macOS/iOS/Android）

### 2.2 ASP.NET Web 应用
- **ASP.NET Core MVC**：Model-View-Controller 模式
- **ASP.NET Web API**：构建 RESTful API
- **Razor Pages**：页面优先的 Web 开发模型
- **Blazor**：使用 C# 构建交互式 Web UI（替代 JavaScript）

### 2.3 Unity 游戏开发
Unity 游戏引擎使用 C# 作为主要脚本语言，广泛应用于：
- 2D/3D 游戏开发
- AR/VR 应用
- 实时仿真

### 2.4 安全领域应用
- **Web 安全审计**：审计 ASP.NET 应用漏洞
- **恶意代码分析**：分析 .NET 恶意软件（如 Remcos、Agent Tesla）
- **安全工具开发**：渗透测试工具、漏洞扫描器
- **逆向工程**：dnSpy、ILSpy 等 .NET 反编译工具
- **红队工具**：C# 编写的后门、C2 框架（如 Covenant）

---

## 3. 环境配置

### 3.1 .NET SDK

**下载安装：**
- 官网：https://dotnet.microsoft.com/download
- 选择 .NET SDK（包含运行时和工具）

**验证安装：**
```bash
dotnet --version
dotnet --list-sdks
```

**常用命令：**
```bash
dotnet new console    # 创建控制台项目
dotnet build          # 编译项目
dotnet run            # 运行项目
dotnet run --project <项目路径>
```

### 3.2 IDE / 编辑器

**Visual Studio（Windows）**
- 社区版免费，功能完整
- 内置调试器、设计器、测试工具
- 下载：https://visualstudio.microsoft.com/

**JetBrains Rider（跨平台）**
- 功能强大的 .NET IDE
- 支持 Windows/macOS/Linux
- 付费软件，学生可免费使用

**Visual Studio Code（跨平台）**
- 轻量级编辑器
- 安装 C# 扩展（C# Dev Kit）
- 配合 dotnet CLI 使用

### 3.3 第一个程序

```bash
dotnet new console -n HelloWorld
cd HelloWorld
dotnet run
```

---

## 4. 基础语法

### 4.1 变量与常量

```csharp
// 变量声明：类型 变量名 = 值;
int age = 25;
string name = "张三";
double salary = 9999.99;
bool isActive = true;

// 常量：使用 const 关键字
const double PI = 3.1415926;
const string AppName = "MyApp";

// 类型推断：使用 var 关键字（编译时推断类型）
var number = 100;          // 推断为 int
var message = "Hello";     // 推断为 string
var price = 19.99m;        // 推断为 decimal
```

### 4.2 数据类型

**值类型（Value Types）：**
- 整型：`sbyte`, `byte`, `short`, `ushort`, `int`, `uint`, `long`, `ulong`
- 浮点型：`float`, `double`, `decimal`
- 字符型：`char`
- 布尔型：`bool`
- 枚举：`enum`
- 结构：`struct`

**引用类型（Reference Types）：**
- `string`（字符串）
- `object`（所有类型的基类）
- `class`（类）
- `interface`（接口）
- `delegate`（委托）
- 数组

**可空类型：**
```csharp
int? nullableInt = null;   // 可空值类型
string? nullableStr = null; // C# 8.0+ 可空引用类型
```

### 4.3 运算符

**算术运算符：** `+`, `-`, `*`, `/`, `%`, `++`, `--`

**比较运算符：** `==`, `!=`, `>`, `<`, `>=`, `<=`

**逻辑运算符：** `&&`, `||`, `!`

**位运算符：** `&`, `|`, `^`, `~`, `<<`, `>>`

**赋值运算符：** `=`, `+=`, `-=`, `*=`, `/=`, `%=`

**空合并运算符：**
```csharp
string name = null;
string result = name ?? "默认值";  // result = "默认值"

// 空合并赋值
name ??= "默认值";
```

**空条件运算符：**
```csharp
string? s = null;
int? length = s?.Length;  // s 为 null 时返回 null，不抛出异常
```

### 4.4 类型转换

```csharp
// 隐式转换（安全，无数据丢失）
int i = 100;
long l = i;       // int -> long
double d = i;     // int -> double

// 显式转换（强制转换，可能丢失数据）
double x = 3.14;
int y = (int)x;   // y = 3

// 使用 Convert 类
string str = "123";
int num = Convert.ToInt32(str);
double dbl = Convert.ToDouble("3.14");

// 使用 Parse / TryParse
int n = int.Parse("456");
bool success = int.TryParse("abc", out int result);  // success = false
```

---

## 5. 控制流

### 5.1 条件语句

```csharp
// if/else
int score = 85;
if (score >= 90)
{
    Console.WriteLine("优秀");
}
else if (score >= 60)
{
    Console.WriteLine("及格");
}
else
{
    Console.WriteLine("不及格");
}

// 三元运算符
string grade = score >= 60 ? "及格" : "不及格";
```

### 5.2 循环语句

```csharp
// for 循环
for (int i = 0; i < 10; i++)
{
    Console.WriteLine(i);
}

// foreach 循环（遍历集合）
string[] names = { "张三", "李四", "王五" };
foreach (string name in names)
{
    Console.WriteLine(name);
}

// while 循环
int count = 0;
while (count < 5)
{
    count++;
}

// do-while 循环（至少执行一次）
int n = 0;
do
{
    n++;
} while (n < 5);
```

### 5.3 switch 语句

```csharp
// 传统 switch
int day = 3;
switch (day)
{
    case 1:
        Console.WriteLine("星期一");
        break;
    case 2:
        Console.WriteLine("星期二");
        break;
    default:
        Console.WriteLine("其他");
        break;
}

// switch 表达式（C# 8.0+）
string dayName = day switch
{
    1 => "星期一",
    2 => "星期二",
    3 => "星期三",
    _ => "其他"
};
```

### 5.4 模式匹配

```csharp
// 类型模式
object obj = "hello";
if (obj is string s)
{
    Console.WriteLine($"字符串长度：{s.Length}");
}

// 关系模式（C# 9.0+）
int age = 25;
string category = age switch
{
    < 18 => "未成年",
    < 30 => "青年",
    < 60 => "中年",
    _ => "老年"
};

// 逻辑模式（C# 9.0+）
if (age is >= 18 and <= 60) { }
if (score is < 0 or > 100) { }
```

---

## 6. 方法（函数）

### 6.1 方法定义

```csharp
// 基本语法：访问修饰符 返回值类型 方法名(参数列表) { 方法体 }
int Add(int a, int b)
{
    return a + b;
}

// 无返回值
void PrintMessage(string msg)
{
    Console.WriteLine(msg);
}
```

### 6.2 参数类型

```csharp
// 值参数（默认）
void ChangeValue(int x)
{
    x = 100;  // 不影响调用方
}

// 引用参数 ref
void ChangeByRef(ref int x)
{
    x = 100;  // 影响调用方
}
// 调用：ChangeByRef(ref num);

// 输出参数 out
void Divide(int a, int b, out int result, out int remainder)
{
    result = a / b;
    remainder = a % b;
}
// 调用：Divide(10, 3, out int r, out int rem);

// 输入参数 in（只读引用）
void PrintValue(in int x)
{
    // x 不能被修改
    Console.WriteLine(x);
}

// 可变参数 params
int Sum(params int[] numbers)
{
    int total = 0;
    foreach (int n in numbers) total += n;
    return total;
}
// 调用：Sum(1, 2, 3, 4, 5);
```

### 6.3 可选参数与命名参数

```csharp
// 可选参数（带默认值）
void Greet(string name, string greeting = "你好")
{
    Console.WriteLine($"{greeting}，{name}！");
}

Greet("张三");           // 你好，张三！
Greet("李四", "早上好");  // 早上好，李四！

// 命名参数
Greet(greeting: "晚上好", name: "王五");
```

### 6.4 方法重载

```csharp
// 同一个类中，方法名相同但参数列表不同
int Add(int a, int b) { return a + b; }
double Add(double a, double b) { return a + b; }
int Add(int a, int b, int c) { return a + b + c; }
```

### 6.5 扩展方法

```csharp
// 为现有类型添加方法，而无需创建新类型
public static class StringExtensions
{
    public static bool IsEmail(this string str)
    {
        return str.Contains("@");
    }
}

// 调用：
// string email = "test@example.com";
// bool isEmail = email.IsEmail();
```

---

## 7. 数组与集合

### 7.1 数组（Array）

```csharp
// 声明和初始化
int[] numbers = new int[5];              // 长度为 5 的 int 数组
int[] nums = { 1, 2, 3, 4, 5 };         // 初始化器
string[] names = new string[] { "A", "B" };

// 访问元素（索引从 0 开始）
int first = nums[0];
nums[1] = 10;

// 数组属性
int len = nums.Length;

// 多维数组
int[,] matrix = new int[3, 3];           // 二维数组
int[,,] cube = new int[3, 3, 3];         // 三维数组

// 交错数组（数组的数组）
int[][] jagged = new int[3][];
jagged[0] = new int[] { 1, 2 };
jagged[1] = new int[] { 3, 4, 5 };
```

### 7.2 List\<T\>（泛型列表）

最常用的动态数组，位于 `System.Collections.Generic` 命名空间。

```csharp
// 创建
List<int> list = new List<int>();
List<string> names = new List<string> { "张三", "李四" };

// 添加
list.Add(1);
list.AddRange(new int[] { 2, 3, 4 });
list.Insert(0, 0);  // 在指定位置插入

// 访问
int first = list[0];

// 修改
list[0] = 100;

// 删除
list.Remove(100);       // 移除第一个匹配项
list.RemoveAt(0);       // 按索引移除
list.RemoveAll(x => x > 3);  // 按条件移除

// 查找
bool has = list.Contains(2);
int index = list.IndexOf(2);
int count = list.Count;

// 遍历
foreach (int item in list) { }

// 排序
list.Sort();                          // 默认升序
list.Sort((a, b) => b.CompareTo(a));  // 降序

// 转换为数组
int[] arr = list.ToArray();
```

### 7.3 Dictionary\<TKey, TValue\>（字典）

键值对集合，基于哈希表，查找速度 O(1)。

```csharp
// 创建
Dictionary<string, int> dict = new Dictionary<string, int>();
Dictionary<string, string> capitals = new Dictionary<string, string>
{
    ["中国"] = "北京",
    ["美国"] = "华盛顿"
};

// 添加
dict.Add("key1", 100);
dict["key2"] = 200;  // 索引器方式，存在则更新

// 访问
int value = dict["key1"];

// 安全访问
if (dict.TryGetValue("key3", out int val))
{
    // 找到
}

// 判断是否存在
bool hasKey = dict.ContainsKey("key1");
bool hasValue = dict.ContainsValue(100);

// 删除
dict.Remove("key1");

// 遍历
foreach (var kvp in dict)
{
    Console.WriteLine($"{kvp.Key}: {kvp.Value}");
}

// 只遍历键或值
foreach (string key in dict.Keys) { }
foreach (int val in dict.Values) { }
```

### 7.4 HashSet\<T\>（哈希集）

不包含重复元素的集合，用于去重和集合运算。

```csharp
HashSet<int> set = new HashSet<int> { 1, 2, 3 };

set.Add(1);    // 返回 false，已存在
set.Add(4);    // 返回 true

bool contains = set.Contains(2);
set.Remove(2);

// 集合运算
HashSet<int> other = new HashSet<int> { 3, 4, 5 };
set.UnionWith(other);        // 并集
set.IntersectWith(other);    // 交集
set.ExceptWith(other);       // 差集
```

---

## 8. 字符串操作

### 8.1 string 类

```csharp
string s1 = "Hello";
string s2 = "World";

// 拼接
string s3 = s1 + " " + s2;       // "Hello World"
string s4 = string.Concat(s1, s2);

// 长度
int len = s1.Length;

// 查找
bool contains = s1.Contains("el");
int index = s1.IndexOf('l');     // 2
bool startsWith = s1.StartsWith("He");
bool endsWith = s1.EndsWith("lo");

// 提取子串
string sub = s1.Substring(1, 3);  // "ell"

// 分割
string[] parts = "a,b,c".Split(',');

// 替换
string replaced = s1.Replace('l', 'L');  // "HeLLo"

// 大小写
string upper = s1.ToUpper();
string lower = s1.ToLower();

// 去空白
string trimmed = "  hello  ".Trim();
string trimStart = "  hello".TrimStart();
string trimEnd = "hello  ".TrimEnd();

// 空字符串判断
bool isEmpty = string.IsNullOrEmpty(s1);
bool isWhiteSpace = string.IsNullOrWhiteSpace(s1);
```

### 8.2 字符串格式化与插值

```csharp
// 复合格式化
string fmt = string.Format("姓名：{0}，年龄：{1}", "张三", 25);

// 字符串插值（C# 6.0+，推荐）
string name = "张三";
int age = 25;
string interpolated = $"姓名：{name}，年龄：{age}";

// 插值中的格式
double price = 19.99;
string priceStr = $"价格：{price:C2}";       // 货币格式
string dateStr = $"日期：{DateTime.Now:yyyy-MM-dd}";

// 原始字符串（C# 11.0+）
string json = """
{
    "name": "张三",
    "age": 25
}
""";
```

### 8.3 StringBuilder

当需要频繁修改字符串时使用，避免创建大量临时字符串对象。

```csharp
using System.Text;

StringBuilder sb = new StringBuilder();
sb.Append("Hello");
sb.Append(" ");
sb.AppendLine("World");   // 追加并换行
sb.AppendFormat("年龄：{0}", 25);

// 插入
sb.Insert(0, "前缀：");

// 删除
sb.Remove(0, 3);

// 替换
sb.Replace("World", "C#");

// 转换为 string
string result = sb.ToString();
```

---

## 9. 面向对象编程

### 9.1 类与对象

```csharp
// 类定义
public class Person
{
    // 字段（私有）
    private string _name;
    private int _age;

    // 属性
    public string Name
    {
        get { return _name; }
        set { _name = value; }
    }

    // 自动属性（编译器自动生成 backing field）
    public int Age { get; set; }

    // 只读属性
    public string Description { get; }

    // 构造函数
    public Person(string name, int age)
    {
        _name = name;
        Age = age;
        Description = $"{name} ({age}岁)";
    }

    // 方法
    public void SayHello()
    {
        Console.WriteLine($"你好，我是{_name}");
    }

    // 析构函数（垃圾回收前调用，很少使用）
    ~Person()
    {
        // 清理非托管资源
    }
}

// 创建对象
Person p = new Person("张三", 25);
p.SayHello();
```

### 9.2 继承

```csharp
// 基类
public class Animal
{
    public string Name { get; set; }
    public virtual void Speak()
    {
        Console.WriteLine("动物发出声音");
    }
}

// 派生类
public class Dog : Animal
{
    public string Breed { get; set; }

    // 重写基类方法
    public override void Speak()
    {
        Console.WriteLine("汪汪汪！");
    }
}

public class Cat : Animal
{
    public override void Speak()
    {
        Console.WriteLine("喵喵喵！");
    }
}
```

### 9.3 多态

```csharp
// 基类引用指向派生类对象
Animal myDog = new Dog { Name = "旺财" };
Animal myCat = new Cat { Name = "咪咪" };

// 调用 Speak 时，根据实际类型执行不同实现（运行时多态）
myDog.Speak();  // 汪汪汪！
myCat.Speak();  // 喵喵喵！

// 多态数组
Animal[] animals = { myDog, myCat };
foreach (Animal a in animals)
{
    a.Speak();  // 根据实际类型调用对应方法
}
```

### 9.4 接口

```csharp
// 接口定义
public interface IFlyable
{
    void Fly();   // 接口方法，无实现
    int Speed { get; }
}

// 接口实现
public class Bird : Animal, IFlyable
{
    public int Speed => 30;

    public void Fly()
    {
        Console.WriteLine("鸟儿在飞翔");
    }

    public override void Speak()
    {
        Console.WriteLine("叽叽喳喳");
    }
}
```

### 9.5 抽象类

```csharp
public abstract class Shape
{
    public abstract double Area { get; }  // 抽象属性
    public abstract double Perimeter { get; }

    public void PrintInfo()  // 普通方法
    {
        Console.WriteLine($"面积：{Area:F2}，周长：{Perimeter:F2}");
    }
}

public class Circle : Shape
{
    public double Radius { get; set; }
    public override double Area => Math.PI * Radius * Radius;
    public override double Perimeter => 2 * Math.PI * Radius;
}
```

### 9.6 记录类型（Record）

C# 9.0 引入，值比较的不可变类型。

```csharp
public record Student(string Name, int Age);  // 主构造函数

// 使用
var s1 = new Student("张三", 20);
var s2 = new Student("张三", 20);
bool equal = s1 == s2;  // true，值比较

// with 表达式创建副本并修改
var s3 = s1 with { Age = 21 };
```

---

## 10. 异常处理

### 10.1 try/catch/finally

```csharp
try
{
    // 可能抛出异常的代码
    int result = 10 / int.Parse("0");
}
catch (DivideByZeroException ex)
{
    // 捕获特定异常
    Console.WriteLine($"除以零错误：{ex.Message}");
}
catch (FormatException ex)
{
    Console.WriteLine($"格式错误：{ex.Message}");
}
catch (Exception ex)
{
    // 捕获所有其他异常（放在最后）
    Console.WriteLine($"发生错误：{ex.Message}");
}
finally
{
    // 无论是否发生异常都会执行
    // 常用于资源清理
    Console.WriteLine("执行完毕");
}
```

### 10.2 throw 抛出异常

```csharp
// 抛出系统异常
void CheckAge(int age)
{
    if (age < 0)
    {
        throw new ArgumentOutOfRangeException(nameof(age), "年龄不能为负数");
    }
}

// 重新抛出异常（保留调用栈）
try
{
    // ...
}
catch (Exception ex)
{
    // 记录日志
    throw;  // 使用 throw; 而不是 throw ex;
}
```

### 10.3 自定义异常

```csharp
public class SecurityException : Exception
{
    public SecurityException() { }
    public SecurityException(string message) : base(message) { }
    public SecurityException(string message, Exception inner)
        : base(message, inner) { }
}

// 使用
throw new SecurityException("检测到 SQL 注入攻击");
```

### 10.4 using 语句

自动释放实现了 `IDisposable` 接口的对象。

```csharp
// using 语句（自动调用 Dispose）
using (StreamReader reader = new StreamReader("file.txt"))
{
    string content = reader.ReadToEnd();
}

// using 声明（C# 8.0+）
using StreamWriter writer = new StreamWriter("output.txt");
writer.WriteLine("Hello");
// 方法结束时自动释放
```

---

## 11. 委托与事件

### 11.1 委托（Delegate）

委托是一种类型安全的函数指针。

```csharp
// 声明委托类型
public delegate int MathDelegate(int a, int b);

// 使用
int Add(int a, int b) => a + b;
int Subtract(int a, int b) => a - b;

MathDelegate mathOp = Add;
int result = mathOp(10, 5);  // 15

mathOp = Subtract;
result = mathOp(10, 5);  // 5

// 多播委托
mathOp += Add;   // 依次调用
mathOp -= Add;
```

### 11.2 内置委托类型

```csharp
// Func：有返回值的泛型委托
Func<int, int, int> add = (a, b) => a + b;

// Action：无返回值的泛型委托
Action<string> print = msg => Console.WriteLine(msg);

// Predicate：返回 bool 的泛型委托
Predicate<int> isPositive = x => x > 0;
```

### 11.3 Lambda 表达式

```csharp
// 语法：(参数列表) => 表达式/语句块
Func<int, int> square = x => x * x;
Func<int, int, int> sum = (a, b) => a + b;

Action<string> greet = name =>
{
    string msg = $"你好，{name}！";
    Console.WriteLine(msg);
};

// 结合 LINQ 使用
var numbers = new List<int> { 1, 2, 3, 4, 5 };
var evens = numbers.Where(n => n % 2 == 0).ToList();
```

### 11.4 事件（Event）

事件是委托的封装，实现发布-订阅模式。

```csharp
public class Button
{
    // 声明事件
    public event EventHandler? Click;

    // 触发事件
    public void OnClick()
    {
        Click?.Invoke(this, EventArgs.Empty);
    }
}

// 订阅事件
Button btn = new Button();
btn.Click += (sender, e) => Console.WriteLine("按钮被点击了！");

btn.OnClick();  // 触发
```

---

## 12. LINQ 基础

LINQ（Language Integrated Query）提供统一的查询语法操作各种数据源。

### 12.1 查询语法

```csharp
using System.Linq;

int[] numbers = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };

// 查询语法（类似 SQL）
var evenNumbers = from n in numbers
                  where n % 2 == 0
                  orderby n descending
                  select n * 2;
```

### 12.2 方法语法

```csharp
// 方法语法（更常用）
var evens = numbers.Where(n => n % 2 == 0)
                   .OrderByDescending(n => n)
                   .Select(n => n * 2);

// 常用操作符
var count = numbers.Count(n => n > 5);
var sum = numbers.Sum();
var avg = numbers.Average();
var max = numbers.Max();
var min = numbers.Min();

var first = numbers.First(n => n > 5);       // 第一个匹配项
var firstOrDefault = numbers.FirstOrDefault(n => n > 100);  // 没有则返回默认值

var any = numbers.Any(n => n > 10);          // 是否存在
var all = numbers.All(n => n > 0);           // 是否全部满足

var skipTake = numbers.Skip(5).Take(3);      // 分页

var groups = numbers.GroupBy(n => n % 2);    // 分组
```

### 12.3 复杂对象查询

```csharp
var people = new List<Person>
{
    new Person { Name = "张三", Age = 25, City = "北京" },
    new Person { Name = "李四", Age = 30, City = "上海" },
    new Person { Name = "王五", Age = 22, City = "北京" },
};

// 查询北京的年轻人，按年龄排序
var youngBeijing = people
    .Where(p => p.City == "北京" && p.Age < 30)
    .OrderBy(p => p.Age)
    .Select(p => new { p.Name, p.Age })  // 投影到匿名类型
    .ToList();
```

---

## 13. 异步编程 async/await

C# 5.0 引入的异步编程模型，简化异步代码编写。

### 13.1 基本用法

```csharp
using System.Net.Http;

// 异步方法
async Task<string> FetchDataAsync(string url)
{
    using HttpClient client = new HttpClient();
    string result = await client.GetStringAsync(url);  // 等待时不阻塞线程
    return result;
}

// 调用
async Task DoWorkAsync()
{
    string data = await FetchDataAsync("https://example.com");
    Console.WriteLine(data);
}
```

### 13.2 返回值类型

```csharp
// 无返回值
async Task DoSomethingAsync()
{
    await Task.Delay(1000);
}

// 有返回值
async Task<int> GetValueAsync()
{
    await Task.Delay(1000);
    return 42;
}

// 异步事件处理程序可用 async void（尽量避免）
async void Button_Click(object sender, EventArgs e)
{
    await DoSomethingAsync();
}
```

### 13.3 并行执行

```csharp
async Task<string[]> FetchAllAsync()
{
    Task<string> t1 = FetchDataAsync("https://api.example.com/1");
    Task<string> t2 = FetchDataAsync("https://api.example.com/2");
    Task<string> t3 = FetchDataAsync("https://api.example.com/3");

    // 等待所有任务完成
    string[] results = await Task.WhenAll(t1, t2, t3);
    return results;
}

// 等待任一任务完成
Task<string> firstCompleted = await Task.WhenAny(t1, t2, t3);
```

### 13.4 Task.Run

将 CPU 密集型工作放到后台线程。

```csharp
async Task<int> HeavyComputationAsync()
{
    return await Task.Run(() =>
    {
        // 耗时计算
        int sum = 0;
        for (int i = 0; i < 1000000000; i++) sum += i;
        return sum;
    });
}
```

---

## 14. 文件操作

位于 `System.IO` 命名空间。

### 14.1 文件读写

```csharp
// 读取全部文本
string content = File.ReadAllText("test.txt", Encoding.UTF8);

// 写入文本（覆盖）
File.WriteAllText("output.txt", "Hello World", Encoding.UTF8);

// 追加文本
File.AppendAllText("log.txt", "新的日志行\n");

// 读取所有行
string[] lines = File.ReadAllLines("test.txt");

// 写入所有行
File.WriteAllLines("output.txt", new[] { "第一行", "第二行" });
```

### 14.2 文件和目录操作

```csharp
// 判断文件是否存在
if (File.Exists("test.txt")) { }

// 复制文件
File.Copy("source.txt", "dest.txt", overwrite: true);

// 移动文件
File.Move("source.txt", "dest.txt");

// 删除文件
File.Delete("test.txt");

// 创建目录
Directory.CreateDirectory("mydir");

// 判断目录是否存在
if (Directory.Exists("mydir")) { }

// 获取目录下的文件
string[] files = Directory.GetFiles("mydir", "*.txt");

// 获取子目录
string[] dirs = Directory.GetDirectories("mydir");
```

### 14.3 流操作

```csharp
// StreamReader 读取
using StreamReader sr = new StreamReader("test.txt", Encoding.UTF8);
string? line;
while ((line = sr.ReadLine()) != null)
{
    Console.WriteLine(line);
}

// StreamWriter 写入
using StreamWriter sw = new StreamWriter("output.txt", append: true);
sw.WriteLine("新内容");

// FileStream 二进制操作
using FileStream fs = new FileStream("data.bin", FileMode.Create);
byte[] data = { 0x48, 0x65, 0x6C, 0x6C, 0x6F };
fs.Write(data, 0, data.Length);
```

---

## 15. 网络请求（HttpClient）

### 15.1 GET 请求

```csharp
using System.Net.Http;
using System.Net.Http.Headers;

// HttpClient 设计为单例使用（全局共享一个实例）
// 正确做法：使用静态单例或依赖注入
static readonly HttpClient _httpClient = new HttpClient();

async Task<string> GetAsync(string url)
{
    HttpResponseMessage response = await _httpClient.GetAsync(url);
    response.EnsureSuccessStatusCode();  // 确保成功，否则抛出异常
    string content = await response.Content.ReadAsStringAsync();
    return content;
}
```

### 15.2 POST 请求

```csharp
async Task<string> PostJsonAsync(string url, string jsonContent)
{
    var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
    HttpResponseMessage response = await _httpClient.PostAsync(url, content);
    response.EnsureSuccessStatusCode();
    return await response.Content.ReadAsStringAsync();
}

// 发送表单数据
async Task<string> PostFormAsync(string url)
{
    var formData = new Dictionary<string, string>
    {
        ["username"] = "admin",
        ["password"] = "123456"
    };
    var content = new FormUrlEncodedContent(formData);
    HttpResponseMessage response = await _httpClient.PostAsync(url, content);
    return await response.Content.ReadAsStringAsync();
}
```

### 15.3 自定义 Header

```csharp
// 设置默认请求头（所有请求都携带）
_httpClient.DefaultRequestHeaders.Add("User-Agent", "MyApp/1.0");
_httpClient.DefaultRequestHeaders.Authorization =
    new AuthenticationHeaderValue("Bearer", "token-here");

// 针对单个请求设置头
var request = new HttpRequestMessage(HttpMethod.Get, url);
request.Headers.Add("X-Custom-Header", "value");
request.Headers.Referrer = new Uri("https://example.com");

HttpResponseMessage response = await _httpClient.SendAsync(request);
```

### 15.4 处理 JSON

```csharp
using System.Text.Json;

// 反序列化 JSON
string json = await _httpClient.GetStringAsync(url);
var user = JsonSerializer.Deserialize<User>(json);

// 序列化对象
var data = new { Name = "张三", Age = 25 };
string jsonStr = JsonSerializer.Serialize(data);
```

---

## 16. 正则表达式（Regex）

位于 `System.Text.RegularExpressions` 命名空间。

### 16.1 基本匹配

```csharp
using System.Text.RegularExpressions;

// 判断是否匹配
string pattern = @"^\d+$";
bool isMatch = Regex.IsMatch("12345", pattern);  // true

// 匹配单个
Match match = Regex.Match("abc123def", @"\d+");
if (match.Success)
{
    string value = match.Value;  // "123"
    int index = match.Index;     // 3
}

// 匹配所有
MatchCollection matches = Regex.Matches("a1b2c3", @"\d");
foreach (Match m in matches)
{
    Console.WriteLine(m.Value);  // "1", "2", "3"
}
```

### 16.2 分组捕获

```csharp
string text = "2024-01-15";
Match m = Regex.Match(text, @"(\d{4})-(\d{2})-(\d{2})");

if (m.Success)
{
    string year = m.Groups[1].Value;   // "2024"
    string month = m.Groups[2].Value;  // "01"
    string day = m.Groups[3].Value;    // "15"
}

// 命名分组
Match m2 = Regex.Match(text, @"(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})");
string y = m2.Groups["year"].Value;
```

### 16.3 替换

```csharp
// 简单替换
string result = Regex.Replace("abc123def456", @"\d", "*");
// "abc***def***"

// 使用 MatchEvaluator
string result2 = Regex.Replace("Hello World", @"\w+", m => m.Value.ToUpper());
// "HELLO WORLD"
```

### 16.4 常用正则模式

```csharp
// 邮箱
string emailPattern = @"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$";

// 手机号（中国）
string phonePattern = @"^1[3-9]\d{9}$";

// IP 地址（简化版）
string ipPattern = @"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$";

// URL
string urlPattern = @"^https?://[^\s/$.?#].[^\s]*$";

// HTML 标签（不推荐用正则解析 HTML）
string tagPattern = @"<[^>]+>";
```

### 16.5 RegexOptions

```csharp
// 忽略大小写
Regex.IsMatch("Hello", "hello", RegexOptions.IgnoreCase);

// 多行模式
Regex.Matches(text, pattern, RegexOptions.Multiline);

// 编译正则（提高性能，首次编译耗时）
Regex regex = new Regex(pattern, RegexOptions.Compiled);
regex.IsMatch(input);
```

---

## 17. C#/.NET 在安全领域的应用

### 17.1 ASP.NET 常见安全漏洞

**1. SQL 注入**

```csharp
// 危险代码：字符串拼接 SQL
string sql = $"SELECT * FROM Users WHERE Username='{username}' AND Password='{password}'";
// 攻击者输入：' OR '1'='1

// 安全做法：参数化查询
using (var cmd = new SqlCommand("SELECT * FROM Users WHERE Username=@u AND Password=@p", conn))
{
    cmd.Parameters.AddWithValue("@u", username);
    cmd.Parameters.AddWithValue("@p", password);
}

// 更推荐：使用 Entity Framework Core（自动参数化）
var user = dbContext.Users
    .FirstOrDefault(u => u.Username == username && u.Password == password);
```

**2. XSS 跨站脚本攻击**

ASP.NET Core 默认对 Razor 视图输出进行 HTML 编码：
```csharp
// Razor 中：@Model.Content 自动编码
// 危险：@Html.Raw(Model.Content) —— 直接输出原始 HTML

// 安全做法：输出时编码，输入时验证
```

**3. CSRF 跨站请求伪造**

```csharp
// ASP.NET Core MVC 中使用防伪标记
// 视图中：@Html.AntiForgeryToken()
// Action 上：[ValidateAntiForgeryToken]

// 推荐使用 ASP.NET Core Identity 内置的 CSRF 保护
```

**4. 身份认证与授权**

```csharp
// ASP.NET Core Identity
// JWT Bearer 认证
// [Authorize] 属性保护接口
```

### 17.2 .NET 反序列化漏洞

.NET 反序列化是高危漏洞类型，常见于：

**BinaryFormatter 反序列化：**
```csharp
// 危险：BinaryFormatter 反序列化不受信任的数据
IFormatter formatter = new BinaryFormatter();
Stream stream = File.OpenRead("data.bin");
object obj = formatter.Deserialize(stream);  // 危险！可能执行恶意代码

// 安全建议：
// - 不要使用 BinaryFormatter 反序列化外部输入
// - 使用 System.Text.Json 或 XmlSerializer
// - 启用类型白名单
```

**常见攻击载荷：**
- TypeConfuseDelegate
- TextFormattingRunProperties
- ObjectDataProvider
- PSObject（PowerShell）

**检测工具：**
- dnSpy / ILSpy：反编译 .NET 程序
- ILRecompile：动态分析
- YSoSerial.Net：生成反序列化 payload

### 17.3 代码审计要点

**输入验证：**
- 检查所有用户输入是否经过验证
- 查找 `[ValidateInput(false)]` 特性
- 检查 `Request.Form`, `Request.QueryString`, `Request.Headers` 的使用

**文件操作：**
- 路径遍历漏洞：检查 `Path.Combine` 是否过滤了 `../`
- 文件上传：检查文件类型、扩展名、存储位置验证

**加密与安全：**
- 查找硬编码的密钥、密码
- 检查是否使用弱加密算法（MD5、SHA1、DES）
- 推荐使用 SHA256/SHA512 哈希、AES 加密

```csharp
// 弱密码哈希（危险）
string hash = FormsAuthentication.HashPasswordForStoringInConfigFile(password, "MD5");

// 安全做法：使用 ASP.NET Core Identity 的 PasswordHasher
// 或使用 BCrypt / PBKDF2
```

**权限控制：**
- 检查 `[Authorize]` 属性是否遗漏
- 检查是否存在越权访问（IDOR）

### 17.4 安全工具开发

C# 常用于开发安全工具，示例：

**端口扫描器：**
```csharp
// 使用 TcpClient 进行端口扫描
async Task<bool> IsPortOpen(string host, int port, int timeoutMs = 1000)
{
    try
    {
        using TcpClient client = new TcpClient();
        var connectTask = client.ConnectAsync(host, port);
        var timeoutTask = Task.Delay(timeoutMs);
        var completed = await Task.WhenAny(connectTask, timeoutTask);
        return completed == connectTask;
    }
    catch
    {
        return false;
    }
}
```

**Web 目录扫描器：**
```csharp
async Task<bool> CheckPath(string baseUrl, string path)
{
    try
    {
        var response = await _httpClient.GetAsync($"{baseUrl.TrimEnd('/')}/{path}");
        return response.StatusCode == System.Net.HttpStatusCode.OK;
    }
    catch
    {
        return false;
    }
}
```

### 17.5 逆向工程与恶意代码分析

**.NET 程序特点：**
- 编译为中间语言（IL/MSIL），易于反编译
- 可使用 dnSpy、ILSpy、dotPeek 等工具还原源代码
- 混淆器：ConfuserEx、Dotfuscator、Obfuscar 等增加逆向难度

**分析 .NET 恶意软件常用工具：**
- **dnSpy**：开源 .NET 调试器和反编译器
- **ILSpy**：开源反编译器
- **de4dot**：.NET 脱壳/去混淆工具
- **CFF Explorer**：PE 文件分析
- **Process Hacker**：进程监控

**常见 .NET 恶意软件家族：**
- Agent Tesla（窃密木马）
- Remcos RAT（远控木马）
- LimeRAT
- NanoCore RAT
- AsyncRAT

---

## 参考资源

- [C# 官方文档](https://docs.microsoft.com/zh-cn/dotnet/csharp/)
- [ASP.NET Core 安全文档](https://docs.microsoft.com/zh-cn/aspnet/core/security/)
- [OWASP .NET 安全指南](https://owasp.org/www-project-dotnet-security/)
- [YSoSerial.Net](https://github.com/pwntester/ysoserial.net)
- [dnSpy](https://github.com/dnSpy/dnSpy)

---

## 学习资源与知识拓展

### 官方资源

- **C# 官方文档**：各语言官网提供最权威的文档和教程
- **C# 标准库参考**：官方标准库 API 文档

### 在线教程

- **菜鸟教程 C#**：https://www.runoob.com/ — 中文入门教程
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

- 《C#程序设计》— 入门经典教材
- 《C#高级编程》— 进阶学习指南
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
