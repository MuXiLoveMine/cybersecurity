// ============================================================
// 05_hashmap.rs - Rust HashMap 哈希表示例
// 编译运行：rustc 05_hashmap.rs && ./05_hashmap
// ============================================================

use std::collections::HashMap;
use std::collections::HashSet;

fn main() {
    // --------------------------------------------------------
    // 1. 创建 HashMap
    // --------------------------------------------------------
    println!("=== 创建 HashMap ===");

    // 空 HashMap
    let mut scores: HashMap<String, i32> = HashMap::new();
    println!("空 HashMap: {:?}", scores);
    println!("长度: {}", scores.len());

    // 插入数据
    scores.insert(String::from("Red"), 10);
    scores.insert(String::from("Blue"), 50);
    scores.insert(String::from("Green"), 30);
    println!("插入后: {:?}", scores);

    // 从元组向量创建
    let teams = vec![
        (String::from("Red"), 10),
        (String::from("Blue"), 50),
        (String::from("Green"), 30),
    ];
    let map: HashMap<_, _> = teams.into_iter().collect();
    println!("从元组向量创建: {:?}", map);
    println!();

    // --------------------------------------------------------
    // 2. 访问元素
    // --------------------------------------------------------
    println!("=== 访问元素 ===");

    let scores = create_sample_map();

    // get 方法（返回 Option<&V>）
    match scores.get("Blue") {
        Some(score) => println!("Blue 的分数: {}", score),
        None => println!("未找到 Blue"),
    }

    match scores.get("Yellow") {
        Some(score) => println!("Yellow 的分数: {}", score),
        None => println!("未找到 Yellow"),
    }

    // 包含检查
    println!("包含 Red: {}", scores.contains_key("Red"));
    println!("包含 Yellow: {}", scores.contains_key("Yellow"));

    // len / is_empty
    println!("长度: {}", scores.len());
    println!("是否为空: {}", scores.is_empty());
    println!();

    // --------------------------------------------------------
    // 3. 增删改
    // --------------------------------------------------------
    println!("=== 增删改 ===");

    let mut scores = create_sample_map();
    println!("原始: {:?}", scores);

    // insert - 插入或更新
    scores.insert(String::from("Yellow"), 40);    // 新增
    println!("插入 Yellow: {:?}", scores);

    scores.insert(String::from("Red"), 25);        // 更新已存在的键
    println!("更新 Red: {:?}", scores);

    // entry + or_insert - 只在键不存在时插入
    scores.entry(String::from("Blue")).or_insert(100);   // 已存在，不修改
    scores.entry(String::from("Purple")).or_insert(60);  // 不存在，插入
    println!("entry/or_insert 后: {:?}", scores);

    // 修改已有值（基于旧值）
    let count = scores.entry(String::from("Red")).or_insert(0);
    *count += 10;
    println!("Red 加 10 后: {:?}", scores);

    // remove - 删除
    scores.remove("Green");
    println!("删除 Green: {:?}", scores);

    // 也可以使用 entry 的 remove_entry
    // let removed = scores.remove_entry("Blue");

    // clear - 清空
    let mut map2 = create_sample_map();
    map2.clear();
    println!("clear 后: {:?}, 空吗? {}", map2, map2.is_empty());
    println!();

    // --------------------------------------------------------
    // 4. 遍历 HashMap
    // --------------------------------------------------------
    println!("=== 遍历 HashMap ===");

    let scores = create_sample_map();

    // 遍历键值对
    println!("键值对遍历:");
    for (key, value) in &scores {
        println!("  {}: {}", key, value);
    }

    // 只遍历键
    println!("键遍历:");
    for key in scores.keys() {
        println!("  {}", key);
    }

    // 只遍历值
    println!("值遍历:");
    for value in scores.values() {
        println!("  {}", value);
    }

    // 可变遍历值
    let mut scores = create_sample_map();
    for value in scores.values_mut() {
        *value += 5;
    }
    println!("所有值加 5 后: {:?}", scores);
    println!();

    // --------------------------------------------------------
    // 5. 词频统计示例
    // --------------------------------------------------------
    println!("=== 词频统计 ===");

    let text = "hello world hello rust world hello programming";
    let freq = word_count(text);

    println!("文本: \"{}\"", text);
    println!("词频统计:");
    for (word, count) in &freq {
        println!("  {}: {}", word, count);
    }

    // 找出出现次数最多的词
    let most_frequent = freq.iter().max_by_key(|&(_, count)| count);
    if let Some((word, count)) = most_frequent {
        println!("出现最多的词: {} ({} 次)", word, count);
    }
    println!();

    // --------------------------------------------------------
    // 6. HashMap 的所有权
    // --------------------------------------------------------
    println!("=== HashMap 与所有权 ===");

    let key = String::from("name");
    let value = String::from("Alice");

    let mut map = HashMap::new();
    map.insert(key, value);    // key 和 value 的所有权被移动给 map

    // println!("{}", key);    // 错误：key 已被移动
    // println!("{}", value);  // 错误：value 已被移动

    println!("map: {:?}", map);

    // 如果使用引用类型（&str），则不会移动
    let mut map2: HashMap<&str, i32> = HashMap::new();
    let name = "Alice";
    map2.insert(name, 100);
    println!("使用引用类型，name 仍然有效: {}", name);
    println!();

    // --------------------------------------------------------
    // 7. HashSet
    // --------------------------------------------------------
    println!("=== HashSet ===");

    // 创建 HashSet
    let mut set: HashSet<i32> = HashSet::new();
    set.insert(1);
    set.insert(2);
    set.insert(3);
    set.insert(2);    // 重复插入，不会改变
    println!("HashSet: {:?}", set);
    println!("长度: {}", set.len());

    // 包含检查
    println!("包含 2: {}", set.contains(&2));
    println!("包含 5: {}", set.contains(&5));

    // 删除
    set.remove(&2);
    println!("删除 2 后: {:?}", set);

    // 遍历
    println!("遍历:");
    for x in &set {
        println!("  {}", x);
    }

    // 从 Vec 创建
    let vec = vec![1, 2, 3, 2, 4, 1, 5];
    let unique: HashSet<_> = vec.into_iter().collect();
    println!("从 Vec 去重: {:?}", unique);

    // 集合运算
    let a: HashSet<_> = [1, 2, 3, 4].iter().cloned().collect();
    let b: HashSet<_> = [3, 4, 5, 6].iter().cloned().collect();

    let intersection: Vec<_> = a.intersection(&b).collect();
    println!("交集: {:?}", intersection);

    let union: Vec<_> = a.union(&b).collect();
    println!("并集: {:?}", union);

    let diff: Vec<_> = a.difference(&b).collect();
    println!("差集 (a - b): {:?}", diff);

    let sym_diff: Vec<_> = a.symmetric_difference(&b).collect();
    println!("对称差集: {:?}", sym_diff);

    // 子集/超集判断
    let small: HashSet<_> = [1, 2].iter().cloned().collect();
    println!("small 是 a 的子集: {}", small.is_subset(&a));
    println!("a 是 small 的超集: {}", a.is_superset(&small));

    println!();
    println!("=== 05_hashmap.rs 执行完毕 ===");
}

// --------------------------------------------------------
// 辅助函数：创建示例 HashMap
// --------------------------------------------------------
fn create_sample_map() -> HashMap<String, i32> {
    let mut map = HashMap::new();
    map.insert(String::from("Red"), 10);
    map.insert(String::from("Blue"), 50);
    map.insert(String::from("Green"), 30);
    map
}

// --------------------------------------------------------
// 词频统计函数
// --------------------------------------------------------
fn word_count(text: &str) -> HashMap<String, u32> {
    let mut map = HashMap::new();

    for word in text.split_whitespace() {
        // entry 返回该键的条目，or_insert(0) 在键不存在时插入默认值
        let count = map.entry(word.to_string()).or_insert(0);
        *count += 1;
    }

    map
}
