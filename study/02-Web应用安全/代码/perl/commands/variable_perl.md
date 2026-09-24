# variable_perl

> **分类**：变量与类型
> **说明**：Perl 变量（标量/数组/哈希）

---

## 语法

```perl
$scalar  标量\n@array   数组\n%hash    哈希
```

## 变量类型

标量 $ / 数组 @ / 哈希 % / 类型团 *

## 特殊变量

$_ 默认变量 / @_ 函数参数 / %ENV 环境变量 / $! 错误信息 / $$ PID

## 示例代码

```perl
#!/usr/bin/perl
use strict;
use warnings;

# ===== 标量 $ =====
my $name = "Alice";     # 字符串
my $age = 25;           # 整数
my $price = 9.99;       # 浮点数
my $flag = 1;           # 布尔（Perl 没有专门的 bool）
my $nothing = undef;    # 未定义

# 字符串操作
my $str = "Hello, Perl!";
length($str);               # 长度
substr($str, 0, 5);         # "Hello"
uc($str);                   # 大写
lc($str);                   # 小写
reverse($str);              # 反转
index($str, "Perl");        # 查找位置
$str =~ s/Perl/World/g;     # 替换

# 数字操作
my $sum = 10 + 5;
my $diff = 10 - 5;
my $prod = 10 * 5;
my $quot = 10 / 3;          # 3.333...
my $mod = 10 % 3;           # 1
my $pow = 2 ** 10;          # 1024

# 类型转换
my $num = "123" + 0;        # 转数字
my $text = 456 . "";        # 转字符串

# ===== 数组 @ =====
my @fruits = ("apple", "banana", "cherry");
$fruits[0];                 # "apple"
$fruits[1] = "orange";      # 修改
$#fruits;                   # 最后一个索引（2）
scalar(@fruits);            # 元素个数（3）

# 数组操作
push(@fruits, "grape");     # 末尾添加
pop(@fruits);               # 末尾弹出
unshift(@fruits, "mango");  # 开头添加
shift(@fruits);             # 开头弹出
@fruits = reverse(@fruits); # 反转
my @sorted = sort(@fruits); # 排序

# 数组切片
my @subset = @fruits[0, 2];

# 遍历
foreach my $fruit (@fruits) {
    print "$fruit\n";
}

# ===== 哈希 % =====
my %person = (
    name => "Alice",
    age  => 25,
    city => "Beijing",
);

$person{name};              # "Alice"
$person{email} = "a@test.com";  # 添加
delete $person{city};       # 删除

# 判断存在
exists $person{name};       # 键是否存在
defined $person{age};       # 值是否定义

# 遍历
while (my ($key, $value) = each %person) {
    print "$key: $value\n";
}

foreach my $key (keys %person) {
    print "$key: $person{$key}\n";
}

# keys/values
my @keys = keys %person;
my @values = values %person;

# ===== 特殊变量 =====
$_;         # 默认变量
@_;         # 函数参数列表
%ENV;       # 环境变量
$!;         # 系统错误信息
$$;         # 当前进程 PID
$0;         # 脚本名
$\;        # 输出记录分隔符
$/;        # 输入记录分隔符
```
