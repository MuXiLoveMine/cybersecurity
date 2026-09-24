# vector_string

> **分类**：STL容器
> **说明**：C++ 标准模板库常用容器

---

## 语法

```cpp
vector<Type> vec;\nstring str;\nmap<Key,Value> mp;
```

## 常用容器

vector / string / map / unordered_map / set / unordered_set / list / deque / queue / stack / array

## 常用算法

sort / find / count / for_each / transform / reverse / unique / lower_bound / upper_bound

## 示例代码

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <unordered_map>
#include <set>
#include <algorithm>
#include <iterator>
using namespace std;

int main() {
    // ===== vector =====
    vector<int> vec = {1, 2, 3, 4, 5};

    // 添加
    vec.push_back(6);
    vec.emplace_back(7);  // C++11，原地构造
    vec.insert(vec.begin() + 2, 100);  // 在索引2插入

    // 访问
    cout << vec[0] << endl;      // 0号元素
    cout << vec.at(1) << endl;   // 带边界检查
    cout << vec.front() << endl; // 第一个
    cout << vec.back() << endl;  // 最后一个
    cout << vec.size() << endl;  // 大小

    // 删除
    vec.pop_back();              // 删除最后一个
    vec.erase(vec.begin() + 2);  // 删除指定位置
    vec.clear();                 // 清空

    // 遍历
    for (int i = 0; i < vec.size(); i++) cout << vec[i] << " ";
    for (int num : vec) cout << num << " ";  // 范围 for (C++11)
    for (auto it = vec.begin(); it != vec.end(); ++it) cout << *it << " ";

    // ===== string =====
    string str = "Hello, World!";
    cout << str.length() << endl;
    cout << str.substr(0, 5) << endl;  // "Hello"
    cout << str.find("World") << endl; // 7
    str += " C++";                      // 拼接
    str.append("!!");                   // 追加
    str.replace(0, 5, "Hi");            // 替换

    // ===== map（有序） =====
    map<string, int> scores;
    scores["Alice"] = 95;
    scores["Bob"] = 88;
    scores["Charlie"] = 92;

    for (auto& pair : scores) {
        cout << pair.first << ": " << pair.second << endl;
    }

    // 查找
    auto it = scores.find("Bob");
    if (it != scores.end()) {
        cout << "Bob 的分数: " << it->second << endl;
    }

    // ===== unordered_map（哈希表，更快） =====
    unordered_map<string, int> umap;
    umap["apple"] = 10;
    umap["banana"] = 20;

    // ===== set =====
    set<int> s = {3, 1, 4, 1, 5, 9, 2, 6};
    // 自动排序，无重复

    // ===== 算法 =====
    vector<int> nums = {5, 2, 8, 1, 9, 3};

    sort(nums.begin(), nums.end());                    // 排序
    sort(nums.rbegin(), nums.rend());                  // 降序
    reverse(nums.begin(), nums.end());                 // 反转

    auto pos = find(nums.begin(), nums.end(), 8);      // 查找
    int cnt = count(nums.begin(), nums.end(), 3);      // 计数

    // for_each
    for_each(nums.begin(), nums.end(), [](int n) {
        cout << n << " ";
    });

    // transform
    vector<int> squares;
    transform(nums.begin(), nums.end(), back_inserter(squares),
              [](int n) { return n * n; });

    return 0;
}
```
