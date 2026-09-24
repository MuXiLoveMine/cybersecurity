// ============================================================
// 06_string.rs - Rust String 字符串操作示例
// 编译运行：rustc 06_string.rs && ./06_string
// ============================================================

fn main() {
    // --------------------------------------------------------
    // 1. 创建字符串
    // --------------------------------------------------------
    println!("=== 创建字符串 ===");

    // 空字符串
    let s1 = String::new();
    println!("空字符串: '{}'", s1);

    // 从字符串字面量创建（&str -> String）
    let s2 = "hello".to_string();
    println!("to_string: '{}'", s2);

    let s3 = String::from("hello, world");
    println!("String::from: '{}'", s3);

    // format! 宏
    let s4 = format!("{} + {} = {}", 1, 2, 3);
    println!("format!: '{}'", s4);

    // 从字符创建
    let chars = ['R', 'u', 's', 't'];
    let s5: String = chars.iter().collect();
    println!("从字符数组: '{}'", s5);

    // 重复
    let s6 = "ab".repeat(5);
    println!("repeat: '{}'", s6);
    println!();

    // --------------------------------------------------------
    // 2. 更新字符串
    // --------------------------------------------------------
    println!("=== 更新字符串 ===");

    // push_str - 追加字符串
    let mut s = String::from("foo");
    s.push_str("bar");
    println!("push_str: '{}'", s);

    // push - 追加字符
    s.push('!');
    println!("push: '{}'", s);

    // insert_str - 在指定位置插入字符串
    let mut s2 = String::from("Hello World");
    s2.insert_str(5, ", Beautiful");
    println!("insert_str: '{}'", s2);

    // insert - 在指定位置插入字符
    let mut s3 = String::from("Hello");
    s3.insert(3, 'L');
    println!("insert: '{}'", s3);

    // replace_range - 替换指定范围
    let mut s4 = String::from("Hello, World!");
    s4.replace_range(7..12, "Rust");
    println!("replace_range: '{}'", s4);

    // + 运算符（注意：会获取左操作数的所有权）
    let s5 = String::from("Hello, ");
    let s6 = String::from("World");
    let s7 = s5 + &s6;    // s5 的所有权被移动，s6 被借用
    println!("+ 运算: '{}'", s7);
    // println!("{}", s5); // 错误：s5 已被移动
    println!("s6 仍然有效: '{}'", s6);

    // += 运算符
    let mut s8 = String::from("Hello");
    s8 += ", Rust!";
    println!("+= 运算: '{}'", s8);
    println!();

    // --------------------------------------------------------
    // 3. 字符串长度
    // --------------------------------------------------------
    println!("=== 字符串长度 ===");

    let s1 = "hello";
    println!("'hello' 字节长度: {}", s1.len());
    println!("'hello' 字符数: {}", s1.chars().count());

    let s2 = "你好，Rust";
    println!("'你好，Rust' 字节长度: {}", s2.len());
    println!("'你好，Rust' 字符数: {}", s2.chars().count());

    // 判断是否为空
    println!("空字符串: '{}', is_empty: {}", "", "".is_empty());
    println!();

    // --------------------------------------------------------
    // 4. 字符访问与迭代
    // --------------------------------------------------------
    println!("=== 字符访问与迭代 ===");

    let s = "你好，Rust";

    // Rust 不支持用整数索引访问字符
    // let c = s[0];  // 错误！

    // chars() - 字符迭代器
    println!("chars() 迭代:");
    for c in s.chars() {
        print!("{} ", c);
    }
    println!();

    // bytes() - 字节迭代器
    println!("bytes() 前 6 个字节:");
    for b in s.bytes().take(6) {
        print!("{} ", b);
    }
    println!();

    // char_indices - 带字节位置的字符迭代
    println!("char_indices:");
    for (index, c) in s.char_indices() {
        println!("  字节位置 {}: {}", index, c);
    }

    // 获取第 n 个字符
    let nth_char = s.chars().nth(1);
    println!("第 2 个字符: {:?}", nth_char);
    println!();

    // --------------------------------------------------------
    // 5. 字符串切片
    // --------------------------------------------------------
    println!("=== 字符串切片 ===");

    let s = "Hello, World!";

    // 按字节切片（必须确保在字符边界上）
    let hello = &s[0..5];
    let world = &s[7..12];
    println!("[0..5]: '{}'", hello);
    println!("[7..12]: '{}'", world);

    // 省略起始或结束
    let from_start = &s[..5];
    let to_end = &s[7..];
    println!("[..5]: '{}'", from_start);
    println!("[7..]: '{}'", to_end);

    // 注意：UTF-8 字符串切片必须在字符边界上
    let chinese = "你好世界";
    // &chinese[0..2];  // 错误！'你' 占 3 字节，0..2 不在字符边界

    // 正确的中文切片（需要找到正确的字节位置）
    let first_char = &chinese[0..3];    // 第一个字符 "你"
    println!("中文切片 [0..3]: '{}'", first_char);
    println!();

    // --------------------------------------------------------
    // 6. 查找与包含
    // --------------------------------------------------------
    println!("=== 查找与包含 ===");

    let s = "Hello, World! Hello, Rust!";

    // contains - 是否包含
    println!("包含 'World': {}", s.contains("World"));
    println!("包含 'world': {}", s.contains("world"));  // 大小写敏感

    // starts_with / ends_with
    println!("以 'Hello' 开头: {}", s.starts_with("Hello"));
    println!("以 'Rust!' 结尾: {}", s.ends_with("Rust!"));

    // find - 查找第一个匹配的位置（返回 Option<usize>）
    match s.find("World") {
        Some(pos) => println!("'World' 首次出现位置: {}", pos),
        None => println!("未找到 'World'"),
    }

    match s.find("Python") {
        Some(pos) => println!("'Python' 位置: {}", pos),
        None => println!("未找到 'Python'"),
    }

    // rfind - 查找最后一个匹配的位置
    match s.rfind("Hello") {
        Some(pos) => println!("'Hello' 最后出现位置: {}", pos),
        None => println!("未找到"),
    }

    // find + 字符
    match s.find(',') {
        Some(pos) => println!("第一个逗号位置: {}", pos),
        None => println!("没有逗号"),
    }
    println!();

    // --------------------------------------------------------
    // 7. 替换
    // --------------------------------------------------------
    println!("=== 替换 ===");

    let s = "Hello, World! Hello, World!";

    // replace - 替换所有匹配
    let replaced = s.replace("World", "Rust");
    println!("替换所有: '{}'", replaced);

    // replacen - 替换前 n 个匹配
    let replaced_n = s.replacen("World", "Rust", 1);
    println!("替换第一个: '{}'", replaced_n);

    // to_lowercase / to_uppercase
    let s2 = "Hello, Rust!";
    println!("小写: '{}'", s2.to_lowercase());
    println!("大写: '{}'", s2.to_uppercase());
    println!();

    // --------------------------------------------------------
    // 8. 分割
    // --------------------------------------------------------
    println!("=== 分割 ===");

    let s = "apple,banana,orange,grape";

    // split - 按分隔符分割
    println!("split(','):");
    for part in s.split(',') {
        println!("  '{}'", part);
    }

    // split_whitespace - 按空白字符分割
    let s2 = "hello   world\tfoo\nbar";
    println!("split_whitespace:");
    for word in s2.split_whitespace() {
        println!("  '{}'", word);
    }

    // splitn - 分割为 n 份
    println!("splitn(',', 2):");
    for part in s.splitn(',', 2) {
        println!("  '{}'", part);
    }

    // lines - 按行分割
    let s3 = "第一行\n第二行\n第三行";
    println!("lines:");
    for line in s3.lines() {
        println!("  '{}'", line);
    }

    // 收集为 Vec<&str>
    let parts: Vec<&str> = s.split(',').collect();
    println!("收集为 Vec: {:?}", parts);
    println!();

    // --------------------------------------------------------
    // 9. 去除空白
    // --------------------------------------------------------
    println!("=== 去除空白 ===");

    let s = "   Hello, Rust!   ";
    println!("原始: '{}'", s);
    println!("trim: '{}'", s.trim());
    println!("trim_start: '{}'", s.trim_start());
    println!("trim_end: '{}'", s.trim_end());

    // 去除两端特定字符
    let s2 = "***Hello***";
    println!("trim_matches '*': '{}'", s2.trim_matches('*'));
    println!();

    // --------------------------------------------------------
    // 10. 字符串拼接
    // --------------------------------------------------------
    println!("=== 字符串拼接 ===");

    // 使用 format!（推荐，最灵活）
    let s1 = "Hello";
    let s2 = "World";
    let result = format!("{}, {}!", s1, s2);
    println!("format!: '{}'", result);

    // concat - 连接字符串切片数组
    let parts = ["Hello", " ", "Rust", "!"];
    let result = parts.concat();
    println!("concat: '{}'", result);

    // join - 用分隔符连接
    let words = ["apple", "banana", "orange"];
    let result = words.join(", ");
    println!("join: '{}'", result);
    println!();

    // --------------------------------------------------------
    // 11. 字符串与类型转换
    // --------------------------------------------------------
    println!("=== 类型转换 ===");

    // 数字转字符串
    let num = 42;
    let num_str = num.to_string();
    println!("数字转字符串: {} -> '{}'", num, num_str);

    let float_num = 3.14;
    let float_str = float_num.to_string();
    println!("浮点数转字符串: {} -> '{}'", float_num, float_str);

    // 字符串转数字
    let num_str = "123";
    match num_str.parse::<i32>() {
        Ok(n) => println!("字符串转 i32: '{}' -> {}", num_str, n),
        Err(e) => println!("解析失败: {}", e),
    }

    let float_str = "3.14";
    match float_str.parse::<f64>() {
        Ok(n) => println!("字符串转 f64: '{}' -> {}", float_str, n),
        Err(e) => println!("解析失败: {}", e),
    }

    // 解析失败的情况
    let invalid = "abc";
    match invalid.parse::<i32>() {
        Ok(n) => println!("解析成功: {}", n),
        Err(e) => println!("解析 'abc' 失败: {}", e),
    }
    println!();

    // --------------------------------------------------------
    // 12. String 与 &str
    // --------------------------------------------------------
    println!("=== String 与 &str ===");

    // String 自动解引用为 &str（Deref 强制转换）
    let s = String::from("hello");
    print_str(&s);    // &String 自动转为 &str

    // 获取 &str
    let slice: &str = &s[..];
    println!("slice: '{}'", slice);

    // 字面量就是 &str
    let literal: &str = "hello world";
    println!("字面量 &str: '{}'", literal);
    println!("长度: {}", literal.len());

    println!();
    println!("=== 06_string.rs 执行完毕 ===");
}

/// 接收 &str 参数的函数
fn print_str(s: &str) {
    println!("print_str: '{}'", s);
}
