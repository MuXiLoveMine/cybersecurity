#!/usr/bin/perl
# ============================================================
# Web 目录爆破工具 (Directory Brute Force)
# ============================================================
#
# 【原理说明】
# 目录爆破是 Web 安全测试中用于发现隐藏目录和文件的常用技术。
# 本工具通过字典枚举的方式，向目标 Web 服务器发送大量 HTTP 请求，
# 根据响应状态码判断目录/文件是否存在。
#
# 【常见状态码含义】
#   200 OK          - 页面/文件存在且可正常访问
#   301/302 重定向   - 页面存在但发生了跳转
#   403 Forbidden    - 页面存在但禁止访问
#   404 Not Found    - 页面不存在
#   500 Internal Error - 服务器内部错误
#
# 【使用方法】
#   perl dir_brute.pl <目标URL> [字典文件] [并发数] [超时时间]
#
# 【参数说明】
#   目标URL   - 必填，目标网站 URL，例如 http://example.com
#   字典文件  - 可选，字典文件路径，每行一个路径
#               不指定则使用内置字典
#   并发数    - 可选，并发子进程数，默认 15
#   超时时间  - 可选，请求超时时间（秒），默认 10
#
# 【示例】
#   perl dir_brute.pl http://127.0.0.1
#   perl dir_brute.pl http://example.com wordlist.txt 20
#   perl dir_brute.pl https://target.com /path/to/dict.txt 30 15
#
# 【依赖模块】
#   LWP::UserAgent - Perl 常用 HTTP 客户端模块
#   安装方法：cpanm LWP  或  apt install libwww-perl
#
#   如果没有 LWP 模块，本工具会自动降级使用 IO::Socket 手动
#   发送 HTTP 请求（仅支持 HTTP，不支持 HTTPS）。
#
# 【内置字典说明】
#   内置了常见的后台、备份、配置、敏感文件路径约 80 个，
#   适用于快速检测。实际使用建议加载更大的字典文件。
#
# 【免责声明】
#   本工具仅供学习和授权测试使用，未经授权对他人网站进行
#   目录爆破属于违法行为。使用本工具请遵守当地法律法规。
# ============================================================

use strict;
use warnings;
use POSIX ":sys_wait_h";  # 进程等待
use Time::HiRes qw(time); # 高精度时间

# ============================================================
# 尝试加载 LWP::UserAgent，如果失败则使用手动 HTTP 实现
# ============================================================
my $USE_LWP = 0;
BEGIN {
    eval {
        require LWP::UserAgent;
        LWP::UserAgent->import();
        $USE_LWP = 1;
    };
    if ($@) {
        warn "[*] 未检测到 LWP::UserAgent 模块，将使用内置 HTTP 客户端（仅支持 HTTP）\n";
        warn "[*] 如需 HTTPS 支持，请安装 LWP 模块：cpanm LWP\n";
        require IO::Socket;
        IO::Socket->import();
    }
}

# ============================================================
# 内置字典：常见 Web 目录和敏感文件路径
# ============================================================
my @DEFAULT_WORDLIST = qw(
    admin admin/ administrator admin.php admin.html
    login login.php login.html admin/index.php admin/login.php
    manage manager backend system user users
    member members dashboard console controlpanel
    wp-admin wp-login.php phpmyadmin pma myadmin

    backup backup.zip backup.tar backup.tar.gz backup.sql
    .git .git/config .git/HEAD .svn
    config config.php config.inc.php configuration.php
    database.sql db.sql dump.sql
    .htaccess .htpasswd robots.txt
    phpinfo.php info.php test.php

    .vscode .idea .DS_Store
    .env .env.local

    upload uploads images img css js
    data cache temp tmp logs log
    api api/v1 api/v2 rest
    docs doc files download
    forum blog news article
    search about contact faq
    install install.php setup setup.php

    index.html index.php index.asp index.jsp
    default.html default.php
    home.html home.php main.php
    README README.md CHANGELOG
    crossdomain.xml sitemap.xml
);

# ============================================================
# HTTP 响应结果结构体（用哈希表示）
# ============================================================
# {
#   status_code    - 状态码
#   redirect_url   - 重定向地址
#   content_length - 响应体长度
#   error          - 错误信息（如有）
# }

# ============================================================
# 发送 HTTP GET 请求（LWP 版本）
# ============================================================
sub http_get_lwp {
    my ($url, $timeout) = @_;

    my %result = (
        status_code    => 0,
        redirect_url   => '',
        content_length => 0,
        error          => undef,
    );

    eval {
        my $ua = LWP::UserAgent->new(
            timeout => $timeout,
            max_redirect => 0,  # 不跟随重定向
        );

        # 设置请求头，模拟浏览器
        $ua->agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        $ua->default_header('Accept' => 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8');
        $ua->default_header('Accept-Language' => 'zh-CN,zh;q=0.9,en;q=0.8');
        $ua->default_header('Connection' => 'close');

        my $response = $ua->get($url);

        $result{status_code} = $response->code;
        $result{content_length} = length($response->content);

        if ($response->is_redirect) {
            $result{redirect_url} = $response->header('Location') || '';
        }
    };

    if ($@) {
        $result{error} = $@;
    }

    return \%result;
}

# ============================================================
# 发送 HTTP GET 请求（IO::Socket 手动实现版本）
# ============================================================
sub http_get_socket {
    my ($host, $port, $path, $timeout) = @_;

    my %result = (
        status_code    => 0,
        redirect_url   => '',
        content_length => 0,
        error          => undef,
    );

    eval {
        # 创建 TCP 连接
        my $socket = IO::Socket::INET->new(
            PeerHost => $host,
            PeerPort => $port,
            Proto    => 'tcp',
            Timeout  => $timeout,
        ) or die "连接失败: $!";

        $socket->timeout($timeout);

        # 构建 HTTP 请求报文
        my $request = "GET $path HTTP/1.1\r\n";
        $request .= "Host: $host\r\n";
        $request .= "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n";
        $request .= "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n";
        $request .= "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8\r\n";
        $request .= "Connection: close\r\n";
        $request .= "\r\n";

        # 发送请求
        print $socket $request;
        $socket->flush();

        # 读取响应
        local $/;
        my $response = <$socket>;
        close($socket);

        # 解析响应
        if ($response =~ /^HTTP\/\d\.\d\s+(\d+)\s+/) {
            $result{status_code} = $1;
        }

        # 提取 Location 头
        if ($response =~ /Location:\s*(\S+)/i) {
            $result{redirect_url} = $1;
        }

        # 计算响应体长度
        if ($response =~ /\r\n\r\n(.*)/s) {
            $result{content_length} = length($1);
        }
    };

    if ($@) {
        $result{error} = $@;
    }

    return \%result;
}

# ============================================================
# 统一的 HTTP 请求接口
# ============================================================
sub http_request {
    my ($url, $timeout) = @_;

    if ($USE_LWP) {
        return http_get_lwp($url, $timeout);
    } else {
        # 手动解析 URL
        if ($url =~ /^(https?):\/\/([^\/:]+)(?::(\d+))?(\/.*)?$/) {
            my $scheme = $1;
            my $host = $2;
            my $port = $3 || ($scheme eq 'https' ? 443 : 80);
            my $path = $4 || '/';

            if ($scheme eq 'https') {
                return { status_code => 0, error => 'HTTPS requires LWP module' };
            }

            return http_get_socket($host, $port, $path, $timeout);
        } else {
            return { status_code => 0, error => 'URL parse error' };
        }
    }
}

# ============================================================
# 判断结果是否为"有效"路径
# ============================================================
sub is_valid_result {
    my ($status_code) = @_;
    return 0 unless $status_code;
    return 1 if $status_code >= 200 && $status_code <= 299;
    return 1 if $status_code >= 300 && $status_code <= 399;
    return 1 if $status_code == 401 || $status_code == 403;
    return 0;
}

# ============================================================
# 加载字典文件
# ============================================================
sub load_wordlist {
    my ($file_path) = @_;
    my @paths;

    open(my $fh, '<', $file_path) or do {
        warn "[!] 无法打开字典文件 '$file_path': $!\n";
        return ();
    };

    while (my $line = <$fh>) {
        chomp $line;
        $line =~ s/^\s+|\s+$//g;  # 去除首尾空白
        next if $line =~ /^#/;     # 跳过注释行
        next if $line eq '';       # 跳过空行
        $line =~ s/^\///;          # 去掉开头的斜杠
        push @paths, $line if $line;
    }

    close($fh);
    return @paths;
}

# ============================================================
# 目录爆破主函数（fork 多进程）
# ============================================================
sub dir_brute {
    my ($base_url, $wordlist_ref, $max_forks, $timeout) = @_;
    my @wordlist = @$wordlist_ref;
    my $total_paths = scalar(@wordlist);

    # 确保基础 URL 以 / 结尾
    $base_url .= '/' unless $base_url =~ /\/$/;

    print "\n[*] 开始目录爆破\n";
    print "[*] 目标 URL: $base_url\n";
    print "[*] 字典数量: $total_paths\n";
    print "[*] 并发进程数: $max_forks\n";
    print "[*] 超时时间: ${timeout}秒\n";
    print '=' x 60 . "\n";

    my $start_time = time();

    # 创建管道用于子进程返回结果
    pipe(my $read_pipe, my $write_pipe) or die "无法创建管道: $!";

    my @found_paths;       # 存储发现的有效路径
    my $current_idx = 0;   # 当前待分配的路径索引
    my $scanned_count = 0; # 已扫描数量
    my %children;          # 子进程表
    my $active_forks = 0;  # 活动子进程数

    # 持续分配任务直到所有路径扫描完毕
    while ($current_idx < $total_paths || $active_forks > 0) {
        # fork 新的子进程
        while ($current_idx < $total_paths && $active_forks < $max_forks) {
            my $path = $wordlist[$current_idx++];
            my $pid = fork();

            if (!defined($pid)) {
                warn "[!] fork 失败: $!";
                next;
            }

            if ($pid == 0) {
                # ============================================================
                # 子进程：发送 HTTP 请求并返回结果
                # ============================================================
                close($read_pipe);

                my $target_url = $base_url . $path;
                my $result = http_request($target_url, $timeout);

                # 格式化结果写入管道
                my $status = $result->{status_code} || 0;
                my $redirect = $result->{redirect_url} || '';
                my $length = $result->{content_length} || 0;
                my $error = $result->{error} ? '1' : '0';

                print $write_pipe "$path|$status|$length|$redirect|$error\n";
                close($write_pipe);
                exit 0;
            } else {
                $children{$pid} = 1;
                $active_forks++;
            }
        }

        # 收集结果
        if ($active_forks > 0) {
            vec(my $rin, fileno($read_pipe), 1) = 1;

            if (select($rin, undef, undef, 0.1) > 0) {
                while (my $line = <$read_pipe>) {
                    chomp($line);
                    my ($path, $status, $length, $redirect, $error) = split(/\|/, $line, 5);

                    $scanned_count++;

                    if ($status && is_valid_result($status)) {
                        push @found_paths, {
                            path           => $path,
                            status_code    => $status,
                            content_length => $length,
                            redirect_url   => $redirect,
                        };

                        if ($status >= 200 && $status <= 299) {
                            print "[+] [$status] /$path ($length bytes)\n";
                        } elsif ($status >= 300 && $status <= 399) {
                            print "[*] [$status] /$path -> $redirect\n";
                        } elsif ($status == 401 || $status == 403) {
                            print "[!] [$status] /$path (需要认证/禁止访问)\n";
                        }
                    }

                    # 打印进度
                    if ($scanned_count % 50 == 0 || $scanned_count == $total_paths) {
                        my $progress = sprintf("%.1f", $scanned_count / $total_paths * 100);
                        my $found = scalar(@found_paths);
                        print "\r[*] 扫描进度: $scanned_count/$total_paths ($progress%)  发现: $found";
                        $| = 1;
                    }
                }
            }

            # 回收子进程
            foreach my $pid (keys %children) {
                my $wait_result = waitpid($pid, WNOHANG);
                if ($wait_result == $pid) {
                    delete $children{$pid};
                    $active_forks--;
                }
            }
        }
    }

    close($read_pipe);
    close($write_pipe);

    my $end_time = time();
    my $duration = sprintf("%.2f", $end_time - $start_time);

    # ============================================================
    # 输出扫描结果汇总
    # ============================================================
    print "\n" . '=' x 60 . "\n";
    print "[*] 扫描完成！耗时: $duration 秒\n";
    print "[*] 扫描路径总数: $total_paths\n";
    print "[+] 发现有效路径: " . scalar(@found_paths) . " 个\n";

    if (@found_paths) {
        print "\n[*] 发现的路径列表:\n";
        print '-' x 50 . "\n";

        # 按状态码分组
        my %by_status;
        foreach my $entry (@found_paths) {
            push @{$by_status{$entry->{status_code}}}, $entry;
        }

        foreach my $status (sort { $a <=> $b } keys %by_status) {
            print "\n  状态码 $status:\n";
            foreach my $entry (@{$by_status{$status}}) {
                my $extra = $entry->{redirect_url} ? " -> $entry->{redirect_url}" : '';
                print "    /$entry->{path}  ($entry->{content_length} bytes)$extra\n";
            }
        }
    }

    return \@found_paths;
}

# ============================================================
# 主程序入口
# ============================================================
sub main {
    if (@ARGV < 1) {
        print "用法: perl dir_brute.pl <目标URL> [字典文件] [并发数] [超时时间]\n";
        print "示例: perl dir_brute.pl http://127.0.0.1\n";
        print "      perl dir_brute.pl http://example.com wordlist.txt 20\n";
        exit 1;
    }

    my $base_url = $ARGV[0];
    my $wordlist_file = $ARGV[1];
    my $max_forks = $ARGV[2] || 15;
    my $timeout = $ARGV[3] || 10;

    # 验证 URL 格式
    if ($base_url !~ /^https?:\/\//i) {
        print "[!] 错误：URL 必须以 http:// 或 https:// 开头\n";
        exit 1;
    }

    # 参数检查
    if ($max_forks < 1 || $max_forks > 100) {
        print "[!] 错误：并发数应在 1-100 之间\n";
        exit 1;
    }

    # 加载字典
    my @wordlist;
    if ($wordlist_file && -f $wordlist_file) {
        @wordlist = load_wordlist($wordlist_file);
        print "[*] 已从字典文件加载 " . scalar(@wordlist) . " 个路径\n";
    } else {
        if ($wordlist_file) {
            print "[!] 字典文件不存在，使用内置字典\n";
        } else {
            print "[*] 使用内置字典\n";
        }
        @wordlist = @DEFAULT_WORDLIST;
    }

    if (!@wordlist) {
        print "[!] 错误：字典为空\n";
        exit 1;
    }

    # 捕获中断信号
    $SIG{INT} = sub {
        print "\n[!] 用户中断扫描\n";
        exit 0;
    };

    # 执行目录爆破
    eval {
        dir_brute($base_url, \@wordlist, $max_forks, $timeout);
    };
    if ($@) {
        print "\n[!] 扫描出错: $@\n";
        exit 1;
    }
}

# 运行主程序
main();
