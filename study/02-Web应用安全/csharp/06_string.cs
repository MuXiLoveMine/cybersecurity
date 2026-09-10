// ============================================================
// 06_string.cs - 字符串操作：拼接、查找、分割、替换、格式化、插值、StringBuilder
// 运行方式：dotnet run --project .  或  csc 06_string.cs && 06_string.exe
// ============================================================

using System;
using System.Text;

// ---------- 1. 字符串基础 ----------
Console.WriteLine("========== 1. 字符串基础 ==========");

// 字符串声明
string s1 = "Hello";
string s2 = "World";
string empty = "";            // 空字符串
string nullStr = null;        // null 引用

Console.WriteLine($"s1 = \"{s1}\"");
Console.WriteLine($"s2 = \"{s2}\"");
Console.WriteLine($"空字符串长度：{empty.Length}");

// 字符串是不可变的（immutable）
string original = "Hello";
string modified = original.ToUpper();  // 返回新字符串，original 不变
Console.WriteLine($"\n字符串不可变性：");
Console.WriteLine($"  original = \"{original}\"（未改变）");
Console.WriteLine($"  modified = \"{modified}\"（新字符串）");

// 字符串相等比较
string a = "hello";
string b = "HELLO";
Console.WriteLine($"\n字符串比较：");
Console.WriteLine($"  \"{a}\" == \"{b}\" : {a == b}（区分大小写）");
Console.WriteLine($"  不区分大小写：{a.Equals(b, StringComparison.OrdinalIgnoreCase)}");

// 空字符串判断
Console.WriteLine($"\n空字符串判断：");
Console.WriteLine($"  string.IsNullOrEmpty(\"\") = {string.IsNullOrEmpty("")}");
Console.WriteLine($"  string.IsNullOrEmpty(null) = {string.IsNullOrEmpty(null)}");
Console.WriteLine($"  string.IsNullOrWhiteSpace(\"   \") = {string.IsNullOrWhiteSpace("   ")}");

Console.WriteLine();

// ---------- 2. 字符串拼接 ----------
Console.WriteLine("========== 2. 字符串拼接 ==========");

// 使用 + 运算符
string result1 = "Hello" + " " + "World";
Console.WriteLine($"+ 拼接：\"{result1}\"");

// 使用 string.Concat
string result2 = string.Concat("C#", " ", "is", " ", "awesome");
Console.WriteLine($"Concat：\"{result2}\"");

// 使用 string.Join
string[] parts = { "北京", "上海", "广州", "深圳" };
string joined = string.Join(", ", parts);
Console.WriteLine($"Join：\"{joined}\"");

// 拼接多个字符串数组
string[] arr1 = { "a", "b", "c" };
string[] arr2 = { "d", "e", "f" };
string combined = string.Concat(arr1.Concat(arr2));
Console.WriteLine($"数组合并：\"{combined}\"");

Console.WriteLine();

// ---------- 3. 字符串查找 ----------
Console.WriteLine("========== 3. 字符串查找 ==========");

string sentence = "The quick brown fox jumps over the lazy dog";
Console.WriteLine($"原文：\"{sentence}\"");

// Contains：是否包含
Console.WriteLine($"\nContains(\"fox\")：{sentence.Contains("fox")}");
Console.WriteLine($"Contains(\"cat\")：{sentence.Contains("cat")}");

// IndexOf：查找位置
Console.WriteLine($"\nIndexOf('o')：{sentence.IndexOf('o')}");
Console.WriteLine($"IndexOf(\"the\")：{sentence.IndexOf("the")}");
Console.WriteLine($"IndexOf(\"the\", 20)：{sentence.IndexOf("the", 20)}（从索引 20 开始）");

// LastIndexOf：最后出现的位置
Console.WriteLine($"\nLastIndexOf('o')：{sentence.LastIndexOf('o')}");
Console.WriteLine($"LastIndexOf(\"the\")：{sentence.LastIndexOf("the")}");

// StartsWith / EndsWith
Console.WriteLine($"\nStartsWith(\"The\")：{sentence.StartsWith("The")}");
Console.WriteLine($"EndsWith(\"dog\")：{sentence.EndsWith("dog")}");
Console.WriteLine($"StartsWith(\"the\")：{sentence.StartsWith("the")}（区分大小写）");

// 统计字符出现次数
int countO = 0;
foreach (char c in sentence)
{
    if (c == 'o') countO++;
}
Console.WriteLine($"\n字符 'o' 出现次数：{countO}");

// IndexOfAny：查找任意字符
char[] searchChars = { 'x', 'y', 'z' };
int foundIndex = sentence.IndexOfAny(searchChars);
Console.WriteLine($"IndexOfAny(['x','y','z'])：{foundIndex}");

Console.WriteLine();

// ---------- 4. 字符串提取与子串 ----------
Console.WriteLine("========== 4. 字符串提取与子串 ==========");

string text = "Hello, World!";
Console.WriteLine($"原文：\"{text}\"");

// Substring：提取子串
string sub1 = text.Substring(0, 5);     // 从索引 0 开始，取 5 个字符
string sub2 = text.Substring(7);        // 从索引 7 开始到末尾
Console.WriteLine($"Substring(0, 5) = \"{sub1}\"");
Console.WriteLine($"Substring(7) = \"{sub2}\"");

// 索引和范围（C# 8.0+）
Console.WriteLine($"\n索引语法（C# 8.0+）：");
Console.WriteLine($"text[0..5] = \"{text[0..5]}\"");
Console.WriteLine($"text[7..] = \"{text[7..]}\"");
Console.WriteLine($"text[..5] = \"{text[..5]}\"");
Console.WriteLine($"text[^6..] = \"{text[^6..]}\"（最后 6 个字符）");

// 按索引访问字符
Console.WriteLine($"\ntext[0] = '{text[0]}'");
Console.WriteLine($"text[^1] = '{text[^1]}'（最后一个字符）");

// 截取邮箱用户名和域名
string email = "zhangsan@example.com";
int atIndex = email.IndexOf('@');
if (atIndex > 0)
{
    string username = email.Substring(0, atIndex);
    string domain = email.Substring(atIndex + 1);
    Console.WriteLine($"\n邮箱解析：{email}");
    Console.WriteLine($"  用户名：{username}");
    Console.WriteLine($"  域名：{domain}");
}

Console.WriteLine();

// ---------- 5. 字符串分割 ----------
Console.WriteLine("========== 5. 字符串分割 ==========");

// 按字符分割
string csv = "苹果,香蕉,橙子,葡萄,西瓜";
string[] fruits = csv.Split(',');
Console.WriteLine($"CSV 字符串：\"{csv}\"");
Console.WriteLine("Split(',') 结果：");
foreach (string fruit in fruits)
{
    Console.WriteLine($"  - {fruit}");
}

// 按字符串分割
string html = "<div>内容</div><span>文字</span><p>段落</p>";
string[] tags = html.Split(new string[] { "</div>", "</span>", "</p>" },
    StringSplitOptions.RemoveEmptyEntries);
Console.WriteLine($"\nHTML 分割：");
foreach (string tag in tags)
{
    Console.WriteLine($"  - {tag}");
}

// 分割选项
string messy = "a,,b,c,,d";
string[] withEmpty = messy.Split(',');
string[] withoutEmpty = messy.Split(',', StringSplitOptions.RemoveEmptyEntries);
Console.WriteLine($"\n乱字符串：\"{messy}\"");
Console.WriteLine($"  保留空元素：{withEmpty.Length} 个");
Console.WriteLine($"  移除空元素：{withoutEmpty.Length} 个");

// 去除空格后分割
string spaced = "  one   two  three  ";
string[] trimmed = spaced.Split(' ', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
Console.WriteLine($"\n带空格字符串：\"{spaced}\"");
Console.WriteLine($"  清理后分割：{string.Join(", ", trimmed)}");

// 多行分割
string multiLine = @"第一行
第二行
第三行";
string[] lines = multiLine.Split('\n');
Console.WriteLine($"\n多行文本分割为 {lines.Length} 行");

Console.WriteLine();

// ---------- 6. 字符串替换 ----------
Console.WriteLine("========== 6. 字符串替换 ==========");

string message = "Hello World! World is great!";
Console.WriteLine($"原文：\"{message}\"");

// Replace 简单替换
string replaced = message.Replace("World", "C#");
Console.WriteLine($"Replace(\"World\", \"C#\")：\"{replaced}\"");

// 替换字符
string noSpaces = message.Replace(" ", "_");
Console.WriteLine($"空格替换为下划线：\"{noSpaces}\"");

// 删除字符（替换为空字符串）
string removed = message.Replace("!", "");
Console.WriteLine($"删除感叹号：\"{removed}\"");

// 多次替换（链式调用）
string clean = "<p>Hello <b>World</b></p>"
    .Replace("<p>", "")
    .Replace("</p>", "")
    .Replace("<b>", "")
    .Replace("</b>", "");
Console.WriteLine($"\n移除 HTML 标签（简单替换）：\"{clean}\"");

// 注意：Replace 不支持正则，如需正则替换请用 Regex.Replace

Console.WriteLine();

// ---------- 7. 大小写转换与修剪 ----------
Console.WriteLine("========== 7. 大小写转换与修剪 ==========");

string mixed = "  Hello World  ";
Console.WriteLine($"原文：\"{mixed}\"");

// 大小写转换
Console.WriteLine($"ToUpper()：\"{mixed.ToUpper()}\"");
Console.WriteLine($"ToLower()：\"{mixed.ToLower()}\"");

// 修剪空白
Console.WriteLine($"Trim()：\"{mixed.Trim()}\"");
Console.WriteLine($"TrimStart()：\"{mixed.TrimStart()}\"");
Console.WriteLine($"TrimEnd()：\"{mixed.TrimEnd()}\"");

// 修剪指定字符
string withBrackets = "[Hello World]";
Console.WriteLine($"\n带括号：\"{withBrackets}\"");
Console.WriteLine($"Trim('[', ']')：\"{withBrackets.Trim('[', ']')}\"");

// PadLeft / PadRight：填充
string numStr = "42";
Console.WriteLine($"\nPadLeft(5, '0')：\"{numStr.PadLeft(5, '0')}\"");
Console.WriteLine($"PadRight(5, '.')：\"{numStr.PadRight(5, '.')}\"");

Console.WriteLine();

// ---------- 8. 字符串格式化 ----------
Console.WriteLine("========== 8. 字符串格式化 ==========");

// string.Format（复合格式化）
string name = "张三";
int age = 25;
double salary = 9999.99;
string fmt1 = string.Format("姓名：{0}，年龄：{1}，工资：{2}", name, age, salary);
Console.WriteLine($"string.Format：{fmt1}");

// 格式说明符
Console.WriteLine($"\n数字格式：");
Console.WriteLine($"  货币：{string.Format("{0:C}", salary)}");
Console.WriteLine($"  固定2位小数：{string.Format("{0:F2}", salary)}");
Console.WriteLine($"  百分比：{string.Format("{0:P}", 0.85)}");
Console.WriteLine($"  科学计数：{string.Format("{0:E}", 1234567.89)}");
Console.WriteLine($"  千分位：{string.Format("{0:N}", 1234567.89)}");

// 日期格式
DateTime now = DateTime.Now;
Console.WriteLine($"\n日期格式：");
Console.WriteLine($"  短日期：{string.Format("{0:d}", now)}");
Console.WriteLine($"  长日期：{string.Format("{0:D}", now)}");
Console.WriteLine($"  自定义：{string.Format("{0:yyyy-MM-dd HH:mm:ss}", now)}");

Console.WriteLine();

// ---------- 9. 字符串插值（C# 6.0+） ----------
Console.WriteLine("========== 9. 字符串插值 ==========");

// 基本用法：$"..."
string interpolated = $"姓名：{name}，年龄：{age}，工资：{salary}";
Console.WriteLine($"插值字符串：{interpolated}");

// 插值中使用表达式
Console.WriteLine($"\n表达式插值：");
Console.WriteLine($"  明年年龄：{age + 1} 岁");
Console.WriteLine($"  工资翻倍：{salary * 2:C}");
Console.WriteLine($"  是否成年：{(age >= 18 ? "是" : "否")}");

// 插值 + 格式字符串
Console.WriteLine($"\n插值格式：");
Console.WriteLine($"  货币格式：{salary:C2}");
Console.WriteLine($"  日期：{now:yyyy年MM月dd日}");
Console.WriteLine($"  数字补零：{age:D3}");

// 多行插值（$@ 或 @$）
string multi = $@"
个人信息：
  姓名：{name}
  年龄：{age}
  工资：{salary:C}
";
Console.WriteLine($"多行插值：{multi}");

// 原始字符串插值（C# 11.0+）
string json = $$"""
{
    "name": "{{name}}",
    "age": {{age}},
    "salary": {{salary}}
}
""";
Console.WriteLine($"JSON 插值：\n{json}");

Console.WriteLine();

// ---------- 10. StringBuilder ----------
Console.WriteLine("========== 10. StringBuilder ==========");

// 频繁拼接字符串时使用 StringBuilder，避免创建大量临时对象

// 基本用法
StringBuilder sb = new StringBuilder();
sb.Append("Hello");
sb.Append(" ");
sb.Append("World");
sb.Append("!");
Console.WriteLine($"基本拼接：\"{sb.ToString()}\"");

// 链式调用
StringBuilder sb2 = new StringBuilder()
    .AppendLine("姓名：张三")
    .AppendLine("年龄：25")
    .AppendLine("城市：北京");
Console.WriteLine($"链式 AppendLine：\n{sb2.ToString()}");

// AppendFormat
StringBuilder sb3 = new StringBuilder();
sb3.AppendFormat("今天是 {0:yyyy年MM月dd日}", DateTime.Now);
sb3.AppendFormat("，现在时间是 {0:HH:mm:ss}", DateTime.Now);
Console.WriteLine($"AppendFormat：{sb3.ToString()}");

// 插入
StringBuilder sb4 = new StringBuilder("Hello World!");
sb4.Insert(5, " Beautiful");
Console.WriteLine($"\nInsert：\"{sb4.ToString()}\"");

// 删除
sb4.Remove(5, 10);  // 从索引 5 开始删除 10 个字符
Console.WriteLine($"Remove：\"{sb4.ToString()}\"");

// 替换
sb4.Replace("Hello", "Hi");
Console.WriteLine($"Replace：\"{sb4.ToString()}\"");

// 性能对比：拼接 10000 次
Console.WriteLine("\n性能对比（拼接 10000 次）：");
var watch = System.Diagnostics.Stopwatch.StartNew();
string strResult = "";
for (int i = 0; i < 10000; i++)
{
    strResult += i.ToString();
}
watch.Stop();
Console.WriteLine($"  string + ：{watch.ElapsedMilliseconds} ms，长度 {strResult.Length}");

watch.Restart();
StringBuilder sbResult = new StringBuilder();
for (int i = 0; i < 10000; i++)
{
    sbResult.Append(i);
}
watch.Stop();
Console.WriteLine($"  StringBuilder：{watch.ElapsedMilliseconds} ms，长度 {sbResult.Length}");

// StringBuilder 属性
Console.WriteLine($"\nStringBuilder 属性：");
Console.WriteLine($"  Length：{sbResult.Length}");
Console.WriteLine($"  Capacity：{sbResult.Capacity}");

// 清空
sbResult.Clear();
Console.WriteLine($"  Clear 后 Length：{sbResult.Length}");

Console.WriteLine();
Console.WriteLine("========== 程序结束 ==========");
