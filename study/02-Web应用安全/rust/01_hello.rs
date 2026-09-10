// ============================================================
// 01_hello.rs - Rust 基础语法示例
// 编译运行：rustc 01_hello.rs && ./01_hello
// ============================================================

fn main() {
    // --------------------------------------------------------
    // 1. Hello World
    // --------------------------------------------------------
    println!("=== Hello World ===");
    println!("Hello, Rust!");
    println!("你好，Rust！");
    println!();

    // --------------------------------------------------------
    // 2. 变量（let / mut）
    // --------------------------------------------------------
    println!("=== 变量 ===");

    // 不可变变量（默认）
    let x = 5;
    println!("不可变变量 x = {}", x);
    // x = 6;  // 错误：不能修改不可变变量

    // 可变变量（mut）
    let mut y = 10;
    println!("可变变量 y = {}", y);
    y = 20;
    println!("修改后 y = {}", y);

    // 变量遮蔽（Shadowing）
    let z = 5;
    let z = z + 1;          // 遮蔽旧变量，值为 6
    let z = z * 2;          // 再次遮蔽，值为 12
    println!("变量遮蔽 z = {}", z);

    // 遮蔽可以改变类型
    let spaces = "   ";
    let spaces = spaces.len();
    println!("空格数 = {}", spaces);
    println!();

    // --------------------------------------------------------
    // 3. 常量
    // --------------------------------------------------------
    println!("=== 常量 ===");

    const MAX_POINTS: u32 = 100_000;
    const PI: f64 = 3.14159265358979;
    const APP_NAME: &str = "RustDemo";

    println!("MAX_POINTS = {}", MAX_POINTS);
    println!("PI = {}", PI);
    println!("APP_NAME = {}", APP_NAME);
    println!();

    // --------------------------------------------------------
    // 4. 数据类型 - 标量类型
    // --------------------------------------------------------
    println!("=== 标量类型 ===");

    // 整数类型
    let a: i32 = 10;            // 有符号 32 位整数（默认）
    let b: u64 = 100;           // 无符号 64 位整数
    let c: isize = 200;         // 平台相关有符号整数
    let d: usize = 300;         // 平台相关无符号整数
    let hex = 0xff;             // 十六进制
    let oct = 0o77;             // 八进制
    let bin = 0b1010;           // 二进制
    let byte = b'A';            // 字节（u8）

    println!("i32: a = {}", a);
    println!("u64: b = {}", b);
    println!("isize: c = {}", c);
    println!("usize: d = {}", d);
    println!("十六进制: 0xff = {}", hex);
    println!("八进制: 0o77 = {}", oct);
    println!("二进制: 0b1010 = {}", bin);
    println!("字节: b'A' = {}", byte);

    // 浮点数类型
    let e: f32 = 3.14;          // 单精度浮点数
    let f: f64 = 2.71828;       // 双精度浮点数（默认）
    println!("f32: e = {}", e);
    println!("f64: f = {}", f);

    // 布尔类型
    let g: bool = true;
    let h: bool = false;
    println!("bool: g = {}, h = {}", g, h);

    // 字符类型（Unicode，4 字节）
    let i: char = 'R';
    let j: char = '字';
    let k: char = '😀';
    println!("char: i = {}, j = {}, k = {}", i, j, k);
    println!();

    // --------------------------------------------------------
    // 5. 数据类型 - 复合类型
    // --------------------------------------------------------
    println!("=== 复合类型 ===");

    // 元组（Tuple）
    let tup: (i32, f64, char) = (500, 6.4, 'R');
    println!("元组: ({}, {}, {})", tup.0, tup.1, tup.2);

    // 元组解构
    let (x_tup, y_tup, z_tup) = tup;
    println!("解构: x={}, y={}, z={}", x_tup, y_tup, z_tup);

    // 数组（Array）- 长度固定，元素类型相同
    let arr: [i32; 5] = [1, 2, 3, 4, 5];
    println!("数组: [{}, {}, {}, {}, {}]", arr[0], arr[1], arr[2], arr[3], arr[4]);
    println!("数组长度: {}", arr.len());

    // 初始化为相同值
    let arr2 = [0; 5];   // [0, 0, 0, 0, 0]
    println!("初始化为0: {:?}", arr2);
    println!();

    // --------------------------------------------------------
    // 6. 类型推断
    // --------------------------------------------------------
    println!("=== 类型推断 ===");

    let num = 42;                // 推断为 i32
    let float_num = 3.14;        // 推断为 f64
    let flag = true;             // 推断为 bool
    let ch = 'a';                // 推断为 char
    let text = "hello";          // 推断为 &str

    println!("num = {} (推断为 i32)", num);
    println!("float_num = {} (推断为 f64)", float_num);
    println!("flag = {} (推断为 bool)", flag);
    println!("ch = {} (推断为 char)", ch);
    println!("text = {} (推断为 &str)", text);

    // 当无法推断时，需要手动标注类型
    let guess: u32 = "42".parse().expect("不是数字");
    println!("guess = {} (手动标注 u32)", guess);
    println!();

    // --------------------------------------------------------
    // 7. 类型转换
    // --------------------------------------------------------
    println!("=== 类型转换 ===");

    let int_val: i32 = 100;
    let float_val: f64 = int_val as f64;       // i32 -> f64
    println!("i32 -> f64: {} -> {}", int_val, float_val);

    let float_val2: f64 = 3.7;
    let int_val2: i32 = float_val2 as i32;     // f64 -> i32（截断小数）
    println!("f64 -> i32: {} -> {}", float_val2, int_val2);

    let byte_val: u8 = 255;
    let int_val3: i16 = byte_val as i16;       // u8 -> i16
    println!("u8 -> i16: {} -> {}", byte_val, int_val3);

    // 字符与整数转换
    let c_val: char = 'A';
    let c_code: u32 = c_val as u32;            // char -> u32
    println!("char -> u32: '{}' -> {}", c_val, c_code);
    println!();

    // --------------------------------------------------------
    // 8. 运算符
    // --------------------------------------------------------
    println!("=== 运算符 ===");

    // 算术运算符
    let add = 5 + 3;
    let sub = 5 - 3;
    let mul = 5 * 3;
    let div = 5 / 3;          // 整数除法：1
    let div_f = 5.0 / 3.0;    // 浮点除法：1.666...
    let rem = 5 % 3;          // 取余：2
    println!("加法: 5 + 3 = {}", add);
    println!("减法: 5 - 3 = {}", sub);
    println!("乘法: 5 * 3 = {}", mul);
    println!("整数除法: 5 / 3 = {}", div);
    println!("浮点除法: 5.0 / 3.0 = {}", div_f);
    println!("取余: 5 % 3 = {}", rem);

    // 赋值运算符
    let mut v = 10;
    v += 5;       // v = v + 5
    println!("v += 5 -> {}", v);
    v -= 3;
    println!("v -= 3 -> {}", v);
    v *= 2;
    println!("v *= 2 -> {}", v);
    v /= 4;
    println!("v /= 4 -> {}", v);
    v %= 3;
    println!("v %= 3 -> {}", v);

    // 比较运算符
    println!("5 > 3 = {}", 5 > 3);
    println!("5 < 3 = {}", 5 < 3);
    println!("5 == 5 = {}", 5 == 5);
    println!("5 != 3 = {}", 5 != 3);
    println!("5 >= 5 = {}", 5 >= 5);
    println!("5 <= 3 = {}", 5 <= 3);

    // 逻辑运算符
    println!("true && false = {}", true && false);
    println!("true || false = {}", true || false);
    println!("!true = {}", !true);

    // 位运算符
    println!("0b1010 & 0b1100 = {:04b}", 0b1010 & 0b1100);    // 按位与
    println!("0b1010 | 0b1100 = {:04b}", 0b1010 | 0b1100);    // 按位或
    println!("0b1010 ^ 0b1100 = {:04b}", 0b1010 ^ 0b1100);    // 按位异或
    println!("0b1010 << 2 = {:06b}", 0b1010 << 2);            // 左移
    println!("0b1010 >> 1 = {:04b}", 0b1010 >> 1);            // 右移

    println!();
    println!("=== 01_hello.rs 执行完毕 ===");
}
