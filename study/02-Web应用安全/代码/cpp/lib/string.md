# string - C++ 字符串库

> C++ 标准库字符串类 `std::string`，提供安全的字符串操作。

---

## 一、引入与基本用法

```cpp
#include <iostream>
#include <string>
#include <string_view>  // C++17
```

---

## 二、std::string 基本操作

### 2.1 创建与初始化

```cpp
// 多种初始化方式
std::string s1 = "hello";
std::string s2("world");
std::string s3(5, 'a');      // "aaaaa"
std::string s4 = s1;          // 拷贝构造
std::string s5 = std::move(s1);  // 移动构造（C++11）
std::string s6("hello world", 5);  // 前5个字符: "hello"

// C++11 列表初始化
std::string s7{"hello"};

// 从 char* 构造
const char* cstr = "hello";
std::string s8(cstr);

// 空字符串
std::string empty;
```

### 2.2 容量与访问

```cpp
std::string s = "hello world";

// 长度
s.size();       // 11
s.length();     // 11（和 size 一样）
s.empty();      // false
s.max_size();   // 最大可能长度

// 容量
s.capacity();   // 当前分配的容量
s.reserve(100); // 预分配 100 字节
s.shrink_to_fit();  // 释放多余容量（C++11）

// 访问字符
s[0];           // 'h'（不检查边界）
s.at(0);        // 'h'（越界抛 std::out_of_range 异常）
s.front();      // 第一个字符
s.back();       // 最后一个字符
s.data();       // 返回 char* 指针（C++11 保证以 '\0' 结尾）
s.c_str();      // 返回 C 风格字符串（const char*）
```

### 2.3 拼接与追加

```cpp
std::string s = "hello";

// 拼接
s += " world";          // "hello world"
s = s + "!";            // "hello world!"

// append 方法
s.append(" more");      // 追加字符串
s.append(3, '!');       // 追加 3 个 '!'
s.append("hello world", 0, 5);  // 追加子串

// push_back / pop_back
s.push_back('!');       // 追加一个字符
s.pop_back();           // 删除最后一个字符

// 插入
s.insert(5, " beautiful");  // 在位置 5 插入
s.insert(s.begin(), 'X');   // 在开头插入

// 删除
s.erase(5, 3);         // 从位置 5 删除 3 个字符
s.erase(s.begin());    // 删除第一个字符
s.clear();             // 清空
```

### 2.4 查找与替换

```cpp
std::string s = "hello world hello";

// 查找（返回位置索引，找不到返回 string::npos）
s.find("world");       // 6（从开头找）
s.find("hello", 1);    // 12（从位置 1 开始找）
s.rfind("hello");      // 12（从后往前找）

// 查找任一字符
s.find_first_of("aeiou");   // 1（第一个元音 'e'）
s.find_last_of("aeiou");    // 13
s.find_first_not_of("hel"); // 5（第一个不在 "hel" 中的字符）
s.find_last_not_of("lo");   // 11

// 替换
s.replace(6, 5, "there");   // 从位置 6 替换 5 个字符
// 结果: "hello there hello"

// 子串
std::string sub = s.substr(0, 5);  // "hello"（从 0 开始，取 5 个）
std::string tail = s.substr(6);    // 从 6 到末尾
```

### 2.5 比较

```cpp
std::string s1 = "apple";
std::string s2 = "banana";

// 比较运算符
s1 == s2;    // false
s1 != s2;    // true
s1 < s2;     // true（字典序）
s1 > s2;     // false
s1 <= s2;    // true
s1 >= s2;    // false

// compare 方法
s1.compare(s2);           // < 0 (s1 < s2)
s1.compare("apple");      // 0 (相等)
s1.compare(0, 1, s2, 0, 1);  // 比较部分
```

### 2.6 数值转换

```cpp
#include <string>

// 字符串 -> 数字
std::to_string(42);       // "42"
std::to_string(3.14);     // "3.140000"

// 数字 -> 字符串
std::stoi("42");          // 42 (int)
std::stol("1234567");     // 1234567 (long)
std::stoul("1234567");    // unsigned long
std::stoll("1234567890"); // long long
std::stoull("1234567890");// unsigned long long
std::stof("3.14");        // float
std::stod("3.14159");     // double
std::stold("3.14159");    // long double

// 带进制和位置
size_t pos;
int val = std::stoi("1010", &pos, 2);  // 二进制 1010 = 10
long hex_val = std::stol("FF", &pos, 16);  // 十六进制 FF = 255
```

---

## 三、C++17 std::string_view

```cpp
#include <string_view>

// string_view 是字符串的只读视图，不拷贝数据
std::string s = "hello world";
std::string_view sv = s;

// 支持大部分 string 的只读操作
sv.size();
sv[0];
sv.substr(0, 5);  // 返回新的 string_view（不拷贝）
sv.find("world");

// 从 C 字符串创建
std::string_view sv2("hello world");
std::string_view sv3("hello world", 5);  // "hello"

/*
    string_view 的优势：
    - 零拷贝，性能高
    - 函数参数传递更高效
    
    注意事项：
    - 不拥有数据，原字符串必须保持有效
    - 可能悬空（类似指针/引用）
    - 不保证以 '\0' 结尾
*/

// 安全的函数参数
void process(std::string_view sv) {  // 比 const std::string& 更灵活
    // 只读访问
    std::cout << sv.size() << std::endl;
}
```

---

## 四、安全相关内容

### 4.1 缓冲区溢出（C vs C++）

```cpp
/*
    C 风格字符串容易溢出：
    char buf[10];
    strcpy(buf, "hello world");  // ❌ 溢出
    
    C++ std::string 自动管理内存：
    std::string s = "hello world";  // ✅ 自动扩容
*/

// ===== 危险：用 C 方式操作 string =====
std::string s = "hello";
char* ptr = &s[0];
strcpy(ptr, "this is way too long");  // ❌ 溢出！破坏内存

// ===== 安全：使用 string 的方法 =====
s = "this is way too long";  // ✅ 自动扩容

// ===== at() vs [] =====
std::string s = "hello";
s[10] = 'x';     // ❌ 未定义行为（越界不检查）
s.at(10) = 'x';  // ✅ 抛出 std::out_of_range 异常

// 建议：
// - 确定安全时用 []（性能好）
// - 不确定时用 at()（安全）
```

### 4.2 整数溢出与字符串长度

```cpp
/*
    size_t 是无符号整数，注意溢出和比较问题
*/

// 危险的比较
std::string s = "test";
int n = -1;
if (s.size() < n) {  // n 被转为 size_t，变成很大的数！
    // 这个条件可能意外成立
}

// 正确的写法
if (n < 0 || s.size() < static_cast<size_t>(n)) {
    // ...
}

// substr 的边界检查
std::string s = "hello";
s.substr(10);  // 越界？不，会抛 out_of_range 异常

try {
    auto sub = s.substr(10);
} catch (const std::out_of_range& e) {
    std::cerr << "越界: " << e.what() << std::endl;
}
```

### 4.3 格式化字符串安全

```cpp
/*
    C 风格 printf 格式化字符串漏洞在 C++ 中仍然存在
    推荐使用 C++20 std::format 或 fmt 库
*/

#include <cstdio>
#include <string>

// ❌ 危险：用户输入作为格式串
void dangerous(const std::string& user_input) {
    printf(user_input.c_str());  // 格式化字符串漏洞！
}

// ✅ 安全：作为参数
void safe(const std::string& user_input) {
    printf("%s", user_input.c_str());  // 作为参数，不是格式串
}

// ===== C++20 std::format =====
#include <format>

std::string name = "Alice";
int age = 25;
std::string msg = std::format("Hello, {}! You are {} years old.", name, age);

// 类型安全：编译时检查格式串
auto msg2 = std::format("{:d}", "not a number");  // 编译错误！
```

### 4.4 密码与敏感数据处理

```cpp
#include <string>
#include <algorithm>

/*
    std::string 析构时不一定会清零内存
    敏感数据（密码、密钥等）需要手动清除
*/

// 安全字符串（析构时清零）
class SecureString {
public:
    SecureString(const std::string& data) : data_(data) {}
    
    ~SecureString() {
        // 清零内存
        std::fill(data_.begin(), data_.end(), '\0');
        data_.clear();
        data_.shrink_to_fit();
    }
    
    const std::string& get() const { return data_; }
    
private:
    std::string data_;
};

// 使用
{
    SecureString password("my_secret_password");
    // 使用 password.get()...
}  // 离开作用域时自动清零

// 手动清零
std::string secret = "password";
// 使用后...
std::fill(secret.begin(), secret.end(), '\0');
secret.clear();
```

---

## 五、常见操作速查

| 操作 | 方法 |
|------|------|
| 获取长度 | `s.size()` / `s.length()` |
| 是否为空 | `s.empty()` |
| 追加 | `s += ...` / `s.append(...)` |
| 插入 | `s.insert(pos, ...)` |
| 删除 | `s.erase(pos, len)` |
| 查找 | `s.find(...)` |
| 替换 | `s.replace(pos, len, ...)` |
| 子串 | `s.substr(pos, len)` |
| 比较 | `s == other` / `s.compare(...)` |
| 转 C 串 | `s.c_str()` |
| 清空 | `s.clear()` |
| 预分配 | `s.reserve(n)` |
