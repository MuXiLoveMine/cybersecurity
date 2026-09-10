// ============================================================
// 07_stl_string.cpp —— string 字符串操作
// 编译命令：g++ -std=c++11 07_stl_string.cpp -o 07_stl_string
// 运行命令：./07_stl_string（Linux/Mac） 或 07_stl_string.exe（Windows）
// ============================================================

#include <iostream>
#include <string>
#include <algorithm>  // 算法（reverse 等）
#include <sstream>    // 字符串流
#include <vector>
using namespace std;

int main() {
    // ---------- 1. string 的创建与初始化 ----------
    cout << "========== string 的创建与初始化 ==========" << endl;

    string s1;                    // 空字符串
    string s2("Hello");           // 用 C 风格字符串初始化
    string s3 = "World";          // 赋值初始化
    string s4(5, 'A');            // 5 个 'A' 组成的字符串
    string s5(s2);                // 拷贝构造
    string s6(s2, 1, 3);          // 从 s2 的第 1 个位置开始，取 3 个字符
    string s7 = "Hello, World!";  // 列表初始化

    cout << "s1（空）：\"" << s1 << "\"" << endl;
    cout << "s2：\"" << s2 << "\"" << endl;
    cout << "s3：\"" << s3 << "\"" << endl;
    cout << "s4（5个'A'）：\"" << s4 << "\"" << endl;
    cout << "s5（拷贝 s2）：\"" << s5 << "\"" << endl;
    cout << "s6（s2 第1位开始3个字符）：\"" << s6 << "\"" << endl;
    cout << "s7：\"" << s7 << "\"" << endl;


    // ---------- 2. 基本属性 ----------
    cout << "\n========== 基本属性 ==========" << endl;

    string s = "Hello, C++ World!";
    cout << "字符串：\"" << s << "\"" << endl;
    cout << "长度（length()）：" << s.length() << endl;
    cout << "大小（size()）：" << s.size() << "（与 length 相同）" << endl;
    cout << "是否为空（empty()）：" << (s.empty() ? "是" : "否") << endl;
    cout << "容量（capacity()）：" << s.capacity() << endl;
    cout << "最大大小（max_size()）：" << s.max_size() << endl;

    string empty_str;
    cout << "\n空字符串 empty()：" << (empty_str.empty() ? "true（空）" : "false") << endl;


    // ---------- 3. 字符访问 ----------
    cout << "\n========== 字符访问 ==========" << endl;

    string str = "Hello, World!";
    cout << "字符串：\"" << str << "\"" << endl;

    cout << "str[0] = '" << str[0] << "'（下标访问，不检查边界）" << endl;
    cout << "str[7] = '" << str[7] << "'" << endl;
    cout << "str.at(4) = '" << str.at(4) << "'（at() 访问，带边界检查）" << endl;
    cout << "str.front() = '" << str.front() << "'（第一个字符，C++11）" << endl;
    cout << "str.back() = '" << str.back() << "'（最后一个字符，C++11）" << endl;

    // 修改字符
    str[0] = 'h';
    cout << "修改 str[0] = 'h' 后：\"" << str << "\"" << endl;

    // at() 越界会抛异常
    try {
        str.at(100);
    } catch (const out_of_range& e) {
        cout << "at(100) 越界异常：" << e.what() << endl;
    }


    // ---------- 4. 字符串拼接 ----------
    cout << "\n========== 字符串拼接 ==========" << endl;

    string a = "Hello";
    string b = "World";

    string c = a + ", " + b + "!";
    cout << "a + \", \" + b + \"!\" = \"" << c << "\"" << endl;

    // append 方法
    string d = "学习";
    d.append(" C++");
    d.append(" 编程", 2);  // 追加前 2 个字符
    cout << "d append 后：\"" << d << "\"" << endl;

    // += 运算符
    string e = "你好";
    e += "，世界";
    e += '!';
    cout << "e += 后：\"" << e << "\"" << endl;

    // push_back（添加单个字符）
    string f = "abc";
    f.push_back('d');
    cout << "f push_back('d') 后：\"" << f << "\"" << endl;


    // ---------- 5. 子串与查找 ----------
    cout << "\n========== 子串与查找 ==========" << endl;

    string text = "Hello, World! Hello, C++!";
    cout << "原字符串：\"" << text << "\"" << endl;

    // substr：获取子串
    cout << "\nsubstr(0, 5) = \"" << text.substr(0, 5) << "\"（前 5 个字符）" << endl;
    cout << "substr(7, 5) = \"" << text.substr(7, 5) << "\"（第 7 位开始 5 个字符）" << endl;
    cout << "substr(7) = \"" << text.substr(7) << "\"（第 7 位到末尾）" << endl;

    // find：查找子串
    cout << "\nfind(\"World\") = " << text.find("World") << "（第一次出现的位置）" << endl;
    cout << "find(\"Hello\") = " << text.find("Hello") << endl;
    cout << "find(\"Hello\", 5) = " << text.find("Hello", 5) << "（从第 5 位开始找）" << endl;
    cout << "find(\"Python\") = " << text.find("Python")
         << "（string::npos = " << string::npos << " 表示未找到）" << endl;

    // rfind：从后往前找
    cout << "\nrfind(\"Hello\") = " << text.rfind("Hello") << "（最后一次出现的位置）" << endl;

    // find_first_of / find_last_of
    cout << "find_first_of(\"aeiou\") = " << text.find_first_of("aeiou")
         << "（第一个元音字母位置）" << endl;
    cout << "find_last_of(\"aeiou\") = " << text.find_last_of("aeiou")
         << "（最后一个元音字母位置）" << endl;

    // 判断是否包含子串（C++23 有 contains，这里用 find 实现）
    if (text.find("C++") != string::npos) {
        cout << "\n字符串中包含 \"C++\"" << endl;
    }


    // ---------- 6. 替换、插入、删除 ----------
    cout << "\n========== 替换、插入、删除 ==========" << endl;

    string s_op = "Hello, World!";
    cout << "原始：\"" << s_op << "\"" << endl;

    // replace：替换
    s_op.replace(7, 5, "C++");  // 从第 7 位开始，5 个字符替换为 "C++"
    cout << "replace(7, 5, \"C++\")：\"" << s_op << "\"" << endl;

    // insert：插入
    s_op.insert(5, ", beautiful");
    cout << "insert(5, \", beautiful\")：\"" << s_op << "\"" << endl;

    // erase：删除
    s_op.erase(5, 11);  // 从第 5 位开始删除 11 个字符
    cout << "erase(5, 11)：\"" << s_op << "\"" << endl;

    s_op.erase(s_op.begin() + 5);  // 删除第 5 个字符
    cout << "erase 第 5 个字符：\"" << s_op << "\"" << endl;

    // pop_back：删除最后一个字符（C++11）
    s_op.pop_back();
    cout << "pop_back()：\"" << s_op << "\"" << endl;

    // clear：清空
    s_op.clear();
    cout << "clear() 后：\"" << s_op << "\"（空）" << endl;


    // ---------- 7. 比较 ----------
    cout << "\n========== 字符串比较 ==========" << endl;

    string x = "apple";
    string y = "banana";
    string z = "apple";

    cout << "x = \"" << x << "\", y = \"" << y << "\", z = \"" << z << "\"" << endl;

    // 关系运算符
    cout << "\nx == z：" << (x == z ? "相等" : "不相等") << endl;
    cout << "x != y：" << (x != y ? "不相等" : "相等") << endl;
    cout << "x < y：" << (x < y ? "是（按字典序）" : "否") << endl;
    cout << "x > y：" << (x > y ? "是" : "否") << endl;

    // compare 方法
    int cmp = x.compare(y);
    cout << "\nx.compare(y) = " << cmp << "（负数表示 x < y）" << endl;
    cout << "x.compare(z) = " << x.compare(z) << "（0 表示相等）" << endl;
    cout << "y.compare(x) = " << y.compare(x) << "（正数表示 y > x）" << endl;

    // 比较子串
    cout << "x.compare(0, 3, \"app\") = " << x.compare(0, 3, "app")
         << "（比较前 3 个字符）" << endl;


    // ---------- 8. 转换 ----------
    cout << "\n========== 类型转换 ==========" << endl;

    // string 转 C 风格字符串
    string cpp_str = "Hello";
    const char* c_str = cpp_str.c_str();
    cout << "string -> const char*：\"" << c_str << "\"" << endl;

    // 数字转 string（C++11）
    string int_str = to_string(12345);
    string float_str = to_string(3.14);
    cout << "to_string(12345) = \"" << int_str << "\"" << endl;
    cout << "to_string(3.14) = \"" << float_str << "\"" << endl;

    // string 转数字（C++11）
    string num_str = "42";
    int i_val = stoi(num_str);       // string to int
    long l_val = stol(num_str);      // string to long
    double d_val = stod("3.14159");  // string to double
    cout << "stoi(\"42\") = " << i_val << endl;
    cout << "stol(\"42\") = " << l_val << endl;
    cout << "stod(\"3.14159\") = " << d_val << endl;

    // 字符串流（更灵活的转换）
    stringstream ss;
    ss << "年龄：" << 25 << "，分数：" << 95.5;
    string result = ss.str();
    cout << "\nstringstream 拼接：\"" << result << "\"" << endl;

    // 从字符串流读取
    string data = "10 20 30";
    stringstream ss_in(data);
    int a1, a2, a3;
    ss_in >> a1 >> a2 >> a3;
    cout << "从 \"10 20 30\" 解析：" << a1 << ", " << a2 << ", " << a3 << endl;


    // ---------- 9. 其他操作 ----------
    cout << "\n========== 其他操作 ==========" << endl;

    string s_other = "Hello, World!";
    cout << "原字符串：\"" << s_other << "\"" << endl;

    // 反转
    reverse(s_other.begin(), s_other.end());
    cout << "reverse 反转后：\"" << s_other << "\"" << endl;

    reverse(s_other.begin(), s_other.end());  // 转回来

    // 大小写转换（需要逐个字符处理）
    string upper_str = s_other;
    for (char& ch : upper_str) {
        ch = toupper(ch);
    }
    cout << "转大写：\"" << upper_str << "\"" << endl;

    string lower_str = s_other;
    for (char& ch : lower_str) {
        ch = tolower(ch);
    }
    cout << "转小写：\"" << lower_str << "\"" << endl;

    // 判断前缀/后缀（C++20 有 starts_with/ends_with，这里手动实现）
    string url = "https://www.example.com";
    cout << "\nurl = \"" << url << "\"" << endl;
    if (url.substr(0, 8) == "https://") {
        cout << "URL 以 https:// 开头" << endl;
    }
    if (url.substr(url.size() - 4) == ".com") {
        cout << "URL 以 .com 结尾" << endl;
    }

    // 交换
    string s_a = "AAA", s_b = "BBB";
    cout << "\n交换前：s_a = \"" << s_a << "\", s_b = \"" << s_b << "\"" << endl;
    s_a.swap(s_b);
    cout << "swap 后：s_a = \"" << s_a << "\", s_b = \"" << s_b << "\"" << endl;


    // ---------- 10. 实战：分割字符串 ----------
    cout << "\n========== 实战：分割字符串 ==========" << endl;

    string csv = "apple,banana,orange,grape,mango";
    cout << "原始 CSV：\"" << csv << "\"" << endl;

    vector<string> fruits;
    stringstream ss_csv(csv);
    string fruit;
    while (getline(ss_csv, fruit, ',')) {
        fruits.push_back(fruit);
    }

    cout << "分割结果：" << endl;
    for (size_t i = 0; i < fruits.size(); i++) {
        cout << "  [" << i << "] = \"" << fruits[i] << "\"" << endl;
    }


    // ---------- 安全小贴士 ----------
    cout << "\n========== 安全小贴士 ==========" << endl;
    cout << "1. std::string 自动管理内存，比 char[] 更安全。" << endl;
    cout << "2. 但 .c_str() 返回的指针在 string 修改后可能失效。" << endl;
    cout << "3. 字符串拼接可能导致内存重新分配，迭代器会失效。" << endl;
    cout << "4. stoi/stod 等函数在解析失败时会抛出异常，注意捕获。" << endl;
    cout << "5. 格式化字符串漏洞（printf 系列）在 C++ 中用 string 可避免。" << endl;

    return 0;
}
