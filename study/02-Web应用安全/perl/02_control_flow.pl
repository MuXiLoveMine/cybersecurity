#!/usr/bin/perl
# ============================================================
# 02_control_flow.pl - 控制流：条件判断、循环、given-when
# 运行方式：perl 02_control_flow.pl
# ============================================================

use strict;
use warnings;
use feature 'say';
use feature 'switch';    # 启用 given/when

# ---------- if / elsif / else ----------
say "=" x 50;
say "1. if / elsif / else 条件判断";
say "=" x 50;

my $score = 85;
say "分数: $score";

if ($score >= 90) {
    say "评级: 优秀 (A)";
} elsif ($score >= 80) {
    say "评级: 良好 (B)";
} elsif ($score >= 60) {
    say "评级: 及格 (C)";
} else {
    say "评级: 不及格 (D)";
}

# 多条件判断
my $age = 20;
if ($age >= 18 && $age < 60) {
    say "年龄 $age: 成年人";
}

# ---------- unless ----------
say "\n" . "=" x 50;
say "2. unless 条件（if not 的反义词）";
say "=" x 50;

my $success = 1;

# unless 等价于 if not
unless ($success) {
    say "操作失败";
} else {
    say "操作成功（unless...else）";
}

# 更地道的用法：unless 作为语句修饰符
my $error = 0;
say "程序正常运行" unless $error;

# ---------- 三目运算符 ----------
say "\n" . "=" x 50;
say "3. 三目运算符 (条件 ? 真 : 假)";
say "=" x 50;

my $a = 10;
my $b = 20;
my $max = $a > $b ? $a : $b;
say "$a 和 $b 中较大的是: $max";

my $status = $age >= 18 ? "成年" : "未成年";
say "年龄 $age: $status";

# 嵌套三目运算符
my $grade = $score >= 90 ? "A" :
            $score >= 80 ? "B" :
            $score >= 60 ? "C" : "D";
say "分数 $score 对应的等级: $grade";

# ---------- for / foreach 循环 ----------
say "\n" . "=" x 50;
say "4. for / foreach 循环";
say "=" x 50;

# C 风格 for 循环
say "C 风格 for 循环:";
for (my $i = 1; $i <= 5; $i++) {
    say "  第 $i 次";
}

# foreach 遍历数组（for 和 foreach 是同义词）
my @fruits = ("苹果", "香蕉", "橙子", "葡萄");
say "\nforeach 遍历数组:";
foreach my $fruit (@fruits) {
    say "  水果: $fruit";
}

# for 简写（和 foreach 完全一样）
say "\nfor 简写:";
for my $f (@fruits) {
    say "  -> $f";
}

# 使用默认变量 $_
say "\n使用默认变量 \$_:";
for (@fruits) {
    say "  $_";       # $_ 是默认变量
}

# 范围操作符 ..
say "\n范围操作符 (1..10):";
for my $num (1 .. 10) {
    print "$num ";
}
say "";

# 带索引遍历
say "\n带索引遍历:";
for my $i (0 .. $#fruits) {
    say "  $i: $fruits[$i]";
}

# ---------- while / until 循环 ----------
say "\n" . "=" x 50;
say "5. while / until 循环";
say "=" x 50;

# while 循环
say "while 循环:";
my $count = 1;
while ($count <= 5) {
    say "  count = $count";
    $count++;
}

# until 循环（while not）
say "until 循环:";
my $num = 5;
until ($num <= 0) {
    say "  num = $num";
    $num--;
}

# do...while（至少执行一次）
say "do...while 循环:";
my $x = 10;
do {
    say "  x = $x";
    $x++;
} while ($x < 3);   # 条件不满足也会执行一次

# ---------- given / when ----------
say "\n" . "=" x 50;
say "6. given / when (类似 switch)";
say "=" x 50;

my $fruit = "banana";

given ($fruit) {
    when ("apple")  { say "这是苹果，红色的" }
    when ("banana") { say "这是香蕉，黄色的" }
    when ("orange") { say "这是橙子，橙色的" }
    when (/berry$/) { say "这是浆果类" }      # 支持正则匹配
    default         { say "未知水果: $_" }
}

# 用 given 判断数字范围
my $score2 = 75;
given ($score2) {
    when ($_ >= 90) { say "分数 $score2: 优秀" }
    when ($_ >= 80) { say "分数 $score2: 良好" }
    when ($_ >= 60) { say "分数 $score2: 及格" }
    default         { say "分数 $score2: 不及格" }
}

# ---------- 循环控制：next / last / redo ----------
say "\n" . "=" x 50;
say "7. 循环控制：next / last / redo";
say "=" x 50;

# next - 跳过本次循环（类似 continue）
say "next 示例（跳过偶数）:";
for my $i (1 .. 10) {
    next if $i % 2 == 0;    # 偶数跳过
    print "$i ";
}
say "";

# last - 退出循环（类似 break）
say "last 示例（遇到 7 就退出）:";
for my $i (1 .. 10) {
    last if $i == 7;        # 遇到 7 就退出
    print "$i ";
}
say "";

# redo - 重新开始当前迭代
say "redo 示例（重试 3 次）:";
my $tries = 0;
my $target = 0;
{
    $tries++;
    $target++;
    if ($tries < 3) {
        redo;               # 回到块开头重新执行
    }
    say "  尝试了 $tries 次，target = $target";
}

# ---------- 语句修饰符 ----------
say "\n" . "=" x 50;
say "8. 语句修饰符（Perl 风格）";
say "=" x 50;

# 将条件或循环写在语句后面，更简洁
my @numbers = (1, 2, 3, 4, 5);
my $total = 0;

$total += $_ for @numbers;      # for 修饰符
say "数组求和: $total";

my $found = 0;
$_ == 3 && ($found = 1) for @numbers;
say "是否找到 3: $found";

# if / unless 修饰符
my $value = 100;
say "$value 是正数" if $value > 0;
say "$value 不是负数" unless $value < 0;

# while 修饰符
my $n = 3;
print "$n " and $n-- while $n > 0;
say "";

say "\n所有控制流示例运行完毕！";
