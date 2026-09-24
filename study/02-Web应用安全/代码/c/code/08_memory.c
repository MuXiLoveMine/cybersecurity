// ============================================================
// 08_memory.c —— 内存管理（malloc, calloc, realloc, free）
// 编译命令：gcc 08_memory.c -o 08_memory
// ============================================================

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    // ---------- 1. 内存分区 ----------
    printf("========== 内存分区 ==========\n");

    // 栈区（Stack）：局部变量，由系统自动分配和释放
    int stack_var = 100;
    char stack_arr[100] = "栈上的数组";

    // 堆区（Heap）：动态分配，需要手动 malloc/free
    int *heap_var = (int *)malloc(sizeof(int));
    *heap_var = 200;

    // 全局/静态区：全局变量和静态变量
    static int static_var = 300;

    // 常量区：字符串常量等
    char *const_str = "常量字符串";

    // 代码区：存放程序代码

    printf("栈变量地址：%p，值：%d\n", (void *)&stack_var, stack_var);
    printf("堆变量地址：%p，值：%d\n", (void *)heap_var, *heap_var);
    printf("静态变量地址：%p，值：%d\n", (void *)&static_var, static_var);
    printf("常量区地址：%p，值：%s\n", (void *)const_str, const_str);
    printf("栈数组地址：%p\n", (void *)stack_arr);

    free(heap_var);  // 释放堆内存
    heap_var = NULL;


    // ---------- 2. malloc 动态分配 ----------
    printf("\n========== malloc 动态分配 ==========\n");

    // 分配一个 int
    int *p = (int *)malloc(sizeof(int));
    if (p == NULL) {
        printf("内存分配失败！\n");
        return 1;
    }

    *p = 42;
    printf("分配的 int 值：%d\n", *p);
    printf("地址：%p\n", (void *)p);

    free(p);   // 释放内存
    p = NULL;  // 置空，避免野指针


    // ---------- 3. malloc 分配数组 ----------
    printf("\n========== malloc 分配数组 ==========\n");

    int n = 5;
    int *arr = (int *)malloc(n * sizeof(int));
    if (arr == NULL) {
        printf("内存分配失败！\n");
        return 1;
    }

    // 使用分配的内存
    for (int i = 0; i < n; i++) {
        arr[i] = (i + 1) * 10;
    }

    printf("动态数组内容：");
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");

    free(arr);
    arr = NULL;


    // ---------- 4. calloc 初始化为0 ----------
    printf("\n========== calloc 初始化为0 ==========\n");

    // calloc 会将分配的内存初始化为 0
    int *arr2 = (int *)calloc(5, sizeof(int));
    if (arr2 != NULL) {
        printf("calloc 分配的数组（已初始化为0）：");
        for (int i = 0; i < 5; i++) {
            printf("%d ", arr2[i]);
        }
        printf("\n");
        free(arr2);
        arr2 = NULL;
    }


    // ---------- 5. realloc 重新分配 ----------
    printf("\n========== realloc 重新分配 ==========\n");

    int *dyn_arr = (int *)malloc(3 * sizeof(int));
    if (dyn_arr == NULL) return 1;

    dyn_arr[0] = 10;
    dyn_arr[1] = 20;
    dyn_arr[2] = 30;

    printf("原始数组（3个元素）：%d %d %d\n", dyn_arr[0], dyn_arr[1], dyn_arr[2]);

    // 扩容到 6 个元素
    int *temp = (int *)realloc(dyn_arr, 6 * sizeof(int));
    if (temp == NULL) {
        printf("realloc 失败\n");
        free(dyn_arr);
        return 1;
    }
    dyn_arr = temp;  // 重新赋值

    // 新增元素
    dyn_arr[3] = 40;
    dyn_arr[4] = 50;
    dyn_arr[5] = 60;

    printf("扩容后（6个元素）：");
    for (int i = 0; i < 6; i++) {
        printf("%d ", dyn_arr[i]);
    }
    printf("\n");

    // 缩容到 2 个元素
    dyn_arr = (int *)realloc(dyn_arr, 2 * sizeof(int));
    printf("缩容后（2个元素）：%d %d\n", dyn_arr[0], dyn_arr[1]);

    free(dyn_arr);
    dyn_arr = NULL;


    // ---------- 6. 内存操作函数 ----------
    printf("\n========== 内存操作函数 ==========\n");

    char src[50] = "Hello, Memory!";
    char dest[50];

    // memcpy - 内存拷贝
    memcpy(dest, src, strlen(src) + 1);  // +1 包含 '\0'
    printf("memcpy 结果：%s\n", dest);

    // memmove - 内存移动（可处理重叠区域）
    char overlap[] = "abcdefghij";
    printf("memmove 前：%s\n", overlap);
    memmove(overlap + 2, overlap, 5);  // 重叠拷贝
    printf("memmove 后：%s\n", overlap);

    // memset - 内存设置
    char buf[20];
    memset(buf, 'A', 10);  // 将前 10 字节设为 'A'
    buf[10] = '\0';
    printf("memset 结果：%s\n", buf);

    // memset 也常用于清零
    int nums[5];
    memset(nums, 0, sizeof(nums));
    printf("memset 清零：");
    for (int i = 0; i < 5; i++) {
        printf("%d ", nums[i]);
    }
    printf("\n");

    // memcmp - 内存比较
    char str1[] = "abcde";
    char str2[] = "abxde";
    int cmp = memcmp(str1, str2, 5);
    printf("memcmp 结果：%d\n", cmp);

    // memchr - 内存查找字符
    char *found = memchr(src, 'M', strlen(src));
    if (found != NULL) {
        printf("memchr 找到 'M'：%s\n", found);
    }


    // ---------- 7. 常见内存错误 ----------
    printf("\n========== 常见内存错误 ==========\n");

    printf("1. 内存泄漏：只 malloc 不 free\n");
    printf("2. 重复释放：对同一块内存 free 两次\n");
    printf("3. 野指针：指针未初始化或已释放后仍使用\n");
    printf("4. 空指针解引用：对 NULL 指针进行 * 操作\n");
    printf("5. 越界访问：访问分配内存以外的区域\n");
    printf("6. 使用已释放的内存（Use-After-Free）\n");


    // ---------- 8. 内存安全编程实践 ----------
    printf("\n========== 内存安全编程实践 ==========\n");

    // 1. 分配后检查是否为 NULL
    int *safe_ptr = (int *)malloc(sizeof(int) * 10);
    if (safe_ptr == NULL) {
        printf("内存分配失败，程序退出\n");
        return 1;
    }

    // 2. 初始化内存
    memset(safe_ptr, 0, sizeof(int) * 10);

    // 3. 使用时注意边界
    for (int i = 0; i < 10; i++) {
        safe_ptr[i] = i;
    }

    // 4. 释放后置 NULL
    free(safe_ptr);
    safe_ptr = NULL;

    // 5. 不使用已释放的指针
    // printf("%d", safe_ptr[0]);  // 错误！Use-After-Free

    printf("安全编程实践完成\n");


    // ---------- 安全小贴士 ----------
    printf("\n========== 安全小贴士 ==========\n");
    printf("1. 内存泄漏会导致程序占用内存持续增长\n");
    printf("2. Use-After-Free 是常见的漏洞利用方式\n");
    printf("3. 缓冲区溢出可导致代码执行（栈溢出、堆溢出）\n");
    printf("4. 使用工具检测内存问题：valgrind、AddressSanitizer\n");
    printf("5. 释放后置 NULL 是良好的编程习惯\n");

    return 0;
}
