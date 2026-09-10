// ============================================================
// 08_regex.cpp —— C++11 正则表达式
// 编译命令：g++ -std=c++11 08_regex.cpp -o 08_regex
// 运行命令：./08_regex（Linux/Mac） 或 08_regex.exe（Windows）
// ============================================================

#include <iostream>
#include <string>
#include <regex>   // 正则表达式头文件（C++11）
#include <vector>
using namespace std;

int main() {
    // ---------- 1. 正则表达式基础 ----------
    cout << "========== 正则表达式基础 ==========" << endl;

    // regex_match：完全匹配（整个字符串必须匹配）
    string s1 = "12345";
    regex pattern1("\\d+");  // \d 匹配数字，+ 表示一个或多个

    if (regex_match(s1, pattern1)) {
        cout << "\"" << s1 << "\" 完全匹配 \\d+（全是数字）" << endl;
    }

    string s2 = "abc123";
    if (!regex_match(s2, pattern1)) {
        cout << "\"" << s2 << "\" 不匹配 \\d+（不是纯数字）" << endl;
    }

    // regex_search：搜索匹配（只要有子串匹配即可）
    cout << "\nregex_search 搜索：" << endl;
    string text = "我的电话是 13812345678，邮箱是 test@example.com";

    regex phone_pattern("1\\d{10}");  // 手机号：1 开头 + 10 位数字
    if (regex_search(text, phone_pattern)) {
        cout << "  文本中包含手机号" << endl;
    }

    regex email_pattern("\\w+@\\w+\\.\\w+");  // 简单邮箱匹配
    if (regex_search(text, email_pattern)) {
        cout << "  文本中包含邮箱地址" << endl;
    }


    // ---------- 2. 提取匹配内容（smatch） ----------
    cout << "\n========== 提取匹配内容（smatch） ==========" << endl;

    string text2 = "联系电话：13812345678，备用号码：15987654321";
    regex phone_pat("1\\d{10}");
    smatch match;  // 存储匹配结果

    // 查找第一个匹配
    if (regex_search(text2, match, phone_pat)) {
        cout << "找到第一个手机号：" << match.str() << endl;
        cout << "  匹配位置：" << match.position() << endl;
        cout << "  匹配长度：" << match.length() << endl;
    }

    // 捕获组（用括号分组）
    cout << "\n捕获组示例：" << endl;
    string date_str = "今天是 2024-01-15，星期一";
    regex date_pat("(\\d{4})-(\\d{2})-(\\d{2})");  // 年-月-日
    smatch date_match;

    if (regex_search(date_str, date_match, date_pat)) {
        cout << "  完整匹配：" << date_match[0] << endl;
        cout << "  年份（第 1 组）：" << date_match[1] << endl;
        cout << "  月份（第 2 组）：" << date_match[2] << endl;
        cout << "  日期（第 3 组）：" << date_match[3] << endl;
    }


    // ---------- 3. 查找所有匹配 ----------
    cout << "\n========== 查找所有匹配 ==========" << endl;

    string text3 = "邮箱列表：admin@test.com, user@example.org, info@demo.net";
    regex email_pat(R"(\w+@\w+\.\w+)");  // R"(...)" 是原始字符串，不用转义

    // 使用 sregex_iterator 迭代所有匹配
    auto begin = sregex_iterator(text3.begin(), text3.end(), email_pat);
    auto end = sregex_iterator();

    vector<string> emails;
    for (auto i = begin; i != end; ++i) {
        emails.push_back(i->str());
    }

    cout << "找到 " << emails.size() << " 个邮箱：" << endl;
    for (size_t i = 0; i < emails.size(); i++) {
        cout << "  [" << i << "] " << emails[i] << endl;
    }

    // 带捕获组的多匹配
    cout << "\n提取所有用户名和域名：" << endl;
    regex email_pat2(R"((\w+)@(\w+\.\w+))");
    auto begin2 = sregex_iterator(text3.begin(), text3.end(), email_pat2);
    for (auto i = begin2; i != sregex_iterator(); ++i) {
        cout << "  用户名：" << (*i)[1] << "，域名：" << (*i)[2] << endl;
    }


    // ---------- 4. 替换 ----------
    cout << "\n========== 正则替换 ==========" << endl;

    string text4 = "联系我们：support@company.com 或 sales@company.com";
    cout << "原始文本：" << text4 << endl;

    // 简单替换
    regex email_pat3(R"(\w+@\w+\.\w+)");
    string replaced = regex_replace(text4, email_pat3, "[邮箱已隐藏]");
    cout << "替换后：" << replaced << endl;

    // 使用捕获组进行替换
    string phone_text = "电话：13812345678";
    regex phone_pat2(R"(1(\d{2})(\d{4})(\d{4}))");
    string phone_formatted = regex_replace(phone_text, phone_pat2, "1$1****$3");
    cout << "\n手机号脱敏：" << phone_formatted << endl;

    // HTML 标签去除
    string html = "<h1>标题</h1><p>这是<strong>加粗</strong>文本</p>";
    cout << "\n原始 HTML：" << html << endl;
    regex tag_pat(R"(<[^>]+>)");
    string plain = regex_replace(html, tag_pat, "");
    cout << "去除标签后：" << plain << endl;


    // ---------- 5. 常用正则表达式模式 ----------
    cout << "\n========== 常用正则表达式模式 ==========" << endl;

    struct TestCase {
        string name;
        string pattern;
        vector<string> tests;
    };

    vector<TestCase> cases = {
        {
            "手机号码",
            "^1[3-9]\\d{9}$",
            {"13812345678", "12345678901", "13812345", "19912345678"}
        },
        {
            "邮箱地址（简单版）",
            "^\\w+@\\w+\\.\\w+$",
            {"test@example.com", "user.name@domain.com", "abc@.com", "@test.com"}
        },
        {
            "IP 地址（简单版）",
            "^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$",
            {"192.168.1.1", "10.0.0.255", "256.1.1.1", "1.2.3"}
        },
        {
            "URL（简单版）",
            "^https?://.*",
            {"http://example.com", "https://test.org/path", "ftp://file.com", "example.com"}
        },
        {
            "中文字符",
            "^[\\u4e00-\\u9fa5]+$",
            {"你好世界", "Hello你好", "123", "测试文本"}
        },
        {
            "身份证号（18位）",
            "^\\d{17}[\\dXx]$",
            {"110101199001011234", "12345678901234567X", "12345", "abcdefghijklmnopqr"}
        }
    };

    for (const auto& tc : cases) {
        cout << "\n【" << tc.name << "】 模式：" << tc.pattern << endl;
        regex pat(tc.pattern);
        for (const string& test : tc.tests) {
            bool ok = regex_match(test, pat);
            cout << "  \"" << test << "\" → " << (ok ? "✓ 匹配" : "✗ 不匹配") << endl;
        }
    }


    // ---------- 6. 正则表达式标志（flag） ----------
    cout << "\n========== 正则表达式标志 ==========" << endl;

    string text5 = "Hello World hello world HELLO WORLD";
    cout << "文本：" << text5 << endl;

    // 默认（大小写敏感）
    regex pat_normal("hello");
    int count_normal = 0;
    auto it_normal = sregex_iterator(text5.begin(), text5.end(), pat_normal);
    for (auto i = it_normal; i != sregex_iterator(); ++i) count_normal++;
    cout << "默认（大小写敏感）匹配 \"hello\" 的次数：" << count_normal << endl;

    // 忽略大小写（icase）
    regex pat_icase("hello", regex::icase);
    int count_icase = 0;
    auto it_icase = sregex_iterator(text5.begin(), text5.end(), pat_icase);
    for (auto i = it_icase; i != sregex_iterator(); ++i) count_icase++;
    cout << "icase（忽略大小写）匹配 \"hello\" 的次数：" << count_icase << endl;

    // 其他标志：
    // regex::icase   - 忽略大小写
    // regex::nosubs  - 不保存子匹配
    // regex::optimize - 优化匹配速度


    // ---------- 7. 实战：验证用户输入 ----------
    cout << "\n========== 实战：验证用户输入 ==========" << endl;

    // 验证用户名：3-16 位字母数字下划线
    string username = "user_123";
    regex username_pat("^\\w{3,16}$");
    cout << "用户名 \"" << username << "\"："
         << (regex_match(username, username_pat) ? "有效" : "无效") << endl;

    string bad_user = "ab";
    cout << "用户名 \"" << bad_user << "\"："
         << (regex_match(bad_user, username_pat) ? "有效" : "无效（太短）") << endl;

    // 验证密码：至少 8 位，包含字母和数字
    string password = "Pass1234";
    // 正向预查：至少一个字母，至少一个数字，总长度 >= 8
    regex pwd_pat("^(?=.*[A-Za-z])(?=.*\\d).{8,}$");
    cout << "密码 \"" << password << "\"："
         << (regex_match(password, pwd_pat) ? "有效" : "无效") << endl;

    string weak_pwd = "12345678";
    cout << "密码 \"" << weak_pwd << "\"："
         << (regex_match(weak_pwd, pwd_pat) ? "有效" : "无效（没有字母）") << endl;


    // ---------- 8. 正则表达式语法速查 ----------
    cout << "\n========== 正则表达式语法速查 ==========" << endl;
    cout << "字符类：" << endl;
    cout << "  \\d  - 数字 [0-9]" << endl;
    cout << "  \\D  - 非数字" << endl;
    cout << "  \\w  - 单词字符 [a-zA-Z0-9_]" << endl;
    cout << "  \\W  - 非单词字符" << endl;
    cout << "  \\s  - 空白字符（空格、制表符等）" << endl;
    cout << "  \\S  - 非空白字符" << endl;
    cout << "  .   - 任意字符（除换行）" << endl;
    cout << "\n量词：" << endl;
    cout << "  *   - 0 个或多个" << endl;
    cout << "  +   - 1 个或多个" << endl;
    cout << "  ?   - 0 个或 1 个" << endl;
    cout << "  {n} - 恰好 n 个" << endl;
    cout << "  {n,} - 至少 n 个" << endl;
    cout << "  {n,m} - n 到 m 个" << endl;
    cout << "\n位置：" << endl;
    cout << "  ^   - 字符串开头" << endl;
    cout << "  $   - 字符串结尾" << endl;
    cout << "\n分组与引用：" << endl;
    cout << "  ()  - 捕获组" << endl;
    cout << "  (?: ) - 非捕获组" << endl;
    cout << "  |   - 或（选择）" << endl;
    cout << "\n原始字符串字面量（C++11）：" << endl;
    cout << "  R\"(...)\"  内部的反斜杠不需要转义" << endl;
    cout << "  例如：R\"(\\d+\\.\\d+)\" 等价于 \"\\\\d+\\\\.\\\\d+\"" << endl;


    // ---------- 安全小贴士 ----------
    cout << "\n========== 安全小贴士 ==========" << endl;
    cout << "1. 正则表达式可用于输入验证，防止恶意输入（如 SQL 注入、XSS）。" << endl;
    cout << "2. 但正则表达式并非万能，复杂的验证仍需多层防护。" << endl;
    cout << "3. 编写不当的正则可能导致 ReDoS（正则表达式拒绝服务攻击）。" << endl;
    cout << "4. C++ regex 性能相对一般，高性能场景可考虑 PCRE 等库。" << endl;
    cout << "5. 原始字符串 R\"(...)\" 可以避免复杂的转义，推荐使用。" << endl;

    return 0;
}
