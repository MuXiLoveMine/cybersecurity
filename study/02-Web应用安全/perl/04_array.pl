#!/usr/bin/perl
# ============================================================
# 04_array.pl - 数组操作：创建、增删改查、遍历、排序、上下文
# 运行方式：perl 04_array.pl
# ============================================================

use strict;
use warnings;
use feature 'say';

# ---------- 数组创建 ----------
say "=" x 50;
say "1. 数组的创建";
say "=" x 50;

# 列表赋值
my @nums = (1, 2, 3, 4, 5);
say "数字数组: @nums";

my @fruits = ("苹果", "香蕉", "橙子", "葡萄");
say "水果数组: @fruits";

# 空数组
my @empty = ();
say "空数组长度: " . scalar(@empty);

# 范围操作符 ..
my @range = (1 .. 10);
say "范围 1..10: @range";

my @letters = ('a' .. 'j');
say "字母 a..j: @letters";

# qw 操作符（引号词，空格分隔）
my @words = qw(apple banana orange grape);
say "qw 数组: @words";

my @mixed = (1, "hello", 3.14, "world");
say "混合类型: @mixed";

# ---------- 访问元素 ----------
say "\n" . "=" x 50;
say "2. 访问数组元素";
say "=" x 50;

@fruits = qw(apple banana orange grape);

say "第一个元素: $fruits[0]";      # 索引从0开始
say "第二个元素: $fruits[1]";
say "最后一个元素: $fruits[-1]";    # 负索引从末尾开始
say "倒数第二个: $fruits[-2]";

# 数组长度
my $len = @fruits;                  # 标量上下文返回长度
say "数组长度: $len";
say "数组长度(显式): " . scalar(@fruits);
say "最后一个索引: $#fruits";       # 最后一个元素的索引

# 数组切片
my @subset = @fruits[0, 2];         # 取第0和第2个元素
say "切片 [0,2]: @subset";

my @slice = @fruits[1 .. 3];        # 取第1到第3个元素
say "切片 [1..3]: @slice";

# ---------- 增删元素 ----------
say "\n" . "=" x 50;
say "3. 增删元素（push/pop/shift/unshift）";
say "=" x 50;

my @stack = (1, 2, 3);
say "初始数组: @stack";

# push - 末尾添加
push(@stack, 4);
say "push 4 后: @stack";

push(@stack, 5, 6);
say "push 5,6 后: @stack";

# pop - 末尾删除
my $popped = pop(@stack);
say "pop 出: $popped, 剩余: @stack";

# unshift - 开头添加
unshift(@stack, 0);
say "unshift 0 后: @stack";

# shift - 开头删除
my $shifted = shift(@stack);
say "shift 出: $shifted, 剩余: @stack";

# splice - 任意位置增删
my @array = (1, 2, 3, 4, 5);
say "\nsplice 操作，原数组: @array";

# 删除元素（位置，长度）
splice(@array, 2, 2);
say "splice(2,2) 删除后: @array";

# 插入元素（位置，0，新元素...）
@array = (1, 2, 3, 4, 5);
splice(@array, 2, 0, 'a', 'b');
say "splice(2,0,'a','b') 插入后: @array";

# 替换元素
@array = (1, 2, 3, 4, 5);
splice(@array, 1, 2, 'x', 'y', 'z');
say "splice(1,2,'x','y','z') 替换后: @array";

# ---------- 遍历数组 ----------
say "\n" . "=" x 50;
say "4. 遍历数组";
say "=" x 50;

@fruits = qw(苹果 香蕉 橙子 葡萄 西瓜);

# 方式一：foreach
say "foreach 遍历:";
foreach my $fruit (@fruits) {
    say "  $fruit";
}

# 方式二：for（和 foreach 一样）
say "\nfor 遍历:";
for my $f (@fruits) {
    say "  -> $f";
}

# 方式三：使用默认变量 $_
say "\n使用默认变量 \$_:";
for (@fruits) {
    say "  * $_";
}

# 方式四：带索引
say "\n带索引遍历:";
for my $i (0 .. $#fruits) {
    say "  [$i] $fruits[$i]";
}

# 方式五：each 遍历（Perl 5.12+）
say "\neach 遍历:";
while (my ($idx, $val) = each @fruits) {
    say "  $idx: $val";
}

# ---------- 排序 ----------
say "\n" . "=" x 50;
say "5. 数组排序";
say "=" x 50;

my @unsorted = (30, 5, 100, 1, 25, 10);
say "原数组: @unsorted";

# 默认按字典序排序（注意：数字会被当字符串比较！）
my @str_sorted = sort @unsorted;
say "字典序排序: @str_sorted";

# 数值排序（用 <=> 飞船运算符）
my @num_sorted = sort { $a <=> $b } @unsorted;
say "数值升序: @num_sorted";

# 数值降序
my @num_desc = sort { $b <=> $a } @unsorted;
say "数值降序: @num_desc";

# 字符串排序
my @strs = qw(bob Alice Charlie dave);
my @alpha_sorted = sort { lc($a) cmp lc($b) } @strs;
say "不区分大小写排序: @alpha_sorted";

# 反转
my @reversed = reverse @nums;
say "reverse 反转 (1..5): @reversed";

# ---------- 常用函数 ----------
say "\n" . "=" x 50;
say "6. 常用数组函数";
say "=" x 50;

# join - 连接成字符串
my @items = ("苹果", "香蕉", "橙子");
my $str = join(" | ", @items);
say "join: $str";

# grep - 过滤
my @numbers = (1 .. 20);
my @evens = grep { $_ % 2 == 0 } @numbers;
say "偶数: @evens";

my @greater = grep { $_ > 10 } @numbers;
say "大于10: @greater";

# map - 映射转换
my @doubled = map { $_ * 2 } @numbers;
say "翻倍: @doubled";

my @squares = map { $_ * $_ } (1 .. 10);
say "平方: @squares";

# map 也可以生成更多元素
my @pairs = map { $_, $_ * 2 } (1 .. 5);
say "成对: @pairs";

# reverse - 反转
my @rev = reverse (1 .. 5);
say "反转: @rev";

# ---------- 上下文 ----------
say "\n" . "=" x 50;
say "7. 上下文（Context）";
say "=" x 50;

my @arr = (10, 20, 30);

# 标量上下文：返回数组长度
my $count = @arr;
say "标量上下文（长度）: $count";

# 列表上下文：复制数组
my @copy = @arr;
say "列表上下文（复制）: @copy";

# 强制标量上下文
say "强制标量上下文: " . scalar(@arr);

# 字符串插值中的数组
say "字符串插值: 元素有 @arr 个";

# 在字符串中用 $" 变量控制分隔符
{
    local $" = ", ";   # 临时修改分隔符
    say "自定义分隔符: @arr";
}

# ---------- 数组合并与拆分 ----------
say "\n" . "=" x 50;
say "8. 数组合并与拆分";
say "=" x 50;

my @a = (1, 2, 3);
my @b = (4, 5, 6);

# 合并数组
my @merged = (@a, @b);
say "合并: @merged";

# 列表扁平化
my @flat = (@a, 7, 8, @b);
say "扁平化: @flat";

# split - 字符串分割成数组
my $csv = "apple,banana,orange,grape";
my @split_arr = split(/,/, $csv);
say "split 分割: @split_arr";

# 限制分割次数
my @split_limit = split(/,/, $csv, 3);
say "split 限制3段: @split_limit";

# ---------- 列表与数组的其他操作 ----------
say "\n" . "=" x 50;
say "9. 其他操作";
say "=" x 50;

# 列表赋值
my ($x, $y, $z) = (10, 20, 30);
say "列表赋值: x=$x, y=$y, z=$z";

# 交换变量
($x, $y) = ($y, $x);
say "交换后: x=$x, y=$y";

# 忽略某些值
my ($first, , $third) = (1, 2, 3, 4, 5);
say "忽略第二个: first=$first, third=$third";

# 检查元素是否存在（用 grep 或 smartmatch）
my @names = qw(Alice Bob Charlie);
my $found = grep { $_ eq 'Bob' } @names;
say "是否包含 Bob: " . ($found ? "是" : "否");

# uniq 去重（需要 List::Util 模块，这里手动实现）
my @dups = (1, 2, 2, 3, 3, 3, 4);
my %seen;
my @unique = grep { !$seen{$_}++ } @dups;
say "去重前: @dups";
say "去重后: @unique";

say "\n所有数组操作示例运行完毕！";
