# variable_cpp

> **分类**：变量与类型
> **说明**：C++ 变量和数据类型

---

## 语法

```cpp
type variableName = value;
```

## 基本类型

bool/char/short/int/long/long long/float/double/long double/wchar_t

## 修饰符

signed/unsigned/short/long/const/static/volatile

## C++11+

auto 类型推导 / decltype / nullptr / using 别名

## 示例代码

```cpp
#include <iostream>
#include <string>
#include <vector>
using namespace std;

int main() {
    // 整数类型
    int i = 42;
    short s = 32767;
    long l = 2147483647L;
    long long ll = 9223372036854775807LL;
    unsigned int ui = 4294967295U;

    // 浮点类型
    float f = 3.14f;
    double d = 3.1415926535;
    long double ld = 3.14159265358979L;

    // 字符和布尔
    char c = 'A';
    bool b = true;

    // 字符串
    string str = "Hello, World!";
    cout << str.length() << endl;    // 长度
    cout << str.substr(0, 5) << endl; // 子串
    cout << str + " C++" << endl;     // 拼接

    // const 常量
    const int MAX_SIZE = 100;
    const double PI = 3.14159;

    // auto 类型推导 (C++11)
    auto x = 42;          // int
    auto y = 3.14;        // double
    auto s = "hello";     // const char*
    auto v = vector<int>{1,2,3};  // vector<int>

    // decltype
    int a = 10;
    decltype(a) b = 20;  // b 也是 int

    // 引用
    int num = 42;
    int& ref = num;      // ref 是 num 的引用
    ref = 100;           // 修改 ref 也修改 num
    cout << num << endl; // 100

    // 指针
    int val = 42;
    int* ptr = &val;
    cout << *ptr << endl;  // 42
    *ptr = 100;
    cout << val << endl;   // 100

    // nullptr (C++11，优于 NULL)
    int* p = nullptr;

    // 类型别名
    using MyInt = int;
    MyInt n = 42;

    // 枚举
    enum Color { Red, Green, Blue };
    Color color = Red;

    // enum class (C++11，强类型枚举)
    enum class Direction { Up, Down, Left, Right };
    Direction dir = Direction::Up;

    return 0;
}
```
