// ============================================================
// 07_regex.cs - 正则表达式：匹配、查找、分组、替换、常用模式
// 运行方式：dotnet run --project .  或  csc 07_regex.cs && 07_regex.exe
// ============================================================

using System;
using System.Text.RegularExpressions;

// ---------- 1. 基本匹配 ----------
Console.WriteLine("========== 1. 基本匹配 ==========");

// IsMatch：判断是否匹配
string pattern1 = @"\d+";  // 匹配一个或多个数字
string test1 = "abc123def";
Console.WriteLine($"字符串：\"{test1}\"");
Console.WriteLine($"模式：{pattern1}");
Console.WriteLine($"IsMatch：{Regex.IsMatch(test1, pattern1)}");

// 完整匹配（开头到结尾）
string pattern2 = @"^\d+$";  // 纯数字字符串
Console.WriteLine($"\n模式：{pattern2}（纯数字）");
Console.WriteLine($"\"12345\" IsMatch：{Regex.IsMatch("12345", pattern2)}");
Console.WriteLine($"\"abc123\" IsMatch：{Regex.IsMatch("abc123", pattern2)}");
Console.WriteLine($"\"12a34\" IsMatch：{Regex.IsMatch("12a34", pattern2)}");

// 邮箱格式验证
string emailPattern = @"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$";
Console.WriteLine($"\n邮箱验证：");
Console.WriteLine($"  test@example.com -> {Regex.IsMatch("test@example.com", emailPattern)}");
Console.WriteLine($"  user.name+tag@domain.co.uk -> {Regex.IsMatch("user.name+tag@domain.co.uk", emailPattern)}");
Console.WriteLine($"  invalid@ -> {Regex.IsMatch("invalid@", emailPattern)}");
Console.WriteLine($"  @example.com -> {Regex.IsMatch("@example.com", emailPattern)}");

// 手机号验证（中国大陆）
string phonePattern = @"^1[3-9]\d{9}$";
Console.WriteLine($"\n手机号验证：");
Console.WriteLine($"  13812345678 -> {Regex.IsMatch("13812345678", phonePattern)}");
Console.WriteLine($"  19900001111 -> {Regex.IsMatch("19900001111", phonePattern)}");
Console.WriteLine($"  12345678901 -> {Regex.IsMatch("12345678901", phonePattern)}");
Console.WriteLine($"  1381234567 -> {Regex.IsMatch("1381234567", phonePattern)}（10位）");

Console.WriteLine();

// ---------- 2. 查找匹配项 ----------
Console.WriteLine("========== 2. 查找匹配项 ==========");

string text = "今天的日期是 2024-01-15，明天是 2024-01-16，后天是 2024-01-17";
Console.WriteLine($"原文：{text}");

// Match：找第一个匹配
Match firstMatch = Regex.Match(text, @"\d{4}-\d{2}-\d{2}");
if (firstMatch.Success)
{
    Console.WriteLine($"\n第一个日期：{firstMatch.Value}");
    Console.WriteLine($"  位置索引：{firstMatch.Index}");
    Console.WriteLine($"  长度：{firstMatch.Length}");
}

// Matches：找所有匹配
MatchCollection allDates = Regex.Matches(text, @"\d{4}-\d{2}-\d{2}");
Console.WriteLine($"\n找到 {allDates.Count} 个日期：");
foreach (Match m in allDates)
{
    Console.WriteLine($"  - {m.Value}（索引 {m.Index}）");
}

// 查找所有数字
string mixed = "订单号：A10025，金额：99.99元，数量：3件";
MatchCollection allNumbers = Regex.Matches(mixed, @"\d+\.?\d*");
Console.WriteLine($"\n字符串：{mixed}");
Console.WriteLine("所有数字：");
foreach (Match m in allNumbers)
{
    Console.WriteLine($"  - {m.Value}");
}

Console.WriteLine();

// ---------- 3. 分组捕获 ----------
Console.WriteLine("========== 3. 分组捕获 ==========");

// 数字分组（索引分组）
string dateStr = "2024-01-15";
Match dateMatch = Regex.Match(dateStr, @"(\d{4})-(\d{2})-(\d{2})");
if (dateMatch.Success)
{
    Console.WriteLine($"日期：{dateStr}");
    Console.WriteLine($"  完整匹配：{dateMatch.Groups[0].Value}");
    Console.WriteLine($"  年份（组1）：{dateMatch.Groups[1].Value}");
    Console.WriteLine($"  月份（组2）：{dateMatch.Groups[2].Value}");
    Console.WriteLine($"  日期（组3）：{dateMatch.Groups[3].Value}");
}

// 命名分组
string namedPattern = @"(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})";
Match namedMatch = Regex.Match(dateStr, namedPattern);
if (namedMatch.Success)
{
    Console.WriteLine($"\n命名分组：");
    Console.WriteLine($"  year = {namedMatch.Groups["year"].Value}");
    Console.WriteLine($"  month = {namedMatch.Groups["month"].Value}");
    Console.WriteLine($"  day = {namedMatch.Groups["day"].Value}");
}

// 提取 URL 信息
string url = "https://www.example.com:8080/path/to/page?id=123&name=test";
string urlPattern = @"(?<protocol>https?)://(?<host>[^:/]+)(:(?<port>\d+))?(?<path>[^?]*)(\?(?<query>.*))?";
Match urlMatch = Regex.Match(url, urlPattern);
if (urlMatch.Success)
{
    Console.WriteLine($"\nURL 解析：{url}");
    Console.WriteLine($"  协议：{urlMatch.Groups["protocol"].Value}");
    Console.WriteLine($"  主机：{urlMatch.Groups["host"].Value}");
    Console.WriteLine($"  端口：{urlMatch.Groups["port"].Value}");
    Console.WriteLine($"  路径：{urlMatch.Groups["path"].Value}");
    Console.WriteLine($"  查询：{urlMatch.Groups["query"].Value}");
}

// 提取 HTML 标签内容
string html = "<h1>标题</h1><p>这是段落</p><span>文本</span>";
MatchCollection tagMatches = Regex.Matches(html, @"<(\w+)>([^<]+)</\1>");
Console.WriteLine($"\nHTML 标签内容提取：");
foreach (Match m in tagMatches)
{
    Console.WriteLine($"  标签 <{m.Groups[1].Value}>：{m.Groups[2].Value}");
}

Console.WriteLine();

// ---------- 4. 正则替换 ----------
Console.WriteLine("========== 4. 正则替换 ==========");

// 简单替换
string input = "abc123def456ghi789";
string replaced = Regex.Replace(input, @"\d", "*");
Console.WriteLine($"原文：{input}");
Console.WriteLine($"数字替换为 *：{replaced}");

// 替换多个空格为单个空格
string messySpaces = "Hello    World   !   How   are   you?";
string cleaned = Regex.Replace(messySpaces, @"\s+", " ");
Console.WriteLine($"\n原文：\"{messySpaces}\"");
Console.WriteLine($"清理空格：\"{cleaned}\"");

// 使用分组引用替换
string phone = "13812345678";
string formattedPhone = Regex.Replace(phone, @"(\d{3})(\d{4})(\d{4})", "$1-$2-$3");
Console.WriteLine($"\n手机号：{phone}");
Console.WriteLine($"格式化：{formattedPhone}");

// 日期格式转换
string usDate = "01/15/2024";
string cnDate = Regex.Replace(usDate, @"(\d{2})/(\d{2})/(\d{4})", "$3-$1-$2");
Console.WriteLine($"\n美国日期：{usDate}");
Console.WriteLine($"中国格式：{cnDate}");

// 使用 MatchEvaluator 动态替换
string expr = "数字：5，数字：10，数字：3";
string doubled = Regex.Replace(expr, @"\d+", m => (int.Parse(m.Value) * 2).ToString());
Console.WriteLine($"\n原文：{expr}");
Console.WriteLine($"数字翻倍：{doubled}");

// 敏感信息脱敏
string idCard = "110101199001011234";
string maskedId = Regex.Replace(idCard, @"(\d{6})\d{8}(\d{4})", "$1********$2");
Console.WriteLine($"\n身份证号：{idCard}");
Console.WriteLine($"脱敏后：{maskedId}");

string emailAddr = "zhangsan@example.com";
string maskedEmail = Regex.Replace(emailAddr, @"(.{2}).*(@.*)", "$1***$2");
Console.WriteLine($"邮箱：{emailAddr}");
Console.WriteLine($"脱敏后：{maskedEmail}");

Console.WriteLine();

// ---------- 5. 正则分割 ----------
Console.WriteLine("========== 5. 正则分割 ==========");

// 按多种分隔符分割
string mixedDelimiters = "a,b;c:d e|f";
string[] splitResult = Regex.Split(mixedDelimiters, @"[,;:\s\|]");
Console.WriteLine($"原文：\"{mixedDelimiters}\"");
Console.WriteLine($"按多种分隔符分割：[{string.Join(", ", splitResult)}]");

// 按数字分割（保留分隔符前后的文本）
string withNumbers = "abc123def456ghi";
string[] splitByNumbers = Regex.Split(withNumbers, @"\d+");
Console.WriteLine($"\n原文：{withNumbers}");
Console.WriteLine($"按数字分割：[{string.Join(", ", splitByNumbers)}]");

Console.WriteLine();

// ---------- 6. RegexOptions 选项 ----------
Console.WriteLine("========== 6. RegexOptions 选项 ==========");

// IgnoreCase：忽略大小写
string ignoreCaseStr = "Hello World hello";
Console.WriteLine($"字符串：{ignoreCaseStr}");
Console.WriteLine($"匹配 \"hello\"（区分大小写）：{Regex.Matches(ignoreCaseStr, "hello").Count} 个");
Console.WriteLine($"匹配 \"hello\"（忽略大小写）：{Regex.Matches(ignoreCaseStr, "hello", RegexOptions.IgnoreCase).Count} 个");

// Multiline：多行模式（^ 和 $ 匹配每行的开头和结尾）
string multiLineText = "第一行\n第二行\n第三行";
Console.WriteLine($"\n多行文本：");
Console.WriteLine(multiLineText);
Console.WriteLine($"匹配行首数字（多行模式）：");
MatchCollection lineStarts = Regex.Matches(multiLineText, @"^第", RegexOptions.Multiline);
Console.WriteLine($"  找到 {lineStarts.Count} 个行首的\"第\"");

// Singleline：单行模式（. 匹配换行符）
string multiLineHtml = "<div>\n  Hello\n</div>";
Console.WriteLine($"\n多行 HTML：{multiLineHtml}");
Console.WriteLine($".* 匹配 div 内容（默认）：{Regex.Match(multiLineHtml, "<div>(.*)</div>").Success}");
Console.WriteLine($".* 匹配 div 内容（Singleline）：{Regex.Match(multiLineHtml, "<div>(.*)</div>", RegexOptions.Singleline).Success}");

// Compiled：编译正则（提高性能，首次使用耗时）
Console.WriteLine("\n编译正则：");
Regex compiledRegex = new Regex(@"\d+", RegexOptions.Compiled);
Console.WriteLine($"  已编译正则，匹配结果：{compiledRegex.Match("abc123").Value}");

Console.WriteLine();

// ---------- 7. 常用正则模式 ----------
Console.WriteLine("========== 7. 常用正则模式 ==========");

var patterns = new (string Name, string Pattern, string Test, bool Expected)[]
{
    ("IP地址（IPv4简化）", @"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", "192.168.1.1", true),
    ("URL", @"^https?://[^\s/$.?#].[^\s]*$", "https://example.com/path", true),
    ("中文字符", @"^[\u4e00-\u9fa5]+$", "你好世界", true),
    ("邮政编码", @"^\d{6}$", "100000", true),
    ("正整数", @"^[1-9]\d*$", "12345", true),
    ("浮点数", @"^-?\d+\.\d+$", "-3.14", true),
    ("用户名（字母开头，字母数字下划线，3-16位）", @"^[a-zA-Z][a-zA-Z0-9_]{2,15}$", "user_123", true),
    ("十六进制颜色", @"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", "#FF5733", true),
    ("身份证号（简化版18位）", @"^\d{17}[\dXx]$", "110101199001011234", true),
    ("QQ号", @"^[1-9][0-9]{4,10}$", "123456789", true),
};

foreach (var p in patterns)
{
    bool result = Regex.IsMatch(p.Test, p.Pattern);
    string status = result == p.Expected ? "✓" : "✗";
    Console.WriteLine($"{status} {p.Name}");
    Console.WriteLine($"    模式：{p.Pattern}");
    Console.WriteLine($"    测试：\"{p.Test}\" -> {result}（预期：{p.Expected}）");
}

Console.WriteLine();

// ---------- 8. 安全领域应用示例 ----------
Console.WriteLine("========== 8. 安全领域应用示例 ==========");

// 示例1：检测 SQL 注入特征
string[] testInputs = {
    "正常输入",
    "' OR '1'='1",
    "1; DROP TABLE users",
    "admin'--",
    "正常的名字"
};

string sqlInjectionPattern = @"('|(--)|(;)|(\bOR\b|\bAND\b).*=)";
Console.WriteLine("SQL 注入特征检测：");
foreach (string input in testInputs)
{
    bool isSuspicious = Regex.IsMatch(input, sqlInjectionPattern, RegexOptions.IgnoreCase);
    string mark = isSuspicious ? "⚠ 危险" : "✓ 安全";
    Console.WriteLine($"  {mark}：\"{input}\"");
}

// 示例2：检测 XSS 特征
string[] xssTests = {
    "正常文本",
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(1)",
    "<a href='http://example.com'>链接</a>"
};

string xssPattern = @"(<script|<img.*onerror|javascript:|<.*on\w+\s*=)";
Console.WriteLine("\nXSS 特征检测：");
foreach (string input in xssTests)
{
    bool isSuspicious = Regex.IsMatch(input, xssPattern, RegexOptions.IgnoreCase);
    string mark = isSuspicious ? "⚠ 危险" : "✓ 安全";
    Console.WriteLine($"  {mark}：\"{input}\"");
}

// 示例3：提取日志中的 IP 地址
string log = @"2024-01-15 10:23:45 192.168.1.100 GET /login
2024-01-15 10:23:46 10.0.0.5 POST /api/data
2024-01-15 10:23:47 172.16.0.1 GET /index.html";

MatchCollection ipMatches = Regex.Matches(log, @"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b");
Console.WriteLine("\n日志中提取的 IP 地址：");
foreach (Match m in ipMatches)
{
    Console.WriteLine($"  - {m.Value}");
}

// 示例4：密码强度检测
string[] passwords = { "123456", "abcdef", "Abc123", "Abc12345!", "P@ssw0rd123" };
string strongPasswordPattern = @"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}$";
Console.WriteLine("\n密码强度检测（至少8位，包含大小写字母、数字和特殊字符）：");
foreach (string pwd in passwords)
{
    bool isStrong = Regex.IsMatch(pwd, strongPasswordPattern);
    string mark = isStrong ? "✓ 强" : "✗ 弱";
    Console.WriteLine($"  {mark}：{pwd}");
}

Console.WriteLine();
Console.WriteLine("========== 程序结束 ==========");
