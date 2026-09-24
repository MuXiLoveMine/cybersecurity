# JavaScript 基础教程

## 目录

- [一、语言概述与应用场景](#一语言概述与应用场景)
- [二、基础语法](#二基础语法)
- [三、条件判断](#三条件判断)
- [四、循环](#四循环)
- [五、函数](#五函数)
- [六、数组操作](#六数组操作)
- [七、对象/字典](#七对象字典)
- [八、字符串操作](#八字符串操作)
- [九、正则表达式](#九正则表达式)
- [十、网络请求](#十网络请求)
- [十一、Node.js 文件操作](#十一nodejs-文件操作)
- [十二、JavaScript 在 Web 安全中的应用](#十二javascript-在-web-安全中的应用)

---

## 一、语言概述与应用场景

### 1.1 什么是 JavaScript

JavaScript（简称 JS）是一种**轻量级、解释型**的编程语言，最初由 Brendan Eich 在 1995 年为 Netscape 浏览器设计，仅用 10 天完成。它是 Web 前端开发的核心语言之一，与 HTML、CSS 并称为"前端三剑客"。

- **解释型语言**：不需要编译，直接由解释器执行
- **动态类型**：变量类型在运行时确定
- **事件驱动**：擅长处理用户交互和异步操作
- **单线程**：基于事件循环（Event Loop）实现异步

### 1.2 运行环境

JavaScript 可以在多种环境中运行：

| 运行环境 | 说明 | 典型应用 |
|---------|------|---------|
| 浏览器 | 原生支持，通过 V8/SpiderMonkey 等引擎执行 | 网页交互、前端框架 |
| Node.js | 基于 Chrome V8 引擎的服务端运行时 | 后端服务、命令行工具 |
| Electron | 结合 Chromium 和 Node.js | 桌面应用（VS Code、Discord） |
| 移动端 | React Native、Weex 等 | 跨平台移动应用 |

### 1.3 应用场景

1. **Web 前端开发**
   - 网页动态效果与用户交互
   - 前端框架：React、Vue.js、Angular
   - 构建工具：Webpack、Vite

2. **服务端开发（Node.js）**
   - API 服务器
   - 实时通信应用（WebSocket）
   - 微服务架构

3. **网络安全领域**
   - XSS（跨站脚本）攻击与防御
   - CSRF 攻击理解与防护
   - 前端安全审计
   - 编写安全测试脚本
   - Burp Suite 等工具的自定义脚本

4. **其他领域**
   - 桌面应用开发（Electron）
   - 移动应用开发（React Native）
   - 游戏开发（Cocos、Phaser）
   - 机器学习（TensorFlow.js）

---

## 二、基础语法

### 2.1 变量声明

JavaScript 中有三种变量声明方式：

| 关键字 | 作用域 | 重复声明 | 重新赋值 | 声明提升 |
|-------|--------|---------|---------|---------|
| `var` | 函数作用域 | 允许 | 允许 | 是 |
| `let` | 块级作用域 | 不允许 | 允许 | 否（暂时性死区） |
| `const` | 块级作用域 | 不允许 | 不允许 | 否（暂时性死区） |

```javascript
// var - 函数作用域，存在变量提升
var name = "Alice";
var name = "Bob";  // 允许重复声明
name = "Charlie";  // 允许重新赋值

// let - 块级作用域，ES6 推荐
let age = 25;
// let age = 30;  // 错误：不允许重复声明
age = 26;          // 允许重新赋值

// const - 块级作用域，常量声明
const PI = 3.14159;
// PI = 3.14;      // 错误：不允许重新赋值

// 注意：const 声明的对象，其属性可以修改
const person = { name: "Alice" };
person.name = "Bob";  // 允许，因为对象引用未变
```

### 2.2 数据类型

JavaScript 数据类型分为**基本类型**和**引用类型**。

#### 基本类型（值类型）

| 类型 | 说明 | 示例 |
|-----|------|------|
| `string` | 字符串 | `"hello"`、`'world'`、`` `template` `` |
| `number` | 数字（整数和浮点数） | `42`、`3.14`、`NaN`、`Infinity` |
| `boolean` | 布尔值 | `true`、`false` |
| `undefined` | 未定义 | 声明但未赋值的变量 |
| `null` | 空值 | 表示"没有对象" |
| `symbol` | 符号（ES6） | 唯一标识符 |
| `bigint` | 大整数（ES2020） | `123n` |

#### 引用类型

| 类型 | 说明 | 示例 |
|-----|------|------|
| `Object` | 对象 | `{name: "Alice"}` |
| `Array` | 数组 | `[1, 2, 3]` |
| `Function` | 函数 | `function() {}` |
| `Date` | 日期 | `new Date()` |
| `RegExp` | 正则表达式 | `/abc/g` |

```javascript
// 使用 typeof 检查类型
typeof "hello"        // "string"
typeof 42             // "number"
typeof true           // "boolean"
typeof undefined      // "undefined"
typeof null           // "object" （历史遗留问题）
typeof Symbol()       // "symbol"
typeof 123n           // "bigint"
typeof {}             // "object"
typeof []             // "object"
typeof function() {}  // "function"
```

### 2.3 运算符

#### 算术运算符

```javascript
let a = 10, b = 3;

a + b   // 13   加法
a - b   // 7    减法
a * b   // 30   乘法
a / b   // 3.333...  除法
a % b   // 1    取模（余数）
a ** b  // 1000 幂运算（ES7）
a++     // 10   后置递增（先返回后加1）
++a     // 11   前置递增（先加1后返回）
a--     // 10   后置递减
--a     // 9    前置递减
```

#### 赋值运算符

```javascript
let x = 10;
x += 5;   // x = x + 5  → 15
x -= 3;   // x = x - 3  → 12
x *= 2;   // x = x * 2  → 24
x /= 4;   // x = x / 4  → 6
x %= 4;   // x = x % 4  → 2
x **= 3;  // x = x ** 3 → 8
```

#### 比较运算符

```javascript
5 == "5"     // true   相等（自动类型转换）
5 === "5"    // false  严格相等（类型和值都相等）
5 != "5"     // false  不相等（自动类型转换）
5 !== "5"    // true   严格不相等
5 > 3        // true   大于
5 >= 5       // true   大于等于
5 < 3        // false  小于
5 <= 5       // true   小于等于
```

> **安全提示**：推荐使用 `===` 和 `!==` 进行比较，避免类型转换带来的意外行为，减少安全漏洞。

#### 逻辑运算符

```javascript
true && false   // false  逻辑与（两边都为真才为真）
true || false   // true   逻辑或（一边为真就为真）
!true           // false  逻辑非

// 短路求值
let result = a && b;  // 如果 a 为假，直接返回 a，不计算 b
let result = a || b;  // 如果 a 为真，直接返回 a，不计算 b
```

#### 其他运算符

```javascript
// 三元运算符（条件运算符）
let age = 20;
let status = age >= 18 ? "成年" : "未成年";  // "成年"

// typeof 运算符
typeof 42  // "number"

// 空值合并运算符（ES2020）
let value = null ?? "default";  // "default"
let value = 0 ?? "default";     // 0（只有 null/undefined 才触发）

// 可选链运算符（ES2020）
let user = { name: "Alice" };
let city = user.address?.city;  // undefined，不会报错
```

---

## 三、条件判断

### 3.1 if / else 语句

```javascript
let score = 85;

// 基本 if 语句
if (score >= 60) {
    console.log("及格");
}

// if...else 语句
if (score >= 60) {
    console.log("及格");
} else {
    console.log("不及格");
}

// if...else if...else 多分支
if (score >= 90) {
    console.log("优秀");
} else if (score >= 80) {
    console.log("良好");
} else if (score >= 60) {
    console.log("及格");
} else {
    console.log("不及格");
}
```

### 3.2 switch 语句

```javascript
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
    case 5:
        console.log("工作日");
        break;
    default:
        console.log("周末");
}
```

> **注意**：`switch` 使用 `===` 进行比较，每个 case 需要 `break` 语句防止"穿透"。

### 3.3 真值与假值

在 JavaScript 中，以下值在条件判断中被视为 `false`（假值）：

- `false`
- `0`、`-0`、`0n`
- `""`（空字符串）
- `null`
- `undefined`
- `NaN`

其他所有值都被视为 `true`（真值），包括：
- `"0"`（字符串 0）
- `"false"`（字符串 false）
- `[]`（空数组）
- `{}`（空对象）

---

## 四、循环

### 4.1 for 循环

```javascript
// 传统 for 循环
for (let i = 0; i < 5; i++) {
    console.log(i);  // 输出 0, 1, 2, 3, 4
}

// 从后往前遍历
for (let i = 5; i > 0; i--) {
    console.log(i);  // 输出 5, 4, 3, 2, 1
}
```

### 4.2 while 循环

```javascript
let i = 0;
while (i < 5) {
    console.log(i);  // 输出 0, 1, 2, 3, 4
    i++;
}
```

### 4.3 do...while 循环

```javascript
let i = 0;
do {
    console.log(i);  // 输出 0, 1, 2, 3, 4
    i++;
} while (i < 5);
```

> **区别**：`do...while` 至少执行一次循环体，然后再判断条件。

### 4.4 forEach 方法

```javascript
const fruits = ["apple", "banana", "orange"];

fruits.forEach(function(fruit, index, array) {
    console.log(index + ": " + fruit);
});

// 箭头函数写法
fruits.forEach((fruit, index) => {
    console.log(`${index}: ${fruit}`);
});
```

### 4.5 for...in 循环

遍历对象的**可枚举属性**（或数组的索引）：

```javascript
const person = {
    name: "Alice",
    age: 25,
    city: "Beijing"
};

for (let key in person) {
    console.log(key + ": " + person[key]);
}
// 输出：
// name: Alice
// age: 25
// city: Beijing
```

> **注意**：`for...in` 不推荐用于数组遍历，因为它会遍历原型链上的属性。

### 4.6 for...of 循环

遍历**可迭代对象**的值（ES6 引入）：

```javascript
const fruits = ["apple", "banana", "orange"];

for (let fruit of fruits) {
    console.log(fruit);
}
// 输出：apple, banana, orange

// 遍历字符串
for (let char of "hello") {
    console.log(char);
}
// 输出：h, e, l, l, o
```

### 4.7 循环控制语句

```javascript
// break - 跳出循环
for (let i = 0; i < 10; i++) {
    if (i === 5) break;
    console.log(i);  // 输出 0-4
}

// continue - 跳过本次循环
for (let i = 0; i < 5; i++) {
    if (i === 2) continue;
    console.log(i);  // 输出 0, 1, 3, 4
}
```

---

## 五、函数

### 5.1 普通函数

```javascript
// 函数声明（会提升）
function greet(name) {
    return "Hello, " + name + "!";
}

console.log(greet("Alice"));  // "Hello, Alice!"

// 函数表达式（不会提升）
const add = function(a, b) {
    return a + b;
};

console.log(add(2, 3));  // 5
```

### 5.2 箭头函数（ES6）

```javascript
// 基本语法
const add = (a, b) => {
    return a + b;
};

// 简写：只有一个参数时可以省略括号
const double = x => {
    return x * 2;
};

// 简写：函数体只有一行 return 时可以省略花括号和 return
const triple = x => x * 3;

console.log(add(2, 3));    // 5
console.log(double(5));    // 10
console.log(triple(4));    // 12
```

> **箭头函数特点**：
> - 没有自己的 `this`，继承外层的 `this`
> - 不能作为构造函数，不能使用 `new`
> - 没有 `arguments` 对象

### 5.3 匿名函数

```javascript
// 作为函数表达式
const sayHello = function() {
    console.log("Hello!");
};

// 作为回调函数
setTimeout(function() {
    console.log("3秒后执行");
}, 3000);

// 作为立即执行函数（IIFE）
(function() {
    console.log("立即执行");
})();
```

### 5.4 闭包（Closure）

闭包是指有权访问另一个函数作用域中变量的函数。

```javascript
function createCounter() {
    let count = 0;  // 局部变量
    
    return function() {
        count++;
        return count;
    };
}

const counter = createCounter();
console.log(counter());  // 1
console.log(counter());  // 2
console.log(counter());  // 3

// 闭包应用：数据私有化
function createBankAccount(initialBalance) {
    let balance = initialBalance;
    
    return {
        deposit: function(amount) {
            balance += amount;
            return balance;
        },
        withdraw: function(amount) {
            if (amount <= balance) {
                balance -= amount;
                return balance;
            }
            return "余额不足";
        },
        getBalance: function() {
            return balance;
        }
    };
}

const account = createBankAccount(1000);
account.deposit(500);   // 1500
account.withdraw(200);  // 1300
account.getBalance();   // 1300
// account.balance  无法直接访问，实现了数据封装
```

### 5.5 回调函数

```javascript
// 同步回调
function processArray(arr, callback) {
    for (let i = 0; i < arr.length; i++) {
        callback(arr[i], i);
    }
}

processArray([1, 2, 3], function(item, index) {
    console.log(`索引${index}: ${item * 2}`);
});

// 异步回调
console.log("开始");
setTimeout(function() {
    console.log("2秒后执行");
}, 2000);
console.log("结束");
// 输出顺序：开始 → 结束 → 2秒后执行
```

---

## 六、数组操作

### 6.1 创建数组

```javascript
// 字面量方式（推荐）
const fruits = ["apple", "banana", "orange"];

// 构造函数方式
const numbers = new Array(1, 2, 3, 4, 5);

// 创建指定长度的空数组
const emptyArr = new Array(5);  // [empty × 5]

// Array.from
const arrFrom = Array.from("hello");  // ['h', 'e', 'l', 'l', 'o']

// Array.fill
const filled = new Array(3).fill(0);  // [0, 0, 0]
```

### 6.2 增删改查

```javascript
const arr = [1, 2, 3];

// 末尾添加
arr.push(4);          // [1, 2, 3, 4]，返回新长度
// 末尾删除
arr.pop();            // [1, 2, 3]，返回被删除的元素

// 开头添加
arr.unshift(0);       // [0, 1, 2, 3]，返回新长度
// 开头删除
arr.shift();          // [1, 2, 3]，返回被删除的元素

// 任意位置增删
arr.splice(1, 1);     // 从索引1删除1个元素 → [1, 3]
arr.splice(1, 0, 2);  // 从索引1插入元素2 → [1, 2, 3]
arr.splice(1, 1, 5);  // 从索引1替换1个元素 → [1, 5, 3]

// 访问元素
console.log(arr[0]);  // 1（通过索引访问）
console.log(arr[10]); // undefined（越界访问不报错）

// 查找索引
arr.indexOf(3);       // 2，找不到返回 -1
arr.includes(3);      // true，是否包含
arr.find(x => x > 2); // 3，找到第一个满足条件的元素
arr.findIndex(x => x > 2); // 2，找到第一个满足条件的索引
```

### 6.3 遍历数组

```javascript
const arr = ["a", "b", "c"];

// for 循环
for (let i = 0; i < arr.length; i++) {
    console.log(arr[i]);
}

// for...of
for (let item of arr) {
    console.log(item);
}

// forEach
arr.forEach((item, index) => {
    console.log(`${index}: ${item}`);
});

// map - 映射转换（返回新数组）
const numbers = [1, 2, 3];
const doubled = numbers.map(x => x * 2);  // [2, 4, 6]

// filter - 过滤（返回新数组）
const evens = numbers.filter(x => x % 2 === 0);  // [2]

// reduce - 归约（返回单个值）
const sum = numbers.reduce((acc, cur) => acc + cur, 0);  // 6

// some - 是否有至少一个满足条件
const hasEven = numbers.some(x => x % 2 === 0);  // true

// every - 是否所有都满足条件
const allEven = numbers.every(x => x % 2 === 0);  // false
```

### 6.4 其他常用方法

```javascript
const arr = [3, 1, 4, 1, 5];

// 排序
arr.sort();              // [1, 1, 3, 4, 5]（按字符串排序）
arr.sort((a, b) => a - b);  // [1, 1, 3, 4, 5]（数字升序）
arr.sort((a, b) => b - a);  // [5, 4, 3, 1, 1]（数字降序）

// 反转
arr.reverse();           // [5, 4, 3, 1, 1]

// 拼接
arr.join("-");           // "5-4-3-1-1"

// 截取
arr.slice(1, 3);         // [4, 3]（不修改原数组）

// 合并
const arr2 = [6, 7];
const merged = arr.concat(arr2);  // [5, 4, 3, 1, 1, 6, 7]

// 扁平化
const nested = [1, [2, [3, 4]]];
nested.flat();           // [1, 2, [3, 4]]（默认1层）
nested.flat(2);          // [1, 2, 3, 4]
```

---

## 七、对象/字典

### 7.1 创建对象

```javascript
// 字面量方式（推荐）
const person = {
    name: "Alice",
    age: 25,
    city: "Beijing",
    "full name": "Alice Wang"  // 属性名有空格需加引号
};

// 构造函数方式
const person2 = new Object();
person2.name = "Bob";
person2.age = 30;

// 计算属性名
const key = "email";
const user = {
    name: "Charlie",
    [key]: "charlie@example.com"
};
// { name: "Charlie", email: "charlie@example.com" }
```

### 7.2 属性访问

```javascript
const person = { name: "Alice", age: 25 };

// 点语法
console.log(person.name);  // "Alice"

// 方括号语法
console.log(person["age"]);  // 25
console.log(person["full name"]);  // 必须用方括号访问有空格的属性

// 动态属性名
const prop = "name";
console.log(person[prop]);  // "Alice"

// 访问不存在的属性
console.log(person.height);  // undefined（不会报错）

// 可选链（ES2020）
console.log(person.address?.city);  // undefined，不会报错
```

### 7.3 增删改查

```javascript
const person = { name: "Alice" };

// 添加属性
person.age = 25;
person["city"] = "Beijing";

// 修改属性
person.name = "Alice Wang";

// 删除属性
delete person.age;

// 检查属性是否存在
"name" in person;              // true（包括继承的属性）
person.hasOwnProperty("name"); // true（只检查自身属性）
```

### 7.4 遍历对象

```javascript
const person = {
    name: "Alice",
    age: 25,
    city: "Beijing"
};

// for...in 遍历可枚举属性（包括原型链）
for (let key in person) {
    if (person.hasOwnProperty(key)) {
        console.log(`${key}: ${person[key]}`);
    }
}

// Object.keys - 获取所有键名数组
const keys = Object.keys(person);  // ["name", "age", "city"]
keys.forEach(key => console.log(key));

// Object.values - 获取所有值数组
const values = Object.values(person);  // ["Alice", 25, "Beijing"]

// Object.entries - 获取键值对数组
const entries = Object.entries(person);
// [["name", "Alice"], ["age", 25], ["city", "Beijing"]]

for (let [key, value] of entries) {
    console.log(`${key}: ${value}`);
}
```

### 7.5 常用方法

```javascript
const target = { a: 1, b: 2 };
const source = { b: 3, c: 4 };

// Object.assign - 合并对象
const merged = Object.assign({}, target, source);
// { a: 1, b: 3, c: 4 }（后面的覆盖前面的）

// 展开运算符（ES6）
const merged2 = { ...target, ...source };
// { a: 1, b: 3, c: 4 }

// Object.freeze - 冻结对象（不可修改）
const frozen = Object.freeze({ x: 1 });
// frozen.x = 2;  // 严格模式下报错，非严格模式下静默失败

// Object.seal - 密封对象（不可增删，但可修改）
const sealed = Object.seal({ y: 2 });
sealed.y = 3;      // 允许修改
// sealed.z = 4;  // 不允许添加
```

---

## 八、字符串操作

### 8.1 字符串创建

```javascript
// 单引号
const str1 = 'hello';

// 双引号
const str2 = "world";

// 模板字符串（反引号，ES6）
const name = "Alice";
const greeting = `Hello, ${name}!`;  // "Hello, Alice!"

// 多行字符串
const multiLine = `
    第一行
    第二行
    第三行
`;

// String 构造函数
const strObj = new String("hello");  // 字符串对象，不推荐
```

### 8.2 常用方法

```javascript
const str = "Hello, World!";

// 获取长度
str.length;  // 13

// 字符访问
str.charAt(0);       // "H"
str[0];              // "H"
str.charCodeAt(0);   // 72（ASCII 码）

// 查找
str.indexOf("World");   // 7，找不到返回 -1
str.lastIndexOf("l");   // 10
str.includes("Hello");  // true
str.startsWith("Hello"); // true
str.endsWith("!");      // true

// 截取
str.slice(0, 5);     // "Hello"（支持负数）
str.substring(7, 12); // "World"（不支持负数）
str.substr(7, 5);    // "World"（已弃用）

// 大小写转换
str.toUpperCase();   // "HELLO, WORLD!"
str.toLowerCase();   // "hello, world!"

// 去除空白
"  hello  ".trim();    // "hello"
"  hello  ".trimStart(); // "hello  "
"  hello  ".trimEnd();   // "  hello"

// 替换
str.replace("World", "JavaScript");  // "Hello, JavaScript!"
str.replace(/l/g, "L");              // "HeLLo, WorLd!"

// 分割
"a,b,c".split(",");   // ["a", "b", "c"]
"hello".split("");    // ["h", "e", "l", "l", "o"]

// 拼接
"Hello".concat(" ", "World");  // "Hello World"

// 重复
"ab".repeat(3);      // "ababab"

// 填充
"5".padStart(3, "0");   // "005"
"5".padEnd(3, "0");     // "500"
```

### 8.3 模板字符串

```javascript
const name = "Alice";
const age = 25;

// 变量插值
const info = `姓名: ${name}, 年龄: ${age}`;

// 表达式计算
const result = `1 + 2 = ${1 + 2}`;  // "1 + 2 = 3"

// 调用函数
function toUpper(str) {
    return str.toUpperCase();
}
const msg = `HELLO: ${toUpper("world")}`;  // "HELLO: WORLD"

// 嵌套模板字符串
const isAdmin = true;
const status = `用户状态: ${isAdmin ? `管理员` : `普通用户`}`;
```

---

## 九、正则表达式

### 9.1 创建正则表达式

```javascript
// 字面量方式（推荐）
const regex1 = /abc/;
const regex2 = /abc/gi;  // 带修饰符

// 构造函数方式
const regex3 = new RegExp("abc");
const regex4 = new RegExp("abc", "gi");

// 动态构建正则
const pattern = "user\\d+";
const regex5 = new RegExp(pattern, "g");
```

#### 修饰符

| 修饰符 | 说明 |
|-------|------|
| `g` | 全局匹配（查找所有匹配项） |
| `i` | 忽略大小写 |
| `m` | 多行模式 |
| `s` | 点号匹配换行符 |
| `u` | Unicode 模式 |

### 9.2 test 方法

测试字符串是否匹配正则，返回布尔值：

```javascript
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

emailRegex.test("user@example.com");  // true
emailRegex.test("invalid-email");     // false

// 安全应用：验证用户输入
const ipRegex = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/;
ipRegex.test("192.168.1.1");  // true
```

### 9.3 exec 方法

执行匹配，返回匹配结果数组或 `null`：

```javascript
const regex = /(\d+)-(\d+)/g;
const str = "范围：100-200 和 300-400";

let match;
while ((match = regex.exec(str)) !== null) {
    console.log(`匹配: ${match[0]}, 组1: ${match[1]}, 组2: ${match[2]}`);
}
// 匹配: 100-200, 组1: 100, 组2: 200
// 匹配: 300-400, 组1: 300, 组2: 400
```

### 9.4 match 方法

字符串的方法，返回匹配结果：

```javascript
const str = "Hello World Hello";

// 不带 g 修饰符，返回第一个匹配及捕获组
str.match(/Hello/);
// ["Hello", index: 0, input: "Hello World Hello"]

// 带 g 修饰符，返回所有匹配的数组
str.match(/Hello/g);
// ["Hello", "Hello"]

// 没有匹配返回 null
str.match(/Bye/g);  // null
```

### 9.5 replace 方法

替换匹配的内容：

```javascript
const str = "Hello World";

// 简单替换
str.replace("World", "JavaScript");  // "Hello JavaScript"

// 正则替换
str.replace(/o/g, "0");  // "Hell0 W0rld"

// 使用函数作为替换参数
const result = "user123".replace(/\d+/, match => {
    return "[" + match + "]";
});
// "user[123]"

// 安全应用：敏感信息脱敏
const phone = "13812345678";
const masked = phone.replace(/(\d{3})\d{4}(\d{4})/, "$1****$2");
// "138****5678"
```

### 9.6 search 方法

查找第一个匹配的位置，返回索引，找不到返回 `-1`：

```javascript
const str = "Hello World";
str.search(/World/);  // 6
str.search(/Bye/);    // -1
```

### 9.7 常用正则模式

```javascript
// 邮箱
const email = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// 手机号码（中国）
const phone = /^1[3-9]\d{9}$/;

// URL
const url = /^https?:\/\/.+/;

// IP 地址（IPv4）
const ipv4 = /^(\d{1,3}\.){3}\d{1,3}$/;

// 身份证号
const idCard = /^\d{17}[\dXx]$/;

// 中文字符
const chinese = /[\u4e00-\u9fa5]/;

// HTML 标签
const htmlTag = /<[^>]+>/g;

// SQL 注入特征（简单检测）
const sqlInjection = /('|--|union|select|insert|delete|drop)/i;
```

---

## 十、网络请求

### 10.1 Node.js http/https 模块

#### 发送 GET 请求

```javascript
const https = require('https');

https.get('https://api.example.com/data', (res) => {
    let data = '';

    // 接收数据
    res.on('data', (chunk) => {
        data += chunk;
    });

    // 接收完成
    res.on('end', () => {
        console.log('响应状态码:', res.statusCode);
        console.log('响应数据:', data);
    });

}).on('error', (err) => {
    console.error('请求错误:', err.message);
});
```

#### 发送 POST 请求

```javascript
const http = require('http');

const postData = JSON.stringify({
    username: 'admin',
    password: '123456'
});

const options = {
    hostname: 'localhost',
    port: 3000,
    path: '/api/login',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
    }
};

const req = http.request(options, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
        console.log('登录结果:', data);
    });
});

req.on('error', (err) => {
    console.error('请求失败:', err);
});

req.write(postData);
req.end();
```

#### 创建简单 HTTP 服务器

```javascript
const http = require('http');

const server = http.createServer((req, res) => {
    // 设置响应头
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });

    // 根据请求路径返回不同内容
    if (req.url === '/') {
        res.end('<h1>首页</h1><p>欢迎访问！</p>');
    } else if (req.url === '/about') {
        res.end('<h1>关于我们</h1>');
    } else {
        res.writeHead(404);
        res.end('<h1>404 Not Found</h1>');
    }
});

server.listen(3000, () => {
    console.log('服务器运行在 http://localhost:3000');
});
```

### 10.2 fetch API（浏览器/Node 18+）

```javascript
// GET 请求
fetch('https://api.example.com/users')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('错误:', error));

// POST 请求
fetch('https://api.example.com/users', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        name: 'Alice',
        email: 'alice@example.com'
    })
})
    .then(response => response.json())
    .then(data => console.log(data));

// async/await 写法
async function getUserData() {
    try {
        const response = await fetch('https://api.example.com/users/1');
        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.error('请求失败:', error);
    }
}
```

### 10.3 axios（第三方库）

```javascript
const axios = require('axios');

// GET 请求
axios.get('https://api.example.com/users')
    .then(response => {
        console.log(response.data);
    })
    .catch(error => {
        console.error(error);
    });

// POST 请求
axios.post('https://api.example.com/users', {
    name: 'Alice',
    age: 25
})
    .then(res => console.log(res.data));

// async/await
async function fetchData() {
    try {
        const res = await axios.get('https://api.example.com/users', {
            params: { page: 1, limit: 10 },
            headers: { 'Authorization': 'Bearer token123' }
        });
        console.log(res.data);
    } catch (err) {
        console.error(err.message);
    }
}
```

---

## 十一、Node.js 文件操作

### 11.1 fs 模块引入

Node.js 内置 `fs` 模块提供文件系统操作，支持同步和异步两种方式。

```javascript
const fs = require('fs');
const path = require('path');
```

### 11.2 读取文件

```javascript
// 异步读取
fs.readFile('file.txt', 'utf-8', (err, data) => {
    if (err) {
        console.error('读取失败:', err);
        return;
    }
    console.log('文件内容:', data);
});

// 同步读取
try {
    const data = fs.readFileSync('file.txt', 'utf-8');
    console.log('文件内容:', data);
} catch (err) {
    console.error('读取失败:', err);
}

// Promise 方式（fs.promises）
async function readFileAsync() {
    try {
        const data = await fs.promises.readFile('file.txt', 'utf-8');
        console.log(data);
    } catch (err) {
        console.error(err);
    }
}
```

### 11.3 写入文件

```javascript
const content = 'Hello, Node.js!';

// 异步写入（覆盖）
fs.writeFile('output.txt', content, 'utf-8', (err) => {
    if (err) {
        console.error('写入失败:', err);
        return;
    }
    console.log('写入成功');
});

// 同步写入
fs.writeFileSync('output.txt', content, 'utf-8');

// 追加写入
fs.appendFile('log.txt', '新的日志行\n', 'utf-8', (err) => {
    if (err) console.error(err);
});
```

### 11.4 目录操作

```javascript
// 创建目录
fs.mkdir('newDir', { recursive: true }, (err) => {
    if (err) console.error(err);
});

// 读取目录
fs.readdir('.', (err, files) => {
    if (err) {
        console.error(err);
        return;
    }
    console.log('目录内容:', files);
});

// 检查文件/目录是否存在
fs.exists('file.txt', (exists) => {
    console.log('文件存在:', exists);
});

// 获取文件信息
fs.stat('file.txt', (err, stats) => {
    if (err) console.error(err);
    console.log('是文件:', stats.isFile());
    console.log('是目录:', stats.isDirectory());
    console.log('大小:', stats.size, '字节');
});

// 删除文件
fs.unlink('file.txt', (err) => {
    if (err) console.error(err);
});

// 删除目录
fs.rmdir('emptyDir', (err) => {
    if (err) console.error(err);
});
```

### 11.5 path 模块常用方法

```javascript
const path = require('path');

// 拼接路径
path.join('/user', 'local', 'bin');  // '/user/local/bin'

// 解析路径
path.resolve('file.txt');  // 返回绝对路径

// 获取文件名
path.basename('/path/to/file.txt');      // 'file.txt'
path.basename('/path/to/file.txt', '.txt');  // 'file'

// 获取目录名
path.dirname('/path/to/file.txt');  // '/path/to'

// 获取扩展名
path.extname('/path/to/file.txt');  // '.txt'

// 解析路径对象
path.parse('/path/to/file.txt');
// { root: '/', dir: '/path/to', base: 'file.txt', ext: '.txt', name: 'file' }
```

---

## 十二、JavaScript 在 Web 安全中的应用

### 12.1 XSS（跨站脚本攻击）

XSS 是最常见的 Web 安全漏洞之一，攻击者通过注入恶意脚本到网页中，使其在用户浏览器中执行。

#### XSS 类型

1. **反射型 XSS**：恶意脚本通过 URL 参数传递，服务端直接输出到页面
2. **存储型 XSS**：恶意脚本存储在数据库中，其他用户访问时执行
3. **DOM 型 XSS**：客户端 JavaScript 处理不当导致的 XSS

#### JavaScript 防御方法

```javascript
// 1. HTML 转义，防止 XSS
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// 2. 使用 textContent 代替 innerHTML
// 危险：element.innerHTML = userInput;
// 安全：element.textContent = userInput;

// 3. URL 参数编码
const safeUrl = encodeURIComponent(userInput);

// 4. 设置 Cookie 的 HttpOnly 属性（防止 JS 读取 Cookie）
// 服务端设置：Set-Cookie: session=xxx; HttpOnly

// 5. Content Security Policy (CSP)
// <meta http-equiv="Content-Security-Policy" content="default-src 'self'">
```

### 12.2 CSRF（跨站请求伪造）

攻击者诱导用户在已登录的网站上执行非预期操作。

```javascript
// 防御：CSRF Token
// 1. 服务端生成 token 并嵌入页面
// 2. 请求时携带 token
async function postData(url, data) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken
        },
        body: JSON.stringify(data)
    });
    return response.json();
}
```

### 12.3 前端安全审计

使用 JavaScript 进行安全检测：

```javascript
// 检测是否存在 eval 调用（潜在安全风险）
function checkForEval(code) {
    return /\beval\s*\(/.test(code);
}

// 检测不安全的 innerHTML 使用
function hasUnsafeInnerHTML(html) {
    const dangerousTags = /<(script|iframe|form|img|svg)/i;
    return dangerousTags.test(html);
}

// 密码强度检测
function checkPasswordStrength(password) {
    let score = 0;
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;
    return score;  // 0-4 分
}

// SQL 注入简单检测
function detectSQLInjection(input) {
    const patterns = [
        /(\b(union|select|insert|update|delete|drop|alter)\b)/i,
        /'(\s*or\s*'[^']*'[^']*')/i,
        /;--/,
        /\bexec\b/i
    ];
    return patterns.some(pattern => pattern.test(input));
}
```

### 12.4 安全编码实践

```javascript
// 1. 避免使用 eval
// 危险：
// eval("2 + 2");
// 安全替代：使用 JSON.parse 解析 JSON
const data = JSON.parse(jsonString);

// 2. 安全使用 setTimeout/setInterval
// 危险：
// setTimeout("doSomething()", 1000);
// 安全：
setTimeout(doSomething, 1000);

// 3. 输入验证
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

// 4. 输出编码
function safeOutput(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}
```

### 12.5 安全工具开发

JavaScript/Node.js 可用于开发安全工具：

```javascript
// 简单的端口扫描器示例
const net = require('net');

function portScan(host, ports) {
    ports.forEach(port => {
        const socket = new net.Socket();
        socket.setTimeout(1000);
        
        socket.connect(port, host, () => {
            console.log(`端口 ${port} 开放`);
            socket.destroy();
        });
        
        socket.on('error', () => {
            // 端口关闭或过滤
        });
        
        socket.on('timeout', () => {
            socket.destroy();
        });
    });
}

// 简单的目录爆破工具示例
const http = require('http');

async function dirBuster(url, wordlist) {
    for (const path of wordlist) {
        const fullUrl = `${url}/${path}`;
        // 发送请求检查状态码
        console.log(`检查: ${fullUrl}`);
    }
}
```

---

## 总结

JavaScript 是 Web 安全领域必须掌握的编程语言之一。掌握 JavaScript 基础语法、DOM 操作、网络请求和文件操作，对于理解和防御 Web 安全漏洞（如 XSS、CSRF、SQL 注入等）至关重要。建议结合实际的漏洞练习环境（如 DVWA、XSS Game 等）进行实践学习。

---

## 学习资源与知识拓展

### 官方资源

- **JavaScript 官方文档**：各语言官网提供最权威的文档和教程
- **JavaScript 标准库参考**：官方标准库 API 文档

### 在线教程

- **菜鸟教程 JavaScript**：https://www.runoob.com/ — 中文入门教程
- **W3Schools**：https://www.w3schools.com/ — 交互式学习平台
- **MDN Web Docs**：https://developer.mozilla.org/ — Web 技术文档（适用于 JS/HTML/CSS）

### 安全编程资源

- **OWASP 速查表系列**：https://cheatsheetseries.owasp.org/ — 各种安全最佳实践
- **CWE 常见弱点枚举**：https://cwe.mitre.org/ — 软件弱点分类体系
- **安全开发指南**：各语言官方安全文档与最佳实践

### 安全工具与库

- 根据语言选择相应的安全库和工具（加密库、HTTP 库、网络库等）
- 关注 GitHub 上的安全开源项目与社区

### 练习平台

- **LeetCode**：https://leetcode.cn/ — 算法练习平台
- **Codewars**：https://www.codewars.com/ — 编程挑战网站
- **Hack The Box**：https://www.hackthebox.com/ — 安全靶场
- **TryHackMe**：https://tryhackme.com/ — 安全学习房间
- **Bugku**：https://ctf.bugku.com/ — 国内 CTF 平台
- **攻防世界**：https://adworld.xctf.org.cn/ — XCTF 竞赛平台

### 推荐书籍

- 《JavaScript程序设计》— 入门经典教材
- 《JavaScript高级编程》— 进阶学习指南
- 各类安全相关技术书籍

### 社区与资讯

- **GitHub**：https://github.com/ — 开源项目托管平台
- **Stack Overflow**：https://stackoverflow.com/ — 编程问答社区
- **FreeBuf**：https://www.freebuf.com/ — 安全资讯媒体
- **安全客**：https://www.anquanke.com/ — 安全技术媒体
- **先知社区**：https://xz.aliyun.com/ — 阿里云安全社区

### 学习路线建议

1. **入门阶段**（1-2月）：掌握基本语法、数据类型、控制流
2. **进阶阶段**（2-3月）：函数、面向对象、异常处理、标准库
3. **实战练习**（1-2月）：通过项目巩固知识
4. **安全方向**（持续）：了解语言相关的安全漏洞和防护
5. **持续学习**：关注社区、阅读源码、参与开源
