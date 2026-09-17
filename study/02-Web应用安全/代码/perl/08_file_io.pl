#!/usr/bin/perl
# ============================================================
# 08_file_io.pl - 文件操作：读写文件、文件测试、目录操作
# 运行方式：perl 08_file_io.pl
# ============================================================

use strict;
use warnings;
use feature 'say';
use File::Basename;   # 文件名解析
use File::Path qw(make_path remove_tree);  # 目录操作

# 定义测试目录
my $test_dir = "perl_file_test";
my $test_file = "$test_dir/test.txt";
my $output_file = "$test_dir/output.txt";

# 清理之前的测试文件（如果存在）
if (-d $test_dir) {
    remove_tree($test_dir);
}

# 创建测试目录
make_path($test_dir) or die "无法创建目录: $!";

# ---------- 写入文件 ----------
say "=" x 50;
say "1. 写入文件";
say "=" x 50;

# 方式一：open + print
open(my $out, '>', $test_file) or die "无法创建文件 '$test_file': $!";
print $out "第一行：Hello, Perl!\n";
print $out "第二行：文件操作示例\n";
print $out "第三行：第三行内容\n";
print $out "第四行：第四行内容\n";
print $out "第五行：第五行内容\n";
close($out);

say "已创建文件: $test_file";

# 方式二：追加写入
open(my $append, '>>', $test_file) or die "无法打开文件追加: $!";
print $append "第六行：追加的内容\n";
print $append "第七行：再追加一行\n";
close($append);

say "已追加内容到: $test_file";

# printf 格式化写入
open(my $fmt_out, '>', $output_file) or die $!;
printf $fmt_out "%-10s %5s %8s\n", "姓名", "年龄", "分数";
printf $fmt_out "%s\n", "-" x 25;
printf $fmt_out "%-10s %5d %8.1f\n", "张三", 25, 90.5;
printf $fmt_out "%-10s %5d %8.1f\n", "李四", 30, 85.0;
printf $fmt_out "%-10s %5d %8.1f\n", "王五", 28, 92.3;
close($fmt_out);

say "已写入格式化数据到: $output_file";

# ---------- 读取文件 ----------
say "\n" . "=" x 50;
say "2. 读取文件";
say "=" x 50;

# 方式一：逐行读取（推荐，内存占用小）
say "逐行读取 '$test_file':";
open(my $in, '<', $test_file) or die "无法打开文件 '$test_file': $!";
my $line_num = 1;
while (my $line = <$in>) {
    chomp($line);   # 去掉换行符
    say "  行 $line_num: $line";
    $line_num++;
}
close($in);

# 方式二：使用默认变量 $_
say "\n使用默认变量读取:";
open(my $in2, '<', $test_file) or die $!;
while (<$in2>) {
    chomp;
    say "  $. : $_";   # $. 是当前行号
}
close($in2);

# 方式三：一次性读取所有行到数组
say "\n一次性读取所有行:";
open(my $in3, '<', $test_file) or die $!;
my @lines = <$in3>;
close($in3);
chomp(@lines);   # 批量去掉换行符
say "  共 " . scalar(@lines) . " 行";
say "  第三行: $lines[2]";

# 方式四：一次性读取整个文件
say "\n一次性读取整个文件:";
open(my $in4, '<', $test_file) or die $!;
local $/;         # 取消输入记录分隔符
my $content = <$in4>;
close($in4);
say "  文件大小: " . length($content) . " 字节";
say "  内容预览: " . substr($content, 0, 50) . "...";

# ---------- 文件测试 ----------
say "\n" . "=" x 50;
say "3. 文件测试操作符";
say "=" x 50;

my $file = $test_file;
say "测试文件: $file";

# 存在性
say "  存在 (-e): " . (-e $file ? "是" : "否");

# 文件类型
say "  普通文件 (-f): " . (-f $file ? "是" : "否");
say "  目录 (-d): " . (-d $file ? "是" : "否");
say "  符号链接 (-l): " . (-l $file ? "是" : "否");

# 权限
say "  可读 (-r): " . (-r $file ? "是" : "否");
say "  可写 (-w): " . (-w $file ? "是" : "否");
say "  可执行 (-x): " . (-x $file ? "是" : "否");

# 大小
say "  非空 (-s): " . (-s $file ? "是 (" . (-s $file) . " 字节)" : "否 (空文件)");
say "  空文件 (-z): " . (-z $file ? "是" : "否");

# 目录测试
say "\n测试目录: $test_dir";
say "  存在 (-e): " . (-e $test_dir ? "是" : "否");
say "  是目录 (-d): " . (-d $test_dir ? "是" : "否");

# ---------- 目录操作 ----------
say "\n" . "=" x 50;
say "4. 目录操作";
say "=" x 50;

# 创建目录
my $subdir = "$test_dir/subdir";
mkdir($subdir) or die "无法创建目录: $!";
say "创建目录: $subdir";

# 创建多级目录
my $deep_dir = "$test_dir/a/b/c";
make_path($deep_dir);   # 需要 File::Path
say "创建多级目录: $deep_dir";

# 打开目录读取
say "\n目录 '$test_dir' 内容:";
opendir(my $dh, $test_dir) or die "无法打开目录: $!";
while (my $entry = readdir($dh)) {
    next if $entry =~ /^\./;    # 跳过 . 和 .. 及隐藏文件
    my $full_path = "$test_dir/$entry";
    my $type = -d $full_path ? "目录" : "文件";
    say "  $entry ($type)";
}
closedir($dh);

# glob 模式匹配
say "\nglob 查找 .txt 文件:";
my @txt_files = glob("$test_dir/*.txt");
foreach my $f (@txt_files) {
    say "  " . basename($f) . " (" . (-s $f) . " 字节)";
}

# 递归查找（简单实现）
say "\n递归查找所有文件:";
my @all_files = find_all_files($test_dir);
foreach my $f (@all_files) {
    say "  $f";
}

# ---------- 文件操作 ----------
say "\n" . "=" x 50;
say "5. 文件重命名、复制、删除";
say "=" x 50;

# 重命名
my $old_name = "$test_dir/test.txt";
my $new_name = "$test_dir/renamed.txt";
rename($old_name, $new_name) or die "重命名失败: $!";
say "重命名: $old_name -> $new_name";

# 复制（用模块）
use File::Copy;
my $copy_name = "$test_dir/copy.txt";
copy($new_name, $copy_name) or die "复制失败: $!";
say "复制: $new_name -> $copy_name";

# 删除文件
unlink($copy_name) or die "删除失败: $!";
say "删除文件: $copy_name";

# 删除空目录
my $empty_dir = "$test_dir/empty_dir";
mkdir($empty_dir);
rmdir($empty_dir) or die "删除目录失败: $!";
say "删除空目录: $empty_dir";

# ---------- 处理 CSV 文件 ----------
say "\n" . "=" x 50;
say "6. 实际应用：处理 CSV 文件";
say "=" x 50;

# 写入 CSV
my $csv_file = "$test_dir/users.csv";
open(my $csv_out, '>', $csv_file) or die $!;
print $csv_out "id,name,age,city\n";
print $csv_out "1,张三,25,北京\n";
print $csv_out "2,李四,30,上海\n";
print $csv_out "3,王五,28,广州\n";
print $csv_out "4,赵六,35,深圳\n";
close($csv_out);

say "已创建 CSV 文件: $csv_file";

# 读取并解析 CSV
say "\n读取并解析 CSV:";
open(my $csv_in, '<', $csv_file) or die $!;
my $header = <$csv_in>;  # 跳过表头
chomp($header);
my @headers = split(/,/, $header);
say "表头: @headers";

my @users;
while (<$csv_in>) {
    chomp;
    my ($id, $name, $age, $city) = split(/,/);
    push @users, { id => $id, name => $name, age => $age, city => $city };
    say "  ID:$id 姓名:$name 年龄:$age 城市:$city";
}
close($csv_in);

# 统计
say "\n统计信息:";
my $total_age = 0;
$total_age += $_->{age} for @users;
say "  总人数: " . scalar(@users);
say "  平均年龄: " . ($total_age / @users);

# ---------- 日志分析 ----------
say "\n" . "=" x 50;
say "7. 实际应用：日志分析";
say "=" x 50;

# 创建模拟日志文件
my $log_file = "$test_dir/access.log";
open(my $log_out, '>', $log_file) or die $!;
print $log_out '192.168.1.1 - - [10/Jan/2024:10:00:00 +0800] "GET /index.html HTTP/1.1" 200 1234' . "\n";
print $log_out '192.168.1.2 - - [10/Jan/2024:10:01:00 +0800] "GET /about.html HTTP/1.1" 200 567' . "\n";
print $log_out '10.0.0.1 - - [10/Jan/2024:10:02:00 +0800] "GET /admin HTTP/1.1" 403 200' . "\n";
print $log_out '192.168.1.1 - - [10/Jan/2024:10:03:00 +0800] "POST /login HTTP/1.1" 302 0' . "\n";
print $log_out '192.168.1.1 - - [10/Jan/2024:10:04:00 +0800] "GET /dashboard HTTP/1.1" 200 2000' . "\n";
print $log_out '172.16.0.5 - - [10/Jan/2024:10:05:00 +0800] "GET /?id=1 OR 1=1 HTTP/1.1" 500 100' . "\n";
print $log_out '10.0.0.1 - - [10/Jan/2024:10:06:00 +0800] "GET /admin/users HTTP/1.1" 403 200' . "\n";
print $log_out '192.168.1.3 - - [10/Jan/2024:10:07:00 +0800] "GET /index.html HTTP/1.1" 200 1234' . "\n";
close($log_out);

say "已创建日志文件: $log_file";

# 分析日志
say "\n日志分析结果:";
open(my $log_in, '<', $log_file) or die $!;

my %ip_count;
my %status_count;
my @error_requests;

while (<$log_in>) {
    chomp;
    if (/^(\S+).*?" (\S+) (\S+) .*?" (\d{3})/) {
        my ($ip, $method, $path, $status) = ($1, $2, $3, $4);
        $ip_count{$ip}++;
        $status_count{$status}++;
        if ($status >= 400) {
            push @error_requests, "$ip $method $path -> $status";
        }
    }
}
close($log_in);

# IP 访问统计
say "\nIP 访问统计（按访问量排序）:";
foreach my $ip (sort { $ip_count{$b} <=> $ip_count{$a} } keys %ip_count) {
    say "  $ip: $ip_count{$ip} 次";
}

# 状态码统计
say "\n状态码统计:";
foreach my $status (sort keys %status_count) {
    say "  $status: $status_count{$status} 次";
}

# 错误请求
say "\n错误请求 (4xx/5xx):";
say "  $_" for @error_requests;

# ---------- 钻石操作符 <> ----------
say "\n" . "=" x 50;
say "8. 钻石操作符 <> 简介";
say "=" x 50;

say "钻石操作符 <> 可以从命令行指定的文件或标准输入读取";
say "用法: perl script.pl file1.txt file2.txt";
say "也可以通过管道: cat file.txt | perl script.pl";

# ---------- 清理测试文件 ----------
say "\n" . "=" x 50;
say "清理测试文件";
say "=" x 50;

# 保留测试目录供查看，只打印提示
say "测试文件保存在: $test_dir";
say "可以手动删除以清理";

say "\n所有文件操作示例运行完毕！";

# ---------- 辅助函数 ----------
sub find_all_files {
    my ($dir) = @_;
    my @files;
    
    opendir(my $dh, $dir) or return ();
    while (my $entry = readdir($dh)) {
        next if $entry =~ /^\./;
        my $path = "$dir/$entry";
        if (-d $path) {
            push @files, find_all_files($path);
        } else {
            push @files, $path;
        }
    }
    closedir($dh);
    
    return @files;
}
