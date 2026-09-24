# match_if_let

> **分类**：模式匹配与控制流
> **说明**：Rust 的 match 和 if let 模式匹配

---

## 语法

```rust
match value {\n  pattern => expression,\n  _ => default,\n}
```

## 控制流

if/else / loop / while / for / match / if let / while let

## 模式匹配

字面量 / 变量 / 通配符 _ / 结构体/枚举解构 / 范围 / 守卫

## 示例代码

```rust
fn main() {
    // if/else
    let age = 18;
    if age >= 18 {
        println!("成年");
    } else if age >= 6 {
        println!("少年");
    } else {
        println!("儿童");
    }

    // if 表达式（可以赋值）
    let status = if age >= 18 { "成年" } else { "未成年" };

    // loop 循环（无限循环）
    let mut count = 0;
    loop {
        count += 1;
        if count == 5 {
            break;
        }
    }

    // loop 返回值
    let mut counter = 0;
    let result = loop {
        counter += 1;
        if counter == 10 {
            break counter * 2;  // break 可以带返回值
        }
    };

    // while 循环
    let mut number = 3;
    while number != 0 {
        println!("{}!", number);
        number -= 1;
    }

    // for 循环（遍历迭代器）
    let arr = [10, 20, 30, 40, 50];
    for element in arr.iter() {
        println!("值: {}", element);
    }

    // 范围
    for i in 1..=5 {  // 1到5（包含）
        println!("{}", i);
    }
    for i in 0..5 {   // 0到4（不包含5）
        println!("{}", i);
    }

    // ===== match =====
    let number = 3;
    match number {
        1 => println!("一"),
        2 => println!("二"),
        3 => println!("三"),
        4..=9 => println!("四到九"),
        _ => println!("其他"),  // 通配符
    }

    // match 表达式返回值
    let day_name = match number {
        1 => "星期一",
        2 => "星期二",
        3 => "星期三",
        _ => "其他",
    };

    // 匹配枚举
    enum Message {
        Quit,
        Move { x: i32, y: i32 },
        Write(String),
        ChangeColor(i32, i32, i32),
    }

    let msg = Message::Write(String::from("hello"));
    match msg {
        Message::Quit => println!("退出"),
        Message::Move { x, y } => println!("移动到 ({}, {})", x, y),
        Message::Write(text) => println!("文本: {}", text),
        Message::ChangeColor(r, g, b) => println!("颜色: {},{},{}", r, g, b),
    }

    // 匹配 Option
    let some_value = Some(42);
    match some_value {
        Some(0) => println!("零"),
        Some(n) if n > 0 => println!("正数: {}", n),  // 匹配守卫
        None => println!("空"),
        _ => (),
    }

    // if let（只关心一种模式时）
    let some_u8 = Some(3u8);
    if let Some(3) = some_u8 {
        println!("三");
    } else {
        println!("不是三");
    }

    // while let
    let mut stack = Vec::new();
    stack.push(1);
    stack.push(2);
    stack.push(3);
    while let Some(top) = stack.pop() {
        println!("{}", top);
    }
}
```
