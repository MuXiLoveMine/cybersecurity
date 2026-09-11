#!/usr/bin/perl
# ============================================================
# SQL 注入检测工具 (SQL Injection Scanner)
# ============================================================
#
# 【原理说明】
# SQL 注入是最常见的 Web 安全漏洞之一，攻击者通过在输入参数中
# 插入恶意 SQL 代码，使应用执行非预期的数据库操作。
#
# 本工具实现了两种常见的 SQL 注入检测技术：
#
# 1. 布尔盲注 (Boolean-based Blind SQLi)
#    - 原理：构造使 SQL 查询结果为真/假的 payload
#    - 通过比较页面内容变化判断注入是否存在
#    - 例如：在参数后加 ' AND '1'='1 和 ' AND '1'='2
#    - 如果前者页面正常，后者页面异常，则存在注入
#
# 2. 报错注入 (Error-based SQLi)
#    - 原理：构造导致数据库报错的 payload
#    - 通过检测响应中的数据库错误信息判断
#    - 例如：单引号 ' 可能触发 SQL 语法错误
#    - 错误信息中常包含 SQL 语法、表名、列名等信息
#
# 此外，本工具还使用正则匹配检测常见的 SQL 注入特征。
#
# 【使用方法】
#   perl sqli_scanner.pl <目标URL> [参数名]
#
# 【参数说明】
#   目标URL  - 必填，带参数的完整 URL，例如 http://example.com/page?id=1
#              如果 URL 中有多个参数，会逐一检测每个参数
#   参数名   - 可选，只检测指定的参数名
#
# 【示例】
#   perl sqli_scanner.pl "http://127.0.0.1/page?id=1"
#   perl sqli_scanner.pl "http://example.com/search?q=test&cat=1" id
#
# 【依赖模块】
#   LWP::UserAgent - HTTP 客户端（可选，无则使用内置实现）
#
# 【免责声明】
#   本工具仅供学习和授权测试使用，未经授权检测他人网站属于违法行为。
#   使用本工具请遵守当地法律法规，违者后果自负。
# ============================================================

use strict;
use warnings;
use URI::Escape;  # URL 编码/解码（如不可用会手动实现）

# ============================================================
# 检查 URI::Escape 是否可用，不可用则手动实现
# ============================================================
BEGIN {
    eval {
        require URI::Escape;
        URI::Escape->import('uri_escape', 'uri_unescape');
    };
    if ($@) {
        # 手动实现简单的 URL 编码/解码
        *uri_escape = sub {
            my ($str) = @_;
            $str =~ s/([^A-Za-z0-9\-_.~])/sprintf("%%%02X", ord($1))/ge;
            return $str;
        };
        *uri_unescape = sub {
            my ($str) = @_;
            $str =~ s/%([0-9A-Fa-f]{2})/chr(hex($1))/ge;
            return $str;
        };
    }
}

# ============================================================
# 尝试加载 LWP::UserAgent
# ============================================================
my $USE_LWP = 0;
BEGIN {
    eval {
        require LWP::UserAgent;
        LWP::UserAgent->import();
        $USE_LWP = 1;
    };
    if ($@) {
        require IO::Socket;
        IO::Socket->import();
    }
}

# ============================================================
# SQL 注入 Payload 定义
# ============================================================

# 布尔盲注 payload 对：一个为真（True），一个为假（False）
my @BOOLEAN_PAYLOADS = (
    # 单引号闭合的情况
    { true => "' AND '1'='1",   false => "' AND '1'='2",   desc => "单引号字符型" },
    # 双引号闭合的情况
    { true => '" AND "1"="1',   false => '" AND "1"="2',   desc => "双引号字符型" },
    # 数字型注入（无需闭合）
    { true => " AND 1=1",       false => " AND 1=2",       desc => "数字型" },
    # 单引号+注释闭合
    { true => "' AND 1=1-- ",   false => "' AND 1=2-- ",   desc => "单引号+注释" },
    # 双引号+注释闭合
    { true => '" AND 1=1-- ',   false => '" AND 1=2-- ',   desc => "双引号+注释" },
    # 括号闭合的情况
    { true => "') AND ('1'='1", false => "') AND ('1'='2", desc => "单引号+括号" },
);

# 报错注入 payload（触发数据库错误）
my @ERROR_PAYLOADS = (
    { payload => "'",          desc => "单引号" },
    { payload => '"',          desc => "双引号" },
    { payload => "')",         desc => "单引号+括号" },
    { payload => '")',         desc => "双引号+括号" },
    { payload => "' OR 1=1-- ", desc => "OR 注入" },
);

# 数据库错误关键字（用于正则匹配报错信息）
my @ERROR_KEYWORDS = (
    # MySQL 错误
    'MySQL syntax', 'mysql_fetch', 'mysql_error', 'MySQL server',
    'You have an error in your SQL syntax',
    'Warning: mysql_', 'Warning: mysqli_',
    # MSSQL 错误
    'Microsoft SQL Server', 'SQL Server', 'Unclosed quotation mark',
    'System\.Data\.SqlClient', 'SQLException',
    # PostgreSQL 错误
    'PostgreSQL', 'pg_query', 'pg_exec', 'syntax error at or near',
    # Oracle 错误
    'ORA-', 'Oracle error', 'Oracle Database',
    # SQLite 错误
    'SQLite/JDBCDriver', 'SQLite3::', 'sqlite_',
    # 通用 SQL 错误
    'SQL syntax', 'sql error', 'syntax error', 'unclosed quotation',
    'quoted string not properly terminated',
);

# ============================================================
# SQL 注入特征正则（用于检测 URL/参数中的注入迹象）
# ============================================================
my @SQLI_PATTERNS = (
    qr/'\s*(OR|AND)\s*['"]?\d+['"]?\s*=\s*['"]?\d+/i,      # ' OR 1=1 类型
    qr/UNION\s+(ALL\s+)?SELECT/i,                           # UNION SELECT 注入
    qr/(;|--|#)\s*(DROP|INSERT|UPDATE|DELETE|ALTER)/i,      # 堆叠查询
    qr/(OR|AND)\s+1\s*=\s*1/i,                              # 恒真条件
    qr/'\s*OR\s+''\s*=\s*'/i,                               # 单引号绕过
    qr/WAITFOR\s+DELAY/i,                                   # MSSQL 时间盲注
    qr/SLEEP\s*\(/i,                                        # MySQL 时间盲注
    qr/BENCHMARK\s*\(/i,                                    # MySQL BENCHMARK
    qr/PG_SLEEP\s*\(/i,                                     # PostgreSQL 时间盲注
    qr/INFORMATION_SCHEMA/i,                                # 元数据查询
    qr/LOAD_FILE\s*\(/i,                                    # MySQL 读文件
    qr/INTO\s+(OUT|DUMP)FILE/i,                             # MySQL 写文件
);

# ============================================================
# HTTP 请求函数
# ============================================================
sub http_request {
    my ($url, $timeout) = @_;
    $timeout ||= 15;

    my %result = (
        status_code    => 0,
        body           => '',
        response_time  => 0,
        content_length => 0,
        error          => undef,
    );

    my $start_time = time();

    if ($USE_LWP) {
        eval {
            my $ua = LWP::UserAgent->new(
                timeout => $timeout,
                max_redirect => 0,
            );
            $ua->agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
            $ua->default_header('Accept' => 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8');
            $ua->default_header('Accept-Language' => 'zh-CN,zh;q=0.9,en;q=0.8');

            my $response = $ua->get($url);
            $result{status_code} = $response->code;
            my $body = $response->content;
            # 限制最大 50KB
            if (length($body) > 51200) {
                $body = substr($body, 0, 51200);
            }
            $result{body} = $body;
            $result{content_length} = length($body);
        };
        if ($@) {
            $result{error} = $@;
        }
    } else {
        # 使用 IO::Socket 手动实现
        if ($url =~ /^http:\/\/([^\/:]+)(?::(\d+))?(\/.*)?$/) {
            my $host = $1;
            my $port = $2 || 80;
            my $path = $3 || '/';

            eval {
                my $socket = IO::Socket::INET->new(
                    PeerHost => $host,
                    PeerPort => $port,
                    Proto    => 'tcp',
                    Timeout  => $timeout,
                ) or die "连接失败: $!";

                $socket->timeout($timeout);

                my $request = "GET $path HTTP/1.1\r\n";
                $request .= "Host: $host\r\n";
                $request .= "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n";
                $request .= "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n";
                $request .= "Connection: close\r\n\r\n";

                print $socket $request;
                $socket->flush();

                local $/;
                my $response = <$socket>;
                close($socket);

                if ($response =~ /^HTTP\/\d\.\d\s+(\d+)\s+/) {
                    $result{status_code} = $1;
                }

                if ($response =~ /\r\n\r\n(.*)/s) {
                    my $body = $1;
                    if (length($body) > 51200) {
                        $body = substr($body, 0, 51200);
                    }
                    $result{body} = $body;
                    $result{content_length} = length($body);
                }
            };
            if ($@) {
                $result{error} = $@;
            }
        } else {
            $result{error} = 'URL parse error';
        }
    }

    $result{response_time} = int((time() - $start_time) * 1000);
    return \%result;
}

# ============================================================
# 解析 URL 参数
# ============================================================
sub parse_url_params {
    my ($url_str) = @_;

    my ($base_url, $query_string);
    if ($url_str =~ /^([^?]+)\?(.*)$/) {
        $base_url = $1;
        $query_string = $2;
    } else {
        $base_url = $url_str;
        $query_string = '';
    }

    my %params;
    if ($query_string) {
        my @pairs = split(/&/, $query_string);
        foreach my $pair (@pairs) {
            my ($key, $value) = split(/=/, $pair, 2);
            $key = uri_unescape($key) if defined $key;
            $value = uri_unescape($value) if defined $value;
            $params{$key} = $value || '';
        }
    }

    return { base_url => $base_url, params => \%params };
}

# ============================================================
# 构造带注入 payload 的 URL
# ============================================================
sub build_test_url {
    my ($base_url, $params_ref, $target_param, $payload) = @_;
    my %params = %$params_ref;

    # 修改目标参数的值（追加 payload）
    $params{$target_param} = ($params{$target_param} || '') . $payload;

    # 构建查询字符串
    my @pairs;
    foreach my $key (keys %params) {
        push @pairs, uri_escape($key) . '=' . uri_escape($params{$key});
    }

    return $base_url . '?' . join('&', @pairs);
}

# ============================================================
# 1. 报错注入检测
# ============================================================
sub test_error_based {
    my ($base_url, $params_ref, $param_name) = @_;

    foreach my $payload_info (@ERROR_PAYLOADS) {
        eval {
            my $test_url = build_test_url($base_url, $params_ref, $param_name, $payload_info->{payload});
            my $result = http_request($test_url);

            my $body = lc($result->{body});

            # 检查响应中是否包含数据库错误关键字
            foreach my $keyword (@ERROR_KEYWORDS) {
                if ($body =~ /\Q$keyword\E/i) {
                    return {
                        vulnerable => 1,
                        details => "报错注入 ($payload_info->{desc})\n" .
                                   "      错误关键字: $keyword\n" .
                                   "      Payload: $payload_info->{payload}\n" .
                                   "      状态码: $result->{status_code}",
                    };
                }
            }
        };
        if ($@) {
            next;
        }
    }

    return { vulnerable => 0, details => '' };
}

# ============================================================
# 2. 布尔盲注检测
# ============================================================
sub test_boolean_blind {
    my ($base_url, $params_ref, $param_name) = @_;

    # 先获取原始页面作为基准
    my $base_test_url = build_test_url($base_url, $params_ref, $param_name, '');
    my $base_result = http_request($base_test_url);
    my $base_length = $base_result->{content_length};

    print "    [*] 基准页面长度: $base_length 字节\n";

    # 逐一测试各组布尔 payload
    foreach my $payload_info (@BOOLEAN_PAYLOADS) {
        eval {
            # 构造真/假两个测试 URL
            my $true_url = build_test_url($base_url, $params_ref, $param_name, $payload_info->{true});
            my $false_url = build_test_url($base_url, $params_ref, $param_name, $payload_info->{false});

            # 发起两次请求
            my $true_result = http_request($true_url);
            my $false_result = http_request($false_url);

            my $true_len = $true_result->{content_length};
            my $false_len = $false_result->{content_length};

            # 计算页面长度差异比例
            my $diff_ratio = abs($true_len - $false_len) / ($base_length > 0 ? $base_length : 1);

            # 判断条件
            my $true_diff_base = abs($true_len - $base_length) / ($base_length > 0 ? $base_length : 1);
            my $false_diff_base = abs($false_len - $base_length) / ($base_length > 0 ? $base_length : 1);

            if ($diff_ratio > 0.2 && ($false_diff_base > $true_diff_base * 1.5 || $false_diff_base > 0.3)) {
                return {
                    vulnerable => 1,
                    details => "布尔盲注 ($payload_info->{desc})\n" .
                               "      基准长度: $base_length\n" .
                               "      真值长度: $true_len (差异: " . sprintf("%.1f", $true_diff_base * 100) . "%)\n" .
                               "      假值长度: $false_len (差异: " . sprintf("%.1f", $false_diff_base * 100) . "%)\n" .
                               "      Payload: $payload_info->{true} / $payload_info->{false}",
                };
            }
        };
        if ($@) {
            next;
        }
    }

    return { vulnerable => 0, details => '' };
}

# ============================================================
# 3. 正则匹配检测（快速扫描注入特征）
# ============================================================
sub test_pattern_match {
    my ($url) = @_;

    my @found;
    foreach my $pattern (@SQLI_PATTERNS) {
        if ($url =~ $pattern) {
            push @found, $pattern;
        }
    }

    return @found;
}

# ============================================================
# SQL 注入扫描主函数
# ============================================================
sub scan_sql_injection {
    my ($url_str, $target_param) = @_;

    my $parsed = parse_url_params($url_str);
    my $base_url = $parsed->{base_url};
    my $params_ref = $parsed->{params};
    my %params = %$params_ref;
    my @param_names = keys %params;

    if (!@param_names) {
        print "[!] 未发现 GET 参数，请提供带参数的 URL\n";
        return;
    }

    print "\n" . '=' x 60 . "\n";
    print "[*] SQL 注入检测工具 (Perl 版)\n";
    print '=' x 60 . "\n";
    print "[*] 目标 URL: $url_str\n";
    print "[*] 发现参数: " . join(', ', @param_names) . "\n";
    print "[*] 检测类型: 报错注入 / 布尔盲注 / 正则特征匹配\n";
    print '=' x 60 . "\n";

    my @found_vulns;

    # 逐一检测每个参数
    foreach my $param_name (@param_names) {
        next if $target_param && $param_name ne $target_param;

        print "\n[*] 正在检测参数: $param_name (值: $params{$param_name})\n";

        # 1. 报错注入检测（最快，先测）
        print "    [-] 检测报错注入...\n";
        my $error_result = test_error_based($base_url, \%params, $param_name);
        if ($error_result->{vulnerable}) {
            print "    [!] 发现报错注入！\n";
            push @found_vulns, { param => $param_name, type => '报错注入', details => $error_result->{details} };
        } else {
            print "    [-] 未发现报错注入\n";
        }

        # 2. 布尔盲注检测
        print "    [-] 检测布尔盲注...\n";
        my $boolean_result = test_boolean_blind($base_url, \%params, $param_name);
        if ($boolean_result->{vulnerable}) {
            print "    [!] 发现布尔盲注！\n";
            push @found_vulns, { param => $param_name, type => '布尔盲注', details => $boolean_result->{details} };
        } else {
            print "    [-] 未发现布尔盲注\n";
        }
    }

    # ============================================================
    # 输出检测结果汇总
    # ============================================================
    print "\n" . '=' x 60 . "\n";
    print "[*] 检测完成！\n";
    print '=' x 60 . "\n";

    if (@found_vulns) {
        print "\n[!] 发现 " . scalar(@found_vulns) . " 个 SQL 注入漏洞：\n";
        print '-' x 50 . "\n";
        my $index = 1;
        foreach my $vuln (@found_vulns) {
            print "\n  [$index] 参数: $vuln->{param}\n";
            print "      类型: $vuln->{type}\n";
            print "      详情: $vuln->{details}\n";
            $index++;
        }
        print "\n[!] 风险等级: 高危\n";
        print "[!] 修复建议: 使用参数化查询/预编译语句，对用户输入进行严格过滤\n";
    } else {
        print "\n[-] 未检测到 SQL 注入漏洞\n";
        print "    注意：本工具仅基于简单特征检测，不代表绝对安全\n";
        print "    建议结合手工测试和专业扫描器进行深入检测\n";
    }

    return \@found_vulns;
}

# ============================================================
# 主程序入口
# ============================================================
sub main {
    if (@ARGV < 1) {
        print "用法: perl sqli_scanner.pl <目标URL> [参数名]\n";
        print "示例: perl sqli_scanner.pl \"http://127.0.0.1/page?id=1\"\n";
        print "      perl sqli_scanner.pl \"http://example.com/search?q=test\" q\n";
        exit 1;
    }

    my $target_url = $ARGV[0];
    my $target_param = $ARGV[1];

    # 验证 URL 格式
    if ($target_url !~ /^https?:\/\//i) {
        print "[!] 错误：URL 格式无效，请包含 http:// 或 https://\n";
        exit 1;
    }

    # 捕获中断信号
    $SIG{INT} = sub {
        print "\n[!] 用户中断检测\n";
        exit 0;
    };

    # 执行扫描
    eval {
        scan_sql_injection($target_url, $target_param);
    };
    if ($@) {
        print "\n[!] 扫描出错: $@\n";
        exit 1;
    }
}

# 运行主程序
main();
