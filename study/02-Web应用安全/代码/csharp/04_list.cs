// ============================================================
// 04_list.cs - List<T> 集合操作（增删改查、遍历、排序）
// 运行方式：dotnet run --project .  或  csc 04_list.cs && 04_list.exe
// ============================================================

using System;
using System.Collections.Generic;
using System.Linq;

// ---------- 1. List 的创建与初始化 ----------
Console.WriteLine("========== 1. List 创建与初始化 ==========");

// 创建空列表
List<int> numbers = new List<int>();
Console.WriteLine($"空列表元素数量：{numbers.Count}");
Console.WriteLine($"空列表容量：{numbers.Capacity}");

// 使用初始化器创建并填充
List<string> fruits = new List<string> { "苹果", "香蕉", "橙子", "葡萄" };
Console.WriteLine($"\n水果列表（初始化器）：共 {fruits.Count} 个元素");
PrintList("水果", fruits);

// 创建指定初始容量的列表
List<int> bigList = new List<int>(100);
Console.WriteLine($"\n指定容量的列表：Capacity = {bigList.Capacity}");

// 从数组创建
int[] arr = { 10, 20, 30, 40, 50 };
List<int> fromArray = new List<int>(arr);
Console.WriteLine($"\n从数组创建的列表：");
PrintList("数字", fromArray);

// 使用 Enumerable.Range 创建
List<int> rangeList = Enumerable.Range(1, 10).ToList();
Console.WriteLine($"\nEnumerable.Range(1,10) 创建：");
PrintList("序列", rangeList);

Console.WriteLine();

// ---------- 2. 添加元素（增） ----------
Console.WriteLine("========== 2. 添加元素 ==========");

List<string> programmingLangs = new List<string>();

// Add：添加单个元素
programmingLangs.Add("C#");
programmingLangs.Add("Python");
programmingLangs.Add("Java");
Console.WriteLine("Add 三个元素后：");
PrintList("编程语言", programmingLangs);

// AddRange：添加多个元素（集合）
programmingLangs.AddRange(new string[] { "JavaScript", "Go", "Rust" });
Console.WriteLine("\nAddRange 后：");
PrintList("编程语言", programmingLangs);

// Insert：在指定位置插入
programmingLangs.Insert(1, "C++");
Console.WriteLine("\nInsert 到索引 1 后：");
PrintList("编程语言", programmingLangs);

// InsertRange：插入多个元素
programmingLangs.InsertRange(0, new[] { "PHP", "Ruby" });
Console.WriteLine("\nInsertRange 到开头后：");
PrintList("编程语言", programmingLangs);

Console.WriteLine();

// ---------- 3. 访问元素（查） ----------
Console.WriteLine("========== 3. 访问元素 ==========");

// 通过索引访问
List<string> colors = new List<string> { "红", "橙", "黄", "绿", "青", "蓝", "紫" };
Console.WriteLine($"颜色列表：{string.Join(", ", colors)}");
Console.WriteLine($"第 1 个元素（索引 0）：{colors[0]}");
Console.WriteLine($"第 4 个元素（索引 3）：{colors[3]}");
Console.WriteLine($"最后 1 个元素（索引 {colors.Count - 1}）：{colors[colors.Count - 1]}");

// 范围索引（C# 8.0+）
Console.WriteLine($"第 2 到第 4 个元素：{string.Join(", ", colors[1..4])}");
Console.WriteLine($"前 3 个元素：{string.Join(", ", colors[..3])}");
Console.WriteLine($"后 3 个元素：{string.Join(", ", colors[^3..])}");

// IndexOf / LastIndexOf
Console.WriteLine($"\n\"绿\" 的索引：{colors.IndexOf("绿")}");
Console.WriteLine($"不存在的元素索引：{colors.IndexOf("黑")}（-1 表示未找到）");

// Contains：判断是否包含
Console.WriteLine($"包含\"蓝\"：{colors.Contains("蓝")}");
Console.WriteLine($"包含\"黑\"：{colors.Contains("黑")}");

// Exists：按条件判断是否存在
List<int> scores = new List<int> { 85, 92, 78, 95, 60, 88 };
Console.WriteLine($"\n分数列表：{string.Join(", ", scores)}");
Console.WriteLine($"存在 90 分以上：{scores.Exists(s => s >= 90)}");
Console.WriteLine($"存在不及格：{scores.Exists(s => s < 60)}");

// Find：查找第一个匹配项
int firstHighScore = scores.Find(s => s >= 90);
Console.WriteLine($"第一个 90 分以上：{firstHighScore}");

// FindIndex：查找第一个匹配项的索引
int firstHighIndex = scores.FindIndex(s => s >= 90);
Console.WriteLine($"第一个 90 分以上的索引：{firstHighIndex}");

// FindAll：查找所有匹配项
List<int> highScores = scores.FindAll(s => s >= 85);
Console.WriteLine($"所有 85 分以上：{string.Join(", ", highScores)}");

// FindLast / FindLastIndex
int lastHighScore = scores.FindLast(s => s >= 90);
Console.WriteLine($"最后一个 90 分以上：{lastHighScore}");

// TrueForAll：判断是否所有元素都满足条件
bool allPassed = scores.TrueForAll(s => s >= 60);
Console.WriteLine($"全部及格：{allPassed}");

Console.WriteLine();

// ---------- 4. 修改元素（改） ----------
Console.WriteLine("========== 4. 修改元素 ==========");

List<string> weekDays = new List<string> { "Monday", "Tuesday", "Wednesday", "Thursday", "Friday" };
Console.WriteLine($"原列表：{string.Join(", ", weekDays)}");

// 通过索引修改
weekDays[0] = "星期一";
Console.WriteLine($"修改索引 0 后：{string.Join(", ", weekDays)}");

// 替换指定值（先找再改）
int tuesdayIndex = weekDays.IndexOf("Tuesday");
if (tuesdayIndex != -1)
{
    weekDays[tuesdayIndex] = "星期二";
}
Console.WriteLine($"替换 Tuesday 后：{string.Join(", ", weekDays)}");

// ConvertAll：批量转换
List<int> nums = new List<int> { 1, 2, 3, 4, 5 };
List<string> strNums = nums.ConvertAll(n => n.ToString("D2"));
Console.WriteLine($"\n数字转字符串（两位）：{string.Join(", ", strNums)}");

List<int> doubled = nums.ConvertAll(n => n * 2);
Console.WriteLine($"数字翻倍：{string.Join(", ", doubled)}");

Console.WriteLine();

// ---------- 5. 删除元素（删） ----------
Console.WriteLine("========== 5. 删除元素 ==========");

List<char> chars = new List<char> { 'A', 'B', 'C', 'D', 'E', 'F', 'G' };
Console.WriteLine($"原列表：{string.Join(", ", chars)}");

// Remove：移除第一个匹配项
chars.Remove('C');
Console.WriteLine($"Remove('C') 后：{string.Join(", ", chars)}");

// RemoveAt：按索引移除
chars.RemoveAt(0);
Console.WriteLine($"RemoveAt(0) 后：{string.Join(", ", chars)}");

// RemoveRange：移除指定范围
chars.RemoveRange(1, 2);  // 从索引 1 开始，移除 2 个
Console.WriteLine($"RemoveRange(1, 2) 后：{string.Join(", ", chars)}");

// RemoveAll：按条件移除
List<int> numList = new List<int> { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
Console.WriteLine($"\n原数字列表：{string.Join(", ", numList)}");
numList.RemoveAll(n => n % 2 == 0);  // 移除所有偶数
Console.WriteLine($"RemoveAll 偶数后：{string.Join(", ", numList)}");

// Clear：清空所有元素
numList.Clear();
Console.WriteLine($"Clear 后：元素数 = {numList.Count}");

Console.WriteLine();

// ---------- 6. 遍历 ----------
Console.WriteLine("========== 6. 遍历 List ==========");

List<string> animals = new List<string> { "猫", "狗", "兔子", "熊猫", "老虎" };

// foreach 遍历（最常用）
Console.WriteLine("foreach 遍历：");
foreach (string animal in animals)
{
    Console.WriteLine($"  - {animal}");
}

// for 循环遍历（需要索引时使用）
Console.WriteLine("\nfor 循环遍历：");
for (int i = 0; i < animals.Count; i++)
{
    Console.WriteLine($"  [{i}] {animals[i]}");
}

// ForEach 方法（Lambda 表达式）
Console.WriteLine("\nForEach 方法：");
animals.ForEach(a => Console.WriteLine($"  * {a}"));

// 使用索引迭代（C# 8.0+）
Console.WriteLine("\n带索引的遍历：");
foreach (var (item, index) in animals.Select((a, i) => (a, i)))
{
    Console.WriteLine($"  #{index}: {item}");
}

Console.WriteLine();

// ---------- 7. 排序 ----------
Console.WriteLine("========== 7. 排序 ==========");

// 默认排序（升序）
List<int> randomNums = new List<int> { 45, 12, 78, 23, 56, 9, 67 };
Console.WriteLine($"原列表：{string.Join(", ", randomNums)}");

randomNums.Sort();
Console.WriteLine($"升序排序：{string.Join(", ", randomNums)}");

// 降序排序（使用 Comparison 委托）
randomNums.Sort((a, b) => b.CompareTo(a));
Console.WriteLine($"降序排序：{string.Join(", ", randomNums)}");

// 自定义排序规则
List<string> names = new List<string> { "张三", "李明", "王小明", "赵", "欧阳锋" };
Console.WriteLine($"\n原名称列表：{string.Join(", ", names)}");

// 按长度排序
names.Sort((a, b) => a.Length.CompareTo(b.Length));
Console.WriteLine($"按长度排序：{string.Join(", ", names)}");

// 倒序
names.Reverse();
Console.WriteLine($"反转顺序：{string.Join(", ", names)}");

// 复杂对象排序
List<Student> students = new List<Student>
{
    new Student { Name = "张三", Score = 85 },
    new Student { Name = "李四", Score = 92 },
    new Student { Name = "王五", Score = 78 },
    new Student { Name = "赵六", Score = 92 },
};

Console.WriteLine("\n学生列表（按分数降序，分数相同按名字升序）：");
students.Sort((a, b) =>
{
    int scoreCompare = b.Score.CompareTo(a.Score);
    if (scoreCompare != 0) return scoreCompare;
    return a.Name.CompareTo(b.Name);
});
foreach (var s in students)
{
    Console.WriteLine($"  {s.Name} - {s.Score} 分");
}

Console.WriteLine();

// ---------- 8. 其他常用操作 ----------
Console.WriteLine("========== 8. 其他常用操作 ==========");

// ToArray：转换为数组
List<int> list = new List<int> { 1, 2, 3, 4, 5 };
int[] array = list.ToArray();
Console.WriteLine($"List 转数组：{string.Join(", ", array)}");

// CopyTo
int[] dest = new int[10];
list.CopyTo(dest, 3);  // 从目标数组索引 3 开始复制
Console.WriteLine($"CopyTo 后目标数组：{string.Join(", ", dest)}");

// EnsureCapacity：确保容量
list.EnsureCapacity(100);
Console.WriteLine($"EnsureCapacity(100) 后容量：{list.Capacity}");

// TrimExcess：压缩容量（减少内存占用）
list.TrimExcess();
Console.WriteLine($"TrimExcess 后容量：{list.Capacity}");

// 二分查找（列表必须已排序）
List<int> sortedList = new List<int> { 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 };
int index = sortedList.BinarySearch(50);
Console.WriteLine($"\n二分查找 50：索引 = {index}");

int notFound = sortedList.BinarySearch(45);
Console.WriteLine($"二分查找 45（不存在）：{notFound}（负数表示未找到）");

// Exists / Find 与 LINQ 的对比
List<int> data = new List<int> { 1, 3, 5, 7, 9, 11, 13 };
Console.WriteLine($"\n数据：{string.Join(", ", data)}");
Console.WriteLine($"List.Find(>10)：{data.Find(x => x > 10)}");
Console.WriteLine($"LINQ First(>10)：{data.First(x => x > 10)}");

Console.WriteLine();
Console.WriteLine("========== 程序结束 ==========");

// ============================================================
// 辅助方法和类
// ============================================================

void PrintList<T>(string name, List<T> list)
{
    Console.WriteLine($"  {name}列表：[{string.Join(", ", list)}]");
}

public class Student
{
    public string Name { get; set; } = string.Empty;
    public int Score { get; set; }
}
