// basics.cpp —— C/C++ 基础语法示例（安全从业者视角）
//
// 涵盖内容：
//   1. 基本数据类型与大小
//   2. 指针与地址
//   3. 数组与字符串
//   4. 函数
//   5. 结构体、联合体、枚举
//   6. 动态内存分配
//   7. 文件操作
//   8. C++ STL 简介
//   9. 内存布局理解
//
// 编译方式：
//   g++ -o basics basics.cpp
//   或: gcc -lstdc++ -o basics basics.cpp
//
// 注意：本脚本用于学习参考，可以直接编译运行。

#include <iostream>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <memory>  // 智能指针

using namespace std;

// ============================================================
// 辅助函数
// ============================================================

void printSection(const char *title) {
    cout << endl;
    cout << "============================================================" << endl;
    cout << "  " << title << endl;
    cout << "============================================================" << endl;
    cout << endl;
}

void printSubsection(const char *title) {
    cout << endl;
    cout << "  --- " << title << " ---" << endl;
    cout << endl;
}

// ============================================================
// 1. 基本数据类型
// ============================================================

void demoDataTypes() {
    printSection("【1. 基本数据类型与大小】");

    printSubsection("1.1 基本类型大小（当前平台）");

    printf("  char:          %zu 字节\n", sizeof(char));
    printf("  short:         %zu 字节\n", sizeof(short));
    printf("  int:           %zu 字节\n", sizeof(int));
    printf("  long:          %zu 字节\n", sizeof(long));
    printf("  long long:     %zu 字节\n", sizeof(long long));
    printf("  float:         %zu 字节\n", sizeof(float));
    printf("  double:        %zu 字节\n", sizeof(double));
    printf("  void* (指针):  %zu 字节\n", sizeof(void*));

    int bits = sizeof(void*) * 8;
    printf("\n  当前平台: %d 位\n", bits);
    printf("  地址空间: 2^%d = %zu GB (理论)\n", bits,
           (size_t)(1ULL << (bits > 32 ? 36 : 30)));
    // 注：实际可用地址空间远小于理论值（用户态只占一部分）

    printSubsection("1.2 有符号与无符号");

    int signed_val = -1;
    unsigned int unsigned_val = (unsigned int)signed_val;

    printf("  int -1 的值:            %d\n", signed_val);
    printf("  转成 unsigned int 后:   %u\n", unsigned_val);
    printf("  (十六进制: 0x%08x)\n", unsigned_val);
    printf("\n");
    printf("  💡 有符号数负数的无符号表示是很大的正数\n");
    printf("     这是整数溢出/类型混淆漏洞的常见原因\n");

    printSubsection("1.3 字符与字节");

    char ch = 'A';
    printf("  字符 '%c' 的 ASCII 值: %d (0x%02x)\n", ch, ch, ch);

    unsigned char byte = 0xFF;
    printf("  字节 0xFF 的无符号值: %u\n", byte);
    printf("  字节 0xFF 的有符号值: %d (char 默认可能有符号)\n", (char)byte);
    printf("\n");
    printf("  💡 char 的符号性取决于编译器\n");
    printf("     处理二进制数据时建议显式用 unsigned char\n");
}

// ============================================================
// 2. 指针
// ============================================================

void demoPointers() {
    printSection("【2. 指针与地址】");

    printSubsection("2.1 指针基础");

    int x = 42;
    int *p = &x;

    printf("  变量 x 的值: %d\n", x);
    printf("  变量 x 的地址: %p\n", (void*)&x);
    printf("  指针 p 的值:   %p\n", (void*)p);
    printf("  指针 p 指向的值: %d\n", *p);
    printf("\n");

    // 通过指针修改
    *p = 100;
    printf("  通过 *p = 100 修改后，x = %d\n", x);

    printSubsection("2.2 指针算术");

    int arr[] = {10, 20, 30, 40, 50};
    int *ap = arr;

    printf("  数组起始地址: %p\n", (void*)arr);
    printf("  arr[0] = %d  (地址: %p)\n", *ap, (void*)ap);
    printf("  arr[1] = %d  (地址: %p)\n", *(ap + 1), (void*)(ap + 1));
    printf("  arr[2] = %d  (地址: %p)\n", ap[2], (void*)(ap + 2));
    printf("\n");
    printf("  💡 指针 +1 前进的字节数 = 指向类型的大小\n");
    printf("     int* +1 前进 %zu 字节，char* +1 前进 %zu 字节\n",
           sizeof(int), sizeof(char));

    printSubsection("2.3 多级指针");

    int val = 42;
    int *p1 = &val;
    int **p2 = &p1;

    printf("  val = %d, 地址: %p\n", val, (void*)&val);
    printf("  p1 = %p, *p1 = %d\n", (void*)p1, *p1);
    printf("  p2 = %p, *p2 = %p, **p2 = %d\n",
           (void*)p2, (void*)*p2, **p2);
    printf("\n");
    printf("  💡 二级指针在二维数组、链表、函数修改指针时常用\n");

    printSubsection("2.4 空指针");

    int *np = NULL;  // 或 nullptr (C++11+)
    printf("  NULL 指针的值: %p\n", (void*)np);
    printf("  访问空指针会导致段错误 (Segmentation Fault)\n");
    printf("  💡 好的实践：malloc/new 后检查是否为 NULL\n");
    printf("          释放内存后置指针为 NULL，防止野指针\n");
}

// ============================================================
// 3. 数组与字符串
// ============================================================

void demoArraysAndStrings() {
    printSection("【3. 数组与字符串】");

    printSubsection("3.1 数组基础");

    int nums[5] = {1, 2, 3, 4, 5};

    printf("  数组大小: %zu 字节\n", sizeof(nums));
    printf("  元素个数: %zu\n", sizeof(nums) / sizeof(nums[0]));
    printf("  数组名 = 首元素地址: %p = %p\n",
           (void*)nums, (void*)&nums[0]);

    printf("\n  数组元素:\n");
    for (int i = 0; i < 5; i++) {
        printf("    nums[%d] = %d (地址: %p)\n",
               i, nums[i], (void*)&nums[i]);
    }

    printf("\n  💡 arr[i] 等价于 *(arr + i)\n");
    printf("     甚至 i[arr] 也是合法的（但不要这么写）\n");

    printSubsection("3.2 字符串（C 风格）");

    char str1[] = "Hello";  // 自动加 '\0'
    // 内存: H e l l o \0  (共 6 字节)

    printf("  字符串: \"%s\"\n", str1);
    printf("  sizeof: %zu 字节 (包含 '\\0')\n", sizeof(str1));
    printf("  strlen: %zu 字符 (不包含 '\\0')\n", strlen(str1));

    char str2[20] = "Hello";
    strcat(str2, " World");  // 字符串拼接
    printf("\n  strcat 后: \"%s\"\n", str2);
    printf("  长度: %zu\n", strlen(str2));

    // 字符串比较
    printf("\n  strcmp(\"abc\", \"abc\") = %d (相等)\n", strcmp("abc", "abc"));
    printf("  strcmp(\"abc\", \"abd\") = %d (小于)\n", strcmp("abc", "abd"));

    printSubsection("3.3 危险 vs 安全的字符串函数");

    printf("  ⚠️  危险函数（容易溢出）:   安全替代:\n");
    printf("    gets()                     fgets()\n");
    printf("    strcpy()                   strncpy()\n");
    printf("    strcat()                   strncat()\n");
    printf("    sprintf()                  snprintf()\n");
    printf("\n");
    printf("  💡 永远检查目标缓冲区大小！\n");
    printf("     缓冲区溢出是最经典的内存安全漏洞\n");

    printSubsection("3.4 C++ string（更安全）");

    string s = "Hello, C++ String";
    s += " - 自动管理内存";
    cout << "  string 内容: " << s << endl;
    cout << "  string 长度: " << s.size() << endl;
    cout << "  string 容量: " << s.capacity() << endl;
    cout << endl;
    cout << "  💡 std::string 自动管理内存，不用担心缓冲区溢出" << endl;
    cout << "     但 .c_str() 返回的指针在 string 失效后也会失效" << endl;
}

// ============================================================
// 4. 函数
// ============================================================

// 传值
int add(int a, int b) {
    return a + b;
}

// 传指针（可以修改原变量）
void swapByPointer(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

// 传引用（C++，可以修改原变量，语法更简洁）
void swapByReference(int &a, int &b) {
    int temp = a;
    a = b;
    b = temp;
}

// 函数指针
int multiply(int a, int b) {
    return a * b;
}

void demoFunctions() {
    printSection("【4. 函数】");

    printSubsection("4.1 传值 vs 传指针 vs 传引用");

    int a = 10, b = 20;
    printf("  初始: a = %d, b = %d\n", a, b);

    swapByPointer(&a, &b);
    printf("  传指针交换后: a = %d, b = %d\n", a, b);

    swapByReference(a, b);
    printf("  传引用交换后: a = %d, b = %d\n", a, b);

    printf("\n");
    printf("  💡 传值: 拷贝一份，不影响原变量\n");
    printf("     传指针: 传地址，通过解引用修改原变量\n");
    printf("     传引用: C++ 特性，别名，直接修改原变量\n");

    printSubsection("4.2 函数指针");

    int (*funcPtr)(int, int) = multiply;  // 函数指针
    printf("  函数指针 multiply(3, 4) = %d\n", funcPtr(3, 4));
    printf("\n");
    printf("  💡 函数指针可用于回调、虚表等\n");
    printf("     vtable 覆盖就是修改函数指针\n");

    printSubsection("4.3 栈帧理解（概念演示）");

    printf("  函数调用栈帧结构（简化）:\n");
    printf("    高地址 ...\n");
    printf("    ┌─────────────────────┐\n");
    printf("    │ 调用者栈帧           │\n");
    printf("    ├─────────────────────┤\n");
    printf("    │ 返回地址 (return IP) │ ← 被覆盖就可以控制执行流\n");
    printf("    ├─────────────────────┤\n");
    printf("    │ 保存的 EBP/RBP      │\n");
    printf("    ├─────────────────────┤\n");
    printf("    │ 局部变量 buffer      │ ← 溢出从这里开始\n");
    printf("    │ ...                 │\n");
    printf("    └─────────────────────┘ ← ESP/RSP\n");
    printf("    低地址 ...\n");
    printf("\n");
    printf("  💡 栈溢出原理：覆盖局部变量后面的返回地址\n");
    printf("     防护机制：Stack Canary、DEP/NX、ASLR、CFI\n");
}

// ============================================================
// 5. 结构体、联合体、枚举
// ============================================================

// 结构体
struct User {
    char username[50];
    char email[100];
    int age;
    int is_active;
};

// 联合体（所有成员共用内存）
union Data {
    int i;
    float f;
    unsigned char bytes[4];
};

// 枚举
enum Role {
    ROLE_USER = 0,
    ROLE_EDITOR = 1,
    ROLE_ADMIN = 2
};

void demoStructsAndUnions() {
    printSection("【5. 结构体、联合体、枚举】");

    printSubsection("5.1 结构体");

    struct User alice;
    strncpy(alice.username, "alice", sizeof(alice.username) - 1);
    strncpy(alice.email, "alice@example.com", sizeof(alice.email) - 1);
    alice.age = 25;
    alice.is_active = 1;

    printf("  结构体大小: %zu 字节\n", sizeof(struct User));
    printf("  username 偏移: %zu 字节\n", offsetof(struct User, username));
    printf("  email 偏移:    %zu 字节\n", offsetof(struct User, email));
    printf("  age 偏移:      %zu 字节\n", offsetof(struct User, age));
    printf("  is_active 偏移: %zu 字节\n", offsetof(struct User, is_active));
    printf("\n");

    struct User *p = &alice;
    printf("  通过指针访问: p->username = %s\n", p->username);
    printf("  成员年龄: %d\n", p->age);

    printf("\n  💡 结构体大小不一定等于各成员大小之和\n");
    printf("     编译器会进行内存对齐（为了访问效率）\n");
    printf("     理解内存对齐对漏洞利用（堆风水等）很重要\n");

    printSubsection("5.2 联合体（union）");

    union Data d;
    d.i = 0x41424344;  // 十六进制: A B C D

    printf("  联合体大小: %zu 字节\n", sizeof(union Data));
    printf("  d.i = 0x%08x\n", d.i);
    printf("  d.f = %f (解释为 float)\n", d.f);
    printf("  d.bytes: ");
    for (int i = 0; i < 4; i++) {
        printf("0x%02x ", d.bytes[i]);
    }
    printf("\n");
    printf("  (小端序：低字节在低地址)\n");
    printf("\n");
    printf("  💡 联合体所有成员共用同一块内存\n");
    printf("     可以用来查看内存布局，也可能导致类型混淆漏洞\n");

    printSubsection("5.3 枚举");

    enum Role role = ROLE_ADMIN;
    printf("  角色值: %d\n", role);
    printf("  ROLE_USER = %d, ROLE_EDITOR = %d, ROLE_ADMIN = %d\n",
           ROLE_USER, ROLE_EDITOR, ROLE_ADMIN);
}

// ============================================================
// 6. 动态内存分配
// ============================================================

void demoDynamicMemory() {
    printSection("【6. 动态内存分配】");

    printSubsection("6.1 C 风格：malloc / free");

    int *arr1 = (int*)malloc(5 * sizeof(int));
    if (arr1 == NULL) {
        printf("  内存分配失败！\n");
        return;
    }

    // 初始化
    for (int i = 0; i < 5; i++) {
        arr1[i] = i * 10;
    }

    printf("  malloc 分配的数组: ");
    for (int i = 0; i < 5; i++) {
        printf("%d ", arr1[i]);
    }
    printf("\n");

    // realloc 扩容
    int *arr2 = (int*)realloc(arr1, 10 * sizeof(int));
    if (arr2 == NULL) {
        printf("  realloc 失败！\n");
        free(arr1);  // 失败了原指针还需要释放
        return;
    }
    arr1 = arr2;  // 更新指针

    printf("  realloc 后容量: 10 个 int\n");

    free(arr1);  // 释放内存
    arr1 = NULL;  // 好的实践：释放后置空
    printf("  内存已释放\n");

    printSubsection("6.2 C++ 风格：new / delete");

    int *p1 = new int(42);       // 单个 int，初始化为 42
    printf("  new int: %d\n", *p1);
    delete p1;

    int *arr3 = new int[5];      // 数组
    for (int i = 0; i < 5; i++) {
        arr3[i] = i * 100;
    }
    printf("  new int[5]: ");
    for (int i = 0; i < 5; i++) {
        printf("%d ", arr3[i]);
    }
    printf("\n");
    delete[] arr3;  // 数组用 delete[]

    printSubsection("6.3 C++ 智能指针（更安全）");

    // unique_ptr：独占所有权，离开作用域自动释放
    unique_ptr<int> uptr(new int(100));
    printf("  unique_ptr: %d\n", *uptr);

    // shared_ptr：引用计数，多个共享，引用计数为 0 时释放
    shared_ptr<int> sptr = make_shared<int>(200);
    printf("  shared_ptr: %d (use_count: %ld)\n", *sptr, sptr.use_count());

    {
        shared_ptr<int> sptr2 = sptr;  // 共享
        printf("  共享后 use_count: %ld\n", sptr.use_count());
    }
    printf("  离开作用域后 use_count: %ld\n", sptr.use_count());

    printf("\n");
    printf("  💡 智能指针能有效防止内存泄漏和 UAF\n");
    printf("     现代 C++ 推荐优先使用智能指针\n");

    printSubsection("6.4 常见内存错误");

    printf("  常见内存错误类型:\n");
    printf("    1. 内存泄漏 (Memory Leak)     - 分配了不释放\n");
    printf("    2. 重复释放 (Double Free)    - 同一块内存释放两次\n");
    printf("    3. 释放后使用 (UAF)          - 释放后继续访问\n");
    printf("    4. 空指针解引用 (Null Deref) - 访问 NULL 指针\n");
    printf("    5. 野指针 (Wild Pointer)     - 指向无效内存\n");
    printf("    6. 越界访问 (Out-of-Bounds)  - 数组/堆溢出\n");
    printf("    7. 未初始化读取             - 读取未初始化的内存\n");
    printf("\n");
    printf("  检测工具: Valgrind、AddressSanitizer (ASan)\n");
}

// ============================================================
// 7. 文件操作
// ============================================================

void demoFileIO() {
    printSection("【7. 文件操作】");

    printSubsection("7.1 文本文件读写");

    const char *filename = "cpp_basics_test.txt";

    // 写入
    FILE *fw = fopen(filename, "w");
    if (fw == NULL) {
        perror("  fopen 写入失败");
        return;
    }

    fprintf(fw, "Hello, C/C++!\n");
    fprintf(fw, "这是一个测试文件\n");
    fprintf(fw, "数字: %d, %f\n", 42, 3.14);
    fclose(fw);
    printf("  已写入文件: %s\n", filename);

    // 读取
    FILE *fr = fopen(filename, "r");
    if (fr == NULL) {
        perror("  fopen 读取失败");
        return;
    }

    printf("\n  文件内容:\n");
    char line[256];
    int lineNum = 0;
    while (fgets(line, sizeof(line), fr) != NULL) {
        lineNum++;
        printf("    %d: %s", lineNum, line);
    }
    fclose(fr);

    printSubsection("7.2 二进制文件读写");

    const char *binFilename = "cpp_basics_test.bin";

    // 写入二进制数据
    FILE *fb = fopen(binFilename, "wb");
    if (fb) {
        int data[] = {0x41424344, 0x45464748, 0x494A4B4C};
        fwrite(data, sizeof(int), 3, fb);
        fclose(fb);
        printf("  已写入二进制文件: %s\n", binFilename);
    }

    // 读取二进制数据
    fb = fopen(binFilename, "rb");
    if (fb) {
        int readData[3];
        size_t n = fread(readData, sizeof(int), 3, fb);
        printf("  读取了 %zu 个整数:\n", n);
        for (size_t i = 0; i < n; i++) {
            printf("    [%zu] 0x%08x = %d\n", i, readData[i], readData[i]);
        }
        fclose(fb);
    }

    // 清理测试文件
    remove(filename);
    remove(binFilename);
    printf("\n  已清理测试文件\n");
}

// ============================================================
// 8. C++ STL 简介
// ============================================================

void demoSTL() {
    printSection("【8. C++ STL 简介（更安全的容器）】");

    printSubsection("8.1 std::vector（动态数组）");

    vector<int> vec = {10, 20, 30, 40, 50};
    vec.push_back(60);  // 末尾添加，自动扩容

    cout << "  vector 大小: " << vec.size() << endl;
    cout << "  vector 容量: " << vec.capacity() << endl;
    cout << "  元素: ";
    for (int v : vec) {  // 范围 for
        cout << v << " ";
    }
    cout << endl;

    // at() 带边界检查（越界抛异常）
    try {
        vec.at(100);  // 越界
    } catch (const out_of_range &e) {
        cout << "  at(100) 越界异常: " << e.what() << endl;
    }

    cout << "  💡 [] 不检查边界（和 C 数组一样危险）" << endl;
    cout << "     at() 检查边界（更安全，但有性能开销）" << endl;

    printSubsection("8.2 std::string");

    string s = "安全字符串";
    s += " - 自动管理内存";
    cout << "  内容: " << s << endl;
    cout << "  长度: " << s.size() << endl;
    cout << "  子串: " << s.substr(0, 5) << endl;
    cout << "  查找: " << (s.find("安全") != string::npos ? "找到" : "未找到") << endl;

    printSubsection("8.3 迭代器");

    cout << "  vector 迭代器遍历: ";
    for (auto it = vec.begin(); it != vec.end(); ++it) {
        cout << *it << " ";
    }
    cout << endl;

    cout << "\n  💡 STL 容器比 C 原生数组安全得多" << endl;
    cout << "     但也要注意：" << endl;
    cout << "     - [] 不检查边界，和 C 数组一样危险" << endl;
    cout << "     - 迭代器失效（push_back 后迭代器可能失效）" << endl;
    cout << "     - C++ 也有自己的漏洞类型（如虚表覆盖）" << endl;
}

// ============================================================
// 9. 内存布局理解
// ============================================================

// 全局变量（数据段）
int global_var = 42;
const int const_global = 100;
static int static_global = 200;

void demoMemoryLayout() {
    printSection("【9. 内存布局理解】");

    // 局部变量（栈）
    int local_var = 10;
    char local_buf[64] = "stack buffer";
    static int static_local = 300;  // 静态局部变量（数据段）

    // 动态分配（堆）
    int *heap_var = new int(1234);
    char *heap_buf = new char[128];

    printf("  各变量的内存地址:\n\n");
    printf("  代码段（只读）:\n");
    printf("    函数 demoMemoryLayout: %p\n", (void*)demoMemoryLayout);
    printf("    字符串常量 \"test\":    %p\n", (void*)"test");
    printf("\n");

    printf("  数据段:\n");
    printf("    全局变量 global_var:   %p\n", (void*)&global_var);
    printf("    静态全局 static_global: %p\n", (void*)&static_global);
    printf("    静态局部 static_local:  %p\n", (void*)&static_local);
    printf("    const 全局 const_global: %p\n", (void*)&const_global);
    printf("\n");

    printf("  堆（动态分配，从低地址向高地址增长）:\n");
    printf("    heap_var:  %p\n", (void*)heap_var);
    printf("    heap_buf:  %p\n", (void*)heap_buf);
    printf("\n");

    printf("  栈（局部变量，从高地址向低地址增长）:\n");
    printf("    local_var:   %p\n", (void*)&local_var);
    printf("    local_buf:   %p\n", (void*)local_buf);
    printf("\n");

    printf("  💡 观察地址可以验证：\n");
    printf("     - 代码段 < 数据段 < 堆 < 栈（一般情况）\n");
    printf("     - 栈上先声明的变量地址更高（栈向下增长）\n");
    printf("     - 堆上先分配的地址更低（堆向上增长）\n");

    delete heap_var;
    delete[] heap_buf;
}

// ============================================================
// 主函数
// ============================================================

int main() {
    cout << endl;
    cout << "============================================================" << endl;
    cout << "  C/C++ 基础语法示例（安全从业者视角）" << endl;
    cout << "  C/C++ Basics for Security Practitioners" << endl;
    cout << "============================================================" << endl;

    // 1. 基本数据类型
    demoDataTypes();

    // 2. 指针
    demoPointers();

    // 3. 数组与字符串
    demoArraysAndStrings();

    // 4. 函数
    demoFunctions();

    // 5. 结构体、联合体、枚举
    demoStructsAndUnions();

    // 6. 动态内存
    demoDynamicMemory();

    // 7. 文件操作
    demoFileIO();

    // 8. C++ STL
    demoSTL();

    // 9. 内存布局
    demoMemoryLayout();

    cout << endl;
    cout << "============================================================" << endl;
    cout << "  所有示例执行完毕" << endl;
    cout << "  涵盖：数据类型、指针、数组、函数、结构体、" << endl;
    cout << "  动态内存、文件操作、STL、内存布局" << endl;
    cout << "============================================================" << endl;
    cout << endl;

    return 0;
}
