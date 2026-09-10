/**
 * 03_functions.js - 函数定义、箭头函数、闭包、回调
 * 
 * 本示例演示 JavaScript 的函数相关知识：
 * - 函数声明与函数表达式
 * - 箭头函数
 * - 匿名函数与立即执行函数（IIFE）
 * - 闭包
 * - 回调函数
 * - 高阶函数
 */

// ========== 1. 函数声明 ==========

console.log("=== 1. 函数声明 ===");

// 函数声明（会被提升，可以在声明前调用）
function greet(name) {
    return "你好，" + name + "！";
}

console.log(greet("张三"));
console.log(greet("李四"));

// 带默认参数的函数（ES6）
function welcome(name = "访客") {
    return `欢迎，${name}！`;
}

console.log(welcome());          // 欢迎，访客！
console.log(welcome("小明"));    // 欢迎，小明！

// 多个参数
function add(a, b) {
    return a + b;
}

console.log("1 + 2 =", add(1, 2));

// ========== 2. 函数表达式 ==========

console.log("\n=== 2. 函数表达式 ===");

// 函数表达式（不会提升，必须先声明后使用）
const multiply = function(a, b) {
    return a * b;
};

console.log("3 * 4 =", multiply(3, 4));

// 函数表达式可以命名（便于调试）
const divide = function div(a, b) {
    if (b === 0) {
        return "除数不能为零";
    }
    return a / b;
};

console.log("10 / 2 =", divide(10, 2));
console.log("10 / 0 =", divide(10, 0));

// ========== 3. 箭头函数 ==========

console.log("\n=== 3. 箭头函数（ES6） ===");

// 完整写法
const square = (x) => {
    return x * x;
};
console.log("5 的平方:", square(5));

// 简写：只有一个参数时可以省略括号
const double = x => {
    return x * 2;
};
console.log("5 的两倍:", double(5));

// 简写：函数体只有一行 return 时可以省略花括号和 return
const triple = x => x * 3;
console.log("5 的三倍:", triple(5));

// 多个参数的箭头函数
const sum = (a, b) => a + b;
console.log("3 + 7 =", sum(3, 7));

// 返回对象时需要用括号包裹
const createUser = (name, age) => ({ name: name, age: age });
console.log("创建用户:", createUser("王五", 30));

// ========== 4. 匿名函数 ==========

console.log("\n=== 4. 匿名函数 ===");

// 匿名函数作为变量值
const sayHello = function() {
    console.log("Hello!");
};
sayHello();

// 匿名函数作为参数（回调函数）
setTimeout(function() {
    console.log("这是 1 秒后执行的匿名函数");
}, 1000);
// 注意：由于是异步的，这行会在后面的同步代码执行完后才输出

// ========== 5. 立即执行函数（IIFE） ==========

console.log("\n=== 5. 立即执行函数（IIFE） ===");

// 立即执行函数表达式：定义后立即执行
(function() {
    console.log("这是一个立即执行函数");
    let message = "内部变量";
    console.log(message);
})();

// 带参数的 IIFE
(function(name) {
    console.log("你好，" + name + "！（来自 IIFE）");
})("小红");

// IIFE 的作用：创建独立作用域，避免变量污染全局
// 这是早期模块化的常用方式

// ========== 6. 闭包（Closure） ==========

console.log("\n=== 6. 闭包 ===");

// 闭包：函数能够访问其词法作用域中的变量，即使函数在其词法作用域之外执行
function createCounter() {
    let count = 0;  // 私有变量

    // 返回的内部函数形成了闭包，可以访问 count
    return function() {
        count++;
        return count;
    };
}

const counter1 = createCounter();
console.log("counter1 第 1 次调用:", counter1());  // 1
console.log("counter1 第 2 次调用:", counter1());  // 2
console.log("counter1 第 3 次调用:", counter1());  // 3

const counter2 = createCounter();
console.log("counter2 第 1 次调用:", counter2());  // 1（独立的计数器）
console.log("counter1 第 4 次调用:", counter1());  // 4

// 闭包应用：数据私有化
console.log("\n闭包应用：数据封装 - 银行账户");

function createBankAccount(initialBalance) {
    let balance = initialBalance;  // 私有变量，外部无法直接访问

    return {
        // 存款
        deposit: function(amount) {
            if (amount <= 0) {
                return "存款金额必须大于 0";
            }
            balance += amount;
            return `存款成功，当前余额：${balance}`;
        },

        // 取款
        withdraw: function(amount) {
            if (amount <= 0) {
                return "取款金额必须大于 0";
            }
            if (amount > balance) {
                return "余额不足";
            }
            balance -= amount;
            return `取款成功，当前余额：${balance}`;
        },

        // 查询余额
        getBalance: function() {
            return balance;
        }
    };
}

const account = createBankAccount(1000);
console.log("初始余额:", account.getBalance());
console.log(account.deposit(500));
console.log(account.withdraw(200));
console.log(account.withdraw(2000));
console.log("最终余额:", account.getBalance());
// console.log(account.balance);  // undefined，无法直接访问私有变量

// ========== 7. 回调函数 ==========

console.log("\n=== 7. 回调函数 ===");

// 同步回调
function processArray(arr, callback) {
    let result = [];
    for (let i = 0; i < arr.length; i++) {
        result.push(callback(arr[i], i));
    }
    return result;
}

const numbers = [1, 2, 3, 4, 5];

// 传入一个回调函数，将每个元素乘以 2
const doubled = processArray(numbers, function(num) {
    return num * 2;
});
console.log("每个元素乘以 2:", doubled);

// 使用箭头函数作为回调
const squared = processArray(numbers, num => num * num);
console.log("每个元素的平方:", squared);

// ========== 8. 高阶函数 ==========

console.log("\n=== 8. 高阶函数 ===");

// 高阶函数：接收函数作为参数，或者返回函数的函数

// 示例：创建乘法器工厂函数
function createMultiplier(multiplier) {
    return function(x) {
        return x * multiplier;
    };
}

const doubleFn = createMultiplier(2);
const tripleFn = createMultiplier(3);

console.log("doubleFn(5):", doubleFn(5));    // 10
console.log("tripleFn(5):", tripleFn(5));    // 15

// 函数作为参数
function calculate(a, b, operation) {
    return operation(a, b);
}

const addFn = (x, y) => x + y;
const multiplyFn = (x, y) => x * y;

console.log("加法:", calculate(5, 3, addFn));        // 8
console.log("乘法:", calculate(5, 3, multiplyFn));   // 15

// ========== 9. 递归函数 ==========

console.log("\n=== 9. 递归函数 ===");

// 阶乘
function factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

console.log("5! =", factorial(5));  // 120
console.log("10! =", factorial(10)); // 3628800

// 斐波那契数列
function fibonacci(n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

console.log("斐波那契数列前 10 项:");
for (let i = 0; i < 10; i++) {
    console.log(`  fibonacci(${i}) = ${fibonacci(i)}`);
}

// ========== 10. 安全应用：输入验证函数 ==========

console.log("\n=== 10. 安全示例：输入验证函数 ===");

// 创建验证器工厂函数
function createValidator(pattern, errorMsg) {
    return function(input) {
        if (pattern.test(input)) {
            return { valid: true, message: "验证通过" };
        }
        return { valid: false, message: errorMsg };
    };
}

// 邮箱验证器
const emailValidator = createValidator(
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    "请输入有效的邮箱地址"
);

// 手机号验证器
const phoneValidator = createValidator(
    /^1[3-9]\d{9}$/,
    "请输入有效的手机号码"
);

// 用户名验证器（字母数字下划线，3-20 位）
const usernameValidator = createValidator(
    /^[a-zA-Z0-9_]{3,20}$/,
    "用户名只能包含字母、数字和下划线，长度 3-20 位"
);

console.log("邮箱验证 test@example.com:", emailValidator("test@example.com"));
console.log("邮箱验证 invalid-email:", emailValidator("invalid-email"));
console.log("手机号验证 13812345678:", phoneValidator("13812345678"));
console.log("手机号验证 12345:", phoneValidator("12345"));
console.log("用户名验证 admin_123:", usernameValidator("admin_123"));
console.log("用户名验证 a:", usernameValidator("a"));

console.log("\n=== 示例运行完成 ===");
