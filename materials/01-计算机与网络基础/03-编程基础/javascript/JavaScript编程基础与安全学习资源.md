# JavaScript 编程基础与安全学习资源

> 本文系统介绍 JavaScript 编程基础与 Web 安全领域应用：JavaScript 在安全中的定位、编程基础（安全视角）、Web 安全核心用法、常用库与工具、2026 年免费学习资源、推荐 GitHub 项目，以及两个可运行的示例脚本（basics.js 和 security_cases.js）。面向 Web 安全工程师与渗透测试人员，全部内容从防御、授权测试和安全研究的正向角度出发。

---

## 目录

- [一、JavaScript 在网络安全中的定位](#一javascript-在网络安全中的定位)
- [二、JavaScript 编程基础（安全视角）](#二javascript-编程基础安全视角)
- [三、Web 安全核心用法](#三web-安全核心用法)
- [四、常用安全库与工具](#四常用安全库与工具)
- [五、2026 年免费学习资源](#五2026-年免费学习资源)
- [六、2026 年推荐 GitHub 项目](#六2026-年推荐-github-项目)
- [七、示例代码文件](#七示例代码文件)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、JavaScript 在网络安全中的定位

### 1.1 为什么安全从业者必须掌握 JavaScript

**JavaScript（简称 JS）** 是 Web 的编程语言，是所有现代浏览器的内置脚本语言。对于 Web 安全从业者来说，JavaScript 既是**攻击工具**，也是**防御工具**——不懂 JS，就无法真正理解 Web 漏洞的原理和防护。

| 优势 / 特点 | 说明 |
|------------|------|
| **Web 通用语言** | 所有浏览器都支持，99% 的网站使用 JS |
| **客户端执行** | 代码在用户浏览器中运行，可被查看和修改 |
| **DOM 操作能力** | 可直接操作网页内容、结构和样式 |
| **异步通信** | AJAX / Fetch API 实现不刷新页面的数据交互 |
| **安全攻防核心** | XSS、CSRF、CORS、点击劫持等都与 JS 密切相关 |
| **生态丰富** | Node.js 让 JS 走向服务端，npm 生态全球最大 |

> **安全视角的重要性**：
> - 作为**防御者**：必须理解 XSS 攻击如何注入、如何绕过过滤，才能写出安全的代码和有效的 WAF 规则
> - 作为**渗透测试人员**：需要阅读前端 JS 代码发现隐藏的 API 接口、调试加密逻辑、构造 XSS Payload
> - 作为**安全研究人员**：浏览器安全、原型链污染、前端混淆与反混淆都离不开 JS 功底

### 1.2 JavaScript 运行环境

| 环境 | 说明 | 安全场景 |
|------|------|---------|
| **浏览器** | 最主要的运行环境，Chrome/Firefox/Safari/Edge | XSS、CSRF、DOM 操作、前端逻辑分析 |
| **Node.js** | 服务端 JS 运行时，基于 V8 引擎 | 服务端代码审计、npm 供应链安全 |
| **Web Worker** | 浏览器后台线程 | 前端加密、耗时计算 |
| **Service Worker** | 浏览器代理服务 | PWA 安全、离线缓存攻击 |
| **Electron / NW.js** | 桌面应用框架 | 客户端应用安全、Node 集成风险 |
| **扩展 / 插件** | 浏览器扩展 | 扩展权限滥用、数据窃取 |

### 1.3 安全领域的应用方向

| 方向 | JavaScript 的作用 | 典型场景 |
|------|------------------|---------|
| **Web 渗透测试** | 构造 Payload、分析前端逻辑 | XSS 利用、CSRF 构造、API 发现 |
| **前端安全审计** | 代码审查、漏洞挖掘 | 检查输入验证、DOM XSS、敏感信息泄露 |
| **浏览器安全** | 理解浏览器安全机制 | 同源策略、CSP、Sandbox、隔离原理 |
| **漏洞研究** | 原型链污染、类型混淆 | 高级 Web 漏洞利用技术研究 |
| **安全工具开发** | 浏览器扩展、爬虫、扫描器 | Burp 插件、安全检查工具 |
| **安全防护** | 前端防护、WAF 规则编写 | 输入净化、CSP 配置、XSS 防御 |

---

## 二、JavaScript 编程基础（安全视角）

### 2.1 变量与数据类型

#### var / let / const

```javascript
// var —— 函数作用域，可重复声明，存在变量提升（不推荐）
var name = "Alice";
var name = "Bob";  // 可以重复声明（容易出错）

// let —— 块级作用域，不可重复声明（ES6+ 推荐）
let age = 25;
age = 26;  // 可以重新赋值
// let age = 30;  // 错误：不能重复声明

// const —— 块级作用域，声明后不可重新赋值（常量）
const PI = 3.14159;
// PI = 3;  // 错误：不能重新赋值

// 注意：const 声明的对象，其属性仍可修改
const user = { name: "Alice" };
user.name = "Bob";  // 合法！对象的引用不变，属性可变
```

> **安全提示**：优先使用 `const`，其次 `let`，避免 `var`。`var` 的函数作用域和变量提升容易导致意外的变量覆盖，在大型项目中可能引入安全隐患。

#### 基本数据类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `string` | 字符串 | `"hello"`、`'world'`、`` `template` `` |
| `number` | 数字（整数/浮点数） | `42`、`3.14`、`NaN`、`Infinity` |
| `boolean` | 布尔值 | `true`、`false` |
| `undefined` | 未定义（声明未赋值） | `let x; // x 是 undefined` |
| `null` | 空值（主动赋值为空） | `let y = null;` |
| `symbol` | 唯一标识符 | `Symbol("id")` |
| `bigint` | 大整数 | `12345678901234567890n` |

#### 引用类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `Object` | 对象 | `{ name: "Alice", age: 25 }` |
| `Array` | 数组 | `[1, 2, 3, "four"]` |
| `Function` | 函数 | `function add(a, b) { return a + b; }` |
| `Date` | 日期 | `new Date()` |
| `RegExp` | 正则表达式 | `/pattern/g` |
| `Map` / `Set` | 映射 / 集合 | `new Map()`、`new Set()` |

#### 类型转换与安全陷阱

```javascript
// 隐式类型转换（容易出 bug 和安全问题）
console.log("5" + 3);      // "53"  字符串拼接
console.log("5" - 3);      // 2     自动转数字
console.log("5" * "3");    // 15    自动转数字
console.log(true + 1);     // 2     true 转 1
console.log([] + []);      // ""    空数组转空字符串
console.log([] + {});      // "[object Object]"
console.log({} + []);      // 0     （对象被当成语句块）

// 严格相等 vs 宽松相等
console.log("5" == 5);     // true   宽松相等（自动转换）
console.log("5" === 5);    // false  严格相等（类型也比）
console.log(null == undefined);  // true
console.log(null === undefined); // false
```

> **安全最佳实践**：始终使用 `===` 和 `!==`（严格相等/不等），避免 `==` 和 `!=` 导致的意外类型转换。类型转换是许多 Web 漏洞（如类型混淆、原型链污染）的根源之一。

### 2.2 运算符与流程控制

#### 常用运算符

| 类别 | 运算符 | 说明 |
|------|--------|------|
| 算术 | `+` `-` `*` `/` `%` `**` `++` `--` | 加减乘除、取模、幂、自增自减 |
| 比较 | `===` `!==` `>` `<` `>=` `<=` | 严格相等、大于小于 |
| 逻辑 | `&&` `\|\|` `!` | 与、或、非 |
| 位运算 | `&` `\|` `^` `~` `<<` `>>` `>>>` | 按位与/或/异或/取反/移位 |
| 赋值 | `=` `+=` `-=` `*=` `/=` `%=` `**=` | 赋值及复合赋值 |
| 三元 | `条件 ? 表达式1 : 表达式2` | 条件运算符 |
| 可选链 | `?.` | 安全访问嵌套属性（ES2020） |
| 空值合并 | `??` | 左侧为 null/undefined 时取右侧 |

#### 条件语句

```javascript
// if / else if / else
const score = 85;
if (score >= 90) {
    console.log("优秀");
} else if (score >= 60) {
    console.log("及格");
} else {
    console.log("不及格");
}

// switch
const role = "admin";
switch (role) {
    case "admin":
        console.log("管理员权限");
        break;
    case "editor":
        console.log("编辑权限");
        break;
    case "viewer":
        console.log("只读权限");
        break;
    default:
        console.log("未知角色");
}
```

#### 循环

```javascript
// for 循环
for (let i = 0; i < 5; i++) {
    console.log(i);
}

// for...of 遍历数组（值）
const colors = ["red", "green", "blue"];
for (const color of colors) {
    console.log(color);
}

// for...in 遍历对象（键）
const user = { name: "Alice", age: 25 };
for (const key in user) {
    console.log(key + ": " + user[key]);
}

// while 循环
let count = 0;
while (count < 3) {
    console.log(count);
    count++;
}

// do...while 循环（至少执行一次）
let i = 0;
do {
    console.log(i);
    i++;
} while (i < 3);

// 数组方法遍历
colors.forEach((color, index) => {
    console.log(index + ": " + color);
});
```

### 2.3 函数

#### 函数声明与表达式

```javascript
// 函数声明（有提升）
function add(a, b) {
    return a + b;
}

// 函数表达式（无提升）
const multiply = function(a, b) {
    return a * b;
};

// 箭头函数（ES6+）
const subtract = (a, b) => a - b;

// 多行箭头函数需要大括号和 return
const divide = (a, b) => {
    if (b === 0) throw new Error("除数不能为零");
    return a / b;
};

// 调用
console.log(add(2, 3));      // 5
console.log(multiply(2, 3)); // 6
```

#### 函数参数

```javascript
// 默认参数
function greet(name = "Guest") {
    return "Hello, " + name + "!";
}
greet();          // "Hello, Guest!"
greet("Alice");   // "Hello, Alice!"

// 剩余参数（rest parameters）
function sum(...numbers) {
    return numbers.reduce((acc, n) => acc + n, 0);
}
sum(1, 2, 3, 4);  // 10

// 解构参数
function printUser({ name, age }) {
    console.log(name + " is " + age + " years old");
}
printUser({ name: "Bob", age: 30 });
```

### 2.4 闭包（Closure）

闭包是 JavaScript 最重要的概念之一，也是理解许多安全模式的基础。

```javascript
// 闭包：函数可以访问其外部作用域的变量，即使外部函数已经返回
function createCounter() {
    let count = 0;  // 私有变量
    
    return {
        increment: function() {
            count++;
            return count;
        },
        decrement: function() {
            count--;
            return count;
        },
        getCount: function() {
            return count;
        }
    };
}

const counter = createCounter();
console.log(counter.increment());  // 1
console.log(counter.increment());  // 2
console.log(counter.getCount());   // 2
// console.log(count);  // 错误：count 是私有变量，外部无法直接访问
```

> **安全意义**：闭包可以用来实现**私有变量**和**封装**，但也可能导致**内存泄漏**。在前端安全中，理解闭包是分析混淆代码、理解模块化模式的基础。

### 2.5 对象与原型链

#### 对象基础

```javascript
// 对象字面量
const person = {
    name: "Alice",
    age: 25,
    greet: function() {
        return "Hello, I'm " + this.name;
    }
};

console.log(person.name);       // "Alice"
console.log(person["age"]);     // 25
console.log(person.greet());    // "Hello, I'm Alice"

// 动态添加属性
person.email = "alice@example.com";
person["phone"] = "1234567890";

// 删除属性
delete person.phone;

// 检查属性是否存在
console.log("name" in person);           // true
console.log(person.hasOwnProperty("name")); // true
```

#### 原型链

JavaScript 是基于**原型**的面向对象语言，每个对象都有一个原型（`__proto__`），指向另一个对象。

```javascript
// 构造函数
function User(name, email) {
    this.name = name;
    this.email = email;
}

// 原型方法（所有实例共享）
User.prototype.greet = function() {
    return "Hello, I'm " + this.name;
};

// 创建实例
const alice = new User("Alice", "alice@example.com");
const bob = new User("Bob", "bob@example.com");

console.log(alice.greet());  // "Hello, I'm Alice"
console.log(bob.greet());    // "Hello, I'm Bob"

// 原型链查找：alice → User.prototype → Object.prototype → null
console.log(alice.__proto__ === User.prototype);       // true
console.log(User.prototype.__proto__ === Object.prototype); // true
console.log(Object.prototype.__proto__);               // null
```

> **安全意义**：**原型链污染（Prototype Pollution）** 是一种常见的 JavaScript 安全漏洞。攻击者通过修改 `Object.prototype` 等原型对象，可以影响所有对象，导致权限绕过、代码执行等严重后果。

```javascript
// 原型链污染示例（防御视角）
const obj = {};
console.log(obj.isAdmin);  // undefined

// 如果攻击者能污染原型
obj.__proto__.isAdmin = true;

const anotherObj = {};
console.log(anotherObj.isAdmin);  // true！所有对象都被污染了

// 防御：使用 Object.create(null) 创建无原型对象
const safeObj = Object.create(null);
safeObj.name = "test";
// safeObj 没有原型，不会被原型链污染影响
```

#### ES6 Class 语法

```javascript
// class 是原型的语法糖
class User {
    constructor(name, email) {
        this.name = name;
        this.email = email;
    }
    
    greet() {
        return `Hello, I'm ${this.name}`;
    }
    
    // 静态方法
    static createGuest() {
        return new User("Guest", "guest@example.com");
    }
}

// 继承
class Admin extends User {
    constructor(name, email, role) {
        super(name, email);  // 调用父类构造函数
        this.role = role;
    }
    
    manageUsers() {
        return "Managing users...";
    }
}

const admin = new Admin("SuperAdmin", "admin@example.com", "superadmin");
console.log(admin.greet());       // "Hello, I'm SuperAdmin"
console.log(admin.manageUsers()); // "Managing users..."
```

### 2.6 数组

```javascript
// 创建数组
const fruits = ["apple", "banana", "orange"];
const numbers = new Array(1, 2, 3, 4, 5);

// 访问元素
console.log(fruits[0]);      // "apple"
console.log(fruits.length);  // 3

// 常用方法
fruits.push("grape");        // 末尾添加：["apple", "banana", "orange", "grape"]
fruits.pop();                // 末尾删除：返回 "grape"
fruits.unshift("mango");     // 开头添加
fruits.shift();              // 开头删除
fruits.slice(1, 3);          // 切片（不修改原数组）：["banana", "orange"]
fruits.indexOf("banana");    // 索引：1
fruits.includes("apple");    // 是否包含：true

// 迭代方法（安全代码中大量使用）
const nums = [1, 2, 3, 4, 5];

// map：映射转换
const doubled = nums.map(n => n * 2);        // [2, 4, 6, 8, 10]

// filter：筛选
const evens = nums.filter(n => n % 2 === 0); // [2, 4]

// reduce：归约
const sum = nums.reduce((acc, n) => acc + n, 0); // 15

// find：查找第一个匹配
const firstEven = nums.find(n => n % 2 === 0); // 2

// some / every：是否有/全部满足
const hasLarge = nums.some(n => n > 4);       // true
const allPositive = nums.every(n => n > 0);   // true
```

### 2.7 JSON 处理

```javascript
// JSON 序列化（对象 → 字符串）
const user = { name: "Alice", age: 25, isAdmin: false };
const jsonStr = JSON.stringify(user);
console.log(jsonStr);  // '{"name":"Alice","age":25,"isAdmin":false}'

// JSON 解析（字符串 → 对象）
const parsed = JSON.parse(jsonStr);
console.log(parsed.name);  // "Alice"

// 安全注意事项
try {
    const badJson = "{ name: 'Alice' }";  // 不是合法 JSON（属性名没双引号，单引号）
    JSON.parse(badJson);  // 抛出 SyntaxError
} catch (e) {
    console.log("JSON 解析错误:", e.message);
}

// JSON.parse 安全吗？
// 安全：它不会执行代码（不像 eval）
// 但需要用 try/catch 包裹，防止非法输入导致崩溃
```

> **安全提示**：永远不要用 `eval()` 解析 JSON！`eval()` 会执行字符串中的代码，存在严重的代码注入风险。始终使用 `JSON.parse()`。

### 2.8 DOM 操作与事件

DOM（Document Object Model）是 HTML 文档的编程接口，JavaScript 通过 DOM 操作网页。

#### 选择元素

```javascript
// 常用选择方法
const byId = document.getElementById("myElement");
const byClass = document.getElementsByClassName("myClass");  // HTMLCollection
const byTag = document.getElementsByTagName("div");          // HTMLCollection
const firstMatch = document.querySelector(".myClass");       // 第一个匹配
const allMatches = document.querySelectorAll(".myClass");    // NodeList
```

#### 修改内容与属性

```javascript
const el = document.getElementById("test");

// 内容操作
el.textContent = "安全的文本";        // ✅ 安全，不会解析 HTML
el.innerHTML = "<b>危险</b>";         // ⚠️ 危险！可能导致 XSS
el.innerText = "纯文本内容";           // ✅ 安全

// 属性操作
el.setAttribute("href", "https://example.com");
el.getAttribute("data-id");
el.classList.add("highlight");
el.classList.remove("highlight");
el.classList.toggle("active");

// 样式操作
el.style.color = "red";
el.style.fontSize = "16px";
```

> **XSS 风险关键点**：
> - `textContent` / `innerText` → 安全，只设置纯文本
> - `innerHTML` / `outerHTML` / `document.write()` → 危险，会解析 HTML，可能导致 DOM XSS
> - `setAttribute("href", ...)` → 需检查协议（防止 `javascript:` 伪协议）

#### 事件处理

```javascript
const btn = document.getElementById("myBtn");

// 添加事件监听器
btn.addEventListener("click", function(event) {
    console.log("按钮被点击了");
    console.log("事件目标:", event.target);
});

// 常见事件类型
// - 鼠标：click, dblclick, mouseover, mouseout, mousedown, mouseup
// - 键盘：keydown, keyup, keypress
// - 表单：submit, change, input, focus, blur
// - 文档：DOMContentLoaded, load, beforeunload
// - 其他：scroll, resize, error

// 事件委托（高效处理大量子元素事件）
const list = document.getElementById("myList");
list.addEventListener("click", function(event) {
    if (event.target.tagName === "LI") {
        console.log("点击了列表项:", event.target.textContent);
    }
});
```

### 2.9 异步编程

#### Promise

```javascript
// Promise 基础
const fetchData = new Promise((resolve, reject) => {
    // 模拟异步操作
    setTimeout(() => {
        const success = true;
        if (success) {
            resolve({ data: "获取成功" });
        } else {
            reject(new Error("获取失败"));
        }
    }, 1000);
});

// 使用 .then / .catch
fetchData
    .then(result => {
        console.log(result);  // { data: "获取成功" }
    })
    .catch(error => {
        console.error(error);
    })
    .finally(() => {
        console.log("操作完成");
    });

// Promise 链式调用
fetchData
    .then(result => processData(result))
    .then(processed => saveData(processed))
    .catch(handleError);
```

#### async / await

```javascript
// async/await 是 Promise 的语法糖，更易读
async function fetchUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("获取用户数据失败:", error);
        throw error;  // 向上抛出，让调用者处理
    }
}

// 并行执行多个异步操作
async function fetchAllData() {
    const [users, posts, comments] = await Promise.all([
        fetchUsers(),
        fetchPosts(),
        fetchComments()
    ]);
    return { users, posts, comments };
}
```

> **安全提示**：异步代码中要特别注意错误处理，未捕获的 Promise 异常可能导致应用崩溃或状态不一致。同时，`fetch` 默认不会拒绝 HTTP 错误状态（如 404、500），需要手动检查 `response.ok`。

### 2.10 正则表达式

```javascript
// 创建正则
const pattern1 = /hello/i;            // 字面量（推荐）
const pattern2 = new RegExp("hello", "i");  // 构造函数

// 常用修饰符
// - g: 全局匹配
// - i: 忽略大小写
// - m: 多行模式
// - s: 点号匹配换行符

// 常用方法
const text = "User email: alice@example.com, bob@test.org";

// test：测试是否匹配
const hasEmail = /\S+@\S+\.\S+/.test(text);  // true

// match：获取匹配结果
const emails = text.match(/\S+@\S+\.\S+/g);  // ["alice@example.com", "bob@test.org"]

// replace：替换
const masked = text.replace(/(\S+)@(\S+\.\S+)/g, "***@$2");
// "User email: ***@example.com, ***@test.org"

// exec：循环匹配
const re = /\S+@\S+\.\S+/g;
let match;
while ((match = re.exec(text)) !== null) {
    console.log("找到邮箱:", match[0], "位置:", match.index);
}
```

> **安全提示**：正则表达式可能导致**ReDoS（正则表达式拒绝服务）**——某些恶意输入可以让正则匹配耗时指数级增长。避免使用嵌套量词（如 `(a+)+`），对用户输入的正则要进行限制。

---

## 三、Web 安全核心用法

### 3.1 XSS 原理与防护

XSS（Cross-Site Scripting，跨站脚本攻击）是最常见的 Web 安全漏洞之一。攻击者注入恶意脚本到网页中，其他用户访问时执行。

#### XSS 三种类型

| 类型 | 说明 | 典型场景 | 危害等级 |
|------|------|---------|---------|
| **存储型 XSS** | 恶意脚本存储在服务器数据库中，每个访问者都会执行 | 评论区、用户资料、论坛帖子 | 🔴 高 |
| **反射型 XSS** | 恶意脚本通过 URL 参数传递，服务器反射到页面中 | 搜索结果页、错误提示页 | 🟠 中 |
| **DOM 型 XSS** | 恶意脚本在客户端 JS 中执行，不经过服务器 | URL hash 处理、JS 操作 DOM | 🟡 中-高 |

#### XSS 防御方法

```javascript
// 危险：直接使用 innerHTML
function renderUserInput_bad(input) {
    document.getElementById("output").innerHTML = input;
    // 攻击者输入 <script>stealCookies()</script> 就会执行
}

// 安全：使用 textContent
function renderUserInput_good(input) {
    document.getElementById("output").textContent = input;
    // 文本会被转义，不会执行
}

// 如果必须使用 HTML，需要正确转义
function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
// 或者使用 DOMPurify 库（推荐）
```

#### XSS 防护层次

| 层次 | 措施 | 说明 |
|------|------|------|
| **输入验证** | 服务端校验输入格式 | 白名单验证优于黑名单 |
| **输出编码** | 根据上下文正确转义 | HTML/JS/CSS/URL 编码方式不同 |
| **CSP** | 内容安全策略 | 限制脚本来源，禁止内联脚本 |
| **HttpOnly** | Cookie 设置 HttpOnly | XSS 无法窃取 Cookie |
| **输入长度限制** | 限制输入长度 | 减小攻击面 |

### 3.2 CSRF 原理与防护

CSRF（Cross-Site Request Forgery，跨站请求伪造）：攻击者诱导用户访问恶意网站，利用用户已登录的身份，以用户名义发送请求。

#### CSRF 原理

```
用户已登录 bank.com
  ↓
用户访问 attacker.com（攻击者控制的网站）
  ↓
attacker.com 页面中隐藏了一个请求：bank.com/transfer?to=hacker&amount=1000
  ↓
浏览器自动携带 bank.com 的 Cookie 发送请求
  ↓
银行服务器认为是用户本人操作，转账成功
```

#### CSRF 防御方法

| 方法 | 说明 | 有效性 |
|------|------|--------|
| **CSRF Token** | 每个请求携带随机 Token，服务端验证 | ✅ 最常用，有效 |
| **SameSite Cookie** | Cookie 设置 SameSite=Strict/Lax | ✅ 现代浏览器支持 |
| **验证 Referer** | 检查请求来源 | ⚠️ 可被绕过 |
| **验证码** | 关键操作需要验证码 | ✅ 有效但影响体验 |
| **重新认证** | 敏感操作要求重新输入密码 | ✅ 最安全但最繁琐 |

#### CSRF Token 实现原理

```javascript
// 服务端生成 Token 并放入页面
// <meta name="csrf-token" content="abc123xyz...">

// 前端请求时带上 Token
async function postData(url, data) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": csrfToken  // 放在请求头中
        },
        body: JSON.stringify(data)
    });
    return response.json();
}
```

### 3.3 同源策略与 CORS

#### 同源策略（Same-Origin Policy）

同源策略是浏览器最核心的安全机制，限制不同源之间的资源访问。

**同源的定义**：协议 + 域名 + 端口 都相同

| URL | 与 http://example.com 是否同源 | 原因 |
|-----|-------------------------------|------|
| `http://example.com/page` | ✅ 是 | 同协议、同域名、同端口 |
| `https://example.com` | ❌ 否 | 协议不同（http vs https） |
| `http://api.example.com` | ❌ 否 | 域名不同 |
| `http://example.com:8080` | ❌ 否 | 端口不同（默认 80 vs 8080） |
| `http://example.org` | ❌ 否 | 域名不同 |

#### CORS（Cross-Origin Resource Sharing）

CORS 是一种机制，允许服务器声明哪些源有权访问其资源。

```javascript
// 简单请求：GET/HEAD/POST + 特定 Content-Type
// 浏览器直接发送请求，带上 Origin 头
// 服务器返回 Access-Control-Allow-Origin 头

// 预检请求（Preflight）：PUT/DELETE/自定义头 等
// 浏览器先发送 OPTIONS 请求询问服务器是否允许
// 服务器返回允许的方法、头、凭证等
// 确认后才发送实际请求

// 常见 CORS 响应头
// - Access-Control-Allow-Origin: https://example.com 或 *
// - Access-Control-Allow-Methods: GET, POST, PUT, DELETE
// - Access-Control-Allow-Headers: Content-Type, X-Custom
// - Access-Control-Allow-Credentials: true
// - Access-Control-Max-Age: 86400
```

> **安全提示**：
> - 不要设置 `Access-Control-Allow-Origin: *` 且同时 `Allow-Credentials: true`（浏览器会拒绝）
> - 使用白名单而不是 `*`，特别是涉及敏感数据的接口
> - 配置不当的 CORS 可能导致数据泄露

### 3.4 前端加密与混淆分析

#### 常见前端加密场景

| 场景 | 加密方式 | 安全说明 |
|------|---------|---------|
| 密码传输 | HTTPS（TLS） | 前端加密密码不能替代 HTTPS |
| 本地存储 | Web Crypto API | localStorage 不安全，敏感数据不要存 |
| 敏感数据 | AES 对称加密 | 密钥不能硬编码在前端 |
| 数据完整性 | HMAC / 签名 | 验证数据未被篡改 |

```javascript
// 使用 Web Crypto API 进行 SHA-256 哈希
async function sha256(message) {
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest("SHA-256", msgBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
    return hashHex;
}

// 注意：前端哈希不能替代服务端密码哈希
// 因为攻击者可以直接抓包获取哈希值，等同于密码
```

#### 代码混淆与反混淆

| 混淆技术 | 说明 | 反混淆方法 |
|---------|------|-----------|
| 变量名混淆 | 变量改为 a, b, c... | 格式化代码，逐步分析 |
| 字符串加密 | 字符串加密存储，运行时解密 | 断点调试，hook 解密函数 |
| 控制流平坦化 | 打乱代码执行流程 | 静态分析工具、AST 还原 |
| 死代码注入 | 插入无用代码干扰分析 | 动态调试，代码覆盖 |
| 虚拟机保护 | 自定义字节码 + 虚拟机 | 分析虚拟机指令集 |

> **安全研究提示**：分析混淆代码是前端逆向和恶意脚本分析的重要技能。常用工具包括 Chrome DevTools、AST 工具（Babel/Acorn）、js-beautify、deobfuscate.io 等。

### 3.5 浏览器开发者工具使用

Chrome DevTools 是 Web 安全分析的核心工具。

| 面板 | 用途 | 安全场景 |
|------|------|---------|
| **Elements** | 查看/修改 DOM 和 CSS | 检查 XSS 注入点、DOM 变化 |
| **Console** | 执行 JS、查看日志 | 测试 Payload、调试脚本 |
| **Sources** | 查看/调试 JS 源码 | 分析前端逻辑、下断点调试 |
| **Network** | 查看网络请求 | 分析 API 接口、请求响应 |
| **Application** | 存储、Cookie、缓存 | 检查 Cookie 属性、localStorage |
| **Security** | 安全信息概览 | 查看证书、混合内容、CSP |
| **Performance** | 性能分析 | 分析脚本执行流程 |
| **Memory** | 内存分析 | 检测内存泄漏、分析内存结构 |

---

## 四、常用安全库与工具

### 4.1 前端安全库

| 库名 | 用途 | 说明 |
|------|------|------|
| **DOMPurify** | HTML 净化，防止 XSS | 最流行的 XSS 防护库，支持 HTML/SVG/MathML |
| **js-xss** | XSS 过滤 | 白名单过滤，可自定义规则 |
| **validator.js** | 数据验证 | 字符串验证、消毒，支持多种验证规则 |
| **zxcvbn** | 密码强度检测 | Dropbox 开源的密码强度估算库 |
| **crypto-js** | 加密算法库 | AES、DES、SHA、HMAC 等 |
| **Web Crypto API** | 浏览器原生加密 | 浏览器内置，性能好，更安全 |

```javascript
// DOMPurify 使用示例
import DOMPurify from "dompurify";

const dirty = '<b>Hello</b><script>alert("XSS")</script>';
const clean = DOMPurify.sanitize(dirty);
// clean = '<b>Hello</b>'  （script 被移除）
```

### 4.2 Node.js 安全库

| 库名 | 用途 | 说明 |
|------|------|------|
| **Helmet** | 安全 HTTP 头 | 设置各种安全相关的响应头 |
| **express-mongo-sanitize** | MongoDB 注入防护 | 清理查询中的 `$` 和 `.` 字符 |
| **csurf** | CSRF 防护 | CSRF Token 中间件 |
| **express-rate-limit** | 速率限制 | 防止暴力破解和 DDoS |
| **bcrypt** | 密码哈希 | 安全的密码哈希（带盐） |
| **jsonwebtoken** | JWT 处理 | JWT 的生成和验证 |
| **joi / zod** | 数据验证 | 模式验证，防止非法输入 |

```javascript
// Helmet 使用示例
const express = require("express");
const helmet = require("helmet");

const app = express();
app.use(helmet());  // 一键启用多种安全头
// 包括：CSP, HSTS, X-Frame-Options, X-XSS-Protection 等
```

### 4.3 代码质量与安全检查工具

| 工具 | 用途 | 说明 |
|------|------|------|
| **ESLint** | JS/TS 代码检查 | 可配置安全规则插件 |
| **eslint-plugin-security** | ESLint 安全规则 | 检测常见安全问题 |
| **eslint-plugin-no-unsanitized** | XSS 检测 | 检测不安全的 DOM 操作 |
| **Snyk** | 依赖漏洞扫描 | 检测 npm 包中的已知漏洞 |
| **npm audit** | npm 审计 | npm 内置的漏洞检查 |
| **Retire.js** | 前端依赖检测 | 检测有漏洞的 JS 库版本 |

---

## 五、2026 年免费学习资源

| 资源 | 类型 | 说明 | 链接/获取方式 |
|------|------|------|--------------|
| **MDN Web Docs - JavaScript Guide** | 文档/教程 | 最权威的 JavaScript 参考，由 Mozilla 维护，内容全面准确 | [developer.mozilla.org](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript) |
| **freeCodeCamp JavaScript Curriculum** | 交互式课程 | 完整的 JavaScript 学习路径，从基础到高级，含大量练习 | [freecodecamp.org](https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/) |
| **MDN Dynamic scripting with JavaScript** | 交互式环境 | 交互式 JavaScript 学习，前 40 课免费，动手实践为主 | [MDN Learn JavaScript](https://developer.mozilla.org/zh-CN/docs/Learn/JavaScript) |
| **国家高等教育智慧教育平台** | 在线课程 | Web 前端开发基础之 JavaScript 程序设计，国内高校优质课程 | [智慧教育平台](https://www.icourse163.org/) |
| **JavaScript.info** | 教程 | 现代 JavaScript 教程，从基础到高级，免费在线阅读 | [javascript.info](https://javascript.info/) |
| **Eloquent JavaScript** | 电子书 | 经典 JavaScript 教材，第 4 版免费在线阅读 | [eloquentjavascript.net](https://eloquentjavascript.net/) |
| **Frontend Masters - Intro to JS** | 视频 | 部分免费的高质量视频课程 | [frontendmasters.com](https://frontendmasters.com/) |

> **2026 年时效性标注**：以上资源均为长期维护的官方或社区知名资源。建议以 ES6+ 现代 JavaScript 语法为主要学习方向，同时了解 ES5 旧语法以便阅读和分析遗留代码。

---

## 六、2026 年推荐 GitHub 项目

| 项目 | Stars（约） | 说明 | 适用场景 |
|------|------------|------|---------|
| **hassanireza/learnJavascript** | 数百+ | 30 天 30 个实战项目的免费课程，涵盖变量到 async/await、DOM、OOP | 系统学习 JS，项目驱动 |
| **Prakhar-Sethi/vulnlab** | 数百+ | 交互式 XSS 与 CSRF 安全教育 Web 应用，带 ML 攻击检测器 | XSS/CSRF 学习与防御练习 |
| **ransomleak/training-application-security** | 数百+ | 40 个免费开源安全编码练习，涵盖 SQL 注入等真实漏洞的利用与修复 | 安全编码练习，OWASP Top 10 |
| **secure-code-game** | 数千+ | 在编辑器中通过游戏学习安全编码，浏览器中即可开始 | 趣味学习安全编码 |
| **OWASP/CheatSheetSeries** | 数万+ | OWASP 安全速查表，包含 XSS 防护、CSRF 防护等各种安全主题 | 安全开发参考，防御指南 |
| **shutdownRepo/hackthebox-writeups** | 数千+ | HTB 平台 Web 题解，含大量 JS 相关的 Web 挑战 | Web 渗透学习，实战案例 |
| **s0md3v/Photon** | 数千+ | 快速的 Web 爬虫，可提取 JS 文件、接口、端点等信息 | 信息收集，JS 分析 |

> **⚠️ 免责声明**：以上 GitHub 项目仅供学习研究使用。漏洞环境（如 vulnlab）**仅限在完全授权的测试环境中使用**。未经授权对任何系统进行测试可能违反法律。学习者应重点关注漏洞原理和防御方法。

---

## 七、示例代码文件

`code/` 目录下包含两个可运行的 JavaScript 示例：

| 文件 | 内容 | 运行方式 |
|------|------|---------|
| `basics.js` | JS 基础语法示例：变量、函数、数组、对象、DOM 操作、异步编程、闭包 | Node.js 环境：`node basics.js`；浏览器环境可在控制台粘贴运行 |
| `security_cases.js` | 安全案例集：XSS 输入检测与净化、CSRF Token 生成与验证、前端加密逻辑分析、正则安全检测 | Node.js 环境：`node security_cases.js`；浏览器环境需调整 DOM 相关代码 |

### 7.1 basics.js 内容概览

- 变量与数据类型（var/let/const、类型转换）
- 函数与箭头函数
- 数组操作（map/filter/reduce）
- 对象与原型链
- 闭包
- JSON 处理
- 异步编程（Promise、async/await）
- 正则表达式
- DOM 操作（Node 环境用模拟说明）
- 错误处理

### 7.2 security_cases.js 内容概览

| 案例 | 功能 | 说明 |
|------|------|------|
| **XSS 输入检测与净化** | 检测恶意脚本、HTML 转义、URL 净化 | 防御 DOM XSS、反射型 XSS |
| **CSRF Token 生成与验证** | Token 生成、验证、存储机制 | 理解 CSRF 防护原理 |
| **前端加密逻辑分析** | 哈希计算、Base64 编解码、常见混淆模式识别 | 前端安全分析基础 |
| **正则安全检测** | ReDoS 风险检测、邮箱/IP 安全验证 | 正则安全最佳实践 |

> **运行注意**：
> - 脚本使用 Node.js 兼容语法，可直接用 `node` 命令运行
> - DOM 相关功能在 Node 环境中使用模拟实现，浏览器环境可直接替换为真实 DOM API
> - 所有案例均为防御和学习目的，不包含可直接利用的攻击代码

---

## 附：优化后的提示词模板

```
# 角色
你是一名资深 Web 安全与 JavaScript 专家，精通 XSS/CSRF 等 Web 漏洞原理、前端安全审计、浏览器安全机制和 JS 代码分析。

# 任务
请针对以下 JavaScript / Web 安全任务给出完整方案：
【在此处填入具体任务，如"分析某网站前端 JS 代码中的安全问题"】

# 输出要求
- 漏洞原理说明（攻击 + 防御双视角）
- 代码示例（漏洞代码 + 修复代码对比）
- 检测方法（如何发现此类问题）
- 修复方案（多层次防御建议）
- 相关 CWE / OWASP 编号

# 约束
- 仅限防御、安全研究和授权测试场景
- 攻击代码仅用于原理说明，需做脱敏处理
- 必须给出对应的防御和修复方案
- 强调伦理与法律边界
```

---

> **免责声明**：本文档所有内容仅用于学习、研究和授权环境下的安全测试与防御实践。任何未经授权的测试或攻击行为均属违法。读者应遵守所在地区法律法规，对自己的行为负责。
