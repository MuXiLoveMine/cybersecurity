// ============================================================
// 03_functions.c —— 函数的定义、声明、参数传递、递归
// 编译命令：gcc 03_functions.c -o 03_functions
// ============================================================

#include <stdio.h>
#include <stdlib.h>

// ---------- 函数声明（函数原型） ----------
// 在使用函数之前需要声明，告诉编译器函数的存在
int add(int a, int b);                    // 两个整数相加
void print_hello(void);                   // 无参数、无返回值
int max(int x, int y);                    // 求两个数的最大值
void swap(int *a, int *b);                // 通过指针交换变量值
int factorial(int n);                     // 递归计算阶乘
int sum_array(int arr[], int size);       // 数组求和
void print_info(char *name, int age);     // 打印信息


// ---------- 主函数 ----------
int main() {
    printf("========== 函数基础 ==========\n");

    // 调用无参函数
    print_hello();

    // 调用有返回值函数
    int result = add(3, 5);
    printf("3 + 5 = %d\n", result);
    printf("10 + 20 = %d\n", add(10, 20));

    // 求最大值
    printf("max(10, 20) = %d\n", max(10, 20));
    printf("max(100, 50) = %d\n", max(100, 50));


    // ---------- 2. 参数传递 ----------
    printf("\n========== 参数传递 ==========\n");

    // 值传递：函数内部修改不影响外部
    int x = 10, y = 20;
    printf("值传递示例：\n");
    printf("调用前: x = %d, y = %d\n", x, y);
    // 这是一个值传递的 swap 版本（不会真正交换）
    int temp = x; x = y; y = temp;  // 这里直接交换，只是为了演示
    printf("直接交换后: x = %d, y = %d\n", x, y);

    // 地址传递（指针）：函数内部可以修改外部变量
    int a = 100, b = 200;
    printf("\n地址传递（指针）示例：\n");
    printf("调用 swap 前: a = %d, b = %d\n", a, b);
    swap(&a, &b);  // 传入变量地址
    printf("调用 swap 后: a = %d, b = %d\n", a, b);


    // ---------- 3. 数组作为函数参数 ----------
    printf("\n========== 数组作为函数参数 ==========\n");

    int numbers[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    int len = sizeof(numbers) / sizeof(numbers[0]);
    int total = sum_array(numbers, len);
    printf("数组元素之和 = %d\n", total);


    // ---------- 4. 递归函数 ----------
    printf("\n========== 递归函数 ==========\n");

    int n = 5;
    printf("%d! = %d\n", n, factorial(n));
    printf("10! = %d\n", factorial(10));

    // 递归的原理：函数自己调用自己，直到满足终止条件
    // 5! = 5 * 4!
    // 4! = 4 * 3!
    // 3! = 3 * 2!
    // 2! = 2 * 1!
    // 1! = 1  （终止条件）


    // ---------- 5. 函数指针 ----------
    printf("\n========== 函数指针 ==========\n");

    // 函数指针：指向函数的指针
    int (*func_ptr)(int, int);  // 声明一个函数指针，指向返回 int、参数为两个 int 的函数

    func_ptr = add;  // 指向 add 函数
    printf("通过函数指针调用 add(3, 4) = %d\n", func_ptr(3, 4));

    func_ptr = max;  // 指向 max 函数
    printf("通过函数指针调用 max(3, 4) = %d\n", func_ptr(3, 4));


    // ---------- 6. 作用域与存储类别 ----------
    printf("\n========== 作用域与存储类别 ==========\n");

    // 局部变量：函数内部定义，只在函数内有效
    // 全局变量：函数外部定义，整个程序都可以访问
    // static 静态变量：保留上一次调用的值

    void test_static(void);  // 函数声明
    test_static();  // count = 1
    test_static();  // count = 2
    test_static();  // count = 3


    // ---------- 安全小贴士 ----------
    printf("\n========== 安全小贴士 ==========\n");
    printf("1. 函数参数要做合法性校验，防止无效输入导致异常\n");
    printf("2. 递归函数要确保有终止条件，防止栈溢出\n");
    printf("3. 指针参数使用前要检查是否为 NULL\n");
    printf("4. 函数指针可用于实现回调，但也可能被利用进行攻击\n");

    return 0;
}


// ---------- 函数定义 ----------

// 无返回值函数
void print_hello(void) {
    printf("Hello from print_hello function!\n");
}

// 有返回值函数
int add(int a, int b) {
    return a + b;
}

// 求最大值
int max(int x, int y) {
    if (x > y) {
        return x;
    } else {
        return y;
    }
}

// 通过指针交换两个变量的值（地址传递）
void swap(int *a, int *b) {
    int temp = *a;  // 取 a 指向的值
    *a = *b;        // 将 b 指向的值赋给 a 指向的位置
    *b = temp;      // 将原值赋给 b 指向的位置
}

// 递归计算阶乘
int factorial(int n) {
    if (n <= 1) {
        return 1;  // 终止条件（基线条件）
    }
    return n * factorial(n - 1);  // 递归调用
}

// 数组求和（数组作为参数会退化为指针）
int sum_array(int arr[], int size) {
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += arr[i];
    }
    return sum;
}

// 打印信息
void print_info(char *name, int age) {
    printf("姓名: %s, 年龄: %d\n", name, age);
}

// 静态变量示例
void test_static(void) {
    static int count = 0;  // 静态局部变量，只初始化一次，保留上次的值
    count++;
    printf("  test_static 被调用第 %d 次\n", count);
}
