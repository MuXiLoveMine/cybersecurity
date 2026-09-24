// ============================================================
// 04_array_string.c —— 数组与字符串
// 编译命令：gcc 04_array_string.c -o 04_array_string
// ============================================================

#include <stdio.h>
#include <string.h>   // 字符串处理函数头文件
#include <stdlib.h>

int main() {
    // ---------- 1. 一维数组 ----------
    printf("========== 一维数组 ==========\n");

    // 声明并初始化数组
    int nums[5] = {10, 20, 30, 40, 50};

    // 访问数组元素（下标从 0 开始）
    printf("nums[0] = %d\n", nums[0]);
    printf("nums[2] = %d\n", nums[2]);

    // 修改数组元素
    nums[3] = 100;
    printf("修改后 nums[3] = %d\n", nums[3]);

    // 遍历数组
    printf("数组全部元素：");
    for (int i = 0; i < 5; i++) {
        printf("%d ", nums[i]);
    }
    printf("\n");

    // 数组大小
    int arr[] = {1, 2, 3, 4, 5, 6, 7};
    int len = sizeof(arr) / sizeof(arr[0]);
    printf("数组长度 = %d\n", len);

    // 数组初始化的几种方式
    int a[5] = {1, 2, 3};       // 部分初始化，剩余元素为 0
    int b[5] = {0};             // 全部初始化为 0
    int c[] = {1, 2, 3, 4};     // 由初始化列表确定大小


    // ---------- 2. 二维数组 ----------
    printf("\n========== 二维数组 ==========\n");

    // 声明并初始化二维数组
    int matrix[3][4] = {
        {1, 2, 3, 4},
        {5, 6, 7, 8},
        {9, 10, 11, 12}
    };

    // 遍历二维数组
    printf("3x4 矩阵：\n");
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 4; j++) {
            printf("%3d ", matrix[i][j]);
        }
        printf("\n");
    }

    // 二维数组在内存中是连续存储的（行优先）
    printf("\n二维数组首地址 = %p\n", (void *)matrix);
    printf("matrix[0] 地址 = %p\n", (void *)matrix[0]);
    printf("matrix[1] 地址 = %p\n", (void *)matrix[1]);


    // ---------- 3. 字符数组与字符串 ----------
    printf("\n========== 字符数组与字符串 ==========\n");

    // C 语言中字符串是以 '\0' 结尾的字符数组
    char str1[20] = "Hello";           // 自动添加 '\0'
    char str2[] = "World";              // 由编译器确定大小
    char str3[] = {'H', 'i', '\0'};     // 手动添加 '\0'

    printf("str1 = %s\n", str1);
    printf("str2 = %s\n", str2);
    printf("str3 = %s\n", str3);

    // 字符串长度（不包含 '\0'）
    printf("str1 长度 = %zu\n", strlen(str1));
    printf("str1 占用字节数 = %zu\n", sizeof(str1));


    // ---------- 4. 字符串常用函数 ----------
    printf("\n========== 字符串常用函数 ==========\n");

    char s1[50] = "Hello ";
    char s2[] = "World";
    char s3[50];

    // strcpy - 字符串复制
    strcpy(s3, s1);
    printf("strcpy(s3, s1) 后 s3 = %s\n", s3);

    // strcat - 字符串拼接
    strcat(s1, s2);
    printf("strcat(s1, s2) 后 s1 = %s\n", s1);

    // strlen - 字符串长度
    printf("s1 长度 = %zu\n", strlen(s1));

    // strcmp - 字符串比较
    int cmp = strcmp("abc", "abc");
    printf("strcmp(\"abc\", \"abc\") = %d\n", cmp);  // 0 表示相等
    printf("strcmp(\"abc\", \"abd\") = %d\n", strcmp("abc", "abd"));  // < 0
    printf("strcmp(\"abd\", \"abc\") = %d\n", strcmp("abd", "abc"));  // > 0

    // strchr - 查找字符
    char *pos = strchr("Hello World", 'W');
    if (pos != NULL) {
        printf("strchr 找到 'W'，位置：%s\n", pos);
    }

    // strstr - 查找子串
    char *sub = strstr("Hello World", "World");
    if (sub != NULL) {
        printf("strstr 找到 \"World\"，位置：%s\n", sub);
    }


    // ---------- 5. 字符串输入输出 ----------
    printf("\n========== 字符串输入输出 ==========\n");

    char name[50];
    printf("请输入你的名字（不含空格）：");
    scanf("%s", name);                    // 遇到空格或换行结束
    printf("你好，%s！\n", name);

    // gets 函数（不安全，不推荐使用，可能导致缓冲区溢出）
    // gets(name);  // 不推荐！

    // fgets - 安全的字符串读取
    char line[100];
    printf("请输入一行文本：");
    getchar();  // 吸收上一个 scanf 留下的换行符
    fgets(line, sizeof(line), stdin);     // 安全，可以读取空格
    printf("你输入的是：%s", line);


    // ---------- 6. 字符数组与指针 ----------
    printf("\n========== 字符数组与字符指针的区别 ==========\n");

    char arr_str[] = "Hello";   // 字符数组，内容可修改
    char *ptr_str = "Hello";    // 字符指针，指向字符串常量（只读）

    printf("字符数组: %s\n", arr_str);
    printf("字符指针: %s\n", ptr_str);

    arr_str[0] = 'h';  // 可以修改
    printf("修改后数组: %s\n", arr_str);

    // ptr_str[0] = 'h';  // 错误！字符串常量不可修改，会导致段错误

    printf("数组地址: %p\n", (void *)arr_str);
    printf("指针指向: %p\n", (void *)ptr_str);


    // ---------- 安全小贴士 ----------
    printf("\n========== 安全小贴士 ==========\n");
    printf("1. 永远不要使用 gets() 函数，它没有边界检查，会导致缓冲区溢出\n");
    printf("2. 使用 strcpy、strcat 时要确保目标缓冲区足够大\n");
    printf("3. 推荐使用 strncpy、strncat 等带长度限制的函数\n");
    printf("4. 字符串常量存储在只读内存区，修改会导致程序崩溃\n");
    printf("5. 缓冲区溢出是 C 语言最常见的安全漏洞之一\n");

    return 0;
}
