# variable_rust

> **分类**：变量与类型
> **说明**：Rust 变量和数据类型

---

## 语法

```rust
let variable: type = value;\nlet mut variable = value;  // 可变
```

## 标量类型

i8/i16/i32/i64/i128/isize / u8/u16/u32/u64/u128/usize / f32/f64 / bool / char

## 复合类型

tuple / array / struct / enum

## 特性

不可变默认 / 类型推断 / 模式匹配 / 解构

## 示例代码

```rust
fn main() {
    // 不可变变量（默认）
    let x = 5;
    // x = 6;  // 错误！默认不可变

    // 可变变量
    let mut y = 5;
    y = 6;  // OK

    // 类型标注
    let num: i32 = 42;
    let float_num: f64 = 3.14;
    let flag: bool = true;
    let letter: char = 'A';

    // 整数类型
    let a: i8 = 127;
    let b: u32 = 4294967295;
    let c: isize = 100;  // 指针大小的有符号整数
    let d: usize = 200;  // 指针大小的无符号整数

    // 浮点数
    let f1: f32 = 3.14;
    let f2: f64 = 3.1415926535;

    // 常量（编译期求值，必须标注类型）
    const MAX_POINTS: u32 = 100_000;
    const THREE_HOURS_IN_SECONDS: u32 = 60 * 60 * 3;

    // 元组 tuple
    let tup: (i32, f64, char) = (500, 6.4, 'A');
    let (x, y, z) = tup;  // 解构
    println!("{}", tup.0);  // 500（用.访问）

    // 数组（固定大小，同类型）
    let arr: [i32; 5] = [1, 2, 3, 4, 5];
    let first = arr[0];
    let len = arr.len();

    // 所有元素相同
    let zeros = [0; 10];  // [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    // 字符串
    let s1 = "hello";          // &str 字符串切片
    let s2 = String::from("hello");  // String 拥有所有权
    let s3 = s2.clone();       // 深拷贝

    // 结构体
    struct User {
        username: String,
        email: String,
        active: bool,
    }
    let user = User {
        email: String::from("alice@example.com"),
        username: String::from("alice"),
        active: true,
    };

    // 枚举
    enum Message {
        Quit,
        Move { x: i32, y: i32 },
        Write(String),
        ChangeColor(i32, i32, i32),
    }
    let msg = Message::Write(String::from("hello"));

    // Option（可能为空）
    let some_number: Option<i32> = Some(5);
    let absent_number: Option<i32> = None;

    // Result（可能出错）
    let ok_result: Result<i32, String> = Ok(42);
    let err_result: Result<i32, String> = Err("出错了".to_string());

    // 类型转换
    let num: i32 = 42;
    let float_num: f64 = num as f64;
}
```
