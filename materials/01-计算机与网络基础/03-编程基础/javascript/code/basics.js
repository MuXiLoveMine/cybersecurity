/**
 * basics.js —— JavaScript 基础语法示例（安全从业者视角）
 *
 * 涵盖内容：
 *   1. 变量与数据类型
 *   2. 函数与箭头函数
 *   3. 数组操作
 *   4. 对象与原型链
 *   5. 闭包
 *   6. JSON 处理
 *   7. 异步编程（Promise / async-await）
 *   8. 正则表达式
 *   9. DOM 操作（Node 环境模拟说明）
 *  10. 错误处理
 *
 * 运行方式：
 *   Node.js 环境：node basics.js
 *   浏览器环境：在 DevTools Console 中粘贴运行
 *
 * 注意：本脚本用于学习参考，可以直接运行查看输出。
 */

"use strict";

// ============================================================
console.log("=".repeat(60));
console.log("  JavaScript 基础语法示例（安全从业者视角）");
console.log("  JavaScript Basics for Security Practitioners");
console.log("=".repeat(60));
console.log("");

// ============================================================
// 1. 变量与数据类型
// ============================================================
console.log("=".repeat(60));
console.log("【1. 变量与数据类型】");
console.log("=".repeat(60));
console.log("");

// 1.1 var / let / const
console.log("1.1 var / let / const");
var nameVar = "Alice (var)";
let nameLet = "Bob (let)";
const nameConst = "Charlie (const)";
console.log("  var   :", nameVar);
console.log("  let   :", nameLet);
console.log("  const :", nameConst);
console.log("");

// 1.2 基本数据类型
console.log("1.2 基本数据类型");
const str = "hello";
const num = 42;
const bool = true;
const undef = undefined;
const nullVal = null;
const big = 12345678901234567890n;

console.log("  string  :", str, "-> typeof:", typeof str);
console.log("  number  :", num, "-> typeof:", typeof num);
console.log("  boolean :", bool, "-> typeof:", typeof bool);
console.log("  undefined:", undef, "-> typeof:", typeof undef);
console.log("  null    :", nullVal, "-> typeof:", typeof nullVal, "(历史遗留bug)");
console.log("  bigint  :", big.toString(), "-> typeof:", typeof big);
console.log("");

// 1.3 类型转换与安全陷阱
console.log("1.3 类型转换与安全陷阱");
console.log("  '5' + 3  =", "5" + 3, "(字符串拼接)");
console.log("  '5' - 3  =", "5" - 3, "(自动转数字)");
console.log("  true + 1 =", true + 1, "(true 转 1)");
console.log("  [] + []  =", "[]" + "[]" ? '"" (空字符串)' : "", "(空数组转空字符串)");
console.log("");
console.log("  == 宽松相等:");
console.log("    '5' == 5     :", "5" == 5, "（不推荐）");
console.log("    null == undefined :", null == undefined, "（不推荐）");
console.log("  === 严格相等:");
console.log("    '5' === 5    :", "5" === 5, "（推荐使用）");
console.log("    null === undefined :", null === undefined, "（推荐使用）");
console.log("");
console.log("  💡 安全建议：始终使用 === 和 !==，避免隐式类型转换导致的安全问题");
console.log("");

// ============================================================
// 2. 函数与箭头函数
// ============================================================
console.log("=".repeat(60));
console.log("【2. 函数与箭头函数】");
console.log("=".repeat(60));
console.log("");

// 2.1 函数声明
console.log("2.1 函数声明与表达式");
function add(a, b) {
    return a + b;
}
console.log("  add(2, 3) =", add(2, 3));

// 函数表达式
const multiply = function(a, b) {
    return a * b;
};
console.log("  multiply(2, 3) =", multiply(2, 3));
console.log("");

// 2.2 箭头函数
console.log("2.2 箭头函数");
const subtract = (a, b) => a - b;
console.log("  subtract(10, 3) =", subtract(10, 3));

const greet = name => `Hello, ${name}!`;
console.log("  greet('Alice') =", greet("Alice"));

// 多行箭头函数
const divide = (a, b) => {
    if (b === 0) {
        throw new Error("除数不能为零");
    }
    return a / b;
};
try {
    console.log("  divide(10, 2) =", divide(10, 2));
} catch (e) {
    console.log("  错误:", e.message);
}
console.log("");

// 2.3 默认参数与剩余参数
console.log("2.3 默认参数与剩余参数");
function welcome(name = "Guest") {
    return `Welcome, ${name}!`;
}
console.log("  welcome() =", welcome());
console.log("  welcome('Bob') =", welcome("Bob"));

function sumAll(...numbers) {
    return numbers.reduce((acc, n) => acc + n, 0);
}
console.log("  sumAll(1, 2, 3, 4, 5) =", sumAll(1, 2, 3, 4, 5));
console.log("");

// ============================================================
// 3. 数组操作
// ============================================================
console.log("=".repeat(60));
console.log("【3. 数组操作】");
console.log("=".repeat(60));
console.log("");

// 3.1 数组基础
console.log("3.1 数组基础");
const fruits = ["apple", "banana", "orange", "grape"];
console.log("  数组:", fruits.join(", "));
console.log("  长度:", fruits.length);
console.log("  第一个:", fruits[0]);
console.log("  最后一个:", fruits[fruits.length - 1]);
console.log("  索引 banana:", fruits.indexOf("banana"));
console.log("  包含 mango:", fruits.includes("mango"));
console.log("");

// 3.2 常用数组方法
console.log("3.2 常用迭代方法（安全代码中大量使用）");
const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
console.log("  原始数组:", numbers.join(", "));

// map：映射转换
const doubled = numbers.map(n => n * 2);
console.log("  map (x2):", doubled.slice(0, 5).join(", "), "...");

// filter：筛选
const evens = numbers.filter(n => n % 2 === 0);
console.log("  filter (偶数):", evens.join(", "));

// reduce：归约
const sum = numbers.reduce((acc, n) => acc + n, 0);
console.log("  reduce (求和):", sum);

// find：查找第一个
const firstOverFive = numbers.find(n => n > 5);
console.log("  find (>5):", firstOverFive);

// some / every
const hasLarge = numbers.some(n => n > 8);
const allPositive = numbers.every(n => n > 0);
console.log("  some (>8):", hasLarge);
console.log("  every (>0):", allPositive);
console.log("");

// 3.3 安全场景：IP 地址列表处理
console.log("3.3 安全场景：IP 地址列表处理");
const ipList = [
    "192.168.1.1",
    "10.0.0.5",
    "192.168.1.100",
    "172.16.0.1",
    "192.168.1.1",     // 重复
    "203.0.113.45"
];

// 去重
const uniqueIPs = [...new Set(ipList)];
console.log("  去重后 IP 数:", uniqueIPs.length, "(原始:", ipList.length, ")");

// 筛选内网 IP
const privateIPs = ipList.filter(ip =>
    ip.startsWith("192.168.") ||
    ip.startsWith("10.") ||
    ip.startsWith("172.16.") ||
    ip.startsWith("172.17.") ||
    ip.startsWith("172.18.") ||
    ip.startsWith("172.19.") ||
    ip.startsWith("172.2") ||
    ip.startsWith("172.30.") ||
    ip.startsWith("172.31.")
);
console.log("  内网 IP:", [...new Set(privateIPs)].join(", "));

// 统计出现次数
const ipCount = ipList.reduce((acc, ip) => {
    acc[ip] = (acc[ip] || 0) + 1;
    return acc;
}, {});
console.log("  IP 出现统计:", JSON.stringify(ipCount));
console.log("");

// ============================================================
// 4. 对象与原型链
// ============================================================
console.log("=".repeat(60));
console.log("【4. 对象与原型链】");
console.log("=".repeat(60));
console.log("");

// 4.1 对象基础
console.log("4.1 对象基础");
const user = {
    name: "Alice",
    age: 25,
    email: "alice@example.com",
    isAdmin: false,
    greet() {
        return `Hello, I'm ${this.name}`;
    }
};

console.log("  name:", user.name);
console.log("  age:", user["age"]);
console.log("  greet():", user.greet());

// 动态添加属性
user.role = "editor";
console.log("  添加 role 后:", Object.keys(user).join(", "));

// 删除属性
delete user.role;
console.log("  删除 role 后:", Object.keys(user).join(", "));

// 检查属性
console.log("  'name' in user:", "name" in user);
console.log("  hasOwnProperty('name'):", user.hasOwnProperty("name"));
console.log("  hasOwnProperty('toString'):", user.hasOwnProperty("toString"));
console.log("  (toString 是继承自原型的方法)");
console.log("");

// 4.2 解构赋值
console.log("4.2 解构赋值");
const { name, age, isAdmin: admin } = user;
console.log("  解构后: name =", name, ", age =", age, ", admin =", admin);

const [first, second, ...rest] = fruits;
console.log("  数组解构: first =", first, ", second =", second, ", rest =", rest.join(", "));
console.log("");

// 4.3 原型链与安全
console.log("4.3 原型链与原型链污染（安全重点）");
console.log("  原型链: user -> Object.prototype -> null");
console.log("  user.__proto__ === Object.prototype :", Object.getPrototypeOf(user) === Object.prototype);

// 原型链污染演示（防御视角）
console.log("");
console.log("  ⚠️  原型链污染演示（仅用于理解原理，请勿用于攻击）");
const obj1 = {};
const obj2 = {};
console.log("  污染前 obj1.isAdmin:", obj1.isAdmin);
console.log("  污染前 obj2.isAdmin:", obj2.isAdmin);

// 模拟污染（通过 __proto__）
const maliciousInput = JSON.parse('{"__proto__": {"isAdmin": true}}');
// 注意：JSON.parse 不会直接污染原型，因为 __proto__ 会被当作普通属性
// 真正的污染通常发生在递归合并对象的场景

// 正确创建无原型对象（防御原型链污染）
const safeObj = Object.create(null);
safeObj.name = "safe";
console.log("");
console.log("  ✅ 安全对象（无原型）:");
console.log("    safeObj.name =", safeObj.name);
console.log("    safeObj.__proto__ =", Object.getPrototypeOf(safeObj));
console.log("    (没有原型，不会被原型链污染影响)");
console.log("");

// ============================================================
// 5. 闭包
// ============================================================
console.log("=".repeat(60));
console.log("【5. 闭包（Closure）】");
console.log("=".repeat(60));
console.log("");

// 5.1 闭包基础
console.log("5.1 闭包基础：函数可以访问外部作用域的变量");
function createCounter() {
    let count = 0;  // 私有变量
    
    return {
        increment() {
            count++;
            return count;
        },
        decrement() {
            count--;
            return count;
        },
        getCount() {
            return count;
        }
    };
}

const counter = createCounter();
console.log("  counter.increment():", counter.increment());
console.log("  counter.increment():", counter.increment());
console.log("  counter.getCount():", counter.getCount());
console.log("  counter.decrement():", counter.decrement());
console.log("  (count 是私有变量，外部无法直接访问)");
console.log("");

// 5.2 安全场景：简单的 Token 管理器
console.log("5.2 安全场景：Token 管理器（闭包实现私有变量）");
function createTokenManager() {
    let token = null;      // 私有：不直接暴露
    let expiresAt = null;  // 私有：过期时间
    
    return {
        setToken(newToken, ttlSeconds = 3600) {
            token = newToken;
            expiresAt = Date.now() + ttlSeconds * 1000;
            console.log("  Token 已设置");
        },
        
        getToken() {
            if (!token || Date.now() > expiresAt) {
                console.log("  Token 不存在或已过期");
                return null;
            }
            return token;
        },
        
        clearToken() {
            token = null;
            expiresAt = null;
            console.log("  Token 已清除");
        },
        
        isValid() {
            return token !== null && Date.now() < expiresAt;
        }
    };
}

const tokenMgr = createTokenManager();
tokenMgr.setToken("abc123xyz-secret-token", 3600);
console.log("  Token 有效:", tokenMgr.isValid());
console.log("  获取 Token:", tokenMgr.getToken() ? "*** (已隐藏)" : "无");
tokenMgr.clearToken();
console.log("  清除后有效:", tokenMgr.isValid());
console.log("");
console.log("  💡 闭包可以模拟私有变量，防止敏感数据被意外访问");
console.log("");

// ============================================================
// 6. JSON 处理
// ============================================================
console.log("=".repeat(60));
console.log("【6. JSON 处理】");
console.log("=".repeat(60));
console.log("");

// 6.1 序列化与解析
console.log("6.1 JSON.stringify / JSON.parse");
const data = {
    user: "Alice",
    age: 25,
    isAdmin: false,
    roles: ["editor", "viewer"]
};

const jsonStr = JSON.stringify(data, null, 2);
console.log("  JSON.stringify 结果:");
console.log("  " + jsonStr.replace(/\n/g, "\n  "));

const parsed = JSON.parse(jsonStr);
console.log("  JSON.parse 后 user:", parsed.user);
console.log("  JSON.parse 后 roles:", parsed.roles.join(", "));
console.log("");

// 6.2 安全注意事项
console.log("6.2 安全注意事项");
console.log("  ✅ JSON.parse 是安全的：不会执行代码（不像 eval）");
console.log("  ❌ 永远不要用 eval() 解析 JSON！");
console.log("");

// 错误处理
try {
    const badJson = "{ name: 'Alice' }";  // 不合法的 JSON
    JSON.parse(badJson);
} catch (e) {
    console.log("  非法 JSON 解析错误:", e.message);
}

try {
    JSON.parse("null");  // 合法，但结果是 null
    console.log("  JSON.parse('null') = null (合法)");
} catch (e) {
    console.log("  错误:", e.message);
}
console.log("");

// ============================================================
// 7. 异步编程
// ============================================================
console.log("=".repeat(60));
console.log("【7. 异步编程（Promise / async-await）】");
console.log("=".repeat(60));
console.log("");

// 7.1 Promise 基础
console.log("7.1 Promise 基础");
function delay(ms, value) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (Math.random() > 0.1) {  // 90% 成功率
                resolve(value);
            } else {
                reject(new Error("模拟失败"));
            }
        }, ms);
    });
}

console.log("  创建 Promise...");
delay(100, "数据A")
    .then(result => {
        console.log("  Promise 成功:", result);
        return delay(100, "数据B");
    })
    .then(result => {
        console.log("  链式调用结果:", result);
    })
    .catch(error => {
        console.log("  Promise 失败:", error.message);
    })
    .finally(() => {
        console.log("  Promise 完成（finally 总是执行）");
        console.log("");
        runAsyncAwaitDemo();
    });

// 7.2 async/await
function runAsyncAwaitDemo() {
    console.log("7.2 async/await");
    
    async function fetchData() {
        try {
            console.log("  正在获取数据...");
            const resultA = await delay(100, "数据A");
            console.log("  获取到:", resultA);
            
            const resultB = await delay(100, "数据B");
            console.log("  获取到:", resultB);
            
            return [resultA, resultB];
        } catch (error) {
            console.error("  获取失败:", error.message);
            throw error;
        }
    }
    
    fetchData().then(results => {
        console.log("  async/await 完成，结果:", results.join(", "));
        console.log("");
        runPromiseAllDemo();
    });
}

// 7.3 Promise.all 并行执行
function runPromiseAllDemo() {
    console.log("7.3 Promise.all 并行执行");
    
    async function fetchAll() {
        console.log("  并行获取 3 个数据...");
        const start = Date.now();
        
        const [a, b, c] = await Promise.all([
            delay(100, "数据A"),
            delay(100, "数据B"),
            delay(100, "数据C")
        ]);
        
        const elapsed = Date.now() - start;
        console.log("  全部获取完成:", a, b, c);
        console.log("  耗时:", elapsed, "ms（串行需要 300ms+）");
        console.log("");
        
        runRegexDemo();
    }
    
    fetchAll().catch(() => runRegexDemo());
}

// ============================================================
// 8. 正则表达式
// ============================================================
function runRegexDemo() {
    console.log("=".repeat(60));
    console.log("【8. 正则表达式】");
    console.log("=".repeat(60));
    console.log("");

    // 8.1 基础用法
    console.log("8.1 基础用法");
    const text = "联系我们：alice@example.com 或 bob@test.org，紧急电话 13800138000";
    
    // test：测试是否匹配
    const hasEmail = /\S+@\S+\.\S+/.test(text);
    console.log("  包含邮箱:", hasEmail);
    
    // match：获取匹配
    const emails = text.match(/\S+@\S+\.\S+/g);
    console.log("  找到邮箱:", emails ? emails.join(", ") : "无");
    
    // matchAll：获取所有匹配详情
    const phoneMatch = text.match(/1[3-9]\d{9}/g);
    console.log("  找到手机号:", phoneMatch ? phoneMatch.join(", ") : "无");
    
    // replace：替换
    const masked = text.replace(/(\S+)@(\S+\.\S+)/g, "***@$2");
    console.log("  邮箱脱敏:", masked);
    console.log("");

    // 8.2 安全场景：输入验证
    console.log("8.2 安全场景：输入验证");
    
    function validateEmail(email) {
        // 简单的邮箱格式验证（实际场景建议用更完善的验证库）
        const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return re.test(email);
    }
    
    function validateIP(ip) {
        // IPv4 格式验证
        const re = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return re.test(ip);
    }
    
    function validateURL(url) {
        // 安全的 URL 验证：只允许 http/https
        try {
            const u = new URL(url);
            return u.protocol === "http:" || u.protocol === "https:";
        } catch {
            return false;
        }
    }
    
    const testEmails = ["alice@example.com", "bob@test", "invalid@", "charlie@domain.co.uk"];
    console.log("  邮箱验证:");
    testEmails.forEach(e => console.log(`    ${e}: ${validateEmail(e) ? "✅" : "❌"}`));
    
    const testIPs = ["192.168.1.1", "10.0.0.256", "invalid", "8.8.8.8"];
    console.log("  IP 验证:");
    testIPs.forEach(ip => console.log(`    ${ip}: ${validateIP(ip) ? "✅" : "❌"}`));
    
    const testURLs = ["https://example.com", "javascript:alert(1)", "ftp://files.com", "http://test.org/path"];
    console.log("  URL 验证（仅 http/https）:");
    testURLs.forEach(u => console.log(`    ${u}: ${validateURL(u) ? "✅" : "❌"}`));
    console.log("");

    // 8.3 ReDoS 风险提示
    console.log("8.3 ReDoS 风险提示");
    console.log("  ⚠️  嵌套量词的正则可能导致 ReDoS（正则拒绝服务）");
    console.log("  危险示例: /(a+)+$/  （输入 'aaaaaaaaaaaaaaaaaaaa!' 会极慢）");
    console.log("  安全建议:");
    console.log("    - 避免嵌套量词");
    console.log("    - 限制输入长度");
    console.log("    - 设置正则匹配超时（Node.js 可用 --max-old-space-size）");
    console.log("    - 使用 RE2 等安全的正则引擎");
    console.log("");
    
    runDOMDemo();
}

// ============================================================
// 9. DOM 操作（Node 环境模拟说明）
// ============================================================
function runDOMDemo() {
    console.log("=".repeat(60));
    console.log("【9. DOM 操作（安全视角）】");
    console.log("=".repeat(60));
    console.log("");
    console.log("  注：Node.js 环境没有真实 DOM，以下为原理说明");
    console.log("");

    console.log("9.1 安全的 DOM 操作 vs 危险的 DOM 操作");
    console.log("");
    console.log("  ✅ 安全（纯文本，不会解析 HTML）:");
    console.log("     element.textContent = userInput;");
    console.log("     element.innerText = userInput;");
    console.log("");
    console.log("  ❌ 危险（会解析 HTML，可能导致 XSS）:");
    console.log("     element.innerHTML = userInput;");
    console.log("     element.outerHTML = userInput;");
    console.log("     document.write(userInput);");
    console.log("");
    console.log("  ⚠️  需要注意的属性（可能导致 XSS）:");
    console.log("     - href / src （需检查是否为 javascript: 伪协议）");
    console.log("     - onload / onerror / onclick 等事件属性");
    console.log("     - style 中的 expression（IE）");
    console.log("");

    // HTML 转义函数
    function escapeHtml(str) {
        const div = { textContent: "", innerHTML: "" }; // 模拟
        // 实际浏览器中：
        // const div = document.createElement("div");
        // div.textContent = str;
        // return div.innerHTML;
        
        // 手动转义（Node 环境演示）
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }
    
    const dangerousInput = '<script>alert("XSS")</script><img src=x onerror=alert(1)>';
    console.log("  HTML 转义示例:");
    console.log("    原始输入:", dangerousInput);
    console.log("    转义后:", escapeHtml(dangerousInput));
    console.log("    （转义后在页面上只会显示为文本，不会执行脚本）");
    console.log("");

    console.log("9.2 DOM XSS 常见 sink（危险点）");
    const sinks = [
        "innerHTML / outerHTML / document.write()",
        "eval() / setTimeout(string) / setInterval(string)",
        "location.href / location.replace() （javascript: 伪协议）",
        "document.createElement('script') + src",
        "window.postMessage （未验证 origin）",
        "localStorage / sessionStorage （读取后直接插入 DOM）"
    ];
    console.log("  常见的 DOM XSS 注入点:");
    sinks.forEach((s, i) => console.log(`    ${i + 1}. ${s}`));
    console.log("");
    
    runErrorDemo();
}

// ============================================================
// 10. 错误处理
// ============================================================
function runErrorDemo() {
    console.log("=".repeat(60));
    console.log("【10. 错误处理】");
    console.log("=".repeat(60));
    console.log("");

    // 10.1 try/catch/finally
    console.log("10.1 try/catch/finally");
    try {
        console.log("  尝试执行危险操作...");
        throw new Error("模拟错误");
        console.log("  这行不会执行");
    } catch (error) {
        console.log("  捕获到错误:", error.message);
        console.log("  错误名称:", error.name);
        // console.log("  错误栈:", error.stack);
    } finally {
        console.log("  finally 块：总是执行（清理工作）");
    }
    console.log("");

    // 10.2 自定义错误
    console.log("10.2 自定义错误类");
    class SecurityError extends Error {
        constructor(message, code) {
            super(message);
            this.name = "SecurityError";
            this.code = code;
        }
    }
    
    try {
        throw new SecurityError("检测到恶意输入", "SEC-001");
    } catch (error) {
        if (error instanceof SecurityError) {
            console.log("  安全错误:", error.message);
            console.log("  错误码:", error.code);
            console.log("  错误类型:", error.name);
        }
    }
    console.log("");

    // 10.3 异步错误处理
    console.log("10.3 异步错误处理");
    
    async function asyncOperation() {
        throw new Error("异步操作失败");
    }
    
    asyncOperation()
        .then(() => console.log("  成功"))
        .catch(err => console.log("  异步错误（.catch）:", err.message));
    
    async function safeAsyncCall() {
        try {
            await asyncOperation();
        } catch (err) {
            console.log("  异步错误（try/catch）:", err.message);
        }
    }
    
    safeAsyncCall().then(() => {
        console.log("");
        printSummary();
    });
}

// ============================================================
// 总结
// ============================================================
function printSummary() {
    console.log("=".repeat(60));
    console.log("  所有示例执行完毕");
    console.log("  脚本涵盖：变量、函数、数组、对象、闭包、");
    console.log("  JSON、异步、正则、DOM 安全、错误处理");
    console.log("=".repeat(60));
    console.log("");
    console.log("  💡 安全从业者 JavaScript 学习重点：");
    console.log("     1. 理解 DOM 操作的安全风险（XSS）");
    console.log("     2. 掌握原型链与原型链污染原理");
    console.log("     3. 熟悉异步编程模式（分析前端逻辑）");
    console.log("     4. 学会使用 Chrome DevTools 调试 JS");
    console.log("     5. 了解常见的代码混淆与反混淆方法");
    console.log("");
}
