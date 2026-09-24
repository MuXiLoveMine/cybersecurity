# 第四章：JavaScript 基础

### 4.1 什么是 JavaScript

JavaScript（简称 JS）是一种轻量级的解释型编程语言，是 Web 前端的核心技术之一，用于实现网页的交互功能。它运行在浏览器中，也可以通过 Node.js 在服务端运行。

**JS 的核心作用**：
- 操作 DOM 元素（修改页面内容和样式）
- 处理用户交互（点击、输入、鼠标移动等）
- 发送网络请求（AJAX / Fetch）
- 表单验证
- 动画效果
- 本地存储（Cookie、LocalStorage）

### 4.2 引入方式

```html
<!-- 方式一：内联脚本 -->
<button onclick="alert('Hello')">点击</button>

<!-- 方式二：内部脚本 -->
<script>
    console.log("Hello, World!");
</script>

<!-- 方式三：外部脚本（推荐） -->
<script src="script.js"></script>

<!-- defer：页面解析完再执行 -->
<script src="script.js" defer></script>

<!-- async：异步加载，加载完立即执行 -->
<script src="script.js" async></script>
```

### 4.3 变量与数据类型

```javascript
// 变量声明
let name = "张三";     // 可变变量（推荐）
const PI = 3.14159;    // 常量（不可变，推荐）
var age = 25;          // 旧方式（函数作用域，不推荐）

// 数据类型
let str = "hello";           // string 字符串
let num = 123;               // number 数字
let isTrue = true;           // boolean 布尔值
let arr = [1, 2, 3];         // object 数组
let obj = {a: 1, b: 2};      // object 对象
let n = null;                // null 空值
let u;                       // undefined 未定义
let sym = Symbol("key");     // symbol 符号

// typeof 判断类型
console.log(typeof str);     // "string"
console.log(typeof num);     // "number"
console.log(typeof arr);     // "object"
```

### 4.4 运算符

```javascript
// 算术运算
let a = 10, b = 3;
console.log(a + b);    // 加
console.log(a - b);    // 减
console.log(a * b);    // 乘
console.log(a / b);    // 除
console.log(a % b);    // 取余
console.log(a ** b);   // 幂
console.log(++a);      // 自增
console.log(--b);      // 自减

// 比较运算
console.log(a == b);   // 等于（类型转换后比较）
console.log(a === b);  // 严格等于（类型和值都相同，推荐）
console.log(a != b);   // 不等于
console.log(a !== b);  // 严格不等于
console.log(a > b);
console.log(a < b);
console.log(a >= b);
console.log(a <= b);

// 逻辑运算
console.log(true && false);   // 与
console.log(true || false);   // 或
console.log(!true);           // 非

// 字符串拼接
console.log("Hello " + "World");
```

> **安全提示**：`==` 会进行类型转换，可能导致意外结果（如 `0 == ''` 为 true），建议始终使用 `===` 和 `!==`。

### 4.5 字符串操作

```javascript
let s = "Hello World";

// 长度
console.log(s.length);          // 11

// 索引
console.log(s[0]);              // H
console.log(s.charAt(1));       // e

// 查找
console.log(s.indexOf("World"));  // 6
console.log(s.lastIndexOf("l"));  // 9
console.log(s.includes("llo"));   // true
console.log(s.startsWith("He"));  // true
console.log(s.endsWith("ld"));    // true

// 截取
console.log(s.slice(0, 5));       // Hello
console.log(s.substring(6));      // World
console.log(s.substr(6, 3));      // Wor

// 替换
console.log(s.replace("World", "JS"));  // Hello JS
console.log(s.replaceAll("l", "L"));    // HeLLo WorLd

// 大小写
console.log(s.toUpperCase());  // HELLO WORLD
console.log(s.toLowerCase());  // hello world

// 分割与连接
console.log(s.split(" "));     // ["Hello", "World"]
let arr = ["a", "b", "c"];
console.log(arr.join("-"));    // "a-b-c"

// 去除空白
console.log("  hello  ".trim());    // "hello"
```

### 4.6 数组操作

```javascript
let fruits = ["apple", "banana", "cherry"];

// 访问
console.log(fruits[0]);        // apple
console.log(fruits.length);    // 3

// 添加/删除
fruits.push("date");           // 末尾添加
fruits.pop();                  // 末尾删除
fruits.unshift("apricot");     // 开头添加
fruits.shift();                // 开头删除

// 查找
console.log(fruits.indexOf("banana"));  // 1
console.log(fruits.includes("cherry")); // true

// 遍历
for (let i = 0; i < fruits.length; i++) {
    console.log(fruits[i]);
}

for (let fruit of fruits) {
    console.log(fruit);
}

fruits.forEach(function(item, index) {
    console.log(index + ": " + item);
});

// 高阶函数
let nums = [1, 2, 3, 4, 5];

// map：映射转换
let doubled = nums.map(x => x * 2);      // [2, 4, 6, 8, 10]

// filter：过滤
let evens = nums.filter(x => x % 2 === 0); // [2, 4]

// reduce：归约
let sum = nums.reduce((acc, x) => acc + x, 0); // 15

// find：查找第一个满足条件的
let firstEven = nums.find(x => x % 2 === 0); // 2

// 排序
fruits.sort();                    // 字母排序
nums.sort((a, b) => a - b);       // 数字升序
nums.sort((a, b) => b - a);       // 数字降序

// 反转
fruits.reverse();
```

### 4.7 对象操作

```javascript
let person = {
    name: "张三",
    age: 25,
    city: "北京",
    greet: function() {
        console.log("你好，我是" + this.name);
    }
};

// 访问属性
console.log(person.name);       // 张三
console.log(person["age"]);     // 25（方括号方式，支持变量）

// 修改/添加
person.age = 26;
person.job = "工程师";

// 删除
delete person.city;

// 判断属性是否存在
console.log("name" in person);         // true
console.log(person.hasOwnProperty("name")); // true

// 遍历
for (let key in person) {
    console.log(key + ": " + person[key]);
}

// 获取所有键/值
console.log(Object.keys(person));      // ["name", "age", "job", "greet"]
console.log(Object.values(person));    // 值数组
console.log(Object.entries(person));   // 键值对数组

// 方法调用
person.greet();
```

### 4.8 条件判断与循环

```javascript
// if-else
let score = 85;
if (score >= 90) {
    console.log("A");
} else if (score >= 80) {
    console.log("B");
} else if (score >= 60) {
    console.log("C");
} else {
    console.log("D");
}

// 三元运算符
let result = score >= 60 ? "及格" : "不及格";

// switch
let day = 1;
switch (day) {
    case 1:
        console.log("星期一");
        break;
    case 2:
        console.log("星期二");
        break;
    default:
        console.log("其他");
}

// for 循环
for (let i = 0; i < 5; i++) {
    console.log(i);
}

// while 循环
let count = 0;
while (count < 5) {
    count++;
}

// do-while
do {
    count--;
} while (count > 0);

// for-in（遍历对象）
for (let key in person) {
    console.log(key);
}

// for-of（遍历数组/字符串）
for (let item of fruits) {
    console.log(item);
}
```

### 4.9 函数

```javascript
// 函数声明
function add(a, b) {
    return a + b;
}
console.log(add(3, 5));

// 函数表达式
const multiply = function(a, b) {
    return a * b;
};

// 箭头函数（ES6+）
const divide = (a, b) => a / b;
const square = x => x * x;

// 默认参数
function greet(name, greeting = "Hello") {
    console.log(greeting + ", " + name + "!");
}
greet("张三");           // Hello, 张三!
greet("李四", "早上好");  // 早上好, 李四!

// 可变参数
function sumAll(...args) {
    return args.reduce((acc, x) => acc + x, 0);
}
console.log(sumAll(1, 2, 3, 4));

// 立即执行函数（IIFE）
(function() {
    console.log("立即执行");
})();

// 闭包
function counter() {
    let count = 0;
    return function() {
        return ++count;
    };
}
let c = counter();
console.log(c());  // 1
console.log(c());  // 2
```

### 4.10 DOM 操作

DOM（Document Object Model，文档对象模型）是 HTML 文档的树形表示，JS 通过 DOM API 操作页面元素。

```javascript
// ===== 查找元素 =====
const byId = document.getElementById("myId");
const byClass = document.getElementsByClassName("myClass");  // HTMLCollection
const byTag = document.getElementsByTagName("div");          // HTMLCollection
const first = document.querySelector(".myClass");             // 第一个匹配
const all = document.querySelectorAll(".myClass");           // NodeList

// ===== 修改内容 =====
element.textContent = "新的文本内容";    // 纯文本
element.innerHTML = "<b>加粗</b>";       // HTML 内容

// ===== 修改属性 =====
element.setAttribute("src", "new.jpg");
let src = element.getAttribute("src");
element.href = "https://example.com";     // 直接操作标准属性

// ===== 修改样式 =====
element.style.color = "red";
element.style.fontSize = "20px";          // 注意：驼峰式
element.classList.add("active");          // 添加类
element.classList.remove("active");       // 删除类
element.classList.toggle("active");       // 切换类
element.classList.contains("active");     // 判断是否有类

// ===== 创建与添加 =====
const newDiv = document.createElement("div");
newDiv.textContent = "新的 div";
parent.appendChild(newDiv);                          // 末尾添加
parent.insertBefore(newDiv, referenceNode);          // 指定位置插入

// ===== 删除 =====
element.remove();                                     // 删除自身
parent.removeChild(childElement);                     // 删除子元素

// ===== 事件监听 =====
const btn = document.getElementById("myBtn");
btn.addEventListener("click", function() {
    alert("按钮被点击了！");
});

// 常见事件
// - click：点击
// - dblclick：双击
// - mouseover / mouseout：鼠标移入/移出
// - keydown / keyup：键盘按下/抬起
// - input：输入变化
// - change：值改变（失焦时）
// - submit：表单提交
// - load：页面加载完成
// - scroll：滚动
```

> **安全提示**：使用 `innerHTML` 插入用户可控的内容可能导致 XSS 攻击，应优先使用 `textContent`，或对内容进行严格的转义过滤。

### 4.11 事件与事件冒泡

事件从目标元素向上传播到根节点的过程称为**事件冒泡**。

```javascript
// 阻止冒泡
element.addEventListener("click", function(e) {
    e.stopPropagation();
});

// 阻止默认行为（如链接跳转、表单提交）
link.addEventListener("click", function(e) {
    e.preventDefault();
});

// 事件委托：给父元素添加监听器，利用冒泡处理子元素事件
list.addEventListener("click", function(e) {
    if (e.target.tagName === "LI") {
        console.log("点击了列表项: " + e.target.textContent);
    }
});
```

### 4.12 网络请求（AJAX / Fetch）

```javascript
// ===== Fetch API（现代方式） =====

// GET 请求
fetch("https://api.example.com/data")
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error("错误:", error));

// POST 请求（JSON）
fetch("https://api.example.com/login", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        username: "admin",
        password: "123456"
    })
})
    .then(response => response.json())
    .then(data => console.log(data));

// async / await 写法（更简洁）
async function fetchData() {
    try {
        const response = await fetch("https://api.example.com/data");
        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.error("错误:", error);
    }
}

// ===== XMLHttpRequest（旧方式） =====
const xhr = new XMLHttpRequest();
xhr.open("GET", "https://api.example.com/data", true);
xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
        console.log(JSON.parse(xhr.responseText));
    }
};
xhr.send();
```

### 4.13 浏览器存储

```javascript
// LocalStorage（永久存储，5MB 左右）
localStorage.setItem("username", "张三");
let name = localStorage.getItem("username");
localStorage.removeItem("username");
localStorage.clear();

// SessionStorage（会话存储，关闭浏览器即失效）
sessionStorage.setItem("token", "abc123");

// Cookie
document.cookie = "username=张三; path=/; max-age=3600";
console.log(document.cookie);
```

---

---

