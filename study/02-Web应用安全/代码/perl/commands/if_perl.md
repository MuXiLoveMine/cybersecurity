# if_perl

> **分类**：条件与循环
> **说明**：Perl 条件判断和循环

---

## 语法

```perl
if (condition) { ... } elsif (cond) { ... } else { ... }
```

## 比较运算符

数字: ==/!=/</>/<=/>=/<=>\n字符串: eq/ne/lt/gt/le/ge/cmp

## 循环

for/foreach/while/until/do...while/continue

## 修饰符

语句 if 条件 / 语句 while 条件

## 示例代码

```perl
#!/usr/bin/perl
use strict;
use warnings;

# if/elsif/else
my $age = 18;
if ($age >= 18) {
    print "成年\n";
} elsif ($age >= 6) {
    print "少年\n";
} else {
    print "儿童\n";
}

# unless（if 反义）
print "未成年\n" unless $age >= 18;

# 数字比较
if ($a == $b) { print "相等" }
if ($a != $b) { print "不等" }
if ($a > $b)  { print "大于" }
if ($a < $b)  { print "小于" }
if ($a >= $b) { print "大于等于" }
if ($a <= $b) { print "小于等于" }
if ($a <=> $b) { print "比较（-1/0/1）" }

# 字符串比较
if ($str1 eq $str2) { print "相等" }
if ($str1 ne $str2) { print "不等" }
if ($str1 lt $str2) { print "小于" }
if ($str1 gt $str2) { print "大于" }
if ($str1 cmp $str2) { print "比较" }

# 逻辑运算
if ($a > 0 && $b > 0) { print "都大于0" }
if ($a > 0 || $b > 0) { print "至少一个大于0" }
if (!$error) { print "没有错误" }
if (not $error) { print "没有错误" }

# 三元运算符
my $status = $age >= 18 ? "成年" : "未成年";

# given/when (Perl 5.10+，experimental)
# use v5.10;
# given ($day) {
#     when ("Monday") { say "星期一" }
#     default { say "其他" }
# }

# for/foreach 循环
my @nums = (1, 2, 3, 4, 5);
foreach my $n (@nums) {
    print "$n\n";
}

for (my $i = 0; $i < 5; $i++) {
    print "$i\n";
}

# while 循环
my $count = 0;
while ($count < 5) {
    print "$count\n";
    $count++;
}

# until（while 反义）
my $i = 0;
until ($i >= 5) {
    print "$i\n";
    $i++;
}

# do...while
my $j = 0;
do {
    print "$j\n";
    $j++;
} while ($j < 5);

# 修饰符形式（语句后接条件）
print "正的\n" if $num > 0;
print "$_\n" for @nums;

# last / next / redo
foreach my $n (1..10) {
    next if $n == 3;   # 跳过3
    last if $n == 7;   # 到7停止
    print "$n\n";
}
```
