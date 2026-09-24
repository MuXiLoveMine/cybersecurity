// security_cases.cpp —— C/C++ 安全案例集
//
// 涵盖内容（均从原理理解和防御角度）：
//   案例 1：缓冲区溢出演示与防护（栈溢出原理 + 安全版本对比）
//   案例 2：格式化字符串漏洞演示与防护
//   案例 3：内存泄漏检测示例（常见泄漏场景 + 正确释放方式）
//   案例 4：整数溢出演示与防护
//   案例 5：UAF（释放后使用）原理演示与防护
//
// 编译方式：
//   g++ -o security_cases security_cases.cpp
//
// 重要提示：
//   - 本文件仅用于安全学习和防御研究
//   - 所有漏洞演示用于理解原理，不提供利用代码
//   - 请在授权测试环境中运行
//   - 重点关注每个案例的"修复方案"和"安全编码实践"

#include <iostream>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <cstdint>
#include <string>
#include <vector>

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

void printWarning(const char *msg) {
    cout << "  ⚠️  " << msg << endl;
}

void printSafe(const char *msg) {
    cout << "  ✅ " << msg << endl;
}

// ============================================================
// 案例 1：缓冲区溢出演示与防护
// ============================================================

// 危险版本：使用 strcpy，不检查目标缓冲区大小
void vulnerable_strcpy(const char *input) {
    char buffer[16];  // 16 字节的小缓冲区
    strcpy(buffer, input);  // 危险！不检查长度
    printf("  [危险版本] buffer 内容: %s\n", buffer);
}

// 安全版本 1：使用 strncpy
void safe_strncpy(const char *input, size_t input_len) {
    char buffer[16];
    size_t max_copy = sizeof(buffer) - 1;  // 留一个位置给 '\0'

    strncpy(buffer, input, max_copy);
    buffer[max_copy] = '\0';  // 确保 null 终止

    printf("  [安全版本 strncpy] buffer 内容: %s\n", buffer);
    printf("  (输入长度 %zu，最多复制 %zu 字节)\n", input_len, max_copy);
}

// 安全版本 2：使用 snprintf
void safe_snprintf(const char *input) {
    char buffer[16];
    int written = snprintf(buffer, sizeof(buffer), "%s", input);

    printf("  [安全版本 snprintf] buffer 内容: %s\n", buffer);
    if (written >= (int)sizeof(buffer)) {
        printf("  (输入被截断了！原长度需要 %d 字节)\n", written);
    }
}

// 安全版本 3：C++ std::string（最安全，自动管理）
void safe_cpp_string(const string &input) {
    string buffer = input;  // 自动扩容，永远不会溢出
    printf("  [安全版本 C++ string] buffer 长度: %zu\n", buffer.size());
    printf("  (std::string 自动管理内存，不用担心缓冲区溢出)\n");
}

void case_bufferOverflow() {
    printSection("【案例 1：缓冲区溢出演示与防护】");

    printf("  缓冲区溢出（Buffer Overflow）是最经典的内存安全漏洞。\n");
    printf("  原理：向固定大小的缓冲区写入超过其容量的数据，\n");
    printf("        覆盖相邻的内存区域（包括返回地址）。\n\n");

    printSubsection("1.1 正常输入（不会溢出）");

    const char *normal_input = "Hello";
    printf("  输入: \"%s\" (长度: %zu)\n", normal_input, strlen(normal_input));
    vulnerable_strcpy(normal_input);
    printSafe("正常输入没有问题");

    printSubsection("1.2 过长输入（演示溢出风险）");

    // 构造一个比缓冲区大的输入
    char long_input[100];
    memset(long_input, 'A', 80);
    long_input[80] = '\0';

    printf("  输入长度: 80 个 'A' (远大于 16 字节的缓冲区)\n");
    printf("\n");
    printWarning("注意：由于现代编译器有栈保护（Stack Canary），");
    printWarning("直接运行可能会触发栈溢出检测而崩溃（这是好事！）。");
    printWarning("在学习环境中可用 -fno-stack-protector 关闭保护观察效果。");
    printf("\n");

    // 注意：这里我们不直接调用危险版本的长输入演示，
    // 因为可能导致程序崩溃（这是预期行为，但影响后续演示）。
    // 原理已经解释清楚，重点看下面的安全版本。

    printf("  栈溢出可以覆盖：\n");
    printf("    1. 栈上的其他局部变量\n");
    printf("    2. 保存的帧指针 (EBP/RBP)\n");
    printf("    3. ★ 返回地址（最重要！可以控制执行流）\n");
    printf("    4. 函数参数\n");

    printSubsection("1.3 安全版本对比");

    const char *test_input = "This is a very long input string that will overflow";
    size_t test_len = strlen(test_input);

    printf("  测试输入长度: %zu 字节\n\n", test_len);

    // 安全方式 1：strncpy
    safe_strncpy(test_input, test_len);
    printf("\n");

    // 安全方式 2：snprintf
    safe_snprintf(test_input);
    printf("\n");

    // 安全方式 3：C++ string
    safe_cpp_string(test_input);

    printSubsection("1.4 防护机制总结");

    printf("  代码层面防护：\n");
    printf("    1. 永远检查缓冲区大小\n");
    printf("    2. 使用带长度限制的函数（strncpy、snprintf、fgets）\n");
    printf("    3. C++ 优先使用 std::string、std::vector 等安全容器\n");
    printf("    4. 输入验证：不信任任何外部输入\n");
    printf("\n");
    printf("  系统层面防护：\n");
    printf("    1. Stack Canary（栈金丝雀）- 检测栈溢出\n");
    printf("    2. DEP / NX（数据执行保护）- 栈不可执行\n");
    printf("    3. ASLR（地址空间随机化）- 地址随机\n");
    printf("    4. CFI（控制流完整性）- 限制间接跳转目标\n");
    printf("    5. SafeSEH / SEHOP（Windows）- 异常处理链保护\n");
    printf("\n");
    printf("  编译选项：\n");
    printf("    -fstack-protector-strong   启用栈保护\n");
    printf("    -D_FORTIFY_SOURCE=2        强化源检查\n");
    printf("    -fPIE -pie                 位置无关可执行\n");
    printf("    -Wl,-z,relro,-z,now        重定位只读\n");
}

// ============================================================
// 案例 2：格式化字符串漏洞演示与防护
// ============================================================

// 危险版本：用户输入直接作为格式化字符串
void vulnerable_format(const char *input) {
    printf(input);  // 极度危险！用户控制格式化字符串
}

// 安全版本：用户输入只作为数据
void safe_format(const char *input) {
    printf("%s", input);  // 正确：input 是 %s 的数据，不是格式串
}

void case_formatString() {
    printSection("【案例 2：格式化字符串漏洞演示与防护】");

    printf("  格式化字符串漏洞：当用户输入被直接用作 printf 的格式化\n");
    printf("  字符串时，攻击者可以通过特殊格式符读取或写入内存。\n\n");

    printSubsection("2.1 正常用法 vs 危险用法");

    const char *normal = "Hello, World!";
    printf("  正常输入: ");
    vulnerable_format(normal);
    printf(" (没问题)\n\n");

    printf("  含格式符的输入: \"%%x %%x %%x\"\n");
    printf("  危险版本输出: ");
    vulnerable_format("%x %x %x");  // 会读取栈上的数据！
    printf("\n\n");

    printWarning("危险版本会泄露栈上的内存内容！");
    printf("\n");

    printf("  格式化字符串漏洞的危害：\n");
    printf("    1. 信息泄露：用 %%x、%%p 读取栈内存\n");
    printf("    2. 任意地址读：用 %%s 读取任意地址的字符串\n");
    printf("    3. 任意地址写：用 %%n 向任意地址写入数据\n");
    printf("    4. 程序崩溃：用 %%n 写入非法地址导致崩溃\n");

    printSubsection("2.2 正确写法");

    printf("  安全版本（使用 %%s）: ");
    safe_format("%x %x %x");  // 安全：%x %x %x 被当普通字符串输出
    printf("\n");
    printSafe("用户输入只作为数据，不控制格式");

    printSubsection("2.3 常见危险函数");

    printf("  危险函数（格式化字符串由外部控制时）:\n");
    printf("    printf, fprintf, sprintf, snprintf\n");
    printf("    vprintf, vfprintf, vsprintf, vsnprintf\n");
    printf("    syslog（系统日志函数）\n");
    printf("\n");
    printf("  防护方法：\n");
    printf("    1. 永远不要把用户输入作为格式化字符串\n");
    printf("    2. 始终使用 \"%%s\" 等格式符，将输入作为数据\n");
    printf("    3. 启用编译器警告：-Wformat-security\n");
    printf("    4. 代码审查：检查所有格式化函数的调用\n");
    printf("    5. 使用静态分析工具检测\n");
}

// ============================================================
// 案例 3：内存泄漏检测示例
// ============================================================

// 泄漏场景 1：函数返回前忘记释放
void leak_scenario1() {
    int *data = (int*)malloc(100 * sizeof(int));
    // ... 使用 data ...
    data[0] = 42;

    // 忘记 free(data) 了！
    // 函数返回后，data 指针消失，但内存还在堆上
    // 这就是内存泄漏
}

// 泄漏场景 2：异常/提前返回导致泄漏
int leak_scenario2(bool error) {
    int *data = (int*)malloc(100 * sizeof(int));
    if (data == NULL) return -1;

    if (error) {
        // 提前返回，忘记释放！
        return -1;
    }

    // ... 正常处理 ...
    free(data);
    return 0;
}

// 泄漏场景 3：指针重新赋值，原内存泄漏
void leak_scenario3() {
    int *p = (int*)malloc(100 * sizeof(int));
    p = (int*)malloc(200 * sizeof(int));  // 原内存泄漏了！
    free(p);  // 只释放了第二次分配的
}

// 正确方式 1：确保所有路径都释放
int safe_scenario2(bool error) {
    int *data = (int*)malloc(100 * sizeof(int));
    if (data == NULL) return -1;

    if (error) {
        free(data);  // 提前返回前释放
        return -1;
    }

    // ... 正常处理 ...
    free(data);
    return 0;
}

// 正确方式 2：C++ 智能指针（自动释放）
void safe_cpp_smart_ptr() {
    // unique_ptr 离开作用域自动释放
    auto data = make_unique<int[]>(100);
    data[0] = 42;

    // 即使提前返回也没问题，智能指针自动释放
    // 不需要手动 delete
}

void case_memoryLeak() {
    printSection("【案例 3：内存泄漏检测示例】");

    printf("  内存泄漏：动态分配的内存没有被释放，导致系统可用内存\n");
    printf("  逐渐减少。虽然不会直接导致代码执行，但长期运行的服务\n");
    printf("  可能因此耗尽内存而崩溃（DDoS）。\n\n");

    printSubsection("3.1 常见内存泄漏场景");

    printf("  场景 1：函数返回前忘记释放\n");
    printf("    void func() {\n");
    printf("        int *p = malloc(100);\n");
    printf("        // ... 使用 ...\n");
    printf("        // 忘记 free(p)！\n");
    printf("    }\n");
    printf("\n");

    printf("  场景 2：异常/提前返回路径遗漏释放\n");
    printf("    int func(bool err) {\n");
    printf("        int *p = malloc(100);\n");
    printf("        if (err) return -1;  // 泄漏！\n");
    printf("        free(p);\n");
    printf("        return 0;\n");
    printf("    }\n");
    printf("\n");

    printf("  场景 3：指针重新赋值\n");
    printf("    int *p = malloc(100);\n");
    printf("    p = malloc(200);  // 第一次分配的内存泄漏了！\n");
    printf("\n");

    printf("  场景 4：循环中重复分配不释放\n");
    printf("  场景 5：数据结构中（链表/树）节点没有正确释放\n");
    printf("  场景 6：C++ 中基类析构函数不是 virtual\n");

    printSubsection("3.2 检测工具");

    printf("  Valgrind Memcheck:\n");
    printf("    valgrind --leak-check=full ./program\n");
    printf("    优点：不需要重新编译，检测准确\n");
    printf("    缺点：速度慢（慢 10-30 倍）\n");
    printf("\n");

    printf("  AddressSanitizer (ASan):\n");
    printf("    gcc -fsanitize=address -g program.c -o program\n");
    printf("    优点：速度快（只慢 2 倍左右），信息详细\n");
    printf("    缺点：需要重新编译\n");
    printf("\n");

    printf("  其他工具：\n");
    printf("    - Dr. Memory: Windows/Linux\n");
    printf("    - LeakSanitizer (LSan): 专门检测泄漏\n");
    printf("    - Visual Studio 内存诊断: Windows\n");

    printSubsection("3.3 预防方法");

    printf("  C 语言：\n");
    printf("    1. malloc 和 free 配对，写在同一个函数里\n");
    printf("    2. 所有返回路径都要检查释放\n");
    printf("    3. 使用 goto 统一清理（Linux 内核风格）\n");
    printf("    4. 释放后置指针为 NULL\n");
    printf("\n");
    printf("  C++：\n");
    printf("    1. 使用智能指针（unique_ptr、shared_ptr）\n");
    printf("    2. 使用 RAII 惯用法\n");
    printf("    3. 优先使用 STL 容器，避免手动管理内存\n");
    printf("    4. 基类析构函数声明为 virtual\n");

    printSubsection("3.4 演示：运行时检测（概念说明）");

    printf("  下面演示几个泄漏场景（程序结束后 OS 会回收，\n");
    printf("  但实际运行中长时间运行的服务会积累泄漏）：\n\n");

    // 这些函数会造成泄漏，但程序退出后系统会回收
    // 用 Valgrind 或 ASan 才能检测到
    leak_scenario1();
    leak_scenario2(true);
    leak_scenario3();

    printSafe("安全版本：");
    safe_scenario2(true);
    safe_cpp_smart_ptr();

    printf("\n");
    printWarning("检测内存泄漏需要 Valgrind 或 AddressSanitizer 等工具");
    printf("  编译时加入 -fsanitize=address 即可在运行时看到详细报告\n");
}

// ============================================================
// 案例 4：整数溢出演示与防护
// ============================================================

// 危险：整数溢出导致缓冲区大小计算错误
void vulnerable_int_overflow(unsigned int user_size) {
    // 检查 size 不超过 1024
    if (user_size > 1024) {
        printf("  [危险版本] size 太大，拒绝\n");
        return;
    }

    // 但是 size * 2 可能溢出！
    // 如果 user_size = 0x80000000 (2^31)，user_size * 2 = 0
    // malloc(0) 可能返回很小的缓冲区，后面写入就会溢出
    unsigned int total_size = user_size * 2;
    printf("  [危险版本] user_size = %u, total_size = %u\n",
           user_size, total_size);

    // 实际场景中这里会 malloc(total_size) 然后写入 user_size * 2 的数据
    // 就会导致堆溢出
}

// 安全：在计算前检查是否溢出
int safe_int_multiply(unsigned int a, unsigned int b, unsigned int *result) {
    if (a > UINT32_MAX / b) {
        return -1;  // 会溢出
    }
    *result = a * b;
    return 0;
}

void safe_int_overflow(unsigned int user_size) {
    if (user_size > 1024) {
        printf("  [安全版本] size 太大，拒绝\n");
        return;
    }

    unsigned int total_size;
    if (safe_int_multiply(user_size, 2, &total_size) != 0) {
        printf("  [安全版本] 乘法溢出！拒绝操作\n");
        return;
    }

    printf("  [安全版本] user_size = %u, total_size = %u\n",
           user_size, total_size);
    printSafe("整数溢出检查通过");
}

void case_integerOverflow() {
    printSection("【案例 4：整数溢出演示与防护】");

    printf("  整数溢出：当算术运算结果超出类型所能表示的范围时，\n");
    printf("  结果会回绕（无符号）或产生未定义行为（有符号）。\n");
    printf("  整数溢出常导致缓冲区分配不足，进而引发堆溢出。\n\n");

    printSubsection("4.1 有符号 vs 无符号转换问题");

    int signed_val = -1;
    unsigned int unsigned_val = (unsigned int)signed_val;

    printf("  int -1 = %d\n", signed_val);
    printf("  转 unsigned int 后 = %u (0x%08x)\n", unsigned_val, unsigned_val);
    printf("\n");

    printf("  典型漏洞模式：\n");
    printf("    void func(int len) {\n");
    printf("        if (len < 0) return;   // 检查负数\n");
    printf("        char buf[100];\n");
    printf("        memcpy(buf, input, len);  // len 是 size_t（无符号）\n");
    printf("    }                             // len = -1 变成超大正数！\n");
    printf("\n");
    printWarning("有符号/无符号隐式转换是常见的整数问题来源");

    printSubsection("4.2 算术溢出演示");

    printf("  测试 1：正常大小\n");
    vulnerable_int_overflow(100);
    printf("\n");

    printf("  测试 2：溢出大小（接近 2^32 / 2）\n");
    // 用一个不会触发 > 1024 检查但乘法会溢出的值
    // 注意：因为有 > 1024 的检查，这里用一个不同的演示
    unsigned int big = 0x80000000u / 2;  // 2^30
    // 这个值 * 2 = 2^31，无符号下不会溢出（因为 2^31 < 2^32）
    // 但如果是有符号 int 就溢出了

    printf("  有符号溢出演示：\n");
    int32_t signed_max = INT32_MAX;
    printf("  int32_max = %d (0x%08x)\n", signed_max, signed_max);
    printf("  signed_max + 1 = %d (溢出！)\n", signed_max + 1);
    printf("  (有符号整数溢出是未定义行为)\n");
    printf("\n");

    printf("  无符号回绕演示：\n");
    uint32_t unsigned_max = UINT32_MAX;
    printf("  uint32_max = %u (0x%08x)\n", unsigned_max, unsigned_max);
    printf("  unsigned_max + 1 = %u (回绕到 0)\n", unsigned_max + 1);
    printf("  (无符号整数是定义良好的回绕行为)\n");

    printSubsection("4.3 安全整数运算");

    printf("  安全乘法检查：\n");
    safe_int_overflow(100);
    printf("\n");

    printf("  溢出检测：\n");
    unsigned int result;
    if (safe_int_multiply(UINT32_MAX, 2, &result) != 0) {
        printSafe("正确检测到溢出，拒绝操作");
    }

    printSubsection("4.4 防护方法");

    printf("  代码层面：\n");
    printf("    1. 计算前检查是否会溢出\n");
    printf("    2. 使用安全整数运算库（如 C++20 的 std::overflow）\n");
    printf("    3. 避免有符号/无符号混用\n");
    printf("    4. 使用足够大的类型（size_t 做大小计算）\n");
    printf("\n");
    printf("  工具层面：\n");
    printf("    1. 编译器警告：-Wconversion -Wsign-conversion\n");
    printf("    2. UBSan (UndefinedBehaviorSanitizer): -fsanitize=undefined\n");
    printf("    3. 静态代码分析工具\n");
    printf("    4. 代码审查：特别注意大小计算相关的代码\n");
}

// ============================================================
// 案例 5：UAF（释放后使用）演示与防护
// ============================================================

// 一个简单的数据结构
struct UserData {
    char name[32];
    int age;
    void (*printFunc)(struct UserData*);  // 函数指针
};

void printUser(struct UserData *u) {
    printf("    用户名: %s, 年龄: %d\n", u->name, u->age);
}

// 危险：释放后继续使用
void vulnerable_uaf() {
    struct UserData *user = (struct UserData*)malloc(sizeof(struct UserData));
    if (user == NULL) return;

    strncpy(user->name, "Alice", sizeof(user->name) - 1);
    user->age = 25;
    user->printFunc = printUser;

    printf("  释放前: ");
    user->printFunc(user);

    free(user);  // 释放内存
    // user = NULL;  // 没有置空！

    printf("  释放后: ");
    // ⚠️ UAF！user 已经释放了，但还在使用
    // 实际行为：可能正常（内存还没被覆盖）、可能崩溃、可能被利用
    // 这取决于内存分配器和时间
    printf("（演示 UAF 原理：释放后的指针称为悬垂指针）\n");
    printf("    如果这时候内存被重新分配并修改...\n");
    printf("    继续使用旧指针就会访问到错误的数据\n");
    printf("    极端情况：函数指针被篡改，导致任意代码执行\n");

    // 注意：我们不在这真的调用 UAF，因为行为不确定
    // 实际中 UAF 是现代最常见的高危漏洞类型之一
}

// 安全版本 1：释放后置空
void safe_uaf_null_after_free() {
    struct UserData *user = (struct UserData*)malloc(sizeof(struct UserData));
    if (user == NULL) return;

    strncpy(user->name, "Bob", sizeof(user->name) - 1);
    user->age = 30;

    printf("  释放前: 用户名: %s, 年龄: %d\n", user->name, user->age);

    free(user);
    user = NULL;  // 释放后置空！

    // 之后使用前检查
    if (user != NULL) {
        printf("  user 指针有效\n");
    } else {
        printSafe("user 已释放且置空，不会误访问");
    }
}

// 安全版本 2：C++ 智能指针
void safe_uaf_smart_ptr() {
    // shared_ptr 使用引用计数
    auto user = make_shared<string>("Charlie");

    {
        auto user2 = user;  // 增加引用计数
        printf("  作用域内: %s (引用计数: %ld)\n", user->c_str(), user.use_count());
    }

    printf("  作用域外: %s (引用计数: %ld)\n", user->c_str(), user.use_count());
    printSafe("shared_ptr 引用计数为 0 才释放，不会 UAF");

    // weak_ptr 不增加引用计数，但可以检查是否有效
    weak_ptr<string> weak = user;
    if (auto shared = weak.lock()) {
        printf("  weak_ptr 锁定成功: %s\n", shared->c_str());
    } else {
        printf("  对象已释放\n");
    }
}

void case_uaf() {
    printSection("【案例 5：UAF（释放后使用）演示与防护】");

    printf("  UAF (Use-After-Free)：内存被释放后，程序继续使用\n");
    printf("  指向该内存的指针。这是现代软件中最常见的高危漏洞类型之一，\n");
    printf("  特别是在浏览器、iOS、Android 等复杂系统中。\n\n");

    printSubsection("5.1 UAF 原理");

    printf("  典型场景：\n\n");
    printf("    1. 分配对象: obj = malloc(size)\n");
    printf("    2. 使用对象: obj->method()\n");
    printf("    3. 释放对象: free(obj)\n");
    printf("    4. ★ 继续使用: obj->method()  ← UAF！\n");
    printf("\n");

    printf("  为什么危险：\n");
    printf("    1. 释放的内存可能被重新分配给其他对象\n");
    printf("    2. 如果攻击者控制了新分配的数据，就相当于控制了旧对象\n");
    printf("    3. 如果对象有虚函数表（vtable），可以篡改函数指针\n");
    printf("    4. 最终可能实现任意代码执行\n");

    printSubsection("5.2 危险示例（原理演示）");

    vulnerable_uaf();

    printSubsection("5.3 防护方法");

    printf("  C 语言：\n");
    printf("    1. 释放内存后立即将指针置为 NULL\n");
    printf("    2. 使用前检查指针是否为 NULL\n");
    printf("    3. 清晰的所有权语义：谁分配谁释放\n");
    printf("    4. 引用计数机制（手动实现）\n");
    printf("\n");
    printf("  C++：\n");
    printf("    1. 使用 std::unique_ptr（独占所有权）\n");
    printf("    2. 使用 std::shared_ptr（共享所有权，引用计数）\n");
    printf("    3. 使用 std::weak_ptr（观察，不增加引用）\n");
    printf("    4. 遵循 RAII 原则\n");
    printf("\n");
    printf("  检测工具：\n");
    printf("    1. AddressSanitizer (ASan) - 能精确检测 UAF\n");
    printf("    2. Valgrind Memcheck\n");
    printf("    3. 各种 fuzzing 工具\n");

    printSubsection("5.4 安全版本演示");

    printf("  方式 1：释放后置空\n");
    safe_uaf_null_after_free();
    printf("\n");

    printf("  方式 2：C++ 智能指针\n");
    safe_uaf_smart_ptr();
}

// ============================================================
// 总结：安全编码最佳实践
// ============================================================

void printSecurityChecklist() {
    printSection("【附：C/C++ 安全编码检查清单】");

    printf("  内存安全：\n");
    printf("    [ ] 所有缓冲区操作都检查长度\n");
    printf("    [ ] 使用安全的字符串函数（strncpy、snprintf 等）\n");
    printf("    [ ] malloc 返回值检查是否为 NULL\n");
    printf("    [ ] malloc 和 free 配对，所有路径都释放\n");
    printf("    [ ] 释放后置指针为 NULL\n");
    printf("    [ ] 不访问已释放的内存（UAF）\n");
    printf("    [ ] 不重复释放同一块内存（Double Free）\n");
    printf("\n");

    printf("  整数安全：\n");
    printf("    [ ] 大小计算检查整数溢出\n");
    printf("    [ ] 避免有符号/无符号隐式转换\n");
    printf("    [ ] 数组下标检查边界\n");
    printf("    [ ] 使用 size_t 做大小/索引计算\n");
    printf("\n");

    printf("  格式化字符串：\n");
    printf("    [ ] 不把用户输入作为格式化字符串\n");
    printf("    [ ] 始终使用 \"%%s\" 等格式符输出用户输入\n");
    printf("    [ ] 启用 -Wformat-security 警告\n");
    printf("\n");

    printf("  输入验证：\n");
    printf("    [ ] 不信任任何外部输入\n");
    printf("    [ ] 验证输入长度、范围、格式\n");
    printf("    [ ] 边界值测试（0、-1、最大值、超长）\n");
    printf("\n");

    printf("  编译选项：\n");
    printf("    [ ] -Wall -Wextra -Wpedantic（启用警告）\n");
    printf("    [ ] -Werror（警告视为错误）\n");
    printf("    [ ] -fstack-protector-strong（栈保护）\n");
    printf("    [ ] -D_FORTIFY_SOURCE=2（源强化）\n");
    printf("    [ ] -fPIE -pie（位置无关可执行）\n");
    printf("    [ ] -Wl,-z,relro,-z,now（重定位保护）\n");
    printf("    [ ] -O2（优化也能消除一些问题）\n");
    printf("\n");

    printf("  测试与工具：\n");
    printf("    [ ] AddressSanitizer 检测内存错误\n");
    printf("    [ ] Valgrind 检测内存泄漏\n");
    printf("    [ ] 静态代码分析（Cppcheck、Clang Static Analyzer）\n");
    printf("    [ ] Fuzzing 测试（AFL、libFuzzer）\n");
    printf("    [ ] 代码审查\n");
    printf("\n");

    printf("  C++ 额外建议：\n");
    printf("    [ ] 优先使用 std::string 而非 char*\n");
    printf("    [ ] 优先使用 STL 容器而非原生数组\n");
    printf("    [ ] 使用智能指针而非裸指针\n");
    printf("    [ ] 遵循 RAII 原则\n");
    printf("    [ ] 基类析构函数声明为 virtual\n");
    printf("    [ ] 用 at() 而非 [] 做边界检查（性能不敏感时）\n");
}

// ============================================================
// 主函数
// ============================================================

int main(int argc, char *argv[]) {
    cout << endl;
    cout << "============================================================" << endl;
    cout << "  C/C++ 安全案例集" << endl;
    cout << "  C/C++ Security Cases" << endl;
    cout << "============================================================" << endl;
    cout << endl;
    cout << "  本程序从防御角度演示常见 C/C++ 内存安全漏洞的" << endl;
    cout << "  原理与防护方法。所有案例均用于学习研究，" << endl;
    cout << "  请在授权环境中使用。" << endl;

    // 如果指定了案例编号，只运行指定案例
    int caseNum = 0;
    if (argc > 1) {
        caseNum = atoi(argv[1]);
    }

    switch (caseNum) {
        case 0:
            // 运行所有案例
            case_bufferOverflow();
            case_formatString();
            case_memoryLeak();
            case_integerOverflow();
            case_uaf();
            printSecurityChecklist();
            break;
        case 1:
            case_bufferOverflow();
            break;
        case 2:
            case_formatString();
            break;
        case 3:
            case_memoryLeak();
            break;
        case 4:
            case_integerOverflow();
            break;
        case 5:
            case_uaf();
            break;
        case 6:
            printSecurityChecklist();
            break;
        default:
            printf("  用法: %s [案例编号]\n", argv[0]);
            printf("  案例: 1=缓冲区溢出  2=格式化字符串  3=内存泄漏\n");
            printf("         4=整数溢出    5=UAF          6=安全检查清单\n");
            printf("         0 或不指定 = 全部运行\n");
            return 1;
    }

    cout << endl;
    cout << "============================================================" << endl;
    cout << "  演示完成。记住：理解漏洞原理是为了更好地防御。" << endl;
    cout << "  请遵守法律法规，仅在授权环境中进行安全测试。" << endl;
    cout << "============================================================" << endl;
    cout << endl;

    return 0;
}
