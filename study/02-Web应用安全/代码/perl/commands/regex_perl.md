# regex_perl

> **分类**：正则表达式
> **说明**：Perl 正则匹配、替换和分割

---

## 语法

```perl
$str =~ /pattern/;   # 匹配\n$str =~ s/old/new/;  # 替换\n@parts = split /pattern/, $str;  # 分割
```

## 修饰符

i 忽略大小写 / g 全局 / m 多行 / s 单行(.匹配换行) / x 扩展

## 常用模式

\d 数字 / \w 单词字符 / \s 空白 / . 任意字符 / * 零或多 / + 一或多 / ? 零或一

## 示例代码

```perl
#!/usr/bin/perl
use strict;
use warnings;

# ===== 匹配 =====
my $str = "Hello, World!";

# 基本匹配
if ($str =~ /World/) {
    print "匹配成功\n";
}

# 忽略大小写
if ($str =~ /world/i) {
    print "忽略大小写匹配\n";
}

# 捕获组
my $email = "alice@example.com";
if ($email =~ /(\w+)@(\w+\.\w+)/) {
    my $username = $1;
    my $domain = $2;
    print "用户名: $username, 域名: $domain\n";
}

# 命名捕获 (Perl 5.10+)
if ($email =~ /(?<user>\w+)@(?<domain>\w+\.\w+)/) {
    print "用户: $+{user}, 域名: $+{domain}\n";
}

# 匹配所有
my $text = "apple banana apple cherry apple";
my @matches = ($text =~ /apple/g);
print "apple 出现了 " . scalar(@matches) . " 次\n";

# ===== 替换 =====
my $s = "Hello, World!";
$s =~ s/World/Perl/;        # 替换第一个
print "$s\n";              # Hello, Perl!

$s = "foo bar foo baz foo";
$s =~ s/foo/XXX/g;          # 全局替换
print "$s\n";              # XXX bar XXX baz XXX

# 大小写转换
$s = "hello world";
$s =~ s/(\w+)/\u$1/g;     # 首字母大写
print "$s\n";              # Hello World

# ===== 分割 =====
my $csv = "apple,banana,cherry,date";
my @fruits = split /,/, $csv;
print "@fruits\n";

# 多个分隔符
my $data = "a b,c;d";
my @parts = split /[ ,;]/, $data;

# 限制分割次数
my ($first, $rest) = split /,/, $csv, 2;

# ===== 常用正则 =====
my $phone = "13812345678";
if ($phone =~ /^1[3-9]\d{9}$/) {
    print "手机号格式正确\n";
}

my $url = "https://example.com/path";
if ($url =~ m{^https?://}) {
    print "是 HTTP URL\n";
}

# 验证 IP
my $ip = "192.168.1.1";
if ($ip =~ /^(\d{1,3}\.){3}\d{1,3}$/) {
    print "可能是 IP\n";
}

# 去掉首尾空白
my $trimmed = "  hello  ";
$trimmed =~ s/^\s+|\s+$//g;
```
