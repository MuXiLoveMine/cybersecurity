#!/usr/bin/perl
# ============================================================
# 05_hash.pl - 哈希操作（字典）：创建、增删改查、遍历、词频统计
# 运行方式：perl 05_hash.pl
# ============================================================

use strict;
use warnings;
use feature 'say';

# ---------- 哈希创建 ----------
say "=" x 50;
say "1. 哈希的创建";
say "=" x 50;

# 方式一：列表形式
my %user1 = (
    "name", "Alice",
    "age", 25,
    "email", "alice@example.com"
);

# 方式二：胖箭头形式（推荐，更清晰）
my %user = (
    name  => "Alice",
    age   => 25,
    email => "alice@example.com",
    city  => "北京"
);

say "用户信息:";
say "  姓名: $user{name}";
say "  年龄: $user{age}";
say "  邮箱: $user{email}";
say "  城市: $user{city}";

# 空哈希
my %empty = ();
say "空哈希键数: " . scalar(keys %empty);

# ---------- 访问元素 ----------
say "\n" . "=" x 50;
say "2. 访问哈希元素";
say "=" x 50;

my %config = (
    host => "localhost",
    port => 3306,
    user => "root",
    pass => "password123"
);

say "host: $config{host}";
say "port: $config{port}";

# 不存在的键返回 undef
my $debug = $config{debug};
say "debug 是否存在: " . (defined($debug) ? "是，值为 $debug" : "否");

# 哈希切片
my @info = @config{qw(host port user)};
say "切片 (host,port,user): @info";

# ---------- 增删改 ----------
say "\n" . "=" x 50;
say "3. 增删改操作";
say "=" x 50;

my %student = (
    id   => "S001",
    name => "张三"
);

say "初始: id=$student{id}, name=$student{name}";

# 添加新键
$student{age} = 20;
$student{grade} = "大三";
say "添加后: age=$student{age}, grade=$student{grade}";

# 修改已有键
$student{age} = 21;
say "修改后: age=$student{age}";

# 删除键
delete $student{grade};
say "删除 grade 后，grade 是否存在: " . (exists $student{grade} ? "是" : "否");

# 检查键是否存在
say "name 键是否存在: " . (exists $student{name} ? "是" : "否");
say "phone 键是否存在: " . (exists $student{phone} ? "是" : "否");

# 清空哈希
my %temp = (a => 1, b => 2);
%temp = ();
say "清空后键数: " . scalar(keys %temp);

# ---------- 遍历哈希 ----------
say "\n" . "=" x 50;
say "4. 遍历哈希";
say "=" x 50;

my %fruit_colors = (
    apple  => "红色",
    banana => "黄色",
    orange => "橙色",
    grape  => "紫色",
    watermelon => "绿色"
);

# 方式一：keys 遍历键
say "keys 遍历:";
foreach my $fruit (keys %fruit_colors) {
    say "  $fruit: $fruit_colors{$fruit}";
}

# 方式二：按排序后的键遍历
say "\n按键排序遍历:";
foreach my $fruit (sort keys %fruit_colors) {
    say "  $fruit: $fruit_colors{$fruit}";
}

# 方式三：values 遍历值
say "\nvalues 遍历值:";
foreach my $color (values %fruit_colors) {
    say "  颜色: $color";
}

# 方式四：each 遍历键值对
say "\neach 遍历:";
while (my ($fruit, $color) = each %fruit_colors) {
    say "  $fruit -> $color";
}

# ---------- 哈希函数 ----------
say "\n" . "=" x 50;
say "5. 哈希常用函数";
say "=" x 50;

my %scores = (
    语文 => 90,
    数学 => 85,
    英语 => 95,
    物理 => 80,
    化学 => 88
);

# keys - 所有键
my @subjects = keys %scores;
say "所有科目: @subjects";

# values - 所有值
my @all_scores = values %scores;
say "所有分数: @all_scores";

# 哈希大小（键的数量）
my $size = keys %scores;
say "科目数量: $size";

# 反转哈希（键值互换，值必须唯一）
my %color_fruit = reverse %fruit_colors;
say "反转哈希 - 红色对应的水果: $color_fruit{红色}";

# 检查哈希是否为空
say "哈希是否为空: " . (%scores ? "否" : "是");

# ---------- 哈希合并 ----------
say "\n" . "=" x 50;
say "6. 哈希合并";
say "=" x 50;

my %base_config = (
    host => "localhost",
    port => 3306,
    user => "root"
);

my %override_config = (
    port => 5432,
    pass => "secret",
    db   => "mydb"
);

# 合并（后面的会覆盖前面的相同键）
my %merged = (%base_config, %override_config);
say "合并后配置:";
while (my ($k, $v) = each %merged) {
    say "  $k => $v";
}

# ---------- 词频统计 ----------
say "\n" . "=" x 50;
say "7. 经典应用：词频统计";
say "=" x 50;

my $text = "hello world hello perl world hello programming perl perl";
say "文本: $text";

my @words = split /\s+/, $text;

my %word_count = ();
foreach my $word (@words) {
    $word_count{$word}++;
}

say "\n词频统计结果:";
foreach my $word (sort keys %word_count) {
    say "  $word: $word_count{$word}";
}

# 按词频排序输出
say "\n按词频降序排列:";
foreach my $word (sort { $word_count{$b} <=> $word_count{$a} } keys %word_count) {
    say "  $word: $word_count{$word}";
}

# ---------- 嵌套数据结构 ----------
say "\n" . "=" x 50;
say "8. 复杂数据结构（哈希的哈希）";
say "=" x 50;

# 哈希的哈希（HoH - Hash of Hashes）
my %users = (
    alice => {
        age  => 25,
        city => "北京",
        email => "alice@example.com"
    },
    bob => {
        age  => 30,
        city => "上海",
        email => "bob@example.com"
    },
    charlie => {
        age  => 28,
        city => "广州",
        email => "charlie@example.com"
    }
);

say "Alice 的年龄: $users{alice}{age}";
say "Bob 的城市: $users{bob}{city}";

# 遍历所有用户
say "\n所有用户信息:";
foreach my $username (sort keys %users) {
    my $info = $users{$username};
    say "  $username: $info->{age}岁, $info->{city}, $info->{email}";
}

# 哈希的数组（AoH - Array of Hashes）
my @people = (
    { name => "张三", age => 25, city => "北京" },
    { name => "李四", age => 30, city => "上海" },
    { name => "王五", age => 28, city => "广州" }
);

say "\n数组中的哈希:";
say "  第一个人: $people[0]{name}, $people[0]{age}岁";

foreach my $person (@people) {
    say "  $person->{name} - $person->{age}岁 - $person->{city}";
}

# ---------- 哈希的实际应用 ----------
say "\n" . "=" x 50;
say "9. 实际应用：IP 访问统计";
say "=" x 50;

# 模拟访问日志
my @log_lines = (
    "192.168.1.1 - - [01/Jan/2024] GET /index.html",
    "192.168.1.2 - - [01/Jan/2024] GET /about.html",
    "192.168.1.1 - - [01/Jan/2024] POST /login",
    "10.0.0.1 - - [01/Jan/2024] GET /admin",
    "192.168.1.1 - - [01/Jan/2024] GET /dashboard",
    "192.168.1.2 - - [01/Jan/2024] GET /contact",
    "10.0.0.1 - - [01/Jan/2024] POST /admin/config",
    "192.168.1.3 - - [01/Jan/2024] GET /index.html",
);

my %ip_count = ();
my %ip_pages = ();

foreach my $line (@log_lines) {
    if ($line =~ /^(\S+).*? (GET|POST) (\S+)/) {
        my $ip = $1;
        my $page = $3;
        $ip_count{$ip}++;
        push @{$ip_pages{$ip}}, $page;   # 哈希的值是数组引用
    }
}

say "各 IP 访问次数（按访问量排序）:";
foreach my $ip (sort { $ip_count{$b} <=> $ip_count{$a} } keys %ip_count) {
    say "  $ip: $ip_count{$ip} 次";
    say "    访问页面: @{$ip_pages{$ip}}";
}

say "\n所有哈希操作示例运行完毕！";
