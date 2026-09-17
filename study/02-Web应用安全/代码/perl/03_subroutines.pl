#!/usr/bin/perl
# ============================================================
# 03_subroutines.pl - 子程序（函数）：定义、参数、返回值、作用域
# 运行方式：perl 03_subroutines.pl
# ============================================================

use strict;
use warnings;
use feature 'say';
use feature 'state';   # 启用 state 静态变量

# ---------- 子程序定义 ----------
say "=" x 50;
say "1. 子程序的定义与调用";
say "=" x 50;

# 简单的子程序
sub greet {
    say "Hello, Perl!";
}

greet();    # 调用
greet;      # 括号可以省略

# ---------- 参数传递 ----------
say "\n" . "=" x 50;
say "2. 参数传递（通过 \@_ 数组）";
say "=" x 50;

# 方式一：用 shift 逐个取参数
sub say_hello {
    my $name = shift;    # 从 @_ 中取出第一个参数
    say "Hello, $name!";
}

say_hello("Alice");
say_hello "Bob";         # 括号可省略

# 方式二：解构 @_
sub add {
    my ($a, $b) = @_;    # 一次性解构所有参数
    return $a + $b;
}

my $sum = add(3, 4);
say "3 + 4 = $sum";

# 方式三：直接使用 @_
sub sum_all {
    my $total = 0;
    $total += $_ for @_;
    return $total;
}

my $total = sum_all(1, 2, 3, 4, 5);
say "1+2+3+4+5 = $total";

# 多个参数示例
sub print_user {
    my ($name, $age, $email) = @_;
    say "姓名: $name";
    say "年龄: $age";
    say "邮箱: $email";
}

print_user("张三", 25, "zhangsan\@example.com");

# ---------- 返回值 ----------
say "\n" . "=" x 50;
say "3. 返回值";
say "=" x 50;

# 显式 return
sub max {
    my ($a, $b) = @_;
    if ($a > $b) {
        return $a;
    } else {
        return $b;
    }
}

say "max(10, 20) = " . max(10, 20);

# 隐式返回：最后一个表达式的值会被返回
sub square {
    my $x = shift;
    $x * $x;    # 隐式返回（不推荐省略，但常见）
}

say "square(5) = " . square(5);

# 返回列表
sub get_user_info {
    my ($id) = @_;
    return ("用户$id", 20 + $id, "user$id\@example.com");
}

my ($name, $age, $email) = get_user_info(1);
say "用户信息: $name, $age, $email";

# 返回哈希
sub get_config {
    return (
        host => "localhost",
        port => 3306,
        user => "root"
    );
}

my %config = get_config();
say "配置: host=$config{host}, port=$config{port}";

# 返回引用（适合大数据结构）
sub get_users {
    return [
        { name => "Alice", age => 25 },
        { name => "Bob",   age => 30 }
    ];
}

my $users = get_users();
say "第一个用户: $users->[0]{name}";

# ---------- my 词法变量 ----------
say "\n" . "=" x 50;
say "4. my 词法变量（块级作用域）";
say "=" x 50;

my $outer = "外部变量";

sub test_scope {
    my $inner = "内部变量";      # 仅在子程序内可见
    say "在子程序内可以访问: $outer";   # 可以访问外部词法变量
    say "在子程序内可以访问: $inner";
}

test_scope();
# say $inner;   # 错误：$inner 不可见（作用域外）

# 块级作用域
{
    my $block_var = "块内变量";
    say "块内可以访问: $block_var";
}
# say $block_var;  # 错误：块外不可见

# 注意：循环变量也是词法作用域
for my $i (1..3) {
    say "循环内: $i";
}
# say $i;   # 错误：循环外不可见

# ---------- 默认变量 $_ ----------
say "\n" . "=" x 50;
say "5. 默认变量 \$_";
say "=" x 50;

# 很多函数默认操作 $_
sub print_list {
    for (@_) {
        say "  -> $_";        # $_ 是默认变量
    }
}

print_list("苹果", "香蕉", "橙子");

# 带参数也可以用 @_
sub show_args {
    say "参数数量: " . scalar(@_);
    say "第一个参数: $_[0]";   # 直接访问 @_ 元素
    say "最后一个参数: $_[-1]";
}

show_args("a", "b", "c");

# ---------- state 静态变量 ----------
say "\n" . "=" x 50;
say "6. state 静态变量（Perl 5.10+）";
say "=" x 50;

# state 变量只初始化一次，多次调用之间保留值
sub counter {
    state $count = 0;    # 只在第一次调用时初始化
    return ++$count;
}

say "第 " . counter() . " 次调用";
say "第 " . counter() . " 次调用";
say "第 " . counter() . " 次调用";
say "第 " . counter() . " 次调用";

# 静态变量的应用：记录函数调用历史
sub log_call {
    state @history;
    my $msg = shift;
    push @history, $msg;
    return @history;
}

log_call("启动");
log_call("处理数据");
log_call("完成");

my @logs = log_call();
say "调用历史记录:";
say "  $_" for @logs;

# ---------- 子程序引用 ----------
say "\n" . "=" x 50;
say "7. 子程序引用与匿名子程序";
say "=" x 50;

# 命名子程序的引用
my $add_ref = \&add;
say "通过引用调用: " . $add_ref->(5, 6);

# 匿名子程序
my $multiply = sub {
    my ($a, $b) = @_;
    return $a * $b;
};

say "匿名子程序: 3 * 4 = " . $multiply->(3, 4);

# 子程序作为参数传递（回调）
sub apply {
    my ($func, @nums) = @_;
    my @result;
    push @result, $func->($_) for @nums;
    return @result;
}

my $double = sub { $_[0] * 2 };
my @numbers = (1, 2, 3, 4, 5);
my @doubled = apply($double, @numbers);
say "原数组: @numbers";
say "翻倍后: @doubled";

# 闭包（Closure）：引用了外部词法变量的匿名子程序
sub make_counter {
    my $start = shift;
    return sub {
        return $start++;
    };
}

my $c1 = make_counter(10);
my $c2 = make_counter(100);

say "计数器1: " . $c1->();  # 10
say "计数器1: " . $c1->();  # 11
say "计数器2: " . $c2->();  # 100
say "计数器1: " . $c1->();  # 12
say "计数器2: " . $c2->();  # 101

# ---------- 递归 ----------
say "\n" . "=" x 50;
say "8. 递归子程序";
say "=" x 50;

# 阶乘
sub factorial {
    my $n = shift;
    return 1 if $n <= 1;       # 基线条件
    return $n * factorial($n - 1);
}

say "5! = " . factorial(5);    # 120
say "10! = " . factorial(10);  # 3628800

# 斐波那契数列
sub fib {
    my $n = shift;
    return 0 if $n == 0;
    return 1 if $n == 1;
    return fib($n - 1) + fib($n - 2);
}

say "斐波那契数列前10项:";
for my $i (0 .. 9) {
    print fib($i) . " ";
}
say "";

# ---------- 错误处理 ----------
say "\n" . "=" x 50;
say "9. 错误处理（die / eval）";
say "=" x 50;

# die - 抛出错误并退出
sub divide {
    my ($a, $b) = @_;
    die "除数不能为零" if $b == 0;
    return $a / $b;
}

# eval - 捕获异常
my $result = eval { divide(10, 0) };
if ($@) {
    say "捕获到错误: $@";
} else {
    say "结果: $result";
}

$result = eval { divide(10, 2) };
if ($@) {
    say "错误: $@";
} else {
    say "10 / 2 = $result";
}

say "\n所有子程序示例运行完毕！";
