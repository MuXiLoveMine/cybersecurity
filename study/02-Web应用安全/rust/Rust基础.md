# Rust 语言基础

## 目录

- [一、Rust 语言简介](#一rust-语言简介)
- [二、使用场景](#二使用场景)
- [三、环境安装](#三环境安装)
- [四、基础语法](#四基础语法)
- [五、运算符](#五运算符)
- [六、控制流](#六控制流)
- [七、函数](#七函数)
- [八、所有权（Ownership）](#八所有权ownership)
- [九、结构体（struct）](#九结构体struct)
- [十、枚举（enum）与模式匹配](#十枚举enum与模式匹配)
- [十一、方法（impl）](#十一方法impl)
- [十二、泛型与特征（trait）](#十二泛型与特征trait)
- [十三、集合类型](#十三集合类型)
- [十四、字符串操作](#十四字符串操作)
- [十五、错误处理](#十五错误处理)
- [十六、模块系统](#十六模块系统)
- [十七、包管理（Cargo）](#十七包管理cargo)
- [十八、文件操作](#十八文件操作)
- [十九、网络请求](#十九网络请求)
- [二十、正则表达式](#二十正则表达式)
- [二十一、Rust 在安全领域的应用](#二十一rust-在安全领域的应用)

---

## 一、Rust 语言简介

### 1.1 历史

Rust 是由 Mozilla 研究院的 Graydon Hoare 于 2006 年开始设计的系统级编程语言，2010 年正式对外公布。2015 年发布 1.0 稳定版。Rust 的设计目标是成为一门安全、并发、实用的系统编程语言。

自 2016 年起，Rust 连续多年在 Stack Overflow 开发者调查中被评为"最受喜爱的编程语言"。

### 1.2 核心特点

#### 内存安全（无 GC）
- Rust 通过**所有权系统**（Ownership）、**借用检查器**（Borrow Checker）在编译时保证内存安全
- 不需要垃圾回收器（Garbage Collector），运行时无额外开销
- 杜绝空指针、悬垂指针、缓冲区溢出等常见内存安全问题

#### 并发安全
- Rust 的所有权系统同样保证了线程安全
- "无畏并发"（Fearless Concurrency）：编译时防止数据竞争

#### 高性能
- 零成本抽象（Zero-cost abstractions）
- 直接编译为机器码，性能与 C/C++ 相当
- 没有运行时开销和 GC 停顿

#### 其他特性
- 模式匹配（Pattern Matching）
- 泛型与特征（Generics & Traits）
- 宏系统（Macros）
- 类型推断
- 表达式导向的语言

---

## 二、使用场景

### 2.1 系统编程
- 操作系统内核开发
- 嵌入式系统
- 设备驱动程序
- 底层库开发

### 2.2 WebAssembly (Wasm)
- 前端高性能计算
- 游戏引擎的 Web 版本
- 图像处理、视频编解码

### 2.3 安全工具开发
- 静态分析工具
- 模糊测试（Fuzzing）框架
- 二进制分析工具
- 密码学库

### 2.4 区块链
- Solana、Polkadot、Near 等区块链项目使用 Rust 开发
- 智能合约开发

### 2.5 命令行工具
- ripgrep（快速搜索工具）
- fd（find 替代品）
- exa（ls 替代品）

### 2.6 Web 后端
- Actix-web、Axum、Rocket 等 Web 框架
- 高性能 API 服务

---

## 三、环境安装

### 3.1 rustup — Rust 工具链管理器

**Windows 安装：**
1. 访问 [https://rustup.rs](https://rustup.rs) 下载安装程序
2. 运行 `rustup-init.exe`，按提示安装
3. 需要提前安装 Visual Studio Build Tools（C++ 构建工具）

**Linux/macOS 安装：**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### 3.2 常用 rustup 命令

```bash
rustup update              # 更新 Rust 工具链
rustup default stable      # 设置默认工具链为稳定版
rustup default nightly     # 设置默认工具链为 nightly 版
rustup toolchain list      # 列出已安装的工具链
rustc --version            # 查看 Rust 编译器版本
cargo --version            # 查看 Cargo 版本
```

### 3.3 组件说明

| 组件 | 说明 |
|------|------|
| `rustc` | Rust 编译器 |
| `cargo` | Rust 包管理器和构建工具 |
| `rustup` | Rust 工具链版本管理器 |
| `rustfmt` | 代码格式化工具 |
| `clippy` | 代码静态检查（Lint）工具 |
| `rust-docs` | 本地文档 |

### 3.4 编译运行方式

**方式一：使用 rustc 直接编译**
```bash
rustc main.rs        # 编译，生成 main.exe (Windows) 或 main (Linux)
./main               # 运行
```

**方式二：使用 Cargo 项目管理**
```bash
cargo new my_project     # 创建新项目
cd my_project
cargo build              # 编译
cargo run                # 编译并运行
cargo check              # 检查代码是否能编译（不生成可执行文件）
cargo build --release    # 发布版本编译（优化）
```

---

## 四、基础语法

### 4.1 变量

#### 不可变变量（let）
Rust 中变量默认是**不可变**的，这是 Rust 保证安全和并发的设计之一。

```rust
let x = 5;      // x 是不可变的
// x = 6;       // 错误：不能修改不可变变量
```

#### 可变变量（mut）
使用 `mut` 关键字声明可变变量。

```rust
let mut x = 5;  // x 是可变的
x = 6;          // 正确
```

#### 变量遮蔽（Shadowing）
可以用 `let` 重新声明同名变量，新变量会遮蔽旧变量。

```rust
let x = 5;
let x = x + 1;      // x 现在是 6
let x = "hello";    // x 现在是字符串类型
```

与 `mut` 不同，遮蔽可以改变变量类型。

### 4.2 常量（const）

```rust
const MAX_POINTS: u32 = 100_000;
const PI: f64 = 3.14159265358979;
```

- 常量必须标注类型
- 常量可以在任何作用域声明，包括全局作用域
- 常量只能被设置为常量表达式，不能在运行时计算
- 命名规范：全大写 + 下划线分隔

### 4.3 数据类型

Rust 是静态类型语言，编译时必须知道所有变量的类型。Rust 有强大的**类型推断**能力。

#### 标量类型（Scalar）

| 类型分类 | 类型 | 说明 |
|---------|------|------|
| 有符号整数 | i8, i16, i32, i64, i128, isize | 8~128位有符号整数，isize 取决于平台 |
| 无符号整数 | u8, u16, u32, u64, u128, usize | 8~128位无符号整数，usize 取决于平台 |
| 浮点数 | f32, f64 | 单精度/双精度浮点数，默认 f64 |
| 布尔值 | bool | true / false |
| 字符 | char | Unicode 标量值，4字节 |

**整数类型默认是 i32。**

```rust
let a: i32 = 10;
let b: u64 = 100;
let c: f64 = 3.14;
let d: bool = true;
let e: char = 'R';
let f: char = '字';  // 支持中文
```

#### 复合类型（Compound）

**元组（Tuple）：**
```rust
let tup: (i32, f64, char) = (500, 6.4, 'R');
let (x, y, z) = tup;    // 解构
let first = tup.0;       // 索引访问
```

**数组（Array）：**
```rust
let arr: [i32; 5] = [1, 2, 3, 4, 5];
let first = arr[0];      // 索引访问
let arr2 = [0; 5];       // 5个元素都是0
```

- 数组长度固定，元素类型相同
- 栈上分配
- 越界访问会导致 panic（运行时检查）

### 4.4 类型推断

Rust 编译器可以根据上下文推断类型，大多数时候不需要手动标注。

```rust
let x = 5;          // 推断为 i32
let y = 3.14;       // 推断为 f64
let s = "hello";    // 推断为 &str
```

当编译器无法推断时，需要手动标注：
```rust
let guess: u32 = "42".parse().expect("不是数字");
```

### 4.5 类型转换

Rust 不允许隐式类型转换，必须使用 `as` 显式转换。

```rust
let x: i32 = 5;
let y: f64 = x as f64;    // 整数转浮点数
let z: u8 = 255;
let w: i16 = z as i16;    // 无符号转有符号
```

---

## 五、运算符

### 5.1 算术运算符

| 运算符 | 说明 | 示例 |
|-------|------|------|
| `+` | 加法 | `5 + 3 = 8` |
| `-` | 减法 | `5 - 3 = 2` |
| `*` | 乘法 | `5 * 3 = 15` |
| `/` | 除法 | `5 / 3 = 1`（整数除法） |
| `%` | 取余 | `5 % 3 = 2` |

### 5.2 赋值运算符

| 运算符 | 说明 | 示例 |
|-------|------|------|
| `=` | 赋值 | `x = 5` |
| `+=` | 加等 | `x += 3` |
| `-=` | 减等 | `x -= 3` |
| `*=` | 乘等 | `x *= 3` |
| `/=` | 除等 | `x /= 3` |
| `%=` | 取余等 | `x %= 3` |

### 5.3 比较运算符

| 运算符 | 说明 |
|-------|------|
| `==` | 等于 |
| `!=` | 不等于 |
| `>` | 大于 |
| `<` | 小于 |
| `>=` | 大于等于 |
| `<=` | 小于等于 |

### 5.4 逻辑运算符

| 运算符 | 说明 |
|-------|------|
| `&&` | 逻辑与（短路） |
| `\|\|` | 逻辑或（短路） |
| `!` | 逻辑非 |

### 5.5 位运算符

| 运算符 | 说明 |
|-------|------|
| `&` | 按位与 |
| `\|` | 按位或 |
| `^` | 按位异或 |
| `!` | 按位取反 |
| `<<` | 左移 |
| `>>` | 右移 |

---

## 六、控制流

### 6.1 if / else if / else

```rust
let number = 6;

if number % 4 == 0 {
    println!("能被 4 整除");
} else if number % 3 == 0 {
    println!("能被 3 整除");
} else if number % 2 == 0 {
    println!("能被 2 整除");
} else {
    println!("不能被 4、3、2 整除");
}
```

**if 是表达式，可以返回值：**

```rust
let condition = true;
let number = if condition { 5 } else { 6 };
```

### 6.2 loop 无限循环

```rust
let mut count = 0;
loop {
    count += 1;
    if count == 10 {
        break;      // 跳出循环
    }
    if count % 2 == 0 {
        continue;   // 跳过本次迭代
    }
    println!("count = {}", count);
}
```

**loop 可以返回值：**

```rust
let mut counter = 0;
let result = loop {
    counter += 1;
    if counter == 10 {
        break counter * 2;    // break 后的值就是 loop 的返回值
    }
};
println!("result = {}", result);  // 20
```

**循环标签（嵌套循环时使用）：**

```rust
'outer: loop {
    'inner: loop {
        break 'outer;    // 跳出外层循环
    }
}
```

### 6.3 while 循环

```rust
let mut number = 3;

while number != 0 {
    println!("{}!", number);
    number -= 1;
}
println!("发射！");
```

### 6.4 for 循环

```rust
let arr = [10, 20, 30, 40, 50];

for element in arr.iter() {
    println!("值为：{}", element);
}
```

**Range 范围：**

```rust
for i in 1..5 {       // 1, 2, 3, 4（左闭右开）
    println!("{}", i);
}

for i in 1..=5 {      // 1, 2, 3, 4, 5（包含右端点）
    println!("{}", i);
}

for i in (1..5).rev() {  // 反向：4, 3, 2, 1
    println!("{}", i);
}
```

### 6.5 match 模式匹配

```rust
let number = 3;

match number {
    1 => println!("一"),
    2 => println!("二"),
    3 => println!("三"),
    4..=6 => println!("四到六"),
    _ => println!("其他数字"),    // _ 是通配符，匹配所有情况
}
```

**match 是表达式，可以返回值：**

```rust
let number = 3;
let result = match number {
    1 => "one",
    2 => "two",
    3 => "three",
    _ => "other",
};
```

**匹配枚举：**
```rust
enum Color {
    Red,
    Green,
    Blue,
    RGB(u8, u8, u8),
}

let color = Color::RGB(255, 0, 0);
match color {
    Color::Red => println!("红色"),
    Color::Green => println!("绿色"),
    Color::Blue => println!("蓝色"),
    Color::RGB(r, g, b) => println!("RGB({}, {}, {})", r, g, b),
}
```

### 6.6 if let 简洁控制流

当只关心一种匹配情况时，`if let` 比 `match` 更简洁。

```rust
let some_value = Some(3);

// match 写法
match some_value {
    Some(3) => println!("等于三"),
    _ => (),
}

// if let 写法（等价）
if let Some(3) = some_value {
    println!("等于三");
}

// 可以带 else
if let Some(n) = some_value {
    println!("值为：{}", n);
} else {
    println!("没有值");
}
```

---

## 七、函数

### 7.1 函数定义

```rust
fn function_name(parameter: Type) -> ReturnType {
    // 函数体
}
```

```rust
fn greet() {
    println!("Hello, Rust!");
}

fn main() {
    greet();
}
```

### 7.2 参数

```rust
fn print_sum(x: i32, y: i32) {
    println!("{} + {} = {}", x, y, x + y);
}

fn main() {
    print_sum(5, 3);
}
```

- 函数参数必须声明类型
- 多个参数用逗号分隔

### 7.3 返回值

使用 `->` 声明返回值类型，函数最后一个表达式的值就是返回值（不需要 return）。

```rust
fn add(x: i32, y: i32) -> i32 {
    x + y    // 表达式，没有分号，就是返回值
}
```

也可以使用 `return` 提前返回：

```rust
fn abs(x: i32) -> i32 {
    if x < 0 {
        return -x;
    }
    x
}
```

### 7.4 语句与表达式

Rust 是**表达式导向**的语言，语句和表达式有重要区别：

- **语句**（Statement）：执行操作但不返回值，以分号结尾
- **表达式**（Expression）：计算并返回值，可以没有分号

```rust
fn main() {
    let y = {                // 块是表达式
        let x = 3;           // 语句
        x + 1                // 表达式，返回值
    };
    println!("y = {}", y);   // y = 4
}
```

### 7.5 表达式体函数

如果函数体只有一个表达式，可以省略大括号：

```rust
fn add(x: i32, y: i32) -> i32 {
    x + y
}

// 等价于
fn add(x: i32, y: i32) -> i32 { x + y }
```

---

## 八、所有权（Ownership）

所有权是 Rust 最独特的特性，它使 Rust 无需 GC 就能保证内存安全。

### 8.1 核心概念

#### 所有权规则
1. Rust 中每个值都有一个**所有者**（owner）
2. 同一时刻只能有一个所有者
3. 当所有者离开作用域，值将被丢弃（drop）

#### 作用域

```rust
fn main() {
    let s = "hello";   // s 进入作用域
    // 使用 s
}                      // s 离开作用域，内存被释放
```

#### 移动（Move）

对于存储在堆上的数据（如 String），赋值操作会导致所有权**移动**：

```rust
let s1 = String::from("hello");
let s2 = s1;           // s1 的所有权移动给 s2
// println!("{}", s1); // 错误：s1 已经无效了
println!("{}", s2);    // 正确
```

这和 C++ 的深拷贝不同，Rust 永远不会自动创建数据的深拷贝。

#### 克隆（Clone）

如果需要深拷贝堆上的数据，使用 `clone` 方法：

```rust
let s1 = String::from("hello");
let s2 = s1.clone();    // 深拷贝
println!("s1 = {}, s2 = {}", s1, s2);  // 都有效
```

#### 拷贝（Copy）

对于存储在栈上的简单类型（如整数、浮点数、布尔值、char 等），赋值是**拷贝**而不是移动，因为它们实现了 `Copy` trait。

```rust
let x = 5;
let y = x;       // 拷贝，x 仍然有效
println!("x = {}, y = {}", x, y);
```

### 8.2 借用（Borrowing）与引用

很多时候我们不想转移所有权，这时候可以使用**引用**。

#### 不可变引用

```rust
fn calculate_length(s: &String) -> usize {
    s.len()
}                       // s 离开作用域，但因为它没有所有权，所以不会 drop

fn main() {
    let s1 = String::from("hello");
    let len = calculate_length(&s1);  // 借用 s1，不转移所有权
    println!("'{}' 的长度是 {}", s1, len);  // s1 仍然有效
}
```

#### 可变引用

```rust
fn change(s: &mut String) {
    s.push_str(", world");
}

fn main() {
    let mut s = String::from("hello");
    change(&mut s);
    println!("{}", s);  // hello, world
}
```

#### 引用规则
1. 在任意给定时间，要么只能有一个可变引用，要么只能有多个不可变引用
2. 引用必须总是有效的（不能有悬垂引用）

```rust
let mut s = String::from("hello");

let r1 = &s;     // 不可变引用
let r2 = &s;     // 多个不可变引用是允许的
// let r3 = &mut s;  // 错误：不能同时有可变和不可变引用
```

```rust
let mut s = String::from("hello");

let r1 = &mut s; // 可变引用
// let r2 = &mut s;  // 错误：不能同时有多个可变引用
```

这个规则防止了数据竞争（data race）。

#### 悬垂引用（Dangling References）

Rust 编译器会确保引用不会悬垂：

```rust
fn dangle() -> &String {    // 错误：缺少生命周期参数
    let s = String::from("hello");
    &s                      // 返回局部变量的引用，s 离开作用域后会被释放
}
```

### 8.3 生命周期简介

生命周期（Lifetime）是引用的有效期，Rust 的借用检查器会确保引用的有效。

```rust
// 函数签名中的生命周期标注
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

- `'a` 是生命周期参数
- 表示返回值的生命周期与参数 x、y 的生命周期相同
- 大多数时候，生命周期可以被编译器自动推断（生命周期省略规则）

---

## 九、结构体（struct）

### 9.1 定义结构体

```rust
struct User {
    username: String,
    email: String,
    sign_in_count: u64,
    active: bool,
}
```

### 9.2 创建实例

```rust
let user = User {
    email: String::from("someone@example.com"),
    username: String::from("someusername"),
    active: true,
    sign_in_count: 1,
};

println!("用户名：{}", user.username);
```

### 9.3 可变结构体

```rust
let mut user = User {
    email: String::from("old@example.com"),
    username: String::from("user1"),
    active: true,
    sign_in_count: 1,
};

user.email = String::from("new@example.com");  // 修改字段
```

### 9.4 字段初始化简写

当字段名和变量名相同时：

```rust
fn build_user(email: String, username: String) -> User {
    User {
        email,        // 等价于 email: email
        username,     // 等价于 username: username
        active: true,
        sign_in_count: 1,
    }
}
```

### 9.5 结构体更新语法

```rust
let user2 = User {
    email: String::from("new@example.com"),
    username: String::from("user2"),
    ..user1    // 其余字段使用 user1 的值
};
```

### 9.6 元组结构体（Tuple Structs）

字段没有名称，只有类型：

```rust
struct Color(i32, i32, i32);
struct Point(i32, i32, i32);

let black = Color(0, 0, 0);
let origin = Point(0, 0, 0);
```

### 9.7 单元结构体（Unit-Like Structs）

没有任何字段的结构体：

```rust
struct AlwaysEqual;

let subject = AlwaysEqual;
```

---

## 十、枚举（enum）与模式匹配

### 10.1 定义枚举

```rust
enum IpAddrKind {
    V4,
    V6,
}

let four = IpAddrKind::V4;
let six = IpAddrKind::V6;
```

### 10.2 枚举值关联数据

```rust
enum IpAddr {
    V4(u8, u8, u8, u8),
    V6(String),
}

let home = IpAddr::V4(127, 0, 0, 1);
let loopback = IpAddr::V6(String::from("::1"));
```

每个枚举成员可以有不同类型和数量的数据：

```rust
enum Message {
    Quit,                       // 没有关联数据
    Move { x: i32, y: i32 },    // 包含匿名结构体
    Write(String),              // 包含单个 String
    ChangeColor(i32, i32, i32), // 包含三个 i32
}
```

### 10.3 Option 枚举

Rust 没有 null，使用 `Option<T>` 表示可能为空的值：

```rust
enum Option<T> {
    Some(T),    // 包含一个值
    None,       // 没有值
}
```

```rust
let some_number: Option<i32> = Some(5);
let some_string: Option<&str> = Some("hello");
let absent_number: Option<i32> = None;
```

使用 `Option<T>` 时必须处理 `None` 的情况，防止空指针错误。

---

## 十一、方法（impl）

### 11.1 定义方法

```rust
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    // 方法，第一个参数是 &self
    fn area(&self) -> u32 {
        self.width * self.height
    }

    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }
}

fn main() {
    let rect = Rectangle { width: 30, height: 50 };
    println!("面积：{}", rect.area());
}
```

### 11.2 关联函数（静态方法）

不以 `self` 为参数的函数，使用 `::` 调用：

```rust
impl Rectangle {
    // 关联函数，常用于构造函数
    fn square(size: u32) -> Rectangle {
        Rectangle { width: size, height: size }
    }
}

let sq = Rectangle::square(10);
```

### 11.3 多个 impl 块

可以为同一个结构体定义多个 impl 块：

```rust
impl Rectangle {
    fn area(&self) -> u32 { self.width * self.height }
}

impl Rectangle {
    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }
}
```

---

## 十二、泛型与特征（trait）

### 12.1 泛型

泛型用于编写适用于多种类型的代码。

#### 函数泛型

```rust
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}
```

#### 结构体泛型

```rust
struct Point<T> {
    x: T,
    y: T,
}

let integer = Point { x: 5, y: 10 };
let float = Point { x: 1.0, y: 4.0 };
```

#### 枚举泛型

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

#### 方法泛型

```rust
impl<T> Point<T> {
    fn x(&self) -> &T {
        &self.x
    }
}
```

### 12.2 特征（trait）

Trait 定义了一组方法签名，类似于其他语言的接口。

```rust
trait Summary {
    fn summarize(&self) -> String;

    // 默认实现
    fn summarize_author(&self) -> String {
        String::from("未知作者")
    }
}

struct Article {
    title: String,
    author: String,
    content: String,
}

impl Summary for Article {
    fn summarize(&self) -> String {
        format!("{} - 作者：{}", self.title, self.author)
    }
}
```

#### trait 作为参数

```rust
fn notify(item: &impl Summary) {
    println!("通知：{}", item.summarize());
}

// 等价的 Trait Bound 语法
fn notify<T: Summary>(item: &T) {
    println!("通知：{}", item.summarize());
}
```

#### 多个 trait bound

```rust
fn notify(item: &(impl Summary + Display)) {}

fn notify<T: Summary + Display>(item: &T) {}
```

#### where 子句

当 trait bound 太多时使用 where 子句更清晰：

```rust
fn some_function<T, U>(t: &T, u: &U) -> i32
where
    T: Display + Clone,
    U: Clone + Debug,
{
    // ...
}
```

---

## 十三、集合类型

### 13.1 Vec\<T\>（向量/动态数组）

Vec 是可增长的动态数组，存储在堆上。

**创建：**
```rust
let v: Vec<i32> = Vec::new();       // 空向量
let v = vec![1, 2, 3];               // 使用宏创建
let mut v = Vec::new();
v.push(1);                           // 添加元素
v.push(2);
```

**访问：**
```rust
let v = vec![1, 2, 3, 4, 5];
let third: &i32 = &v[2];          // 索引访问，越界会 panic
match v.get(2) {                  // get 方法，返回 Option
    Some(value) => println!("值：{}", value),
    None => println!("索引越界"),
}
```

**增删改：**
```rust
let mut v = vec![1, 2, 3];
v.push(4);                        // 末尾添加
let last = v.pop();               // 弹出末尾元素，返回 Option
v.insert(0, 0);                   // 在指定位置插入
let removed = v.remove(1);        // 删除指定位置元素
v[0] = 10;                        // 修改元素
```

**遍历：**
```rust
let v = vec![100, 32, 57];
for i in &v {
    println!("{}", i);
}

// 可变遍历
let mut v = vec![100, 32, 57];
for i in &mut v {
    *i += 50;  // 需要解引用
}
```

**迭代器：**
```rust
let v: Vec<i32> = (1..10).collect();              // 从迭代器收集
let doubled: Vec<i32> = v.iter().map(|x| x * 2).collect();
let filtered: Vec<i32> = v.into_iter().filter(|x| x > &3).collect();
```

### 13.2 HashMap（哈希表）

键值对集合，类似其他语言的字典/Map。

**创建：**
```rust
use std::collections::HashMap;

let mut scores: HashMap<String, i32> = HashMap::new();
scores.insert(String::from("Red"), 10);
scores.insert(String::from("Blue"), 50);
```

**访问：**
```rust
let team_name = String::from("Blue");
let score = scores.get(&team_name);    // 返回 Option<&i32>

match score {
    Some(s) => println!("分数：{}", s),
    None => println!("未找到"),
}
```

**增删改：**
```rust
scores.insert(String::from("Yellow"), 30);   // 插入
scores.remove("Red");                        // 删除

// 只在键不存在时插入
scores.entry(String::from("Blue")).or_insert(50);

// 修改已有值
let score = scores.entry(String::from("Blue")).or_insert(0);
*score += 10;
```

**遍历：**
```rust
for (key, value) in &scores {
    println!("{}: {}", key, value);
}
```

**词频统计示例：**
```rust
use std::collections::HashMap;

fn word_count(text: &str) -> HashMap<String, u32> {
    let mut map = HashMap::new();
    for word in text.split_whitespace() {
        let count = map.entry(word.to_string()).or_insert(0);
        *count += 1;
    }
    map
}
```

### 13.3 HashSet（集合）

不重复元素的集合。

```rust
use std::collections::HashSet;

let mut set: HashSet<i32> = HashSet::new();
set.insert(1);
set.insert(2);
set.insert(2);    // 重复插入，不会改变

println!("{}", set.contains(&1));  // true

for x in &set {
    println!("{}", x);
}

// 交集、并集、差集
let a: HashSet<_> = [1, 2, 3].iter().cloned().collect();
let b: HashSet<_> = [2, 3, 4].iter().cloned().collect();

let intersection: Vec<_> = a.intersection(&b).collect();  // 交集
let union: Vec<_> = a.union(&b).collect();                // 并集
let diff: Vec<_> = a.difference(&b).collect();            // 差集
```

### 13.4 String

字符串的详细操作见下一节。

---

## 十四、字符串操作

Rust 的字符串处理相对复杂，主要有两种字符串类型：
- `&str`：字符串切片，固定大小，不可变，通常以引用形式使用
- `String`：可增长的、可变的、有所有权的字符串类型

### 14.1 创建字符串

```rust
let s1 = String::new();                    // 空字符串
let s2 = "hello".to_string();              // 从 &str 创建
let s3 = String::from("hello");            // 从 &str 创建
let s4 = format!("{} {}", "hello", "world");  // 格式化
```

### 14.2 更新字符串

```rust
let mut s = String::from("foo");
s.push_str("bar");        // 追加字符串切片
s.push('!');              // 追加字符

let s2 = String::from("hello");
let s3 = s2 + " world";   // 使用 + 运算符（s2 的所有权会被移动）
```

### 14.3 字符串拼接

```rust
let s1 = String::from("tic");
let s2 = String::from("tac");
let s3 = String::from("toe");

let s = format!("{}-{}-{}", s1, s2, s3);  // 推荐，不会获取所有权
```

### 14.4 字符串长度

```rust
let s = String::from("hello");
println!("{}", s.len());        // 5（字节长度）

let s = String::from("你好");
println!("{}", s.len());        // 6（每个中文字符占 3 字节）
println!("{}", s.chars().count());  // 2（字符数）
```

### 14.5 字符串索引

Rust 不允许用整数索引访问字符串中的字符（因为 UTF-8 字符长度不固定）。

```rust
let s = String::from("hello");
// let c = s[0];   // 错误！

// 使用 chars() 迭代
for c in s.chars() {
    println!("{}", c);
}

// 使用 bytes() 迭代字节
for b in s.bytes() {
    println!("{}", b);
}
```

### 14.6 字符串切片

```rust
let s = String::from("hello world");
let hello = &s[0..5];     // 按字节切片，必须在字符边界处
let world = &s[6..11];
```

### 14.7 查找与包含

```rust
let s = String::from("hello world");

println!("{}", s.contains("world"));   // true
println!("{}", s.starts_with("hello")); // true
println!("{}", s.ends_with("world"));   // true

let index = s.find("world");            // 返回 Option<usize>
match index {
    Some(i) => println!("位置：{}", i),
    None => println!("未找到"),
}
```

### 14.8 替换

```rust
let s = String::from("hello world");
let replaced = s.replace("world", "Rust");  // "hello Rust"
```

### 14.9 分割

```rust
let s = String::from("a,b,c,d");
for part in s.split(',') {
    println!("{}", part);
}

let parts: Vec<&str> = s.split(',').collect();
```

### 14.10 去除空白

```rust
let s = String::from("  hello world  ");
let trimmed = s.trim();         // 去掉两端空白
let left = s.trim_start();      // 去掉开头空白
let right = s.trim_end();       // 去掉结尾空白
```

---

## 十五、错误处理

Rust 将错误分为两大类：
- **可恢复错误**（recoverable）：如文件未找到，使用 `Result<T, E>`
- **不可恢复错误**（unrecoverable）：如数组越界，使用 `panic!`

### 15.1 panic! 宏

遇到不可恢复的错误时使用：

```rust
fn main() {
    // panic!("崩溃了！");  // 直接触发 panic

    let v = vec![1, 2, 3];
    v[100];  // 越界访问，自动触发 panic
}
```

### 15.2 Result 枚举

```rust
enum Result<T, E> {
    Ok(T),   // 成功，包含值
    Err(E),  // 失败，包含错误信息
}
```

**使用 match 处理：**

```rust
use std::fs::File;

fn main() {
    let result = File::open("hello.txt");

    let file = match result {
        Ok(f) => f,
        Err(error) => {
            panic!("打开文件失败：{:?}", error);
        }
    };
}
```

**unwrap 和 expect：**

```rust
let f = File::open("hello.txt").unwrap();
// 如果 Ok，返回值；如果 Err，调用 panic!

let f = File::open("hello.txt").expect("无法打开文件");
// 与 unwrap 类似，但可以自定义错误消息
```

### 15.3 ? 运算符

用于传播错误，只能在返回 Result 的函数中使用。

```rust
use std::fs::File;
use std::io::Read;

fn read_username_from_file() -> Result<String, std::io::Error> {
    let mut f = File::open("username.txt")?;
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}
```

`?` 运算符的作用：
- 如果结果是 `Ok`，取出值继续执行
- 如果结果是 `Err`，将错误作为函数返回值返回

### 15.4 Option 枚举

表示可能存在也可能不存在的值。

```rust
fn find_first_even(numbers: &[i32]) -> Option<i32> {
    for &n in numbers {
        if n % 2 == 0 {
            return Some(n);
        }
    }
    None
}

fn main() {
    let nums = vec![1, 3, 5, 7];
    match find_first_even(&nums) {
        Some(n) => println!("第一个偶数：{}", n),
        None => println!("没有偶数"),
    }
}
```

**Option 的常用方法：**

```rust
let x: Option<i32> = Some(5);

x.is_some();    // true
x.is_none();    // false
x.unwrap();     // 5（如果是 None 会 panic）
x.unwrap_or(0); // 5（如果是 None 返回默认值）
x.map(|v| v * 2);  // Some(10)
x.and_then(|v| if v > 0 { Some(v * 2) } else { None });
```

### 15.5 错误处理的组合

```rust
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err(String::from("除数不能为零"))
    } else {
        Ok(a / b)
    }
}

fn main() {
    match divide(10.0, 2.0) {
        Ok(result) => println!("结果：{}", result),
        Err(e) => println!("错误：{}", e),
    }
}
```

---

## 十六、模块系统

### 16.1 mod 定义模块

```rust
// 定义模块
mod front_of_house {
    pub mod hosting {   // pub 使其对外可见
        pub fn add_to_waitlist() {
            println!("添加到等待列表");
        }

        fn seat_at_table() {   // 私有函数
            println("安排座位");
        }
    }

    mod serving {
        fn take_order() {}
    }
}

fn main() {
    // 调用模块中的函数
    front_of_house::hosting::add_to_waitlist();
}
```

### 16.2 use 引入

```rust
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

use front_of_house::hosting;

fn main() {
    hosting::add_to_waitlist();
}
```

**as 重命名：**

```rust
use front_of_house::hosting as h;

fn main() {
    h::add_to_waitlist();
}
```

### 16.3 crate

- **crate** 是 Rust 的编译单元
- 一个 crate 可以是二进制项目或库项目
- `src/main.rs` 是二进制 crate 的根
- `src/lib.rs` 是库 crate 的根

---

## 十七、包管理（Cargo）

### 17.1 Cargo.toml

```toml
[package]
name = "my_project"
version = "0.1.0"
edition = "2021"
authors = ["Your Name <you@example.com>"]

[dependencies]
serde = "1.0"           # 引入 serde crate，版本 1.0.x
rand = "0.8"
reqwest = { version = "0.11", features = ["json"] }  # 带特性
```

### 17.2 crates.io

[crates.io](https://crates.io) 是 Rust 的官方包注册表，可以搜索和下载第三方库。

### 17.3 Cargo 常用命令

| 命令 | 说明 |
|------|------|
| `cargo new project_name` | 创建新项目 |
| `cargo new --lib project_name` | 创建库项目 |
| `cargo build` | 编译项目 |
| `cargo run` | 编译并运行 |
| `cargo test` | 运行测试 |
| `cargo check` | 检查编译 |
| `cargo clean` | 清理构建产物 |
| `cargo update` | 更新依赖 |
| `cargo doc` | 生成文档 |
| `cargo publish` | 发布到 crates.io |

---

## 十八、文件操作

### 18.1 读取文件

```rust
use std::fs;
use std::io::Read;

fn main() -> std::io::Result<()> {
    // 一次性读取整个文件
    let content = fs::read_to_string("test.txt")?;
    println!("文件内容：{}", content);

    // 读取字节
    let bytes = fs::read("test.txt")?;

    // 逐行读取
    let file = fs::File::open("test.txt")?;
    let reader = std::io::BufReader::new(file);
    for line in reader.lines() {
        println!("{}", line?);
    }

    Ok(())
}
```

### 18.2 写入文件

```rust
use std::fs;
use std::io::Write;

fn main() -> std::io::Result<()> {
    // 写入文件（覆盖）
    fs::write("output.txt", "Hello, Rust!\n")?;

    // 追加写入
    let mut file = fs::OpenOptions::new()
        .append(true)
        .create(true)
        .open("output.txt")?;
    writeln!(file, "追加一行")?;

    Ok(())
}
```

### 18.3 文件系统操作

```rust
use std::fs;

fn main() -> std::io::Result<()> {
    fs::create_dir("new_dir")?;           // 创建目录
    fs::create_dir_all("a/b/c")?;         // 递归创建目录
    fs::copy("a.txt", "b.txt")?;          // 复制文件
    fs::rename("a.txt", "c.txt")?;        // 重命名/移动
    fs::remove_file("c.txt")?;            // 删除文件
    fs::remove_dir("new_dir")?;           // 删除空目录
    fs::remove_dir_all("a")?;             // 递归删除目录

    // 读取目录
    for entry in fs::read_dir(".")? {
        let entry = entry?;
        println!("{:?}", entry.file_name());
    }

    Ok(())
}
```

---

## 十九、网络请求

使用 `reqwest` crate 进行 HTTP 请求。

### 19.1 添加依赖

在 Cargo.toml 中添加：

```toml
[dependencies]
reqwest = { version = "0.11", features = ["json", "blocking"] }
tokio = { version = "1", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
```

### 19.2 阻塞式 GET 请求

```rust
use reqwest;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let body = reqwest::blocking::get("https://httpbin.org/get")?
        .text()?;
    println!("{}", body);
    Ok(())
}
```

### 19.3 异步 GET 请求

```rust
use reqwest;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let body = reqwest::get("https://httpbin.org/get")
        .await?
        .text()
        .await?;
    println!("{}", body);
    Ok(())
}
```

### 19.4 POST 请求（JSON）

```rust
use reqwest;
use serde::Deserialize;

#[derive(Deserialize, Debug)]
struct Post {
    userId: u32,
    id: u32,
    title: String,
    body: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let post: Post = reqwest::Client::new()
        .post("https://jsonplaceholder.typicode.com/posts")
        .json(&serde_json::json!({
            "title": "foo",
            "body": "bar",
            "userId": 1
        }))
        .send()
        .await?
        .json()
        .await?;

    println!("{:?}", post);
    Ok(())
}
```

### 19.5 使用标准库（仅 TCP）

Rust 标准库提供了底层的 TCP/UDP 网络能力：

```rust
use std::io::Read;
use std::net::TcpStream;

fn main() -> std::io::Result<()> {
    let mut stream = TcpStream::connect("example.com:80")?;
    stream.write_all(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")?;

    let mut response = String::new();
    stream.read_to_string(&mut response)?;
    println!("{}", response);

    Ok(())
}
```

---

## 二十、正则表达式

使用 `regex` crate。

### 20.1 添加依赖

```toml
[dependencies]
regex = "1"
```

### 20.2 基本使用

```rust
use regex::Regex;

fn main() {
    // 编译正则表达式
    let re = Regex::new(r"\d+").unwrap();

    // 检查是否匹配
    println!("{}", re.is_match("abc123def"));  // true

    // 查找第一个匹配
    if let Some(caps) = re.find("abc123def456") {
        println!("匹配到：{}", caps.as_str());  // 123
    }

    // 查找所有匹配
    for cap in re.find_iter("abc123def456") {
        println!("{}", cap.as_str());
    }
}
```

### 20.3 捕获组

```rust
use regex::Regex;

fn main() {
    let re = Regex::new(r"(\d{4})-(\d{2})-(\d{2})").unwrap();
    let text = "日期：2024-01-15 和 2024-12-25";

    for caps in re.captures_iter(text) {
        println!("年份：{}, 月份：{}, 日期：{}", &caps[1], &caps[2], &caps[3]);
    }
}
```

### 20.4 替换

```rust
use regex::Regex;

fn main() {
    let re = Regex::new(r"\d+").unwrap();
    let text = "价格：100元，数量：5个";

    // 替换所有匹配
    let result = re.replace_all(text, "XXX");
    println!("{}", result);  // 价格：XXX元，数量：XXX个

    // 使用闭包进行替换
    let result = re.replace_all(text, |caps: &regex::Captures| {
        let num: i32 = caps[0].parse().unwrap();
        format!("{}", num * 2)
    });
    println!("{}", result);  // 价格：200元，数量：10个
}
```

### 20.5 常用正则模式

```rust
// 邮箱
let email_re = Regex::new(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$").unwrap();

// IP 地址（简化版）
let ip_re = Regex::new(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}").unwrap();

// URL（简化版）
let url_re = Regex::new(r"https?://[^\s]+").unwrap();

// 中文字符
let zh_re = Regex::new(r"[\u{4e00}-\u{9fa5}]+").unwrap();
```

---

## 二十一、Rust 在安全领域的应用

### 21.1 内存安全

Rust 最大的安全优势是**编译时内存安全保证**：

- **没有空指针**：使用 `Option<T>` 强制处理空值
- **没有悬垂指针**：借用检查器确保引用始终有效
- **没有缓冲区溢出**：数组访问有运行时边界检查
- **没有数据竞争**：所有权系统保证线程安全
- **没有 use-after-free**：所有权转移后原变量无法使用
- **没有 double-free**：所有权唯一，析构自动执行

这些特性使得用 Rust 编写的程序从根源上消除了大量 C/C++ 中常见的安全漏洞。

### 21.2 安全工具开发

Rust 非常适合开发安全工具：

- **静态分析工具**：Rust 的类型系统和所有权模型有助于编写准确的分析器
- **模糊测试（Fuzzing）**：`cargo-fuzz`、`honggfuzz-rs` 等框架
- **二进制分析**：`goblin`、`capstone-rs` 等库
- **网络安全工具**：`nmap` 替代品、端口扫描器等
- **密码学库**：`ring`、`RustCrypto` 项目等

### 21.3 漏洞利用

虽然 Rust 本身很安全，但它也可以用于编写漏洞利用代码：

- **Shellcode 开发**：Rust 可以编译成裸机代码
- **Exploit 开发**：可以精确控制内存布局
- **ROP 链构造**：可以编写工具辅助漏洞利用

### 21.4 逆向分析

- **反汇编工具**：基于 `capstone-rs` 开发反汇编器
- **PE/ELF 解析**：`goblin` crate 支持多种二进制格式解析
- **符号执行**：Rust 的性能适合开发符号执行引擎

### 21.5 区块链安全

- 许多区块链项目使用 Rust 开发（Solana、Polkadot 等）
- 智能合约审计和安全分析
- 加密货币安全工具

### 21.6 Web 安全

- **WebAssembly 安全**：Rust 是 Wasm 的主要源语言之一
- **Web 服务安全**：Rust 的 Web 框架（Actix-web、Axum）内存安全
- **SSRF、SQL 注入防护**：类型系统和所有权机制减少安全漏洞

---

## 参考资源

- [Rust 官方网站](https://www.rust-lang.org/)
- [Rust 程序设计语言（The Book）](https://doc.rust-lang.org/book/)
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
- [crates.io](https://crates.io/)
- [Rust 标准库文档](https://doc.rust-lang.org/std/)
