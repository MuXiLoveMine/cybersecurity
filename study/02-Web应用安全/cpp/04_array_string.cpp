// ============================================================
// 04_array_string.cpp —— 数组、字符串操作、指针
// 编译命令：g++ 04_array_string.cpp -o 04_array_string
// 运行命令：./04_array_string（Linux/Mac） 或 04_array_string.exe（Windows）
// ============================================================

#include <iostream>
#include <cstring>   // C 风格字符串函数
#include <string>    // C++ string 类
using namespace std;

int main() {
    // ---------- 1. 一维数组 ----------
    cout << "========== 一维数组 ==========" << endl;

    // 定义并初始化数组
    int nums[5] = {10, 20, 30, 40, 50};

    // 访问数组元素（下标从 0 开始）
    cout << "nums[0] = " << nums[0] << endl;
    cout << "nums[2] = " << nums[2] << endl;
    cout << "nums[4] = " << nums[4] << endl;

    // 修改元素
    nums[1] = 200;
    cout << "修改后 nums[1] = " << nums[1] << endl;

    // 数组大小
    cout << "数组大小（字节）：" << sizeof(nums) << endl;
    cout << "元素个数：" << sizeof(nums) / sizeof(nums[0]) << endl;

    // 遍历数组
    cout << "\n遍历数组：";
    for (int i = 0; i < 5; i++) {
        cout << nums[i] << " ";
    }
    cout << endl;

    // 其他初始化方式
    int arr1[10] = {0};          // 全部初始化为 0
    int arr2[] = {1, 2, 3, 4, 5}; // 自动推断大小
    cout << "arr2 的元素个数：" << (sizeof(arr2)/sizeof(arr2[0])) << endl;

    // 范围 for 循环（C++11）
    cout << "范围 for 遍历：";
    for (int x : arr2) {
        cout << x << " ";
    }
    cout << endl;


    // ---------- 2. 二维数组 ----------
    cout << "\n========== 二维数组 ==========" << endl;

    // 定义 3x3 的矩阵
    int matrix[3][3] = {
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    };

    // 访问元素
    cout << "matrix[1][2] = " << matrix[1][2] << "（第2行第3列）" << endl;

    // 遍历二维数组
    cout << "3x3 矩阵：" << endl;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            cout << matrix[i][j] << "\t";
        }
        cout << endl;
    }

    // 二维数组的内存布局是连续的（行优先）
    cout << "\n二维数组在内存中是连续存储的（行优先）：" << endl;
    int* p = &matrix[0][0];
    for (int i = 0; i < 9; i++) {
        cout << "第 " << i << " 个字节位置的值：" << *(p + i) << endl;
    }


    // ---------- 3. 指针基础 ----------
    cout << "\n========== 指针基础 ==========" << endl;

    int var = 42;
    int* ptr = &var;   // ptr 指向 var 的地址

    cout << "var 的值：" << var << endl;
    cout << "var 的地址：" << &var << endl;
    cout << "ptr 的值（var 的地址）：" << ptr << endl;
    cout << "ptr 指向的值（解引用）：" << *ptr << endl;

    // 通过指针修改变量
    *ptr = 100;
    cout << "\n通过 *ptr = 100 修改后：" << endl;
    cout << "var = " << var << endl;

    // 空指针
    int* null_ptr = nullptr;  // C++11 推荐
    cout << "\n空指针：" << null_ptr << endl;
    // cout << *null_ptr << endl;  // 错误：解引用空指针会导致程序崩溃


    // ---------- 4. 指针与数组 ----------
    cout << "\n========== 指针与数组 ==========" << endl;

    int arr[5] = {10, 20, 30, 40, 50};
    int* p_arr = arr;  // 数组名是首元素的地址

    cout << "arr 首地址：" << arr << endl;
    cout << "p_arr 的值：" << p_arr << endl;

    // 使用指针访问数组元素
    cout << "\n使用指针遍历数组：" << endl;
    for (int i = 0; i < 5; i++) {
        cout << "*(p_arr + " << i << ") = " << *(p_arr + i)
             << "  等价于 arr[" << i << "] = " << arr[i] << endl;
    }

    // 指针运算
    cout << "\n指针运算：" << endl;
    cout << "p_arr 指向：" << *p_arr << endl;
    p_arr++;  // 指针加 1，指向下一个元素
    cout << "p_arr++ 后指向：" << *p_arr << endl;
    p_arr--;  // 指针减 1
    cout << "p_arr-- 后指向：" << *p_arr << endl;

    // 指针相减（计算元素个数）
    int* start = &arr[0];
    int* end = &arr[4];
    cout << "\nend - start = " << (end - start) << " 个元素间隔" << endl;


    // ---------- 5. C 风格字符串 ----------
    cout << "\n========== C 风格字符串 ==========" << endl;

    // 字符串是以 '\0' 结尾的字符数组
    char str1[20] = "Hello";
    char str2[] = "World";

    cout << "str1 = " << str1 << endl;
    cout << "str2 = " << str2 << endl;

    // 字符串长度
    cout << "str1 长度（strlen）：" << strlen(str1) << endl;
    cout << "str1 大小（sizeof）：" << sizeof(str1) << "字节" << endl;

    // 字符串复制
    char dest[20];
    strcpy(dest, str1);
    cout << "\nstrcpy(dest, str1) 后 dest = " << dest << endl;

    // 字符串拼接
    strcat(dest, " ");
    strcat(dest, str2);
    cout << "strcat 拼接后：" << dest << endl;

    // 字符串比较
    cout << "\nstrcmp(\"abc\", \"abc\") = " << strcmp("abc", "abc") << "（相等）" << endl;
    cout << "strcmp(\"abc\", \"abd\") = " << strcmp("abc", "abd") << "（小于）" << endl;
    cout << "strcmp(\"abd\", \"abc\") = " << strcmp("abd", "abc") << "（大于）" << endl;

    // 查找字符
    char* pos = strchr(dest, 'W');
    if (pos != nullptr) {
        cout << "\n找到 'W' 的位置：" << pos << endl;
    }

    // 遍历字符串
    cout << "\n逐个字符遍历 str1：" << endl;
    for (int i = 0; str1[i] != '\0'; i++) {
        cout << "  str1[" << i << "] = '" << str1[i] << "'" << endl;
    }

    // 使用指针遍历
    cout << "\n使用指针遍历 str2：" << endl;
    char* p_str = str2;
    while (*p_str != '\0') {
        cout << "  '" << *p_str << "' ";
        p_str++;
    }
    cout << endl;


    // ---------- 6. C++ string 类 ----------
    cout << "\n========== C++ string 类 ==========" << endl;

    string s1 = "Hello";
    string s2 = "C++";

    cout << "s1 = " << s1 << endl;
    cout << "s2 = " << s2 << endl;

    // 字符串拼接
    string s3 = s1 + ", " + s2 + "!";
    cout << "拼接：" << s3 << endl;

    // 长度
    cout << "s3 长度：" << s3.length() << " 或 " << s3.size() << endl;
    cout << "s3 是否为空：" << (s3.empty() ? "是" : "否") << endl;

    // 访问字符
    cout << "s3[0] = " << s3[0] << endl;
    cout << "s3.at(7) = " << s3.at(7) << "（带边界检查）" << endl;

    // 子串
    cout << "\ns3.substr(0, 5) = " << s3.substr(0, 5) << endl;
    cout << "s3.substr(7) = " << s3.substr(7) << endl;

    // 查找
    cout << "\n查找 'C++' 的位置：" << s3.find("C++") << endl;
    cout << "查找 'Python' 的位置：" << s3.find("Python")
         << "（string::npos = " << string::npos << " 表示没找到）" << endl;

    // 替换
    string s4 = s3;
    s4.replace(7, 3, "World");
    cout << "替换后：" << s4 << endl;

    // 插入和删除
    s4.insert(5, ", beautiful");
    cout << "插入后：" << s4 << endl;
    s4.erase(0, 7);
    cout << "删除前 7 个字符后：" << s4 << endl;

    // 比较
    cout << "\ns1 比较 s2：" << (s1 == s2 ? "相等" : "不相等") << endl;
    cout << "s1 比较 \"Hello\"：" << (s1 == "Hello" ? "相等" : "不相等") << endl;

    // 转换为 C 风格字符串
    const char* c_str = s1.c_str();
    cout << "\ns1.c_str() = " << c_str << "（const char* 类型）" << endl;

    // 数字与字符串转换（C++11）
    string num_str = to_string(12345);
    cout << "to_string(12345) = " << num_str << endl;
    int num_val = stoi("42");
    cout << "stoi(\"42\") = " << num_val << endl;
    double d_val = stod("3.14");
    cout << "stod(\"3.14\") = " << d_val << endl;


    // ---------- 7. 字符数组与指针的区别 ----------
    cout << "\n========== 字符数组 vs 字符指针 ==========" << endl;

    char arr_str[] = "Hello";  // 字符数组，内容存储在栈上，可修改
    const char* ptr_str = "Hello";  // 字符串常量，存储在只读数据段

    cout << "arr_str = " << arr_str << "（可修改）" << endl;
    cout << "ptr_str = " << ptr_str << "（只读）" << endl;

    arr_str[0] = 'h';  // 可以修改
    cout << "修改后 arr_str = " << arr_str << endl;
    // ptr_str[0] = 'h';  // 错误：尝试修改只读内存，会导致崩溃


    // ---------- 安全小贴士 ----------
    cout << "\n========== 安全小贴士 ==========" << endl;
    cout << "1. strcpy、gets、sprintf 等函数不检查边界，容易导致缓冲区溢出。" << endl;
    cout << "2. 数组越界是 C/C++ 中最常见的漏洞来源之一。" << endl;
    cout << "3. 字符串常量存储在只读内存区，修改会导致段错误。" << endl;
    cout << "4. C++ 的 std::string 比 C 风格字符串更安全，推荐使用。" << endl;
    cout << "5. 指针错误（空指针解引用、野指针）是常见崩溃原因。" << endl;

    return 0;
}
