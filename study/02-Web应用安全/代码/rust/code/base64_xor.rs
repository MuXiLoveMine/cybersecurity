// ============================================================
// Base64 / XOR 编解码工具
// ============================================================
//
// 【原理说明】
// 本工具集成了两种常见的编码/加密算法：
//
// 1. Base64 编码
//    - 原理：将二进制数据转换为 64 个可打印 ASCII 字符的表示方式
//    - 用途：常用于在文本协议中传输二进制数据（如邮件、HTTP）
//    - 注意：Base64 是编码而非加密，任何人都可以解码
//
// 2. XOR 加密/解密
//    - 原理：将明文与密钥进行按位异或运算，相同操作可解密
//    - 特点：对称加密，加密解密使用相同密钥
//    - 安全性：单字节密钥非常弱，仅用于学习和简单混淆
//    - 提示：当密钥长度与明文相同时，称为一次性密码本（One-Time Pad），
//           在理论上是不可破解的
//
// 【编译运行】
//   rustc base64_xor.rs && ./base64_xor <操作> <输入> [密钥/选项]
//
// 【使用方法】
//   base64_xor <操作> <输入内容> [密钥]
//
// 【操作类型】
//   b64enc      - Base64 编码
//   b64dec      - Base64 解码
//   xor         - XOR 加密/解密（需指定密钥）
//   xor-brute   - XOR 单字节密钥暴力破解
//
// 【参数说明】
//   操作        - 必填，操作类型（b64enc / b64dec / xor / xor-brute）
//   输入内容    - 必填，要处理的文本
//   密钥        - 可选，XOR 加密的密钥（xor 操作时必填）
//
// 【示例】
//   base64_xor b64enc "Hello, World!"
//   base64_xor b64dec "SGVsbG8sIFdvcmxkIQ=="
//   base64_xor xor "secret message" "mykey"
//   base64_xor xor-brute "KHOtwsbh"
//
// 【说明】
//   本工具手动实现了 Base64 和 XOR 算法，无需外部依赖，
//   便于学习编码和加密算法的底层原理。
//
// 【免责声明】
//   本工具仅供学习和授权测试使用。XOR 加密安全性极低，
//   请勿用于保护重要数据。实际应用请使用 AES 等标准加密算法。
// ============================================================

use std::env;          // 命令行参数
use std::process;      // 进程控制

// ============================================================
// Base64 编码表
// ============================================================
// 标准 Base64 字符表，共 64 个字符
const BASE64_CHARS: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

// ============================================================
// Base64 编码
// ============================================================
// 将字节数组编码为 Base64 字符串
// 参数：input - 输入字节数组
// 返回：Base64 编码后的字符串
fn base64_encode(input: &[u8]) -> String {
    let mut result = String::new();
    let len = input.len();

    // 每 3 个字节（24 位）为一组，编码为 4 个 Base64 字符
    for i in (0..len).step_by(3) {
        // 获取当前组的 3 个字节（不足时补 0）
        let b0 = input[i];
        let b1 = if i + 1 < len { input[i + 1] } else { 0 };
        let b2 = if i + 2 < len { input[i + 2] } else { 0 };

        // 将 3 个字节组合成 24 位整数
        let triple = ((b0 as u32) << 16) | ((b1 as u32) << 8) | (b2 as u32);

        // 拆分为 4 个 6 位索引
        let idx0 = ((triple >> 18) & 0x3F) as usize;
        let idx1 = ((triple >> 12) & 0x3F) as usize;
        let idx2 = ((triple >> 6) & 0x3F) as usize;
        let idx3 = (triple & 0x3F) as usize;

        // 根据索引查找 Base64 字符
        result.push(BASE64_CHARS[idx0] as char);
        result.push(BASE64_CHARS[idx1] as char);

        // 处理填充（= 符号）
        if i + 1 < len {
            result.push(BASE64_CHARS[idx2] as char);
        } else {
            result.push('=');  // 第二个填充字符
        }

        if i + 2 < len {
            result.push(BASE64_CHARS[idx3] as char);
        } else {
            result.push('=');  // 第一个填充字符
        }
    }

    result
}

// ============================================================
// Base64 解码
// ============================================================
// 将 Base64 字符串解码为字节数组
// 参数：input - Base64 编码的字符串
// 返回：解码后的字节数组（Result 类型，可能失败）
fn base64_decode(input: &str) -> Result<Vec<u8>, String> {
    // 移除空白字符
    let clean: Vec<char> = input.chars()
        .filter(|c| !c.is_whitespace())
        .collect();

    let len = clean.len();

    // 验证长度必须是 4 的倍数
    if len % 4 != 0 {
        return Err("Base64 字符串长度必须是 4 的倍数".to_string());
    }

    // 构建反向查找表（字符 -> 索引值）
    let mut char_to_idx = [0xFFu8; 256];
    for (i, &c) in BASE64_CHARS.iter().enumerate() {
        char_to_idx[c as usize] = i as u8;
    }

    let mut result = Vec::new();

    // 每 4 个字符为一组，解码为 3 个字节
    for i in (0..len).step_by(4) {
        // 获取 4 个字符的索引值
        let c0 = clean[i] as u8;
        let c1 = clean[i + 1] as u8;
        let c2 = clean[i + 2] as u8;
        let c3 = clean[i + 3] as u8;

        let idx0 = char_to_idx[c0 as usize];
        let idx1 = char_to_idx[c1 as usize];

        // 验证字符有效性
        if idx0 == 0xFF || idx1 == 0xFF {
            return Err(format!("无效的 Base64 字符: '{}' 或 '{}'", c0 as char, c1 as char));
        }

        // 第一个字节：前 6 位来自 c0，后 2 位来自 c1 的前 2 位
        let b0 = (idx0 << 2) | (idx1 >> 4);
        result.push(b0);

        // 第二个字符是填充符号则跳过
        if c2 == b'=' {
            break;
        }

        let idx2 = char_to_idx[c2 as usize];
        if idx2 == 0xFF {
            return Err(format!("无效的 Base64 字符: '{}'", c2 as char));
        }

        // 第二个字节：前 4 位来自 c1 的后 4 位，后 4 位来自 c2 的前 4 位
        let b1 = ((idx1 & 0x0F) << 4) | (idx2 >> 2);
        result.push(b1);

        // 第三个字符是填充符号则跳过
        if c3 == b'=' {
            break;
        }

        let idx3 = char_to_idx[c3 as usize];
        if idx3 == 0xFF {
            return Err(format!("无效的 Base64 字符: '{}'", c3 as char));
        }

        // 第三个字节：前 2 位来自 c2 的后 2 位，后 6 位来自 c3
        let b2 = ((idx2 & 0x03) << 6) | idx3;
        result.push(b2);
    }

    Ok(result)
}

// ============================================================
// XOR 加密/解密
// ============================================================
// XOR 是对称加密，加密和解密使用相同的操作
// 参数：
//   data - 明文或密文字节
//   key - 密钥字节（循环使用）
// 返回：加密/解密后的字节
fn xor_encrypt(data: &[u8], key: &[u8]) -> Vec<u8> {
    if key.is_empty() {
        return data.to_vec();
    }

    data.iter()
        .enumerate()
        .map(|(i, &byte)| byte ^ key[i % key.len()])
        .collect()
}

// ============================================================
// XOR 单字节密钥暴力破解
// ============================================================
// 通过字符频率分析尝试找出最可能的单字节密钥
// 参数：ciphertext - 密文字节
// 返回：最可能的明文和对应的密钥（以可打印字符比例评分）
fn xor_brute_single_byte(ciphertext: &[u8]) -> Vec<(u8, f64, String)> {
    let mut results = Vec::new();

    // 遍历所有 256 个可能的单字节密钥
    for key in 0..=255u8 {
        let decrypted: Vec<u8> = ciphertext.iter().map(|&b| b ^ key).collect();

        // 计算可打印字符比例（作为评分依据）
        let printable_count = decrypted.iter()
            .filter(|&&b| b >= 32 && b <= 126)  // 可打印 ASCII 范围
            .count();

        let score = printable_count as f64 / decrypted.len() as f64;

        // 只保留可打印字符比例较高的结果
        if score > 0.7 {
            let text = String::from_utf8_lossy(&decrypted).to_string();
            results.push((key, score, text));
        }
    }

    // 按评分从高到低排序
    results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

    results
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
// 从十六进制字符串解析字节数组
// ============================================================
fn from_hex(hex: &str) -> Result<Vec<u8>, String> {
    let hex = hex.trim().replace(" ", "").replace("0x", "");
    if hex.len() % 2 != 0 {
        return Err("十六进制字符串长度必须是偶数".to_string());
    }

    let mut bytes = Vec::new();
    for i in (0..hex.len()).step_by(2) {
        let byte = u8::from_str_radix(&hex[i..i + 2], 16)
            .map_err(|e| format!("无效的十六进制字符: {}", e))?;
        bytes.push(byte);
    }

    Ok(bytes)
}

// ============================================================
// 主函数
// ============================================================
fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 3 {
        println!("用法: {} <操作> <输入内容> [密钥/选项]", args[0]);
        println!();
        println!("操作类型:");
        println!("  b64enc      - Base64 编码");
        println!("  b64dec      - Base64 解码");
        println!("  xor         - XOR 加密/解密（需指定密钥）");
        println!("  xor-brute   - XOR 单字节密钥暴力破解");
        println!();
        println!("示例:");
        println!("  {} b64enc \"Hello, World!\"", args[0]);
        println!("  {} b64dec \"SGVsbG8sIFdvcmxkIQ==\"", args[0]);
        println!("  {} xor \"secret message\" \"mykey\"", args[0]);
        println!("  {} xor-brute \"KHOtwsbh\"", args[0]);
        process::exit(1);
    }

    let operation = &args[1].to_lowercase();
    let input = &args[2];

    match operation.as_str() {
        // ============================================================
        // Base64 编码
        // ============================================================
        "b64enc" | "base64-encode" => {
            println!("\n[*] Base64 编码");
            println!("{}", "=".repeat(50));
            println!("[*] 原始数据: {}", input);

            let encoded = base64_encode(input.as_bytes());

            println!("[+] 编码结果: {}", encoded);
            println!("[*] 原始长度: {} 字节", input.len());
            println!("[*] 编码长度: {} 字符", encoded.len());
        }

        // ============================================================
        // Base64 解码
        // ============================================================
        "b64dec" | "base64-decode" => {
            println!("\n[*] Base64 解码");
            println!("{}", "=".repeat(50));
            println!("[*] 编码数据: {}", input);

            match base64_decode(input) {
                Ok(decoded) => {
                    let text = String::from_utf8_lossy(&decoded);
                    println!("[+] 解码结果 (文本): {}", text);
                    println!("[+] 解码结果 (十六进制): {}", to_hex(&decoded));
                    println!("[*] 解码长度: {} 字节", decoded.len());
                }
                Err(e) => {
                    println!("[!] 解码失败: {}", e);
                    process::exit(1);
                }
            }
        }

        // ============================================================
        // XOR 加密/解密
        // ============================================================
        "xor" => {
            if args.len() < 4 {
                println!("[!] 错误：XOR 操作需要指定密钥");
                println!("    用法: {} xor <内容> <密钥>", args[0]);
                process::exit(1);
            }

            let key = &args[3];

            println!("\n[*] XOR 加密/解密");
            println!("{}", "=".repeat(50));
            println!("[*] 输入数据: {}", input);
            println!("[*] 密钥: {}", key);
            println!("[*] 密钥长度: {} 字节", key.len());

            let result = xor_encrypt(input.as_bytes(), key.as_bytes());

            println!("\n[+] 结果 (十六进制): {}", to_hex(&result));
            println!("[+] 结果 (Base64): {}", base64_encode(&result));

            // 尝试显示为文本（如果可打印）
            let printable = result.iter().all(|&b| b >= 32 && b <= 126);
            if printable {
                println!("[+] 结果 (文本): {}", String::from_utf8_lossy(&result));
            } else {
                println!("[*] 结果包含不可打印字符，已用十六进制和Base64表示");
            }

            // 验证：再次 XOR 应该得到原始数据
            let verify = xor_encrypt(&result, key.as_bytes());
            if verify == input.as_bytes() {
                println!("\n[*] 验证通过：再次 XOR 可恢复原始数据");
            }
        }

        // ============================================================
        // XOR 单字节密钥暴力破解
        // ============================================================
        "xor-brute" | "xor-crack" => {
            println!("\n[*] XOR 单字节密钥暴力破解");
            println!("{}", "=".repeat(50));
            println!("[*] 密文: {}", input);

            // 尝试将输入作为文本处理
            let ciphertext = input.as_bytes();

            println!("[*] 密文长度: {} 字节", ciphertext.len());
            println!("[*] 正在尝试所有 256 个可能的单字节密钥...");

            let results = xor_brute_single_byte(ciphertext);

            if results.is_empty() {
                println!("\n[-] 未找到高置信度的解密结果");
                println!("[-] 可能不是单字节 XOR 加密，或密文太短");
            } else {
                println!("\n[+] 最可能的结果（按可打印字符比例排序）：");
                println!("{}", "-".repeat(50));

                let top_n = std::cmp::min(10, results.len());
                for (i, (key, score, text)) in results.iter().take(top_n).enumerate() {
                    println!("\n  [{}] 密钥: 0x{:02x} ({}, 字符: '{}')",
                             i + 1, key, key,
                             if *key >= 32 && *key <= 126 { *key as char } else { '.' });
                    println!("      置信度: {:.1}%", score * 100.0);
                    println!("      明文: {}", text);
                }
            }

            println!("\n[*] 提示：");
            println!("    - 单字节 XOR 是最弱的加密方式，极易被破解");
            println!("    - 多字节密钥 XOR 则需要更复杂的分析（如 Kasiski 测试）");
            println!("    - 实际应用请使用 AES 等标准加密算法");
        }

        // ============================================================
        // 未知操作
        // ============================================================
        _ => {
            println!("[!] 错误：未知的操作类型 '{}'", operation);
            println!("    支持的操作: b64enc, b64dec, xor, xor-brute");
            process::exit(1);
        }
    }

    println!();
}
