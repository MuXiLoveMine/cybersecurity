// ============================================================
// Web 目录爆破工具 (Directory Brute Force)
// ============================================================
//
// 【原理说明】
// 目录爆破是 Web 安全测试中用于发现隐藏目录和文件的常用技术。
// 本工具通过字典枚举的方式，向目标 Web 服务器发送大量 HTTP 请求，
// 根据响应状态码判断目录/文件是否存在。
//
// 本实现使用 Rust 标准库的 TcpStream 手动构建 HTTP 请求，
// 不依赖第三方库，便于学习 HTTP 协议底层原理。
//
// 【常见状态码含义】
//   200 OK          - 页面/文件存在且可正常访问
//   301/302 重定向   - 页面存在但发生了跳转
//   403 Forbidden    - 页面存在但禁止访问
//   404 Not Found    - 页面不存在
//   500 Internal Error - 服务器内部错误
//
// 【编译运行】
//   rustc dir_brute.rs && ./dir_brute <目标URL> [字典文件] [线程数]
//
// 【使用方法】
//   dir_brute <目标URL> [字典文件] [线程数] [超时时间]
//
// 【参数说明】
//   目标URL   - 必填，目标网站 URL，例如 http://example.com
//   字典文件  - 可选，字典文件路径，每行一个路径
//               不指定则使用内置字典
//   线程数    - 可选，并发线程数，默认 20
//   超时时间  - 可选，请求超时时间（秒），默认 10
//
// 【示例】
//   dir_brute http://127.0.0.1
//   dir_brute http://example.com wordlist.txt 30
//   dir_brute https://target.com /path/to/dict.txt 50 15
//
// 【内置字典说明】
//   内置了常见的后台、备份、配置、敏感文件路径约 80 个，
//   适用于快速检测。实际使用建议加载更大的字典文件。
//
// 【注意事项】
//   本工具使用标准库实现，仅支持 HTTP（HTTPS 需要 openssl 或 rustls 库）
//   如需 HTTPS 支持，建议使用 reqwest 等成熟 HTTP 库
//
// 【免责声明】
//   本工具仅供学习和授权测试使用，未经授权对他人网站进行
//   目录爆破属于违法行为。使用本工具请遵守当地法律法规。
// ============================================================

use std::env;                    // 命令行参数
use std::net::TcpStream;         // TCP 连接
use std::io::{Read, Write, BufRead, BufReader};  // IO 操作
use std::time::Duration;         // 时间类型
use std::sync::{Arc, Mutex};     // 线程同步
use std::thread;                 // 多线程
use std::fs::File;               // 文件操作
use std::collections::HashMap;   // 哈希映射

// ============================================================
// 内置字典：常见 Web 目录和敏感文件路径
// ============================================================
const DEFAULT_WORDLIST: &[&str] = &[
    // 后台管理入口
    "admin", "admin/", "administrator", "admin.php", "admin.html",
    "login", "login.php", "login.html", "admin/index.php", "admin/login.php",
    "manage", "manager", "backend", "system", "user", "users",
    "member", "members", "dashboard", "console", "controlpanel",
    "wp-admin", "wp-login.php", "phpmyadmin", "pma", "myadmin",

    // 备份和配置文件
    "backup", "backup.zip", "backup.tar", "backup.tar.gz", "backup.sql",
    ".git", ".git/config", ".git/HEAD", ".svn",
    "config", "config.php", "config.inc.php", "configuration.php",
    "database.sql", "db.sql", "dump.sql",
    ".htaccess", ".htpasswd", "robots.txt",
    "phpinfo.php", "info.php", "test.php",

    // 编辑器和 IDE 残留
    ".vscode", ".idea", ".DS_Store",
    ".env", ".env.local",

    // 常见目录
    "upload", "uploads", "images", "img", "css", "js",
    "data", "cache", "temp", "tmp", "logs", "log",
    "api", "api/v1", "api/v2", "rest",
    "docs", "doc", "files", "download",
    "forum", "blog", "news", "article",
    "search", "about", "contact", "faq",
    "install", "install.php", "setup", "setup.php",

    // 常见文件
    "index.html", "index.php", "index.asp", "index.jsp",
    "default.html", "default.php",
    "home.html", "home.php", "main.php",
    "README", "README.md", "CHANGELOG",
    "crossdomain.xml", "sitemap.xml",
];

// ============================================================
// HTTP 响应结果结构体
// ============================================================
#[derive(Debug, Clone)]
struct HttpResponse {
    status_code: u32,       // 状态码
    headers: HashMap<String, String>,  // 响应头
    content_length: usize,  // 响应体长度
    body: String,           // 响应体（截断）
    error: Option<String>,  // 错误信息
}

// ============================================================
// 发送 HTTP GET 请求（使用标准库 TcpStream 手动实现）
// ============================================================
// 参数：
//   host - 主机名
//   port - 端口号
//   path - 请求路径
//   timeout - 超时时间
// 返回：HttpResponse 结构体
fn http_get(host: &str, port: u16, path: &str, timeout: Duration) -> HttpResponse {
    let mut response = HttpResponse {
        status_code: 0,
        headers: HashMap::new(),
        content_length: 0,
        body: String::new(),
        error: None,
    };

    let addr = format!("{}:{}", host, port);

    // 建立 TCP 连接
    let mut stream = match TcpStream::connect_timeout(&addr.parse().unwrap(), timeout) {
        Ok(s) => s,
        Err(e) => {
            response.error = Some(format!("连接失败: {}", e));
            return response;
        }
    };

    // 设置读写超时
    if stream.set_read_timeout(Some(timeout)).is_err() {
        response.error = Some("设置读取超时失败".to_string());
        return response;
    }
    if stream.set_write_timeout(Some(timeout)).is_err() {
        response.error = Some("设置写入超时失败".to_string());
        return response;
    }

    // 构建 HTTP 请求报文
    let request = format!(
        "GET {} HTTP/1.1\r\n\
         Host: {}\r\n\
         User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n\
         Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n\
         Accept-Language: zh-CN,zh;q=0.9,en;q=0.8\r\n\
         Connection: close\r\n\
         \r\n",
        path, host
    );

    // 发送请求
    if stream.write_all(request.as_bytes()).is_err() {
        response.error = Some("发送请求失败".to_string());
        return response;
    }

    // 读取响应
    let mut reader = BufReader::new(stream);
    let mut response_text = String::new();

    match reader.read_to_string(&mut response_text) {
        Ok(_) => {}
        Err(e) => {
            response.error = Some(format!("读取响应失败: {}", e));
            return response;
        }
    }

    // 解析响应头和响应体
    // HTTP 响应头和响应体之间用空行分隔（\r\n\r\n）
    if let Some(blank_line_pos) = response_text.find("\r\n\r\n") {
        let headers_part = &response_text[..blank_line_pos];
        let body_part = &response_text[blank_line_pos + 4..];

        // 解析状态行（第一行）
        let mut header_lines = headers_part.lines();
        if let Some(status_line) = header_lines.next() {
            // 状态行格式: HTTP/1.1 200 OK
            let parts: Vec<&str> = status_line.split_whitespace().collect();
            if parts.len() >= 2 {
                response.status_code = parts[1].parse().unwrap_or(0);
            }
        }

        // 解析响应头
        for line in header_lines {
            if let Some(colon_pos) = line.find(':') {
                let key = line[..colon_pos].trim().to_string().to_lowercase();
                let value = line[colon_pos + 1..].trim().to_string();
                response.headers.insert(key, value);
            }
        }

        // 响应体（只保留前 1024 字节用于判断）
        response.body = body_part.chars().take(1024).collect();
        response.content_length = body_part.len();
    }

    response
}

// ============================================================
// URL 解析结果结构体
// ============================================================
struct ParsedUrl {
    scheme: String,   // 协议（http/https）
    host: String,     // 主机名
    port: u16,        // 端口号
    path: String,     // 路径
}

// ============================================================
// 解析 URL
// ============================================================
// 参数：url_str - URL 字符串
// 返回：解析结果
fn parse_url(url_str: &str) -> Result<ParsedUrl, String> {
    let mut url = url_str.to_string();

    // 确定协议
    let scheme = if url.starts_with("https://") {
        url = url[8..].to_string();
        "https".to_string()
    } else if url.starts_with("http://") {
        url = url[7..].to_string();
        "http".to_string()
    } else {
        return Err("URL 必须以 http:// 或 https:// 开头".to_string());
    };

    // 分离主机和路径
    let (host_port, path) = match url.find('/') {
        Some(pos) => (url[..pos].to_string(), url[pos..].to_string()),
        None => (url, "/".to_string()),
    };

    // 分离主机和端口
    let (host, port) = if host_port.contains(':') {
        let parts: Vec<&str> = host_port.splitn(2, ':').collect();
        let port_num: u16 = parts[1].parse().map_err(|_| "端口号无效".to_string())?;
        (parts[0].to_string(), port_num)
    } else {
        let default_port = if scheme == "https" { 443 } else { 80 };
        (host_port, default_port)
    };

    Ok(ParsedUrl { scheme, host, port, path })
}

// ============================================================
// 判断结果是否为"有效"路径
// ============================================================
fn is_valid_result(status_code: u32) -> bool {
    matches!(status_code, 200..=299 | 300..=399 | 401 | 403)
}

// ============================================================
// 加载字典文件
// ============================================================
fn load_wordlist(file_path: &str) -> Result<Vec<String>, String> {
    let file = File::open(file_path).map_err(|e| format!("打开文件失败: {}", e))?;
    let reader = BufReader::new(file);
    let mut paths = Vec::new();

    for line in reader.lines() {
        let line = line.map_err(|e| format!("读取文件失败: {}", e))?;
        let path = line.trim().to_string();
        // 跳过空行和注释行
        if path.is_empty() || path.starts_with('#') {
            continue;
        }
        // 去掉开头的斜杠
        let path = path.trim_start_matches('/').to_string();
        if !path.is_empty() {
            paths.push(path);
        }
    }

    Ok(paths)
}

// ============================================================
// 目录爆破主函数
// ============================================================
fn dir_brute(base_url: &str, wordlist: Vec<String>, thread_count: usize, timeout: Duration) -> Vec<(String, u32, usize, String)> {
    // 解析 URL
    let parsed = match parse_url(base_url) {
        Ok(p) => p,
        Err(e) => {
            println!("[!] URL 解析失败: {}", e);
            return Vec::new();
        }
    };

    // 检查是否是 HTTPS
    if parsed.scheme == "https" {
        println!("[!] 警告：本工具使用标准库实现，不支持 HTTPS");
        println!("[!] 请使用 HTTP 目标，或使用 reqwest 等库实现 HTTPS 版本");
    }

    let total_paths = wordlist.len();
    let base_path = if parsed.path.ends_with('/') {
        parsed.path.clone()
    } else {
        format!("{}/", parsed.path)
    };

    println!("\n[*] 开始目录爆破");
    println!("[*] 目标 URL: {}", base_url);
    println!("[*] 目标主机: {}:{}", parsed.host, parsed.port);
    println!("[*] 字典数量: {}", total_paths);
    println!("[*] 线程数: {}", thread_count);
    println!("[*] 超时时间: {:?}", timeout);
    println!("{}", "=".repeat(60));

    let start_time = std::time::Instant::now();

    // 共享状态
    let path_queue: Arc<Mutex<Vec<String>>> = Arc::new(Mutex::new(wordlist));
    let found_paths: Arc<Mutex<Vec<(String, u32, usize, String)>>> = Arc::new(Mutex::new(Vec::new()));
    let scanned_count: Arc<Mutex<usize>> = Arc::new(Mutex::new(0));

    let mut handles = Vec::new();

    // 启动工作线程
    for _ in 0..thread_count {
        let path_queue = Arc::clone(&path_queue);
        let found_paths = Arc::clone(&found_paths);
        let scanned_count = Arc::clone(&scanned_count);
        let host = parsed.host.clone();
        let base_path = base_path.clone();
        let port = parsed.port;

        let handle = thread::spawn(move || {
            loop {
                // 从队列中取出路径
                let path = {
                    let mut queue = path_queue.lock().unwrap();
                    queue.pop()
                };

                match path {
                    None => break,
                    Some(p) => {
                        // 构造请求路径
                        let request_path = format!("{}{}", base_path, p);

                        // 发送 HTTP 请求
                        let response = http_get(&host, port, &request_path, timeout);

                        // 处理结果
                        let mut count = scanned_count.lock().unwrap();
                        *count += 1;
                        let current_count = *count;

                        if response.status_code != 0 && is_valid_result(response.status_code) {
                            let redirect = response.headers.get("location")
                                .cloned()
                                .unwrap_or_default();

                            let mut results = found_paths.lock().unwrap();
                            results.push((p.clone(), response.status_code, response.content_length, redirect.clone()));

                            // 打印结果
                            match response.status_code {
                                200..=299 => {
                                    println!("[+] [{}] /{} ({} bytes)", response.status_code, p, response.content_length);
                                }
                                300..=399 => {
                                    println!("[*] [{}] /{} -> {}", response.status_code, p, redirect);
                                }
                                401 | 403 => {
                                    println!("[!] [{}] /{} (需要认证/禁止访问)", response.status_code, p);
                                }
                                _ => {}
                            }
                        }

                        // 打印进度
                        if current_count % 50 == 0 || current_count == total_paths {
                            let progress = (current_count as f64 / total_paths as f64) * 100.0;
                            let found = found_paths.lock().unwrap().len();
                            print!("\r[*] 扫描进度: {}/{} ({:.1}%)  发现: {}", current_count, total_paths, progress, found);
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
        let _ = handle.join();
    }

    let duration = start_time.elapsed();

    // 获取结果
    let results = found_paths.lock().unwrap().clone();

    // ============================================================
    // 输出扫描结果汇总
    // ============================================================
    println!("\n{}", "=".repeat(60));
    println!("[*] 扫描完成！耗时: {:.2} 秒", duration.as_secs_f64());
    println!("[*] 扫描路径总数: {}", total_paths);
    println!("[+] 发现有效路径: {} 个", results.len());

    if !results.is_empty() {
        println!("\n[*] 发现的路径列表:");
        println!("{}", "-".repeat(50));

        // 按状态码分组显示
        let mut by_status: HashMap<u32, Vec<&(String, u32, usize, String)>> = HashMap::new();
        for entry in &results {
            by_status.entry(entry.1).or_default().push(entry);
        }

        let mut statuses: Vec<u32> = by_status.keys().cloned().collect();
        statuses.sort();

        for status in statuses {
            println!("\n  状态码 {}:", status);
            if let Some(entries) = by_status.get(&status) {
                for entry in entries {
                    let extra = if !entry.3.is_empty() {
                        format!(" -> {}", entry.3)
                    } else {
                        String::new()
                    };
                    println!("    /{}  ({} bytes){}", entry.0, entry.2, extra);
                }
            }
        }
    }

    results
}

// ============================================================
// 主函数
// ============================================================
fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        println!("用法: {} <目标URL> [字典文件] [线程数] [超时时间]", args[0]);
        println!("示例: {} http://127.0.0.1", args[0]);
        println!("      {} http://example.com wordlist.txt 30", args[0]);
        std::process::exit(1);
    }

    let base_url = &args[1];
    let wordlist_file = args.get(2).map(|s| s.as_str());
    let thread_count: usize = args.get(3)
        .and_then(|s| s.parse().ok())
        .unwrap_or(20);
    let timeout_secs: u64 = args.get(4)
        .and_then(|s| s.parse().ok())
        .unwrap_or(10);

    // 验证 URL 格式
    if !base_url.starts_with("http://") && !base_url.starts_with("https://") {
        println!("[!] 错误：URL 必须以 http:// 或 https:// 开头");
        std::process::exit(1);
    }

    // 参数检查
    if thread_count < 1 || thread_count > 200 {
        println!("[!] 错误：线程数应在 1-200 之间");
        std::process::exit(1);
    }

    let timeout = Duration::from_secs(timeout_secs);

    // 加载字典
    let wordlist = if let Some(file) = wordlist_file {
        match load_wordlist(file) {
            Ok(list) => {
                println!("[*] 已从字典文件加载 {} 个路径", list.len());
                list
            }
            Err(e) => {
                println!("[!] 加载字典文件失败: {}", e);
                println!("[*] 将使用内置字典");
                DEFAULT_WORDLIST.iter().map(|s| s.to_string()).collect()
            }
        }
    } else {
        println!("[*] 使用内置字典");
        DEFAULT_WORDLIST.iter().map(|s| s.to_string()).collect()
    };

    if wordlist.is_empty() {
        println!("[!] 错误：字典为空");
        std::process::exit(1);
    }

    // 执行目录爆破
    dir_brute(base_url, wordlist, thread_count, timeout);
}
