# std::collections - Rust 标准集合

> Rust 标准库集合类型，包括 Vec、HashMap、HashSet 等。

---

## 一、Vec<T> - 动态数组

### 1.1 创建与初始化

```rust
// 创建空 Vec
let v: Vec<i32> = Vec::new();

// 用宏创建
let v = vec![1, 2, 3, 4, 5];
let v = vec![0; 10];  // 10 个 0

// 带初始容量
let mut v: Vec<i32> = Vec::with_capacity(100);
```

### 1.2 增删改查

```rust
let mut v = vec![1, 2, 3];

// 添加
v.push(4);          // 末尾添加
v.insert(2, 99);    // 在索引 2 插入

// 删除
v.pop();            // 弹出最后一个（返回 Option<T>）
v.remove(1);        // 删除索引 1 的元素
v.clear();          // 清空
v.truncate(2);      // 截断到 2 个元素

// 访问
let first = v[0];           // 索引访问（越界 panic）
let safe = v.get(0);        // 返回 Option<&T>，安全
let first_mut = v.get_mut(0); // 可变引用

// 容量
v.capacity();               // 当前容量
v.reserve(100);             // 预留容量
v.shrink_to_fit();          // 收缩容量到实际大小
v.len();                    // 长度
v.is_empty();               // 是否为空
```

### 1.3 遍历与迭代

```rust
let v = vec![1, 2, 3, 4, 5];

// 遍历引用
for x in &v {
    println!("{}", x);
}

// 遍历可变引用
let mut v = vec![1, 2, 3];
for x in &mut v {
    *x *= 2;
}

// 消费迭代（获取所有权）
for x in v {
    println!("{}", x);
}
// v 在这里不再可用

// 迭代器方法
v.iter()
    .filter(|&x| x > 2)
    .map(|&x| x * 2)
    .collect::<Vec<i32>>();
```

---

## 二、HashMap<K, V> - 哈希映射

### 2.1 基本操作

```rust
use std::collections::HashMap;

// 创建
let mut map: HashMap<String, i32> = HashMap::new();

// 插入
map.insert("Alice".to_string(), 25);
map.insert("Bob".to_string(), 30);

// 获取
map.get("Alice");        // Option<&V>
map.get("Unknown");      // None

// 获取可变引用
map.get_mut("Alice");    // Option<&mut V>

// 检查键是否存在
map.contains_key("Alice");  // true

// 删除
map.remove("Bob");       // 返回 Option<V>
map.clear();             // 清空

// 长度
map.len();
map.is_empty();

// 容量
map.capacity();
map.reserve(100);
map.shrink_to_fit();
```

### 2.2 高级操作

```rust
use std::collections::HashMap;

let mut map = HashMap::new();

// entry API（非常有用！）
map.entry("key".to_string())
    .or_insert(0);  // 如果不存在，插入默认值

// 计数示例
let text = "hello world hello rust world hello";
let mut count: HashMap<&str, i32> = HashMap::new();

for word in text.split_whitespace() {
    let counter = count.entry(word).or_insert(0);
    *counter += 1;
}
// {"hello": 3, "world": 2, "rust": 1}

// 遍历
for (key, value) in &map {
    println!("{}: {}", key, value);
}

// 只遍历键
for key in map.keys() { ... }

// 只遍历值
for value in map.values() { ... }

// 可变值遍历
for value in map.values_mut() {
    *value *= 2;
}
```

---

## 三、HashSet<T> - 哈希集合

### 3.1 基本操作

```rust
use std::collections::HashSet;

// 创建
let mut set: HashSet<i32> = HashSet::new();

// 插入
set.insert(1);
set.insert(2);
set.insert(3);
set.insert(2);  // 重复元素不会重复插入

// 检查
set.contains(&1);  // true
set.contains(&4);  // false

// 删除
set.remove(&2);  // 返回 bool

// 长度
set.len();
set.is_empty();
set.clear();
```

### 3.2 集合运算

```rust
use std::collections::HashSet;

let a: HashSet<i32> = [1, 2, 3].iter().cloned().collect();
let b: HashSet<i32> = [2, 3, 4].iter().cloned().collect();

// 并集
let union: HashSet<_> = a.union(&b).collect();
// {1, 2, 3, 4}

// 交集
let intersection: HashSet<_> = a.intersection(&b).collect();
// {2, 3}

// 差集（在 a 中但不在 b 中）
let diff: HashSet<_> = a.difference(&b).collect();
// {1}

// 对称差（在 a 或 b 中，但不同时在两者中）
let sym_diff: HashSet<_> = a.symmetric_difference(&b).collect();
// {1, 4}

// 子集 / 超集
a.is_subset(&b);    // a 是否是 b 的子集
a.is_superset(&b);  // a 是否是 b 的超集
a.is_disjoint(&b);  // 是否不相交
```

---

## 四、其他集合

### 4.1 BTreeMap / BTreeSet

```rust
use std::collections::{BTreeMap, BTreeSet};

// BTreeMap - 有序的映射（基于 B 树）
let mut map = BTreeMap::new();
map.insert(3, "three");
map.insert(1, "one");
map.insert(2, "two");
// 按 key 排序：{1: "one", 2: "two", 3: "three"}

// 范围查询
for (key, value) in map.range(1..3) {
    println!("{}: {}", key, value);
}
// 1: one
// 2: two

// BTreeSet - 有序集合
let mut set = BTreeSet::new();
set.insert(3);
set.insert(1);
set.insert(2);
// {1, 2, 3}
```

### 4.2 VecDeque - 双端队列

```rust
use std::collections::VecDeque;

let mut deque = VecDeque::new();

// 两端操作
deque.push_back(1);    // 尾部添加
deque.push_front(0);   // 头部添加
deque.pop_back();      // 尾部弹出
deque.pop_front();     // 头部弹出

// 两端访问
deque.front();         // 第一个元素
deque.back();          // 最后一个元素

// 用作队列
let mut queue = VecDeque::new();
queue.push_back(1);
queue.push_back(2);
queue.push_back(3);
// 先进先出
let first = queue.pop_front();  // Some(1)

// 用作栈
let mut stack = VecDeque::new();
stack.push_back(1);
stack.push_back(2);
// 后进先出
let last = stack.pop_back();  // Some(2)
```

---

## 五、安全相关内容

### 5.1 Rust 的安全保证

```rust
/*
    Rust 集合类型的安全特性：
    
    1. 内存安全
       - 没有缓冲区溢出（索引越界会 panic，但不会破坏内存）
       - 没有 use-after-free（所有权系统保证）
       - 没有 double-free（所有权系统保证）
    
    2. 类型安全
       - 编译时类型检查
       - 没有隐式类型转换
    
    3. 线程安全
       - Send/Sync trait 保证线程安全
       - 没有数据竞争
    
    4. 迭代器安全
       - 迭代时不能修改集合（借用检查器保证）
*/

// ===== 越界访问 =====
let v = vec![1, 2, 3];
let x = v[10];  // ❌ panic（但安全，不会破坏内存）

// 安全的方式
match v.get(10) {
    Some(x) => println!("{}", x),
    None => println!("索引越界"),
}
// 或
if let Some(x) = v.get(10) {
    println!("{}", x);
}
```

### 5.2 避免常见安全问题

```rust
use std::collections::HashMap;

// ===== 整数溢出 =====
// Rust 中 debug 模式下整数溢出会 panic，release 模式下是 wrapping
// 显式处理溢出：
let a: u32 = 100;
let b: u32 = 200;

// 检查溢出
match a.checked_add(b) {
    Some(result) => println!("{}", result),
    None => println!("溢出"),
}

// 饱和运算
let result = a.saturating_sub(b);  // 不会溢出，结果为 0

// wrapping 运算
let result = a.wrapping_sub(b);

// ===== 哈希碰撞 =====
/*
    Rust 的 HashMap 默认使用 SipHash 算法
    - 防止哈希碰撞拒绝服务攻击
    - 不是密码学安全的哈希
    - 如果需要加密安全，使用专用哈希函数
*/

// 自定义哈希函数
use std::collections::HashMap;
use std::hash::BuildHasherDefault;
// 可以使用不同的哈希器实现
```

### 5.3 不安全的集合操作

```rust
/*
    大部分情况下，Rust 标准集合是安全的
    但以下情况需要注意：
*/

// ===== unsafe 操作 =====
let mut v = vec![1, 2, 3];

// 不安全的索引访问（绕开边界检查）
unsafe {
    let x = v.get_unchecked(10);  // ❌ 未定义行为！
    let x = v.get_unchecked_mut(10);
}

// ===== 原始指针操作 =====
let p = v.as_ptr();  // 获取原始指针
// 操作原始指针需要 unsafe

// ===== set_len 修改长度 =====
let mut v = Vec::with_capacity(10);
unsafe {
    v.set_len(10);  // ❌ 危险！未初始化的内存被视为有效
}

/*
    建议：
    - 除非必要，不要使用 unsafe
    - 优先使用安全的 API
    - get() 而不是 []（当不确定边界时）
    - checked_* 方法处理溢出
*/
```

### 5.4 密码学安全注意

```rust
use std::collections::HashMap;

/*
    注意：标准库的 HashMap/HashSet 
    不是密码学安全的，它们只是防止 HashDoS
    
    如果需要：
    - 密码哈希：用 argon2, bcrypt, scrypt 等库
    - 加密随机数：用 rand crate 的 OsRng
    - 加密哈希：用 sha2, sha3 等库
*/

// 安全的随机数（需要 rand crate）
// use rand::Rng;
// let mut rng = rand::rngs::OsRng;
// let random_num: u32 = rng.gen();

// 密码哈希（需要 argon2 crate）
// use argon2::{Argon2, PasswordHasher};
// let hash = argon2.hash_password(password.as_bytes(), &salt)?;
```

---

## 六、集合选择指南

| 需求 | 推荐集合 |
|------|---------|
| 动态数组，随机访问 | `Vec<T>` |
| 双端队列 | `VecDeque<T>` |
| 键值对，无序，快速查找 | `HashMap<K, V>` |
| 键值对，有序 | `BTreeMap<K, V>` |
| 无序集合，快速查找 | `HashSet<T>` |
| 有序集合 | `BTreeSet<T>` |
| 后进先出（栈） | `Vec<T>` / `VecDeque<T>` |
| 先进先出（队列） | `VecDeque<T>` |
| 固定大小数组（栈分配） | `[T; N]` |
| 字符串 | `String` / `&str` |
