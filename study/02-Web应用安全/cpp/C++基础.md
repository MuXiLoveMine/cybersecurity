# C/C++ 语言基础

## 目录

1. [C/C++ 简介](#1-cc-简介)
2. [环境配置](#2-环境配置)
3. [C 基础：变量、数据类型、运算符、输入输出](#3-c-基础变量数据类型运算符输入输出)
4. [控制流](#4-控制流)
5. [函数](#5-函数)
6. [数组与字符串](#6-数组与字符串)
7. [指针与引用](#7-指针与引用)
8. [结构体](#8-结构体)
9. [C++ 面向对象](#9-c-面向对象)
10. [STL 容器](#10-stl-容器)
11. [STL 算法](#11-stl-算法)
12. [文件操作](#12-文件操作)
13. [网络编程](#13-网络编程)
14. [正则表达式](#14-正则表达式)
15. [C/C++ 在安全领域的应用](#15-cc-在安全领域的应用)

---

## 1. C/C++ 简介

### 1.1 历史

- **C 语言**：1972 年由 Dennis Ritchie 在贝尔实验室设计，用于重写 UNIX 操作系统。是一门结构化、过程式的编程语言。
- **C++**：1983 年由 Bjarne Stroustrup 在贝尔实验室设计，最初称为 "C with Classes"。在 C 语言基础上增加了面向对象特性。
- **标准演进**：C++98 → C++03 → C++11 → C++14 → C++17 → C++20 → C++23

### 1.2 特点

| 特点 | 说明 |
|------|------|
| **高效** | 直接操作内存，编译为机器码，执行效率高 |
| **跨平台** | 源码级跨平台，需在各平台重新编译 |
| **手动内存管理** | 需要程序员自行管理堆内存（new/delete、malloc/free） |
| **面向对象** | 支持封装、继承、多态 |
| **泛型编程** | 模板（Template）机制 |
| **底层能力** | 可直接操作硬件、内存、指针 |

### 1.3 和安全的关系

C/C++ 是安全研究中最重要的编程语言之一，原因如下：

- **操作系统底层**：Windows、Linux、macOS 内核均由 C 编写
- **逆向分析**：大量软件（尤其是恶意软件）由 C/C++ 编译，逆向工程师需要理解 C/C++ 代码对应的汇编
- **漏洞挖掘**：内存安全漏洞（缓冲区溢出、Use-After-Free、整数溢出等）主要存在于 C/C++ 程序中
- **Exploit 开发**：Shellcode、ROP 链、内存破坏利用均需要深入理解 C/C++ 内存模型
- **安全工具开发**：调试器、反汇编器（IDA Pro 插件）、Fuzzer（AFL）常用 C/C++ 开发

---

## 2. 环境配置

### 2.1 Windows 平台

#### MinGW（GCC 的 Windows 版本）

1. 下载 MinGW-w64：https://www.mingw-w64.org/
2. 安装后将 `bin` 目录加入系统 PATH
3. 验证：打开 cmd，输入 `g++ --version`

#### Visual Studio

1. 下载 Visual Studio Community（免费）
2. 安装 "使用 C++ 的桌面开发" 工作负载
3. 使用 Developer Command Prompt 编译

### 2.2 Linux 平台

```bash
sudo apt update
sudo apt install build-essential   # Ubuntu/Debian
sudo yum groupinstall "Development Tools"  # CentOS/RHEL
gcc --version
g++ --version
```

### 2.3 编译运行

```bash
# 编译 C++ 程序
g++ hello.cpp -o hello

# 编译 C 程序
gcc hello.c -o hello

# 启用警告和调试信息
g++ -Wall -g hello.cpp -o hello

# 指定 C++ 标准
g++ -std=c++17 hello.cpp -o hello

# 运行
./hello          # Linux/Mac
hello.exe        # Windows
```

---

## 3. C 基础：变量、数据类型、运算符、输入输出

### 3.1 变量与数据类型

```cpp
// 基本数据类型
int a = 10;                 // 整数，通常 4 字节
short s = 100;              // 短整数，2 字节
long l = 100000L;           // 长整数，4 或 8 字节
long long ll = 123456789LL; // 长长整数，8 字节

float f = 3.14f;            // 单精度浮点数，4 字节
double d = 3.14159;         // 双精度浮点数，8 字节

char c = 'A';               // 字符，1 字节
bool b = true;              // 布尔值（C++），1 字节

// 无符号类型
unsigned int ui = 100;
unsigned char uc = 255;

// 常量
const int MAX = 100;
#define PI 3.14159  // C 风格宏定义
```

### 3.2 运算符

| 类型 | 运算符 |
|------|--------|
| 算术 | `+` `-` `*` `/` `%` `++` `--` |
| 关系 | `==` `!=` `>` `<` `>=` `<=` |
| 逻辑 | `&&` `||` `!` |
| 位运算 | `&` `\|` `^` `~` `<<` `>>` |
| 赋值 | `=` `+=` `-=` `*=` `/=` `%=` |
| 条件 | `?:` （三目运算符） |
| 指针 | `*` `&` `->` |
| 其他 | `sizeof` `,` `.` `[]` |

### 3.3 输入输出

C 风格：
```c
#include <stdio.h>

int main() {
    int num;
    char name[20];
    
    printf("请输入数字：");
    scanf("%d", &num);
    
    printf("请输入姓名：");
    scanf("%s", name);
    
    printf("数字：%d，姓名：%s\n", num, name);
    return 0;
}
```

C++ 风格：
```cpp
#include <iostream>
#include <string>
using namespace std;

int main() {
    int num;
    string name;
    
    cout << "请输入数字：";
    cin >> num;
    
    cout << "请输入姓名：";
    cin >> name;
    
    cout << "数字：" << num << "，姓名：" << name << endl;
    return 0;
}
```

---

## 4. 控制流

### 4.1 if / else

```cpp
int score = 85;

if (score >= 90) {
    cout << "优秀" << endl;
} else if (score >= 60) {
    cout << "及格" << endl;
} else {
    cout << "不及格" << endl;
}
```

### 4.2 for 循环

```cpp
for (int i = 0; i < 10; i++) {
    cout << i << " ";
}

// 范围 for 循环（C++11）
int arr[] = {1, 2, 3, 4, 5};
for (int x : arr) {
    cout << x << " ";
}
```

### 4.3 while / do-while

```cpp
int i = 0;
while (i < 10) {
    cout << i << " ";
    i++;
}

int j = 0;
do {
    cout << j << " ";
    j++;
} while (j < 10);
```

### 4.4 switch

```cpp
int day = 3;
switch (day) {
    case 1: cout << "星期一"; break;
    case 2: cout << "星期二"; break;
    case 3: cout << "星期三"; break;
    default: cout << "其他";
}
```

### 4.5 跳转语句

- `break`：跳出循环或 switch
- `continue`：跳过本次循环剩余部分
- `goto`：跳转到指定标签（不推荐滥用）
- `return`：从函数返回

---

## 5. 函数

### 5.1 函数定义

```cpp
// 返回类型 函数名(参数列表) { 函数体 }
int add(int a, int b) {
    return a + b;
}

// 无返回值函数
void print_hello() {
    cout << "Hello" << endl;
}
```

### 5.2 函数声明（原型）

```cpp
// 函数声明，可以放在调用之前
int add(int a, int b);

int main() {
    int result = add(3, 5);  // 调用函数
    return 0;
}
```

### 5.3 参数传递

```cpp
// 值传递
void swap_by_value(int a, int b) {
    int temp = a; a = b; b = temp;
}  // 不影响实参

// 指针传递
void swap_by_pointer(int* a, int* b) {
    int temp = *a; *a = *b; *b = temp;
}

// 引用传递（C++）
void swap_by_ref(int& a, int& b) {
    int temp = a; a = b; b = temp;
}
```

### 5.4 递归

```cpp
// 计算阶乘
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// 斐波那契数列
int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}
```

### 5.5 函数重载（C++）

```cpp
int max(int a, int b) {
    return a > b ? a : b;
}

double max(double a, double b) {
    return a > b ? a : b;
}
// 同名函数，参数类型不同，自动匹配
```

---

## 6. 数组与字符串

### 6.1 数组

```cpp
// 一维数组
int arr[5] = {1, 2, 3, 4, 5};
int nums[] = {10, 20, 30};  // 自动推断大小

// 访问
cout << arr[0];  // 第一个元素
arr[2] = 100;

// 二维数组
int matrix[3][3] = {
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9}
};
```

### 6.2 C 风格字符串

```c
#include <string.h>

char str1[20] = "Hello";
char str2[] = "World";

// 字符串操作函数
strlen(str1);          // 长度：5
strcpy(str1, str2);    // 复制
strcat(str1, str2);    // 拼接
strcmp(str1, str2);    // 比较，0 表示相等
strchr(str1, 'e');     // 查找字符
```

**安全注意**：`strcpy`、`gets` 等函数不检查边界，容易导致缓冲区溢出。

### 6.3 C++ string 类

```cpp
#include <string>
using namespace std;

string s1 = "Hello";
string s2 = "World";

// 操作
string s3 = s1 + " " + s2;  // 拼接
s1.length();                // 长度
s1.find("lo");              // 查找
s1.substr(0, 3);            // 子串
s1.compare(s2);             // 比较
s1.c_str();                 // 转为 C 风格字符串（const char*）
```

---

## 7. 指针与引用

### 7.1 指针基础

```cpp
int x = 10;
int* p = &x;   // p 指向 x 的地址

cout << *p;    // 解引用，输出 10
*p = 20;       // 通过指针修改 x 的值
```

### 7.2 指针与数组

```cpp
int arr[5] = {1, 2, 3, 4, 5};
int* p = arr;   // 数组名是首元素地址

cout << *p;      // arr[0]
cout << *(p+1);  // arr[1]
cout << p[2];    // arr[2]，指针也可以用下标
```

### 7.3 动态内存分配

```cpp
// C 风格
int* p = (int*)malloc(sizeof(int) * 10);
free(p);

// C++ 风格
int* p = new int(10);       // 单个对象
delete p;

int* arr = new int[10];     // 数组
delete[] arr;
```

**安全注意**：忘记释放内存会导致内存泄漏；释放后继续使用会导致 Use-After-Free 漏洞。

### 7.4 引用（C++）

```cpp
int x = 10;
int& ref = x;   // ref 是 x 的引用（别名）

ref = 20;       // 修改 ref 就是修改 x
cout << x;      // 输出 20
```

引用 vs 指针：
- 引用必须在声明时初始化，且不能改变指向
- 引用更安全，不存在空引用
- 引用本质上是语法糖，底层通常用指针实现

### 7.5 空指针

```cpp
int* p = nullptr;   // C++11 推荐
int* p = NULL;      // C 风格宏
```

---

## 8. 结构体

### 8.1 定义与使用

```cpp
struct Student {
    int id;
    char name[20];
    int age;
    float score;
};

// 使用
Student s1;
s1.id = 1001;
strcpy(s1.name, "张三");
s1.age = 20;
s1.score = 95.5;

// 初始化
Student s2 = {1002, "李四", 21, 88.0};
```

### 8.2 结构体指针

```cpp
Student* p = &s1;
cout << p->id;     // 使用 -> 访问成员
cout << (*p).age;  // 等价写法
```

### 8.3 结构体数组

```cpp
Student class1[3] = {
    {1001, "张三", 20, 95.5},
    {1002, "李四", 21, 88.0},
    {1003, "王五", 19, 92.0}
};
```

### 8.4 内存对齐

结构体的内存布局可能因对齐而产生填充字节：

```cpp
struct Example {
    char a;    // 1 字节
    // 3 字节填充
    int b;     // 4 字节
    short c;   // 2 字节
    // 2 字节填充
};
// 总大小：12 字节（而非 7 字节）
```

可以使用 `#pragma pack(1)` 取消对齐（在逆向分析中常见）。

---

## 9. C++ 面向对象

### 9.1 类与对象

```cpp
#include <iostream>
using namespace std;

class Person {
private:
    string name;    // 私有成员
    int age;

public:
    // 构造函数
    Person(string n, int a) : name(n), age(a) {}

    // 成员函数
    void introduce() {
        cout << "我叫" << name << "，今年" << age << "岁" << endl;
    }

    // Getter / Setter
    string getName() { return name; }
    void setAge(int a) { age = a; }
};

int main() {
    Person p("张三", 20);
    p.introduce();
    p.setAge(21);
    return 0;
}
```

### 9.2 封装

- `public`：公开的，外部可访问
- `private`：私有的，只有类内部可访问
- `protected`：受保护的，子类可访问

### 9.3 继承

```cpp
class Student : public Person {
private:
    int student_id;

public:
    Student(string n, int a, int id) : Person(n, a), student_id(id) {}

    void study() {
        cout << getName() << "在学习" << endl;
    }
};
```

继承方式：
- `public` 继承：基类 public → 派生类 public，protected → protected
- `protected` 继承：基类 public/protected → 派生类 protected
- `private` 继承：基类所有成员 → 派生类 private

### 9.4 多态

```cpp
class Animal {
public:
    virtual void speak() {  // 虚函数
        cout << "动物叫" << endl;
    }
    virtual ~Animal() {}    // 虚析构函数
};

class Dog : public Animal {
public:
    void speak() override {
        cout << "汪汪汪" << endl;
    }
};

class Cat : public Animal {
public:
    void speak() override {
        cout << "喵喵喵" << endl;
    }
};

// 使用：基类指针指向派生类对象
Animal* a = new Dog();
a->speak();   // 输出 "汪汪汪"（动态绑定）
delete a;
```

### 9.5 虚函数表（vtable）

每个含有虚函数的类都有一张虚函数表，对象的前 4/8 字节是指向虚表的指针（vptr）。这是逆向分析中的重要概念。

---

## 10. STL 容器

### 10.1 vector（动态数组/列表）

```cpp
#include <vector>
#include <iostream>
using namespace std;

vector<int> v;

// 添加元素
v.push_back(10);
v.push_back(20);
v.push_back(30);

// 访问
cout << v[0];        // 下标访问
cout << v.at(1);     // 带边界检查
cout << v.front();   // 第一个元素
cout << v.back();    // 最后一个元素

// 大小
v.size();
v.empty();

// 删除
v.pop_back();        // 删除末尾
v.erase(v.begin());  // 删除指定位置

// 遍历
for (int i = 0; i < v.size(); i++)
    cout << v[i] << " ";

for (int x : v)      // C++11 范围 for
    cout << x << " ";
```

### 10.2 map（键值对/字典）

```cpp
#include <map>
#include <string>
using namespace std;

map<string, int> m;

// 插入
m["apple"] = 3;
m.insert(make_pair("banana", 5));

// 访问
cout << m["apple"];

// 查找
if (m.find("orange") != m.end()) {
    // 找到了
}

// 遍历
for (auto& pair : m) {
    cout << pair.first << ": " << pair.second << endl;
}

// 删除
m.erase("apple");
```

map 是有序的（基于红黑树），unordered_map 是哈希表实现。

### 10.3 string

```cpp
#include <string>
using namespace std;

string s = "Hello, World!";

// 常用操作
s.length();                    // 长度
s.substr(0, 5);                // 子串："Hello"
s.find("World");               // 查找位置：7
s.replace(7, 5, "C++");        // 替换
s.erase(0, 7);                 // 删除
s.insert(0, "Hi ");            // 插入

// 转换
s.c_str();                     // 转 const char*
stoi(s);                       // 转 int（C++11）
stod(s);                       // 转 double
to_string(123);                // 数字转 string
```

### 10.4 set（集合）

```cpp
#include <set>
using namespace std;

set<int> s;

s.insert(10);
s.insert(20);
s.insert(10);   // 重复元素不会被插入

s.count(10);    // 1（存在）
s.count(30);    // 0（不存在）

for (int x : s) cout << x << " ";
```

### 10.5 其他容器

- `list`：双向链表
- `deque`：双端队列
- `stack`：栈（适配器）
- `queue`：队列（适配器）
- `priority_queue`：优先队列
- `unordered_map` / `unordered_set`：哈希表

---

## 11. STL 算法

```cpp
#include <algorithm>
#include <vector>
using namespace std;

vector<int> v = {5, 2, 8, 1, 9, 3};

// 排序
sort(v.begin(), v.end());                  // 升序
sort(v.begin(), v.end(), greater<int>());  // 降序

// 查找
auto it = find(v.begin(), v.end(), 8);
if (it != v.end()) { /* 找到 */ }

// 计数
int cnt = count(v.begin(), v.end(), 5);

// 反转
reverse(v.begin(), v.end());

// 去重（需先排序）
sort(v.begin(), v.end());
auto last = unique(v.begin(), v.end());
v.erase(last, v.end());

// 遍历
for_each(v.begin(), v.end(), [](int x) {
    cout << x << " ";
});

// 最大值/最小值
int max_val = *max_element(v.begin(), v.end());
int min_val = *min_element(v.begin(), v.end());
```

---

## 12. 文件操作

### 12.1 C 风格文件操作

```c
#include <stdio.h>

// 写文件
FILE* fp = fopen("test.txt", "w");
if (fp) {
    fprintf(fp, "Hello, %s\n", "World");
    fputc('A', fp);
    fclose(fp);
}

// 读文件
FILE* fp = fopen("test.txt", "r");
if (fp) {
    char buf[100];
    fgets(buf, sizeof(buf), fp);  // 读一行
    printf("%s", buf);
    fclose(fp);
}
```

### 12.2 C++ 文件流

```cpp
#include <fstream>
#include <iostream>
#include <string>
using namespace std;

// 写文件
ofstream out("test.txt");
if (out.is_open()) {
    out << "Hello, World!" << endl;
    out << 123 << endl;
    out.close();
}

// 读文件
ifstream in("test.txt");
if (in.is_open()) {
    string line;
    while (getline(in, line)) {
        cout << line << endl;
    }
    in.close();
}
```

### 12.3 二进制文件

```cpp
ofstream out("data.bin", ios::binary);
int num = 12345;
out.write((char*)&num, sizeof(num));
out.close();

ifstream in("data.bin", ios::binary);
int num;
in.read((char*)&num, sizeof(num));
in.close();
```

---

## 13. 网络编程

### 13.1 Socket 基础

Linux 下的简单 TCP 客户端：

```cpp
#include <iostream>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
using namespace std;

int main() {
    // 创建 socket
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    
    // 设置服务器地址
    sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8080);
    inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr);
    
    // 连接
    connect(sockfd, (sockaddr*)&server_addr, sizeof(server_addr));
    
    // 发送数据
    const char* msg = "Hello Server";
    send(sockfd, msg, strlen(msg), 0);
    
    // 接收数据
    char buf[1024];
    int n = recv(sockfd, buf, sizeof(buf)-1, 0);
    buf[n] = '\0';
    cout << "收到：" << buf << endl;
    
    close(sockfd);
    return 0;
}
```

### 13.2 简单 TCP 服务器

```cpp
#include <iostream>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
using namespace std;

int main() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    
    sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(8080);
    
    bind(server_fd, (sockaddr*)&addr, sizeof(addr));
    listen(server_fd, 5);
    
    cout << "监听 8080 端口..." << endl;
    
    while (true) {
        sockaddr_in client_addr;
        socklen_t len = sizeof(client_addr);
        int client_fd = accept(server_fd, (sockaddr*)&client_addr, &len);
        
        char buf[1024];
        int n = recv(client_fd, buf, sizeof(buf)-1, 0);
        buf[n] = '\0';
        cout << "收到：" << buf << endl;
        
        send(client_fd, buf, n, 0);  // 回显
        close(client_fd);
    }
    
    close(server_fd);
    return 0;
}
```

**Windows 下需使用 Winsock2**，初始化 `WSAStartup`，使用 `closesocket` 代替 `close`。

---

## 14. 正则表达式（C++11 regex）

```cpp
#include <iostream>
#include <string>
#include <regex>
using namespace std;

int main() {
    string s = "我的邮箱是 test@example.com 和 admin@test.org";

    // 匹配模式
    regex pattern(R"(\w+@\w+\.\w+)");

    // 搜索
    smatch match;
    if (regex_search(s, match, pattern)) {
        cout << "找到：" << match.str() << endl;
    }

    // 查找所有匹配
    auto begin = sregex_iterator(s.begin(), s.end(), pattern);
    auto end = sregex_iterator();
    for (auto i = begin; i != end; ++i) {
        cout << "匹配：" << i->str() << endl;
    }

    // 替换
    string result = regex_replace(s, pattern, "[邮箱已隐藏]");
    cout << result << endl;

    // 完全匹配
    string ip = "192.168.1.1";
    regex ip_pattern(R"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})");
    if (regex_match(ip, ip_pattern)) {
        cout << "是 IP 地址" << endl;
    }

    return 0;
}
```

编译时注意：部分旧版本 GCC 需要加 `-std=c++11`。

---

## 15. C/C++ 在安全领域的应用

### 15.1 逆向分析

- **静态分析**：使用 IDA Pro、Ghidra 等工具将二进制反编译为伪 C 代码
- **动态分析**：使用 x64dbg、OllyDbg、GDB 调试程序
- **关键能力**：
  - 理解 C/C++ 代码如何编译为汇编
  - 识别结构体、类、虚函数表
  - 理解调用约定（cdecl、stdcall、fastcall、thiscall）
  - 分析字符串、数组、指针的内存布局

### 15.2 漏洞挖掘

常见 C/C++ 漏洞类型：

| 漏洞类型 | 说明 | 相关函数 |
|----------|------|----------|
| **缓冲区溢出** | 向缓冲区写入超过其大小的数据 | `strcpy`、`sprintf`、`gets` |
| **栈溢出** | 栈上缓冲区溢出，可覆盖返回地址 | 同上 |
| **堆溢出** | 堆上缓冲区溢出，破坏堆结构 | `strcpy`、`memcpy` |
| **Use-After-Free** | 释放内存后继续使用 | `free` / `delete` |
| **Double Free** | 同一块内存释放两次 | `free` / `delete` |
| **整数溢出** | 整数运算超出范围，导致分配不足 | 各种运算 |
| **格式化字符串** | 格式化字符串参数可控 | `printf` 系列 |
| **越界读写** | 数组下标越界 | 数组操作 |

### 15.3 Exploit 开发

- **Shellcode 编写**：用汇编编写，注入到目标进程执行
- **ROP（Return-Oriented Programming）**：利用已有代码片段绕过 DEP
- **堆喷射（Heap Spraying）**：在堆上布置大量可控数据
- **信息泄露**：通过漏洞泄露内存地址，绕过 ASLR
- **相关工具**：pwntools（Python 库）、Metasploit

### 15.4 缓冲区溢出示例（概念）

```c
// 存在栈溢出漏洞的代码
void vulnerable_function(char* input) {
    char buffer[64];   // 64 字节缓冲区
    strcpy(buffer, input);  // 没有检查长度！
}

int main(int argc, char* argv[]) {
    vulnerable_function(argv[1]);
    return 0;
}
```

当输入超过 64 字节时，会覆盖栈上的返回地址，攻击者可以控制程序执行流。

### 15.5 安全开发建议

- 使用安全函数：`strncpy`、`snprintf`、`fgets`
- 开启编译器保护：`-fstack-protector`、`-D_FORTIFY_SOURCE=2`、`-fPIE`
- 开启操作系统保护：ASLR、DEP/NX、GS 保护
- 使用现代 C++ 特性：`std::string`、`std::vector` 代替裸指针和手动内存管理
- 使用内存检测工具：Valgrind、AddressSanitizer（ASAN）

---

## 参考资源

- [cppreference.com](https://en.cppreference.com/) — C++ 参考文档
- [cplusplus.com](http://www.cplusplus.com/) — C++ 教程
- 《C Primer Plus》— C 语言入门经典
- 《C++ Primer》— C++ 入门经典
- 《深入理解计算机系统》— 计算机系统基础
- 《漏洞战争》— 软件漏洞分析
- 《0day 安全：软件漏洞分析技术》— 漏洞挖掘与利用
