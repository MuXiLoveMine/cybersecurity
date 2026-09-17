#!/usr/bin/perl
# ============================================================
# 01_hello.pl - Perl 基础入门：Hello World、变量、数据类型
# 运行方式：perl 01_hello.pl
# ============================================================

use strict;
use warnings;
use feature 'say';  # 启用 say 函数（自动加换行）

# ---------- Hello World ----------
say "=" x 50;
say "1. Hello World";
say "=" x 50;

print "Hello, Perl!\n";          # print 需要手动加换行符
say "Hello, World!";             # say 自动添加换行符（Perl 5.10+）

# ---------- 标量变量 ----------
say "\n" . "=" x 50;
say "2. 标量变量 (\$)";
say "=" x 50;

# 数字类型
my $int = 42;                    # 整数
my $float = 3.14159;             # 浮点数
my $scientific = 6.022e23;       # 科学计数法

say "整数: $int";
say "浮点数: $float";
say "科学计数: $scientific";

# 字符串类型
my $name = "Alice";
my $age = 25;

# 单引号字符串：不进行变量插值和转义（除了 \' 和 \\）
my $single_str = '单引号字符串: $name 不会被插值\n';
say $single_str;

# 双引号字符串：变量会被插值，支持转义字符
my $double_str = "双引号字符串: 我是 $name，今年 $age 岁\n";
print $double_str;

# 字符串拼接用 . 运算符
my $greeting = "Hello, " . $name . "!";
say "字符串拼接: $greeting";

# 字符串重复用 x 运算符
my $separator = "-" x 30;
say "字符串重复: $separator";

# ---------- 特殊值 ----------
say "\n" . "=" x 50;
say "3. 特殊值";
say "=" x 50;

# undef - 未定义值
my $undefined;
say "undef 值: " . (defined($undefined) ? "已定义" : "未定义");

$undefined = 10;
say "赋值后: " . (defined($undefined) ? "已定义" : "未定义");

# 布尔值 - Perl 没有专门的布尔类型
# 以下值为假：0, "0", "", undef, 空列表 ()
my $true_val = 1;
my $false_val = 0;

say "真值: $true_val";
say "假值: $false_val";
say "空字符串为假: " . ("" ? "真" : "假");
say "字符串'0'为假: " . ("0" ? "真" : "假");

# ---------- 变量插值 ----------
say "\n" . "=" x 50;
say "4. 变量插值";
say "=" x 50;

my $fruit = "apple";
my @fruits = ("apple", "banana", "orange");
my %user = (name => "Bob", age => 30);

# 标量插值
say "我喜欢 $fruit";                    # 标量变量插值
say "我喜欢 ${fruit}s";                 # 用 {} 明确变量边界

# 数组插值（元素用空格分隔）
say "水果列表: @fruits";

# 哈希不能直接插值
say "用户名: $user{name}";              # 访问哈希元素
say "年龄: $user{age}";

# ---------- 转义字符 ----------
say "\n" . "=" x 50;
say "5. 转义字符";
say "=" x 50;

print "制表符:\t第一列\t第二列\n";
print "换行符:\n第一行\n第二行\n";
print "反斜杠: \\\n";
print "双引号: \"Hello\"\n";
print "退格: Hello\b \n";

# ---------- 环境变量 ----------
say "\n" . "=" x 50;
say "6. 特殊变量和环境变量";
say "=" x 50;

say "当前脚本名: $0";                   # $0 是脚本文件名
say "当前进程号: $$";                   # $$ 是进程 PID

# 环境变量在 %ENV 哈希中
if (exists $ENV{PATH}) {
    my @path_parts = split(/;/, $ENV{PATH});
    say "PATH 包含 " . scalar(@path_parts) . " 个目录";
    say "第一个目录: $path_parts[0]";
}

say "\n程序运行完毕！";
