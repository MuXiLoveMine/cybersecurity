// ============================================================
// 05_dictionary.cs - Dictionary<TKey,TValue> 操作（增删改查、遍历、词频统计）
// 运行方式：dotnet run --project .  或  csc 05_dictionary.cs && 05_dictionary.exe
// ============================================================

using System;
using System.Collections.Generic;
using System.Linq;

// ---------- 1. Dictionary 创建与初始化 ----------
Console.WriteLine("========== 1. Dictionary 创建与初始化 ==========");

// 创建空字典
Dictionary<string, int> emptyDict = new Dictionary<string, int>();
Console.WriteLine($"空字典元素数量：{emptyDict.Count}");

// 使用初始化器创建
Dictionary<string, string> capitals = new Dictionary<string, string>
{
    { "中国", "北京" },
    { "美国", "华盛顿" },
    { "英国", "伦敦" },
    { "法国", "巴黎" },
    { "日本", "东京" }
};
Console.WriteLine("\n国家首都字典：");
PrintDictionary("国家 -> 首都", capitals);

// 使用索引初始化器（C# 6.0+）
Dictionary<string, int> ages = new Dictionary<string, int>
{
    ["张三"] = 25,
    ["李四"] = 30,
    ["王五"] = 22,
    ["赵六"] = 28
};
Console.WriteLine("\n人员年龄字典：");
PrintDictionary("姓名 -> 年龄", ages);

// 从其他集合创建
var fruitList = new List<(string Name, int Price)>
{
    ("苹果", 5),
    ("香蕉", 3),
    ("橙子", 4)
};
Dictionary<string, int> fruitPrices = fruitList.ToDictionary(f => f.Name, f => f.Price);
Console.WriteLine("\n水果价格字典（从列表创建）：");
PrintDictionary("水果 -> 价格", fruitPrices);

Console.WriteLine();

// ---------- 2. 添加元素（增） ----------
Console.WriteLine("========== 2. 添加元素 ==========");

Dictionary<string, string> config = new Dictionary<string, string>();

// Add 方法添加（键已存在会抛出异常）
config.Add("host", "localhost");
config.Add("port", "8080");
config.Add("username", "admin");
Console.WriteLine("Add 添加后：");
PrintDictionary("配置", config);

// 索引器添加（键不存在则添加，存在则更新）
config["password"] = "123456";   // 添加
config["port"] = "9090";         // 更新
Console.WriteLine("\n索引器添加/更新后：");
PrintDictionary("配置", config);

// TryAdd：尝试添加，不抛异常（C# 8.0+）
bool added = config.TryAdd("timeout", "3000");
Console.WriteLine($"\nTryAdd('timeout', '3000') 成功：{added}");

bool addedAgain = config.TryAdd("host", "127.0.0.1");
Console.WriteLine($"TryAdd('host', '127.0.0.1') 成功：{addedAgain}（键已存在）");

Console.WriteLine("TryAdd 后：");
PrintDictionary("配置", config);

Console.WriteLine();

// ---------- 3. 访问元素（查） ----------
Console.WriteLine("========== 3. 访问元素 ==========");

Dictionary<string, int> productPrices = new Dictionary<string, int>
{
    ["笔记本"] = 5000,
    ["手机"] = 3000,
    ["平板"] = 2000,
    ["耳机"] = 500
};
Console.WriteLine("产品价格：");
PrintDictionary("产品 -> 价格", productPrices);

// 通过索引访问（键不存在会抛出 KeyNotFoundException）
Console.WriteLine($"\n笔记本价格：{productPrices["笔记本"]}");
try
{
    int price = productPrices["相机"];
}
catch (KeyNotFoundException)
{
    Console.WriteLine("访问不存在的键 '相机'：抛出 KeyNotFoundException");
}

// TryGetValue：安全访问（推荐）
if (productPrices.TryGetValue("手机", out int phonePrice))
{
    Console.WriteLine($"TryGetValue('手机')：找到，价格 = {phonePrice}");
}

if (!productPrices.TryGetValue("相机", out int cameraPrice))
{
    Console.WriteLine($"TryGetValue('相机')：未找到，默认值 = {cameraPrice}");
}

// ContainsKey / ContainsValue
Console.WriteLine($"\n包含键 '平板'：{productPrices.ContainsKey("平板")}");
Console.WriteLine($"包含键 '相机'：{productPrices.ContainsKey("相机")}");
Console.WriteLine($"包含值 3000：{productPrices.ContainsValue(3000)}");
Console.WriteLine($"包含值 9999：{productPrices.ContainsValue(9999)}");

Console.WriteLine();

// ---------- 4. 修改元素（改） ----------
Console.WriteLine("========== 4. 修改元素 ==========");

Dictionary<string, int> scores = new Dictionary<string, int>
{
    ["语文"] = 85,
    ["数学"] = 92,
    ["英语"] = 78
};
Console.WriteLine("原始成绩：");
PrintDictionary("科目 -> 分数", scores);

// 索引器修改
scores["英语"] = 88;
Console.WriteLine("\n修改英语成绩后：");
PrintDictionary("科目 -> 分数", scores);

// 安全修改：先检查再修改
string subject = "物理";
if (scores.ContainsKey(subject))
{
    scores[subject] = 90;
}
else
{
    Console.WriteLine($"\n科目 '{subject}' 不存在，无法修改");
}

// 批量修改（使用 for 循环遍历键）
Console.WriteLine("\n所有科目加分 5：");
// 注意：不能直接在 foreach 中修改字典，需要先获取键列表
foreach (string key in scores.Keys.ToList())
{
    scores[key] += 5;
}
PrintDictionary("科目 -> 分数", scores);

Console.WriteLine();

// ---------- 5. 删除元素（删） ----------
Console.WriteLine("========== 5. 删除元素 ==========");

Dictionary<string, string> employees = new Dictionary<string, string>
{
    ["E001"] = "张三",
    ["E002"] = "李四",
    ["E003"] = "王五",
    ["E004"] = "赵六",
    ["E005"] = "钱七"
};
Console.WriteLine("原始员工列表：");
PrintDictionary("工号 -> 姓名", employees);

// Remove：按键删除
bool removed = employees.Remove("E003");
Console.WriteLine($"\nRemove('E003') 成功：{removed}");

bool removedAgain = employees.Remove("E999");
Console.WriteLine($"Remove('E999') 成功：{removedAgain}（不存在）");

PrintDictionary("删除后", employees);

// Remove + out 参数（C# 8.0+）：删除并返回被删除的值
if (employees.Remove("E005", out string? removedName))
{
    Console.WriteLine($"\n删除 E005，被删除的姓名：{removedName}");
}

// 按条件删除
Console.WriteLine("\n删除 E002 之后的员工：");
foreach (string key in employees.Keys.ToList())
{
    if (string.Compare(key, "E002") > 0)
    {
        employees.Remove(key);
    }
}
PrintDictionary("条件删除后", employees);

// Clear：清空字典
employees.Clear();
Console.WriteLine($"\nClear 后元素数量：{employees.Count}");

Console.WriteLine();

// ---------- 6. 遍历 Dictionary ----------
Console.WriteLine("========== 6. 遍历 Dictionary ==========");

Dictionary<string, string> countryContinents = new Dictionary<string, string>
{
    ["中国"] = "亚洲",
    ["美国"] = "北美洲",
    ["巴西"] = "南美洲",
    ["埃及"] = "非洲",
    ["澳大利亚"] = "大洋洲"
};

// 遍历键值对（最常用）
Console.WriteLine("遍历键值对（foreach KeyValuePair）：");
foreach (KeyValuePair<string, string> kvp in countryContinents)
{
    Console.WriteLine($"  {kvp.Key} -> {kvp.Value}");
}

// 使用 var 简化
Console.WriteLine("\n使用 var 遍历：");
foreach (var kvp in countryContinents)
{
    Console.WriteLine($"  {kvp.Key} 位于 {kvp.Value}");
}

// 只遍历键
Console.WriteLine("\n遍历键 Keys：");
foreach (string country in countryContinents.Keys)
{
    Console.WriteLine($"  国家：{country}");
}

// 只遍历值
Console.WriteLine("\n遍历值 Values：");
foreach (string continent in countryContinents.Values)
{
    Console.WriteLine($"  大洲：{continent}");
}

// 解构遍历（C# 7.0+）
Console.WriteLine("\n解构遍历：");
foreach (var (country, continent) in countryContinents)
{
    Console.WriteLine($"  {country} 在 {continent}");
}

Console.WriteLine();

// ---------- 7. 词频统计示例 ----------
Console.WriteLine("========== 7. 词频统计示例 ==========");

string text = "the quick brown fox jumps over the lazy dog the dog barks the fox runs";
Console.WriteLine($"原文：\"{text}\"");

// 方法一：使用 Dictionary 统计词频
string[] words = text.Split(' ', StringSplitOptions.RemoveEmptyEntries);
Dictionary<string, int> wordCount = new Dictionary<string, int>();

foreach (string word in words)
{
    if (wordCount.ContainsKey(word))
    {
        wordCount[word]++;
    }
    else
    {
        wordCount[word] = 1;
    }
}

Console.WriteLine("\n词频统计结果：");
foreach (var kvp in wordCount.OrderByDescending(x => x.Value))
{
    Console.WriteLine($"  {kvp.Key}: {kvp.Value} 次");
}

// 方法二：使用 TryGetValue 简化
Dictionary<string, int> wordCount2 = new Dictionary<string, int>();
foreach (string word in words)
{
    wordCount2.TryGetValue(word, out int count);
    wordCount2[word] = count + 1;
}

// 方法三：使用 GetValueOrDefault（更简洁）
Dictionary<string, int> wordCount3 = new Dictionary<string, int>();
foreach (string word in words)
{
    wordCount3[word] = wordCount3.GetValueOrDefault(word) + 1;
}

// 找出出现次数最多的词
var mostFrequent = wordCount.OrderByDescending(x => x.Value).First();
Console.WriteLine($"\n出现次数最多的词：{mostFrequent.Key}（{mostFrequent.Value} 次）");

// 统计只出现一次的词
var onceWords = wordCount.Where(x => x.Value == 1).Select(x => x.Key).ToList();
Console.WriteLine($"只出现一次的词：{string.Join(", ", onceWords)}");

Console.WriteLine();

// ---------- 8. 字典的实际应用场景 ----------
Console.WriteLine("========== 8. 实际应用场景 ==========");

// 场景1：缓存（快速查找）
Console.WriteLine("场景1：缓存模拟");
Dictionary<int, string> userCache = new Dictionary<int, string>();

string GetUserName(int userId)
{
    if (userCache.TryGetValue(userId, out string? name))
    {
        Console.WriteLine($"  缓存命中：用户 {userId}");
        return name;
    }
    // 模拟从数据库查询
    name = $"用户{userId}";
    userCache[userId] = name;
    Console.WriteLine($"  缓存未命中，查询数据库：用户 {userId}");
    return name;
}

GetUserName(1);
GetUserName(2);
GetUserName(1);  // 第二次访问，缓存命中
GetUserName(3);
GetUserName(2);  // 缓存命中

// 场景2：配置项
Console.WriteLine("\n场景2：配置项管理");
Dictionary<string, string> appConfig = new Dictionary<string, string>
{
    ["app.name"] = "MyApp",
    ["app.version"] = "1.0.0",
    ["db.host"] = "localhost",
    ["db.port"] = "3306",
    ["log.level"] = "info"
};

// 获取数据库相关配置
var dbConfig = appConfig.Where(kvp => kvp.Key.StartsWith("db."))
                        .ToDictionary(kvp => kvp.Key, kvp => kvp.Value);
Console.WriteLine("  数据库配置：");
foreach (var kvp in dbConfig)
{
    Console.WriteLine($"    {kvp.Key} = {kvp.Value}");
}

// 场景3：分组统计
Console.WriteLine("\n场景3：按城市分组人员");
List<PersonInfo> people = new List<PersonInfo>
{
    new PersonInfo { Name = "张三", City = "北京", Age = 25 },
    new PersonInfo { Name = "李四", City = "上海", Age = 30 },
    new PersonInfo { Name = "王五", City = "北京", Age = 22 },
    new PersonInfo { Name = "赵六", City = "广州", Age = 28 },
    new PersonInfo { Name = "钱七", City = "上海", Age = 35 },
    new PersonInfo { Name = "孙八", City = "北京", Age = 27 },
};

// 按城市分组
Dictionary<string, List<PersonInfo>> cityGroups = new Dictionary<string, List<PersonInfo>>();
foreach (var p in people)
{
    if (!cityGroups.ContainsKey(p.City))
    {
        cityGroups[p.City] = new List<PersonInfo>();
    }
    cityGroups[p.City].Add(p);
}

foreach (var group in cityGroups)
{
    Console.WriteLine($"  {group.Key}（{group.Value.Count}人）：");
    foreach (var p in group.Value)
    {
        Console.WriteLine($"    - {p.Name}（{p.Age}岁）");
    }
}

Console.WriteLine();
Console.WriteLine("========== 程序结束 ==========");

// ============================================================
// 辅助方法和类
// ============================================================

void PrintDictionary<TKey, TValue>(string title, Dictionary<TKey, TValue> dict)
    where TKey : notnull
{
    Console.WriteLine($"  {title}：");
    foreach (var kvp in dict)
    {
        Console.WriteLine($"    {kvp.Key} -> {kvp.Value}");
    }
}

public class PersonInfo
{
    public string Name { get; set; } = string.Empty;
    public string City { get; set; } = string.Empty;
    public int Age { get; set; }
}
