// ============================================================
// 端口扫描器 (Port Scanner)
// ============================================================
//
// 【原理说明】
// 端口扫描是网络安全测试中最基础的步骤之一，用于发现目标主机上开放的服务端口。
// 本工具使用 TCP 全连接扫描（Full Connect Scan）原理：
//   - 尝试与目标主机的指定端口建立 TCP 连接
//   - 如果连接成功（三次握手完成），说明端口开放
//   - 如果连接被拒绝（RST包）或超时，说明端口关闭或被防火墙过滤
//
// 【扫描方式对比】
//   - TCP全连接扫描：最可靠、最易检测，需要完成完整三次握手
//   - SYN半开扫描：只发送SYN包，不建立完整连接，更隐蔽（需要原始套接字权限）
//   - UDP扫描：扫描UDP端口，不可靠且速度慢
//
// 【编译运行】
//   方式一：直接运行
//     rustc port_scanner.rs && ./port_scanner <目标IP> [起始端口] [结束端口] [线程数]
//   方式二：使用 Cargo（推荐，便于管理依赖）
//     cargo init scanner && cd scanner
//     （将本文件内容替换 src/main.rs）
//     cargo run -- <目标IP> [起始端口] [结束端口] [线程数]
//
// 【使用方法】
//   port_scanner <目标IP> [起始端口] [结束端口] [线程数]
//
// 【参数说明】
//   目标IP    - 必填，要扫描的主机IP地址或域名
//   起始端口  - 可选，扫描范围起始端口，默认 1
//   结束端口  - 可选，扫描范围结束端口，默认 1024
//   线程数    - 可选，并发线程数，默认 50
//
// 【示例】
//   port_scanner 127.0.0.1
//   port_scanner 192.168.1.1 1 65535 100
//   port_scanner localhost 80 1000 20
//
// 【免责声明】
//   本工具仅供学习和授权测试使用，未经授权扫描他人网络属于违法行为。
//   使用本工具请遵守当地法律法规，违者后果自负。
// ============================================================

use std::env;                    // 命令行参数处理
use std::net::TcpStream;         // TCP 连接
use std::time::Duration;         // 时间类型
use std::sync::{Arc, Mutex};     // 线程同步
use std::thread;                 // 多线程
use std::collections::HashMap;   // 哈希映射

// ============================================================
// 常见端口与服务对应表（部分常用端口）
// 参考：IANA 端口分配标准
// ============================================================
fn get_well_known_ports() -> HashMap<u16, &'static str> {
    let mut ports = HashMap::new();
    ports.insert(21, "FTP (文件传输协议)");
    ports.insert(22, "SSH (安全外壳协议)");
    ports.insert(23, "Telnet (远程终端协议)");
    ports.insert(25, "SMTP (简单邮件传输协议)");
    ports.insert(53, "DNS (域名系统)");
    ports.insert(80, "HTTP (超文本传输协议)");
    ports.insert(110, "POP3 (邮局协议v3)");
    ports.insert(111, "RPC (远程过程调用)");
    ports.insert(135, "MS RPC (微软远程过程调用)");
    ports.insert(139, "NetBIOS (网络基本输入输出系统)");
    ports.insert(143, "IMAP (互联网消息访问协议)");
    ports.insert(443, "HTTPS (安全超文本传输协议)");
    ports.insert(445, "SMB (服务器消息块)");
    ports.insert(993, "IMAPS (安全IMAP)");
    ports.insert(995, "POP3S (安全POP3)");
    ports.insert(1080, "SOCKS (代理协议)");
    ports.insert(1433, "MSSQL (微软SQL Server)");
    ports.insert(1521, "Oracle DB (Oracle数据库)");
    ports.insert(3306, "MySQL (MySQL数据库)");
    ports.insert(3389, "RDP (远程桌面协议)");
    ports.insert(5432, "PostgreSQL (PostgreSQL数据库)");
    ports.insert(5900, "VNC (虚拟网络计算)");
    ports.insert(6379, "Redis (Redis内存数据库)");
    ports.insert(8080, "HTTP-Proxy (HTTP代理/备用端口)");
    ports.insert(8443, "HTTPS-Alt (HTTPS备用端口)");
    ports.insert(8888, "HTTP-Alt (HTTP备用端口)");
    ports.insert(27017, "MongoDB (MongoDB数据库)");
    ports
}

// ============================================================
// 扫描结果结构体
// ============================================================
#[derive(Debug, Clone)]
struct ScanResult {
    port: u16,        // 端口号
    is_open: bool,    // 是否开放
    service: String,  // 对应的服务名称
}

// ============================================================
// 扫描单个端口
// ============================================================
// 扫描指定主机的单个端口，返回扫描结果
// 参数：
//   host - 目标主机IP或域名
//   port - 目标端口号
//   timeout - 连接超时时间
// 返回：ScanResult 结构体
fn scan_port(host: &str, port: u16, timeout: Duration) -> ScanResult {
    let well_known = get_well_known_ports();
    let service = well_known.get(&port)
        .map(|s| s.to_string())
        .unwrap_or_else(|| "未知服务".to_string());

    // 构造地址字符串
    let addr = format!("{}:{}", host, port);

    // 尝试建立 TCP 连接，设置超时
    match TcpStream::connect_timeout(&addr.parse().unwrap(), timeout) {
        Ok(stream) => {
            // 连接成功，端口开放
            drop(stream);  // 关闭连接
            ScanResult {
                port,
                is_open: true,
                service,
            }
        }
        Err(_) => {
            // 连接失败，端口关闭或被过滤
            ScanResult {
                port,
                is_open: false,
                service,
            }
        }
    }
}

// ============================================================
// 并发端口扫描（多线程）
// ============================================================
// 使用线程池模式进行并发端口扫描
// 参数：
//   host - 目标主机
//   start_port - 起始端口
//   end_port - 结束端口
//   thread_count - 线程数
//   timeout - 超时时间
// 返回：开放端口的向量
fn port_scan(host: &str, start_port: u16, end_port: u16, thread_count: usize, timeout: Duration) -> Vec<ScanResult> {
    let total_ports = (end_port - start_port + 1) as usize;

    println!("\n[*] 开始扫描目标: {}", host);
    println!("[*] 端口范围: {} - {} (共 {} 个端口)", start_port, end_port, total_ports);
    println!("[*] 线程数: {}", thread_count);
    println!("[*] 超时时间: {:?}", timeout);
    println!("{}", "=".repeat(60));

    let start_time = std::time::Instant::now();

    // 共享状态：端口队列、结果列表、扫描计数
    // 使用 Arc<Mutex<>> 实现多线程安全共享
    let port_queue: Arc<Mutex<Vec<u16>>> = Arc::new(Mutex::new(
        (start_port..=end_port).collect()
    ));
    let open_ports: Arc<Mutex<Vec<ScanResult>>> = Arc::new(Mutex::new(Vec::new()));
    let scanned_count: Arc<Mutex<usize>> = Arc::new(Mutex::new(0));

    let mut handles = Vec::new();

    // ============================================================
    // 启动工作线程
    // 每个线程不断从端口队列中取出端口进行扫描
    // ============================================================
    for _ in 0..thread_count {
        let port_queue = Arc::clone(&port_queue);
        let open_ports = Arc::clone(&open_ports);
        let scanned_count = Arc::clone(&scanned_count);
        let host = host.to_string();

        let handle = thread::spawn(move || {
            loop {
                // 从端口队列中取出下一个端口
                let port = {
                    let mut queue = port_queue.lock().unwrap();
                    queue.pop()  // 从末尾弹出（效率更高）
                };

                // 队列为空，退出循环
                match port {
                    None => break,
                    Some(p) => {
                        // 扫描当前端口
                        let result = scan_port(&host, p, timeout);

                        // 更新计数和结果
                        let mut count = scanned_count.lock().unwrap();
                        *count += 1;
                        let current_count = *count;

                        // 如果端口开放，添加到结果列表
                        if result.is_open {
                            let mut results = open_ports.lock().unwrap();
                            results.push(result.clone());
                            // 打印发现的开放端口
                            println!("[+] 端口 {} 开放 - {}", result.port, result.service);
                        }

                        // 每扫描100个端口打印一次进度
                        if current_count % 100 == 0 || current_count == total_ports {
                            let progress = (current_count as f64 / total_ports as f64) * 100.0;
                            print!("\r[*] 扫描进度: {}/{} ({:.1}%)", current_count, total_ports, progress);
                            use std::io::Write;
                            std::io::stdout().flush().unwrap();
                        }
                    }
                }
            }
        });

        handles.push(handle);
    }

    // 等待所有线程完成
    for handle in handles {
        handle.join().unwrap();
    }

    let duration = start_time.elapsed();

    // 获取结果并排序
    let mut results = open_ports.lock().unwrap().clone();
    results.sort_by_key(|r| r.port);

    // ============================================================
    // 输出扫描结果汇总
    // ============================================================
    println!("\n{}", "=".repeat(60));
    println!("[*] 扫描完成！耗时: {:.2} 秒", duration.as_secs_f64());
    println!("[*] 扫描端口总数: {}", total_ports);
    println!("[+] 发现开放端口: {} 个", results.len());

    if !results.is_empty() {
        println!("\n[*] 开放端口列表:");
        println!("{}", "-".repeat(40));
        for r in &results {
            println!("  {}/tcp\t开放\t{}", r.port, r.service);
        }
    }

    results
}

// ============================================================
// 主函数
// ============================================================
fn main() {
    // 解析命令行参数
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        println!("用法: {} <目标IP> [起始端口] [结束端口] [线程数]", args[0]);
        println!("示例: {} 127.0.0.1 1 1024 50", args[0]);
        std::process::exit(1);
    }

    let host = &args[1];
    let start_port: u16 = args.get(2)
        .and_then(|s| s.parse().ok())
        .unwrap_or(1);
    let end_port: u16 = args.get(3)
        .and_then(|s| s.parse().ok())
        .unwrap_or(1024);
    let thread_count: usize = args.get(4)
        .and_then(|s| s.parse().ok())
        .unwrap_or(50);

    // 参数合法性检查
    if start_port < 1 || end_port > 65535 || start_port > end_port {
        println!("[!] 错误：端口范围无效，请输入 1-65535 范围内的有效端口");
        std::process::exit(1);
    }

    if thread_count < 1 || thread_count > 500 {
        println!("[!] 错误：线程数应在 1-500 之间");
        std::process::exit(1);
    }

    // 设置超时时间
    let timeout = Duration::from_secs(2);

    // 执行扫描
    port_scan(host, start_port, end_port, thread_count, timeout);
}
