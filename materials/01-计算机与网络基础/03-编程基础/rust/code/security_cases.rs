// security_cases.rs —— Rust 安全案例集
//
// 涵盖内容（均从安全工具开发和防御角度）：
//   案例 1：并发端口扫描器（std::net + 多线程）
//   案例 2：哈希校验工具（MD5/SHA1/SHA256）
//   案例 3：文件完整性检查
//   案例 4：安全随机数生成
//   案例 5：Rust 安全编码检查清单
//
// 编译运行：
//   rustc security_cases.rs -o security_cases
//   ./security_cases [案例编号]
//
// 重要提示：
//   - 本文件仅用于安全学习和工具开发实践
//   - 所有安全工具仅限在授权测试环境中使用
//   - 请遵守法律法规

use std::collections::HashSet;
use std::env;
use std::fs;
use std::io::{self, Read, Write};
use std::net::TcpStream;
use std::path::Path;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

// ============================================================
// 辅助函数
// ============================================================

fn print_section(title: &str) {
    println!();
    println!("============================================================");
    println!("  {}", title);
    println!("============================================================");
    println!();
}

fn print_subsection(title: &str) {
    println!();
    println!("  --- {} ---", title);
    println!();
}

fn print_safe(msg: &str) {
    println!("  ✅ {}", msg);
}

fn print_warn(msg: &str) {
    println!("  ⚠️  {}", msg);
}

fn print_danger(msg: &str) {
    println!("  🔴 {}", msg);
}

// ============================================================
// 案例 1：并发端口扫描器
// ============================================================

/// 扫描单个端口
fn scan_port(host: &str, port: u16, timeout: Duration) -> bool {
    match TcpStream::connect_timeout(
        &format!("{}:{}", host, port).parse().unwrap(),
        timeout,
    ) {
        Ok(_) => true,
        Err(_) => false,
    }
}

/// 多线程端口扫描器
fn port_scan(host: &str, start_port: u16, end_port: u16, threads: usize) -> Vec<u16> {
    let open_ports = Arc::new(Mutex::new(Vec::new()));
    let mut handles = vec![];

    // 计算每个线程负责的端口范围
    let total = (end_port - start_port + 1) as usize;
    let per_thread = (total + threads - 1) / threads;  // 向上取整

    for t in 0..threads {
        let host = host.to_string();
        let open_ports = Arc::clone(&open_ports);

        let start = start_port + (t * per_thread) as u16;
        let end = std::cmp::min(start + per_thread as u16 - 1, end_port);

        if start > end {
            continue;
        }

        let handle = thread::spawn(move || {
            for port in start..=end {
                if scan_port(&host, port, Duration::from_millis(500)) {
                    let mut ports = open_ports.lock().unwrap();
                    ports.push(port);
                }
            }
        });
        handles.push(handle);
    }

    // 等待所有线程完成
    for handle in handles {
        handle.join().unwrap();
    }

    // 排序并返回
    let mut result = open_ports.lock().unwrap().clone();
    result.sort();
    result
}

fn case_port_scanner() {
    print_section("【案例 1：并发端口扫描器】");

    println!("  Rust 非常适合开发高性能安全工具：");
    println!("    - 内存安全，没有 UAF/缓冲区溢出等问题");
    println!("    - 多线程安全，数据竞争编译期检查");
    println!("    - 性能接近 C/C++");
    println!("    - 单二进制部署方便");
    println!();

    print_subsection("1.1 扫描原理");

    println!("  使用 std::net::TcpStream 进行 TCP 连接扫描");
    println!("  连接成功 → 端口开放");
    println!("  连接失败/超时 → 端口关闭或被过滤");
    println!();
    println!("  多线程使用：");
    println!("    - std::thread 原生线程");
    println!("    - Arc<T> 原子引用计数（线程安全的共享指针）");
    println!("    - Mutex<T> 互斥锁（保护共享数据）");
    println!();

    print_safe("Rust 的并发安全保证：");
    println!("     Send / Sync trait 在编译期保证线程安全");
    println!("     数据竞争在编译期就被阻止了");

    print_subsection("1.2 扫描演示（本机常见端口）");

    let host = "127.0.0.1";
    let ports = vec![21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 8080];

    println!("  扫描目标: {}", host);
    println!("  扫描端口: {:?}", ports);
    println!("  超时: 500ms");
    println!();

    // 扫描这些常见端口
    let mut open: Vec<u16> = Vec::new();
    for &port in &ports {
        if scan_port(host, port, Duration::from_millis(500)) {
            open.push(port);
        }
    }

    if open.is_empty() {
        println!("  没有开放的端口（或扫描被防火墙阻止）");
    } else {
        println!("  开放的端口:");
        for port in &open {
            let service = match port {
                21 => "FTP",
                22 => "SSH",
                23 => "Telnet",
                25 => "SMTP",
                53 => "DNS",
                80 => "HTTP",
                110 => "POP3",
                143 => "IMAP",
                443 => "HTTPS",
                3306 => "MySQL",
                3389 => "RDP",
                8080 => "HTTP-Proxy",
                _ => "未知",
            };
            println!("    {} / tcp → {}", port, service);
        }
    }

    print_subsection("1.3 多线程扫描性能对比");

    println!("  并发扫描使用 Arc<Mutex<Vec<u16>>> 共享结果");
    println!("  Arc 是原子引用计数，跨线程安全共享");
    println!("  Mutex 提供互斥访问，保证线程安全");
    println!();

    println!("  代码结构:");
    println!("    let results = Arc::new(Mutex::new(Vec::new()));");
    println!("    for _ in 0..threads {");
    println!("        let results = Arc::clone(&results);");
    println!("        thread::spawn(move || {");
    println!("            // 扫描端口...");
    println!("            results.lock().unwrap().push(port);");
    println!("        });");
    println!("    }");
    println!();

    print_safe("Rust 中数据竞争是编译期错误！");
    println!("     你不可能写出有数据竞争的代码（安全 Rust 中）");

    print_subsection("1.4 使用建议");

    print_warn("端口扫描可能被视为攻击行为");
    println!("    仅限在授权的测试环境中使用");
    println!("    扫描前请确保有书面授权");
    println!("    控制扫描速率，避免对目标造成影响");
    println!();
    println!("  Rust 安全工具开发优势：");
    println!("    1. 内存安全 - 工具本身不会有内存漏洞");
    println!("    2. 高性能 - 接近 C/C++ 的速度");
    println!("    3. 单二进制 - 部署方便，无依赖");
    println!("    4. 跨平台 - Windows/Linux/macOS");
    println!("    5. 并发安全 - 多线程工具开发更可靠");
}

// ============================================================
// 案例 2：哈希校验工具
// ============================================================

/// 简单的 MD5 实现（用于教学，实际项目请使用成熟库）
/// 注意：这只是演示，生产环境请使用 ring、RustCrypto 等成熟库
fn simple_md5(message: &[u8]) -> [u8; 16] {
    // 这是一个简化的 MD5 实现说明
    // 实际项目中请使用成熟的密码学库
    // 如：use md5::{Md5, Digest};
    //      let hash = Md5::digest(message);

    // 为了示例能运行，我们用一个简单的哈希替代
    // 仅用于演示概念，不是真正的 MD5
    let mut hash: [u8; 16] = [0; 16];
    let mut state: [u32; 4] = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476];

    // 简化的哈希计算（仅用于演示结构）
    for (i, &byte) in message.iter().enumerate() {
        state[i % 4] = state[i % 4].wrapping_add(byte as u32);
        state[i % 4] = state[i % 4].rotate_left(3);
    }

    // 将 state 转为 16 字节
    for i in 0..4 {
        let bytes = state[i].to_le_bytes();
        hash[i * 4..i * 4 + 4].copy_from_slice(&bytes);
    }

    hash
}

/// SHA-256 演示（简化版本，实际请用成熟库）
fn simple_sha256(message: &[u8]) -> [u8; 32] {
    // 简化的哈希，仅用于演示
    // 实际项目请使用 sha2 crate 或 ring
    let mut hash: [u8; 32] = [0; 32];

    // 初始哈希值（SHA-256 的前 8 个素数立方根的小数部分）
    let mut h: [u32; 8] = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ];

    // 简化处理（仅演示结构，不是真正的 SHA-256）
    for (i, &byte) in message.iter().enumerate() {
        h[i % 8] = h[i % 8].wrapping_add(byte as u32);
        h[i % 8] = h[i % 8].rotate_left(7);
    }

    // 转为 32 字节
    for i in 0..8 {
        let bytes = h[i].to_be_bytes();
        hash[i * 4..i * 4 + 4].copy_from_slice(&bytes);
    }

    hash
}

/// 将字节数组转为十六进制字符串
fn bytes_to_hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{:02x}", b)).collect()
}

fn case_hash_tool() {
    print_section("【案例 2：哈希校验工具】");

    println!("  哈希函数在安全中用途广泛：");
    println!("    - 文件完整性校验");
    println!("    - 密码存储（加盐 + 慢哈希）");
    println!("    - 数字签名");
    println!("    - 消息认证码（MAC）");
    println!("    - 区块链");

    print_subsection("2.1 字符串哈希演示");

    let test_strings = vec![
        "",
        "a",
        "abc",
        "message digest",
        "The quick brown fox jumps over the lazy dog",
    ];

    println!("  注意：以下哈希为教学演示版本（非标准实现）");
    println!("  生产环境请使用成熟的密码学库（ring、RustCrypto 等）");
    println!();

    for s in &test_strings {
        let md5_hash = simple_md5(s.as_bytes());
        let sha256_hash = simple_sha256(s.as_bytes());

        println!("  输入: \"{}\"", s);
        println!("    MD5:    {}", bytes_to_hex(&md5_hash));
        println!("    SHA256: {}", bytes_to_hex(&sha256_hash));
        println!();
    }

    print_subsection("2.2 雪崩效应演示");

    println!("  雪崩效应：输入微小变化导致输出巨大变化");
    println!();

    let s1 = "Hello, World!";
    let s2 = "Hello, World?";  // 只改了一个字符

    let h1 = simple_sha256(s1.as_bytes());
    let h2 = simple_sha256(s2.as_bytes());

    println!("  s1 = \"{}\"", s1);
    println!("  s2 = \"{}\"", s2);
    println!("  (只有最后一个字符不同)");
    println!();
    println!("  SHA256(s1) = {}", bytes_to_hex(&h1));
    println!("  SHA256(s2) = {}", bytes_to_hex(&h2));
    println!();

    // 计算不同的位数
    let diff_bits: u32 = h1.iter().zip(h2.iter())
        .map(|(a, b)| (a ^ b).count_ones())
        .sum();
    println!("  不同的位数: {} / 256 ({:.1}%)",
        diff_bits,
        diff_bits as f64 / 256.0 * 100.0);

    print_subsection("2.3 文件哈希计算");

    println!("  计算文件哈希是安全工具的常见功能");
    println!();

    // 计算当前源文件自身的哈希
    let current_file = file!();
    match fs::read(current_file) {
        Ok(content) => {
            let md5 = simple_md5(&content);
            let sha256 = simple_sha256(&content);

            println!("  文件: {}", current_file);
            println!("  大小: {} 字节", content.len());
            println!("  MD5:    {}", bytes_to_hex(&md5));
            println!("  SHA256: {}", bytes_to_hex(&sha256));
        }
        Err(e) => {
            println!("  读取文件失败: {}", e);
        }
    }

    print_subsection("2.4 安全使用建议");

    println!("  ❌ 不安全的用法：");
    println!("    - 用 MD5 存储密码（已被破解，碰撞攻击可行）");
    println!("    - 用 SHA1 存储密码（已被破解）");
    println!("    - 用 SHA256/SHA512 直接存储密码（太快，可暴力破解）");
    println!("    - 不加盐的密码哈希");
    println!();

    println!("  ✅ 安全的用法：");
    println!("    - 密码存储：Argon2、bcrypt、PBKDF2（慢哈希算法）");
    println!("    - 文件完整性：SHA-256、SHA-3");
    println!("    - 消息认证：HMAC-SHA256");
    println!("    - 数字签名：Ed25519、ECDSA");
    println!();

    print_safe("Rust 密码学库推荐：");
    println!("     - ring：基于 BoringSSL 的高性能密码学库");
    println!("     - RustCrypto：纯 Rust 实现的密码学算法集合");
    println!("     - rustls：纯 Rust 的 TLS 实现");
    println!("     - sodiumoxide：libsodium 的 Rust 绑定");
}

// ============================================================
// 案例 3：文件完整性检查
// ============================================================

fn case_file_integrity() {
    print_section("【案例 3：文件完整性检查】");

    println!("  文件完整性检查用于检测文件是否被篡改。");
    println!("  常用场景：");
    println!("    - 入侵检测系统（IDS）");
    println!("    - 文件监控");
    println!("    - 软件发布校验");
    println!("    - 取证分析");

    print_subsection("3.1 文件元数据采集");

    // 检查当前源文件
    let filename = file!();
    let path = Path::new(filename);

    match fs::metadata(path) {
        Ok(meta) => {
            println!("  文件: {}", filename);
            println!("  大小: {} 字节", meta.len());
            println!("  是文件: {}", meta.is_file());
            println!("  是目录: {}", meta.is_dir());
            println!("  权限: {:?}", meta.permissions());

            #[cfg(unix)]
            {
                use std::os::unix::fs::MetadataExt;
                println!("  inode: {}", meta.ino());
                println!("  所有者 UID: {}", meta.uid());
                println!("  模式: {:o}", meta.mode());
            }

            match meta.modified() {
                Ok(time) => {
                    println!("  修改时间: {:?}", time);
                }
                Err(_) => println!("  修改时间: 不支持"),
            }

            match meta.created() {
                Ok(time) => println!("  创建时间: {:?}", time),
                Err(_) => println!("  创建时间: 不支持"),
            }
        }
        Err(e) => println!("  获取元数据失败: {}", e),
    }

    print_subsection("3.2 文件哈希校验");

    println!("  通过比较哈希值检测文件是否被篡改");
    println!();

    if let Ok(content) = fs::read(filename) {
        let hash = simple_sha256(&content);
        let hash_hex = bytes_to_hex(&hash);

        println!("  当前文件哈希:");
        println!("    SHA256: {}", hash_hex);
        println!();
        println!("  完整性校验流程：");
        println!("    1. 基线：在已知安全状态下计算文件哈希");
        println!("    2. 定期：重新计算文件哈希");
        println!("    3. 对比：如果哈希变化，说明文件可能被篡改");
        println!("    4. 告警：发现变化时触发告警");
    }

    print_subsection("3.3 常见文件篡改检测技术");

    println!("  1. 哈希校验（MD5/SHA1/SHA256）");
    println!("     - 优点：简单、快速、可靠");
    println!("     - 缺点：需要安全存储基线哈希");
    println!();

    println!("  2. 数字签名");
    println!("     - 优点：可验证来源和完整性");
    println!("     - 缺点：需要 PKI 基础设施");
    println!();

    println!("  3. HMAC（消息认证码）");
    println!("     - 优点：需要密钥才能验证");
    println!("     - 缺点：密钥管理");
    println!();

    println!("  4. 检查文件元数据");
    println!("     - 修改时间、大小、权限等");
    println!("     - 可作为辅助检测手段");
    println!();

    println!("  5. 监控文件系统事件");
    println!("     - inotify（Linux）/ ReadDirectoryChangesW（Windows）");
    println!("     - 实时检测文件变化");

    print_subsection("3.4 Rust 实现优势");

    print_safe("Rust 开发文件完整性工具的优势：");
    println!("     1. 内存安全 - 解析文件时不会有内存漏洞");
    println!("     2. 高性能 - 快速处理大文件");
    println!("     3. 跨平台 - 支持 Windows/Linux/macOS");
    println!("     4. 类型系统 - 减少逻辑错误");
    println!("     5. 零成本抽象 - 高级特性不影响性能");
}

// ============================================================
// 案例 4：安全随机数生成
// ============================================================

fn case_secure_random() {
    print_section("【案例 4：安全随机数生成】");

    println!("  安全随机数在密码学和安全中至关重要：");
    println!("    - 密钥生成");
    println!("    - Token 生成（Session、CSRF、密码重置）");
    println!("    - 盐值生成");
    println!("    - 随机 IV / nonce");
    println!("    - 验证码生成");
    println!();

    print_warn("使用不安全的随机数可能导致加密被破解！");

    print_subsection("4.1 不安全 vs 安全的随机数");

    println!("  ❌ 不安全的随机数生成器：");
    println!("    - rand::thread_rng()（普通用途，非密码学安全）");
    println!("    - 基于时间种子的 PRNG");
    println!("    - 自制的随机算法");
    println!("    - 可预测、可重现");
    println!();

    println!("  ✅ 安全的随机数生成器（CSPRNG）：");
    println!("    - rand::rngs::OsRng（操作系统提供的 CSPRNG）");
    println!("    - ring::rand::SystemRandom");
    println!("    - 密码学安全，不可预测");
    println!();

    print_subsection("4.2 标准库中的随机源");

    println!("  Rust 标准库本身不提供 CSPRNG，");
    println!("  但可以通过操作系统获取安全随机数：");
    println!();

    // 读取系统随机源
    match read_system_random(32) {
        Ok(bytes) => {
            println!("  系统随机数 (32 字节):");
            println!("    hex: {}", bytes_to_hex(&bytes));
            println!("    base64: {}", base64_encode(&bytes));
        }
        Err(e) => {
            println!("  读取系统随机数失败: {}", e);
        }
    }

    print_subsection("4.3 常见安全随机数用途");

    println!("  1. 生成 API Key / Token");
    println!("     - 32 字节随机数 → hex/base64 编码");
    println!("     - 足够的熵（256 位）防暴力破解");
    println!();

    // 生成 API Key 示例
    if let Ok(key_bytes) = read_system_random(32) {
        let api_key = format!("sk-{}", base64_encode_urlsafe(&key_bytes));
        println!("     示例 API Key: {}", api_key);
    }

    println!();
    println!("  2. 生成密码盐值");
    println!("     - 每个用户的密码使用不同的盐");
    println!("     - 防止彩虹表攻击");
    println!();

    if let Ok(salt) = read_system_random(16) {
        println!("     示例盐值 (16字节): {}", bytes_to_hex(&salt));
    }

    println!();
    println!("  3. 生成 CSRF Token");
    println!("  4. 生成验证码（注意：不能太容易预测）");
    println!("  5. 生成 nonce / IV（加密用）");

    print_subsection("4.4 安全随机数最佳实践");

    println!("  1. 安全敏感场景必须使用 CSPRNG");
    println!("     不要用普通的 rand 生成密钥、Token 等");
    println!();

    println!("  2. 不要自己实现随机数生成器");
    println!("     使用操作系统提供的或成熟的密码学库");
    println!();

    println!("  3. 随机数要有足够的熵");
    println!("     - 密钥：至少 256 位（32 字节）");
    println!("     - Token：至少 128 位（16 字节）");
    println!("     - 盐值：至少 128 位（16 字节）");
    println!();

    println!("  4. Rust 推荐库：");
    println!("     - rand crate + OsRng");
    println!("     - ring::rand::SystemRandom");
    println!("     - 不要用 thread_rng() 做密码学用途");

    print_safe("Rust 的 rand crate 安全分层清晰：");
    println!("     - rand::thread_rng() - 快速但非密码学安全");
    println!("     - rand::rngs::OsRng - 操作系统 CSPRNG，安全");
    println!("     类型系统帮助区分安全/不安全的 RNG");
}

/// 从系统随机源读取随机字节
/// 跨平台实现（简化版，实际项目请用 rand crate）
fn read_system_random(len: usize) -> io::Result<Vec<u8>> {
    // Unix 系统：/dev/urandom
    // Windows：BCryptGenRandom / CryptGenRandom
    // 这里用 /dev/urandom 作为示例（Unix 可用）
    // Windows 上可能失败，仅作演示

    #[cfg(unix)]
    {
        let mut file = fs::File::open("/dev/urandom")?;
        let mut buf = vec![0u8; len];
        file.read_exact(&mut buf)?;
        Ok(buf)
    }

    #[cfg(not(unix))]
    {
        // Windows 或其他平台：用一个伪随机代替（仅演示）
        // 实际项目请使用 rand crate
        use std::time::{SystemTime, UNIX_EPOCH};
        let mut buf = vec![0u8; len];
        let seed = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos() as u64;
        let mut state = seed;
        for byte in buf.iter_mut() {
            state = state.wrapping_mul(6364136223846793005);
            state = state.wrapping_add(1442695040888963407);
            *byte = (state >> 32) as u8;
        }
        Ok(buf)
    }
}

/// 简单的 base64 编码（不用外部依赖）
fn base64_encode(input: &[u8]) -> String {
    const CHARS: &[u8; 64] =
        b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let mut result = Vec::new();
    let mut i = 0;
    while i < input.len() {
        let b1 = input[i];
        let b2 = if i + 1 < input.len() { input[i + 1] } else { 0 };
        let b3 = if i + 2 < input.len() { input[i + 2] } else { 0 };

        result.push(CHARS[(b1 >> 2) as usize]);
        result.push(CHARS[(((b1 & 0x03) << 4) | (b2 >> 4)) as usize]);

        if i + 1 < input.len() {
            result.push(CHARS[(((b2 & 0x0f) << 2) | (b3 >> 6)) as usize]);
        } else {
            result.push(b'=');
        }

        if i + 2 < input.len() {
            result.push(CHARS[(b3 & 0x3f) as usize]);
        } else {
            result.push(b'=');
        }

        i += 3;
    }
    String::from_utf8(result).unwrap()
}

/// URL 安全的 base64 编码
fn base64_encode_urlsafe(input: &[u8]) -> String {
    base64_encode(input)
        .replace('+', "-")
        .replace('/', "_")
        .replace('=', "")
}

// ============================================================
// 案例 5：Rust 安全编码检查清单
// ============================================================

fn print_security_checklist() {
    print_section("【附：Rust 安全编码检查清单】");

    println!("  内存安全:");
    println!("    [ ] 优先使用安全 Rust，减少 unsafe 块");
    println!("    [ ] unsafe 块尽量小，有充分的安全证明注释");
    println!("    [ ] 数组访问优先使用 .get()（返回 Option）");
    println!("    [ ] 使用 Option 处理可能为空的值");
    println!("    [ ] 避免在生产代码中使用 unwrap()/expect()");
    println!("    [ ] 正确处理错误，不忽略 Result");
    println!();

    println!("  并发安全:");
    println!("    [ ] 优先使用消息传递（channel）而非共享状态");
    println!("    [ ] 共享状态使用 Mutex/RwLock 等同步原语");
    println!("    [ ] 多线程使用 Arc<T> 而非 Rc<T>");
    println!("    [ ] 不要在 unsafe 中做不安全的并发操作");
    println!();

    println!("  输入验证:");
    println!("    [ ] 所有外部输入都验证");
    println!("    [ ] 使用白名单验证，而非黑名单");
    println!("    [ ] 验证数据类型、长度、范围、格式");
    println!("    [ ] 反序列化外部数据使用安全格式（JSON/protobuf）");
    println!();

    println!("  依赖安全:");
    println!("    [ ] 定期运行 cargo audit 检查依赖漏洞");
    println!("    [ ] 及时更新有安全问题的依赖");
    println!("    [ ] 使用 cargo geiger 检查依赖中的 unsafe 使用");
    println!("    [ ] 评估新增依赖的安全性和维护状态");
    println!();

    println!("  代码质量:");
    println!("    [ ] 使用 cargo clippy 检查 lint");
    println!("    [ ] 使用 rustfmt 格式化代码");
    println!("    [ ] 编写单元测试和集成测试");
    println!("    [ ] 关键代码使用 Miri 检测未定义行为");
    println!("    [ ] 对输入处理代码进行模糊测试（fuzzing）");
    println!();

    println!("  密码学安全:");
    println!("    [ ] 使用成熟的密码学库，不要自己实现");
    println!("    [ ] 使用 CSPRNG（OsRng）生成安全敏感的随机数");
    println!("    [ ] 密码使用慢哈希（argon2、bcrypt、pbkdf2）");
    println!("    [ ] 不在代码中硬编码密钥和密码");
    println!("    [ ] 敏感数据用完后清零内存（zeroize crate）");
    println!();

    println!("  工具链:");
    println!("    [ ] cargo audit - 依赖漏洞审计");
    println!("    [ ] cargo clippy - 静态分析");
    println!("    [ ] cargo fmt - 代码格式化");
    println!("    [ ] cargo geiger - unsafe 检测");
    println!("    [ ] cargo fuzz - 模糊测试");
    println!("    [ ] cargo tarpaulin - 代码覆盖率");
    println!("    [ ] cargo outdated - 过时依赖检查");
}

// ============================================================
// 主函数
// ============================================================

fn main() {
    println!();
    println!("============================================================");
    println!("  Rust 安全案例集");
    println!("  Rust Security Cases");
    println!("============================================================");
    println!();
    println!("  本程序从安全工具开发角度演示 Rust 在安全领域的应用。");
    println!("  所有案例均用于学习研究，请在授权环境中使用。");

    // 获取案例编号
    let args: Vec<String> = env::args().collect();
    let case_num = if args.len() > 1 {
        args[1].parse::<i32>().unwrap_or(0)
    } else {
        0
    };

    match case_num {
        0 => {
            case_port_scanner();
            case_hash_tool();
            case_file_integrity();
            case_secure_random();
            print_security_checklist();
        }
        1 => case_port_scanner(),
        2 => case_hash_tool(),
        3 => case_file_integrity(),
        4 => case_secure_random(),
        5 => print_security_checklist(),
        _ => {
            println!();
            println!("  用法: security_cases [案例编号]");
            println!();
            println!("  案例:");
            println!("    1 = 并发端口扫描器");
            println!("    2 = 哈希校验工具");
            println!("    3 = 文件完整性检查");
            println!("    4 = 安全随机数生成");
            println!("    5 = 安全编码检查清单");
            println!("    0 或不指定 = 全部运行");
            return;
        }
    }

    println!();
    println!("============================================================");
    println!("  演示完成。Rust 是开发安全工具的优秀选择：");
    println!("  内存安全、高性能、并发安全、跨平台。");
    println!("  请遵守法律法规，仅在授权环境中进行安全测试。");
    println!("============================================================");
    println!();
}
