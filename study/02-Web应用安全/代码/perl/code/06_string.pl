#!/usr/bin/perl
# ============================================================
# 06_string.pl - 字符串操作：拼接、查找、分割、替换、格式化
# 运行方式：perl 06_string.pl
# ============================================================

use strict;
use warnings;
use feature 'say';

# ---------- 字符串拼接与重复 ----------
say "=" x 50;
say "1. 字符串拼接与重复";
say "=" x 50;

my $hello = "Hello";
my $world = "World";

# 用 . 运算符拼接
my $greeting = $hello . ", " . $world . "!";
say "拼接: $greeting";

# 变量插值（双引号中）
my $interpolated = "$hello, $world!";
say "插值: $interpolated";

# 用 x 运算符重复
my $line = "-" x 50;
say "重复: $line";

my $laugh = "ha" x 5;
say "笑: $laugh";

# 拼接变量和字面量
my $name = "Alice";
my $msg = "欢迎, " . $name . "!";
say "拼接变量: $msg";

# ---------- 字符串长度 ----------
say "\n" . "=" x 50;
say "2. 字符串长度";
say "=" x 50;

my $str = "Hello, Perl!";
say "字符串: $str";
say "长度: " . length($str);

my $chinese = "你好，世界";
say "中文字符串: $chinese";
say "长度(字符数): " . length($chinese);

# 空字符串
say "空字符串长度: " . length("");

# ---------- 查找子串 ----------
say "\n" . "=" x 50;
say "3. 查找子串 (index / rindex)";
say "=" x 50;

my $text = "The quick brown fox jumps over the lazy dog";
say "文本: $text";

# index - 从左往右找，返回首次出现的位置
my $pos = index($text, "fox");
say "fox 的位置: $pos";

$pos = index($text, "the");
say "第一个 the 的位置: $pos";

# 指定起始位置
$pos = index($text, "the", 10);
say "从位置10开始找 the: $pos";

# 未找到返回 -1
$pos = index($text, "cat");
say "cat 的位置: $pos (未找到)";

# rindex - 从右往左找
$pos = rindex($text, "the");
say "最后一个 the 的位置: $pos";

# 检查是否包含子串
my $contains = index($text, "fox") >= 0;
say "是否包含 fox: " . ($contains ? "是" : "否");

# ---------- 提取子串 ----------
say "\n" . "=" x 50;
say "4. 提取子串 (substr)";
say "=" x 50;

my $s = "Hello, World!";
say "原字符串: $s";

# substr(字符串, 起始位置, 长度)
my $sub1 = substr($s, 0, 5);
say "前5个字符: $sub1";

my $sub2 = substr($s, 7, 5);
say "位置7开始5个字符: $sub2";

# 省略长度，取到末尾
my $sub3 = substr($s, 7);
say "位置7到末尾: $sub3";

# 负索引（从右往左数）
my $sub4 = substr($s, -6);
say "倒数6个字符: $sub4";

my $sub5 = substr($s, -6, 3);
say "倒数第6个开始3个字符: $sub5";

# substr 作为左值，可以替换内容
my $s2 = "Hello, World!";
substr($s2, 7, 5) = "Perl";
say "替换后: $s2";

# ---------- 大小写转换 ----------
say "\n" . "=" x 50;
say "5. 大小写转换";
say "=" x 50;

my $mixed = "Hello, World!";
say "原字符串: $mixed";

say "全小写: " . lc($mixed);
say "全大写: " . uc($mixed);
say "首字母大写: " . ucfirst($mixed);
say "首字母小写: " . lcfirst("Hello");

# 实际应用：不区分大小写比较
my $input = "PERL";
my $target = "perl";
if (lc($input) eq lc($target)) {
    say "不区分大小写比较: 相等";
}

# ---------- 去除空白 ----------
say "\n" . "=" x 50;
say "6. 去除空白 (chomp / 正则)";
say "=" x 50;

# chomp - 去除行尾的换行符
my $with_newline = "hello world\n";
chomp($with_newline);
say "chomp 后: '$with_newline'";

# 去除首尾空白（用正则）
my $padded = "   hello world   ";
say "原字符串: '$padded'";

$padded =~ s/^\s+//;       # 去除开头空白
say "去开头空白: '$padded'";

$padded =~ s/\s+$//;       # 去除结尾空白
say "去结尾空白: '$padded'";

# 一步去除首尾空白
my $padded2 = "   hello world   ";
$padded2 =~ s/^\s+|\s+$//g;
say "一步去首尾: '$padded2'";

# ---------- 分割与连接 ----------
say "\n" . "=" x 50;
say "7. 分割与连接 (split / join)";
say "=" x 50;

# split - 分割字符串为数组
my $csv = "apple,banana,orange,grape";
my @fruits = split(/,/, $csv);
say "CSV 分割: @fruits";

# 按空白分割
my $sentence = "Hello   world\tfrom   Perl";
my @words = split(/\s+/, $sentence);
say "按空白分割: @words";

# 特殊模式 ' '（空格）等价于 /\s+/，但会忽略开头空白
my $padded_text = "   one two three   ";
my @w = split(' ', $padded_text);
say "split ' ' 分割: @w";

# 限制分割次数
my $data = "a:b:c:d:e";
my @parts = split(/:/, $data, 3);
say "限制3段: @parts";

# join - 连接数组为字符串
my @items = ("苹果", "香蕉", "橙子");
my $joined = join(" | ", @items);
say "join 连接: $joined";

my $csv_line = join(",", @items);
say "CSV 行: $csv_line";

# ---------- 字符串替换（基础） ----------
say "\n" . "=" x 50;
say "8. 字符串替换（正则替换，详见 07_regex.pl）";
say "=" x 50;

my $str2 = "Hello, World!";
$str2 =~ s/World/Perl/;
say "替换 World 为 Perl: $str2";

my $path = "/usr/local/bin/perl";
$path =~ s|/|\\|g;    # 用不同分隔符，替换所有 / 为 \
say "路径分隔符替换: $path";

# 全局替换
my $text2 = "hello hello hello";
$text2 =~ s/hello/hi/g;
say "全局替换: $text2";

# ---------- 格式化输出 ----------
say "\n" . "=" x 50;
say "9. 格式化输出 (printf / sprintf)";
say "=" x 50;

# printf - 格式化打印
printf("整数: %d\n", 42);
printf("小数: %.2f\n", 3.14159);
printf("十六进制: 0x%x\n", 255);
printf("八进制: 0o%o\n", 64);
printf("字符串: %s\n", "Hello");

# 宽度和对齐
say "\n对齐示例:";
printf("左对齐: %-10s|\n", "姓名");
printf("右对齐: %10s|\n", "Alice");
printf("数字补零: %05d\n", 42);

# 表格输出
say "\n表格示例:";
printf("%-10s %5s %8s\n", "姓名", "年龄", "分数");
printf("-" x 25 . "\n");
printf("%-10s %5d %8.1f\n", "张三", 25, 90.5);
printf("%-10s %5d %8.1f\n", "李四", 30, 85.0);
printf("%-10s %5d %8.1f\n", "王五", 28, 92.3);

# sprintf - 格式化到变量
my $formatted = sprintf("%04d-%02d-%02d", 2024, 1, 15);
say "格式化日期: $formatted";

# ---------- 字符串比较 ----------
say "\n" . "=" x 50;
say "10. 字符串比较";
say "=" x 50;

# 注意：字符串比较用 eq/ne/lt/gt/le/ge
# 数字比较用 ==/!=/</>/<=/>=
my $s1 = "abc";
my $s2 = "def";
my $s3 = "abc";

say "$s1 eq $s3: " . ($s1 eq $s3 ? "相等" : "不等");
say "$s1 ne $s2: " . ($s1 ne $s2 ? "不等" : "相等");
say "$s1 lt $s2: " . ($s1 lt $s2 ? "小于" : "不小于");
say "$s2 gt $s1: " . ($s2 gt $s1 ? "大于" : "不大于");

# 字典序比较（cmp 返回 -1, 0, 1）
my $cmp_result = $s1 cmp $s2;
say "cmp 比较结果: $cmp_result (" . ($cmp_result < 0 ? "小于" : $cmp_result > 0 ? "大于" : "等于") . ")";

# 常见错误：用 == 比较字符串
# say "abc" == "def";  # 警告！会被转为数字0比较，结果为相等（错误）

# ---------- 其他字符串函数 ----------
say "\n" . "=" x 50;
say "11. 其他字符串操作";
say "=" x 50;

# chr / ord - 字符与 ASCII 码转换
say "chr(65) = " . chr(65);     # A
say "ord('A') = " . ord('A');   # 65

# reverse - 反转字符串
my $original = "hello";
my $reversed = reverse($original);
say "反转 '$original': $reversed";

# 检查是否为数字（用正则）
my $num_str = "12345";
if ($num_str =~ /^\d+$/) {
    say "$num_str 是纯数字";
}

# 字符串重复填充
my $title = " Perl 教程 ";
my $title_len = length($title);
my $pad_len = int((50 - $title_len) / 2);
my $padded_title = ("=" x $pad_len) . $title . ("=" x $pad_len);
say $padded_title;

# 首字母大写每个单词
my $sentence2 = "hello world from perl";
$sentence2 =~ s/(\w+)/\u$1/g;
say "每个单词首字母大写: $sentence2";

say "\n所有字符串操作示例运行完毕！";
