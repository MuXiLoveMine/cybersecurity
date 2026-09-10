// ============================================================
// 06_stl_map.cpp —— map 容器（字典操作）
// 编译命令：g++ -std=c++11 06_stl_map.cpp -o 06_stl_map
// 运行命令：./06_stl_map（Linux/Mac） 或 06_stl_map.exe（Windows）
// ============================================================

#include <iostream>
#include <map>        // map 头文件（有序字典，基于红黑树）
#include <unordered_map>  // unordered_map 头文件（哈希表）
#include <string>
#include <vector>
using namespace std;

// 辅助函数：打印 map
void print_map(const map<string, int>& m, const string& name) {
    cout << name << " = { ";
    for (const auto& pair : m) {
        cout << "\"" << pair.first << "\": " << pair.second << ", ";
    }
    cout << "}  （大小：" << m.size() << "）" << endl;
}

int main() {
    // ---------- 1. map 的创建与初始化 ----------
    cout << "========== map 的创建与初始化 ==========" << endl;

    map<string, int> m1;  // 空 map

    // 插入元素
    m1["apple"] = 3;
    m1["banana"] = 5;
    m1["orange"] = 2;
    print_map(m1, "m1");

    // 列表初始化（C++11）
    map<string, int> m2 = {
        {"red", 1},
        {"green", 2},
        {"blue", 3}
    };
    print_map(m2, "m2");

    // 注意：map 是有序的（按 key 排序），底层是红黑树
    cout << "（map 中的元素按 key 自动排序）" << endl;


    // ---------- 2. 访问元素 ----------
    cout << "\n========== 访问元素 ==========" << endl;

    map<string, int> scores = {
        {"张三", 85},
        {"李四", 92},
        {"王五", 78},
        {"赵六", 95}
    };
    print_map(scores, "scores");

    // 使用 [] 访问
    cout << "scores[\"张三\"] = " << scores["张三"] << endl;
    cout << "scores[\"李四\"] = " << scores["李四"] << endl;

    // 注意：如果 key 不存在，[] 会自动插入默认值（int 为 0）
    cout << "scores[\"无名氏\"] = " << scores["无名氏"] << "（key 不存在时会自动插入）" << endl;
    print_map(scores, "scores");

    // 使用 at() 访问（带边界检查，key 不存在会抛异常）
    try {
        cout << "scores.at(\"王五\") = " << scores.at("王五") << endl;
        cout << "scores.at(\"不存在的人\") = " << scores.at("不存在的人") << endl;
    } catch (const out_of_range& e) {
        cout << "at() 异常：key 不存在 - " << e.what() << endl;
    }


    // ---------- 3. 插入元素 ----------
    cout << "\n========== 插入元素 ==========" << endl;

    map<string, int> m_ins;
    cout << "初始："; print_map(m_ins, "m_ins");

    // 方式 1：[] 运算符
    m_ins["a"] = 1;
    m_ins["b"] = 2;
    cout << "用 [] 插入 a, b 后："; print_map(m_ins, "m_ins");

    // 方式 2：insert 函数
    m_ins.insert(pair<string, int>("c", 3));
    m_ins.insert(make_pair("d", 4));  // 更常用
    cout << "insert 插入 c, d 后："; print_map(m_ins, "m_ins");

    // insert 不会覆盖已有的 key
    auto result = m_ins.insert(make_pair("a", 100));
    cout << "insert (\"a\", 100)：";
    if (result.second) {
        cout << "插入成功，新值为 " << result.first->second << endl;
    } else {
        cout << "插入失败，key 已存在，原值为 " << result.first->second << endl;
    }
    print_map(m_ins, "m_ins");


    // ---------- 4. 删除元素 ----------
    cout << "\n========== 删除元素 ==========" << endl;

    map<string, int> m_del = {
        {"one", 1}, {"two", 2}, {"three", 3},
        {"four", 4}, {"five", 5}
    };
    print_map(m_del, "m_del");

    // 按 key 删除
    size_t removed = m_del.erase("three");
    cout << "erase(\"three\") 删除了 " << removed << " 个元素" << endl;
    print_map(m_del, "m_del");

    // 按迭代器删除
    auto it = m_del.find("two");
    if (it != m_del.end()) {
        m_del.erase(it);
        cout << "erase 迭代器删除 two 后：";
    }
    print_map(m_del, "m_del");

    // 删除范围 [first, last)
    auto start = m_del.find("four");
    m_del.erase(start, m_del.end());
    cout << "erase 从 four 到末尾：";
    print_map(m_del, "m_del");

    // 清空
    m_del.clear();
    cout << "clear 后："; print_map(m_del, "m_del");
    cout << "m_del.empty() = " << (m_del.empty() ? "true（空）" : "false") << endl;


    // ---------- 5. 查找元素 ----------
    cout << "\n========== 查找元素 ==========" << endl;

    map<string, int> m_find = {
        {"CPU", 10}, {"内存", 20}, {"硬盘", 15},
        {"显卡", 8}, {"主板", 12}
    };
    print_map(m_find, "m_find");

    // find 函数：返回迭代器
    auto it_find = m_find.find("内存");
    if (it_find != m_find.end()) {
        cout << "find 找到 \"内存\"，值为：" << it_find->second << endl;
    } else {
        cout << "find 没有找到 \"内存\"" << endl;
    }

    it_find = m_find.find("显示器");
    if (it_find != m_find.end()) {
        cout << "find 找到 \"显示器\"，值为：" << it_find->second << endl;
    } else {
        cout << "find 没有找到 \"显示器\"" << endl;
    }

    // count 函数：返回 key 出现的次数（map 中只能是 0 或 1）
    cout << "\ncount(\"显卡\") = " << m_find.count("显卡") << "（1 表示存在）" << endl;
    cout << "count(\"键盘\") = " << m_find.count("键盘") << "（0 表示不存在）" << endl;

    // lower_bound 和 upper_bound
    auto lower = m_find.lower_bound("显卡");  // 第一个 >= "显卡" 的元素
    auto upper = m_find.upper_bound("显卡");  // 第一个 > "显卡" 的元素
    cout << "\nlower_bound(\"显卡\")：" << lower->first << " = " << lower->second << endl;
    cout << "upper_bound(\"显卡\")：" << upper->first << " = " << upper->second << endl;


    // ---------- 6. 遍历 map ----------
    cout << "\n========== 遍历 map ==========" << endl;

    map<int, string> m_trav = {
        {3, "three"}, {1, "one"}, {4, "four"}, {2, "two"}, {5, "five"}
    };

    // 方式 1：迭代器遍历
    cout << "迭代器遍历（按 key 升序）：" << endl;
    for (map<int, string>::iterator it = m_trav.begin(); it != m_trav.end(); ++it) {
        cout << "  " << it->first << " -> " << it->second << endl;
    }

    // 方式 2：范围 for 循环（C++11）
    cout << "范围 for 循环：" << endl;
    for (const auto& pair : m_trav) {
        cout << "  " << pair.first << " -> " << pair.second << endl;
    }

    // 方式 3：结构化绑定（C++17）
    cout << "结构化绑定遍历（C++17）：" << endl;
    for (const auto& [key, value] : m_trav) {
        cout << "  " << key << " -> " << value << endl;
    }

    // 反向遍历
    cout << "反向遍历（按 key 降序）：" << endl;
    for (auto it = m_trav.rbegin(); it != m_trav.rend(); ++it) {
        cout << "  " << it->first << " -> " << it->second << endl;
    }


    // ---------- 7. map 的大小与容量 ----------
    cout << "\n========== map 的大小与容量 ==========" << endl;

    map<string, int> m_size = {{"a", 1}, {"b", 2}, {"c", 3}};
    cout << "size() = " << m_size.size() << "（元素个数）" << endl;
    cout << "empty() = " << (m_size.empty() ? "true" : "false") << endl;
    cout << "max_size() = " << m_size.max_size() << "（最大可能元素数）" << endl;


    // ---------- 8. unordered_map（哈希表） ----------
    cout << "\n========== unordered_map（哈希表） ==========" << endl;

    // unordered_map 底层是哈希表，无序，查找更快（平均 O(1)）
    unordered_map<string, int> um = {
        {"apple", 3},
        {"banana", 5},
        {"orange", 2},
        {"grape", 7}
    };

    cout << "unordered_map 元素（顺序不固定）：" << endl;
    for (const auto& pair : um) {
        cout << "  " << pair.first << " -> " << pair.second << endl;
    }

    cout << "um[\"banana\"] = " << um["banana"] << endl;
    cout << "um.count(\"apple\") = " << um.count("apple") << endl;

    cout << "\nmap vs unordered_map：" << endl;
    cout << "  map          - 有序（红黑树），O(log n) 查找" << endl;
    cout << "  unordered_map - 无序（哈希表），平均 O(1) 查找" << endl;


    // ---------- 9. 实际应用：统计词频 ----------
    cout << "\n========== 实战：统计词频 ==========" << endl;

    vector<string> words = {
        "apple", "banana", "apple", "orange", "banana",
        "apple", "grape", "banana", "orange", "apple"
    };

    map<string, int> freq;
    for (const string& word : words) {
        freq[word]++;  // 如果 key 不存在，默认值为 0，然后 +1
    }

    cout << "词频统计结果：" << endl;
    for (const auto& pair : freq) {
        cout << "  " << pair.first << ": ";
        for (int i = 0; i < pair.second; i++) cout << "■";
        cout << " (" << pair.second << ")" << endl;
    }


    // ---------- 安全小贴士 ----------
    cout << "\n========== 安全小贴士 ==========" << endl;
    cout << "1. map 的 [] 运算符在 key 不存在时会自动插入，可能导致意外行为。" << endl;
    cout << "2. unordered_map 可能遭受哈希碰撞攻击（DoS）。" << endl;
    cout << "3. map 的迭代器在插入/删除时，其他元素的迭代器仍然有效。" << endl;
    cout << "4. map 和 set 底层都是红黑树，逆向分析中常见相关结构。" << endl;

    return 0;
}
