# Perl 语言基础

## 一、Perl 语言简介

### 1.1 历史

Perl（Practical Extraction and Report Language，实用提取与报告语言）由 Larry Wall 于 1987 年创建。最初设计目的是为了在 Unix 系统上进行报表处理和文本提取，后来逐渐发展成为一种功能强大的通用编程语言。

- **Perl 4** (1991)：广泛用于系统管理和 CGI 编程
- **Perl 5** (1994)：重大版本升级，引入面向对象、引用、模块等特性
- **Perl 6 / Raku** (2019)：Perl 6 正式更名为 Raku，成为独立语言
- **当前主流**：Perl 5.x 系列，最新稳定版本为 Perl 5.38+

### 1.2 核心特点

- **正则之王**：内置强大的正则表达式引擎，正则表达式是 Perl 的一等公民
- **文本处理**：极其擅长文本处理、日志分析、数据提取和报表生成
- **实用主义**："There's more than one way to do it"（TMTOWTDI，不止一种做法）
- **跨平台**：支持 Windows、Linux、macOS 等几乎所有操作系统
- **CPAN 生态**： Comprehensive Perl Archive Network，拥有数万开源模块
- **系统管理利器**：Unix/Linux 系统管理员的必备工具
- **解释型语言**：无需编译，直接运行，开发效率高

### 1.3 与安全领域的渊源

Perl 在网络安全领域有着深厚的历史地位：

- 早期的安全工具大量使用 Perl 编写（如 Nmap 早期脚本、漏洞扫描器）
- 渗透测试中的 PoC（概念验证）脚本常用 Perl 快速编写
- 日志分析、流量分析、文本提取等安全分析工作的利器
- CGI 时代的 Web 漏洞（如远程命令执行）与 Perl CGI 密切相关
- 正则表达式是安全研究中模式匹配、特征提取的核心工具

---

## 二、使用场景

| 场景 | 说明 |
|------|------|
| **系统管理** | 自动化运维脚本、日志处理、用户管理、定时任务 |
| **文本处理** | 正则匹配、日志分析、数据提取、格式转换、报表生成 |
| **网络编程** | Socket 编程、HTTP 客户端/服务端、网络爬虫 |
| **CGI Web** | 早期 Web 动态页面开发（历史上广泛使用） |
| **安全工具** | 漏洞扫描、渗透测试脚本、取证分析、入侵检测 |
| **生物信息** | DNA/蛋白质序列分析（Perl 在 bioinfo 领域曾占统治地位） |
| **数据库管理** | 数据库备份、数据迁移、报表生成 |

---

## 三、环境安装

### 3.1 Windows

**方式一：Strawberry Perl（推荐）**
- 下载地址：https://strawberryperl.com/
- 包含 Perl 解释器、gcc 编译器、常用模块
- 安装后在命令行输入 `perl -v` 验证

**方式二：ActivePerl**
- 下载地址：https://www.activestate.com/products/perl/
- 商业版，有图形化包管理器

**验证安装：**
```bash
perl -v
perl -e "print 'Hello, Perl!\n'"
```

### 3.2 Linux / macOS

大多数 Linux 发行版和 macOS 已预装 Perl：
```bash
perl -v          # 查看版本
which perl       # 查看安装路径
```

**通过包管理器安装/更新：**
```bash
# Ubuntu/Debian
sudo apt install perl

# CentOS/RHEL
sudo yum install perl

# macOS (Homebrew)
brew install perl
```

### 3.3 CPAN 模块安装

CPAN（Comprehensive Perl Archive Network）是 Perl 的模块仓库。

**进入 CPAN shell：**
```bash
cpan
```

**安装模块：**
```bash
# 在 CPAN shell 中
install Module::Name

# 或直接在命令行
cpan Module::Name
cpanm Module::Name   # 需要先安装 cpanm
```

**常用安全相关模块：**
- `LWP::UserAgent` - HTTP 客户端
- `IO::Socket::INET` - Socket 编程
- `Net::SSH::Perl` - SSH 客户端
- `Crypt::*` - 加密相关模块
- `Mojolicious` - 现代 Web 框架

---

## 四、基础语法

### 4.1 变量类型

Perl 有三种主要的变量类型，由前缀符号区分：

| 符号 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `$` | 标量 (Scalar) | 单个值：数字、字符串、引用 | `$name`, `$age`, `$ref` |
| `@` | 数组 (Array) | 有序标量列表 | `@fruits`, `@numbers` |
| `%` | 哈希 (Hash) | 键值对集合（字典） | `%user`, `%config` |

### 4.2 标量变量

```perl
# 数字
$int = 42;
$float = 3.14;
$scientific = 6.022e23;

# 字符串
$name = "Alice";
$single = '单引号字符串，不插值';
$double = "双引号字符串，变量会插值：$name";

# 字符串拼接用 . 运算符
$full = "Hello, " . $name . "!";

# 布尔值 - Perl 没有专门的布尔类型
# 以下值为假：0, "0", "", undef, 空列表
$true = 1;
$false = 0;

# undef - 未定义值
$undefined = undef;
```

### 4.3 上下文概念

Perl 的核心概念之一是**上下文（Context）**。同一个表达式在不同上下文中返回的结果不同。

主要有两种上下文：
- **标量上下文 (Scalar Context)**：期望单个值
- **列表上下文 (List Context)**：期望多个值

```perl
@array = (10, 20, 30);

# 标量上下文：返回数组长度
$count = @array;       # $count = 3

# 列表上下文：复制数组
@copy = @array;        # @copy = (10, 20, 30)

# 强制标量上下文
print scalar @array;   # 输出 3
```

### 4.4 特殊变量

Perl 内置大量特殊变量，以下是最常用的：

| 变量 | 名称 | 说明 |
|------|------|------|
| `$_` | 默认变量 | 很多函数默认操作的变量 |
| `@_` | 参数数组 | 子程序的参数列表 |
| `$/` | 输入记录分隔符 | 默认为换行符 |
| `$\` | 输出记录分隔符 | print 后自动添加 |
| `$"` | 列表分隔符 | 数组插值时的分隔符，默认空格 |
| `$!` | 系统错误信息 | 系统调用失败时的错误信息 |
| `$@` |  eval 错误 | eval 块中的错误信息 |
| `$.` | 当前行号 | 文件读取的当前行号 |
| `$0` | 程序名 | 当前脚本的文件名 |
| `$$` | 进程号 | 当前进程 PID |

---

## 五、运算符

### 5.1 算术运算符

```perl
$a = 10;
$b = 3;

$sum = $a + $b;        # 加 13
$diff = $a - $b;       # 减 7
$prod = $a * $b;       # 乘 30
$quot = $a / $b;       # 除 3.333...
$mod = $a % $b;        # 取模 1
$exp = $a ** $b;       # 幂 1000

# 自增自减
$a++;                   # $a = 11
$b--;                   # $b = 2
```

### 5.2 字符串运算符

```perl
# 字符串拼接
$greeting = "Hello" . " " . "World";   # "Hello World"

# 字符串重复
$line = "-" x 50;                       # 50个减号

# 字符串比较（注意：和数字比较不同！）
"abc" eq "abc";    # 相等，返回真
"abc" ne "def";    # 不等，返回真
"abc" lt "def";    # 小于（字典序）
"abc" gt "aaa";    # 大于
"abc" le "abc";    # 小于等于
"abc" ge "abc";    # 大于等于
```

### 5.3 数字比较运算符

```perl
$a == $b;    # 相等
$a != $b;    # 不等
$a < $b;     # 小于
$a > $b;     # 大于
$a <= $b;    # 小于等于
$a >= $b;    # 大于等于
```

> **注意**：Perl 中数字比较和字符串比较使用不同的运算符，这是常见的易错点！

### 5.4 逻辑运算符

```perl
# 高优先级版本
$a && $b;    # 与
$a || $b;    # 或
!$a;         # 非

# 低优先级版本（常用于流程控制）
$a and $b;
$a or $b;
not $a;

# 定义或运算符 // (Perl 5.10+)
$x //= "default";   # 如果 $x 为 undef，则赋值为 "default"
```

### 5.5 正则绑定运算符

```perl
# 匹配操作
$str =~ /pattern/;    # 正则匹配，成功返回真
$str !~ /pattern/;    # 不匹配

# 替换操作
$str =~ s/pattern/replacement/;

# 转义特殊字符
$str =~ /\Q[special]\E/;   # [special] 中的字符被当作字面量
```

### 5.6 三目运算符

```perl
$max = $a > $b ? $a : $b;

$status = $age >= 18 ? "成年" : "未成年";
```

---

## 六、控制流

### 6.1 if / elsif / else

```perl
if ($score >= 90) {
    print "优秀\n";
} elsif ($score >= 80) {
    print "良好\n";
} elsif ($score >= 60) {
    print "及格\n";
} else {
    print "不及格\n";
}
```

### 6.2 unless

`unless` 是 `if not` 的反义词：

```perl
unless ($error) {
    print "成功\n";
}
# 等价于
if (!$error) {
    print "成功\n";
}

# unless...else 也可以用，但不推荐
unless ($success) {
    print "失败\n";
} else {
    print "成功\n";
}
```

### 6.3 语句修饰符

Perl 支持将条件/循环写在语句后面：

```perl
print "Hello\n" if $greet;
print "Error\n" unless $success;

$total += $_ for @numbers;

$i++ while $i < 10;
```

### 6.4 for / foreach

```perl
# C 风格 for 循环
for (my $i = 0; $i < 10; $i++) {
    print "$i\n";
}

# foreach 遍历数组（for 和 foreach 是同义词）
@fruits = ("apple", "banana", "orange");
foreach my $fruit (@fruits) {
    print "$fruit\n";
}

# 简写 for
for my $fruit (@fruits) {
    print "$fruit\n";
}

# 使用默认变量 $_
for (@fruits) {
    print "$_\n";
}

# 带索引遍历
for my $i (0 .. $#fruits) {
    print "$i: $fruits[$i]\n";
}
```

### 6.5 while / until

```perl
# while 循环
my $i = 0;
while ($i < 5) {
    print "$i\n";
    $i++;
}

# until 循环（while not）
my $j = 0;
until ($j >= 5) {
    print "$j\n";
    $j++;
}

# do...while（至少执行一次）
my $k = 0;
do {
    print "$k\n";
    $k++;
} while ($k < 5);
```

### 6.6 given / when（Perl 5.10+）

类似其他语言的 switch：

```perl
use feature 'switch';

given ($fruit) {
    when ("apple")  { print "红苹果\n" }
    when ("banana") { print "黄香蕉\n" }
    when (/berry$/) { print "浆果类\n" }
    default         { print "其他水果\n" }
}
```

### 6.7 循环控制

```perl
for ($i = 0; $i < 10; $i++) {
    next if $i == 3;     # 跳过本次迭代（类似 continue）
    last if $i == 7;     # 退出循环（类似 break）
    print "$i\n";
}

# redo - 重新开始当前迭代
my $tries = 0;
{
    $tries++;
    if ($tries < 3) {
        redo;  # 回到块开头
    }
    print "尝试了 $tries 次\n";
}
```

---

## 七、函数（子程序）

### 7.1 基本定义

```perl
# 定义子程序
sub greet {
    my $name = shift;    # 从 @_ 中取出第一个参数
    print "Hello, $name!\n";
}

# 调用
greet("Alice");
greet "Bob";            # 括号可以省略
```

### 7.2 参数传递

参数通过特殊数组 `@_` 传递：

```perl
sub add {
    my ($a, $b) = @_;    # 解构参数
    return $a + $b;
}

# 或者使用 shift
sub add2 {
    my $a = shift;
    my $b = shift;
    return $a + $b;
}

# 可变参数
sub sum {
    my $total = 0;
    $total += $_ for @_;
    return $total;
}
print sum(1, 2, 3, 4, 5);   # 15
```

### 7.3 返回值

```perl
# return 显式返回
sub max {
    my ($a, $b) = @_;
    return $a if $a > $b;
    return $b;
}

# 最后一个表达式的值会被隐式返回
sub square {
    my $x = shift;
    $x * $x;    # 隐式返回
}

# 返回列表
sub get_user {
    return ("Alice", 25, "alice\@example.com");
}
my ($name, $age, $email) = get_user();

# 返回哈希
sub get_config {
    return (
        host => "localhost",
        port => 3306,
        user => "root"
    );
}
%config = get_config();
```

### 7.4 变量作用域

```perl
# my - 词法变量（块级作用域，推荐使用）
sub test_my {
    my $x = 10;        # 仅在当前块内可见
    if (1) {
        my $y = 20;    # 仅在 if 块内可见
        print $x;      # 可以访问外层的 $x
    }
    # print $y;        # 错误：$y 不可见
}

# local - 动态作用域（为全局变量创建临时值）
our $global = "original";
sub test_local {
    local $global = "local";   # 临时修改全局变量
    print $global;             # "local"
    test_nested();             # 嵌套调用也能看到
}
sub test_nested {
    print $global;             # "local"
}

# state - 静态变量（Perl 5.10+）
use feature 'state';
sub counter {
    state $count = 0;    # 只初始化一次，调用之间保留值
    return ++$count;
}
```

### 7.5 子程序引用

```perl
# 引用子程序
$ref = \&add;

# 通过引用调用
print $ref->(3, 4);    # 7
print &$ref(3, 4);     # 7（旧风格）

# 匿名子程序
$multiply = sub {
    my ($a, $b) = @_;
    return $a * $b;
};
print $multiply->(3, 4);  # 12
```

---

## 八、数组操作

### 8.1 创建数组

```perl
# 列表赋值
@nums = (1, 2, 3, 4, 5);
@fruits = ("apple", "banana", "orange");

# 空数组
@empty = ();

# 范围操作符
@range = (1 .. 10);        # 1,2,3,...,10
@letters = ('a' .. 'z');   # a到z

# qw 操作符（引号词）
@words = qw(apple banana orange);   # 等价于 ('apple', 'banana', 'orange')
```

### 8.2 访问元素

```perl
@fruits = qw(apple banana orange);

print $fruits[0];      # apple（第一个元素，注意用 $ 前缀）
print $fruits[-1];     # orange（最后一个元素）
print $fruits[10];     # undef（越界）

# 数组长度
$len = @fruits;        # 3（标量上下文）
$len = scalar @fruits; # 3
$last_index = $#fruits; # 2（最后一个元素的索引）
```

### 8.3 增删元素

```perl
@stack = (1, 2, 3);

# 末尾操作
push(@stack, 4);       # (1, 2, 3, 4) - 压栈
$top = pop(@stack);    # 4 - 弹栈

# 开头操作
unshift(@stack, 0);    # (0, 1, 2, 3) - 头插
$first = shift(@stack);# 0 - 头删

# splice - 任意位置增删
@array = (1, 2, 3, 4, 5);
splice(@array, 2, 2);           # 从索引2开始删除2个：(1, 2, 5)
splice(@array, 1, 0, 'a', 'b'); # 从索引1插入：(1, 'a', 'b', 2, 5)
splice(@array, 1, 2, 'x');      # 替换2个元素为1个：(1, 'x', 2, 5)
```

### 8.4 遍历数组

```perl
@fruits = qw(apple banana orange);

# foreach 遍历
foreach my $fruit (@fruits) {
    print "$fruit\n";
}

# 使用默认变量 $_
foreach (@fruits) {
    print "$_\n";
}

# 带索引
for my $i (0 .. $#fruits) {
    print "$i: $fruits[$i]\n";
}

# each 遍历（Perl 5.12+）
while (my ($index, $value) = each @fruits) {
    print "$index: $value\n";
}
```

### 8.5 数组函数

```perl
# 排序
@sorted = sort @nums;           # 字典序排序
@sorted_num = sort { $a <=> $b } @nums;  # 数值排序
@sorted_rev = sort { $b <=> $a } @nums;  # 数值降序

# 反转
@reversed = reverse @nums;

# 连接成字符串
$str = join(", ", @fruits);     # "apple, banana, orange"

# 分割成数组
@parts = split(/,/, "a,b,c");   # ('a', 'b', 'c')

# grep - 过滤
@evens = grep { $_ % 2 == 0 } @nums;

# map - 映射转换
@doubled = map { $_ * 2 } @nums;

# 列表切片
@subset = @nums[1, 3, 5];

# 合并数组
@combined = (@arr1, @arr2);
```

### 8.6 上下文示例

```perl
@arr = (10, 20, 30);

# 列表上下文 - 复制
@copy = @arr;          # (10, 20, 30)

# 标量上下文 - 长度
$count = @arr;         # 3

# 字符串插值
print "数组元素: @arr\n";  # "数组元素: 10 20 30"
```

---

## 九、哈希操作

### 9.1 创建哈希

```perl
# 列表形式
%user = (
    "name", "Alice",
    "age", 25,
    "email", "alice@example.com"
);

# 胖箭头形式（更清晰，推荐）
%user = (
    name  => "Alice",
    age   => 25,
    email => "alice@example.com"
);

# 空哈希
%empty = ();
```

### 9.2 访问元素

```perl
%user = (name => "Alice", age => 25);

print $user{name};     # Alice（访问单个元素，用 $ 前缀 + {}）
print $user{age};      # 25
print $user{phone};    # undef（不存在的键）

# 哈希切片
@info = @user{qw(name age)};  # ("Alice", 25)
```

### 9.3 增删改

```perl
%user = (name => "Alice");

# 添加/修改
$user{age} = 25;           # 添加键 age
$user{name} = "Bob";       # 修改键 name

# 删除
delete $user{age};         # 删除键 age

# 检查键是否存在
if (exists $user{name}) {
    print "存在 name 键\n";
}

# 清空哈希
%user = ();
```

### 9.4 遍历哈希

```perl
%config = (
    host => "localhost",
    port => 3306,
    user => "root",
    pass => "password"
);

# keys 遍历键
foreach my $key (keys %config) {
    print "$key: $config{$key}\n";
}

# values 遍历值
foreach my $value (values %config) {
    print "$value\n";
}

# each 遍历键值对
while (my ($key, $value) = each %config) {
    print "$key: $value\n";
}
```

### 9.5 常用函数

```perl
# 键和值的列表
@keys = keys %hash;
@values = values %hash;

# 哈希大小
$size = keys %hash;        # 标量上下文返回键的数量

# 反转哈希（键值互换，值必须唯一）
%reversed = reverse %hash;

# 删除并返回一个键值对（顺序随机）
$key = each %hash;

# 哈希合并
%merged = (%hash1, %hash2);   # hash2 会覆盖 hash1 中相同的键
```

### 9.6 词频统计示例

```perl
# 统计文本中每个单词出现的次数
$text = "hello world hello perl world hello";
@words = split /\s+/, $text;

%count = ();
foreach $word (@words) {
    $count{$word}++;
}

# 输出结果
while (my ($word, $num) = each %count) {
    print "$word: $num\n";
}
```

---

## 十、字符串操作

### 10.1 基本操作

```perl
$str = "Hello, World!";

# 长度
$len = length($str);        # 13

# 拼接
$full = "Hello" . " " . "World";  # 用 . 运算符

# 重复
$bar = "=" x 40;             # 40个等号

# 字符串插值
$name = "Alice";
$greeting = "Hello, $name!";          # 变量插值
$file = "file-${name}.txt";           # 用 {} 明确变量边界
```

### 10.2 查找与提取

```perl
$str = "Hello, World!";

# index - 查找子串位置
$pos = index($str, "World");    # 7
$pos = index($str, "xyz");      # -1（未找到）
$pos = index($str, "o", 5);     # 从位置5开始找第一个o

# rindex - 从右往左找
$pos = rindex($str, "o");       # 8

# substr - 提取子串
$sub = substr($str, 7, 5);      # "World"（位置7，长度5）
$sub = substr($str, 7);         # "World!"（到末尾）
$sub = substr($str, -6);        # "World!"（从右边数6个开始）

# substr 也可以替换
substr($str, 7, 5) = "Perl";   # $str 变为 "Hello, Perl!"
```

### 10.3 大小写转换

```perl
$str = "Hello, World!";

$lower = lc($str);      # "hello, world!"
$upper = uc($str);      # "HELLO, WORLD!"
$first = ucfirst($str); # 首字母大写
$first_l = lcfirst($str); # 首字母小写
```

### 10.4 分割与连接

```perl
# split - 分割字符串
$csv = "apple,banana,orange";
@fruits = split(/,/, $csv);      # ('apple', 'banana', 'orange')

# 按空白分割
$text = "one two  three\tfour";
@words = split(/\s+/, $text);    # ('one', 'two', 'three', 'four')

# join - 连接数组
$str = join(" - ", @fruits);     # "apple - banana - orange"
```

### 10.5 去除空白

```perl
$str = "  hello world  \n";

# chomp - 去除行尾换行符（只删 \n）
chomp($str);                     # 去掉末尾的换行

# 去除首尾空白（需要自己实现或用模块）
$str =~ s/^\s+|\s+$//g;          # 正则去除首尾空白
$str =~ s/^\s+//;                # 去开头空白
$str =~ s/\s+$//;                # 去结尾空白
```

### 10.6 格式化

```perl
# printf / sprintf
printf("姓名: %-10s 年龄: %03d\n", "Alice", 25);
# 输出: 姓名: Alice      年龄: 025

$formatted = sprintf("%.2f", 3.14159);   # "3.14"
```

---

## 十一、正则表达式

Perl 的正则表达式是其最强大的特性之一，被誉为"正则之王"。

### 11.1 匹配操作 m//

```perl
$str = "Hello, World!";

# 基本匹配
if ($str =~ /World/) {
    print "匹配成功\n";
}

# 不匹配
if ($str !~ /Perl/) {
    print "不匹配\n";
}

# m 可以省略，默认就是匹配
# 也可以用其他分隔符，避免转义
$path =~ m|/usr/local/bin|;     # 用 | 作分隔符
$path =~ m{/usr/local/bin};     # 用 {} 作分隔符
```

### 11.2 修饰符

```perl
# /i - 不区分大小写
$str =~ /hello/i;

# /g - 全局匹配（找到所有匹配）
while ($str =~ /(\w+)/g) {
    print "$1 ";
}

# /s - 让 . 匹配换行符
$multi =~ /start.*end/s;

# /m - 多行模式，^ 和 $ 匹配每行的开头和结尾
$multi =~ /^line/gm;

# /x - 忽略空白和注释（复杂正则的可读性）
$pattern =~ /
    ^           # 开头
    \d{3}       # 3位数字
    -           # 连字符
    \d{4}       # 4位数字
    $           # 结尾
/x;
```

### 11.3 捕获组

```perl
$email = "user@example.com";

# 捕获组用 () 表示
if ($email =~ /(\w+)@(\w+\.\w+)/) {
    $username = $1;     # "user"
    $domain = $2;       # "example.com"
    print "用户名: $username, 域名: $domain\n";
}

# 列表上下文接收所有捕获
@parts = $email =~ /(\w+)@(\w+\.\w+)/;

# 命名捕获（Perl 5.10+）
if ($email =~ /(?<user>\w+)@(?<domain>\w+\.\w+)/) {
    print $+{user};     # "user"
    print $+{domain};   # "example.com"
}

# 非捕获组 (?:...) - 分组但不捕获
if ($str =~ /(?:ab)+/) {
    # 匹配一个或多个 ab，但不捕获
}
```

### 11.4 替换操作 s///

```perl
$str = "Hello, World!";

# 基本替换
$str =~ s/World/Perl/;     # "Hello, Perl!"

# 全局替换
$text = "hello hello hello";
$text =~ s/hello/hi/g;     # "hi hi hi"

# 捕获组在替换中引用
$phone = "123-456-7890";
$phone =~ s/(\d{3})-(\d{3})-(\d{4})/($1) $2-$3/;
# 变为 "(123) 456-7890"

# 大小写转换
$name = "alice";
$name =~ s/(\w)/\U$1/;     # 首字母大写："Alice"
$str = "hello world";
$str =~ s/(\w+)/\u$1/g;    # 每个单词首字母大写："Hello World"
```

### 11.5 分割 split

```perl
# 按正则分割
$text = "a,b;c d\te";
@parts = split /[,;\s]+/, $text;   # ('a', 'b', 'c', 'd', 'e')

# 按空白分割（特殊模式 ' '）
@words = split ' ', $text;         # 等价于 split /\s+/

# 限制分割次数
@parts = split(/,/, $csv, 3);      # 最多分割成3段
```

### 11.6 常用正则模式

```perl
# 数字
/^\d+$/           # 纯数字
/^\d+\.\d+$/      # 小数

# 邮箱
/^\w+@\w+\.\w+$/

# IP地址（简单版）
/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/

# URL
/https?:\/\/[\w\.-]+(\/[\w\.-]*)*\/?/

# 日期 (YYYY-MM-DD)
/^\d{4}-\d{2}-\d{2}$/

# 中文字符
/[\x{4e00}-\x{9fa5}]/

# HTML 标签
/<[^>]+>/
```

### 11.7 特殊变量

| 变量 | 说明 |
|------|------|
| `$1`, `$2`, ... | 第 N 个捕获组的内容 |
| `$+` | 最后一个捕获组的内容 |
| `$&` | 整个匹配的字符串 |
| `` $` `` | 匹配内容之前的部分 |
| `$'` | 匹配内容之后的部分 |
| `@+` | 各捕获组结束位置 |
| `@-` | 各捕获组开始位置 |

---

## 十二、文件操作

### 12.1 打开文件

```perl
# 打开文件进行读取
open(my $fh, '<', 'filename.txt') or die "无法打开文件: $!";

# 打开文件进行写入（会清空原文件）
open(my $out, '>', 'output.txt') or die "无法创建文件: $!";

# 追加模式
open(my $log, '>>', 'log.txt') or die "无法打开日志文件: $!";

# 读写模式
open(my $rw, '+<', 'data.txt') or die "无法打开文件: $!";

# 关闭文件
close($fh);
```

### 12.2 读取文件

```perl
# 逐行读取
open(my $fh, '<', 'file.txt') or die $!;
while (my $line = <$fh>) {
    chomp($line);          # 去掉换行符
    print "行: $line\n";
}
close($fh);

# 使用默认变量 $_
open(my $fh, '<', 'file.txt') or die $!;
while (<$fh>) {
    chomp;
    print "$.\n";          # $. 是当前行号
}
close($fh);

# 一次性读取所有行到数组
open(my $fh, '<', 'file.txt') or die $!;
my @lines = <$fh>;
close($fh);

# 一次性读取整个文件
open(my $fh, '<', 'file.txt') or die $!;
local $/;                   # 取消输入记录分隔符
my $content = <$fh>;        # 整个文件内容
close($fh);
```

### 12.3 写入文件

```perl
open(my $out, '>', 'output.txt') or die $!;

# print 写入
print $out "Hello, World!\n";
print $out "第二行\n";

# printf 格式化写入
printf $out "数字: %04d\n", 42;

close($out);
```

### 12.4 文件测试操作符

```perl
$file = "test.txt";

# 存在性
if (-e $file) { print "文件存在\n"; }

# 文件类型
if (-f $file) { print "普通文件\n"; }
if (-d $file) { print "目录\n"; }
if (-l $file) { print "符号链接\n"; }

# 权限
if (-r $file) { print "可读\n"; }
if (-w $file) { print "可写\n"; }
if (-x $file) { print "可执行\n"; }

# 大小
if (-z $file) { print "空文件\n"; }
if (-s $file) { print "文件大小: " . (-s $file) . " 字节\n"; }

# 时间
$age = -M $file;    # 距修改时间的天数
$atime = -A $file;  # 距访问时间的天数
```

### 12.5 目录操作

```perl
# 打开目录
opendir(my $dh, '/path/to/dir') or die $!;

# 读取目录内容
while (my $file = readdir($dh)) {
    next if $file =~ /^\./;    # 跳过隐藏文件
    print "$file\n";
}
closedir($dh);

# 获取所有文件
my @files = readdir($dh);

# glob 模式匹配
my @txt_files = glob("*.txt");
my @all = glob("*.*");

# 创建目录
mkdir("newdir") or die $!;

# 删除目录
rmdir("emptydir") or die $!;   # 只能删空目录

# 删除文件
unlink("file.txt") or die $!;

# 重命名
rename("old.txt", "new.txt") or die $!;
```

### 12.6 命令行钻石操作符

```perl
# <> 钻石操作符：从命令行指定的文件或标准输入读取
while (<>) {
    chomp;
    print "$.\n";
}
# 运行: perl script.pl file1.txt file2.txt
```

---

## 十三、引用与复杂数据结构

### 13.1 引用基础

引用就是指向变量的指针（类似 C 语言的指针，但更安全）。

```perl
# 对标量的引用
$scalar = "hello";
$ref = \$scalar;
print $$ref;        # "hello"（解引用）

# 对数组的引用
@array = (1, 2, 3);
$ref = \@array;
print @$ref;        # (1, 2, 3)
print $ref->[0];    # 1（箭头操作符，推荐）

# 对哈希的引用
%hash = (a => 1, b => 2);
$ref = \%hash;
print %$ref;        # 解引用整个哈希
print $ref->{a};    # 1（箭头操作符）

# 对子程序的引用
$ref = sub { print "hello\n" };
$ref->();           # 调用
```

### 13.2 匿名数组和哈希

```perl
# 匿名数组（用 []）
$arr_ref = [1, 2, 3, 4];
print $arr_ref->[0];   # 1

# 匿名哈希（用 {}）
$hash_ref = {
    name  => "Alice",
    age   => 25,
    email => "alice@example.com"
};
print $hash_ref->{name};  # "Alice"
```

### 13.3 复杂数据结构

```perl
# 数组的数组（二维数组）
$matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
];
print $matrix->[1][2];    # 6

# 哈希的数组
$users = [
    { name => "Alice", age => 25 },
    { name => "Bob",   age => 30 }
];
print $users->[0]{name};  # "Alice"

# 哈希的哈希
$config = {
    database => {
        host => "localhost",
        port => 3306
    },
    server => {
        port => 8080,
        mode => "production"
    }
};
print $config->{database}{host};  # "localhost"

# 数组的哈希
$groups = {
    fruits => ["apple", "banana"],
    veggies => ["carrot", "potato"]
};
print $groups->{fruits}[0];       # "apple"
```

### 13.4 引用函数

```perl
# 判断引用类型
ref($scalar_ref);   # "SCALAR"
ref($array_ref);    # "ARRAY"
ref($hash_ref);     # "HASH"
ref($code_ref);     # "CODE"
ref($not_ref);      # undef（不是引用）

# 深拷贝（Storable 模块）
use Storable qw(dclone);
$deep_copy = dclone($complex_ref);
```

---

## 十四、模块与 CPAN

### 14.1 使用模块

```perl
# 导入模块
use strict;
use warnings;
use LWP::UserAgent;

# 导入特定函数
use List::Util qw(sum max min);

# 条件导入
use if $^O eq 'MSWin32', 'Win32::Console';

# 模块版本检查
use Module::Name 1.00;    # 要求版本至少 1.00
```

### 14.2 常用核心模块

| 模块 | 用途 |
|------|------|
| `strict` | 强制严格语法（必须声明变量） |
| `warnings` | 开启警告信息 |
| `Carp` | 更好的错误报告（croak, carp, confess） |
| `Data::Dumper` | 数据结构序列化输出（调试用） |
| `List::Util` | 列表工具函数（max, min, sum, reduce 等） |
| `File::Basename` | 文件名解析 |
| `File::Path` | 目录递归操作 |
| `Getopt::Long` | 命令行参数解析 |
| `POSIX` | POSIX 标准函数 |
| `IO::File` | 面向对象文件操作 |

### 14.3 常用 CPAN 模块

| 模块 | 用途 |
|------|------|
| `LWP::UserAgent` | HTTP 客户端 |
| `Mojolicious` | 现代 Web 框架 |
| `DBI` | 数据库接口 |
| `JSON` | JSON 处理 |
| `XML::Simple` | XML 简单处理 |
| `DateTime` | 日期时间处理 |
| `Try::Tiny` | 异常捕获 |
| `Moose` | 面向对象框架 |
| `Net::SSH2` | SSH 客户端 |
| `IO::Socket::SSL` | SSL/TLS 支持 |

### 14.4 推荐的编译指示

```perl
#!/usr/bin/perl
use strict;     # 强制变量声明，减少错误
use warnings;   # 开启警告，发现潜在问题
use feature ':5.10';  # 启用 5.10+ 特性（say, state, given 等）
```

---

## 十五、网络编程

### 15.1 Socket 编程

```perl
use IO::Socket::INET;

# TCP 客户端
$socket = IO::Socket::INET->new(
    PeerHost => 'example.com',
    PeerPort => '80',
    Proto    => 'tcp',
) or die "无法连接: $!";

print $socket "GET / HTTP/1.0\r\n\r\n";
my $response = do { local $/; <$socket> };
close($socket);
```

### 15.2 HTTP 客户端（LWP）

```perl
use LWP::UserAgent;

my $ua = LWP::UserAgent->new;
$ua->timeout(10);
$ua->agent("MyBot/1.0");

# GET 请求
my $response = $ua->get('http://example.com');
if ($response->is_success) {
    print $response->content;
} else {
    print "错误: " . $response->status_line . "\n";
}

# POST 请求
my $response = $ua->post(
    'http://example.com/api',
    { username => 'admin', password => '123456' }
);
```

### 15.3 简单 TCP 服务器

```perl
use IO::Socket::INET;

my $server = IO::Socket::INET->new(
    LocalPort => 8080,
    Type      => SOCK_STREAM,
    Reuse     => 1,
    Listen    => 10,
) or die "无法创建服务器: $!";

print "服务器监听 8080 端口...\n";

while (my $client = $server->accept()) {
    my $peer = $client->peerhost();
    print "新连接: $peer\n";
    
    while (<$client>) {
        print "收到: $_";
        print $client "Echo: $_";
    }
    close($client);
}
```

---

## 十六、Perl 在安全领域的应用

### 16.1 为什么 Perl 适合安全领域

1. **正则之王**：漏洞特征匹配、日志分析、流量分析核心能力
2. **文本处理能力**：安全日志、数据包内容、漏洞报告都是文本
3. **快速开发**：解释型语言，写 PoC 脚本快
4. **跨平台**：Windows/Linux 都能跑
5. **历史积累**：大量安全工具和 PoC 用 Perl 编写
6. **系统底层访问**：Socket、文件系统、进程控制能力强

### 16.2 常见安全应用场景

#### 1. 日志分析
```perl
# 统计 Apache 日志中每个 IP 的访问次数
while (<>) {
    if (/^(\S+)/) {
        $count{$1}++;
    }
}
# 按访问次数排序输出
foreach $ip (sort { $count{$b} <=> $count{$a} } keys %count) {
    printf "%-15s %d\n", $ip, $count{$ip};
}
```

#### 2. 漏洞扫描 PoC
```perl
# 简单的端口扫描示例
use IO::Socket::INET;

@ports = (21, 22, 23, 25, 80, 443, 3306, 8080);
$host = "192.168.1.1";

foreach $port (@ports) {
    $sock = IO::Socket::INET->new(
        PeerAddr => $host,
        PeerPort => $port,
        Proto    => 'tcp',
        Timeout  => 2,
    );
    if ($sock) {
        print "端口 $port 开放\n";
        close($sock);
    }
}
```

#### 3. 正则提取敏感信息
```perl
# 从文本中提取邮箱和手机号
$text = do { local $/; <> };

@emails = $text =~ /[\w\.-]+@[\w\.-]+\.\w+/g;
@phones = $text =~ /1[3-9]\d{9}/g;

print "找到的邮箱: @emails\n";
print "找到的手机号: @phones\n";
```

### 16.3 历史上著名的 Perl 安全工具

- **Nmap**：早期 Nmap Scripting Engine (NSE) 前，很多相关工具用 Perl
- **Nikto**：Web 服务器扫描器，Perl 编写
- **Paros Proxy**（早期版本）：Web 代理工具
- **大量 CGI 漏洞 PoC**：90 年代到 2000 年代初的 Web 漏洞验证脚本
- **Metasploit** 早期版本也曾有 Perl 实现的组件
- **OpenVAS/Nessus** 早期插件生态
- **logwatch / logcheck**：日志分析监控工具

### 16.4 学习建议

1. **打好正则基础**：Perl 的精髓在正则，也是安全分析的核心技能
2. **掌握文本处理**：数组、哈希、字符串操作是日常工作的基础
3. **学习 LWP/Socket**：网络编程是写安全工具的基础
4. **阅读现有工具源码**：Nikto、whatweb 等工具的源码很有学习价值
5. **结合安全场景练习**：日志分析、漏洞 PoC、信息收集脚本

---

## 附录：学习资源

- **Perl 官方文档**：https://perldoc.perl.org/
- **CPAN**：https://metacpan.org/
- **Perl 教程**：https://www.perl.org/learn.html
- **Modern Perl**：现代 Perl 编程指南
- **Perl 正则教程**：https://perldoc.perl.org/perlretut
