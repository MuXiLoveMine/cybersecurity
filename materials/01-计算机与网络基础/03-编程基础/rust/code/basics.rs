// basics.rs —— Rust 基础语法示例（安全从业者视角）
//
// 涵盖内容：
//   1. 变量与数据类型
//   2. 所有权与借用
//   3. 流程控制
//   4. 结构体与枚举
//   5. 模式匹配
//   6. 错误处理
//   7. 集合类型
//   8. 函数与闭包
//
// 编译运行：
//   rustc basics.rs -o basics
//   ./basics   (Linux/macOS)
//   basics.exe (Windows)
//
// 注意：本脚本用于学习参考，包含安全视角的注释说明。

use std::collections::{HashMap, HashSet};
use std::fmt;

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

// ============================================================
// 1. 变量与数据类型
// ============================================================

fn demo_variables_and_types() {
    print_section("【1. 变量与数据类型】");

    print_subsection("1.1 变量：默认不可变");

    let x = 5;
    println!("  x = {}", x);
    // x = 6;  // 编译错误！Rust 变量默认不可变
    println!("  💡 Rust 变量默认不可变（immutable）");
    println!("     减少意外修改导致的 bug");

    // 可变变量
    let mut y = 5;
    println!();
    println!("  可变变量 mut y = {}", y);
    y = 10;
    println!("  修改后 y = {}", y);

    print_subsection("1.2 常量");

    const MAX_POINTS: u32 = 100_000;
    const SECONDS_IN_HOUR: u32 = 3600;
    println!("  MAX_POINTS = {}", MAX_POINTS);
    println!("  SECONDS_IN_HOUR = {}", SECONDS_IN_HOUR);
    println!("  常量必须标注类型，编译时求值");

    print_subsection("1.3 基本数据类型");

    // 整数类型
    let _a: i32 = 42;        // 有符号 32 位（默认）
    let _b: u64 = 100;       // 无符号 64 位
    let _c: u8 = 255;        // 无符号 8 位
    let _d: i128 = 0;        // 128 位整数

    // 浮点类型
    let _e: f32 = 3.14;      // 单精度
    let _f: f64 = 2.71828;   // 双精度（默认）

    // 布尔类型
    let _g: bool = true;
    let _h: bool = false;

    // 字符类型（Unicode，4 字节）
    let _i: char = 'A';
    let _j: char = '🦀';     // 支持 emoji
    let _k: char = '中';     // 支持中文

    println!("  整数类型:");
    println!("    长度     有符号    无符号");
    println!("    8-bit    i8       u8");
    println!("    16-bit   i16      u16");
    println!("    32-bit   i32      u32 (默认整数类型)");
    println!("    64-bit   i64      u64");
    println!("    128-bit  i128     u128");
    println!("    arch     isize    usize (指针大小)");
    println!();
    println!("  浮点类型:");
    println!("    f32 - 单精度");
    println!("    f64 - 双精度（默认）");
    println!();
    println!("  其他类型:");
    println!("    bool - true/false");
    println!("    char - Unicode 字符，4 字节");

    print_subsection("1.4 复合类型");

    // 元组（tuple）
    let tup: (i32, f64, char) = (500, 6.4, 'J');
    println!("  元组: ({}, {}, {})", tup.0, tup.1, tup.2);

    // 解构元组
    let (x, y, z) = tup;
    println!("  解构后: x={}, y={}, z={}", x, y, z);

    // 数组（固定长度，同一类型）
    let arr: [i32; 5] = [1, 2, 3, 4, 5];
    println!();
    println!("  数组: {:?}", arr);
    println!("  长度: {}", arr.len());
    println!("  第一个元素: {}", arr[0]);

    // 安全访问（不会 panic）
    match arr.get(100) {
        Some(val) => println!("  索引 100 的值: {}", val),
        None => println!("  索引 100: 越界（安全返回 None）"),
    }
    println!();
    print_safe("数组越界不会导致内存破坏，而是返回 None 或 panic");
    println!("     比 C/C++ 的缓冲区溢出安全得多");

    print_subsection("1.5 字符串");

    let s1: &str = "hello";       // 字符串切片（引用，只读）
    let s2: String = String::from("world"); // 拥有的字符串（可变）

    println!("  &str = \"{}\" (字符串切片，引用)", s1);
    println!("  String = \"{}\" (拥有的字符串)", s2);
    println!();

    // 字符串拼接
    let combined = format!("{}_{}", s1, s2);
    println!("  拼接: {}", combined);
    println!();

    // 字符串不可以用索引访问（因为是 UTF-8）
    println!("  💡 Rust 字符串不支持 s[0] 索引访问");
    println!("     因为 UTF-8 是变长编码，索引位置不一定是字符边界");
    println!();

    // 正确的遍历方式
    print!("  chars(): ");
    for c in "你好🦀".chars() {
        print!("{} ", c);
    }
    println!();

    print_subsection("1.6 隐藏（Shadowing）");

    let spaces = "   ";
    println!("  spaces = \"{}\" (字符串)", spaces);
    let spaces = spaces.len();
    println!("  let spaces = spaces.len() → {} (数字)", spaces);
    println!("  💡 可以重复声明同名变量，甚至改变类型");
    println!("     和 mut 不同，shadowing 后变量仍然不可变");
}

// ============================================================
// 2. 所有权与借用（Rust 核心概念）
// ============================================================

fn demo_ownership() {
    print_section("【2. 所有权与借用】");

    print_subsection("2.1 所有权规则");

    println!("  Rust 所有权三大规则：");
    println!("    1. 每个值都有一个所有者（owner）");
    println!("    2. 同一时间只能有一个所有者");
    println!("    3. 当所有者离开作用域时，值将被丢弃（drop）");
    println!();

    let s1 = String::from("hello");
    println!("  s1 = \"{}\" (s1 是字符串的所有者)", s1);

    let s2 = s1;  // 所有权移动（move）
    println!("  let s2 = s1;  → 所有权移动到 s2");
    println!("  s2 = \"{}\"", s2);
    // println!("{}", s1);  // 编译错误！s1 不再有效
    println!("  此时 s1 已经无效（值被 move 到 s2 了）");
    println!();
    print_safe("所有权移动确保每个值只有一个所有者");
    println!("     从根源上避免了 double free");

    print_subsection("2.2 借用（引用）");

    println!("  为了不转移所有权，可以使用引用（借用）");
    println!();

    let s1 = String::from("hello");
    let len = calculate_length(&s1);  // 借用，不转移所有权
    println!("  \"{}\" 的长度是 {}", s1, len);
    println!("  s1 仍然有效（只是被借用了）");

    print_subsection("2.3 可变引用");

    let mut s = String::from("hello");
    println!("  修改前: {}", s);
    change(&mut s);  // 可变借用
    println!("  修改后: {}", s);

    print_subsection("2.4 借用规则");

    println!("  借用两大规则：");
    println!("    1. 同一时间，要么有 1 个可变引用，要么有 N 个不可变引用");
    println!("    2. 引用必须总是有效的（不能有悬垂引用）");
    println!();

    let r1 = &s;   // 不可变引用
    let r2 = &s;   // 多个不可变引用 OK
    println!("  r1 = \"{}\", r2 = \"{}\"", r1, r2);
    println!("  可以同时有多个不可变引用");
    // let r3 = &mut s;  // 编译错误！不能同时有可变和不可变引用
    println!();
    print_safe("借用规则在编译期保证：");
    println!("     没有数据竞争（data race）");
    println!("     没有悬垂引用（dangling reference）");
    println!("     没有迭代器失效");

    print_subsection("2.5 所有权与安全");

    println!("  Rust 所有权系统消除的内存安全问题：");
    println!("    ✅ Use-After-Free（释放后使用）");
    println!("    ✅ Double Free（重复释放）");
    println!("    ✅ 悬垂指针");
    println!("    ✅ 数据竞争");
    println!("    ✅ 迭代器失效");
    println!();
    println!("  这些都是在编译期检查的，运行时没有额外开销");
    println!("  这就是 Rust 内存安全的秘诀！");
}

fn calculate_length(s: &String) -> usize {
    s.len()
}  // s 离开作用域，但因为不拥有所有权，所以什么都不发生

fn change(s: &mut String) {
    s.push_str(", world");
}

// ============================================================
// 3. 流程控制
// ============================================================

fn demo_control_flow() {
    print_section("【3. 流程控制】");

    print_subsection("3.1 if-else");

    let number = 6;
    println!("  number = {}", number);

    if number % 4 == 0 {
        println!("  能被 4 整除");
    } else if number % 3 == 0 {
        println!("  能被 3 整除");
    } else if number % 2 == 0 {
        println!("  能被 2 整除");
    } else {
        println!("  不能被 2、3、4 整除");
    }

    // if 是表达式，可以赋值
    let condition = true;
    let num = if condition { 5 } else { 6 };
    println!("  if 表达式: condition={}, num={}", condition, num);

    print_subsection("3.2 match 模式匹配");

    let number = 2;
    print!("  match {} → ", number);
    match number {
        1 => println!("一"),
        2 => println!("二"),
        3 => println!("三"),
        _ => println!("其他"),  // _ 是通配符，匹配所有情况
    }

    // match 是穷尽的（exhaustive），必须处理所有情况
    // 编译器会检查是否遗漏

    // 枚举 + match
    let msg = Message::Write("hello".to_string());
    print!("  match Message::Write → ");
    match msg {
        Message::Quit => println!("退出"),
        Message::Move { x, y } => println!("移动到 ({}, {})", x, y),
        Message::Write(text) => println!("写入: {}", text),
        Message::ChangeColor(r, g, b) => println!("颜色: {},{},{}", r, g, b),
    }

    print_subsection("3.3 循环");

    // for 循环
    print!("  for 1..=5: ");
    for i in 1..=5 {
        print!("{} ", i);
    }
    println!();

    // 遍历数组
    let arr = [10, 20, 30, 40, 50];
    print!("  for in arr: ");
    for elem in arr.iter() {
        print!("{} ", elem);
    }
    println!();

    // while 循环
    print!("  while 倒计时: ");
    let mut n = 5;
    while n > 0 {
        print!("{} ", n);
        n -= 1;
    }
    println!("GO!");

    // loop（无限循环，break 退出）
    let mut count = 0;
    let result = loop {
        count += 1;
        if count == 5 {
            break count * 2;  // break 可以带返回值
        }
    };
    println!("  loop 结果: count=5, result={}", result);

    // if let（只关心一种模式时）
    let some_value = Some(3);
    if let Some(3) = some_value {
        println!("  if let Some(3) = Some(3) → 匹配成功");
    }

    // while let
    let mut stack = vec![1, 2, 3];
    print!("  while let pop: ");
    while let Some(top) = stack.pop() {
        print!("{} ", top);
    }
    println!();
}

// 定义在外面的枚举（给 demo_control_flow 用）
#[derive(Debug)]
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}

// ============================================================
// 4. 结构体与枚举
// ============================================================

#[derive(Debug)]
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

    // 方法（&self 借用）
    fn get_username(&self) -> &str {
        &self.username
    }

    fn is_adult(&self) -> bool {
        self.age >= 18
    }

    // 可变方法（&mut self）
    fn deactivate(&mut self) {
        self.active = false;
    }
}

// 为 User 实现 Display trait，支持 println!("{}", user)
impl fmt::Display for User {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "User{{username: \"{}\", email: \"{}\", age: {}, active: {}}}",
            self.username, self.email, self.age, self.active
        )
    }
}

fn demo_structs_and_enums() {
    print_section("【4. 结构体与枚举】");

    print_subsection("4.1 结构体");

    let mut user = User::new("alice".to_string(), "alice@example.com".to_string(), 25);
    println!("  用户: {}", user);
    println!("  用户名: {}", user.get_username());
    println!("  是否成年: {}", user.is_adult());

    user.deactivate();
    println!("  停用后 active = {}", user.active);

    print_subsection("4.2 Option<T>：替代 null");

    println!("  Rust 没有 null！用 Option<T> 表示可能不存在的值");
    println!("  enum Option<T> {{ Some(T), None }}");
    println!();

    // 使用 Option
    match find_user(1) {
        Some(name) => println!("  找到用户 id=1: {}", name),
        None => println!("  用户 id=1: 不存在"),
    }

    match find_user(999) {
        Some(name) => println!("  找到用户 id=999: {}", name),
        None => println!("  用户 id=999: 不存在"),
    }

    println!();
    print_safe("Option 强制你处理空值的情况");
    println!("     不会出现空指针异常（NullPointerException）");
    println!("     这是 Rust 安全的重要原因之一");

    print_subsection("4.3 Result<T, E>：错误处理");

    println!("  可恢复错误用 Result<T, E>");
    println!("  enum Result<T, E> {{ Ok(T), Err(E) }}");
    println!();

    match divide(10, 2) {
        Ok(result) => println!("  10 / 2 = {}", result),
        Err(e) => println!("  错误: {}", e),
    }

    match divide(10, 0) {
        Ok(result) => println!("  10 / 0 = {}", result),
        Err(e) => println!("  10 / 0 错误: {}", e),
    }

    print_subsection("4.4 枚举与模式匹配的安全意义");

    println!("  1. match 是穷尽的：编译器检查是否处理了所有情况");
    println!("     不会遗漏某个分支导致的 bug");
    println!();
    println!("  2. Option/Result 强制处理边缘情况");
    println!("     空值、错误不能被忽略");
    println!();
    println!("  3. 类型系统表达力强：非法状态用类型消除");
    println!("     例如：用不同的结构体表示不同状态");
}

fn find_user(id: u32) -> Option<String> {
    match id {
        1 => Some("Alice".to_string()),
        2 => Some("Bob".to_string()),
        3 => Some("Charlie".to_string()),
        _ => None,
    }
}

fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err("除数不能为零".to_string())
    } else {
        Ok(a / b)
    }
}

// ============================================================
// 5. 错误处理
// ============================================================

fn demo_error_handling() {
    print_section("【5. 错误处理】");

    print_subsection("5.1 错误分类");

    println!("  Rust 错误分两类：");
    println!("    1. 不可恢复错误：panic!()");
    println!("    2. 可恢复错误：Result<T, E>");
    println!();

    // panic 是安全的失败，不会内存破坏
    // panic!("发生严重错误！");  // 取消注释测试

    print_subsection("5.2 Result 处理方式");

    let result = divide(10, 2);

    // 方式 1：match
    match result {
        Ok(val) => println!("  match: 结果 = {}", val),
        Err(e) => println!("  match: 错误 = {}", e),
    }

    // 方式 2：if let
    if let Ok(val) = divide(20, 4) {
        println!("  if let: 结果 = {}", val);
    }

    // 方式 3：unwrap（不推荐，出错会 panic）
    // let val = divide(10, 0).unwrap();  // 会 panic

    // 方式 4：expect（类似 unwrap，自定义错误信息）
    // let val = divide(10, 0).expect("除法失败");

    // 方式 5：组合子
    let doubled = divide(10, 2).map(|x| x * 2);
    println!("  map 双倍: {:?}", doubled);

    let safe_result = divide(10, 0).unwrap_or(0);
    println!("  unwrap_or: 除以 0 的默认值 = {}", safe_result);

    print_subsection("5.3 ? 运算符：传播错误");

    println!("  ? 运算符可以简洁地传播错误");
    println!("  只能用在返回 Result 或 Option 的函数中");
    println!();

    // 示例函数（在实际项目中常用）
    // fn read_and_parse() -> Result<i32, Box<dyn Error>> {
    //     let content = fs::read_to_string("file.txt")?;
    //     let num: i32 = content.trim().parse()?;
    //     Ok(num)
    // }

    println!("  传统写法（6 行）:");
    println!("    let f = match File::open(\"file.txt\") {{");
    println!("        Ok(f) => f,");
    println!("        Err(e) => return Err(e),");
    println!("    }};");
    println!();
    println!("  ? 运算符写法（1 行）:");
    println!("    let f = File::open(\"file.txt\")?;");

    print_subsection("5.4 错误处理安全要点");

    print_safe("错误必须显式处理，不会被静默忽略");
    println!("     Result 类型编译器会提醒你处理");
    println!();
    print_warn("避免在生产代码中使用 unwrap() 和 expect()");
    println!("     除非你 100% 确定不会出错");
    println!("     否则可能导致服务 panic（虽然安全但会崩溃）");
}

// ============================================================
// 6. 集合类型
// ============================================================

fn demo_collections() {
    print_section("【6. 集合类型】");

    print_subsection("6.1 Vec<T> 动态数组");

    let mut v: Vec<i32> = Vec::new();
    v.push(1);
    v.push(2);
    v.push(3);
    v.push(4);
    v.push(5);

    println!("  Vec: {:?}", v);
    println!("  长度: {}", v.len());
    println!("  第一个: {}", v[0]);
    println!();

    // 安全访问（返回 Option，越界返回 None）
    match v.get(100) {
        Some(val) => println!("  v[100] = {}", val),
        None => println!("  v[100] = None (越界，安全返回)"),
    }
    println!();

    print_safe("越界访问不会导致内存破坏");
    println!("     .get() 返回 Option，安全优雅");
    println!("     [] 越界会 panic，但也是安全终止，不会有 UB");

    print_subsection("6.2 HashMap<K, V> 哈希表");

    let mut scores: HashMap<String, i32> = HashMap::new();
    scores.insert("Alice".to_string(), 95);
    scores.insert("Bob".to_string(), 87);
    scores.insert("Charlie".to_string(), 92);

    println!("  HashMap: {:?}", scores);
    println!();

    // 安全访问
    match scores.get("Alice") {
        Some(score) => println!("  Alice 的分数: {}", score),
        None => println!("  没有 Alice 的记录"),
    }

    match scores.get("Nobody") {
        Some(score) => println!("  Nobody 的分数: {}", score),
        None => println!("  没有 Nobody 的记录"),
    }

    println!();
    println!("  遍历:");
    for (name, score) in &scores {
        println!("    {}: {}", name, score);
    }

    print_subsection("6.3 HashSet<T> 集合");

    let mut set: HashSet<i32> = HashSet::new();
    set.insert(1);
    set.insert(2);
    set.insert(3);
    set.insert(1);  // 重复，不会添加

    println!("  HashSet: {:?}", set);
    println!("  包含 1: {}", set.contains(&1));
    println!("  包含 99: {}", set.contains(&99));
    println!("  长度: {}", set.len());

    print_subsection("6.4 迭代器");

    let nums = vec![1, 2, 3, 4, 5];
    println!("  原始: {:?}", nums);

    // map：转换每个元素
    let doubled: Vec<i32> = nums.iter().map(|x| x * 2).collect();
    println!("  双倍: {:?}", doubled);

    // filter：过滤
    let evens: Vec<&i32> = nums.iter().filter(|x| *x % 2 == 0).collect();
    println!("  偶数: {:?}", evens);

    // sum / max / min
    let sum: i32 = nums.iter().sum();
    let max = nums.iter().max();
    println!("  总和: {}", sum);
    println!("  最大值: {:?}", max);
}

// ============================================================
// 7. 函数与闭包
// ============================================================

fn demo_functions_and_closures() {
    print_section("【7. 函数与闭包】");

    print_subsection("7.1 函数");

    println!("  add(3, 5) = {}", add(3, 5));
    println!("  greet(\"Alice\") = {}", greet("Alice"));

    print_subsection("7.2 闭包");

    println!("  闭包：可以捕获环境变量的匿名函数");
    println!();

    let factor = 10;
    let multiply = |x: i32| x * factor;  // 捕获 factor

    println!("  factor = {}", factor);
    println!("  multiply(5) = {}", multiply(5));
    println!("  multiply(3) = {}", multiply(3));
    println!();

    // 闭包作为参数
    let numbers = vec![1, 2, 3, 4, 5];
    let doubled: Vec<i32> = numbers.iter().map(|x| x * 2).collect();
    println!("  map 闭包: {:?}", doubled);

    print_subsection("7.3 高阶函数");

    println!("  Rust 函数是一等公民，可以作为参数和返回值");
    println!();

    let result = apply_twice(5, add_one);
    println!("  apply_twice(5, add_one) = {}", result);

    let result2 = apply_twice(10, |x| x * 3);
    println!("  apply_twice(10, |x| x*3) = {}", result2);
}

fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

fn add_one(x: i32) -> i32 {
    x + 1
}

fn apply_twice(x: i32, f: fn(i32) -> i32) -> i32 {
    f(f(x))
}

// ============================================================
// 主函数
// ============================================================

fn main() {
    println!();
    println!("============================================================");
    println!("  Rust 基础语法示例（安全从业者视角）");
    println!("  Rust Basics for Security Practitioners");
    println!("============================================================");
    println!();
    println!("  Rust 版本: {}", std::env!("CARGO_PKG_VERSION").unwrap_or("unknown"));
    println!("  操作系统: {}", std::env::consts::OS);
    println!("  架构: {}", std::env::consts::ARCH);

    // 1. 变量与数据类型
    demo_variables_and_types();

    // 2. 所有权与借用
    demo_ownership();

    // 3. 流程控制
    demo_control_flow();

    // 4. 结构体与枚举
    demo_structs_and_enums();

    // 5. 错误处理
    demo_error_handling();

    // 6. 集合类型
    demo_collections();

    // 7. 函数与闭包
    demo_functions_and_closures();

    println!();
    println!("============================================================");
    println!("  所有示例执行完毕");
    println!("  涵盖：变量、数据类型、所有权、借用、流程控制、");
    println!("  结构体、枚举、错误处理、集合、闭包");
    println!("============================================================");
    println!();
}
