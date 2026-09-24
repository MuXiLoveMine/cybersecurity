// ============================================================
// 02_control_flow.cpp —— if/else、for、while、switch
// 编译命令：g++ 02_control_flow.cpp -o 02_control_flow
// 运行命令：./02_control_flow（Linux/Mac） 或 02_control_flow.exe（Windows）
// ============================================================

#include <iostream>
using namespace std;

int main() {
    // ---------- 1. if / else ----------
    cout << "========== if / else ==========" << endl;

    int score = 85;
    cout << "分数：" << score << endl;

    if (score >= 90) {
        cout << "评级：优秀（A）" << endl;
    } else if (score >= 80) {
        cout << "评级：良好（B）" << endl;
    } else if (score >= 60) {
        cout << "评级：及格（C）" << endl;
    } else {
        cout << "评级：不及格（D）" << endl;
    }

    // 嵌套 if
    int num = 15;
    cout << "\n数字：" << num << endl;
    if (num > 0) {
        cout << "正数";
        if (num % 2 == 0) {
            cout << "且是偶数" << endl;
        } else {
            cout << "且是奇数" << endl;
        }
    } else if (num < 0) {
        cout << "负数" << endl;
    } else {
        cout << "零" << endl;
    }

    // 逻辑运算符组合条件
    int age = 20;
    bool has_id = true;
    cout << "\n年龄：" << age << "，有身份证：" << (has_id ? "是" : "否") << endl;
    if (age >= 18 && has_id) {
        cout << "可以进入网吧" << endl;
    } else {
        cout << "不能进入网吧" << endl;
    }


    // ---------- 2. for 循环 ----------
    cout << "\n========== for 循环 ==========" << endl;

    // 基本 for 循环
    cout << "1 到 10 的和：";
    int sum = 0;
    for (int i = 1; i <= 10; i++) {
        sum += i;
    }
    cout << sum << endl;

    // 打印乘法表
    cout << "\n九九乘法表（5x5）：" << endl;
    for (int i = 1; i <= 5; i++) {
        for (int j = 1; j <= i; j++) {
            cout << j << "x" << i << "=" << (i*j) << "\t";
        }
        cout << endl;
    }

    // 从大到小循环
    cout << "\n倒计时：";
    for (int i = 10; i >= 1; i--) {
        cout << i << " ";
    }
    cout << "发射！" << endl;

    // 逗号表达式
    cout << "\n逗号表达式循环：";
    for (int i = 0, j = 10; i < j; i++, j--) {
        cout << "(" << i << "," << j << ") ";
    }
    cout << endl;

    // 范围 for 循环（C++11）
    cout << "\n范围 for 循环遍历数组：";
    int arr[] = {10, 20, 30, 40, 50};
    for (int x : arr) {
        cout << x << " ";
    }
    cout << endl;


    // ---------- 3. while 循环 ----------
    cout << "\n========== while 循环 ==========" << endl;

    // 计算 1+2+3+...+100
    int i = 1, total = 0;
    while (i <= 100) {
        total += i;
        i++;
    }
    cout << "1 到 100 的和：" << total << endl;

    // 猜数字概念示例
    cout << "\n猜数字游戏（3 次机会）：" << endl;
    int target = 42;
    int guess;
    int chances = 3;
    bool found = false;

    // 这里用固定值演示 while 的使用
    int guesses[] = {30, 50, 42};
    int idx = 0;
    while (chances > 0 && !found) {
        guess = guesses[idx++];
        cout << "第 " << (4 - chances) << " 次猜：" << guess;
        if (guess == target) {
            cout << " → 猜对了！" << endl;
            found = true;
        } else if (guess < target) {
            cout << " → 太小了" << endl;
        } else {
            cout << " → 太大了" << endl;
        }
        chances--;
    }
    if (!found) {
        cout << "游戏结束，答案是 " << target << endl;
    }


    // ---------- 4. do-while 循环 ----------
    cout << "\n========== do-while 循环 ==========" << endl;

    // do-while 至少执行一次
    int count = 5;
    cout << "倒计时（do-while）：";
    do {
        cout << count << " ";
        count--;
    } while (count > 0);
    cout << endl;

    // 验证至少执行一次
    int n = 0;
    do {
        cout << "即使 n=" << n << " 不满足条件，也会执行一次" << endl;
        n++;
    } while (n > 10);  // 条件一开始就不满足


    // ---------- 5. switch 语句 ----------
    cout << "\n========== switch 语句 ==========" << endl;

    int day = 3;
    cout << "星期 " << day << " 是：";
    switch (day) {
        case 1: cout << "星期一"; break;
        case 2: cout << "星期二"; break;
        case 3: cout << "星期三"; break;
        case 4: cout << "星期四"; break;
        case 5: cout << "星期五"; break;
        case 6: cout << "星期六"; break;
        case 7: cout << "星期日"; break;
        default: cout << "无效的星期";
    }
    cout << endl;

    // 多个 case 共用一个分支
    char grade = 'B';
    cout << "\n等级 " << grade << " 对应的分数范围：";
    switch (grade) {
        case 'A':
        case 'a':
            cout << "90 ~ 100 分";
            break;
        case 'B':
        case 'b':
            cout << "80 ~ 89 分";
            break;
        case 'C':
        case 'c':
            cout << "70 ~ 79 分";
            break;
        case 'D':
        case 'd':
            cout << "60 ~ 69 分";
            break;
        default:
            cout << "不及格";
    }
    cout << endl;

    // switch 穿透（没有 break 的情况）
    cout << "\nSwitch 穿透演示（没有 break 会继续执行后面的 case）：" << endl;
    int level = 2;
    switch (level) {
        case 3:
            cout << "  获得高级奖励" << endl;
            // 没有 break，继续往下
        case 2:
            cout << "  获得中级奖励" << endl;
            // 没有 break，继续往下
        case 1:
            cout << "  获得初级奖励" << endl;
            break;
        default:
            cout << "  没有奖励" << endl;
    }
    cout << "（等级 " << level << " 会获得等级 1 和 2 的奖励，因为穿透）" << endl;


    // ---------- 6. break 和 continue ----------
    cout << "\n========== break 和 continue ==========" << endl;

    // break：跳出整个循环
    cout << "break 演示：找到第一个大于 50 的数" << endl;
    int nums[] = {12, 35, 28, 67, 45, 80};
    for (int k = 0; k < 6; k++) {
        cout << "  检查 " << nums[k];
        if (nums[k] > 50) {
            cout << " → 大于 50，跳出循环" << endl;
            break;
        }
        cout << " → 继续" << endl;
    }

    // continue：跳过本次循环
    cout << "\ncontinue 演示：打印 1~10 中的奇数" << endl;
    for (int k = 1; k <= 10; k++) {
        if (k % 2 == 0) {
            continue;  // 偶数就跳过
        }
        cout << k << " ";
    }
    cout << endl;


    // ---------- 7. goto 语句 ----------
    cout << "\n========== goto 语句（了解即可，不推荐滥用） ==========" << endl;

    int x = 0;
loop_start:  // 标签
    x++;
    if (x < 5) {
        cout << "goto 循环：x = " << x << endl;
        goto loop_start;  // 跳转到标签
    }
    cout << "goto 循环结束" << endl;

    // goto 在安全领域的用途：跳出多层循环、错误处理
    // 但过度使用会导致代码难以维护（意大利面条代码）


    // ---------- 安全小贴士 ----------
    cout << "\n========== 安全小贴士 ==========" << endl;
    cout << "1. for 循环的边界条件容易出错，导致数组越界。" << endl;
    cout << "2. 整数溢出可能导致循环次数异常，是常见漏洞来源。" << endl;
    cout << "3. switch 的 break 遗漏可能导致逻辑错误。" << endl;

    return 0;
}
