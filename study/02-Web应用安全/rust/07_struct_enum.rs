// ============================================================
// 07_struct_enum.rs - Rust 结构体、枚举与方法示例
// 编译运行：rustc 07_struct_enum.rs && ./07_struct_enum
// ============================================================

fn main() {
    // --------------------------------------------------------
    // 1. 结构体定义与实例化
    // --------------------------------------------------------
    println!("=== 结构体定义与实例化 ===");

    // 定义结构体
    #[derive(Debug)]
    struct User {
        username: String,
        email: String,
        sign_in_count: u64,
        active: bool,
    }

    // 创建实例
    let user1 = User {
        email: String::from("alice@example.com"),
        username: String::from("alice"),
        active: true,
        sign_in_count: 1,
    };
    println!("用户1: {:?}", user1);
    println!("用户名: {}", user1.username);
    println!("邮箱: {}", user1.email);

    // 可变结构体
    let mut user2 = User {
        email: String::from("bob@example.com"),
        username: String::from("bob"),
        active: true,
        sign_in_count: 5,
    };
    user2.email = String::from("bob_new@example.com");
    println!("修改邮箱后: {}", user2.email);

    // 字段初始化简写
    fn build_user(email: String, username: String) -> User {
        User {
            email,        // 等价于 email: email
            username,     // 等价于 username: username
            active: true,
            sign_in_count: 1,
        }
    }
    let user3 = build_user(String::from("charlie@example.com"), String::from("charlie"));
    println!("build_user: {:?}", user3.username);

    // 结构体更新语法
    let user4 = User {
        email: String::from("david@example.com"),
        username: String::from("david"),
        ..user1    // 其余字段使用 user1 的值
    };
    println!("更新语法: username={}, active={}", user4.username, user4.active);
    println!();

    // --------------------------------------------------------
    // 2. 元组结构体
    // --------------------------------------------------------
    println!("=== 元组结构体 ===");

    #[derive(Debug)]
    struct Color(i32, i32, i32);

    #[derive(Debug)]
    struct Point(i32, i32, i32);

    let black = Color(0, 0, 0);
    let origin = Point(0, 0, 0);

    println!("Color: {:?}", black);
    println!("Point: {:?}", origin);
    println!("Color.0 = {}", black.0);

    // 解构
    let Color(r, g, b) = black;
    println!("RGB: {}, {}, {}", r, g, b);

    // 即使字段类型相同，不同元组结构体也是不同类型
    // let color: Color = origin;  // 错误：类型不匹配
    println!();

    // --------------------------------------------------------
    // 3. 单元结构体
    // --------------------------------------------------------
    println!("=== 单元结构体 ===");

    #[derive(Debug)]
    struct AlwaysEqual;

    let subject = AlwaysEqual;
    println!("单元结构体: {:?}", subject);
    println!();

    // --------------------------------------------------------
    // 4. 枚举定义
    // --------------------------------------------------------
    println!("=== 枚举定义 ===");

    // 简单枚举
    #[derive(Debug)]
    enum IpAddrKind {
        V4,
        V6,
    }

    let four = IpAddrKind::V4;
    let six = IpAddrKind::V6;
    println!("IPv4: {:?}", four);
    println!("IPv6: {:?}", six);

    // 带数据的枚举
    #[derive(Debug)]
    enum IpAddr {
        V4(u8, u8, u8, u8),
        V6(String),
    }

    let home = IpAddr::V4(127, 0, 0, 1);
    let loopback = IpAddr::V6(String::from("::1"));
    println!("home: {:?}", home);
    println!("loopback: {:?}", loopback);

    // 复杂枚举 - 每个成员可以有不同类型的数据
    #[derive(Debug)]
    enum Message {
        Quit,                       // 没有关联数据
        Move { x: i32, y: i32 },    // 包含匿名结构体
        Write(String),              // 包含单个 String
        ChangeColor(i32, i32, i32), // 包含三个 i32
    }

    let msg_quit = Message::Quit;
    let msg_move = Message::Move { x: 10, y: 20 };
    let msg_write = Message::Write(String::from("hello"));
    let msg_color = Message::ChangeColor(255, 0, 0);

    println!("Quit: {:?}", msg_quit);
    println!("Move: {:?}", msg_move);
    println!("Write: {:?}", msg_write);
    println!("ChangeColor: {:?}", msg_color);
    println!();

    // --------------------------------------------------------
    // 5. Option 枚举
    // --------------------------------------------------------
    println!("=== Option 枚举 ===");

    // Option<T> 表示可能有值，也可能没有值
    let some_number: Option<i32> = Some(5);
    let some_string: Option<&str> = Some("hello");
    let absent_number: Option<i32> = None;

    println!("Some(5): {:?}", some_number);
    println!("Some('hello'): {:?}", some_string);
    println!("None: {:?}", absent_number);

    // is_some / is_none
    println!("some_number.is_some() = {}", some_number.is_some());
    println!("absent_number.is_none() = {}", absent_number.is_none());

    // unwrap - 取出值（None 会 panic）
    println!("some_number.unwrap() = {}", some_number.unwrap());
    // absent_number.unwrap();  // 会 panic！

    // unwrap_or - None 时返回默认值
    println!("absent_number.unwrap_or(0) = {}", absent_number.unwrap_or(0));

    // map - 对 Some 中的值进行转换
    let doubled = some_number.map(|x| x * 2);
    println!("some_number.map(|x| x*2) = {:?}", doubled);

    // and_then - 链式操作
    let result = some_number.and_then(|x| if x > 0 { Some(x * 3) } else { None });
    println!("and_then: {:?}", result);

    println!();

    // --------------------------------------------------------
    // 6. 方法（impl）
    // --------------------------------------------------------
    println!("=== 方法（impl） ===");

    #[derive(Debug)]
    struct Rectangle {
        width: u32,
        height: u32,
    }

    // 为 Rectangle 实现方法
    impl Rectangle {
        // 计算面积
        fn area(&self) -> u32 {
            self.width * self.height
        }

        // 判断是否能容纳另一个矩形
        fn can_hold(&self, other: &Rectangle) -> bool {
            self.width > other.width && self.height > other.height
        }

        // 关联函数（没有 self，类似静态方法）
        fn square(size: u32) -> Rectangle {
            Rectangle { width: size, height: size }
        }

        // 设置宽度（可变 self）
        fn set_width(&mut self, width: u32) {
            self.width = width;
        }
    }

    let rect1 = Rectangle { width: 30, height: 50 };
    println!("矩形: {:?}", rect1);
    println!("面积: {}", rect1.area());

    let rect2 = Rectangle { width: 10, height: 40 };
    let rect3 = Rectangle { width: 60, height: 45 };

    println!("rect1 能容纳 rect2: {}", rect1.can_hold(&rect2));
    println!("rect1 能容纳 rect3: {}", rect1.can_hold(&rect3));

    // 关联函数调用
    let sq = Rectangle::square(20);
    println!("正方形: {:?}, 面积: {}", sq, sq.area());

    // 可变方法
    let mut rect4 = Rectangle::square(10);
    rect4.set_width(20);
    println!("修改后: {:?}", rect4);

    println!();

    // --------------------------------------------------------
    // 7. 枚举的方法
    // --------------------------------------------------------
    println!("=== 枚举的方法 ===");

    #[derive(Debug)]
    enum Message2 {
        Quit,
        Move { x: i32, y: i32 },
        Write(String),
        ChangeColor(i32, i32, i32),
    }

    impl Message2 {
        fn call(&self) {
            match self {
                Message2::Quit => println!("退出程序"),
                Message2::Move { x, y } => println!("移动到 ({}, {})", x, y),
                Message2::Write(text) => println!("写入文本: {}", text),
                Message2::ChangeColor(r, g, b) => println!("改变颜色为 ({}, {}, {})", r, g, b),
            }
        }
    }

    let msg1 = Message2::Move { x: 10, y: 20 };
    let msg2 = Message2::Write(String::from("hello"));

    msg1.call();
    msg2.call();
    println!();

    // --------------------------------------------------------
    // 8. match 模式匹配进阶
    // --------------------------------------------------------
    println!("=== match 模式匹配进阶 ===");

    // 匹配枚举 + 解构
    let msg = Message2::Move { x: 5, y: 10 };
    match msg {
        Message2::Quit => println!("退出"),
        Message2::Move { x, y } => println!("移动到 ({}, {})", x, y),
        Message2::Write(text) => println!("写入: {}", text),
        Message2::ChangeColor(r, g, b) => println!("颜色: {},{},{}", r, g, b),
    }

    // 匹配 Option
    let value = Some(42);
    match value {
        Some(n) if n > 50 => println!("大于 50: {}", n),
        Some(n) if n > 20 => println!("大于 20: {}", n),
        Some(n) => println!("其他值: {}", n),
        None => println!("没有值"),
    }

    // 匹配元组
    let pair = (2, -2);
    match pair {
        (x, y) if x == y => println!("两个数相等: {}", x),
        (x, y) if x + y == 0 => println!("和为零: {} + {} = 0", x, y),
        (x, _) if x % 2 == 0 => println!("第一个是偶数: {}", x),
        _ => println!("其他情况"),
    }

    // 匹配结构体 + 忽略
    let point = Point2 { x: 0, y: 7 };
    match point {
        Point2 { x: 0, y } => println!("在 y 轴上, y = {}", y),
        Point2 { x, y: 0 } => println!("在 x 轴上, x = {}", x),
        Point2 { x, y } => println!("在 ({}, {})", x, y),
    }

    // @ 绑定
    let num = 5;
    match num {
        n @ 1..=5 => println!("数字在 1-5 之间: {}", n),
        n @ 6..=10 => println!("数字在 6-10 之间: {}", n),
        n => println!("其他数字: {}", n),
    }

    println!();

    // --------------------------------------------------------
    // 9. if let / while let
    // --------------------------------------------------------
    println!("=== if let / while let ===");

    // if let 匹配 Option
    let some_value = Some(3);
    if let Some(3) = some_value {
        println!("if let: 值等于三");
    }

    if let Some(n) = some_value {
        println!("if let: 值为 {}", n);
    } else {
        println!("if let else: 没有值");
    }

    // if let 匹配枚举
    let color = Color2::Blue(0, 0, 255);
    if let Color2::Blue(r, g, b) = color {
        println!("蓝色 RGB({}, {}, {})", r, g, b);
    }

    // while let 循环
    println!("while let 弹出栈:");
    let mut stack = Vec::new();
    stack.push(1);
    stack.push(2);
    stack.push(3);

    while let Some(top) = stack.pop() {
        println!("  弹出: {}", top);
    }

    println!();
    println!("=== 07_struct_enum.rs 执行完毕 ===");
}

// 辅助定义
struct Point2 {
    x: i32,
    y: i32,
}

enum Color2 {
    Red,
    Green,
    Blue(u8, u8, u8),
}
