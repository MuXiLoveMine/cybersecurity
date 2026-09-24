# print_perl

> **分类**：输出
> **说明**：Perl 输出函数

---

## 语法

```perl
print "text";\nprintf "format", args;\nsay "text";  # Perl 5.10+
```

## 输出函数

print / printf / sprintf / say / warn / die

## 特殊变量

$_ 默认变量 / $/ 输入分隔符 / $\ 输出分隔符 / $, 列表分隔符

## 示例代码

```perl
#!/usr/bin/perl
use strict;
use warnings;
use v5.10;  # 启用 say

# print - 基本输出
print "Hello, World!\n";
print "Hello", " ", "World!", "\n";  # 列表形式

my $name = "Alice";
print "你好, $name!\n";

# printf - 格式化输出
printf("姓名: %s, 年龄: %d\n", "Alice", 25);
printf("PI = %.2f\n", 3.14159);

# sprintf - 格式化到字符串
my $str = sprintf("%.2f", 3.14159);

# say - 自动换行 (Perl 5.10+)
say "Hello, World!";  # 自动加换行
say "你好, $name!";

# warn - 警告输出到 stderr
warn "这是一条警告\n";

# die - 报错并退出
# die "发生错误，程序退出\n";

# 变量插值
my $age = 25;
print "姓名: $name, 年龄: $age\n";
print "@{[$age + 1]}\n";  # 表达式插值

# 数组插值
my @fruits = ("apple", "banana", "cherry");
print "水果: @fruits\n";  # 用空格分隔

# 特殊变量 $_
my @nums = (1, 2, 3);
foreach (@nums) {
    print;         # 打印 $_
    print "\n";
}

# 文件输出
# open(my $fh, '>', 'output.txt') or die "无法打开文件: $!";
# print $fh "写入文件\n";
# close $fh;

# STDERR 输出
print STDERR "错误信息\n";
```
