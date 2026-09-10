// ============================================================
// 03_functions.cpp —— 函数定义、参数、返回值、递归
// 编译命令：g++ 03_functions.cpp -o 03_functions
// 运行命令：./03_functions（Linux/Mac） 或 03_functions.exe（Windows）
// ============================================================

#include <iostream>
#include <string>
using namespace std;

// ============================================================
// 一、函数的声明（原型）与定义
// ============================================================

// 函数声明（也叫函数原型）：告诉编译器函数的存在
// 返回类型 函数名(参数类型列表);
int add(int a, int b);
void print_hello();
int max(int a, int b);
void swap_by_value(int a, int b);
void swap_by_pointer(int* a, int* b);
void swap_by_ref(int& a, int& b);
int factorial(int n);
int fibonacci(int n);


// ============================================================
// 二、基本函数
// ============================================================

// 有返回值的函数：计算两个数的和
int add(int a, int b) {
    return a + b;
}

// 无返回值的函数：打印问候
void print_hello() {
    cout << "Hello from print_hello()!" << endl;
}

// 返回较大值
int max(int a, int b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}

// 多个 return 语句的函数
string get_grade(int score) {
    if (score >= 90) return "A";
    if (score >= 80) return "B";
    if (score >= 70) return "C";
    if (score >= 60) return "D";
    return "F";
}


// ============================================================
// 三、参数传递方式
// ============================================================

// 1. 值传递：传递的是实参的副本，函数内修改不影响实参
void swap_by_value(int a, int b) {
    int temp = a;
    a = b;
    b = temp;
    cout << "  swap_by_value 内部：a = " << a << ", b = " << b << endl;
}

// 2. 指针传递：传递地址，可以修改实参的值
void swap_by_pointer(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

// 3. 引用传递（C++）：传递的是实参的别名，可以修改实参
void swap_by_ref(int& a, int& b) {
    int temp = a;
    a = b;
    b = temp;
}


// ============================================================
// 四、函数重载（C++ 特性）
// ============================================================

// 同名函数，参数类型或数量不同
int add_num(int a, int b) {
    return a + b;
}

double add_num(double a, double b) {
    return a + b;
}

int add_num(int a, int b, int c) {
    return a + b + c;
}


// ============================================================
// 五、默认参数
// ============================================================

// 默认参数必须从右往左依次声明
void print_info(string name, int age = 18, string city = "北京") {
    cout << "姓名：" << name << "，年龄：" << age << "，城市：" << city << endl;
}


// ============================================================
// 六、递归函数
// ============================================================

// 阶乘：n! = n * (n-1)!，0! = 1
int factorial(int n) {
    if (n <= 1) {
        return 1;  // 基准情况（递归出口）
    }
    return n * factorial(n - 1);  // 递归调用
}

// 斐波那契数列：F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)
int fibonacci(int n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// 递归求和：1+2+...+n
int sum_recursive(int n) {
    if (n <= 0) return 0;
    return n + sum_recursive(n - 1);
}


// ============================================================
// 七、内联函数（inline）
// ============================================================

// inline 建议编译器将函数体直接展开到调用处，减少函数调用开销
inline int square(int x) {
    return x * x;
}


// ============================================================
// 主函数
// ============================================================

int main() {
    // ---------- 1. 基本函数调用 ----------
    cout << "========== 基本函数调用 ==========" << endl;

    print_hello();

    int result = add(3, 5);
    cout << "add(3, 5) = " << result << endl;

    cout << "max(10, 20) = " << max(10, 20) << endl;
    cout << "max(100, 50) = " << max(100, 50) << endl;

    cout << "get_grade(85) = " << get_grade(85) << endl;
    cout << "get_grade(59) = " << get_grade(59) << endl;


    // ---------- 2. 参数传递方式 ----------
    cout << "\n========== 参数传递方式 ==========" << endl;

    int x = 10, y = 20;
    cout << "初始值：x = " << x << ", y = " << y << endl;

    // 值传递：不影响实参
    cout << "\n值传递：" << endl;
    swap_by_value(x, y);
    cout << "  调用后：x = " << x << ", y = " << y << "（没变）" << endl;

    // 指针传递：可以修改实参
    x = 10; y = 20;
    cout << "\n指针传递：" << endl;
    swap_by_pointer(&x, &y);  // 传入地址
    cout << "  调用后：x = " << x << ", y = " << y << "（交换了）" << endl;

    // 引用传递：可以修改实参（语法更简洁）
    x = 10; y = 20;
    cout << "\n引用传递：" << endl;
    swap_by_ref(x, y);
    cout << "  调用后：x = " << x << ", y = " << y << "（交换了）" << endl;


    // ---------- 3. 函数重载 ----------
    cout << "\n========== 函数重载 ==========" << endl;

    cout << "add_num(3, 5) = " << add_num(3, 5) << "  （int 版本）" << endl;
    cout << "add_num(3.14, 2.72) = " << add_num(3.14, 2.72) << "  （double 版本）" << endl;
    cout << "add_num(1, 2, 3) = " << add_num(1, 2, 3) << "  （三个参数版本）" << endl;


    // ---------- 4. 默认参数 ----------
    cout << "\n========== 默认参数 ==========" << endl;

    print_info("张三");                    // 使用全部默认值
    print_info("李四", 25);                // 部分默认值
    print_info("王五", 30, "上海");        // 全部自定义


    // ---------- 5. 递归函数 ----------
    cout << "\n========== 递归函数 ==========" << endl;

    // 阶乘
    cout << "阶乘：" << endl;
    for (int i = 0; i <= 6; i++) {
        cout << "  " << i << "! = " << factorial(i) << endl;
    }

    // 斐波那契数列
    cout << "\n斐波那契数列（前 10 项）：" << endl;
    for (int i = 0; i < 10; i++) {
        cout << fibonacci(i) << " ";
    }
    cout << endl;

    // 递归求和
    cout << "\n递归求和 1+2+...+100 = " << sum_recursive(100) << endl;

    // 递归的工作原理说明
    cout << "\n递归的执行过程（以 factorial(4) 为例）：" << endl;
    cout << "  factorial(4)" << endl;
    cout << "    = 4 * factorial(3)" << endl;
    cout << "    = 4 * 3 * factorial(2)" << endl;
    cout << "    = 4 * 3 * 2 * factorial(1)" << endl;
    cout << "    = 4 * 3 * 2 * 1" << endl;
    cout << "    = 24" << endl;


    // ---------- 6. 内联函数 ----------
    cout << "\n========== 内联函数 ==========" << endl;

    cout << "square(5) = " << square(5) << endl;
    cout << "square(10) = " << square(10) << endl;
    cout << "（内联函数在编译时展开，没有函数调用开销）" << endl;


    // ---------- 安全小贴士 ----------
    cout << "\n========== 安全小贴士 ==========" << endl;
    cout << "1. 递归深度过大会导致栈溢出（Stack Overflow）。" << endl;
    cout << "2. 函数调用约定（cdecl、stdcall、fastcall）在逆向分析中很重要。" << endl;
    cout << "3. 栈帧结构（返回地址、局部变量、EBP）是缓冲区溢出利用的基础。" << endl;
    cout << "4. 函数指针在漏洞利用（如覆盖虚表）中经常用到。" << endl;

    return 0;
}
