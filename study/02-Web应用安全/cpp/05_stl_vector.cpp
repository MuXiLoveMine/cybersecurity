// ============================================================
// 05_stl_vector.cpp —— vector 容器（列表操作）
// 编译命令：g++ -std=c++11 05_stl_vector.cpp -o 05_stl_vector
// 运行命令：./05_stl_vector（Linux/Mac） 或 05_stl_vector.exe（Windows）
// ============================================================

#include <iostream>
#include <vector>     // vector 头文件
#include <algorithm>  // 算法头文件（sort 等）
using namespace std;

// 辅助函数：打印 vector
void print_vector(const vector<int>& v, const string& name) {
    cout << name << " = [";
    for (size_t i = 0; i < v.size(); i++) {
        cout << v[i];
        if (i < v.size() - 1) cout << ", ";
    }
    cout << "]  （大小：" << v.size() << "，容量：" << v.capacity() << "）" << endl;
}

int main() {
    // ---------- 1. vector 的创建与初始化 ----------
    cout << "========== vector 的创建与初始化 ==========" << endl;

    vector<int> v1;                // 空 vector
    vector<int> v2(5);             // 5 个元素，默认初始化为 0
    vector<int> v3(5, 10);         // 5 个元素，值都是 10
    vector<int> v4 = {1, 2, 3, 4, 5};  // 列表初始化（C++11）

    cout << "v1（空）："; print_vector(v1, "v1");
    cout << "v2（5个0）："; print_vector(v2, "v2");
    cout << "v3（5个10）："; print_vector(v3, "v3");
    cout << "v4（列表初始化）："; print_vector(v4, "v4");

    // 用数组初始化
    int arr[] = {10, 20, 30, 40, 50};
    vector<int> v5(arr, arr + 5);
    cout << "v5（从数组初始化）："; print_vector(v5, "v5");


    // ---------- 2. 元素访问 ----------
    cout << "\n========== 元素访问 ==========" << endl;

    vector<int> v = {10, 20, 30, 40, 50};
    print_vector(v, "v");

    cout << "v[0] = " << v[0] << "（下标访问，不检查边界）" << endl;
    cout << "v[2] = " << v[2] << endl;
    cout << "v.at(3) = " << v.at(3) << "（at() 访问，带边界检查）" << endl;
    cout << "v.front() = " << v.front() << "（第一个元素）" << endl;
    cout << "v.back() = " << v.back() << "（最后一个元素）" << endl;

    // at() 越界会抛出异常，[] 越界是未定义行为
    try {
        v.at(100);  // 越界，会抛出 out_of_range 异常
    } catch (const out_of_range& e) {
        cout << "at(100) 越界异常：" << e.what() << endl;
    }


    // ---------- 3. 添加元素 ----------
    cout << "\n========== 添加元素 ==========" << endl;

    vector<int> v_add;
    cout << "初始："; print_vector(v_add, "v_add");

    // push_back：在末尾添加
    v_add.push_back(10);
    v_add.push_back(20);
    v_add.push_back(30);
    cout << "push_back 10, 20, 30 后："; print_vector(v_add, "v_add");

    // insert：在指定位置插入
    v_add.insert(v_add.begin(), 5);          // 开头插入 5
    cout << "insert 开头插入 5 后："; print_vector(v_add, "v_add");

    v_add.insert(v_add.begin() + 2, 15);     // 第 3 个位置插入 15
    cout << "insert 位置 2 插入 15 后："; print_vector(v_add, "v_add");

    v_add.insert(v_add.end(), 3, 100);       // 末尾插入 3 个 100
    cout << "insert 末尾插入 3 个 100 后："; print_vector(v_add, "v_add");


    // ---------- 4. 删除元素 ----------
    cout << "\n========== 删除元素 ==========" << endl;

    vector<int> v_del = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    cout << "初始："; print_vector(v_del, "v_del");

    // pop_back：删除末尾元素
    v_del.pop_back();
    cout << "pop_back 后："; print_vector(v_del, "v_del");

    // erase：删除指定位置元素
    v_del.erase(v_del.begin());   // 删除第一个
    cout << "erase 第一个元素后："; print_vector(v_del, "v_del");

    v_del.erase(v_del.begin() + 2);  // 删除第 3 个
    cout << "erase 第 3 个元素后："; print_vector(v_del, "v_del");

    // erase：删除范围 [first, last)
    v_del.erase(v_del.begin() + 1, v_del.begin() + 4);
    cout << "erase 范围 [1, 4) 后："; print_vector(v_del, "v_del");

    // clear：清空所有元素
    v_del.clear();
    cout << "clear 后："; print_vector(v_del, "v_del");
    cout << "v_del.empty() = " << (v_del.empty() ? "true（空）" : "false") << endl;


    // ---------- 5. 大小与容量 ----------
    cout << "\n========== 大小与容量 ==========" << endl;

    vector<int> v_size;
    cout << "初始状态：" << endl;
    cout << "  size = " << v_size.size() << "（元素个数）" << endl;
    cout << "  capacity = " << v_size.capacity() << "（容量）" << endl;
    cout << "  empty = " << (v_size.empty() ? "true" : "false") << endl;

    cout << "\n逐步添加元素，观察容量变化：" << endl;
    for (int i = 0; i < 20; i++) {
        v_size.push_back(i);
        if (v_size.size() == 1 || v_size.size() == 2 || v_size.size() == 4 ||
            v_size.size() == 8 || v_size.size() == 16 || v_size.size() == 20) {
            cout << "  size = " << v_size.size()
                 << ", capacity = " << v_size.capacity() << endl;
        }
    }

    // reserve：预分配容量
    v_size.reserve(100);
    cout << "\nreserve(100) 后：" << endl;
    cout << "  size = " << v_size.size() << endl;
    cout << "  capacity = " << v_size.capacity() << endl;

    // resize：改变大小
    v_size.resize(10);
    cout << "\nresize(10) 后："; print_vector(v_size, "v_size");


    // ---------- 6. 遍历 vector ----------
    cout << "\n========== 遍历 vector ==========" << endl;

    vector<int> v_trav = {10, 20, 30, 40, 50};

    // 方式 1：下标遍历
    cout << "下标遍历：";
    for (size_t i = 0; i < v_trav.size(); i++) {
        cout << v_trav[i] << " ";
    }
    cout << endl;

    // 方式 2：迭代器遍历
    cout << "迭代器遍历：";
    for (vector<int>::iterator it = v_trav.begin(); it != v_trav.end(); ++it) {
        cout << *it << " ";
    }
    cout << endl;

    // 方式 3：auto 迭代器（C++11）
    cout << "auto 迭代器：";
    for (auto it = v_trav.begin(); it != v_trav.end(); ++it) {
        cout << *it << " ";
    }
    cout << endl;

    // 方式 4：范围 for 循环（C++11）
    cout << "范围 for 循环：";
    for (int x : v_trav) {
        cout << x << " ";
    }
    cout << endl;

    // 方式 5：反向遍历
    cout << "反向遍历：";
    for (auto it = v_trav.rbegin(); it != v_trav.rend(); ++it) {
        cout << *it << " ";
    }
    cout << endl;


    // ---------- 7. vector 与算法 ----------
    cout << "\n========== vector 与 STL 算法 ==========" << endl;

    vector<int> v_alg = {5, 2, 8, 1, 9, 3, 7, 4, 6};
    print_vector(v_alg, "v_alg");

    // 排序
    sort(v_alg.begin(), v_alg.end());
    cout << "sort 升序排序后："; print_vector(v_alg, "v_alg");

    // 降序排序
    sort(v_alg.begin(), v_alg.end(), greater<int>());
    cout << "sort 降序排序后："; print_vector(v_alg, "v_alg");

    // 反转
    reverse(v_alg.begin(), v_alg.end());
    cout << "reverse 反转后："; print_vector(v_alg, "v_alg");

    // 查找
    auto it = find(v_alg.begin(), v_alg.end(), 7);
    if (it != v_alg.end()) {
        cout << "find 找到 7，下标为：" << (it - v_alg.begin()) << endl;
    }

    // 计数
    int cnt = count(v_alg.begin(), v_alg.end(), 5);
    cout << "count 统计 5 出现的次数：" << cnt << endl;

    // 最大值和最小值
    int max_val = *max_element(v_alg.begin(), v_alg.end());
    int min_val = *min_element(v_alg.begin(), v_alg.end());
    cout << "最大值：" << max_val << "，最小值：" << min_val << endl;


    // ---------- 8. 二维 vector ----------
    cout << "\n========== 二维 vector ==========" << endl;

    // 创建 3 行 4 列的二维 vector
    vector<vector<int>> matrix(3, vector<int>(4, 0));

    // 赋值
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 4; j++) {
            matrix[i][j] = i * 10 + j;
        }
    }

    // 遍历
    cout << "3x4 二维 vector：" << endl;
    for (auto& row : matrix) {
        for (int val : row) {
            cout << val << "\t";
        }
        cout << endl;
    }

    // 每行长度可以不同（不规则数组）
    vector<vector<int>> jagged = {
        {1, 2, 3},
        {4, 5},
        {6, 7, 8, 9}
    };
    cout << "\n不规则二维 vector：" << endl;
    for (size_t i = 0; i < jagged.size(); i++) {
        cout << "第 " << i << " 行（" << jagged[i].size() << " 个元素）：";
        for (int val : jagged[i]) {
            cout << val << " ";
        }
        cout << endl;
    }


    // ---------- 安全小贴士 ----------
    cout << "\n========== 安全小贴士 ==========" << endl;
    cout << "1. vector 自动管理内存，比原生数组更安全。" << endl;
    cout << "2. 使用 at() 而非 [] 可以获得边界检查，但性能略低。" << endl;
    cout << "3. vector 的迭代器在添加/删除元素后可能失效。" << endl;
    cout << "4. reserve() 预分配可以避免频繁扩容，提高性能。" << endl;
    cout << "5. 在逆向分析中，vector 的内部结构（三个指针）是常见考点。" << endl;

    return 0;
}
