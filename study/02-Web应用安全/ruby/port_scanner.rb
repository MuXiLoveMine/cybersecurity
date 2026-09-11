#!/usr/bin/env ruby
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
#   ruby port_scanner.rb <目标IP> [起始端口] [结束端口] [线程数]
#
# 【参数说明】
#   目标IP    - 必填，要扫描的主机IP地址或域名
#   起始端口  - 可选，扫描范围起始端口，默认 1
#   结束端口  - 可选，扫描范围结束端口，默认 1024
#   线程数    - 可选，并发线程数，默认 50
#
# 【示例】
#   ruby port_scanner.rb 127.0.0.1
#   ruby port_scanner.rb 192.168.1.1 1 65535 100
#   ruby port_scanner.rb localhost 80 1000 20
#
# 【免责声明】
#   本工具仅供学习和授权测试使用，未经授权扫描他人网络属于违法行为。
#   使用本工具请遵守当地法律法规，违者后果自负。
# ============================================================

require 'socket'   # Ruby 标准库 socket 模块，用于 TCP 网络操作
require 'thread'   # 线程相关库
require 'timeout'  # 超时处理

# ============================================================
# 常见端口与服务对应表（部分常用端口）
# 参考：IANA 端口分配标准
# ============================================================
WELL_KNOWN_PORTS = {
  21 => 'FTP (文件传输协议)',
  22 => 'SSH (安全外壳协议)',
  23 => 'Telnet (远程终端协议)',
  25 => 'SMTP (简单邮件传输协议)',
  53 => 'DNS (域名系统)',
  80 => 'HTTP (超文本传输协议)',
  110 => 'POP3 (邮局协议v3)',
  111 => 'RPC (远程过程调用)',
  135 => 'MS RPC (微软远程过程调用)',
  139 => 'NetBIOS (网络基本输入输出系统)',
  143 => 'IMAP (互联网消息访问协议)',
  443 => 'HTTPS (安全超文本传输协议)',
  445 => 'SMB (服务器消息块)',
  993 => 'IMAPS (安全IMAP)',
  995 => 'POP3S (安全POP3)',
  1080 => 'SOCKS (代理协议)',
  1433 => 'MSSQL (微软SQL Server)',
  1521 => 'Oracle DB (Oracle数据库)',
  3306 => 'MySQL (MySQL数据库)',
  3389 => 'RDP (远程桌面协议)',
  5432 => 'PostgreSQL (PostgreSQL数据库)',
  5900 => 'VNC (虚拟网络计算)',
  6379 => 'Redis (Redis内存数据库)',
  8080 => 'HTTP-Proxy (HTTP代理/备用端口)',
  8443 => 'HTTPS-Alt (HTTPS备用端口)',
  8888 => 'HTTP-Alt (HTTP备用端口)',
  27017 => 'MongoDB (MongoDB数据库)',
}.freeze

# ============================================================
# 扫描单个端口
# ============================================================
# 扫描指定主机的单个端口，返回扫描结果哈希
# @param host [String] 目标主机IP或域名
# @param port [Integer] 目标端口号
# @param timeout [Integer] 连接超时时间（秒）
# @return [Hash] 扫描结果，包含 port、open、service、error 等字段
def scan_port(host, port, timeout = 2)
  result = {
    port: port,
    open: false,
    service: WELL_KNOWN_PORTS[port] || '未知服务',
    error: nil
  }

  begin
    # 使用 Timeout.timeout 设置连接超时
    # TCPSocket.new 会尝试建立 TCP 连接
    Timeout.timeout(timeout) do
      socket = TCPSocket.new(host, port)
      socket.close  # 连接成功，立即关闭，避免占用资源
      result[:open] = true
    end
  rescue Timeout::Error
    # 连接超时 - 端口可能被防火墙过滤
    result[:error] = 'timeout'
  rescue Errno::ECONNREFUSED
    # 连接被拒绝 - 端口关闭（收到 RST 包）
    result[:error] = 'refused'
  rescue Errno::EHOSTUNREACH
    # 主机不可达
    result[:error] = 'host_unreachable'
  rescue Errno::ENETUNREACH
    # 网络不可达
    result[:error] = 'net_unreachable'
  rescue => e
    # 其他错误
    result[:error] = e.class.name
  end

  result
end

# ============================================================
# 并发端口扫描（多线程）
# ============================================================
# 使用线程池模式进行并发端口扫描
# @param host [String] 目标主机
# @param start_port [Integer] 起始端口
# @param end_port [Integer] 结束端口
# @param thread_count [Integer] 线程数
# @param timeout [Integer] 超时时间（秒）
# @return [Array] 开放端口列表
def port_scan(host, start_port, end_port, thread_count = 50, timeout = 2)
  total_ports = end_port - start_port + 1
  open_ports = []              # 存储开放的端口
  port_queue = (start_port..end_port).to_a  # 待扫描端口队列
  scanned_count = 0            # 已扫描的端口数量
  mutex = Mutex.new            # 互斥锁，用于保护共享资源

  puts "\n[*] 开始扫描目标: #{host}"
  puts "[*] 端口范围: #{start_port} - #{end_port} (共 #{total_ports} 个端口)"
  puts "[*] 线程数: #{thread_count}"
  puts "[*] 超时时间: #{timeout}秒"
  puts '=' * 60

  start_time = Time.now

  # ============================================================
  # 并发控制核心逻辑：工作线程模式
  # 启动 thread_count 个工作线程，每个线程不断从端口队列中
  # 取出下一个端口进行扫描，直到队列为空
  # 使用互斥锁保护共享资源（队列、计数器、结果数组）
  # ============================================================
  threads = []

  thread_count.times do
    threads << Thread.new do
      loop do
        # 从端口队列中取出下一个待扫描端口
        # 使用互斥锁确保线程安全
        port = nil
        mutex.synchronize do
          port = port_queue.shift  # 取出队列第一个元素
        end

        # 队列为空，退出循环
        break if port.nil?

        # 扫描当前端口
        result = scan_port(host, port, timeout)

        # 更新扫描计数并打印进度
        mutex.synchronize do
          scanned_count += 1

          # 如果端口开放，记录并打印
          if result[:open]
            open_ports << result
            puts "[+] 端口 #{result[:port]} 开放 - #{result[:service]}"
          end

          # 每扫描100个端口打印一次进度
          if scanned_count % 100 == 0 || scanned_count == total_ports
            progress = (scanned_count.to_f / total_ports * 100).round(1)
            print "\r[*] 扫描进度: #{scanned_count}/#{total_ports} (#{progress}%)"
            $stdout.flush
          end
        end
      end
    end
  end

  # 等待所有线程完成
  threads.each(&:join)

  end_time = Time.now
  duration = (end_time - start_time).round(2)

  # ============================================================
  # 输出扫描结果汇总
  # ============================================================
  puts "\n" + '=' * 60
  puts "[*] 扫描完成！耗时: #{duration} 秒"
  puts "[*] 扫描端口总数: #{total_ports}"
  puts "[+] 发现开放端口: #{open_ports.length} 个"

  if open_ports.length > 0
    puts "\n[*] 开放端口列表:"
    puts '-' * 40
    # 按端口号排序
    open_ports.sort_by! { |p| p[:port] }
    open_ports.each do |p|
      puts "  #{p[:port]}/tcp\t开放\t#{p[:service]}"
    end
  end

  open_ports
end

# ============================================================
# 命令行参数解析与主程序入口
# ============================================================
def main
  # 解析命令行参数
  # ARGV[0] = 目标IP
  # ARGV[1] = 起始端口
  # ARGV[2] = 结束端口
  # ARGV[3] = 线程数

  if ARGV.length < 1
    puts '用法: ruby port_scanner.rb <目标IP> [起始端口] [结束端口] [线程数]'
    puts '示例: ruby port_scanner.rb 127.0.0.1 1 1024 50'
    exit 1
  end

  host = ARGV[0]
  start_port = (ARGV[1] || 1).to_i
  end_port = (ARGV[2] || 1024).to_i
  thread_count = (ARGV[3] || 50).to_i

  # 参数合法性检查
  if start_port < 1 || end_port > 65535 || start_port > end_port
    puts '[!] 错误：端口范围无效，请输入 1-65535 范围内的有效端口'
    exit 1
  end

  if thread_count < 1 || thread_count > 500
    puts '[!] 错误：线程数应在 1-500 之间'
    exit 1
  end

  # 执行扫描
  begin
    port_scan(host, start_port, end_port, thread_count)
  rescue Interrupt
    puts "\n[!] 用户中断扫描"
    exit 0
  rescue => e
    puts "\n[!] 扫描出错: #{e.message}"
    exit 1
  end
end

# 运行主程序
main if __FILE__ == $0
