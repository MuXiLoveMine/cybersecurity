#!/usr/bin/perl
# ============================================================
# Web 日志分析工具 (Log Analyzer)
# ============================================================
#
# 【原理说明】
# 日志分析是安全运营和入侵检测的重要环节。通过分析 Web 服务器的
# 访问日志（access.log），可以发现攻击行为、异常访问模式和安全事件。
#
# 本工具支持以下分析功能：
#
# 1. 基本统计
#    - 总请求数、独立 IP 数、总字节数
#    - 状态码分布（2xx/3xx/4xx/5xx）
#    - 请求方法分布（GET/POST/...）
#
# 2. IP 分析
#    - IP 访问量排行（TOP N）
#    - 检测高频访问 IP（可能是扫描器/爬虫）
#
# 3. 路径分析
#    - 最常访问的页面/路径
#    - 404 最多的路径（可能是扫描行为）
#
# 4. 安全分析
#    - SQL 注入攻击检测（特征匹配）
#    - XSS 攻击检测（特征匹配）
#    - 目录遍历攻击检测（../ 等）
#    - 扫描器/爬虫识别
#    - 敏感路径访问检测（admin、backup 等）
#    - 错误请求分析（4xx/5xx）
#
# 【支持的日志格式】
#   标准 Apache/Nginx Combined Log Format:
#   %h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i"
#
#   示例:
#   192.168.1.1 - - [10/Jan/2024:10:00:00 +0800] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
#
# 【使用方法】
#   perl log_analyzer.pl <日志文件> [选项]
#
# 【参数说明】
#   日志文件  - 必填，access.log 日志文件路径
#
# 【选项】
#   -top N     - 显示前 N 条结果，默认 10
#   -ip IP     - 只分析指定 IP 的请求
#   -status N  - 只分析指定状态码的请求
#   -attack    - 仅显示攻击检测结果
#
# 【示例】
#   perl log_analyzer.pl access.log
#   perl log_analyzer.pl access.log -top 20
#   perl log_analyzer.pl access.log -ip 192.168.1.1
#   perl log_analyzer.pl access.log -status 404
#   perl log_analyzer.pl access.log -attack
#
# 【免责声明】
#   本工具仅供安全学习和日志分析使用，请勿用于非法用途。
#   攻击检测基于特征匹配，可能存在误报和漏报，仅供参考。
# ============================================================

use strict;
use warnings;
use Getopt::Long;   # 命令行选项解析（如不可用则手动解析）

# ============================================================
# 尝试加载 Getopt::Long，不可用则手动实现简单解析
# ============================================================
my $USE_GETOPT = 0;
BEGIN {
    eval {
        require Getopt::Long;
        Getopt::Long->import();
        $USE_GETOPT = 1;
    };
}

# ============================================================
# 攻击特征正则表达式
# ============================================================

# SQL 注入特征
my @SQLI_PATTERNS = (
    { pattern => qr/'\s*(OR|AND)\s*['"]?\d+/i,       name => "SQL 注入 (OR/AND)" },
    { pattern => qr/UNION\s+(ALL\s+)?SELECT/i,        name => "SQL 注入 (UNION SELECT)" },
    { pattern => qr/(;|--|#)\s*(DROP|INSERT|UPDATE|DELETE|ALTER)/i, name => "SQL 注入 (堆叠查询)" },
    { pattern => qr/INFORMATION_SCHEMA/i,             name => "SQL 注入 (元数据查询)" },
    { pattern => qr/LOAD_FILE\s*\(/i,                 name => "SQL 注入 (读文件)" },
    { pattern => qr/INTO\s+(OUT|DUMP)FILE/i,          name => "SQL 注入 (写文件)" },
    { pattern => qr/SLEEP\s*\(/i,                     name => "SQL 注入 (时间盲注)" },
    { pattern => qr/BENCHMARK\s*\(/i,                 name => "SQL 注入 (BENCHMARK)" },
    { pattern => qr/WAITFOR\s+DELAY/i,                name => "SQL 注入 (MSSQL 延时)" },
);

# XSS 攻击特征
my @XSS_PATTERNS = (
    { pattern => qr/<script[^>]*>/i,                  name => "XSS 攻击 (script 标签)" },
    { pattern => qr/javascript\s*:/i,                  name => "XSS 攻击 (javascript:)" },
    { pattern => qr/on(load|error|click|mouseover|focus)\s*=/i, name => "XSS 攻击 (事件处理)" },
    { pattern => qr/<iframe[^>]*>/i,                  name => "XSS 攻击 (iframe)" },
    { pattern => qr/<img[^>]*onerror/i,               name => "XSS 攻击 (img onerror)" },
    { pattern => qr/document\.cookie/i,               name => "XSS 攻击 (Cookie 窃取)" },
    { pattern => qr/eval\s*\(/i,                      name => "XSS 攻击 (eval)" },
);

# 目录遍历特征
my @TRAVERSAL_PATTERNS = (
    { pattern => qr/\.\.\//,                           name => "目录遍历 (../)" },
    { pattern => qr/\.\.\\/,                           name => "目录遍历 (..\\)" },
    { pattern => qr/%2e%2e%2f/i,                      name => "目录遍历 (URL 编码)" },
    { pattern => qr/\/etc\/passwd/,                    name => "目录遍历 (etc/passwd)" },
    { pattern => qr/\/windows\/system32/i,            name => "目录遍历 (system32)" },
    { pattern => qr/boot\.ini/i,                       name => "目录遍历 (boot.ini)" },
);

# 扫描器/爬虫 User-Agent 特征
my @SCANNER_UA_PATTERNS = (
    { pattern => qr/sqlmap/i,                          name => "SQLMap" },
    { pattern => qr/nmap/i,                            name => "Nmap" },
    { pattern => qr/nikto/i,                           name => "Nikto" },
    { pattern => qr/nessus/i,                          name => "Nessus" },
    { pattern => qr/burpsuite/i,                       name => "Burp Suite" },
    { pattern => qr/acunetix/i,                        name => "Acunetix" },
    { pattern => qr/havij/i,                           name => "Havij" },
    { pattern => qr/dirbuster/i,                       name => "DirBuster" },
    { pattern => qr/gobuster/i,                        name => "Gobuster" },
    { pattern => qr/wfuzz/i,                           name => "Wfuzz" },
    { pattern => qr/metasploit/i,                      name => "Metasploit" },
    { pattern => qr/scanner/i,                         name => "通用扫描器" },
    { pattern => qr/crawler/i,                         name => "爬虫工具" },
    { pattern => qr/spider/i,                          name => "爬虫工具" },
    { pattern => qr/python-requests/i,                 name => "Python requests" },
    { pattern => qr/curl/i,                            name => "curl" },
);

# 敏感路径
my @SENSITIVE_PATHS = (
    { pattern => qr/\/admin/i,                         name => "后台管理" },
    { pattern => qr/\/phpmyadmin/i,                    name => "phpMyAdmin" },
    { pattern => qr/\/wp-admin/i,                      name => "WordPress 后台" },
    { pattern => qr/\/backup/i,                        name => "备份文件" },
    { pattern => qr/\/\.git/i,                         name => "Git 仓库" },
    { pattern => qr/\/\.svn/i,                         name => "SVN 仓库" },
    { pattern => qr/\/config/i,                        name => "配置文件" },
    { pattern => qr/\/install/i,                       name => "安装脚本" },
    { pattern => qr/\/phpinfo/i,                       name => "phpinfo" },
    { pattern => qr/\/shell/i,                         name => "WebShell" },
);

# ============================================================
# 解析日志行
# ============================================================
# 解析 Apache/Nginx Combined 格式的日志行
# 返回包含各字段的哈希引用
sub parse_log_line {
    my ($line) = @_;
    chomp $line;

    # 标准 Combined Log Format 正则
    # 格式: IP - - [时间] "请求方法 路径 协议" 状态码 字节数 "Referer" "User-Agent"
    if ($line =~ /^(\S+)\s+\S+\s+\S+\s+\[([^\]]+)\]\s+"(\S+)\s+(\S+)\s+(\S+)"\s+(\d+)\s+(\d+|"-")\s+"([^"]*)"\s+"([^"]*)"/) {
        return {
            ip        => $1,         # 客户端 IP
            time      => $2,         # 请求时间
            method    => $3,         # 请求方法
            path      => $4,         # 请求路径
            protocol  => $5,         # 协议版本
            status    => int($6),    # 状态码
            bytes     => ($7 eq '-' || $7 eq '"-"') ? 0 : int($7),  # 响应字节数
            referer   => $8,         # Referer
            user_agent => $9,        # User-Agent
        };
    }

    # Common Log Format（不带 Referer 和 UA）
    if ($line =~ /^(\S+)\s+\S+\s+\S+\s+\[([^\]]+)\]\s+"(\S+)\s+(\S+)\s+(\S+)"\s+(\d+)\s+(\d+|"-")/) {
        return {
            ip        => $1,
            time      => $2,
            method    => $3,
            path      => $4,
            protocol  => $5,
            status    => int($6),
            bytes     => ($7 eq '-' || $7 eq '"-"') ? 0 : int($7),
            referer   => '',
            user_agent => '',
        };
    }

    return undef;  # 解析失败
}

# ============================================================
# 检测攻击特征
# ============================================================
sub detect_attacks {
    my ($log_entry) = @_;
    my @attacks;

    my $path = $log_entry->{path};
    my $ua = $log_entry->{user_agent};

    # 检测 SQL 注入
    foreach my $p (@SQLI_PATTERNS) {
        if ($path =~ $p->{pattern}) {
            push @attacks, { type => 'SQL注入', name => $p->{name} };
            last;  # 每种攻击类型只记一次
        }
    }

    # 检测 XSS
    foreach my $p (@XSS_PATTERNS) {
        if ($path =~ $p->{pattern}) {
            push @attacks, { type => 'XSS', name => $p->{name} };
            last;
        }
    }

    # 检测目录遍历
    foreach my $p (@TRAVERSAL_PATTERNS) {
        if ($path =~ $p->{pattern}) {
            push @attacks, { type => '目录遍历', name => $p->{name} };
            last;
        }
    }

    # 检测扫描器
    foreach my $p (@SCANNER_UA_PATTERNS) {
        if ($ua =~ $p->{pattern}) {
            push @attacks, { type => '扫描器', name => $p->{name} };
            last;
        }
    }

    # 检测敏感路径访问
    foreach my $p (@SENSITIVE_PATHS) {
        if ($path =~ $p->{pattern}) {
            push @attacks, { type => '敏感路径', name => $p->{name} };
            last;
        }
    }

    return @attacks;
}

# ============================================================
# 日志分析主函数
# ============================================================
sub analyze_log {
    my ($file, $top_n, $filter_ip, $filter_status, $attack_only) = @_;

    # 统计变量
    my $total_requests = 0;       # 总请求数
    my $total_bytes = 0;          # 总字节数
    my %ip_count;                 # IP 计数
    my %status_count;             # 状态码计数
    my %method_count;             # 请求方法计数
    my %path_count;               # 路径计数
    my %path_404_count;           # 404 路径计数
    my %attack_count;             # 攻击计数
    my %ip_attacks;               # IP 攻击记录
    my $parsed_lines = 0;         # 成功解析的行数
    my $failed_lines = 0;         # 解析失败的行数

    print "\n[*] 正在分析日志文件: $file\n";
    print '=' x 60 . "\n";

    # 打开日志文件
    open(my $fh, '<', $file) or die "[!] 无法打开文件 '$file': $!\n";

    while (my $line = <$fh>) {
        next if $line =~ /^\s*$/;  # 跳过空行

        # 解析日志行
        my $entry = parse_log_line($line);
        if (!$entry) {
            $failed_lines++;
            next;
        }
        $parsed_lines++;

        # 过滤器
        next if $filter_ip && $entry->{ip} ne $filter_ip;
        next if $filter_status && $entry->{status} != $filter_status;

        # 基本统计
        $total_requests++;
        $total_bytes += $entry->{bytes};
        $ip_count{$entry->{ip}}++;
        $status_count{$entry->{status}}++;
        $method_count{$entry->{method}}++;
        $path_count{$entry->{path}}++;

        # 404 路径统计
        if ($entry->{status} == 404) {
            $path_404_count{$entry->{path}}++;
        }

        # 攻击检测
        my @attacks = detect_attacks($entry);
        if (@attacks) {
            foreach my $attack (@attacks) {
                my $key = "$attack->{type}: $attack->{name}";
                $attack_count{$key}++;
                $ip_attacks{$entry->{ip}}->{$key}++;
            }
        }
    }

    close($fh);

    # ============================================================
    # 输出分析结果
    # ============================================================

    unless ($attack_only) {
        # ---- 基本统计 ----
        print "\n" . '=' x 60 . "\n";
        print "[*] 基本统计\n";
        print '=' x 60 . "\n";
        print "  总请求数:       $total_requests\n";
        print "  独立 IP 数:     " . scalar(keys %ip_count) . "\n";
        print "  总流量:         " . format_bytes($total_bytes) . "\n";
        print "  解析成功行数:   $parsed_lines\n";
        print "  解析失败行数:   $failed_lines\n" if $failed_lines > 0;

        # ---- 状态码分布 ----
        print "\n[*] 状态码分布:\n";
        my ($c2xx, $c3xx, $c4xx, $c5xx) = (0, 0, 0, 0);
        foreach my $status (sort { $a <=> $b } keys %status_count) {
            my $count = $status_count{$status};
            my $pct = sprintf("%.1f", $count / $total_requests * 100);
            print "  $status: $count ($pct%)\n";
            $c2xx++ if $status >= 200 && $status < 300;
            $c3xx++ if $status >= 300 && $status < 400;
            $c4xx++ if $status >= 400 && $status < 500;
            $c5xx++ if $status >= 500 && $status < 600;
        }

        # ---- 请求方法分布 ----
        print "\n[*] 请求方法分布:\n";
        foreach my $method (sort { $method_count{$b} <=> $method_count{$a} } keys %method_count) {
            my $count = $method_count{$method};
            my $pct = sprintf("%.1f", $count / $total_requests * 100);
            print "  $method: $count ($pct%)\n";
        }

        # ---- IP 排行 ----
        print "\n[*] IP 访问量 TOP $top_n:\n";
        print '-' x 40 . "\n";
        my @top_ips = sort { $ip_count{$b} <=> $ip_count{$a} } keys %ip_count;
        @top_ips = splice(@top_ips, 0, $top_n);
        my $rank = 1;
        foreach my $ip (@top_ips) {
            my $pct = sprintf("%.1f", $ip_count{$ip} / $total_requests * 100);
            printf("  %2d. %-20s %6d 次 (%s%%)\n", $rank++, $ip, $ip_count{$ip}, $pct);
        }

        # ---- 最常访问路径 ----
        print "\n[*] 最常访问路径 TOP $top_n:\n";
        print '-' x 40 . "\n";
        my @top_paths = sort { $path_count{$b} <=> $path_count{$a} } keys %path_count;
        @top_paths = splice(@top_paths, 0, $top_n);
        $rank = 1;
        foreach my $path (@top_paths) {
            printf("  %2d. %-50s %d 次\n", $rank++, substr($path, 0, 50), $path_count{$path});
        }

        # ---- 404 最多路径 ----
        if (%path_404_count) {
            print "\n[*] 404 最多路径 TOP $top_n:\n";
            print '-' x 40 . "\n";
            my @top_404 = sort { $path_404_count{$b} <=> $path_404_count{$a} } keys %path_404_count;
            @top_404 = splice(@top_404, 0, $top_n);
            $rank = 1;
            foreach my $path (@top_404) {
                printf("  %2d. %-50s %d 次\n", $rank++, substr($path, 0, 50), $path_404_count{$path});
            }
        }
    }

    # ---- 安全分析 ----
    print "\n" . '=' x 60 . "\n";
    print "[*] 安全分析 - 攻击检测\n";
    print '=' x 60 . "\n";

    if (%attack_count) {
        my $total_attacks = 0;
        $total_attacks += $_ for values %attack_count;

        print "\n[!] 检测到 $total_attacks 个可疑请求\n\n";
        print "[攻击类型统计]\n";
        print '-' x 40 . "\n";

        foreach my $attack (sort { $attack_count{$b} <=> $attack_count{$a} } keys %attack_count) {
            printf("  %-40s %d 次\n", $attack, $attack_count{$attack});
        }

        # 攻击性最强的 IP
        print "\n[攻击性 IP TOP $top_n]\n";
        print '-' x 40 . "\n";
        my %ip_attack_total;
        foreach my $ip (keys %ip_attacks) {
            my $total = 0;
            $total += $_ for values %{$ip_attacks{$ip}};
            $ip_attack_total{$ip} = $total;
        }

        my @bad_ips = sort { $ip_attack_total{$b} <=> $ip_attack_total{$a} } keys %ip_attack_total;
        @bad_ips = splice(@bad_ips, 0, $top_n);
        $rank = 1;
        foreach my $ip (@bad_ips) {
            printf("  %2d. %-20s %3d 次攻击\n", $rank++, $ip, $ip_attack_total{$ip});
            # 显示该 IP 的攻击类型
            my @types = sort keys %{$ip_attacks{$ip}};
            print "      类型: " . join(', ', @types) . "\n";
        }
    } else {
        print "\n[-] 未检测到明显的攻击特征\n";
        print "    注意：本工具基于特征匹配，可能存在漏报\n";
    }

    print "\n" . '=' x 60 . "\n";
    print "[*] 分析完成\n";
    print '=' x 60 . "\n";
}

# ============================================================
# 格式化字节数为人类可读格式
# ============================================================
sub format_bytes {
    my ($bytes) = @_;
    return '0 B' if $bytes == 0;

    my @units = ('B', 'KB', 'MB', 'GB', 'TB');
    my $unit_idx = 0;
    my $size = $bytes;

    while ($size >= 1024 && $unit_idx < $#units) {
        $size /= 1024;
        $unit_idx++;
    }

    return sprintf("%.2f %s", $size, $units[$unit_idx]);
}

# ============================================================
# 主程序入口
# ============================================================
sub main {
    my $top_n = 10;
    my $filter_ip = '';
    my $filter_status = 0;
    my $attack_only = 0;

    if ($USE_GETOPT) {
        GetOptions(
            'top=i'    => \$top_n,
            'ip=s'     => \$filter_ip,
            'status=i' => \$filter_status,
            'attack'   => \$attack_only,
        ) or die "参数解析错误\n";
    } else {
        # 手动解析参数
        my @args = @ARGV;
        my $file = shift @args;
        unshift @ARGV, $file if $file;

        for (my $i = 0; $i < @args; $i++) {
            if ($args[$i] eq '-top' && $i + 1 < @args) {
                $top_n = $args[++$i];
            } elsif ($args[$i] eq '-ip' && $i + 1 < @args) {
                $filter_ip = $args[++$i];
            } elsif ($args[$i] eq '-status' && $i + 1 < @args) {
                $filter_status = $args[++$i];
            } elsif ($args[$i] eq '-attack') {
                $attack_only = 1;
            }
        }
    }

    my $log_file = shift @ARGV;

    unless ($log_file) {
        print "用法: perl log_analyzer.pl <日志文件> [选项]\n";
        print "\n选项:\n";
        print "  -top N       显示前 N 条结果（默认 10）\n";
        print "  -ip IP       只分析指定 IP 的请求\n";
        print "  -status N    只分析指定状态码的请求\n";
        print "  -attack      仅显示攻击检测结果\n";
        print "\n示例:\n";
        print "  perl log_analyzer.pl access.log\n";
        print "  perl log_analyzer.pl access.log -top 20 -attack\n";
        exit 1;
    }

    unless (-f $log_file) {
        print "[!] 错误：文件 '$log_file' 不存在\n";
        exit 1;
    }

    eval {
        analyze_log($log_file, $top_n, $filter_ip, $filter_status, $attack_only);
    };
    if ($@) {
        print "\n[!] 分析出错: $@\n";
        exit 1;
    }
}

# 运行主程序
main();
