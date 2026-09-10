// ============================================================
// 04_vec.rs - Rust Vec<T> 向量示例
// 编译运行：rustc 04_vec.rs && ./04_vec
// ============================================================

fn main() {
    // --------------------------------------------------------
    // 1. 创建向量
    // --------------------------------------------------------
    println!("=== 创建向量 ===");

    // 空向量（需要标注类型）
    let v: Vec<i32> = Vec::new();
    println!("空向量: {:?}, 长度: {}", v, v.len());

    // 使用 vec! 宏创建
    let v = vec![1, 2, 3, 4, 5];
    println!("vec! 宏创建: {:?}", v);

    // 创建指定大小的初始值向量
    let v = vec![0; 5];    // 5 个 0
    println!("初始化为 0: {:?}", v);

    // 使用迭代器收集
    let v: Vec<i32> = (1..10).collect();
    println!("Range 收集: {:?}", v);
    println!();

    // --------------------------------------------------------
    // 2. 添加元素
    // --------------------------------------------------------
    println!("=== 添加元素 ===");

    let mut v = Vec::new();

    // push - 末尾添加
    v.push(1);
    v.push(2);
    v.push(3);
    println!("push 后: {:?}", v);

    // insert - 指定位置插入
    v.insert(0, 0);       // 在索引 0 处插入 0
    println!("insert(0, 0) 后: {:?}", v);

    v.insert(2, 100);     // 在索引 2 处插入 100
    println!("insert(2, 100) 后: {:?}", v);

    // append - 合并另一个向量
    let mut v2 = vec![10, 20, 30];
    let mut v3 = vec![40, 50];
    v2.append(&mut v3);
    println!("append 后: {:?}", v2);
    println!("v3 被清空: {:?}", v3);
    println!();

    // --------------------------------------------------------
    // 3. 访问元素
    // --------------------------------------------------------
    println!("=== 访问元素 ===");

    let v = vec![10, 20, 30, 40, 50];

    // 索引访问（越界会 panic）
    println!("v[0] = {}", v[0]);
    println!("v[2] = {}", v[2]);
    println!("v[4] = {}", v[4]);

    // get 方法（返回 Option，安全访问）
    match v.get(2) {
        Some(val) => println!("get(2) = {}", val),
        None => println!("索引越界"),
    }

    match v.get(10) {
        Some(val) => println!("get(10) = {}", val),
        None => println!("get(10): 索引越界"),
    }

    // first / last
    println!("first = {:?}", v.first());
    println!("last = {:?}", v.last());
    println!();

    // --------------------------------------------------------
    // 4. 修改和删除元素
    // --------------------------------------------------------
    println!("=== 修改和删除元素 ===");

    let mut v = vec![1, 2, 3, 4, 5];
    println!("原始: {:?}", v);

    // 修改元素
    v[0] = 10;
    println!("修改 v[0] = 10: {:?}", v);

    // pop - 弹出末尾元素
    let last = v.pop();
    println!("pop 后: {:?}, 弹出: {:?}", v, last);

    // remove - 删除指定位置元素
    let removed = v.remove(1);
    println!("remove(1) 后: {:?}, 删除: {}", v, removed);

    // swap_remove - 用最后一个元素替换并删除（高效，但不保持顺序）
    let mut v2 = vec![1, 2, 3, 4, 5];
    let val = v2.swap_remove(1);
    println!("swap_remove(1): {:?}, 删除: {}", v2, val);

    // clear - 清空
    let mut v3 = vec![1, 2, 3];
    v3.clear();
    println!("clear 后: {:?}, 空吗? {}", v3, v3.is_empty());

    // truncate - 截断到指定长度
    let mut v4 = vec![1, 2, 3, 4, 5];
    v4.truncate(3);
    println!("truncate(3) 后: {:?}", v4);
    println!();

    // --------------------------------------------------------
    // 5. 遍历向量
    // --------------------------------------------------------
    println!("=== 遍历向量 ===");

    let v = vec![10, 20, 30, 40, 50];

    // 不可变遍历
    println!("不可变遍历:");
    for item in &v {
        print!("{} ", item);
    }
    println!();

    // 可变遍历（修改元素）
    let mut v2 = vec![1, 2, 3, 4, 5];
    for item in &mut v2 {
        *item *= 2;    // 解引用后修改
    }
    println!("每个元素 * 2 后: {:?}", v2);

    // 带索引遍历
    println!("带索引遍历:");
    for (index, item) in v.iter().enumerate() {
        println!("[{}] = {}", index, item);
    }
    println!();

    // --------------------------------------------------------
    // 6. 常用方法
    // --------------------------------------------------------
    println!("=== 常用方法 ===");

    let v = vec![10, 20, 30, 40, 50];

    println!("长度: {}", v.len());
    println!("是否为空: {}", v.is_empty());
    println!("容量: {}", v.capacity());

    // 包含检查
    println!("包含 30: {}", v.contains(&30));
    println!("包含 100: {}", v.contains(&100));

    // 查找位置
    println!("位置 30: {:?}", v.iter().position(|&x| x == 30));
    println!("位置 100: {:?}", v.iter().position(|&x| x == 100));

    // 反转
    let mut v2 = vec![1, 2, 3, 4, 5];
    v2.reverse();
    println!("反转: {:?}", v2);

    // 排序
    let mut v3 = vec![3, 1, 4, 1, 5, 9, 2, 6];
    v3.sort();
    println!("排序: {:?}", v3);

    // 去重（需要先排序）
    let mut v4 = vec![1, 2, 2, 3, 3, 3, 4];
    v4.dedup();
    println!("去重: {:?}", v4);

    // 切片
    let slice = &v[1..4];
    println!("切片 [1..4]: {:?}", slice);
    println!();

    // --------------------------------------------------------
    // 7. 迭代器
    // --------------------------------------------------------
    println!("=== 迭代器 ===");

    let v = vec![1, 2, 3, 4, 5];

    // map - 映射转换
    let doubled: Vec<i32> = v.iter().map(|x| x * 2).collect();
    println!("翻倍: {:?}", doubled);

    // filter - 过滤
    let evens: Vec<i32> = v.iter().filter(|&&x| x % 2 == 0).copied().collect();
    println!("偶数: {:?}", evens);

    // fold - 累积
    let sum: i32 = v.iter().fold(0, |acc, x| acc + x);
    println!("求和 (fold): {}", sum);

    // any / all
    println!("有大于 4 的: {}", v.iter().any(|&x| x > 4));
    println!("全部大于 0: {}", v.iter().all(|&x| x > 0));

    // take / skip
    let first_three: Vec<i32> = v.iter().take(3).copied().collect();
    println!("前 3 个: {:?}", first_three);

    let after_two: Vec<i32> = v.iter().skip(2).copied().collect();
    println!("跳过前 2 个: {:?}", after_two);

    // zip - 两个迭代器配对
    let v2 = vec![10, 20, 30];
    let zipped: Vec<_> = v.iter().zip(v2.iter()).collect();
    println!("zip: {:?}", zipped);

    // chain - 连接两个迭代器
    let v3 = vec![1, 2, 3];
    let v4 = vec![4, 5, 6];
    let chained: Vec<_> = v3.iter().chain(v4.iter()).copied().collect();
    println!("chain: {:?}", chained);

    println!();

    // --------------------------------------------------------
    // 8. 向量的所有权示例
    // --------------------------------------------------------
    println!("=== 向量与所有权 ===");

    let v = vec![String::from("a"), String::from("b"), String::from("c")];

    // 迭代引用，不获取所有权
    for item in &v {
        println!("引用: {}", item);
    }
    println!("迭代后 v 仍然有效: {:?}", v);

    // 获取所有权（v 会被消耗）
    let v2 = vec![String::from("x"), String::from("y"), String::from("z")];
    for item in v2 {
        println!("所有权: {}", item);
    }
    // println!("{:?}", v2);  // 错误：v2 已被移动

    println!();
    println!("=== 04_vec.rs 执行完毕 ===");
}
