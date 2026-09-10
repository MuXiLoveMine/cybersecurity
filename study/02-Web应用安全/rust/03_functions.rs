// ============================================================
// 03_functions.rs - Rust 函数示例
// 编译运行：rustc 03_functions.rs && ./03_functions
// ============================================================

fn main() {
    // --------------------------------------------------------
    // 1. 函数定义与调用
    // --------------------------------------------------------
    println!("=== 函数定义与调用 ===");

    // 无参数无返回值的函数
    greet();

    // 调用带参数的函数
    print_sum(5, 3);
    print_sum(10, 20);
    println!();

    // --------------------------------------------------------
    // 2. 函数参数
    // --------------------------------------------------------
    println!("=== 函数参数 ===");

    // 基本类型参数（Copy 类型）
    let x = 5;
    let y = 10;
    print_values(x, y);
    println!("调用后 x = {}, y = {} (仍然有效，因为是 Copy)", x, y);

    // 引用参数（借用，不转移所有权）
    let s = String::from("hello");
    let len = calculate_length(&s);
    println!("字符串 '{}' 的长度是 {}", s, len);
    println!("调用后 s 仍然有效: {}", s);

    // 可变引用参数
    let mut s2 = String::from("hello");
    append_world(&mut s2);
    println!("追加后: {}", s2);
    println!();

    // --------------------------------------------------------
    // 3. 函数返回值
    // --------------------------------------------------------
    println!("=== 函数返回值 ===");

    // 表达式作为返回值（不需要 return）
    let sum = add(5, 3);
    println!("5 + 3 = {}", sum);

    let diff = subtract(10, 4);
    println!("10 - 4 = {}", diff);

    // 使用 return 提前返回
    let abs_val = abs(-5);
    println!("-5 的绝对值是 {}", abs_val);
    let abs_val2 = abs(10);
    println!("10 的绝对值是 {}", abs_val2);

    // 返回多个值（使用元组）
    let (quotient, remainder) = divide(10, 3);
    println!("10 / 3 = {} 余 {}", quotient, remainder);

    // 返回结构体
    let user = create_user(String::from("alice@example.com"), String::from("alice"));
    println!("用户: {} ({})", user.username, user.email);
    println!();

    // --------------------------------------------------------
    // 4. 语句与表达式
    // --------------------------------------------------------
    println!("=== 语句与表达式 ===");

    // 块是表达式，可以返回值
    let y = {
        let x = 3;           // 语句
        x + 1                // 表达式，没有分号，作为块的返回值
    };
    println!("y = {}", y);

    // if 表达式
    let number = 5;
    let result = if number > 0 { "正数" } else { "非正数" };
    println!("{} 是 {}", number, result);

    // loop 表达式
    let mut counter = 0;
    let result = loop {
        counter += 1;
        if counter == 5 {
            break counter * 2;
        }
    };
    println!("loop 表达式结果: {}", result);

    // match 表达式
    let grade = 'B';
    let score = match grade {
        'A' => 90,
        'B' => 80,
        'C' => 70,
        'D' => 60,
        _ => 0,
    };
    println!("等级 {} 对应分数 {}", grade, score);
    println!();

    // --------------------------------------------------------
    // 5. 表达式体函数
    // --------------------------------------------------------
    println!("=== 表达式体函数 ===");

    println!("平方: {}^2 = {}", 5, square(5));
    println!("立方: {}^3 = {}", 3, cube(3));
    println!("最大值: max({}, {}) = {}", 10, 20, max(10, 20));
    println!("最小值: min({}, {}) = {}", 10, 20, min(10, 20));
    println!();

    // --------------------------------------------------------
    // 6. 函数指针
    // --------------------------------------------------------
    println!("=== 函数指针 ===");

    // 将函数赋值给变量
    let op: fn(i32, i32) -> i32 = add;
    println!("通过函数指针调用: {}", op(5, 3));

    // 函数作为参数
    let result = apply(10, 20, add);
    println!("apply add: {}", result);
    let result = apply(10, 20, subtract);
    println!("apply subtract: {}", result);

    // 函数作为返回值
    let op = get_op("add");
    println!("get_op add: {}", op(5, 3));
    let op = get_op("sub");
    println!("get_op sub: {}", op(5, 3));
    println!();

    // --------------------------------------------------------
    // 7. 闭包（Closure）
    // --------------------------------------------------------
    println!("=== 闭包 ===");

    // 简单闭包
    let add_one = |x: i32| x + 1;
    println!("add_one(5) = {}", add_one(5));

    // 闭包捕获环境变量
    let factor = 2;
    let multiply = |x: i32| x * factor;
    println!("multiply(5) = {}", multiply(5));

    // 带多个参数的闭包
    let add_nums = |a: i32, b: i32| a + b;
    println!("add_nums(3, 4) = {}", add_nums(3, 4));

    // 闭包作为参数
    let nums = vec![1, 2, 3, 4, 5];
    let doubled: Vec<i32> = nums.iter().map(|x| x * 2).collect();
    println!("翻倍: {:?}", doubled);

    let filtered: Vec<i32> = nums.into_iter().filter(|x| x > &2).collect();
    println!("过滤 (>2): {:?}", filtered);

    println!();
    println!("=== 03_functions.rs 执行完毕 ===");
}

// ============================================================
// 函数定义
// ============================================================

/// 打印问候语
fn greet() {
    println!("Hello, Rust 函数！");
}

/// 打印两个数的和
fn print_sum(a: i32, b: i32) {
    println!("{} + {} = {}", a, b, a + b);
}

/// 打印两个值
fn print_values(x: i32, y: i32) {
    println!("x = {}, y = {}", x, y);
}

/// 计算字符串长度（借用，不转移所有权）
fn calculate_length(s: &String) -> usize {
    s.len()
} // s 离开作用域，但因为没有所有权，所以不会 drop

/// 向字符串追加内容（可变引用）
fn append_world(s: &mut String) {
    s.push_str(", world!");
}

/// 加法函数 - 表达式体函数
fn add(a: i32, b: i32) -> i32 {
    a + b    // 最后一个表达式就是返回值，不需要分号
}

/// 减法函数
fn subtract(a: i32, b: i32) -> i32 {
    a - b
}

/// 计算绝对值（使用 return 提前返回）
fn abs(x: i32) -> i32 {
    if x < 0 {
        return -x;    // 提前返回
    }
    x
}

/// 除法，返回商和余数（元组返回多个值）
fn divide(a: i32, b: i32) -> (i32, i32) {
    (a / b, a % b)
}

// 定义一个简单的结构体用于演示
struct User {
    username: String,
    email: String,
    sign_in_count: u64,
    active: bool,
}

/// 创建用户
fn create_user(email: String, username: String) -> User {
    User {
        email,        // 字段初始化简写
        username,
        active: true,
        sign_in_count: 1,
    }
}

/// 平方 - 表达式体函数（一行）
fn square(x: i32) -> i32 { x * x }

/// 立方 - 表达式体函数
fn cube(x: i32) -> i32 { x * x * x }

/// 最大值 - 表达式体函数
fn max(a: i32, b: i32) -> i32 { if a > b { a } else { b } }

/// 最小值 - 表达式体函数
fn min(a: i32, b: i32) -> i32 { if a < b { a } else { b } }

/// 函数作为参数
fn apply(a: i32, b: i32, f: fn(i32, i32) -> i32) -> i32 {
    f(a, b)
}

/// 函数作为返回值
fn get_op(name: &str) -> fn(i32, i32) -> i32 {
    match name {
        "add" => add,
        "sub" => subtract,
        _ => add,  // 默认返回 add
    }
}
