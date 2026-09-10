/**
 * 02_control_flow.js - 条件判断、switch、各种循环
 * 
 * 本示例演示 JavaScript 的流程控制：
 * - if / else if / else 条件判断
 * - switch 多分支选择
 * - for、while、do...while 循环
 * - forEach、for...in、for...of 遍历
 * - break 和 continue 控制语句
 */

// ========== 1. 条件判断 ==========

console.log("=== 1. 条件判断 ===");

let score = 85;

// --- if 语句 ---
if (score >= 60) {
    console.log("成绩及格");
}

// --- if...else 语句 ---
if (score >= 60) {
    console.log("成绩及格");
} else {
    console.log("成绩不及格");
}

// --- if...else if...else 多分支 ---
console.log("\n根据分数评级:");
if (score >= 90) {
    console.log("优秀");
} else if (score >= 80) {
    console.log("良好");
} else if (score >= 70) {
    console.log("中等");
} else if (score >= 60) {
    console.log("及格");
} else {
    console.log("不及格");
}

// --- 三元运算符（简化的 if...else）---
let age = 20;
let status = age >= 18 ? "成年" : "未成年";
console.log("\n年龄状态:", status);

// 嵌套三元运算符（可读性差，谨慎使用）
let level = score >= 90 ? "优秀" : score >= 60 ? "及格" : "不及格";
console.log("成绩等级:", level);

// --- 真值与假值 ---
console.log("\n=== 真值与假值测试 ===");

// 假值（falsy）：在条件判断中为 false 的值
console.log("Boolean(false):", Boolean(false));
console.log("Boolean(0):", Boolean(0));
console.log("Boolean(''):", Boolean(''));
console.log("Boolean(null):", Boolean(null));
console.log("Boolean(undefined):", Boolean(undefined));
console.log("Boolean(NaN):", Boolean(NaN));

// 真值（truthy）：除了假值以外的都是真值
console.log("Boolean('0'):", Boolean('0'));      // true
console.log("Boolean('false'):", Boolean('false')); // true
console.log("Boolean([]):", Boolean([]));        // true
console.log("Boolean({}):", Boolean({}));        // true

// ========== 2. switch 语句 ==========

console.log("\n=== 2. switch 语句 ===");

let day = 3;

switch (day) {
    case 1:
        console.log("星期一");
        break;
    case 2:
        console.log("星期二");
        break;
    case 3:
        console.log("星期三");
        break;
    case 4:
        console.log("星期四");
        break;
    case 5:
        console.log("星期五");
        break;
    case 6:
    case 7:
        // 多个 case 共享同一个代码块（case 穿透）
        console.log("周末");
        break;
    default:
        console.log("无效的日期");
}

// 注意：switch 使用 === 严格比较
let numStr = "2";
switch (numStr) {
    case 2:
        console.log("数字 2");
        break;
    case "2":
        console.log("字符串 '2'");
        break;
    default:
        console.log("不匹配");
}
// 输出：字符串 '2'

// ========== 3. for 循环 ==========

console.log("\n=== 3. for 循环 ===");

// 基础 for 循环
console.log("从 0 到 4:");
for (let i = 0; i < 5; i++) {
    console.log("  i =", i);
}

// 倒序循环
console.log("从 5 到 1:");
for (let i = 5; i > 0; i--) {
    console.log("  i =", i);
}

// 计算 1 到 100 的和
let sum = 0;
for (let i = 1; i <= 100; i++) {
    sum += i;
}
console.log("1 到 100 的和:", sum);

// ========== 4. while 循环 ==========

console.log("\n=== 4. while 循环 ===");

let count = 1;
while (count <= 5) {
    console.log("第", count, "次循环");
    count++;
}

// while 循环可能一次都不执行
let x = 10;
while (x < 5) {
    console.log("这句话不会执行");
    x++;
}

// ========== 5. do...while 循环 ==========

console.log("\n=== 5. do...while 循环 ===");

let y = 10;
do {
    console.log("do...while 至少执行一次，y =", y);
    y++;
} while (y < 5);
// 即使条件不满足，也会执行一次循环体

// ========== 6. forEach 方法 ==========

console.log("\n=== 6. forEach 遍历数组 ===");

let fruits = ["苹果", "香蕉", "橙子", "葡萄"];

// 使用 forEach 遍历数组
fruits.forEach(function(fruit, index, array) {
    console.log(`索引 ${index}: ${fruit}`);
});

// 箭头函数写法
console.log("\n箭头函数写法:");
fruits.forEach((fruit, index) => {
    console.log(`[${index}] ${fruit}`);
});

// ========== 7. for...in 循环 ==========

console.log("\n=== 7. for...in 遍历对象 ===");

let person = {
    name: "张三",
    age: 25,
    city: "北京"
};

// for...in 遍历对象的可枚举属性
for (let key in person) {
    // 推荐使用 hasOwnProperty 过滤掉继承的属性
    if (person.hasOwnProperty(key)) {
        console.log(`${key}: ${person[key]}`);
    }
}

// for...in 也可以遍历数组（但不推荐）
console.log("\nfor...in 遍历数组（不推荐）:");
let colors = ["红", "绿", "蓝"];
for (let index in colors) {
    console.log(`colors[${index}] = ${colors[index]}`);
}

// ========== 8. for...of 循环 ==========

console.log("\n=== 8. for...of 遍历可迭代对象 ===");

// 遍历数组
let animals = ["猫", "狗", "兔子"];
for (let animal of animals) {
    console.log("动物:", animal);
}

// 遍历字符串
let str = "Hello";
console.log("\n遍历字符串:");
for (let char of str) {
    console.log("字符:", char);
}

// 结合 entries() 获取索引和值
console.log("\n同时获取索引和值:");
for (let [index, value] of animals.entries()) {
    console.log(`索引 ${index}: ${value}`);
}

// ========== 9. break 和 continue ==========

console.log("\n=== 9. break 和 continue ===");

// break - 跳出整个循环
console.log("遇到 5 就停止:");
for (let i = 1; i <= 10; i++) {
    if (i === 5) {
        break;  // 跳出循环
    }
    console.log("  i =", i);
}

// continue - 跳过当前循环，继续下一次
console.log("\n跳过偶数:");
for (let i = 1; i <= 10; i++) {
    if (i % 2 === 0) {
        continue;  // 跳过本次循环
    }
    console.log("  奇数:", i);
}

// ========== 10. 安全应用：登录验证示例 ==========

console.log("\n=== 10. 安全示例：简单登录验证 ===");

function loginCheck(username, password) {
    // 输入验证：检查是否为空
    if (!username || !password) {
        return "用户名和密码不能为空";
    }

    // 用户名长度检查
    if (username.length < 3 || username.length > 20) {
        return "用户名长度应在 3-20 个字符之间";
    }

    // 密码强度检查
    if (password.length < 6) {
        return "密码长度不能少于 6 位";
    }

    // 模拟验证（实际应查询数据库）
    if (username === "admin" && password === "admin123") {
        return "登录成功";
    } else {
        return "用户名或密码错误";
    }
}

console.log(loginCheck("", ""));
console.log(loginCheck("admin", ""));
console.log(loginCheck("admin", "123"));
console.log(loginCheck("admin", "admin123"));
console.log(loginCheck("user", "password"));

console.log("\n=== 示例运行完成 ===");
