# cout_cin

> **分类**：输入输出
> **说明**：C++ 标准输入输出流

---

## 语法

```cpp
cout << expression << endl;\ncin >> variable;
```

## 头文件

#include <iostream>\nusing namespace std;

## 常用操纵符

endl 换行 / setw(n) 宽度 / setprecision(n) 精度 / left/right 对齐 / hex/oct/dec 进制

## 示例代码

```cpp
#include <iostream>
#include <iomanip>
using namespace std;

int main() {
    // 基本输出
    cout << "Hello, World!" << endl;
    cout << "数字: " << 42 << endl;
    cout << "浮点数: " << 3.14 << endl;

    // 多种输出
    int a = 10, b = 20;
    cout << "a = " << a << ", b = " << b << endl;

    // 输入
    string name;
    int age;
    cout << "输入姓名: ";
    cin >> name;
    cout << "输入年龄: ";
    cin >> age;
    cout << "姓名: " << name << ", 年龄: " << age << endl;

    // 多行输入
    string line;
    getline(cin, line);  // 读取一整行

    // 格式化输出
    cout << setw(10) << "左对齐" << setw(10) << "右对齐" << endl;
    cout << setprecision(4) << 3.1415926 << endl;  // 3.142
    cout << fixed << setprecision(2) << 3.14159 << endl;  // 3.14

    // 进制输出
    cout << hex << 255 << endl;   // ff
    cout << oct << 255 << endl;   // 377
    cout << dec << 255 << endl;   // 255

    // 布尔值输出
    cout << boolalpha << true << endl;   // true
    cout << noboolalpha << true << endl; // 1

    // 错误输出
    cerr << "错误信息" << endl;
    clog << "日志信息" << endl;

    return 0;
}
```
