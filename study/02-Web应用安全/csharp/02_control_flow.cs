// ============================================================
// 02_control_flow.cs - if/else、for、foreach、while、switch、模式匹配
// 运行方式：dotnet run --project .  或  csc 02_control_flow.cs && 02_control_flow.exe
// ============================================================

using System;
using System.Collections.Generic;

// ---------- 1. if / else 条件语句 ----------
Console.WriteLine("========== 1. if / else 条件语句 ==========");

int score = 85;
Console.WriteLine($"分数：{score}");

if (score >= 90)
{
    Console.WriteLine("等级：优秀 (A)");
}
else if (score >= 80)
{
    Console.WriteLine("等级：良好 (B)");
}
else if (score >= 60)
{
    Console.WriteLine("等级：及格 (C)");
}
else
{
    Console.WriteLine("等级：不及格 (D)");
}

// 多条件判断
int age = 25;
if (age >= 18 && age < 30)
{
    Console.WriteLine($"年龄 {age}：青年");
}
else if (age >= 30 && age < 60)
{
    Console.WriteLine($"年龄 {age}：中年");
}
else
{
    Console.WriteLine($"年龄 {age}：其他");
}

// 嵌套 if
bool isVip = true;
decimal total = 150m;
if (total > 100)
{
    if (isVip)
    {
        Console.WriteLine($"VIP 客户，消费 {total} 元，享受 8 折优惠：{total * 0.8m}");
    }
    else
    {
        Console.WriteLine($"普通客户，消费 {total} 元，享受 9 折优惠：{total * 0.9m}");
    }
}

// 三元运算符（简化版 if/else）
string status = age >= 18 ? "成年" : "未成年";
Console.WriteLine($"三元运算：{age}岁 -> {status}");
Console.WriteLine();

// ---------- 2. for 循环 ----------
Console.WriteLine("========== 2. for 循环 ==========");

Console.WriteLine("从 1 到 5：");
for (int i = 1; i <= 5; i++)
{
    Console.WriteLine($"  i = {i}");
}

// 计算 1 到 100 的和
int sum = 0;
for (int i = 1; i <= 100; i++)
{
    sum += i;
}
Console.WriteLine($"1 到 100 的和：{sum}");

// 倒序循环
Console.WriteLine("倒序输出 10 到 1：");
for (int i = 10; i >= 1; i--)
{
    Console.Write($"{i} ");
}
Console.WriteLine();

// 多层循环（九九乘法表）
Console.WriteLine("九九乘法表：");
for (int i = 1; i <= 9; i++)
{
    for (int j = 1; j <= i; j++)
    {
        Console.Write($"{j}x{i}={i * j,-2} ");
    }
    Console.WriteLine();
}
Console.WriteLine();

// ---------- 3. foreach 循环 ----------
Console.WriteLine("========== 3. foreach 循环 ==========");

// 遍历数组
string[] fruits = { "苹果", "香蕉", "橙子", "葡萄", "西瓜" };
Console.WriteLine("水果列表：");
foreach (string fruit in fruits)
{
    Console.WriteLine($"  - {fruit}");
}

// 遍历 List
List<int> numbers = new List<int> { 10, 20, 30, 40, 50 };
Console.WriteLine("\n数字列表：");
foreach (int num in numbers)
{
    Console.Write($"{num} ");
}
Console.WriteLine();

// 遍历字典
Dictionary<string, int> cityPopulations = new Dictionary<string, int>
{
    ["北京"] = 2154,
    ["上海"] = 2428,
    ["广州"] = 1530,
    ["深圳"] = 1344
};
Console.WriteLine("\n城市人口（万人）：");
foreach (var kvp in cityPopulations)
{
    Console.WriteLine($"  {kvp.Key}：{kvp.Value} 万");
}
Console.WriteLine();

// ---------- 4. while 循环 ----------
Console.WriteLine("========== 4. while 循环 ==========");

// 基本用法
int count = 1;
Console.WriteLine("while 循环 1 到 5：");
while (count <= 5)
{
    Console.Write($"{count} ");
    count++;
}
Console.WriteLine();

// 使用 while 查找
int target = 7;
int guess = 0;
int attempts = 0;
Random rnd = new Random();
while (guess != target)
{
    guess = rnd.Next(1, 11);  // 1-10 随机数
    attempts++;
}
Console.WriteLine($"猜数字游戏：猜了 {attempts} 次才猜到 {target}");

// break 跳出循环
Console.WriteLine("\nbreak 示例（找到第一个能被 7 整除的数）：");
for (int i = 1; i <= 100; i++)
{
    if (i % 7 == 0)
    {
        Console.WriteLine($"找到：{i}");
        break;  // 立即跳出循环
    }
}

// continue 跳过当前迭代
Console.WriteLine("\ncontinue 示例（输出 1-10 中的奇数）：");
for (int i = 1; i <= 10; i++)
{
    if (i % 2 == 0)
    {
        continue;  // 跳过偶数
    }
    Console.Write($"{i} ");
}
Console.WriteLine();
Console.WriteLine();

// ---------- 5. do-while 循环 ----------
Console.WriteLine("========== 5. do-while 循环 ==========");

// do-while 至少执行一次
int counter = 6;
Console.WriteLine("do-while 循环（counter 初始为 6）：");
do
{
    Console.WriteLine($"  counter = {counter}");
    counter++;
} while (counter <= 5);  // 条件为 false，但仍执行了一次

// 模拟用户输入验证
string input;
int validNum;
Console.WriteLine("\n模拟输入验证循环（使用预设值）：");
string[] testInputs = { "abc", "123" };
int inputIndex = 0;
do
{
    input = testInputs[inputIndex++];
    Console.WriteLine($"  输入：\"{input}\"");
    if (int.TryParse(input, out validNum))
    {
        Console.WriteLine($"  验证成功，数字：{validNum}");
        break;
    }
    else
    {
        Console.WriteLine($"  验证失败，请重新输入");
    }
} while (inputIndex < testInputs.Length);
Console.WriteLine();

// ---------- 6. switch 语句 ----------
Console.WriteLine("========== 6. switch 语句 ==========");

// 传统 switch-case
int dayOfWeek = 3;
Console.WriteLine($"星期 {dayOfWeek}：");
switch (dayOfWeek)
{
    case 1:
        Console.WriteLine("星期一");
        break;
    case 2:
        Console.WriteLine("星期二");
        break;
    case 3:
        Console.WriteLine("星期三");
        break;
    case 4:
        Console.WriteLine("星期四");
        break;
    case 5:
        Console.WriteLine("星期五");
        break;
    case 6:
    case 7:
        Console.WriteLine("周末");
        break;
    default:
        Console.WriteLine("无效的日期");
        break;
}

// switch 中的 goto（少见用法）
Console.WriteLine("\n使用 goto 贯穿（不推荐）：");
int num = 2;
switch (num)
{
    case 1:
        Console.WriteLine("  执行 case 1");
        goto case 2;
    case 2:
        Console.WriteLine("  执行 case 2");
        break;
}

// switch 表达式（C# 8.0+，更简洁的写法）
int dayNum = 5;
string dayName = dayNum switch
{
    1 => "星期一",
    2 => "星期二",
    3 => "星期三",
    4 => "星期四",
    5 => "星期五",
    6 or 7 => "周末",     // C# 9.0+ 逻辑模式
    _ => "无效日期"         // 默认值
};
Console.WriteLine($"\nswitch 表达式：星期 {dayNum} -> {dayName}");
Console.WriteLine();

// ---------- 7. 模式匹配 ----------
Console.WriteLine("========== 7. 模式匹配 ==========");

// 7.1 类型模式（is 模式）
object obj1 = "Hello World";
object obj2 = 12345;
object obj3 = null;

Console.WriteLine("类型模式（is 模式）：");
if (obj1 is string str1)
{
    Console.WriteLine($"  obj1 是字符串，长度：{str1.Length}");
}

if (obj2 is int intVal)
{
    Console.WriteLine($"  obj2 是整数，值：{intVal}");
}

if (obj3 is null)
{
    Console.WriteLine("  obj3 是 null");
}

if (obj1 is not null)
{
    Console.WriteLine("  obj1 不是 null");
}

// 7.2 关系模式（C# 9.0+）
int testAge = 25;
Console.WriteLine($"\n关系模式：年龄 {testAge}");
string ageGroup = testAge switch
{
    < 0 => "无效",
    < 18 => "未成年",
    < 30 => "青年",
    < 60 => "中年",
    < 120 => "老年",
    _ => "无效"
};
Console.WriteLine($"  年龄段：{ageGroup}");

// 7.3 逻辑模式（C# 9.0+）
int testScore = 85;
Console.WriteLine($"\n逻辑模式：分数 {testScore}");
string grade = testScore switch
{
    < 0 or > 100 => "无效分数",
    >= 90 and <= 100 => "优秀",
    >= 80 and < 90 => "良好",
    >= 60 and < 80 => "及格",
    < 60 => "不及格"
};
Console.WriteLine($"  等级：{grade}");

// 7.4 属性模式
Console.WriteLine("\n属性模式：");
var person = new { Name = "张三", Age = 25, City = "北京" };
if (person is { Age: >= 18, City: "北京" })
{
    Console.WriteLine($"  {person.Name} 是北京的成年人");
}

// 属性模式 + switch
string description = person switch
{
    { Age: < 18 } => "未成年人",
    { Age: >= 18, City: "北京" } => "北京成年人",
    { Age: >= 18, City: "上海" } => "上海成年人",
    _ => "其他"
};
Console.WriteLine($"  描述：{description}");

// 7.5 元组模式
Console.WriteLine("\n元组模式：");
(string color, string shape) item = ("红色", "圆形");
string itemDesc = item switch
{
    ("红色", "圆形") => "红色圆形",
    ("蓝色", "方形") => "蓝色方形",
    ("红色", _) => "红色其他形状",
    (_, "圆形") => "其他颜色圆形",
    _ => "其他"
};
Console.WriteLine($"  描述：{itemDesc}");

// 7.6 列表模式（C# 11.0+）
Console.WriteLine("\n列表模式：");
int[] arr = { 1, 2, 3 };
string arrDesc = arr switch
{
    [] => "空数组",
    [1] => "只有一个元素 1",
    [1, 2, 3] => "数组 [1,2,3]",
    [_, _, _] => "三个元素的数组",
    _ => "其他数组"
};
Console.WriteLine($"  描述：{arrDesc}");

Console.WriteLine();
Console.WriteLine("========== 程序结束 ==========");
