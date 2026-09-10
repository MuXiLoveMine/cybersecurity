// ============================================================
// 02_control_flow.rs - Rust 控制流示例
// 编译运行：rustc 02_control_flow.rs && ./02_control_flow
// ============================================================

fn main() {
    // --------------------------------------------------------
    // 1. if / else if / else
    // --------------------------------------------------------
    println!("=== if / else if / else ===");

    let number = 6;

    if number % 4 == 0 {
        println!("{} 能被 4 整除", number);
    } else if number % 3 == 0 {
        println!("{} 能被 3 整除", number);
    } else if number % 2 == 0 {
        println!("{} 能被 2 整除", number);
    } else {
        println!("{} 不能被 4、3、2 整除", number);
    }

    // if 是表达式，可以返回值
    let condition = true;
    let result = if condition { 5 } else { 6 };
    println!("if 表达式结果: {}", result);

    // 多个条件的 if 表达式
    let score = 85;
    let grade = if score >= 90 {
        'A'
    } else if score >= 80 {
        'B'
    } else if score >= 70 {
        'C'
    } else if score >= 60 {
        'D'
    } else {
        'F'
    };
    println!("分数 {} 对应等级 {}", score, grade);
    println!();

    // --------------------------------------------------------
    // 2. loop 无限循环
    // --------------------------------------------------------
    println!("=== loop 循环 ===");

    let mut count = 0;
    loop {
        count += 1;
        if count > 5 {
            break;      // break 跳出循环
        }
        println!("loop 计数: {}", count);
    }

    // loop 可以返回值
    let mut counter = 0;
    let result = loop {
        counter += 1;
        if counter == 10 {
            break counter * 2;    // break 后面的值就是返回值
        }
    };
    println!("loop 返回值: {}", result);

    // continue 跳过本次迭代
    println!("1 到 10 的奇数：");
    let mut n = 0;
    loop {
        n += 1;
        if n > 10 {
            break;
        }
        if n % 2 == 0 {
            continue;   // 偶数跳过
        }
        print!("{} ", n);
    }
    println!();

    // 循环标签 - 用于嵌套循环中跳出外层循环
    println!("循环标签示例：");
    let mut outer_count = 0;
    'outer: loop {
        outer_count += 1;
        if outer_count > 3 {
            break;
        }
        println!("外层循环: {}", outer_count);

        let mut inner_count = 0;
        loop {
            inner_count += 1;
            if inner_count > 5 {
                break;
            }
            if inner_count == 3 && outer_count == 2 {
                println!("  内层: {} (跳出外层)", inner_count);
                break 'outer;    // 直接跳出外层循环
            }
            println!("  内层: {}", inner_count);
        }
    }
    println!();

    // --------------------------------------------------------
    // 3. while 循环
    // --------------------------------------------------------
    println!("=== while 循环 ===");

    let mut number = 3;
    while number != 0 {
        println!("{}!", number);
        number -= 1;
    }
    println!("发射！");

    // while 循环遍历数组（不推荐，有边界检查开销）
    let arr = [10, 20, 30, 40, 50];
    let mut index = 0;
    while index < arr.len() {
        println!("数组元素 [{}] = {}", index, arr[index]);
        index += 1;
    }
    println!();

    // --------------------------------------------------------
    // 4. for 循环
    // --------------------------------------------------------
    println!("=== for 循环 ===");

    // 遍历数组
    let arr = [10, 20, 30, 40, 50];
    println!("遍历数组：");
    for element in arr.iter() {
        println!("  值为：{}", element);
    }

    // 使用 Range 范围
    println!("Range 1..5：");
    for i in 1..5 {       // 左闭右开：1, 2, 3, 4
        print!("{} ", i);
    }
    println!();

    println!("Range 1..=5：");
    for i in 1..=5 {      // 包含右端点：1, 2, 3, 4, 5
        print!("{} ", i);
    }
    println!();

    // 反向遍历
    println!("反向 Range (1..5).rev()：");
    for i in (1..5).rev() {
        print!("{} ", i);
    }
    println!();

    // 遍历带索引
    println!("enumerate 带索引：");
    for (index, value) in arr.iter().enumerate() {
        println!("  [{}] = {}", index, value);
    }

    // 遍历字符串
    println!("遍历字符串：");
    for c in "Rust编程".chars() {
        print!("{} ", c);
    }
    println!();
    println!();

    // --------------------------------------------------------
    // 5. match 模式匹配
    // --------------------------------------------------------
    println!("=== match 模式匹配 ===");

    // 匹配单个值
    let number = 3;
    match number {
        1 => println!("一"),
        2 => println!("二"),
        3 => println!("三"),
        4..=6 => println!("四到六"),
        _ => println!("其他数字"),    // _ 通配符，匹配所有情况
    }

    // match 是表达式，返回值
    let number = 7;
    let result = match number {
        1 => "one",
        2 => "two",
        3 => "three",
        4..=6 => "four_to_six",
        _ => "other",
    };
    println!("match 结果: {}", result);

    // 匹配多个模式
    let number = 2;
    match number {
        1 | 2 | 3 => println!("一到三"),
        4 | 5 | 6 => println!("四到六"),
        _ => println!("其他"),
    }

    // 匹配守卫（match guard）
    let pair = (2, -2);
    match pair {
        (x, y) if x == y => println!("两个数相等: {}", x),
        (x, y) if x + y == 0 => println!("两个数相加为零: {} + {} = 0", x, y),
        (x, _) if x % 2 == 0 => println!("第一个数是偶数: {}", x),
        _ => println!("其他情况"),
    }

    // 匹配结构体
    struct Point {
        x: i32,
        y: i32,
    }
    let p = Point { x: 0, y: 7 };
    match p {
        Point { x: 0, y } => println!("在 y 轴上，y = {}", y),
        Point { x, y: 0 } => println!("在 x 轴上，x = {}", x),
        Point { x, y } => println!("在位置 ({}, {})", x, y),
    }

    // 匹配 Option
    let some_value: Option<i32> = Some(5);
    match some_value {
        Some(n) if n > 3 => println!("Some 值大于 3: {}", n),
        Some(n) => println!("Some 值: {}", n),
        None => println!("None 值"),
    }

    // 匹配引用
    let v = vec![1, 2, 3];
    match v.get(1) {
        Some(val) => println!("向量索引 1 的值: {}", val),
        None => println!("索引越界"),
    }
    println!();

    // --------------------------------------------------------
    // 6. if let 简洁控制流
    // --------------------------------------------------------
    println!("=== if let ===");

    let some_value = Some(3);

    // match 写法
    match some_value {
        Some(3) => println!("match: 等于三"),
        _ => (),
    }

    // if let 写法（等价，更简洁）
    if let Some(3) = some_value {
        println!("if let: 等于三");
    }

    // if let + else
    let another_value: Option<i32> = None;
    if let Some(n) = another_value {
        println!("值为：{}", n);
    } else {
        println!("没有值");
    }

    // if let 匹配枚举
    #[derive(Debug)]
    enum Color {
        Red,
        Green,
        Blue(u8, u8, u8),
    }

    let color = Color::Blue(0, 0, 255);
    if let Color::Blue(r, g, b) = color {
        println!("蓝色 RGB({}, {}, {})", r, g, b);
    } else {
        println!("不是蓝色");
    }

    // while let 循环
    println!("while let 循环：");
    let mut stack = Vec::new();
    stack.push(1);
    stack.push(2);
    stack.push(3);

    while let Some(top) = stack.pop() {
        println!("弹出: {}", top);
    }

    println!();
    println!("=== 02_control_flow.rs 执行完毕 ===");
}
