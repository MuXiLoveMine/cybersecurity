# fn_rust

> **分类**：函数与所有权
> **说明**：Rust 函数定义和所有权系统

---

## 语法

```rust
fn function_name(param: Type) -> ReturnType { ... }
```

## 所有权规则

每个值只有一个所有者 / 所有者离开作用域值被丢弃 / 可以移动或借用

## 借用规则

同一时间只能有一个可变引用 / 或任意数量不可变引用 / 引用必须总是有效的

## 示例代码

```rust
fn main() {
    // 基本函数
    let sum = add(5, 3);
    println!("5 + 3 = {}", sum);

    // 函数表达式（最后一个表达式就是返回值）
    let x = plus_one(5);
    println!("5 + 1 = {}", x);

    // ===== 所有权 =====
    let s1 = String::from("hello");
    let s2 = s1;  // s1 的所有权移动给 s2
    // println!("{}", s1);  // 错误！s1 已失效
    println!("{}", s2);     // OK

    // clone 深拷贝
    let s3 = s2.clone();
    println!("s2: {}, s3: {}", s2, s3);

    // Copy trait 的类型（栈上复制）
    let x = 5;
    let y = x;  // 复制，不是移动
    println!("x: {}, y: {}", x, y);

    // ===== 引用与借用 =====
    let s = String::from("hello");
    let len = calculate_length(&s);  // 借用（不可变引用）
    println!("'{}' 的长度是 {}", s, len);

    // 可变引用
    let mut s = String::from("hello");
    change(&mut s);
    println!("{}", s);  // hello, world

    // 引用规则：同一时间只能有一个可变引用
    let mut s = String::from("hello");
    {
        let r1 = &mut s;
        // let r2 = &mut s;  // 错误！
    }  // r1 离开作用域

    // 不可变引用可以有多个
    let s = String::from("hello");
    let r1 = &s;
    let r2 = &s;  // OK
    println!("{}, {}", r1, r2);

    // ===== 切片 =====
    let s = String::from("hello world");
    let hello = &s[0..5];  // "hello"
    let world = &s[6..11]; // "world"
    let entire = &s[..];   // 整个字符串

    // 数组切片
    let a = [1, 2, 3, 4, 5];
    let slice = &a[1..3];  // [2, 3]

    // ===== 结构体方法 =====
    let rect = Rectangle { width: 30, height: 50 };
    println!("面积: {}", rect.area());
    println!("是正方形: {}", rect.is_square());

    // 关联函数（类似静态方法）
    let sq = Rectangle::square(10);
    println!("正方形: {:?}", sq);
}

fn add(a: i32, b: i32) -> i32 {
    a + b  // 没有分号，就是返回值
}

fn plus_one(x: i32) -> i32 {
    x + 1
}

fn calculate_length(s: &String) -> usize {
    s.len()
}  // s 离开作用域，但因为它没有所有权，所以什么都不发生

fn change(s: &mut String) {
    s.push_str(", world");
}

#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    // 方法
    fn area(&self) -> u32 {
        self.width * self.height
    }

    fn is_square(&self) -> bool {
        self.width == self.height
    }

    // 关联函数（没有 self）
    fn square(size: u32) -> Rectangle {
        Rectangle { width: size, height: size }
    }
}
```
