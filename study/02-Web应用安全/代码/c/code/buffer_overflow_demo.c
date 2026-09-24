/*
 * ============================================================
 * 文件名：buffer_overflow_demo.c
 * 功能描述：缓冲区溢出漏洞演示与防护
 * 作者：网络安全学习笔记
 * 日期：2026-09-21
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译方式：
 *    gcc buffer_overflow_demo.c -o buffer_overflow_demo -fno-stack-protector -z execstack
 *    （禁用栈保护，便于演示漏洞原理）
 * 2. 正常编译（带保护）：
 *    gcc buffer_overflow_demo.c -o buffer_overflow_demo
 *
 * 【演示内容】
 *   1. 栈溢出基础演示
 *   2. 不安全的字符串函数
 *   3. 格式化字符串漏洞
 *   4. 整数溢出
 *   5. 安全的编程方式
 *
 * 【警告】
 *   本程序仅用于学习缓冲区溢出的原理。
 *   实际环境中请使用安全的编程方式。
 *   利用漏洞攻击未授权系统是违法行为。
 * ============================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

// ==================== 1. 栈溢出演示 ====================

// 有漏洞的函数：使用 gets 读取输入，没有边界检查
void vulnerable_function(char *input) {
    char buffer[16];  // 只有 16 字节的缓冲区

    printf("  [漏洞函数] buffer 地址: %p\n", (void *)buffer);
    printf("  [漏洞函数] input 地址: %p\n", (void *)input);

    // 危险！strcpy 不检查目标缓冲区大小
    strcpy(buffer, input);

    printf("  [漏洞函数] 缓冲区内容: %s\n", buffer);
    printf("  [漏洞函数] 函数正常返回\n");
}

// 安全的函数：使用 strncpy 限制复制长度
void safe_function(char *input, size_t input_len) {
    char buffer[16];

    printf("  [安全函数] buffer 地址: %p\n", (void *)buffer);

    // 安全！限制最大复制长度
    strncpy(buffer, input, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';  // 确保字符串结束

    printf("  [安全函数] 缓冲区内容: %s\n", buffer);
    printf("  [安全函数] 函数正常返回\n");
}


// ==================== 2. 不安全的字符串函数 ====================

void unsafe_string_demo() {
    printf("\n========== 不安全的字符串函数 ==========\n");

    char dest[10];
    char src[] = "This is a very long string that will overflow!";

    printf("危险函数演示（不会实际执行，仅说明）：\n");
    printf("  1. gets(buf) - 永远不要使用，无边界检查\n");
    printf("  2. strcpy(dest, src) - 不检查目标大小\n");
    printf("  3. strcat(dest, src) - 不检查目标剩余空间\n");
    printf("  4. sprintf(buf, format, ...) - 不检查缓冲区大小\n");
    printf("  5. scanf(\"%%s\", buf) - 不限制输入长度\n");

    printf("\n安全替代方案：\n");
    printf("  1. fgets(buf, size, stdin) - 限制读取长度\n");
    printf("  2. strncpy(dest, src, n) - 限制复制长度\n");
    printf("  3. strncat(dest, src, n) - 限制追加长度\n");
    printf("  4. snprintf(buf, size, format, ...) - 限制输出长度\n");
    printf("  5. scanf(\"%%Ns\", buf) - 限制输入长度\n");

    // 安全使用示例
    char safe_buf[16];
    printf("\n安全使用 fgets 示例（输入不超过 15 个字符）：\n");
    printf("  缓冲区大小: %zu 字节\n", sizeof(safe_buf));
    printf("  fgets 会自动限制不超过缓冲区大小\n");
    // 演示用，不实际读取
    strncpy(safe_buf, "safe input", sizeof(safe_buf) - 1);
    safe_buf[sizeof(safe_buf) - 1] = '\0';
    printf("  安全内容: %s\n", safe_buf);
}


// ==================== 3. 格式化字符串漏洞 ====================

void format_string_demo() {
    printf("\n========== 格式化字符串漏洞 ==========\n");

    char user_input[64] = "Hello %x %x %x %x";

    printf("有漏洞的写法（直接使用用户输入作为格式串）：\n");
    printf("  printf(user_input) 可能导致：\n");
    printf("    - 泄露栈上数据（%%x, %%s）\n");
    printf("    - 内存写入（%%n）\n");
    printf("    - 程序崩溃（%%s 访问非法地址）\n");
    printf("\n  示例输出：\n  ");
    // 注意：实际环境中这可能导致崩溃，这里仅演示
    printf(user_input);
    printf("\n");

    printf("\n安全的写法：\n");
    printf("  printf(\"%%s\", user_input)\n");
    printf("  示例输出：\n  ");
    printf("%s", user_input);
    printf("\n");

    // 格式化字符串漏洞的危害说明
    printf("\n格式化字符串漏洞危害：\n");
    printf("  %%x  - 读取栈上数据，泄露内存信息\n");
    printf("  %%s  - 读取字符串，可能导致崩溃\n");
    printf("  %%n  - 将已输出字符数写入指定地址（任意写）\n");
    printf("  %%hn - 写入两字节，更精确的内存写入\n");
}


// ==================== 4. 整数溢出 ====================

void integer_overflow_demo() {
    printf("\n========== 整数溢出 ==========\n");

    // 无符号整数溢出
    unsigned int ui = 4294967295u;  // UINT_MAX
    printf("无符号整数溢出：\n");
    printf("  unsigned int max = %u\n", ui);
    printf("  max + 1 = %u（溢出后归零）\n", ui + 1);

    // 有符号整数溢出（未定义行为）
    int si = 2147483647;  // INT_MAX
    printf("\n有符号整数溢出：\n");
    printf("  int max = %d\n", si);
    printf("  max + 1 = %d（溢出变为负数，UB）\n", si + 1);

    // 整数溢出在安全中的影响
    printf("\n整数溢出的安全影响：\n");
    printf("  1. 内存分配计算溢出：malloc(size * count)\n");
    printf("     当 size * count 溢出时，分配的内存比实际需要的小\n");
    printf("     导致后续写入时发生堆溢出\n");
    printf("  2. 数组下标计算溢出：访问越界\n");
    printf("  3. 长度校验绕过：负数长度绕过检查\n");

    // 示例：危险的内存分配
    printf("\n危险代码示例：\n");
    printf("  void alloc_buffers(int count) {\n");
    printf("      int total = count * 64;  // count 过大时溢出\n");
    printf("      char *buf = malloc(total);\n");
    printf("      // 后续操作可能导致堆溢出\n");
    printf("  }\n");

    printf("\n安全代码示例：\n");
    printf("  int alloc_buffers(int count) {\n");
    printf("      if (count <= 0 || count > INT_MAX / 64) {\n");
    printf("          return -1;  // 参数校验\n");
    printf("      }\n");
    printf("      int total = count * 64;\n");
    printf("      char *buf = malloc(total);\n");
    printf("      // ...\n");
    printf("  }\n");
}


// ==================== 5. 栈结构可视化 ====================

void stack_layout_demo() {
    printf("\n========== 栈结构示意 ==========\n");

    int local_int = 0x12345678;
    char local_buf[8] = "ABCDEFGH";
    char *local_ptr = local_buf;

    printf("局部变量地址（从高到低，栈向下增长）：\n");
    printf("  高地址  ┌─────────────────────┐\n");
    printf("          │     返回地址        │  ← 被覆盖则控制程序流\n");
    printf("          ├─────────────────────┤\n");
    printf("          │     保存的 EBP      │  ← 帧指针\n");
    printf("          ├─────────────────────┤\n");
    printf("          │  local_ptr (8字节)  │  %p\n", (void *)&local_ptr);
    printf("          ├─────────────────────┤\n");
    printf("          │  local_buf (8字节)  │  %p\n", (void *)local_buf);
    printf("          ├─────────────────────┤\n");
    printf("  低地址  │  local_int (4字节)  │  %p\n", (void *)&local_int);
    printf("          └─────────────────────┘\n");

    printf("\n缓冲区溢出原理：\n");
    printf("  向 buffer 写入超过其大小的数据，\n");
    printf("  数据会向上覆盖栈上的其他变量，\n");
    printf("  最终覆盖返回地址，从而控制程序执行流。\n");

    printf("\n防护措施：\n");
    printf("  1. 栈保护（Canary / Stack Cookie）\n");
    printf("  2. 数据执行保护（DEP / NX）\n");
    printf("  3. 地址空间布局随机化（ASLR）\n");
    printf("  4. 安全的编程方式（边界检查）\n");
}


// ==================== 6. 安全编程实践 ====================

void secure_programming() {
    printf("\n========== 安全编程实践 ==========\n");

    printf("1. 永远不要使用 gets()\n");
    printf("   替代：fgets(buf, sizeof(buf), stdin)\n\n");

    printf("2. 字符串操作使用带长度限制的函数\n");
    printf("   strcpy  →  strncpy + 手动补零\n");
    printf("   strcat  →  strncat\n");
    printf("   sprintf →  snprintf\n");
    printf("   scanf   →  限制宽度（%%20s）\n\n");

    printf("3. 整数运算前进行溢出检查\n");
    printf("   - 检查输入参数范围\n");
    printf("   - 使用无符号整数进行大小计算\n");
    printf("   - 乘法前检查是否溢出\n\n");

    printf("4. 格式化字符串使用常量格式串\n");
    printf("   不要：printf(user_input)\n");
    printf("   应该：printf(\"%%s\", user_input)\n\n");

    printf("5. 使用编译器安全选项\n");
    printf("   -fstack-protector    栈保护\n");
    printf("   -fPIE -pie           位置无关可执行\n");
    printf("   -D_FORTIFY_SOURCE=2  源级别强化\n");
    printf("   -z relro -z now      重定位保护\n");
    printf("   -z noexecstack       不可执行栈\n");
}


// ==================== 主函数 ====================

int main(int argc, char *argv[]) {
    printf("========================================\n");
    printf("  缓冲区溢出漏洞演示与防护（C 语言版）\n");
    printf("========================================\n");

    printf("\n【重要声明】\n");
    printf("本程序仅用于学习缓冲区溢出的原理和防护方法。\n");
    printf("请勿将相关技术用于非法用途。\n");

    int choice;
    while (1) {
        printf("\n\n========================================\n");
        printf("              演示菜单\n");
        printf("========================================\n");
        printf("  1. 栈溢出基础演示\n");
        printf("  2. 不安全的字符串函数\n");
        printf("  3. 格式化字符串漏洞\n");
        printf("  4. 整数溢出\n");
        printf("  5. 栈结构示意\n");
        printf("  6. 安全编程实践\n");
        printf("  0. 退出\n");
        printf("========================================\n");
        printf("请选择：");

        if (scanf("%d", &choice) != 1) {
            printf("无效输入\n");
            // 清除输入缓冲区
            int c;
            while ((c = getchar()) != '\n' && c != EOF);
            continue;
        }
        // 清除换行
        getchar();

        switch (choice) {
            case 1: {
                printf("\n========== 栈溢出基础演示 ==========\n");
                char input1[20] = "short input";
                printf("测试1：正常输入（短于缓冲区）\n");
                vulnerable_function(input1);

                printf("\n测试2：安全函数处理长输入\n");
                char input2[100] = "This is a very long input string for testing";
                safe_function(input2, strlen(input2));
                break;
            }
            case 2:
                unsafe_string_demo();
                break;
            case 3:
                format_string_demo();
                break;
            case 4:
                integer_overflow_demo();
                break;
            case 5:
                stack_layout_demo();
                break;
            case 6:
                secure_programming();
                break;
            case 0:
                printf("\n退出程序。安全编程，从我做起！\n");
                return 0;
            default:
                printf("无效选择，请重新输入\n");
        }
    }

    return 0;
}
