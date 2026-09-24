// ============================================================
// 05_pointers.c —— 指针的基本概念与使用
// 编译命令：gcc 05_pointers.c -o 05_pointers
// ============================================================

#include <stdio.h>
#include <stdlib.h>

int main() {
    // ---------- 1. 指针基础 ----------
    printf("========== 指针基础 ==========\n");

    int x = 42;
    int *p;      // 声明一个指向 int 的指针变量
    p = &x;      // 将 x 的地址赋给 p

    printf("x 的值 = %d\n", x);
    printf("x 的地址 = %p\n", (void *)&x);
    printf("p 的值（指向的地址） = %p\n", (void *)p);
    printf("*p 的值（解引用） = %d\n", *p);

    // 通过指针修改值
    *p = 100;
    printf("\n通过 *p = 100 修改后：\n");
    printf("x 的值 = %d\n", x);
    printf("*p 的值 = %d\n", *p);


    // ---------- 2. 指针的大小与类型 ----------
    printf("\n========== 指针的大小与类型 ==========\n");

    printf("int* 指针大小 = %zu 字节\n", sizeof(int *));
    printf("char* 指针大小 = %zu 字节\n", sizeof(char *));
    printf("double* 指针大小 = %zu 字节\n", sizeof(double *));
    printf("void* 指针大小 = %zu 字节\n", sizeof(void *));
    printf("（所有指针大小相同，因为都是存储内存地址）\n");


    // ---------- 3. 指针与数组 ----------
    printf("\n========== 指针与数组 ==========\n");

    int arr[5] = {10, 20, 30, 40, 50};
    int *ptr = arr;  // 数组名是指向数组首元素的指针

    printf("数组首地址 = %p\n", (void *)arr);
    printf("ptr 的值 = %p\n", (void *)ptr);

    // 使用指针访问数组元素
    printf("\n使用指针遍历数组：\n");
    for (int i = 0; i < 5; i++) {
        printf("arr[%d] = %d, *(ptr + %d) = %d\n", i, arr[i], i, *(ptr + i));
    }

    // 指针运算
    printf("\n指针运算：\n");
    printf("ptr = %p\n", (void *)ptr);
    printf("ptr + 1 = %p (增加了 %zu 字节)\n", (void *)(ptr + 1), sizeof(int));
    printf("ptr + 2 = %p (增加了 %zu 字节)\n", (void *)(ptr + 2), 2 * sizeof(int));

    // 使用指针遍历（指针自增）
    printf("\n使用指针自增遍历：");
    int *p_arr = arr;
    for (int i = 0; i < 5; i++) {
        printf("%d ", *p_arr);
        p_arr++;  // 指针移动到下一个元素
    }
    printf("\n");


    // ---------- 4. 指针与字符串 ----------
    printf("\n========== 指针与字符串 ==========\n");

    char *str = "Hello, World!";
    printf("字符串 = %s\n", str);
    printf("首字符 = %c\n", *str);
    printf("第 7 个字符 = %c\n", *(str + 7));

    // 用指针遍历字符串
    printf("用指针遍历字符串：");
    char *p_str = str;
    while (*p_str != '\0') {  // 直到遇到字符串结束符
        printf("%c", *p_str);
        p_str++;
    }
    printf("\n");


    // ---------- 5. 二级指针（指向指针的指针） ----------
    printf("\n========== 二级指针 ==========\n");

    int value = 123;
    int *p1 = &value;     // 一级指针，指向 int
    int **p2 = &p1;       // 二级指针，指向 int*

    printf("value = %d\n", value);
    printf("&value = %p\n", (void *)&value);
    printf("p1 = %p\n", (void *)p1);
    printf("&p1 = %p\n", (void *)&p1);
    printf("p2 = %p\n", (void *)p2);
    printf("*p2 = %p\n", (void *)*p2);
    printf("**p2 = %d\n", **p2);

    // 通过二级指针修改值
    **p2 = 999;
    printf("通过 **p2 = 999 修改后，value = %d\n", value);


    // ---------- 6. 指针数组与数组指针 ----------
    printf("\n========== 指针数组 ==========\n");

    // 指针数组：数组的每个元素都是指针
    char *names[4] = {
        "Alice",
        "Bob",
        "Charlie",
        "David"
    };

    for (int i = 0; i < 4; i++) {
        printf("names[%d] = %s\n", i, names[i]);
    }

    // 数组指针：指向数组的指针
    printf("\n========== 数组指针 ==========\n");
    int arr2d[2][3] = {{1, 2, 3}, {4, 5, 6}};
    int (*p_arr2d)[3] = arr2d;  // 指向包含 3 个 int 的数组的指针

    printf("arr2d[0][0] = %d\n", p_arr2d[0][0]);
    printf("arr2d[1][2] = %d\n", p_arr2d[1][2]);


    // ---------- 7. 空指针与野指针 ----------
    printf("\n========== 空指针与野指针 ==========\n");

    // 空指针：不指向任何有效地址的指针
    int *null_ptr = NULL;
    printf("空指针的值 = %p\n", (void *)null_ptr);

    // 解引用空指针会导致程序崩溃（段错误）
    // printf("%d", *null_ptr);  // 错误！

    // 使用指针前应该检查是否为 NULL
    if (null_ptr != NULL) {
        printf("指针有效\n");
    } else {
        printf("指针为空，不能解引用\n");
    }

    // 野指针：指向未知内存的指针（未初始化或已释放）
    int *wild_ptr;  // 未初始化，值是随机的（野指针）
    // printf("%d", *wild_ptr);  // 危险！行为未定义


    // ---------- 8. 指针作为函数参数 ----------
    printf("\n========== 指针作为函数参数 ==========\n");

    void swap(int *a, int *b);  // 函数声明

    int a = 10, b = 20;
    printf("交换前: a = %d, b = %d\n", a, b);
    swap(&a, &b);
    printf("交换后: a = %d, b = %d\n", a, b);


    // ---------- 安全小贴士 ----------
    printf("\n========== 安全小贴士 ==========\n");
    printf("1. 使用指针前一定要检查是否为 NULL\n");
    printf("2. 避免野指针：声明时初始化，释放后置 NULL\n");
    printf("3. 指针越界访问是缓冲区溢出的常见原因\n");
    printf("4. 空指针解引用会导致程序崩溃（DoS）\n");
    printf("5. 函数指针如果被恶意篡改，可能导致代码执行\n");

    return 0;
}

// 交换两个整数的值（通过指针传递）
void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}
