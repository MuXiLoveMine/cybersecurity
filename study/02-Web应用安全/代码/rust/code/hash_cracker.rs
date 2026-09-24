// ============================================================
// 哈希破解工具 (Hash Cracker)
// ============================================================
//
// 【原理说明】
// 哈希破解是密码学和安全测试中的常见技术，通过字典攻击（Dictionary Attack）
// 或暴力破解（Brute Force）的方式，尝试找到哈希值对应的原始明文。
//
// 本工具支持以下哈希算法：
//   - MD5:   128位哈希，已被证明不安全，常用于旧系统
//   - SHA1:  160位哈希，已被证明存在碰撞攻击，逐渐被淘汰
//   - SHA256: 256位哈希，当前主流安全哈希算法
//
// 【攻击方式】
//   字典攻击：使用预先准备的密码字典，逐一计算哈希并与目标比较
//   优点：速度快、针对性强
//   缺点：只能破解字典中包含的密码
//
// 【防御方法】
//   1. 使用强密码（足够长、包含多种字符）
//   2. 使用 salt 加盐哈希
//   3. 使用 bcrypt/scrypt/Argon2 等慢哈希算法
//   4. 定期更换密码
//
// 【编译运行】
//   rustc hash_cracker.rs && ./hash_cracker <哈希值> <哈希类型> [字典文件]
//
// 【使用方法】
//   hash_cracker <哈希值> <哈希类型> [字典文件]
//
// 【参数说明】
//   哈希值    - 必填，要破解的哈希字符串（十六进制格式）
//   哈希类型  - 必填，md5 / sha1 / sha256
//   字典文件  - 可选，密码字典文件路径，每行一个密码
//               不指定则使用内置的弱密码字典
//
// 【示例】
//   hash_cracker e10adc3949ba59abbe56e057f20f883e md5
//   hash_cracker 7c4a8d09ca3762af61e59520943dc26494f8941b sha1
//   hash_cracker 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8 sha256 wordlist.txt
//
// 【说明】
//   本工具手动实现了 MD5、SHA1、SHA256 算法，无需外部依赖，
//   便于学习哈希算法的底层原理。实际生产环境建议使用成熟的
//   密码学库如 ring、rust-crypto 等。
//
// 【免责声明】
//   本工具仅供学习和授权测试使用，禁止用于非法破解他人密码。
//   使用本工具请遵守当地法律法规，违者后果自负。
// ============================================================

use std::env;          // 命令行参数
use std::fs::File;     // 文件操作
use std::io::{BufRead, BufReader};  // 缓冲读取

// ============================================================
// 内置弱密码字典（常见弱密码）
// ============================================================
const DEFAULT_WORDLIST: &[&str] = &[
    "123456", "password", "12345678", "qwerty", "123456789",
    "12345", "1234", "111111", "1234567", "dragon",
    "123123", "baseball", "iloveyou", "trustno1", "sunshine",
    "princess", "admin", "welcome", "shadow", "superman",
    "michael", "football", "hello", "freedom", "whatever",
    "qazwsx", "monkey", "letmein", "654321", "password1",
    "abc123", "passw0rd", "test", "test123", "guest",
    "root", "toor", "master", "admin123", "administrator",
    "love", "sex", "secret", "god", "sex",
    "123qwe", "qwe123", "asdfgh", "zxcvbn", "000000",
    "555555", "666666", "888888", "123321", "123abc",
    "abc", "123", "a", "1", "testtest",
    "changeme", "default", "system", "server", "mysql",
];

// ============================================================
// MD5 哈希算法实现
// ============================================================
// MD5 消息摘要算法，输出 128 位（16 字节）哈希值
// 参考 RFC 1321 标准
fn md5(message: &[u8]) -> [u8; 16] {
    // 初始化变量（小端序）
    let mut a0: u32 = 0x67452301;
    let mut b0: u32 = 0xefcdab89;
    let mut c0: u32 = 0x98badcfe;
    let mut d0: u32 = 0x10325476;

    // 填充消息
    let mut padded = message.to_vec();
    let original_len_bits = (message.len() as u64) * 8;

    // 追加 0x80
    padded.push(0x80);

    // 填充 0 直到长度 mod 64 == 56
    while padded.len() % 64 != 56 {
        padded.push(0);
    }

    // 追加原始长度（小端序，64位）
    padded.extend_from_slice(&original_len_bits.to_le_bytes());

    // 正弦函数常量表（64个元素）
    let k: [u32; 64] = [
        0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
        0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
        0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
        0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
        0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
        0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
        0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
        0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
        0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
        0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
        0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
        0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
        0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
        0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
        0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
        0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
    ];

    // 每轮左移量
    let s: [u32; 64] = [
        7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,
        5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,
        4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,
        6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,
    ];

    // 处理每个 512 位（64 字节）的块
    for chunk in padded.chunks(64) {
        // 将块分解为 16 个 32 位小端序字
        let mut m = [0u32; 16];
        for i in 0..16 {
            m[i] = u32::from_le_bytes([
                chunk[i * 4],
                chunk[i * 4 + 1],
                chunk[i * 4 + 2],
                chunk[i * 4 + 3],
            ]);
        }

        let mut a = a0;
        let mut b = b0;
        let mut c = c0;
        let mut d = d0;

        // 64 轮操作
        for i in 0..64 {
            let (f, g): (u32, u32) = match i {
                0..=15 => ((b & c) | (!b & d), i as u32),
                16..=31 => ((d & b) | (!d & c), ((5 * i + 1) % 16) as u32),
                32..=47 => (b ^ c ^ d, ((3 * i + 5) % 16) as u32),
                _ => (c ^ (b | !d), ((7 * i) % 16) as u32),
            };

            let temp = d;
            d = c;
            c = b;
            b = b.wrapping_add(
                (a.wrapping_add(f)
                    .wrapping_add(k[i])
                    .wrapping_add(m[g as usize]))
                .rotate_left(s[i])
            );
            a = temp;
        }

        a0 = a0.wrapping_add(a);
        b0 = b0.wrapping_add(b);
        c0 = c0.wrapping_add(c);
        d0 = d0.wrapping_add(d);
    }

    // 拼接结果（小端序）
    let mut result = [0u8; 16];
    result[0..4].copy_from_slice(&a0.to_le_bytes());
    result[4..8].copy_from_slice(&b0.to_le_bytes());
    result[8..12].copy_from_slice(&c0.to_le_bytes());
    result[12..16].copy_from_slice(&d0.to_le_bytes());

    result
}

// ============================================================
// SHA1 哈希算法实现
// ============================================================
// SHA1 安全哈希算法，输出 160 位（20 字节）哈希值
// 参考 RFC 3174 标准
fn sha1(message: &[u8]) -> [u8; 20] {
    // 初始化哈希值
    let mut h0: u32 = 0x67452301;
    let mut h1: u32 = 0xefcdab89;
    let mut h2: u32 = 0x98badcfe;
    let mut h3: u32 = 0x10325476;
    let mut h4: u32 = 0xc3d2e1f0;

    // 填充消息
    let mut padded = message.to_vec();
    let original_len_bits = (message.len() as u64) * 8;

    padded.push(0x80);
    while padded.len() % 64 != 56 {
        padded.push(0);
    }
    padded.extend_from_slice(&original_len_bits.to_be_bytes());

    // 处理每个 512 位块
    for chunk in padded.chunks(64) {
        // 扩展为 80 个 32 位字
        let mut w = [0u32; 80];
        for i in 0..16 {
            w[i] = u32::from_be_bytes([
                chunk[i * 4],
                chunk[i * 4 + 1],
                chunk[i * 4 + 2],
                chunk[i * 4 + 3],
            ]);
        }
        for i in 16..80 {
            w[i] = (w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16]).rotate_left(1);
        }

        let mut a = h0;
        let mut b = h1;
        let mut c = h2;
        let mut d = h3;
        let mut e = h4;

        // 80 轮操作
        for i in 0..80 {
            let (f, k): (u32, u32) = match i {
                0..=19 => ((b & c) | (!b & d), 0x5a827999),
                20..=39 => (b ^ c ^ d, 0x6ed9eba1),
                40..=59 => ((b & c) | (b & d) | (c & d), 0x8f1bbcdc),
                _ => (b ^ c ^ d, 0xca62c1d6),
            };

            let temp = a.rotate_left(5)
                .wrapping_add(f)
                .wrapping_add(e)
                .wrapping_add(k)
                .wrapping_add(w[i]);

            e = d;
            d = c;
            c = b.rotate_left(30);
            b = a;
            a = temp;
        }

        h0 = h0.wrapping_add(a);
        h1 = h1.wrapping_add(b);
        h2 = h2.wrapping_add(c);
        h3 = h3.wrapping_add(d);
        h4 = h4.wrapping_add(e);
    }

    // 拼接结果（大端序）
    let mut result = [0u8; 20];
    result[0..4].copy_from_slice(&h0.to_be_bytes());
    result[4..8].copy_from_slice(&h1.to_be_bytes());
    result[8..12].copy_from_slice(&h2.to_be_bytes());
    result[12..16].copy_from_slice(&h3.to_be_bytes());
    result[16..20].copy_from_slice(&h4.to_be_bytes());

    result
}

// ============================================================
// SHA256 哈希算法实现
// ============================================================
// SHA256 安全哈希算法，输出 256 位（32 字节）哈希值
// 参考 FIPS 180-4 标准
fn sha256(message: &[u8]) -> [u8; 32] {
    // 初始化哈希值（前 8 个素数平方根的小数部分）
    let mut h: [u32; 8] = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ];

    // 64 个常量（前 64 个素数立方根的小数部分）
    let k: [u32; 64] = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
        0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
        0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
        0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
        0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
        0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
    ];

    // 填充消息
    let mut padded = message.to_vec();
    let original_len_bits = (message.len() as u64) * 8;

    padded.push(0x80);
    while padded.len() % 64 != 56 {
        padded.push(0);
    }
    padded.extend_from_slice(&original_len_bits.to_be_bytes());

    // 处理每个 512 位块
    for chunk in padded.chunks(64) {
        // 消息调度：扩展为 64 个 32 位字
        let mut w = [0u32; 64];
        for i in 0..16 {
            w[i] = u32::from_be_bytes([
                chunk[i * 4],
                chunk[i * 4 + 1],
                chunk[i * 4 + 2],
                chunk[i * 4 + 3],
            ]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16]
                .wrapping_add(s0)
                .wrapping_add(w[i - 7])
                .wrapping_add(s1);
        }

        // 初始化工作变量
        let mut a = h[0];
        let mut b = h[1];
        let mut c = h[2];
        let mut d = h[3];
        let mut e = h[4];
        let mut f = h[5];
        let mut g = h[6];
        let mut hh = h[7];

        // 64 轮压缩函数
        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ (!e & g);
            let temp1 = hh
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(k[i])
                .wrapping_add(w[i]);

            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let temp2 = s0.wrapping_add(maj);

            hh = g;
            g = f;
            f = e;
            e = d.wrapping_add(temp1);
            d = c;
            c = b;
            b = a;
            a = temp1.wrapping_add(temp2);
        }

        // 更新哈希值
        h[0] = h[0].wrapping_add(a);
        h[1] = h[1].wrapping_add(b);
        h[2] = h[2].wrapping_add(c);
        h[3] = h[3].wrapping_add(d);
        h[4] = h[4].wrapping_add(e);
        h[5] = h[5].wrapping_add(f);
        h[6] = h[6].wrapping_add(g);
        h[7] = h[7].wrapping_add(hh);
    }

    // 拼接结果（大端序）
    let mut result = [0u8; 32];
    for i in 0..8 {
        result[i * 4..(i + 1) * 4].copy_from_slice(&h[i].to_be_bytes());
    }

    result
}

// ============================================================
// 将字节数组转换为十六进制字符串
// ============================================================
fn to_hex(bytes: &[u8]) -> String {
    bytes.iter()
        .map(|b| format!("{:02x}", b))
        .collect()
}

// ============================================================
// 计算指定类型的哈希值
// ============================================================
fn compute_hash(password: &str, hash_type: &str) -> String {
    match hash_type.to_lowercase().as_str() {
        "md5" => to_hex(&md5(password.as_bytes())),
        "sha1" => to_hex(&sha1(password.as_bytes())),
        "sha256" => to_hex(&sha256(password.as_bytes())),
        _ => String::new(),
    }
}

// ============================================================
// 加载字典文件
// ============================================================
fn load_wordlist(file_path: &str) -> Result<Vec<String>, String> {
    let file = File::open(file_path).map_err(|e| format!("打开文件失败: {}", e))?;
    let reader = BufReader::new(file);
    let mut passwords = Vec::new();

    for line in reader.lines() {
        let line = line.map_err(|e| format!("读取文件失败: {}", e))?;
        let password = line.trim().to_string();
        if !password.is_empty() && !password.starts_with('#') {
            passwords.push(password);
        }
    }

    Ok(passwords)
}

// ============================================================
// 哈希破解主函数
// ============================================================
fn crack_hash(target_hash: &str, hash_type: &str, wordlist: Vec<String>) -> Option<String> {
    let target = target_hash.to_lowercase();
    let total = wordlist.len();

    println!("\n[*] 开始哈希破解");
    println!("[*] 目标哈希: {}", target_hash);
    println!("[*] 哈希类型: {}", hash_type.to_uppercase());
    println!("[*] 字典大小: {} 个密码", total);
    println!("{}", "=".repeat(60));

    let start_time = std::time::Instant::now();
    let mut found: Option<String> = None;
    let mut tried = 0;

    // 遍历字典逐一尝试
    for password in &wordlist {
        tried += 1;
        let hash = compute_hash(password, hash_type);

        if hash == target {
            found = Some(password.clone());
            break;
        }

        // 每 1000 个打印一次进度
        if tried % 1000 == 0 {
            let progress = (tried as f64 / total as f64) * 100.0;
            print!("\r[*] 已尝试: {}/{} ({:.1}%)", tried, total, progress);
            use std::io::Write;
            std::io::stdout().flush().unwrap();
        }
    }

    let duration = start_time.elapsed();
    let speed = if duration.as_secs_f64() > 0.0 {
        tried as f64 / duration.as_secs_f64()
    } else {
        tried as f64
    };

    println!("\n{}", "=".repeat(60));
    println!("[*] 破解完成！耗时: {:.2} 秒", duration.as_secs_f64());
    println!("[*] 尝试密码数: {}", tried);
    println!("[*] 破解速度: {:.0} 密码/秒", speed);

    match &found {
        Some(password) => {
            println!("\n[+] 破解成功！");
            println!("[+] 原始密码: {}", password);
            println!("[+] 哈希值: {}", target_hash);
        }
        None => {
            println!("\n[-] 破解失败");
            println!("[-] 字典中未找到匹配的密码");
            println!("[-] 建议：尝试更大的字典或使用暴力破解");
        }
    }

    found
}

// ============================================================
// 主函数
// ============================================================
fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 3 {
        println!("用法: {} <哈希值> <哈希类型> [字典文件]", args[0]);
        println!("  哈希类型: md5 / sha1 / sha256");
        println!("示例: {} e10adc3949ba59abbe56e057f20f883e md5", args[0]);
        println!("      {} 7c4a8d09ca3762af61e59520943dc26494f8941b sha1", args[0]);
        println!("      {} <hash> sha256 wordlist.txt", args[0]);
        std::process::exit(1);
    }

    let target_hash = &args[1];
    let hash_type = &args[2].to_lowercase();

    // 验证哈希类型
    match hash_type.as_str() {
        "md5" | "sha1" | "sha256" => {}
        _ => {
            println!("[!] 错误：不支持的哈希类型 '{}'", hash_type);
            println!("    支持的类型: md5, sha1, sha256");
            std::process::exit(1);
        }
    }

    // 验证哈希长度
    let expected_len = match hash_type.as_str() {
        "md5" => 32,
        "sha1" => 40,
        "sha256" => 64,
        _ => 0,
    };

    if target_hash.len() != expected_len {
        println!("[!] 警告：哈希值长度不正确");
        println!("    {} 哈希应为 {} 个十六进制字符", hash_type.to_uppercase(), expected_len);
        println!("    当前长度: {} 个字符", target_hash.len());
    }

    // 验证是否为有效的十六进制字符串
    if !target_hash.chars().all(|c| c.is_ascii_hexdigit()) {
        println!("[!] 错误：哈希值包含非十六进制字符");
        std::process::exit(1);
    }

    // 加载字典
    let wordlist = if let Some(file) = args.get(3) {
        match load_wordlist(file) {
            Ok(list) => {
                println!("[*] 已从字典文件加载 {} 个密码", list.len());
                list
            }
            Err(e) => {
                println!("[!] 加载字典文件失败: {}", e);
                println!("[*] 将使用内置字典");
                DEFAULT_WORDLIST.iter().map(|s| s.to_string()).collect()
            }
        }
    } else {
        println!("[*] 使用内置字典（{} 个常见弱密码）", DEFAULT_WORDLIST.len());
        DEFAULT_WORDLIST.iter().map(|s| s.to_string()).collect()
    };

    if wordlist.is_empty() {
        println!("[!] 错误：字典为空");
        std::process::exit(1);
    }

    // 执行破解
    crack_hash(target_hash, hash_type, wordlist);
}
