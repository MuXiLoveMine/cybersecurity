# variable_cs

> **分类**：变量与类型
> **说明**：C# 变量和数据类型

---

## 语法

```csharp
type variableName = value;\nvar variableName = value;  // 类型推断
```

## 值类型

bool / byte / sbyte / char / short / ushort / int / uint / long / ulong / float / double / decimal / enum / struct

## 引用类型

string / object / class / interface / delegate / array / dynamic

## 可空类型

int? / Nullable<T>

## 示例代码

```csharp
using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        // 整数类型
        int i = 42;
        long l = 9223372036854775807L;
        short s = 32767;
        byte b = 255;
        uint ui = 4294967295;

        // 浮点类型
        float f = 3.14f;
        double d = 3.1415926535;
        decimal m = 9.99m;  // 高精度，适合金融

        // 字符和布尔
        char c = 'A';
        bool flag = true;

        // 字符串
        string str = "Hello, C#!";
        Console.WriteLine(str.Length);       // 长度
        Console.WriteLine(str.Substring(0, 5)); // 子串
        Console.WriteLine(str.ToUpper());    // 大写
        Console.WriteLine(str.ToLower());    // 小写

        // 字符串插值
        string name = "Alice";
        int age = 25;
        string greeting = $"你好, {name}, 今年 {age} 岁";

        // 逐字字符串（不转义反斜杠）
        string path = @"C:\Users\name\file.txt";

        // var 类型推断
        var number = 42;           // int
        var text = "hello";        // string
        var list = new List<int>();// List<int>

        // const 常量
        const int MaxSize = 100;
        const double Pi = 3.14159;

        // 可空类型
        int? nullableInt = null;
        int value = nullableInt ?? 0;  // 空合并运算符

        if (nullableInt.HasValue) {
            Console.WriteLine(nullableInt.Value);
        }

        // 类型转换
        int num = int.Parse("123");
        double dbl = double.Parse("3.14");
        string strNum = 456.ToString();

        int a = (int)3.14;      // 强制转换
        string s = 42 as string; // as 转换（失败返回 null，仅引用类型）

        // 类型检查
        if (obj is string) {
            Console.WriteLine("是字符串");
        }

        // 数组
        int[] nums = { 1, 2, 3, 4, 5 };
        int first = nums[0];
        int len = nums.Length;

        string[] names = new string[3];
        names[0] = "Alice";

        // 多维数组
        int[,] matrix = new int[3, 3];
        matrix[0, 0] = 1;

        // 交错数组
        int[][] jagged = new int[3][];
        jagged[0] = new int[] { 1, 2 };

        // 枚举
        enum Color { Red, Green, Blue }
        Color color = Color.Red;
    }
}
```
