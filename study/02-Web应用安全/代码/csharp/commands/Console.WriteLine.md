# Console.WriteLine

> **分类**：输出
> **说明**：C# 控制台输出

---

## 语法

```csharp
Console.WriteLine(value);
```

## 常用方法

WriteLine / Write / ReadLine / ReadKey / Read

## 格式化

字符串插值 $"..." / String.Format / 复合格式化

## 示例代码

```csharp
using System;

class Program {
    static void Main() {
        // 基本输出
        Console.WriteLine("Hello, World!");
        Console.WriteLine(42);
        Console.WriteLine(3.14);

        // 不换行
        Console.Write("输入: ");

        // 字符串插值（推荐）
        string name = "Alice";
        int age = 25;
        Console.WriteLine($"姓名: {name}, 年龄: {age}");

        // 格式化字符串
        Console.WriteLine("PI = {0:F2}", Math.PI);
        Console.WriteLine("{0,10} | {1,5}", "名称", "价格");  // 对齐

        // String.Format
        string msg = string.Format("{0} 今年 {1} 岁", name, age);
        Console.WriteLine(msg);

        // 读取输入
        // string input = Console.ReadLine();
        // Console.WriteLine("你输入了: " + input);

        // 读取单个按键
        // ConsoleKeyInfo key = Console.ReadKey();

        // 颜色输出
        Console.ForegroundColor = ConsoleColor.Red;
        Console.WriteLine("红色文字");
        Console.ForegroundColor = ConsoleColor.Green;
        Console.WriteLine("绿色文字");
        Console.ResetColor();

        // 背景色
        Console.BackgroundColor = ConsoleColor.Yellow;
        Console.WriteLine("黄底黑字");
        Console.ResetColor();

        // 清空屏幕
        // Console.Clear();

        // 设置光标位置
        // Console.SetCursorPosition(10, 5);
        // Console.Write("在(10,5)位置");

        // 错误输出
        Console.Error.WriteLine("错误信息");
    }
}
```
