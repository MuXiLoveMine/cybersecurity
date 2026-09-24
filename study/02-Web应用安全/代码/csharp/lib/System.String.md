# System.String - C# 字符串类

> C# 字符串类 `System.String`，提供丰富的字符串操作。

---

## 一、基本用法

```csharp
using System;

// 字符串创建
string s1 = "hello world";
string s2 = new string('a', 5);    // "aaaaa"
string s3 = new string(new char[] {'h', 'e', 'l', 'l', 'o'});

// 字符串插值（C# 6+）
string name = "Alice";
int age = 25;
string msg = $"Name: {name}, Age: {age}";

// 字符串连接
string s = "Hello" + " " + "World";
string joined = string.Join(", ", new[] {"a", "b", "c"});  // "a, b, c"

// 空字符串
string empty = "";
string empty2 = string.Empty;  // 推荐
```

---

## 二、常用属性与方法

### 2.1 长度与索引

```csharp
string s = "hello world";

// 长度
int len = s.Length;  // 11

// 索引访问
char first = s[0];    // 'h'
char last = s[s.Length - 1];  // 'd'

// 遍历
foreach (char c in s)
{
    Console.WriteLine(c);
}

// 是否为空
string.IsNullOrEmpty(s);   // null 或 "" 都返回 true
string.IsNullOrWhiteSpace(s);  // null、""、全空白都返回 true
```

### 2.2 查找与判断

```csharp
string s = "hello world hello";

// 包含
s.Contains("world");       // true
s.Contains("World", StringComparison.OrdinalIgnoreCase);  // 忽略大小写

// 开头/结尾
s.StartsWith("hello");     // true
s.EndsWith("hello");       // false（结尾是 "hello"？不，结尾是 "hello"）

// 查找位置
s.IndexOf('o');            // 4（第一个 'o' 的位置）
s.IndexOf("world");        // 6
s.IndexOf("hello", 1);     // 12（从位置 1 开始找）
s.LastIndexOf('o');        // 13（最后一个 'o'）
s.LastIndexOf("hello");    // 12

// 查找任一字符
s.IndexOfAny(new char[] {'a', 'e', 'i', 'o', 'u'});  // 1
```

### 2.3 子串与分割

```csharp
string s = "hello world";

// 子串
s.Substring(0, 5);         // "hello"（从 0 开始，取 5 个）
s.Substring(6);            // "world"（从 6 到末尾）

// 分割
string[] parts = s.Split(' ');  // ["hello", "world"]
string[] parts2 = s.Split(new[] {' ', ','}, StringSplitOptions.RemoveEmptyEntries);

// 移除
s.Remove(5);               // "hello"（从位置 5 开始删除）
s.Remove(0, 3);            // "lo world"

// 修剪
"  hello  ".Trim();        // "hello"（去除首尾空白）
"  hello  ".TrimStart();   // "hello  "
"  hello  ".TrimEnd();     // "  hello"
"--hello--".Trim('-');     // "hello"
```

### 2.4 替换与修改

```csharp
string s = "hello world";

// 替换
s.Replace('l', 'L');       // "heLLo worLd"
s.Replace("world", "there");  // "hello there"

// 大小写转换
s.ToUpper();               // "HELLO WORLD"
s.ToLower();               // "hello world"
s.ToUpperInvariant();      // 使用固定区域性

// 插入
s.Insert(5, " beautiful");  // "hello beautiful world"

// 填充
"hello".PadLeft(10);       // "     hello"
"hello".PadRight(10, '*'); // "hello*****"
```

### 2.5 比较

```csharp
string a = "apple";
string b = "banana";

// 相等比较
a == b;                    // false
a.Equals(b);               // false
a.Equals(b, StringComparison.OrdinalIgnoreCase);  // 忽略大小写

// 顺序比较
string.Compare(a, b);      // < 0 (a < b)
string.Compare(a, b, StringComparison.OrdinalIgnoreCase);

// 最佳实践：使用显式的 StringComparison
// StringComparison.Ordinal              - 序数比较（最快，推荐用于内部比较）
// StringComparison.OrdinalIgnoreCase    - 忽略大小序数
// StringComparison.CurrentCulture       - 当前区域性
// StringComparison.InvariantCulture     - 固定区域性
```

### 2.6 格式化

```csharp
// string.Format
string s = string.Format("Name: {0}, Age: {1}", "Alice", 25);

// 数字格式化
string.Format("{0:C}", 123.45);      // ¥123.45（货币）
string.Format("{0:D5}", 42);         // 00042（十进制，5位）
string.Format("{0:N2}", 1234.567);   // 1,234.57（数字格式）
string.Format("{0:P}", 0.85);        // 85.00%（百分比）
string.Format("{0:X}", 255);         // FF（十六进制）
string.Format("{0:0.00}", 3.14159);  // 3.14

// 日期格式化
DateTime now = DateTime.Now;
string.Format("{0:yyyy-MM-dd}", now);        // 2024-01-15
string.Format("{0:HH:mm:ss}", now);          // 14:30:00
string.Format("{0:yyyy-MM-dd HH:mm:ss}", now);

// 字符串插值也支持格式
$"{123.45:C}";
$"{now:yyyy-MM-dd}";
```

### 2.7 类型转换

```csharp
// 字符串 -> 数字
int i = int.Parse("42");
double d = double.Parse("3.14");
long l = long.Parse("1234567890");

// 安全转换（TryParse）
if (int.TryParse("42", out int result))
{
    Console.WriteLine($"转换成功: {result}");
}
else
{
    Console.WriteLine("转换失败");
}

// 数字 -> 字符串
string s1 = 42.ToString();
string s2 = 3.14.ToString();
string s3 = 255.ToString("X");  // "FF"

// Convert 类
int num = Convert.ToInt32("42");
string str = Convert.ToString(42);
```

---

## 三、StringBuilder

```csharp
using System.Text;

/*
    string 是不可变的，每次修改都会创建新对象
    大量拼接操作使用 StringBuilder 更高效
*/

// 创建
StringBuilder sb = new StringBuilder();
StringBuilder sb2 = new StringBuilder("初始内容");
StringBuilder sb3 = new StringBuilder(100);  // 指定初始容量

// 追加
sb.Append("Hello ");
sb.Append("World");
sb.AppendLine();              // 追加换行
sb.AppendLine("Next line");
sb.AppendFormat("Name: {0}, Age: {1}\n", "Alice", 25);

// 插入
sb.Insert(0, "Start: ");

// 删除
sb.Remove(0, 7);  // 从位置 0 删除 7 个字符

// 替换
sb.Replace("World", "C#");

// 获取最终字符串
string result = sb.ToString();

// 容量
sb.Capacity = 1000;
sb.Length;
sb.Clear();

/*
    性能建议：
    - 少量拼接（< 10 次）：用 + 或插值
    - 中等数量：string.Join, string.Concat
    - 大量拼接（循环中）：StringBuilder
*/
```

---

## 四、安全相关内容

### 4.1 字符串与安全

```csharp
/*
    C# 字符串安全注意事项：
    
    1. 字符串是不可变的
       - 修改字符串总是创建新实例
       - 原始字符串可能还在内存中（敏感数据风险）
    
    2. 密码等敏感数据
       - 不要用 string 存储密码
       - 使用 SecureString 或尽快清零
    
    3. 字符串比较
       - 始终使用显式的 StringComparison
       - 避免隐式的区域性比较导致的问题
    
    4. 格式化字符串
       - 不要用用户输入作为格式串
*/

// ===== 危险：用户输入作为格式串 =====
string userInput = "{0} {0} {0}";
string.Format(userInput, "test");  // 虽然不会像 C 那样严重，但也是问题

// ===== 安全：使用占位符 =====
string.Format("User input: {0}", userInput);

// ===== 密码处理 =====
// 不要把密码放在 string 里太久
// 使用 SecureString（但在 .NET Core 中已不推荐）
// 更好的做法：尽快哈希，用完即清

// 字符数组（用完可以清零）
char[] passwordChars = GetPasswordFromInput();
// 使用后清零
Array.Clear(passwordChars, 0, passwordChars.Length);
```

### 4.2 输入验证

```csharp
using System;
using System.Text.RegularExpressions;

// 验证邮箱
public static bool IsValidEmail(string email)
{
    if (string.IsNullOrWhiteSpace(email))
        return false;
    
    if (email.Length > 254)
        return false;
    
    try {
        var addr = new System.Net.Mail.MailAddress(email);
        return addr.Address == email;
    } catch {
        return false;
    }
}

// 验证用户名（只允许字母数字下划线）
public static bool IsValidUsername(string username)
{
    if (string.IsNullOrWhiteSpace(username))
        return false;
    
    return Regex.IsMatch(username, @"^[a-zA-Z0-9_]{3,20}$");
}

// 验证整数范围
public static bool IsValidPort(string portStr)
{
    if (!int.TryParse(portStr, out int port))
        return false;
    
    return port >= 1 && port <= 65535;
}

// 防止 SQL 注入（实际应该用参数化查询）
public static string SafeSqlLike(string input)
{
    // 转义 LIKE 特殊字符
    return input.Replace("%", "\\%")
                .Replace("_", "\\_")
                .Replace("[", "\\[");
}
```

### 4.3 路径安全

```csharp
using System;
using System.IO;

// 防止路径遍历
public static string GetSafeFilePath(string baseDir, string filename)
{
    // 1. 只取文件名部分
    string safeName = Path.GetFileName(filename);
    
    // 2. 组合路径
    string fullPath = Path.Combine(baseDir, safeName);
    
    // 3. 规范化并验证
    string normalized = Path.GetFullPath(fullPath);
    string normalizedBase = Path.GetFullPath(baseDir);
    
    if (!normalized.StartsWith(normalizedBase, StringComparison.OrdinalIgnoreCase))
    {
        throw new UnauthorizedAccessException("非法路径访问");
    }
    
    return normalized;
}

// 使用
try
{
    string safePath = GetSafeFilePath(@"C:\files\", userInput);
    string content = File.ReadAllText(safePath);
}
catch (UnauthorizedAccessException)
{
    // 处理非法访问
}
```

### 4.4 字符串比较的安全坑

```csharp
/*
    字符串比较中的安全陷阱：
    
    1. 大小写敏感性
       - 用户认证时可能绕过（admin vs Admin vs ADMIN）
    
    2. 区域性差异
       - 不同语言环境可能有不同的比较规则
    
    3. Unicode 等价性
       - 看起来相同的字符可能有不同的编码
*/

// 登录验证（不区分大小写的用户名）
public bool ValidateUser(string username, string password)
{
    // 用户名比较应该用 OrdinalIgnoreCase
    var user = _users.FirstOrDefault(u => 
        string.Equals(u.Username, username, StringComparison.OrdinalIgnoreCase));
    
    if (user == null) return false;
    
    // 密码比较应该用恒定时间比较
    return VerifyPassword(password, user.PasswordHash);
}

// 恒定时间字符串比较（防止时序攻击）
public static bool SecureCompare(string a, string b)
{
    if (a == null || b == null)
        return false;
    
    if (a.Length != b.Length)
        return false;
    
    int diff = 0;
    for (int i = 0; i < a.Length; i++)
    {
        diff |= a[i] ^ b[i];
    }
    return diff == 0;
}
```

---

## 五、常用方法速查

| 操作 | 方法 |
|------|------|
| 长度 | `s.Length` |
| 空检查 | `string.IsNullOrEmpty(s)` / `string.IsNullOrWhiteSpace(s)` |
| 拼接 | `s1 + s2` / `string.Concat` / `string.Join` |
| 子串 | `s.Substring(start, length)` |
| 分割 | `s.Split(...)` |
| 替换 | `s.Replace(old, new)` |
| 查找 | `s.IndexOf(...)` / `s.Contains(...)` |
| 比较 | `s.Equals(other, StringComparison.Ordinal)` |
| 大小写 | `s.ToUpper()` / `s.ToLower()` |
| 修剪 | `s.Trim()` / `s.TrimStart()` / `s.TrimEnd()` |
| 填充 | `s.PadLeft()` / `s.PadRight()` |
| 插入 | `s.Insert(index, str)` |
| 删除 | `s.Remove(start, length)` |
| 格式化 | `string.Format(...)` / `$""` 插值 |
| 转换 | `int.Parse()` / `int.TryParse()` / `.ToString()` |
