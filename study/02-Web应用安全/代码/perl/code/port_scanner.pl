#!/usr/bin/perl
# ============================================================
# 端口扫描器 (Port Scanner)
# ============================================================
#
# 【原理说明】
# 端口扫描是网络安全测试中最基础的步骤之一，用于发现目标主机上开放的服务端口。
# 本工具使用 TCP 全连接扫描（Full Connect Scan）原理：
#   - 尝试与目标主机的指定端口建立 TCP 连接
#   - 如果连接成功（三次握手完成），说明端口开放
#   - 如果连接被拒绝（RST包）或超时，说明端口关闭或被防火墙过滤
#
# 【扫描方式对比】
#   - TCP全连接扫描：最可靠、最易检测，需要完成完整三次握手
#   - SYN半开扫描：只发送SYN包，不建立完整连接，更隐蔽（需要原始套接字权限）
#   - UDP扫描：扫描UDP端口，不可靠且速度慢
#
# 【使用方法】
#   perl port_scanner.pl <目标IP> [起始端口] [结束端口] [fork数]
#
# 【参数说明】
#   目标IP    - 必填，要扫描的主机IP地址或域名
#   起始端口  - 可选，扫描范围起始端口，默认 1
#   结束端口  - 可选，扫描范围结束端口，默认 1024
#   fork数    - 可选，并发 fork 子进程数，默认 30
#
# 【示例】
#   perl port_scanner.pl 127.0.0.1
#   perl port_scanner.pl 192.168.1.1 1 65535 50
#   perl port_scanner.pl localhost 80 1000 20
#
# 【技术说明】
#   本工具使用 IO::Socket 模块进行 TCP 连接，
#   使用 fork 多进程方式实现并发扫描（Perl 传统并发模型）。
#   每个子进程负责扫描一部分端口，通过管道将结果返回给父进程。
#
# 【免责声明】
#   本工具仅供学习和授权测试使用，未经授权扫描他人网络属于违法行为。
#   使用本工具请遵守当地法律法规，违者后果自负。
# ============================================================

use strict;             # 严格语法检查
use warnings;           # 开启警告
use IO::Socket;         # 套接字模块
use POSIX ":sys_wait_h"; # 进程等待
use Time::HiRes qw(time);  # 高精度时间

# ============================================================
# 常见端口与服务对应表（部分常用端口）
# 参考：IANA 端口分配标准
# ============================================================
my %WELL_KNOWN_PORTS = (
    21    => 'FTP (文件传输协议)',
    22    => 'SSH (安全外壳协议)',
    23    => 'Telnet (远程终端协议)',
    25    => 'SMTP (简单邮件传输协议)',
    53    => 'DNS (域名系统)',
    80    => 'HTTP (超文本传输协议)',
    110   => 'POP3 (邮局协议v3)',
    111   => 'RPC (远程过程调用)',
    135   => 'MS RPC (微软远程过程调用)',
    139   => 'NetBIOS (网络基本输入输出系统)',
    143   => 'IMAP (互联网消息访问协议)',
    443   => 'HTTPS (安全超文本传输协议)',
    445   => 'SMB (服务器消息块)',
    993   => 'IMAPS (安全IMAP)',
    995   => 'POP3S (安全POP3)',
    1080  => 'SOCKS (代理协议)',
    1433  => 'MSSQL (微软SQL Server)',
    1521  => 'Oracle DB (Oracle数据库)',
    3306  => 'MySQL (MySQL数据库)',
    3389  => 'RDP (远程桌面协议)',
    5432  => 'PostgreSQL (PostgreSQL数据库)',
    5900  => 'VNC (虚拟网络计算)',
    6379  => 'Redis (Redis内存数据库)',
    8080  => 'HTTP-Proxy (HTTP代理/备用端口)',
    8443  => 'HTTPS-Alt (HTTPS备用端口)',
    8888  => 'HTTP-Alt (HTTP备用端口)',
    27017 => 'MongoDB (MongoDB数据库)',
);

# ============================================================
# 扫描单个端口
# ============================================================
# 扫描指定主机的单个端口，返回是否开放
# 参数：
#   $host - 目标主机IP或域名
#   $port - 目标端口号
#   $timeout - 连接超时时间（秒）
# 返回：1（开放）或 0（关闭/过滤）
sub scan_port {
    my ($host, $port, $timeout) = @_;

    # 创建 TCP 套接字并尝试连接
    my $socket = IO::Socket::INET->new(
        PeerHost => $host,        # 目标主机
        PeerPort => $port,        # 目标端口
        Proto    => 'tcp',        # 协议：TCP
        Timeout  => $timeout,     # 超时时间
    );

    if ($socket) {
        # 连接成功，端口开放
        close($socket);
        return 1;
    }

    # 连接失败，端口关闭或被过滤
    return 0;
}

# ============================================================
# 获取端口对应的服务名称
# ============================================================
sub get_service_name {
    my ($port) = @_;
    return $WELL_KNOWN_PORTS{$port} || '未知服务';
}

# ============================================================
# 并发端口扫描（fork 多进程）
# ============================================================
# 使用 fork 多进程方式进行并发端口扫描
# 父进程分配端口任务，子进程执行扫描并通过管道返回结果
# 参数：
#   $host - 目标主机
#   $start_port - 起始端口
#   $end_port - 结束端口
#   $max_forks - 最大并发子进程数
#   $timeout - 超时时间（秒）
# 返回：开放端口列表的引用
sub port_scan {
    my ($host, $start_port, $end_port, $max_forks, $timeout) = @_;

    my $total_ports = $end_port - $start_port + 1;
    my @open_ports;    # 存储开放的端口
    my $current_port = $start_port;  # 当前待分配的端口
    my $scanned_count = 0;  # 已扫描数量

    print "\n[*] 开始扫描目标: $host\n";
    print "[*] 端口范围: $start_port - $end_port (共 $total_ports 个端口)\n";
    print "[*] 最大并发进程数: $max_forks\n";
    print "[*] 超时时间: ${timeout}秒\n";
    print '=' x 60 . "\n";

    my $start_time = time();

    # ============================================================
    # 创建管道用于子进程向父进程发送结果
    # ============================================================
    pipe(my $read_pipe, my $write_pipe) or die "无法创建管道: $!";

    # ============================================================
    # fork 多进程并发扫描
    # 父进程负责任务分配和结果收集
    # 子进程负责扫描指定端口并将结果写入管道
    # ============================================================
    my %children;  # 子进程 PID -> 1 的映射
    my $active_forks = 0;

    # 持续分配任务直到所有端口扫描完毕
    while ($current_port <= $end_port || $active_forks > 0) {
        # 如果还有未分配的端口且子进程数未达上限，fork 新的子进程
        while ($current_port <= $end_port && $active_forks < $max_forks) {
            my $port = $current_port++;
            my $pid = fork();

            if (!defined($pid)) {
                # fork 失败
                warn "[!] fork 失败: $!";
                next;
            }

            if ($pid == 0) {
                # ============================================================
                # 子进程：执行端口扫描
                # ============================================================
                close($read_pipe);  # 子进程关闭读端

                my $is_open = scan_port($host, $port, $timeout);

                # 将结果写入管道（格式：端口号|是否开放）
                print $write_pipe "$port|$is_open\n";
                close($write_pipe);

                exit 0;  # 子进程退出
            } else {
                # ============================================================
                # 父进程：记录子进程
                # ============================================================
                $children{$pid} = 1;
                $active_forks++;
            }
        }

        # ============================================================
        # 父进程：等待子进程完成并收集结果
        # ============================================================
        if ($active_forks > 0) {
            # 读取管道中的结果（非阻塞方式）
            my $line = '';
            vec(my $rin, fileno($read_pipe), 1) = 1;

            # 使用 select 检查管道是否有数据可读
            if (select($rin, undef, undef, 0.1) > 0) {
                while (my $line = <$read_pipe>) {
                    chomp($line);
                    my ($port, $is_open) = split(/\|/, $line);

                    $scanned_count++;

                    if ($is_open) {
                        my $service = get_service_name($port);
                        push @open_ports, { port => $port, service => $service };
                        print "[+] 端口 $port 开放 - $service\n";
                    }

                    # 每扫描100个端口打印一次进度
                    if ($scanned_count % 100 == 0 || $scanned_count == $total_ports) {
                        my $progress = sprintf("%.1f", $scanned_count / $total_ports * 100);
                        print "\r[*] 扫描进度: $scanned_count/$total_ports ($progress%)";
                        $| = 1;  # 刷新输出缓冲区
                    }
                }
            }

            # 回收已退出的子进程
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
    print "[*] 扫描端口总数: $total_ports\n";
    print "[+] 发现开放端口: " . scalar(@open_ports) . " 个\n";

    if (@open_ports) {
        print "\n[*] 开放端口列表:\n";
        print '-' x 40 . "\n";

        # 按端口号排序
        @open_ports = sort { $a->{port} <=> $b->{port} } @open_ports;

        foreach my $p (@open_ports) {
            print "  $p->{port}/tcp\t开放\t$p->{service}\n";
        }
    }

    return \@open_ports;
}

# ============================================================
# 主程序入口
# ============================================================
sub main {
    # 解析命令行参数
    # $ARGV[0] = 目标IP
    # $ARGV[1] = 起始端口
    # $ARGV[2] = 结束端口
    # $ARGV[3] = fork数

    if (@ARGV < 1) {
        print "用法: perl port_scanner.pl <目标IP> [起始端口] [结束端口] [fork数]\n";
        print "示例: perl port_scanner.pl 127.0.0.1 1 1024 30\n";
        exit 1;
    }

    my $host = $ARGV[0];
    my $start_port = $ARGV[1] || 1;
    my $end_port = $ARGV[2] || 1024;
    my $max_forks = $ARGV[3] || 30;

    # 参数合法性检查
    if ($start_port < 1 || $end_port > 65535 || $start_port > $end_port) {
        print "[!] 错误：端口范围无效，请输入 1-65535 范围内的有效端口\n";
        exit 1;
    }

    if ($max_forks < 1 || $max_forks > 200) {
        print "[!] 错误：并发进程数应在 1-200 之间\n";
        exit 1;
    }

    # 设置超时时间
    my $timeout = 2;

    # 捕获中断信号
    $SIG{INT} = sub {
        print "\n[!] 用户中断扫描\n";
        exit 0;
    };

    # 执行扫描
    eval {
        port_scan($host, $start_port, $end_port, $max_forks, $timeout);
    };
    if ($@) {
        print "\n[!] 扫描出错: $@\n";
        exit 1;
    }
}

# 运行主程序
main();
