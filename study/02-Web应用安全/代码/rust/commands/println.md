# println

> **分类**：输出
> **说明**：Rust 格式化输出宏

---

## 语法

```rust
println!("format {}", arg);
```

## 常用宏

print! / println! / eprint! / eprintln! / format! / dbg!

## 格式化占位符

{} Display / {:?} Debug / {:#?} 美化Debug / {:.2} 精度 / {:0>5} 填充对齐

## 示例代码

```rust
fn main() {
    // 基本输出
    println!("Hello, World!");
    println!("数字: {}", 42);
    println!("多个: {} 和 {}", "a", "b");

    // 位置参数
    println!("{0} + {1} = {2}", 1, 2, 3);

    // 命名参数
    println!("{name} 今年 {age} 岁", name = "Alice", age = 25);

    // Debug 输出
    println!("调试: {:?}", vec![1, 2, 3]);
    println!("美化调试: {:#?}", vec![1, 2, 3]);

    // 精度
    println!("PI = {:.4}", 3.14159265);  // PI = 3.1416

    // 填充和对齐
    println!("{:>10}", "右对齐");    // 宽度10，右对齐
    println!("{:<10}", "左对齐");    // 宽度10，左对齐
    println!("{:^10}", "居中");      // 宽度10，居中
    println!("{:0>5}", 42);          // 00042

    // 进制
    println!("二进制: {:b}", 255);   // 11111111
    println!("八进制: {:o}", 255);   // 377
    println!("十六进制: {:x}", 255); // ff
    println!("十六进制: {:X}", 255); // FF

    // 指针
    let x = 42;
    println!("指针地址: {:p}", &x);

    // format! 生成字符串
    let s = format!("Hello, {}!", "Rust");
    println!("{}", s);

    // dbg! 宏（调试用，输出到 stderr）
    let y = dbg!(10 * 20);  // 输出 [src/main.rs:xx] 10 * 20 = 200

    // 错误输出
    eprintln!("这是错误信息");

    // 结构体 Debug 输出
    #[derive(Debug)]
    struct Person { name: String, age: u32 }
    let p = Person { name: "Bob".into(), age: 30 };
    println!("{:?}", p);
    println!("{:#?}", p);
}
```
