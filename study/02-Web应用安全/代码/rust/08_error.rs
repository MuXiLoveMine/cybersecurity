// ============================================================
// 08_error.rs - Rust 错误处理示例
// 编译运行：rustc 08_error.rs && ./08_error
// ============================================================

use std::fs;
use std::io;
use std::io::Read;

fn main() {
    // --------------------------------------------------------
    // 1. panic! 宏
    // --------------------------------------------------------
    println!("=== panic! 宏 ===");

    // 直接调用 panic!
    // panic!("程序崩溃了！");  // 取消注释会立即崩溃

    // 数组越界会自动触发 panic
    let v = vec![1, 2, 3];
    // v[10];  // 取消注释会触发 panic（越界访问）

    // Option 的 unwrap 在 None 时会 panic
    let opt: Option<i32> = None;
    // opt.unwrap();  // 取消注释会 panic

    println!("（为了程序继续运行，上面的 panic 示例已注释）");
    println!();

    // --------------------------------------------------------
    // 2. Result 枚举
    // --------------------------------------------------------
    println!("=== Result 枚举 ===");

    // Result<T, E> 有两个变体：Ok(T) 和 Err(E)
    // 常用于可能失败的操作，如文件操作、网络请求、解析等

    // 手动构造 Result
    let ok_result: Result<i32, String> = Ok(42);
    let err_result: Result<i32, String> = Err(String::from("出错了"));

    println!("Ok 结果: {:?}", ok_result);
    println!("Err 结果: {:?}", err_result);

    // is_ok / is_err
    println!("ok_result.is_ok() = {}", ok_result.is_ok());
    println!("err_result.is_err() = {}", err_result.is_err());
    println!();

    // --------------------------------------------------------
    // 3. 使用 match 处理 Result
    // --------------------------------------------------------
    println!("=== match 处理 Result ===");

    // 除法函数
    fn divide(a: f64, b: f64) -> Result<f64, String> {
        if b == 0.0 {
            Err(String::from("除数不能为零"))
        } else {
            Ok(a / b)
        }
    }

    // 成功的情况
    match divide(10.0, 2.0) {
        Ok(result) => println!("10 / 2 = {}", result),
        Err(e) => println!("错误: {}", e),
    }

    // 失败的情况
    match divide(10.0, 0.0) {
        Ok(result) => println!("10 / 0 = {}", result),
        Err(e) => println!("错误: {}", e),
    }

    // 解析数字
    let num_str = "123";
    match num_str.parse::<i32>() {
        Ok(n) => println!("解析成功: {}", n),
        Err(e) => println!("解析失败: {}", e),
    }

    let invalid_str = "abc";
    match invalid_str.parse::<i32>() {
        Ok(n) => println!("解析成功: {}", n),
        Err(e) => println!("解析 'abc' 失败: {}", e),
    }
    println!();

    // --------------------------------------------------------
    // 4. unwrap 和 expect
    // --------------------------------------------------------
    println!("=== unwrap 和 expect ===");

    // unwrap - 如果 Ok 则返回值，如果 Err 则 panic
    let result = divide(10.0, 2.0).unwrap();
    println!("unwrap 成功: {}", result);

    // divide(10.0, 0.0).unwrap();  // 会 panic！

    // expect - 与 unwrap 类似，但可以自定义错误消息
    let result = divide(20.0, 4.0).expect("除法应该成功");
    println!("expect 成功: {}", result);

    // divide(10.0, 0.0).expect("除法失败了！");  // 会 panic，带自定义消息

    // unwrap_or - Err 时返回默认值
    let result = divide(10.0, 0.0).unwrap_or(0.0);
    println!("unwrap_or(0.0): {}", result);

    // unwrap_or_else - Err 时执行闭包计算默认值
    let result = divide(10.0, 0.0).unwrap_or_else(|err| {
        println!("捕获错误: {}", err);
        -1.0
    });
    println!("unwrap_or_else: {}", result);

    // unwrap_or_default - Err 时返回类型默认值
    let result: f64 = divide(10.0, 0.0).unwrap_or_default();
    println!("unwrap_or_default: {}", result);
    println!();

    // --------------------------------------------------------
    // 5. ? 运算符（传播错误）
    // --------------------------------------------------------
    println!("=== ? 运算符 ===");

    // ? 运算符用于传播错误：
    // - 如果是 Ok，取出值继续执行
    // - 如果是 Err，将错误作为函数返回值返回
    // 只能在返回 Result 的函数中使用

    // 读取文件内容（使用 ? 传播错误）
    fn read_file_contents(path: &str) -> Result<String, io::Error> {
        let mut f = fs::File::open(path)?;  // 如果失败，直接返回 Err
        let mut s = String::new();
        f.read_to_string(&mut s)?;          // 如果失败，直接返回 Err
        Ok(s)
    }

    // 上面的函数可以用更简洁的方式写：
    fn read_file_contents_v2(path: &str) -> Result<String, io::Error> {
        fs::read_to_string(path)
    }

    // 调用可能返回错误的函数
    match read_file_contents("nonexistent.txt") {
        Ok(content) => println!("文件内容: {}", content),
        Err(e) => println!("读取文件失败: {}", e),
    }

    // 链式调用 ?
    fn parse_file_number(path: &str) -> Result<i32, String> {
        let content = fs::read_to_string(path).map_err(|e| e.to_string())?;
        let num: i32 = content.trim().parse().map_err(|e| e.to_string())?;
        Ok(num)
    }

    match parse_file_number("nonexistent.txt") {
        Ok(n) => println!("文件中的数字: {}", n),
        Err(e) => println!("解析文件失败: {}", e),
    }

    println!();

    // --------------------------------------------------------
    // 6. Option 与错误处理
    // --------------------------------------------------------
    println!("=== Option 错误处理 ===");

    // Option<T> 表示可能存在也可能不存在的值
    // 常用于"找不到"这类场景

    // 查找第一个偶数
    fn find_first_even(numbers: &[i32]) -> Option<i32> {
        for &n in numbers {
            if n % 2 == 0 {
                return Some(n);
            }
        }
        None
    }

    let nums = vec![1, 3, 5, 7, 8, 9];
    match find_first_even(&nums) {
        Some(n) => println!("第一个偶数: {}", n),
        None => println!("没有偶数"),
    }

    let all_odd = vec![1, 3, 5, 7];
    match find_first_even(&all_odd) {
        Some(n) => println!("第一个偶数: {}", n),
        None => println!("没有偶数"),
    }

    // Option 的常用方法
    let opt = Some(5);

    println!("opt.is_some() = {}", opt.is_some());
    println!("opt.is_none() = {}", opt.is_none());
    println!("opt.unwrap() = {}", opt.unwrap());
    println!("opt.unwrap_or(0) = {}", opt.unwrap_or(0));
    println!("None.unwrap_or(0) = {}", None.unwrap_or(0));

    // map - 对 Some 中的值进行转换
    let doubled = opt.map(|x| x * 2);
    println!("opt.map(|x| x*2) = {:?}", doubled);

    // and_then - 链式操作
    let result = opt.and_then(|x| if x > 3 { Some(x * 10) } else { None });
    println!("opt.and_then(...) = {:?}", result);

    // filter - 条件过滤
    let filtered = opt.filter(|&x| x > 10);
    println!("opt.filter(|x| x>10) = {:?}", filtered);

    // ok_or - Option 转 Result
    let result: Result<i32, String> = opt.ok_or(String::from("没有值"));
    println!("opt.ok_or(...) = {:?}", result);

    let none_result: Result<i32, String> = None.ok_or(String::from("没有值"));
    println!("None.ok_or(...) = {:?}", none_result);
    println!();

    // --------------------------------------------------------
    // 7. Result 与 Option 的组合
    // --------------------------------------------------------
    println!("=== Result 与 Option 组合 ===");

    // 从向量中找指定索引的元素，并解析为数字
    fn get_and_parse(v: &[&str], index: usize) -> Result<i32, String> {
        v.get(index)
            .ok_or_else(|| format!("索引 {} 越界", index))
            .and_then(|s| s.parse::<i32>().map_err(|e| e.to_string()))
    }

    let items = vec!["10", "20", "30"];

    match get_and_parse(&items, 1) {
        Ok(n) => println!("索引 1 解析成功: {}", n),
        Err(e) => println!("索引 1 失败: {}", e),
    }

    match get_and_parse(&items, 5) {
        Ok(n) => println!("索引 5 解析成功: {}", n),
        Err(e) => println!("索引 5 失败: {}", e),
    }

    match get_and_parse(&items, 0) {
        Ok(n) => println!("索引 0 解析成功: {}", n),
        Err(e) => println!("索引 0 失败: {}", e),
    }
    println!();

    // --------------------------------------------------------
    // 8. 自定义错误类型
    // --------------------------------------------------------
    println!("=== 自定义错误类型 ===");

    // 定义错误枚举
    #[derive(Debug)]
    enum AppError {
        InvalidInput(String),
        NotFound(String),
        IoError(io::Error),
        ParseError(String),
    }

    // 实现 Display trait
    use std::fmt;
    impl fmt::Display for AppError {
        fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
            match self {
                AppError::InvalidInput(msg) => write!(f, "无效输入: {}", msg),
                AppError::NotFound(msg) => write!(f, "未找到: {}", msg),
                AppError::IoError(e) => write!(f, "IO 错误: {}", e),
                AppError::ParseError(msg) => write!(f, "解析错误: {}", msg),
            }
        }
    }

    // 使用自定义错误
    fn process_user_input(input: &str) -> Result<i32, AppError> {
        if input.is_empty() {
            return Err(AppError::InvalidInput(String::from("输入不能为空")));
        }
        if input.len() > 10 {
            return Err(AppError::InvalidInput(String::from("输入过长")));
        }
        input
            .parse::<i32>()
            .map_err(|e| AppError::ParseError(e.to_string()))
    }

    match process_user_input("42") {
        Ok(n) => println!("处理成功: {}", n),
        Err(e) => println!("处理失败: {}", e),
    }

    match process_user_input("") {
        Ok(n) => println!("处理成功: {}", n),
        Err(e) => println!("处理失败: {}", e),
    }

    match process_user_input("not_a_number") {
        Ok(n) => println!("处理成功: {}", n),
        Err(e) => println!("处理失败: {}", e),
    }
    println!();

    // --------------------------------------------------------
    // 9. 综合示例：安全除法计算器
    // --------------------------------------------------------
    println!("=== 综合示例：安全除法计算器 ===");

    fn safe_divide(a: &str, b: &str) -> Result<f64, String> {
        // 解析第一个数
        let num_a: f64 = a.parse().map_err(|_| format!("'{}' 不是有效数字", a))?;

        // 解析第二个数
        let num_b: f64 = b.parse().map_err(|_| format!("'{}' 不是有效数字", b))?;

        // 检查除数是否为零
        if num_b == 0.0 {
            return Err(String::from("除数不能为零"));
        }

        Ok(num_a / num_b)
    }

    fn test_divide(a: &str, b: &str) {
        match safe_divide(a, b) {
            Ok(result) => println!("{} / {} = {}", a, b, result),
            Err(e) => println!("{} / {} 错误: {}", a, b, e),
        }
    }

    test_divide("10", "2");
    test_divide("10", "0");
    test_divide("abc", "2");
    test_divide("10", "xyz");
    test_divide("", "5");

    println!();
    println!("=== 08_error.rs 执行完毕 ===");
}
