# Rust 编程基础与安全学习资源

> 本文系统介绍 Rust 编程基础与系统安全领域应用：Rust 在安全中的定位、编程基础（安全视角，重点关注所有权/借用/内存安全）、Rust 安全核心用法、常用命令与工具、2026 年免费学习资源、推荐 GitHub 项目，以及两个可运行的示例程序（basics.rs 和 security_cases.rs）。面向系统安全工程师与安全工具开发者，全部内容从内存安全、安全编码和安全工具开发的正向角度出发。

---

## 目录

- [一、Rust 在网络安全中的定位](#一rust-在网络安全中的定位)
- [二、Rust 编程基础（安全视角）](#二rust-编程基础安全视角)
- [三、Rust 安全核心用法](#三rust-安全核心用法)
- [四、常用命令与工具](#四常用命令与工具)
- [五、2026 年免费学习资源](#五2026-年免费学习资源)
- [六、2026 年推荐 GitHub 项目](#六2026-年推荐-github-项目)
- [七、示例代码文件](#七示例代码文件)
- [附：Rust 安全编码检查清单](#附rust-安全编码检查清单)

---

## 一、Rust 在网络安全中的定位

### 1.1 Rust 为什么对安全很重要

Rust 是 Mozilla 发起的系统级编程语言，核心目标是**内存安全、并发安全和高性能**。它通过独特的**所有权系统（Ownership）**和**借用检查器（Borrow Checker）**在编译时保证内存安全，不需要垃圾回收器（GC）。

| 特点 | 说明 | 安全意义 |
|------|------|---------|
| **内存安全** | 编译时检查，无数据竞争、无悬垂指针、无越界访问 | 从根源消除 70%+ 的内存安全漏洞 |
| **无 GC** | 不需要垃圾回收，性能与 C/C++ 相当 | 适合编写高性能安全工具、系统级代码 |
| **零成本抽象** | 高级特性编译后与手写底层代码性能一致 | 安全不牺牲性能 |
| **类型系统强大** | 代数数据类型、模式匹配、trait | 更安全的抽象，减少逻辑错误 |
| **并发安全** | Send/Sync trait 在编译期保证线程安全 | 并发安全工具开发更可靠 |
| **C FFI** | 可以和 C 代码互操作 | 可以逐步替换不安全的 C 代码 |

> **安全视角的重要性**：
> - 内存安全漏洞（缓冲区溢出、UAF、Double Free 等）长期占据 CVE 的半壁江山。微软、谷歌的统计数据表明，**约 70% 的安全漏洞是内存安全问题**。Rust 从语言层面消除了这些问题。
> - 作为**安全工具开发者**：用 Rust 编写的安全工具性能接近 C/C++，但不会有内存安全漏洞，更可靠。
> - 作为**系统安全工程师**：理解 Rust 的安全模型有助于理解内存安全的本质，更好地进行漏洞分析和防御。
> - 作为**密码学工程师**：Rust 的内存安全和高性能特性非常适合密码学实现。

### 1.2 安全领域的应用方向

| 方向 | Rust 的作用 | 典型场景 |
|------|------------|---------|
| **安全工具开发** | 高性能、内存安全的安全工具 | 端口扫描器、漏洞扫描器、WebShell 管理工具 |
| **系统编程** | 编写操作系统、驱动、底层工具 | 安全操作系统、内核模块、沙箱 |
| **密码学实现** | 内存安全 + 高性能 + 常量时间 | TLS 库、加密算法实现、签名验证 |
| **网络安全** | 异步高性能网络编程 | 代理、防火墙、IDS/IPS、蜜罐 |
| **逆向与二进制分析** | 高性能二进制分析工具 | 反汇编器、二进制差异分析、符号执行 |
| **嵌入式安全** | 内存安全的嵌入式编程 | IoT 设备安全、可信执行环境 |
| **WebAssembly** | 安全的沙箱执行环境 | 浏览器安全、Serverless、插件系统 |
| **红队工具开发** | 高性能、免杀效果好 | C2 框架、后渗透工具 |

### 1.3 Rust 版本演进

| 版本 | 时间 | 重要特性 |
|------|------|---------|
| Rust 1.0 | 2015 | 首个稳定版本 |
| Rust 1.31 | 2018 | Rust 2018 Edition、模块系统改进 |
| Rust 1.39 | 2019 | async/await 稳定 |
| Rust 1.50 | 2021 | const fn 增强、数组方法 |
| Rust 1.56 | 2021 | Rust 2021 Edition |
| Rust 1.60+ | 2022+ | 持续改进性能和生态 |
| Rust 1.75+ | 2024 | async fn in trait 等 |
| 最新稳定版 | 持续更新 | 每 6 周发布一个新版本 |

> **2026 年时效性**：Rust 版本更新很快（每 6 周一个版本），但核心概念（所有权、借用、生命周期）非常稳定。学习时以最新稳定版为准，安全工具开发推荐使用最新稳定版 Rust。

---

## 二、Rust 编程基础（安全视角）

### 2.1 环境搭建

#### rustup：Rust 版本管理工具

`rustup` 是 Rust 官方的版本管理工具，可以安装、管理、切换多个 Rust 版本。

```bash
# 安装 Rust（官方推荐方式）
# macOS / Linux
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Windows
# 访问 https://rustup.rs/ 下载 rustup-init.exe 运行

# 查看版本
rustc --version
cargo --version
rustup --version

# 更新 Rust 到最新稳定版
rustup update

# 切换版本（stable / beta / nightly）
rustup default stable
rustup default nightly

# 安装组件
rustup component add rustfmt
rustup component add clippy
rustup component add rust-src
```

#### cargo：Rust 的构建工具和包管理器

Cargo 是 Rust 的官方构建系统和包管理器，类似于 Go 的 go mod + Python 的 pip + JS 的 npm。

```bash
# 创建新项目
cargo new my_project        # 二进制项目
cargo new --lib my_lib      # 库项目

# 构建
cargo build                 # 调试构建
cargo build --release       # 发布构建（优化）

# 运行
cargo run

# 测试
cargo test

# 代码检查（编译但不生成可执行文件）
cargo check

# 格式化代码
cargo fmt

# 静态分析（额外的 lint 检查）
cargo clippy

# 生成文档
cargo doc

# 依赖安全审计
cargo audit               # 需要安装 cargo-audit
```

#### IDE 配置

| IDE / 编辑器 | 插件 | 说明 |
|-------------|------|------|
| **VS Code** | rust-analyzer | 最流行的 Rust 开发环境，免费 |
| **CLion + Rust 插件** | Rust 插件 | JetBrains 出品，功能强大（商业） |
| **RustRover** | JetBrains 专门的 Rust IDE | 非商业使用免费 |
| **Vim / Neovim** | rust.vim / rust-tools | 命令行爱好者 |

### 2.2 变量与数据类型

```rust
fn main() {
    // 变量（默认不可变！）
    let x = 5;
    // x = 6;  // 编译错误！默认不可变

    // 可变变量
    let mut y = 5;
    y = 6;  // 正确

    // 常量（编译时求值，必须标注类型）
    const MAX_POINTS: u32 = 100_000;

    // 静态变量（全局生命周期，'static）
    static GLOBAL_COUNT: i32 = 0;

    // 隐藏（Shadowing）：可以重复声明同名变量
    let spaces = "   ";
    let spaces = spaces.len();  // 类型可以变

    // 基本数据类型

    // 整数类型
    let a: i32 = 42;        // 有符号 32 位
    let b: u64 = 100;       // 无符号 64 位
    let c: isize = 200;     // 指针大小的有符号整数
    let d: usize = 300;     // 指针大小的无符号整数

    // 整数类型速查表
    // 长度     有符号    无符号
    // 8-bit    i8       u8
    // 16-bit   i16      u16
    // 32-bit   i32      u32 (默认)
    // 64-bit   i64      u64
    // 128-bit  i128     u128
    // arch     isize    usize

    // 浮点类型
    let e: f32 = 3.14;      // 单精度
    let f: f64 = 2.71828;   // 双精度（默认）

    // 布尔类型
    let g: bool = true;
    let h: bool = false;

    // 字符类型（Unicode，4 字节）
    let i: char = 'A';
    let j: char = '🦀';     // 支持 emoji
    let k: char = '中';     // 支持中文

    // 字符串
    let s1: &str = "hello";  // 字符串切片（引用）
    let s2: String = String::from("world"); // 拥有的字符串

    // 元组（tuple）
    let tup: (i32, f64, char) = (500, 6.4, 'J');
    let (x, y, z) = tup;     // 解构
    let first = tup.0;       // 用 . 访问

    // 数组（固定长度，同一类型）
    let arr: [i32; 5] = [1, 2, 3, 4, 5];
    let first = arr[0];
    let len = arr.len();

    // 切片（slice）
    let slice: &[i32] = &arr[1..3];  // [2, 3]
}
```

> **安全要点**：
> - 变量默认不可变（immutable）：这是 Rust 的核心理念之一，减少意外修改导致的 bug
> - 数组访问有边界检查（越界会 panic，而不是静默内存错误）
> - 没有 null：Rust 用 `Option<T>` 表示可能为空的值，强制处理空的情况
> - 没有未定义行为（安全 Rust 中）

### 2.3 所有权与借用（Rust 核心概念）

所有权是 Rust 最独特也是最重要的特性，是 Rust 内存安全的基础。

#### 所有权规则

1. **每个值都有一个所有者（owner）**
2. **同一时间只能有一个所有者**
3. **当所有者离开作用域时，值将被丢弃（drop）**

```rust
fn main() {
    let s1 = String::from("hello");  // s1 是字符串的所有者
    let s2 = s1;                      // 所有权移动（move）到 s2
    // println!("{}", s1);            // 编译错误！s1 不再有效
    println!("{}", s2);               // s2 有效
}  // s2 离开作用域，drop 被调用，内存释放
```

#### 借用与引用

为了不转移所有权，可以使用引用（借用）。

```rust
fn main() {
    let s1 = String::from("hello");

    // 不可变引用（借用）
    let len = calculate_length(&s1);
    println!("'{}' 的长度是 {}", s1, len);  // s1 仍然有效

    // 可变引用
    let mut s = String::from("hello");
    change(&mut s);
    println!("{}", s);  // hello, world
}

fn calculate_length(s: &String) -> usize {  // s 是引用，不拥有所有权
    s.len()
}  // s 离开作用域，但因为不拥有所有权，所以什么都不发生

fn change(s: &mut String) {  // 可变引用
    s.push_str(", world");
}
```

#### 借用规则

1. **同一时间，要么有一个可变引用，要么有任意数量的不可变引用**
2. **引用必须总是有效的**（不能有悬垂引用）

```rust
let mut s = String::from("hello");

let r1 = &s;     // 不可变引用 OK
let r2 = &s;     // 多个不可变引用 OK
// let r3 = &mut s;  // 编译错误！不能同时有可变和不可变引用
println!("{}, {}", r1, r2);
// r1 和 r2 的作用域在这里结束

let r3 = &mut s;  // 现在可以有可变引用了
println!("{}", r3);
```

#### 生命周期

生命周期是引用的有效范围。大多数时候编译器可以自动推断，但有些情况需要手动标注。

```rust
// 生命周期标注：返回值的生命周期和参数 a、b 中较短的那个相同
fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() { a } else { b }
}
```

> **安全意义**：
> - 所有权系统保证了：没有 double free、没有 use-after-free、没有悬垂指针
> - 借用规则保证了：没有数据竞争（data race）
> - 这些都是在**编译时**检查的，运行时没有额外开销
> - 这就是 Rust 能在没有 GC 的情况下保证内存安全的秘诀

### 2.4 流程控制

```rust
fn main() {
    // if-else
    let number = 6;
    if number % 4 == 0 {
        println!("能被 4 整除");
    } else if number % 3 == 0 {
        println!("能被 3 整除");
    } else if number % 2 == 0 {
        println!("能被 2 整除");
    } else {
        println!("不能被 2、3、4 整除");
    }

    // if 是表达式，可以赋值
    let condition = true;
    let number = if condition { 5 } else { 6 };

    // match 模式匹配（类似 switch，但强大得多）
    let number = 2;
    match number {
        1 => println!("一"),
        2 => println!("二"),
        3 => println!("三"),
        _ => println!("其他"),  // _ 是通配符
    }

    // match 可以赋值
    let result = match number {
        1 => "one",
        2 => "two",
        3 => "three",
        _ => "other",
    };

    // for 循环
    let arr = [10, 20, 30, 40, 50];
    for element in arr.iter() {
        println!("值是: {}", element);
    }

    // Range
    for i in 1..5 {      // 1, 2, 3, 4
        println!("{}", i);
    }
    for i in 1..=5 {     // 1, 2, 3, 4, 5
        println!("{}", i);
    }

    // while 循环
    let mut n = 5;
    while n > 0 {
        println!("{}!", n);
        n -= 1;
    }

    // loop（无限循环，用 break 退出）
    let mut count = 0;
    let result = loop {
        count += 1;
        if count == 10 {
            break count * 2;  // break 可以带返回值
        }
    };
    println!("结果: {}", result);  // 20

    // if let（只关心一种模式时比 match 简洁）
    let some_value = Some(3);
    if let Some(3) = some_value {
        println!("是 3");
    }

    // while let
    let mut stack = Vec::new();
    stack.push(1);
    stack.push(2);
    stack.push(3);
    while let Some(top) = stack.pop() {
        println!("{}", top);  // 3, 2, 1
    }
}
```

### 2.5 结构体与枚举

```rust
// 结构体
struct User {
    username: String,
    email: String,
    age: u32,
    active: bool,
}

impl User {
    // 关联函数（类似静态方法）
    fn new(username: String, email: String, age: u32) -> Self {
        Self {
            username,
            email,
            age,
            active: true,
        }
    }

    // 方法（&self 是借用，不获取所有权）
    fn get_username(&self) -> &str {
        &self.username
    }

    fn is_adult(&self) -> bool {
        self.age >= 18
    }

    // 可变方法
    fn deactivate(&mut self) {
        self.active = false;
    }
}

// 元组结构体（没有命名字段）
struct Color(i32, i32, i32);
struct Point(i32, i32, i32);

// 单元结构体（没有字段）
struct AlwaysEqual;

// 枚举（代数数据类型）
enum Message {
    Quit,                       // 没有数据
    Move { x: i32, y: i32 },    // 匿名结构体
    Write(String),              // 单值
    ChangeColor(i32, i32, i32), // 元组
}

impl Message {
    fn call(&self) {
        match self {
            Message::Quit => println!("退出"),
            Message::Move { x, y } => println!("移动到 ({}, {})", x, y),
            Message::Write(text) => println!("写入: {}", text),
            Message::ChangeColor(r, g, b) => println!("颜色: {},{},{}", r, g, b),
        }
    }
}

// Option<T>：可能存在也可能不存在的值（替代 null）
// enum Option<T> {
//     Some(T),
//     None,
// }

fn find_user(id: u32) -> Option<String> {
    if id == 1 {
        Some("Alice".to_string())
    } else {
        None
    }
}

fn main() {
    // 结构体使用
    let mut user = User::new("alice".to_string(), "alice@example.com".to_string(), 25);
    println!("用户名: {}", user.get_username());
    println!("成年: {}", user.is_adult());
    user.deactivate();

    // 枚举使用
    let msg = Message::Write("hello".to_string());
    msg.call();

    // Option 使用
    match find_user(1) {
        Some(name) => println!("找到用户: {}", name),
        None => println!("用户不存在"),
    }

    // 更简洁的方式
    if let Some(name) = find_user(2) {
        println!("找到: {}", name);
    } else {
        println!("没找到");
    }
}
```

> **安全要点**：
> - `Option<T>` 强制你处理空值的情况，不会出现空指针异常
> - `match` 是穷尽的（exhaustive），编译器会检查你是否处理了所有情况
> - 枚举 + 模式匹配是非常强大的安全抽象

### 2.6 错误处理

Rust 将错误分为两类：**可恢复错误**（`Result<T, E>`）和**不可恢复错误**（`panic!`）。

```rust
use std::fs::File;
use std::io::{self, Read};

// Result<T, E>：可恢复错误
// enum Result<T, E> {
//     Ok(T),
//     Err(E),
// }

fn read_file_contents(path: &str) -> Result<String, io::Error> {
    let mut file = match File::open(path) {
        Ok(f) => f,
        Err(e) => return Err(e),
    };

    let mut contents = String::new();
    match file.read_to_string(&mut contents) {
        Ok(_) => Ok(contents),
        Err(e) => Err(e),
    }
}

// ? 运算符：传播错误的简写（必须在返回 Result 的函数中使用）
fn read_file_short(path: &str) -> Result<String, io::Error> {
    let mut contents = String::new();
    File::open(path)?.read_to_string(&mut contents)?;
    Ok(contents)
}

fn main() {
    // 处理 Result
    match read_file_contents("test.txt") {
        Ok(contents) => println!("文件内容: {}", contents),
        Err(e) => eprintln!("读取失败: {}", e),
    }

    // 更简洁的方式
    if let Ok(contents) = read_file_short("test.txt") {
        println!("内容长度: {}", contents.len());
    }

    // unwrap：如果是 Ok 就返回值，是 Err 就 panic
    // （仅用于确定不会出错的情况或快速原型）
    // let f = File::open("test.txt").unwrap();

    // expect：类似 unwrap，但可以自定义错误信息
    // let f = File::open("test.txt").expect("打开文件失败");

    // panic!：不可恢复错误
    // panic!("发生了严重错误！");

    // 组合 Option 和 Result
    let result = find_user(1)
        .map(|name| format!("用户: {}", name))
        .unwrap_or_else(|| "用户不存在".to_string());
    println!("{}", result);
}

fn find_user(id: u32) -> Option<String> {
    if id == 1 { Some("Alice".to_string()) } else { None }
}
```

> **安全要点**：
> - 错误必须显式处理：`Result` 不会被静默忽略
> - `panic!` 是安全的失败：不会导致内存破坏，而是安全地终止线程
> - `?` 运算符让错误传播既简洁又规范
> - 不像 C++/Java 的异常，Rust 的错误是类型的一部分，编译器确保你处理

### 2.7 模块与包管理

```
项目结构：
my_project/
├── Cargo.toml       # 项目配置和依赖
├── src/
│   ├── main.rs      # 主入口
│   ├── lib.rs       # 库根（如果是库）
│   ├── utils.rs     # 模块文件
│   └── network/     # 模块目录
│       ├── mod.rs   # 模块声明
│       └── tcp.rs
└── target/          # 编译输出
```

```rust
// Cargo.toml 示例
[package]
name = "my_project"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }
rand = "0.8"

[dev-dependencies]
assert_cmd = "2.0"

// src/main.rs
mod utils;        // 声明模块
mod network;      // network 模块（目录形式）

use utils::helper;  // 导入
use network::tcp::TcpClient;

fn main() {
    helper();
    let client = TcpClient::new();
}
```

### 2.8 集合类型

```rust
use std::collections::{HashMap, HashSet, VecDeque};

fn main() {
    // Vec<T>：动态数组
    let mut v: Vec<i32> = Vec::new();
    v.push(1);
    v.push(2);
    v.push(3);
    println!("长度: {}", v.len());
    println!("第一个: {}", v[0]);

    // 安全访问（返回 Option，不会 panic）
    match v.get(100) {
        Some(val) => println!("值: {}", val),
        None => println!("索引越界"),
    }

    // VecDeque：双端队列
    let mut deque = VecDeque::new();
    deque.push_back(1);
    deque.push_front(0);
    let first = deque.pop_front();

    // HashMap<K, V>：哈希表
    let mut map: HashMap<String, i32> = HashMap::new();
    map.insert("Alice".to_string(), 25);
    map.insert("Bob".to_string(), 30);

    // 安全访问
    match map.get("Alice") {
        Some(age) => println!("Alice: {} 岁", age),
        None => println!("没找到"),
    }

    // 遍历
    for (key, value) in &map {
        println!("{}: {}", key, value);
    }

    // HashSet：集合
    let mut set: HashSet<i32> = HashSet::new();
    set.insert(1);
    set.insert(2);
    set.insert(1);  // 重复，不会添加
    println!("包含 1: {}", set.contains(&1));
}
```

### 2.9 并发

```rust
use std::thread;
use std::sync::{mpsc, Mutex, Arc};

fn main() {
    // 创建线程
    let handle = thread::spawn(|| {
        for i in 1..10 {
            println!("线程 1: {}", i);
            thread::sleep_ms(1);
        }
    });

    for i in 1..5 {
        println!("主线程: {}", i);
        thread::sleep_ms(1);
    }

    handle.join().unwrap();  // 等待子线程结束

    // 消息传递：channel
    let (tx, rx) = mpsc::channel();

    thread::spawn(move || {
        let val = String::from("hello");
        tx.send(val).unwrap();  // 发送消息
    });

    let received = rx.recv().unwrap();  // 接收消息（阻塞）
    println!("收到: {}", received);

    // 共享状态：Arc + Mutex
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();
            *num += 1;
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("最终计数: {}", *counter.lock().unwrap());  // 10
}
```

> **安全要点**：
> - Rust 通过 `Send` 和 `Sync` 两个 trait 在编译期保证线程安全
> - 数据竞争在编译期就被阻止了
> - `Arc<T>`（原子引用计数）是线程安全的 `Rc<T>`
> - `Mutex<T>` 提供互斥访问，编译器确保你在访问数据前必须获取锁

---

## 三、Rust 安全核心用法

### 3.1 内存安全：Rust 的核心优势

Rust 的所有权系统、借用检查器和类型系统在编译时消除了以下内存安全问题：

| 漏洞类型 | C/C++ 中 | Rust 中 | 说明 |
|---------|---------|---------|------|
| **缓冲区溢出** | 常见，UB | ✅ 编译期/运行期检查 | 数组越界在 Rust 中会 panic（安全终止） |
| **Use-After-Free** | 常见，高危 | ✅ 编译期阻止 | 借用检查器确保引用不会悬垂 |
| **Double Free** | 常见 | ✅ 编译期阻止 | 所有权系统保证每个值只有一个所有者 |
| **空指针解引用** | 常见 | ✅ 编译期阻止 | 没有 null，用 Option 强制处理空值 |
| **野指针** | 常见 | ✅ 编译期阻止 | 引用必须有效，生命周期确保 |
| **数据竞争** | 多线程常见 | ✅ 编译期阻止 | Send/Sync trait + 借用规则 |
| **未初始化内存** | 常见 | ✅ 编译期阻止 | 变量必须初始化才能使用 |

> **行业验证**：
> - 微软：约 70% 的安全漏洞是内存安全问题，正在用 Rust 重写关键组件
> - 谷歌：Android 中约 70% 的高危漏洞是内存安全问题，新代码优先使用 Rust
> - 亚马逊：AWS 越来越多基础设施使用 Rust
> - 美国白宫：推动从 C/C++ 向内存安全语言（包括 Rust）迁移

### 3.2 不安全 Rust（unsafe）

Rust 有一个 `unsafe` 关键字，可以在安全的 Rust 中打开一个"unsafe 块"，里面可以做一些编译器无法保证安全的操作。

```rust
fn main() {
    let mut num = 5;
    let r1 = &num as *const i32;
    let r2 = &mut num as *mut i32;

    unsafe {
        // unsafe 块中可以解引用裸指针
        println!("r1 指向的值: {}", *r1);
        println!("r2 指向的值: {}", *r2);

        // 还可以调用 unsafe 函数
        // 直接操作内存等
    }
}

// unsafe 函数
unsafe fn dangerous_operation() {
    // 这里面默认就是 unsafe 的
}
```

| unsafe 中可以做的事 | 说明 |
|---------------------|------|
| 解引用裸指针 | 绕过借用检查 |
| 调用 unsafe 函数 | 包括外部 C 函数（FFI） |
| 访问或修改可变静态变量 | 全局变量 |
| 实现 unsafe trait | 手动声明 Send/Sync 等 |
| 访问 union 的字段 | 联合体 |

> **安全建议**：
> - 尽量不要写 unsafe 代码
> - 如果必须写，把 unsafe 块尽量缩小
> - unsafe 块应该有详细的注释说明为什么是安全的
> - 对外暴露的 API 应该是安全的（unsafe 封装在内部）

### 3.3 密码学库

| 库 | 说明 | 特点 |
|----|------|------|
| **ring** | 高性能密码学库 | 基于 BoringSSL，内存安全封装 |
| **rustls** | 纯 Rust 的 TLS 库 | 替代 OpenSSL，内存安全 |
| **RustCrypto** | Rust 密码学项目集合 | 纯 Rust 实现，算法丰富 |
| **sodiumoxide** | libsodium 的 Rust 绑定 | 易用、安全的高级密码学 |
| **ed25519-dalek** | Ed25519 签名 | 快速、安全的签名算法实现 |
| **aes-gcm** | AES-GCM 加密 | 认证加密算法 |

```rust
// 使用 ring 进行哈希
use ring::digest;

fn sha256_hash(data: &[u8]) -> Vec<u8> {
    let digest = digest::digest(&digest::SHA256, data);
    digest.as_ref().to_vec()
}

// 使用 rand 生成安全随机数
use rand::Rng;
use rand::rngs::OsRng;

fn generate_random_key() -> [u8; 32] {
    let mut key = [0u8; 32];
    OsRng.fill_bytes(&mut key);
    key
}
```

### 3.4 网络编程

| 库 | 说明 | 用途 |
|----|------|------|
| **std::net** | 标准库网络 | 基础的 TCP/UDP 编程 |
| **tokio** | 异步运行时 | 高性能异步网络编程 |
| **async-std** | 异步标准库 | 另一个异步运行时 |
| **reqwest** | HTTP 客户端 | 异步 HTTP 客户端 |
| **hyper** | HTTP 库 | 底层 HTTP 实现 |
| **actix-web** | Web 框架 | 高性能异步 Web 框架 |
| **axum** | Web 框架 | 基于 tokio 和 hyper 的 Web 框架 |

```rust
// std::net TCP 连接示例
use std::net::TcpStream;
use std::io::{Read, Write};

fn check_port(host: &str, port: u16) -> bool {
    match TcpStream::connect((host, port)) {
        Ok(mut stream) => {
            // 连接成功
            true
        }
        Err(_) => {
            // 连接失败（端口关闭或过滤）
            false
        }
    }
}

// tokio 异步并发端口扫描（概念示例）
// use tokio::net::TcpStream;
// async fn scan_port(host: String, port: u16) -> bool {
//     TcpStream::connect((host.as_str(), port)).await.is_ok()
// }
```

### 3.5 安全工具开发实践

#### 为什么用 Rust 开发安全工具

| 特性 | 优势 |
|------|------|
| **性能** | 接近 C/C++，比 Python/Go 快很多 |
| **内存安全** | 工具本身不会有内存安全漏洞 |
| **单二进制** | 编译为单个静态链接文件，部署方便 |
| **跨平台** | 支持 Windows/Linux/macOS |
| **并发** | 安全的并发，数据竞争编译期检查 |
| **类型系统** | 减少逻辑错误 |

#### 适合用 Rust 开发的安全工具

- 端口扫描器
- 漏洞扫描器 / PoC 框架
- 哈希校验和密码破解工具
- 网络抓包和分析工具
- 二进制分析工具
- 日志分析和 SIEM 工具
- WebShell 管理工具
- 流量加密和隧道工具

---

## 四、常用命令与工具

### 4.1 Cargo 命令

| 命令 | 说明 |
|------|------|
| `cargo new` | 创建新项目 |
| `cargo build` | 构建项目 |
| `cargo build --release` | 发布构建（优化） |
| `cargo run` | 构建并运行 |
| `cargo test` | 运行测试 |
| `cargo check` | 检查编译（更快，不生成可执行文件） |
| `cargo fmt` | 格式化代码 |
| `cargo clippy` | 静态分析/lint |
| `cargo doc` | 生成文档 |
| `cargo doc --open` | 生成并在浏览器打开文档 |
| `cargo add` | 添加依赖（cargo-edit 扩展） |
| `cargo audit` | 依赖安全审计（cargo-audit 扩展） |
| `cargo bench` | 运行基准测试 |
| `cargo update` | 更新依赖版本 |
| `cargo tree` | 查看依赖树 |

### 4.2 安全工具

| 工具 | 用途 | 安装 |
|------|------|------|
| **cargo audit** | 依赖漏洞审计 | `cargo install cargo-audit` |
| **cargo outdate** | 检查过时的依赖 | `cargo install cargo-outdated` |
| **cargo clippy** | 代码 lint（内置） | `rustup component add clippy` |
| **rustfmt** | 代码格式化（内置） | `rustup component add rustfmt` |
| **cargo geiger** | 检测 unsafe 使用 | `cargo install cargo-geiger` |
| **cargo fuzz** | 模糊测试 | `cargo install cargo-fuzz` |
| **cargo tarpaulin** | 代码覆盖率 | `cargo install cargo-tarpaulin` |
| **Miri** | 未定义行为检测 | `rustup +nightly component add miri` |

```bash
# 依赖安全审计
cargo audit

# 检查 unsafe 使用
cargo geiger

# 代码 lint（包括很多安全相关的 lint）
cargo clippy

# 模糊测试
cargo fuzz init
cargo fuzz run fuzz_target
```

### 4.3 反编译与分析

| 工具 | 用途 |
|------|------|
| **cargo-bloat** | 分析二进制大小 |
| **cargo-asm** | 查看生成的汇编代码 |
| **Ghidra** | 逆向分析（支持 Rust 二进制） |
| **IDA Pro** | 专业逆向工具 |

---

## 五、2026 年免费学习资源

| 资源 | 类型 | 说明 | 链接/获取方式 |
|------|------|------|--------------|
| **Microsoft RustTraining** | 培训课程 | 微软开源全套 Rust 培训，七本内部教材，为 C++/C#/Python 开发者定制 | GitHub 搜索 microsoft/RustTraining |
| **Rust 语言圣经** | 中文教程 | 最用心的 Rust 中文学习教程，全面且深入，含在线练习 | [course.rs](https://course.rs/) |
| **100 Exercises to Learn Rust** | 练习课程 | JetBrains 免费课程，100 道练习题 | JetBrains 官网 |
| **Rustlings** | 小练习 | 官方小练习项目，边做边学 | GitHub: rust-lang/rustlings |
| **Rust by Example** | 示例教程 | 官方示例驱动的 Rust 学习 | [doc.rust-lang.org/rust-by-example](https://doc.rust-lang.org/rust-by-example/) |
| **The Rust Programming Language** | 官方书籍 | Rust 官方教程，俗称"the book" | [doc.rust-lang.org/book](https://doc.rust-lang.org/book/) |
| **Rust 标准库文档** | API 参考 | 最权威的标准库文档 | [doc.rust-lang.org/std](https://doc.rust-lang.org/std/) |
| **Rust Cookbook** | 菜谱式教程 | 常用任务的代码示例 | [rust-lang-nursery.github.io/rust-cookbook](https://rust-lang-nursery.github.io/rust-cookbook/) |
| **Rust Atomics and Locks** | 系统编程书籍 | 低级别并发编程（免费在线阅读） | [marablas.github.io/rustatomics](https://marablas.github.io/rustatomics/) |

> **2026 年时效性标注**：Rust 语言本身发展很快，但核心概念（所有权、借用、生命周期）非常稳定。学习资源以最新稳定版为准。微软等大厂的加入让 Rust 学习资源越来越丰富和系统化。建议先通过官方书籍掌握基础，再通过项目实践深入。

---

## 六、2026 年推荐 GitHub 项目

| 项目 | Stars（约） | 说明 | 适用场景 |
|------|------------|------|---------|
| **microsoft/RustTraining** | 数千+ | 微软内部 Rust 培训教材，七本教材覆盖从入门到高级模式、异步编程、工程实践 | 系统化学习 Rust |
| **sunface/rust-course** | 数万+ | Rust 语言圣经，为国内用户量身打造，含在线阅读与在线练习 | 中文 Rust 学习 |
| **7G-one/Don-t-Fear-the-Borrow-Checker** | 学习级 | 从零开始 15 课掌握 Rust，每课有实战项目、练习题、生活类比 | Rust 入门实战 |
| **EbookFoundation/free-programming-books** | 30万+ | 免费编程书籍大全，含大量 Rust 资源 | 资源索引 |
| **rust-lang/rust** | 数万+ | Rust 语言本身的源码仓库 | 深入理解 Rust |
| **tokio-rs/tokio** | 数万+ | Rust 异步运行时，最流行的异步框架 | 网络编程、异步开发 |
| **RustCrypto/traits** | 数千+ | Rust 密码学 trait 集合 | 密码学开发 |
| **rustls/rustls** | 数千+ | 纯 Rust 的 TLS 实现 | TLS/SSL 开发 |
| **seanmonstar/reqwest** | 数千+ | 易用的 Rust HTTP 客户端 | HTTP 工具开发 |
| **tokio-rs/mini-redis** | 学习级 | Tokio 教程项目，迷你 Redis 实现 | 学习异步 Rust |

> **⚠️ 免责声明**：以上 GitHub 项目仅供学习研究使用。安全工具开发请遵守法律法规，仅在授权环境中使用。

---

## 七、示例代码文件

`code/` 目录下包含两个 Rust 示例程序：

| 文件 | 内容 | 编译运行 |
|------|------|---------|
| `basics.rs` | Rust 基础语法示例：变量、数据类型、所有权、借用、流程控制、结构体、枚举、错误处理、集合 | `rustc basics.rs -o basics && ./basics` |
| `security_cases.rs` | 安全案例集：端口扫描器、哈希校验工具、文件完整性检查、安全随机数 | `rustc security_cases.rs -o security_cases && ./security_cases` |

> **运行注意**：
> - 需要 Rust 工具链（rustup + cargo + rustc）
> - 安装：https://rustup.rs/
> - 单文件直接编译：`rustc filename.rs`
> - 实际项目推荐使用 Cargo：`cargo new project_name`

---

## 附：Rust 安全编码检查清单

### 内存安全

- [ ] 优先使用安全 Rust，避免 `unsafe` 块
- [ ] 如果必须使用 unsafe，尽量缩小 unsafe 块范围
- [ ] unsafe 块有充分的安全证明注释
- [ ] 数组访问优先使用 `.get()`（返回 Option）而非 `[]`
- [ ] 使用 `Option<T>` 处理可能为空的值，不要用 `unwrap()` （除非确定不会出错）
- [ ] 使用 `Result<T, E>` 处理可恢复错误，不要用 `unwrap()`/`expect()`
- [ ] 正确处理错误，不要忽略 Result（`let _ = ...` 要谨慎）

### 输入验证

- [ ] 所有外部输入都进行验证
- [ ] 使用白名单验证，而非黑名单
- [ ] 验证数据类型、长度、范围、格式
- [ ] 反序列化外部数据使用安全的格式（JSON/protobuf）
- [ ] 网络数据读取设置合理的大小限制

### 并发安全

- [ ] 优先使用消息传递（channel）而非共享状态
- [ ] 共享状态使用 `Mutex`/`RwLock` 等同步原语
- [ ] 多线程使用 `Arc<T>` 而非 `Rc<T>`
- [ ] 不要假设内存顺序，正确使用 `Ordering`
- [ ] 避免 `unsafe` 的并发操作

### 依赖安全

- [ ] 定期运行 `cargo audit` 检查依赖漏洞
- [ ] 及时更新有安全问题的依赖
- [ ] 评估新增依赖的安全性和维护状态
- [ ] 使用 `cargo geiger` 检查依赖中的 unsafe 使用
- [ ] 优先选择维护活跃、社区认可的 crate

### 代码质量

- [ ] 使用 `cargo clippy` 检查 lint 警告
- [ ] 使用 `rustfmt` 格式化代码
- [ ] 编写单元测试和集成测试
- [ ] 使用 `cargo tarpaulin` 检查测试覆盖率
- [ ] 关键代码使用 Miri 检测未定义行为
- [ ] 对不安全的输入处理进行模糊测试（fuzzing）

### 密码学安全

- [ ] 使用成熟的密码学库（ring、RustCrypto 等），不要自己实现
- [ ] 使用加密安全的随机数生成器（`rand::rngs::OsRng`）
- [ ] 密码哈希使用专门的算法（argon2、bcrypt、pbkdf2）
- [ ] 不要在代码中硬编码密钥和密码
- [ ] 敏感数据用完后清零内存（使用 `zeroize` crate）

---

> **免责声明**：本文档所有内容仅用于学习、研究和授权环境下的安全测试与防御实践。任何未经授权的测试或攻击行为均属违法。读者应遵守所在地区法律法规，对自己的行为负责。
