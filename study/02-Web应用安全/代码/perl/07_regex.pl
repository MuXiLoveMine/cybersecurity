#!/usr/bin/perl
# ============================================================
# 07_regex.pl - 正则表达式：匹配、替换、分割、修饰符、捕获组
# 运行方式：perl 07_regex.pl
# ============================================================

use strict;
use warnings;
use feature 'say';

# ---------- 基本匹配 ----------
say "=" x 50;
say "1. 基本匹配 (m//)";
say "=" x 50;

my $str = "Hello, World! 欢迎来到 Perl 的世界";

# 简单匹配
if ($str =~ /World/) {
    say "匹配成功：找到了 'World'";
}

# 不匹配
if ($str !~ /Python/) {
    say "匹配失败：未找到 'Python'";
}

# m 可以省略，也可以用其他分隔符
my $path = "/usr/local/bin/perl";
if ($path =~ m|/bin/|) {    # 用 | 作分隔符，避免转义 /
    say "路径中包含 /bin/";
}

if ($path =~ m{/local/}) {  # 用 {} 作分隔符
    say "路径中包含 /local/";
}

# 匹配结果
my $text = "The quick brown fox";
if ($text =~ /quick (.*?) fox/) {
    say "匹配到的整体内容: $&";   # $& 是整个匹配的字符串
    say "捕获组内容: $1";         # $1 是第一个捕获组
}

# ---------- 修饰符 ----------
say "\n" . "=" x 50;
say "2. 正则修饰符";
say "=" x 50;

# /i - 不区分大小写
my $s = "Hello, World!";
if ($s =~ /world/i) {
    say "/i 修饰符：不区分大小写匹配成功";
}

# /g - 全局匹配（找到所有匹配）
my $numbers = "abc123def456ghi789";
my @all_nums = $numbers =~ /\d+/g;
say "/g 全局匹配数字: @all_nums";

# 标量上下文 + /g：迭代匹配
my $count = 0;
while ($numbers =~ /\d+/g) {
    $count++;
}
say "数字出现次数: $count";

# /s - 让 . 匹配换行符
my $multi = "第一行\n第二行\n第三行";
if ($multi =~ /第一行.*第三行/s) {
    say "/s 修饰符：跨行匹配成功";
}

# /m - 多行模式，^ 和 $ 匹配每行的开头结尾
my $lines = "apple\nbanana\norange";
my @start_a = $lines =~ /^a.*/gm;
say "/m 修饰符：以a开头的行: @start_a";

# /x - 忽略空白和注释（提高复杂正则的可读性）
my $phone = "13812345678";
if ($phone =~ /
    ^           # 字符串开头
    1           # 以1开头
    [3-9]       # 第二位3-9
    \d{9}       # 后面9位数字
    $           # 字符串结尾
/x) {
    say "/x 修饰符：手机号格式正确";
}

# 组合使用修饰符
my $html = "<HTML>\n<Body>Hello</body>\n</HTML>";
if ($html =~ /<body>/is) {   # 不区分大小写 + 跨行
    say "组合修饰符 /is：找到 body 标签";
}

# ---------- 捕获组 ----------
say "\n" . "=" x 50;
say "3. 捕获组";
say "=" x 50;

# 普通捕获组
my $email = "user123@example.com";
if ($email =~ /(\w+)@(\w+\.\w+)/) {
    say "邮箱匹配:";
    say "  用户名: $1";
    say "  域名: $2";
}

# 列表上下文接收所有捕获
my ($user, $domain) = $email =~ /(\w+)@(\w+\.\w+)/;
say "列表接收: 用户=$user, 域名=$domain";

# 命名捕获（Perl 5.10+）
my $url = "https://www.example.com/path/to/page";
if ($url =~ /(?<protocol>https?):\/\/(?<host>[^\/]+)(?<path>\/.*)/) {
    say "命名捕获:";
    say "  协议: $+{protocol}";
    say "  主机: $+{host}";
    say "  路径: $+{path}";
}

# 非捕获组 (?:...) - 分组但不捕获
my $str2 = "ababab XYZ";
if ($str2 =~ /(?:ab)+ (.*)/) {
    say "非捕获组: \$1 = $1";   # 只有一个捕获组
}

# 贪婪与非贪婪
my $html2 = "<p>第一段</p><p>第二段</p>";
my @greedy = $html2 =~ /<p>(.*)<\/p>/g;     # 贪婪匹配
say "贪婪匹配: @greedy";

my @non_greedy = $html2 =~ /<p>(.*?)<\/p>/g;  # 非贪婪（加 ?）
say "非贪婪匹配: @non_greedy";

# ---------- 替换操作 ----------
say "\n" . "=" x 50;
say "4. 替换操作 (s///)";
say "=" x 50;

# 基本替换
my $text2 = "Hello, World!";
$text2 =~ s/World/Perl/;
say "替换后: $text2";

# 全局替换 /g
my $text3 = "苹果 香蕉 苹果 橙子 苹果";
my $count2 = ($text3 =~ s/苹果/Apple/g);
say "全局替换（替换了 $count2 处）: $text3";

# 不区分大小写替换
my $text4 = "HELLO hello Hello";
$text4 =~ s/hello/Hi/gi;
say "不区分大小写全局替换: $text4";

# 捕获组在替换中引用
my $phone2 = "13812345678";
$phone2 =~ s/(\d{3})(\d{4})(\d{4})/$1-$2-$3/;
say "手机号格式化: $phone2";

# 日期格式转换
my $date = "2024-01-15";
$date =~ s/(\d{4})-(\d{2})-(\d{2})/$1年$2月$3日/;
say "日期格式化: $date";

# 大小写转换转义
my $name = "alice smith";
$name =~ s/(\w+)/\u$1/g;     # \u 首字母大写
say "首字母大写: $name";

my $str3 = "hello world";
$str3 =~ s/(.*)/\U$1/;       # \U 全部大写
say "全部大写: $str3";

$str3 =~ s/(.*)/\L$1/;       # \L 全部小写
say "全部小写: $str3";

# 计算替换（e 修饰符）
my $math = "2 + 3 = 5";
$math =~ s/(\d+)\s*\+\s*(\d+)/$1 + $2/e;
say "计算替换: $math";

# ---------- 分割 split ----------
say "\n" . "=" x 50;
say "5. 分割 (split)";
say "=" x 50;

# 按固定字符分割
my $csv = "apple,banana,orange,grape";
my @fruits = split(/,/, $csv);
say "按逗号分割: @fruits";

# 按正则分割
my $mixed = "a,b;c d\te|f";
my @parts = split(/[,;\s\|]+/, $mixed);
say "按多种分隔符分割: @parts";

# 按空白分割（特殊模式 ' '）
my $text5 = "  one   two  three\tfour  ";
my @words = split(' ', $text5);
say "split ' ' 按空白分割: @words";

# 限制分割次数
my $path2 = "/usr/local/bin/perl";
my @path_parts = split(/\//, $path2, 3);
say "限制分割3段: @path_parts";

# 分割 IP 地址
my $ip = "192.168.1.100";
my @octets = split(/\./, $ip);
say "IP 分段: @octets";

# ---------- 常用正则模式 ----------
say "\n" . "=" x 50;
say "6. 常用正则模式示例";
say "=" x 50;

# 数字验证
my @test_nums = ("123", "-456", "3.14", "1.5e10", "abc");
foreach my $n (@test_nums) {
    my $is_int = ($n =~ /^-?\d+$/);
    my $is_float = ($n =~ /^-?\d+\.\d+$/);
    say "  '$n' - 整数: " . ($is_int ? "是" : "否") . ", 小数: " . ($is_float ? "是" : "否");
}

# 邮箱验证
my @emails = ("user@example.com", "a.b@c.d", "invalid@", "@no.com");
say "\n邮箱验证:";
foreach my $e (@emails) {
    my $valid = ($e =~ /^[\w\.-]+@[\w\.-]+\.\w+$/);
    say "  $e: " . ($valid ? "有效" : "无效");
}

# 手机号验证
my @phones = ("13812345678", "12345678901", "13812345", "19912345678");
say "\n手机号验证:";
foreach my $p (@phones) {
    my $valid = ($p =~ /^1[3-9]\d{9}$/);
    say "  $p: " . ($valid ? "有效" : "无效");
}

# IP 地址验证（简单版）
my @ips = ("192.168.1.1", "10.0.0.1", "256.1.1.1", "abc");
say "\nIP 地址验证:";
foreach my $ip_addr (@ips) {
    my $valid = ($ip_addr =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/);
    say "  $ip_addr: " . ($valid ? "格式正确" : "格式错误");
}

# URL 提取
my $html3 = 'Visit <a href="http://example.com">example</a> and <a href="https://test.org">test</a>';
my @urls = $html3 =~ /href="(https?:\/\/[^"]+)"/g;
say "\n从 HTML 中提取 URL:";
say "  $_" for @urls;

# HTML 标签去除
my $html4 = "<p>Hello <b>World</b></p>";
(my $plain = $html4) =~ s/<[^>]+>//g;
say "\n去除 HTML 标签: $plain";

# ---------- 特殊变量 ----------
say "\n" . "=" x 50;
say "7. 正则相关特殊变量";
say "=" x 50;

my $sentence = "Hello, World! How are you?";
if ($sentence =~ /World/) {
    say "匹配内容 (\$&): $&";
    say "匹配前内容 (\$`): $`";
    say "匹配后内容 (\$'): $'";
}

# 多次捕获
my $text6 = "name:Alice, age:25, city:Beijing";
my %info = $text6 =~ /(\w+):(\w+)/g;
say "\n键值对提取:";
while (my ($k, $v) = each %info) {
    say "  $k => $v";
}

# ---------- 安全领域应用 ----------
say "\n" . "=" x 50;
say "8. 安全领域应用示例";
say "=" x 50;

# 日志分析：从 Apache 日志中提取信息
my @log_lines = (
    '192.168.1.1 - - [10/Jan/2024:10:00:00 +0800] "GET /index.html HTTP/1.1" 200 1234',
    '10.0.0.5 - - [10/Jan/2024:10:01:00 +0800] "POST /login HTTP/1.1" 302 0',
    '192.168.1.1 - - [10/Jan/2024:10:02:00 +0800] "GET /admin HTTP/1.1" 403 567',
    '172.16.0.1 - - [10/Jan/2024:10:03:00 +0800] "GET /?id=1 OR 1=1 HTTP/1.1" 200 999',
);

say "日志分析 - 访问统计:";
my %ip_stats;
foreach my $line (@log_lines) {
    if ($line =~ /^(\S+).*?"(\S+) (\S+).*?" (\d{3})/) {
        my ($ip, $method, $path, $status) = ($1, $2, $3, $4);
        $ip_stats{$ip}{count}++;
        push @{$ip_stats{$ip}{requests}}, "$method $path -> $status";
    }
}

foreach my $ip (sort keys %ip_stats) {
    say "  $ip: $ip_stats{$ip}{count} 次请求";
    say "    $_" for @{$ip_stats{$ip}{requests}};
}

# SQL 注入检测（简单特征）
say "\nSQL 注入特征检测:";
my @payloads = (
    "/page?id=1",
    "/page?id=1 OR 1=1",
    "/page?id=1' UNION SELECT * FROM users--",
    "/page?id=1; DROP TABLE users--",
    "/search?q=hello",
);

foreach my $p (@payloads) {
    my $is_sqli = 0;
    $is_sqli = 1 if $p =~ /\b(OR|AND)\s+\d+\s*=\s*\d+/i;
    $is_sqli = 1 if $p =~ /\bUNION\s+SELECT\b/i;
    $is_sqli = 1 if $p =~ /\bDROP\s+TABLE\b/i;
    $is_sqli = 1 if $p =~ /'/;
    say "  $p -> " . ($is_sqli ? "疑似SQL注入" : "正常");
}

say "\n所有正则表达式示例运行完毕！";
