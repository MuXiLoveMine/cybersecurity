---

## 四、高级实战案例

### 4.1 高级正则表达式与文本分析

Perl 强大的正则表达式在安全分析中的应用。

```perl
#!/usr/bin/perl
use strict;
use warnings;
use v5.16;

# ===== 日志分析器 =====
package LogAnalyzer;

sub new {
    my ($class, %opts) = @_;
    bless {
        log_file => $opts{log_file},
        patterns => {},
        stats => {},
    }, $class;
}

# 加载常见攻击特征
sub load_attack_patterns {
    my ($self) = @_;
    
    $self->{patterns} = {
        # SQL 注入
        sqli => [
            qr/'\s*OR\s*'?\d+'?\s*=\s*'?\d+/i,
            qr/UNION\s+SELECT/i,
            qr/SELECT\s+.*\s+FROM\s+/i,
            qr/INSERT\s+INTO/i,
            qr/DROP\s+TABLE/i,
            qr/--\s*$/,
            qr/\b(AND|OR)\s+\d+\s*=\s*\d+/i,
            qr/SLEEP\s*\(/i,
            qr/BENCHMARK\s*\(/i,
        ],
        # XSS
        xss => [
            qr/<script[^>]*>/i,
            qr/javascript\s*:/i,
            qr/on\w+\s*=/i,
            qr/eval\s*\(/i,
            qr/document\.cookie/i,
            qr/<img[^>]+onerror/i,
            qr/<svg[^>]+onload/i,
        ],
        # 目录遍历
        path_traversal => [
            qr/\.\.\//,
            qr/\.\.\\/,
            qr/%2e%2e%2f/i,
            qr/\.%2e\//i,
            qr/etc\/passwd/i,
            qr/windows\\win\.ini/i,
        ],
        # 命令注入
        command_injection => [
            qr/[;&|`]\s*(cat|ls|id|whoami|uname|cmd|powershell)/i,
            qr/\|\s*\|/,          # ||
            qr/;\s*rm\s+/,
            qr/`[^`]+`/,
            qr/\$\([^)]+\)/,
        ],
        # 文件包含
        file_include => [
            qr/(include|require|fopen|readfile|file_get_contents)\s*[\(\[][^)]*https?:/i,
            qr/php:\/\/input/i,
            qr/data:\/\/text\/html/i,
            qr/expect:\/\//i,
        ],
        # SSRF
        ssrf => [
            qr/file:\/\/\//i,
            qr/169\.254\.169\.254/,  # AWS metadata
            qr/metadata\.google\.internal/i,
            qr/127\.0\.0\.1.*http/,
            qr/localhost.*http/,
        ],
    };
}

# 分析单行日志
sub analyze_line {
    my ($self, $line) = @_;
    my @findings;
    
    foreach my $attack_type (keys %{$self->{patterns}}) {
        foreach my $pattern (@{$self->{patterns}{$attack_type}}) {
            if ($line =~ $pattern) {
                push @findings, {
                    type => $attack_type,
                    pattern => "$pattern",
                    match => substr($&, 0, 50),
                };
            }
        }
    }
    
    return @findings;
}

# 分析整个日志文件
sub analyze_file {
    my ($self) = @_;
    
    open(my $fh, '<', $self->{log_file}) or die "无法打开日志文件: $!";
    
    my $total = 0;
    my $attacks = 0;
    my %attack_counts;
    my %ip_counts;
    
    while (my $line = <$fh>) {
        $total++;
        my @findings = $self->analyze_line($line);
        
        if (@findings) {
            $attacks++;
            # 提取 IP (通用模式)
            if ($line =~ /(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/) {
                $ip_counts{$1}++;
            }
            
            foreach my $f (@findings) {
                $attack_counts{$f->{type}}++;
            }
        }
    }
    
    close($fh);
    
    $self->{stats} = {
        total_lines => $total,
        attack_lines => $attacks,
        attack_types => \%attack_counts,
        top_ips => [sort { $ip_counts{$b} <=> $ip_counts{$a} } keys %ip_counts][0..9],
        ip_counts => \%ip_counts,
    };
    
    return $self->{stats};
}

# 生成报告
sub generate_report {
    my ($self, $output_file) = @_;
    my $stats = $self->{stats};
    
    open(my $out, '>', $output_file) or die $!;
    
    print $out "=" x 60 . "\n";
    print $out "  Web 日志安全分析报告\n";
    print $out "=" x 60 . "\n\n";
    
    print $out "【统计概览】\n";
    print $out "  总行数: $stats->{total_lines}\n";
    print $out "  攻击尝试: $stats->{attack_lines}\n";
    printf $out "  攻击占比: %.2f%%\n\n", ($stats->{attack_lines} / $stats->{total_lines} * 100);
    
    print $out "【攻击类型分布】\n";
    foreach my $type (sort { $stats->{attack_types}{$b} <=> $stats->{attack_types}{$a} } 
                     keys %{$stats->{attack_types}}) {
        printf $out "  %-20s %d 次\n", $type, $stats->{attack_types}{$type};
    }
    print $out "\n";
    
    print $out "【Top 10 攻击源 IP】\n";
    my $count = 1;
    foreach my $ip (@{$stats->{top_ips}}) {
        printf $out "  %2d. %-15s %d 次\n", $count, $ip, $stats->{ip_counts}{$ip};
        $count++;
    }
    
    close($out);
    print "报告已生成: $output_file\n";
}

1;

# ===== 使用示例 =====
package main;

my $analyzer = LogAnalyzer->new(log_file => 'access.log');
$analyzer->load_attack_patterns();
$analyzer->analyze_file();
$analyzer->generate_report('security_report.txt');
```

### 4.2 网络安全工具开发

Perl 网络编程与安全工具。

```perl
#!/usr/bin/perl
use strict;
use warnings;
use IO::Socket::INET;
use IO::Socket::SSL;
use threads;
use Thread::Queue;
use Socket qw(getaddrinfo getnameinfo);

# ===== 端口扫描器 =====
sub port_scan {
    my ($host, $start_port, $end_port, $threads) = @_;
    $threads ||= 50;
    
    my $queue = Thread::Queue->new();
    my @open_ports;
    my @banners;
    
    # 填充队列
    $queue->enqueue($start_port .. $end_port);
    $queue->end();
    
    # 工作线程
    my @workers;
    for (1..$threads) {
        push @workers, threads->create(sub {
            while (my $port = $queue->dequeue_nb()) {
                my $socket = IO::Socket::INET->new(
                    PeerHost => $host,
                    PeerPort => $port,
                    Proto    => 'tcp',
                    Timeout  => 1,
                );
                
                if ($socket) {
                    push @open_ports, $port;
                    
                    # 简单的 banner 获取
                    $socket->send("HEAD / HTTP/1.0\r\n\r\n");
                    my $banner = '';
                    eval {
                        local $SIG{ALRM} = sub { die "timeout\n" };
                        alarm 1;
                        $socket->recv($banner, 1024);
                        alarm 0;
                    };
                    $banner = substr($banner, 0, 100);
                    push @banners, { port => $port, banner => $banner } if $banner;
                    
                    close($socket);
                }
            }
        });
    }
    
    $_->join() for @workers;
    
    @open_ports = sort { $a <=> $b } @open_ports;
    return \@open_ports, \@banners;
}

# ===== 子域名枚举 =====
sub subdomain_enum {
    my ($domain, $wordlist) = @_;
    my @found;
    
    open(my $fh, '<', $wordlist) or die $!;
    chomp(my @words = <$fh>);
    close($fh);
    
    my $queue = Thread::Queue->new();
    $queue->enqueue(@words);
    $queue->end();
    
    my @threads;
    for (1..20) {
        push @threads, threads->create(sub {
            while (my $sub = $queue->dequeue_nb()) {
                my $hostname = "$sub.$domain";
                
                # DNS 解析
                my ($err, @results) = getaddrinfo($hostname, "http");
                unless ($err) {
                    foreach my $result (@results) {
                        my ($err, $addr) = getnameinfo($result->{addr}, 0);
                        unless ($err) {
                            push @found, { host => $hostname, ip => $addr };
                            last;
                        }
                    }
                }
            }
        });
    }
    
    $_->join() for @threads;
    return @found;
}

# ===== Web 指纹识别 =====
sub web_fingerprint {
    my ($url) = @_;
    my %fingerprint;
    
    $url =~ m|^https?://([^/]+)|;
    my $host = $1;
    my $is_https = $url =~ /^https/;
    
    my $socket;
    if ($is_https) {
        $socket = IO::Socket::SSL->new(
            PeerHost => $host,
            PeerPort => 443,
            SSL_verify_mode => SSL_VERIFY_NONE,
            Timeout => 5,
        ) or return undef;
    } else {
        $socket = IO::Socket::INET->new(
            PeerHost => $host,
            PeerPort => 80,
            Proto    => 'tcp',
            Timeout  => 5,
        ) or return undef;
    }
    
    # 发送请求
    print $socket "GET / HTTP/1.1\r\nHost: $host\r\nUser-Agent: Fingerprint/1.0\r\n\r\n";
    
    my $response = '';
    eval {
        local $SIG{ALRM} = sub { die "timeout\n" };
        alarm 5;
        while (<$socket>) {
            $response .= $_;
            last if $_ eq "\r\n";
        }
        alarm 0;
    };
    
    close($socket);
    
    # 解析响应头
    my @lines = split /\r\n/, $response;
    $fingerprint{status} = $lines[0] if @lines;
    
    foreach my $line (@lines) {
        if ($line =~ /^Server:\s*(.+)/i) {
            $fingerprint{server} = $1;
        } elsif ($line =~ /^X-Powered-By:\s*(.+)/i) {
            $fingerprint{powered_by} = $1;
        } elsif ($line =~ /^Set-Cookie:\s*([^=]+)=/i) {
            $fingerprint{cookies} ||= [];
            push @{$fingerprint{cookies}}, $1;
        } elsif ($line =~ /^Content-Type:\s*(.+)/i) {
            $fingerprint{content_type} = $1;
        }
    }
    
    return \%fingerprint;
}

# ===== 密码强度检测 =====
sub password_strength {
    my ($password) = @_;
    my $score = 0;
    my @feedback;
    
    # 长度评分
    my $len = length($password);
    if ($len < 8) {
        push @feedback, "密码太短（至少 8 位）";
    } elsif ($len >= 12) {
        $score += 2;
    } else {
        $score += 1;
    }
    
    # 字符类型
    if ($password =~ /[a-z]/) {
        $score += 1;
    } else {
        push @feedback, "缺少小写字母";
    }
    
    if ($password =~ /[A-Z]/) {
        $score += 1;
    } else {
        push @feedback, "缺少大写字母";
    }
    
    if ($password =~ /\d/) {
        $score += 1;
    } else {
        push @feedback, "缺少数字";
    }
    
    if ($password =~ /[^a-zA-Z\d]/) {
        $score += 1;
    } else {
        push @feedback, "缺少特殊字符";
    }
    
    # 常见弱密码检测
    my @weak_passwords = qw(password 123456 qwerty admin letmein welcome monkey dragon);
    if (grep { lc($password) eq $_ } @weak_passwords) {
        $score = 0;
        push @feedback, "常见弱密码";
    }
    
    # 评级
    my $rating;
    if ($score <= 2) {
        $rating = '弱';
    } elsif ($score <= 4) {
        $rating = '中等';
    } else {
        $rating = '强';
    }
    
    return {
        score => $score,
        rating => $rating,
        feedback => \@feedback,
    };
}

# ===== 主程序 =====
print "=== Perl 安全工具集 ===\n\n";

# 端口扫描示例
print "[1] 端口扫描\n";
my ($open_ports, $banners) = port_scan('127.0.0.1', 1, 1000, 100);
print "开放端口: " . join(', ', @$open_ports) . "\n\n";

# 密码强度检测
print "[2] 密码强度检测\n";
my $result = password_strength('TestPass123!');
print "评分: $result->{score} ($result->{rating})\n";
print "建议:\n";
print "  - $_\n" for @{$result->{feedback}};
```

---

## 五、进阶学习资源

### 5.1 Perl 安全资源

- **Perl 官方安全文档**：https://perldoc.perl.org/perlsec
- **Perl 安全最佳实践**：https://perldoc.perl.org/perlsec
- **CPAN 安全模块**：https://metacpan.org/
- **Perl 安全公告**：https://perldoc.perl.org/perlsec

### 5.2 安全工具与库

- **网络安全**：
  - IO::Socket::INET — 网络套接字
  - IO::Socket::SSL — SSL/TLS
  - LWP::UserAgent — HTTP 客户端
  - Mojo::UserAgent — 现代 HTTP 客户端

- **加密库**：
  - Crypt::Eksblowfish::Bcrypt — bcrypt
  - Crypt::OpenSSL::RSA — RSA
  - Crypt::OpenSSL::AES — AES
  - Digest::SHA — SHA 哈希
  - Crypt::CBC — CBC 模式加密

- **安全工具**：
  - Nikto — Web 扫描器
  - sqlmap — SQL 注入工具（部分 Perl）
  - OWASP ZAP — Web 安全扫描
  - metasploit — 渗透测试框架

### 5.3 Web 安全

- **OWASP Perl**：https://www.owasp.org/index.php/Perl
- **CGI 安全**：https://perldoc.perl.org/CGI
- **Mojolicious 安全**：https://mojolicious.org/perldoc/Mojolicious/Guides/Rendering
- **Dancer2 安全**：https://metacpan.org/pod/Dancer2::Manual::Security

### 5.4 CTF 与练习平台

- **Hack The Box**：https://www.hackthebox.com/
- **TryHackMe**：https://tryhackme.com/
- **OverTheWire**：https://overthewire.org/wargames/
- **VulnHub**：https://www.vulnhub.com/
- **攻防世界**：https://adworld.xctf.org.cn/

### 5.5 推荐书籍

- **Perl 编程**：
  - 《Perl 编程》（Programming Perl）
  - 《Perl 语言入门》（Learning Perl）
  - 《高阶 Perl》（Higher-Order Perl）
  - 《Perl 最佳实践》

- **安全与渗透**：
  - 《Perl 安全编程》
  - 《黑客攻防技术宝典》
  - 《Web 安全深度剖析》

### 5.6 社区与资源

- **Perl Monks**：https://www.perlmonks.org/
- **Perl.com**：https://www.perl.com/
- **CPAN**：https://www.cpan.org/
- **FreeBuf**：https://www.freebuf.com/
- **先知社区**：https://xz.aliyun.com/

### 5.7 进阶学习路线

**第 1 阶段：Perl 精通（1-2月）**
- 正则表达式深入
- 引用与复杂数据结构
- 面向对象编程
- CPAN 模块使用

**第 2 阶段：系统与网络（2-3月）**
- 网络编程
- 系统管理脚本
- 文件系统操作
- 进程管理

**第 3 阶段：安全工具开发（2-3月）**
- 漏洞扫描器
- 日志分析工具
- 爬虫与自动化
- 文本处理

**第 4 阶段：高级应用（2-3月）**
- Web 框架（Mojolicious/Dancer）
- 数据库安全
- 加密与认证
- 分布式工具

**第 5 阶段：实战与贡献（持续）**
- CTF 比赛
- 安全工具开发
- 漏洞研究
- 开源贡献
