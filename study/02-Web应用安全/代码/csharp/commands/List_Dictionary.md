# List_Dictionary

> **分类**：集合框架
> **说明**：C# 常用泛型集合

---

## 语法

```csharp
List<T> list = new List<T>();\nDictionary<K,V> dict = new Dictionary<K,V>();
```

## 常用集合

List<T> / Dictionary<TKey,TValue> / HashSet<T> / Queue<T> / Stack<T> / SortedList<T> / LinkedList<T>

## LINQ

Where / Select / OrderBy / GroupBy / First / FirstOrDefault / Any / All / Count / Sum / Max / Min

## 示例代码

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

class Program {
    static void Main() {
        // ===== List<T> =====
        var fruits = new List<string> { "apple", "banana", "cherry" };

        // 添加
        fruits.Add("orange");
        fruits.AddRange(new[] { "grape", "mango" });
        fruits.Insert(1, "kiwi");

        // 访问
        Console.WriteLine(fruits[0]);       // "apple"
        Console.WriteLine(fruits.Count);    // 元素个数

        // 修改/删除
        fruits[0] = "grapefruit";
        fruits.Remove("banana");            // 按值删除
        fruits.RemoveAt(0);                 // 按索引删除
        // fruits.Clear();                   // 清空

        // 查找
        bool hasApple = fruits.Contains("apple");
        int idx = fruits.IndexOf("cherry");
        string first = fruits.Find(f => f.StartsWith("c"));
        List<string> filtered = fruits.FindAll(f => f.Length > 5);

        // 排序
        fruits.Sort();
        fruits.Reverse();

        // 遍历
        foreach (var fruit in fruits) {
            Console.WriteLine(fruit);
        }

        // 转数组
        string[] arr = fruits.ToArray();

        // ===== Dictionary<TKey, TValue> =====
        var dict = new Dictionary<string, int> {
            { "apple", 10 },
            { "banana", 20 },
            { "cherry", 30 }
        };

        // 添加
        dict["date"] = 40;
        // dict.Add("apple", 50);  // 如果存在会抛异常

        // 获取值
        int appleCount = dict["apple"];
        int value;
        if (dict.TryGetValue("banana", out value)) {
            Console.WriteLine($"banana: {value}");
        }

        // 判断
        bool hasKey = dict.ContainsKey("apple");
        bool hasVal = dict.ContainsValue(20);

        // 删除
        dict.Remove("cherry");

        // 遍历
        foreach (var kvp in dict) {
            Console.WriteLine($"{kvp.Key}: {kvp.Value}");
        }

        foreach (var key in dict.Keys) {
            Console.WriteLine(key);
        }

        foreach (var val in dict.Values) {
            Console.WriteLine(val);
        }

        // ===== HashSet<T> =====
        var set = new HashSet<int> { 1, 2, 3, 2, 1 };  // 自动去重
        set.Add(4);
        set.Add(2);    // 重复，不会添加
        Console.WriteLine(set.Count);  // 4

        // ===== LINQ =====
        var numbers = new List<int> { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };

        // 过滤
        var evens = numbers.Where(n => n % 2 == 0).ToList();

        // 映射
        var squares = numbers.Select(n => n * n).ToList();

        // 排序
        var sorted = numbers.OrderByDescending(n => n).ToList();

        // 第一个
        int firstNum = numbers.First();
        int? firstEven = numbers.FirstOrDefault(n => n % 2 == 0);

        // 聚合
        int sum = numbers.Sum();
        int max = numbers.Max();
        int min = numbers.Min();
        double avg = numbers.Average();
        int count = numbers.Count(n => n > 5);

        // 分组
        var people = new List<Person> {
            new Person { Name = "Alice", Age = 25, City = "Beijing" },
            new Person { Name = "Bob", Age = 30, City = "Shanghai" },
            new Person { Name = "Charlie", Age = 35, City = "Beijing" },
        };

        var byCity = people.GroupBy(p => p.City);
        foreach (var group in byCity) {
            Console.WriteLine($"{group.Key}: {group.Count()}人");
        }

        // 链式调用
        var result = numbers
            .Where(n => n % 2 == 0)
            .Select(n => n * 10)
            .OrderByDescending(n => n)
            .Take(3)
            .ToList();
    }
}

public class Person {
    public string Name { get; set; }
    public int Age { get; set; }
    public string City { get; set; }
}
```
