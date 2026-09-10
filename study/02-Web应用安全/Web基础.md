# Web 基础

> 本文档系统介绍 Web 应用安全所需的前端基础知识（HTML/CSS/JavaScript）、Web 架构模式，以及 PHP 和 Java 两种主流后端动态语言的基础，为 Web 安全学习奠定全栈知识基础。

---

## 目录

- [第一章：Web 概述](#第一章web-概述)
- [第二章：HTML 基础](#第二章html-基础)
- [第三章：CSS 基础](#第三章css-基础)
- [第四章：JavaScript 基础](#第四章javascript-基础)
- [第五章：Web 架构](#第五章web-架构)
- [第六章：PHP 基础](#第六章php-基础)
- [第七章：Java Web 基础](#第七章java-web-基础)

---

## 第一章：Web 概述

### 1.1 什么是 Web

Web（World Wide Web，万维网）是基于互联网的一个应用系统，通过超文本（Hypertext）和超链接（Hyperlink）将世界各地的文档连接起来，用户可以通过浏览器访问和浏览。

**Web 的三大核心技术**：

| 技术 | 作用 | 发明者/组织 |
|------|------|-------------|
| **HTML** | 网页的结构和内容 | Tim Berners-Lee |
| **HTTP** | 网页传输协议 | CERN / W3C |
| **URL** | 资源定位方式 | - |

### 1.2 Web 工作原理

```
用户浏览器                          Web 服务器
   │                                    │
   │ 1. 输入 URL / 点击链接              │
   │───────────────────────────────────→│
   │     HTTP 请求（GET /index.html）    │
   │                                    │
   │ 2. 服务器处理请求                   │
   │                                    │
   │ 3. 返回响应                         │
   │←───────────────────────────────────│
   │     HTTP 响应（HTML 页面）          │
   │                                    │
   │ 4. 浏览器解析渲染页面               │
   │    - 解析 HTML 构建 DOM 树          │
   │    - 解析 CSS 构建样式树            │
   │    - 执行 JavaScript               │
   │    - 渲染页面显示给用户             │
```

### 1.3 前端与后端

| 角色 | 说明 | 技术栈 |
|------|------|--------|
| **前端（Frontend）** | 用户直接看到和交互的部分 | HTML、CSS、JavaScript、Vue/React |
| **后端（Backend）** | 服务器端的逻辑和数据处理 | PHP、Java、Python、Node.js 等 |
| **数据库（Database）** | 存储和管理数据 | MySQL、PostgreSQL、Oracle 等 |

---

## 第二章：HTML 基础

### 2.1 什么是 HTML

HTML（HyperText Markup Language，超文本标记语言）是用于创建网页的标准标记语言。它不是编程语言，而是用标签（tag）来描述网页的结构和内容。

### 2.2 HTML 基本结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网页标题</title>
</head>
<body>
    <h1>这是一级标题</h1>
    <p>这是一个段落。</p>
</body>
</html>
```

**结构说明**：
- `<!DOCTYPE html>`：声明文档类型为 HTML5
- `<html>`：根元素，包含整个 HTML 文档
- `<head>`：头部，包含元数据（字符集、标题、样式等）
- `<body>`：主体，包含页面可见内容

### 2.3 常用 HTML 标签

#### 2.3.1 文本标签

| 标签 | 说明 | 示例 |
|------|------|------|
| `<h1>`~`<h6>` | 标题（h1 最大，h6 最小） | `<h1>一级标题</h1>` |
| `<p>` | 段落 | `<p>这是段落</p>` |
| `<br>` | 换行 | `第一行<br>第二行` |
| `<hr>` | 水平线 | `<hr>` |
| `<strong>` | 加粗（强调） | `<strong>重要内容</strong>` |
| `<em>` | 斜体（强调） | `<em>强调文本</em>` |
| `<span>` | 行内容器 | `<span style="color:red">红色</span>` |
| `<div>` | 块级容器 | `<div>内容块</div>` |

#### 2.3.2 链接与图片

```html
<!-- 超链接 -->
<a href="https://www.example.com">访问示例网站</a>
<a href="https://example.com" target="_blank">新窗口打开</a>
<a href="#section1">跳转到页面内锚点</a>
<a href="mailto:test@example.com">发送邮件</a>

<!-- 图片 -->
<img src="image.jpg" alt="图片描述" width="200" height="100">
<img src="https://example.com/logo.png" alt="Logo">
```

#### 2.3.3 列表

```html
<!-- 无序列表 -->
<ul>
    <li>苹果</li>
    <li>香蕉</li>
    <li>樱桃</li>
</ul>

<!-- 有序列表 -->
<ol>
    <li>第一步</li>
    <li>第二步</li>
    <li>第三步</li>
</ol>

<!-- 定义列表 -->
<dl>
    <dt>HTML</dt>
    <dd>超文本标记语言</dd>
    <dt>CSS</dt>
    <dd>层叠样式表</dd>
</dl>
```

#### 2.3.4 表格

```html
<table border="1">
    <thead>
        <tr>
            <th>姓名</th>
            <th>年龄</th>
            <th>城市</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>张三</td>
            <td>25</td>
            <td>北京</td>
        </tr>
        <tr>
            <td>李四</td>
            <td>30</td>
            <td>上海</td>
        </tr>
    </tbody>
</table>
```

#### 2.3.5 表单

表单是用户输入和提交数据的重要方式，也是 Web 安全的重点关注对象。

```html
<form action="/login" method="POST">
    <!-- 文本输入 -->
    <label>用户名：</label>
    <input type="text" name="username" value="" placeholder="请输入用户名">
    <br>

    <!-- 密码输入 -->
    <label>密码：</label>
    <input type="password" name="password">
    <br>

    <!-- 单选框 -->
    <label>性别：</label>
    <input type="radio" name="gender" value="male" checked> 男
    <input type="radio" name="gender" value="female"> 女
    <br>

    <!-- 复选框 -->
    <label>爱好：</label>
    <input type="checkbox" name="hobby" value="reading"> 阅读
    <input type="checkbox" name="hobby" value="music"> 音乐
    <input type="checkbox" name="hobby" value="sports"> 运动
    <br>

    <!-- 下拉选择 -->
    <label>城市：</label>
    <select name="city">
        <option value="beijing">北京</option>
        <option value="shanghai">上海</option>
        <option value="guangzhou">广州</option>
    </select>
    <br>

    <!-- 文本域 -->
    <label>留言：</label>
    <textarea name="message" rows="4" cols="30"></textarea>
    <br>

    <!-- 隐藏字段 -->
    <input type="hidden" name="token" value="abc123">

    <!-- 按钮 -->
    <button type="submit">提交</button>
    <button type="reset">重置</button>
</form>
```

**表单重要属性**：

| 属性 | 说明 | 安全意义 |
|------|------|---------|
| `action` | 表单提交的目标 URL | - |
| `method` | 提交方式：GET 或 POST | GET 参数在 URL 中，POST 在请求体中 |
| `name` | 表单元素的名称，提交时的键 | - |
| `value` | 表单元素的默认值 | - |
| `placeholder` | 提示文字 | - |

> **安全提示**：表单是 XSS、SQL 注入、CSRF 等漏洞的常见入口，所有用户输入都需要在后端进行严格的验证和过滤。

### 2.4 HTML 全局属性

| 属性 | 说明 |
|------|------|
| `id` | 元素的唯一标识符 |
| `class` | 元素的类名（用于 CSS 和 JS） |
| `style` | 内联 CSS 样式 |
| `title` | 鼠标悬停时显示的提示 |
| `data-*` | 自定义数据属性 |
| `hidden` | 隐藏元素 |

### 2.5 语义化标签

HTML5 引入了语义化标签，使页面结构更清晰：

| 标签 | 说明 |
|------|------|
| `<header>` | 页面或区块的头部 |
| `<nav>` | 导航区域 |
| `<main>` | 主要内容 |
| `<section>` | 章节 |
| `<article>` | 独立的文章内容 |
| `<aside>` | 侧边栏 |
| `<footer>` | 页脚 |

---

## 第三章：CSS 基础

### 3.1 什么是 CSS

CSS（Cascading Style Sheets，层叠样式表）用于描述 HTML 元素的样式和布局，控制网页的外观（颜色、字体、间距、位置等）。

### 3.2 CSS 的引入方式

```html
<!-- 方式一：内联样式（不推荐） -->
<p style="color: red; font-size: 16px;">红色文字</p>

<!-- 方式二：内部样式表 -->
<head>
    <style>
        p {
            color: blue;
            font-size: 14px;
        }
    </style>
</head>

<!-- 方式三：外部样式表（推荐） -->
<head>
    <link rel="stylesheet" href="style.css">
</head>
```

### 3.3 CSS 选择器

选择器用于选中需要应用样式的 HTML 元素。

#### 3.3.1 基本选择器

| 选择器 | 说明 | 示例 |
|--------|------|------|
| 元素选择器 | 选中所有指定元素 | `p { color: red; }` |
| ID 选择器 | 选中指定 ID 的元素（唯一） | `#header { ... }` |
| 类选择器 | 选中指定类的元素 | `.active { ... }` |
| 通配符选择器 | 选中所有元素 | `* { margin: 0; }` |

#### 3.3.2 组合选择器

| 选择器 | 说明 | 示例 |
|--------|------|------|
| `A, B` | 群组选择器（同时选中 A 和 B） | `h1, h2 { ... }` |
| `A B` | 后代选择器（A 内部所有 B） | `.nav a { ... }` |
| `A > B` | 子选择器（A 的直接子元素 B） | `ul > li { ... }` |
| `A + B` | 相邻兄弟选择器 | `h1 + p { ... }` |

#### 3.3.3 伪类选择器

| 选择器 | 说明 |
|--------|------|
| `:hover` | 鼠标悬停时 |
| `:active` | 被点击时 |
| `:focus` | 获得焦点时 |
| `:visited` | 已访问的链接 |
| `:first-child` | 第一个子元素 |
| `:last-child` | 最后一个子元素 |
| `:nth-child(n)` | 第 n 个子元素 |

### 3.4 常用 CSS 属性

#### 3.4.1 文本与字体

```css
p {
    color: #333;                /* 文字颜色 */
    font-size: 16px;            /* 字体大小 */
    font-family: Arial, sans-serif; /* 字体 */
    font-weight: bold;          /* 字重（粗体） */
    font-style: italic;         /* 斜体 */
    text-align: center;         /* 文字对齐：left/center/right */
    text-decoration: underline; /* 下划线 */
    line-height: 1.5;           /* 行高 */
    letter-spacing: 2px;        /* 字间距 */
}
```

#### 3.4.2 背景与边框

```css
.box {
    background-color: #f0f0f0;  /* 背景色 */
    background-image: url(bg.png); /* 背景图片 */
    background-size: cover;     /* 背景大小 */
    background-position: center; /* 背景位置 */
    background-repeat: no-repeat; /* 不重复 */

    border: 1px solid #ccc;     /* 边框 */
    border-radius: 8px;         /* 圆角 */
    border-color: red;          /* 边框颜色 */
    border-width: 2px;          /* 边框宽度 */
    border-style: dashed;       /* 边框样式：solid/dashed/dotted */
}
```

#### 3.4.3 盒子模型

每个 HTML 元素都可以看作一个盒子，由内到外包括：

```
┌───────────────────────────────┐
│          margin (外边距)        │
│  ┌─────────────────────────┐  │
│  │    border (边框)         │  │
│  │  ┌───────────────────┐  │  │
│  │  │  padding (内边距)  │  │  │
│  │  │  ┌─────────────┐  │  │  │
│  │  │  │   content   │  │  │  │
│  │  │  │   (内容)    │  │  │  │
│  │  │  └─────────────┘  │  │  │
│  │  └───────────────────┘  │  │
│  └─────────────────────────┘  │
└───────────────────────────────┘
```

```css
.box {
    width: 200px;               /* 宽度 */
    height: 100px;              /* 高度 */
    padding: 20px;              /* 内边距 */
    padding-top: 10px;
    padding-right: 20px;
    padding-bottom: 10px;
    padding-left: 20px;
    margin: 10px auto;          /* 外边距（auto 可水平居中） */
    border: 1px solid #000;
    box-sizing: border-box;     /* 宽高包含 padding 和 border */
}
```

#### 3.4.4 布局

```css
/* 显示模式 */
display: block;        /* 块级元素（独占一行） */
display: inline;       /* 行内元素（不换行，不支持宽高） */
display: inline-block; /* 行内块（不换行，支持宽高） */
display: none;         /* 隐藏元素（不占空间） */
visibility: hidden;    /* 隐藏元素（仍占空间） */

/* 浮动 */
float: left;
float: right;
clear: both;           /* 清除浮动 */

/* Flexbox 弹性布局 */
display: flex;
justify-content: center;    /* 主轴对齐 */
align-items: center;        /* 交叉轴对齐 */
flex-direction: row;        /* 方向：row/column */
flex-wrap: wrap;            /* 换行 */

/* 定位 */
position: static;     /* 默认定位 */
position: relative;   /* 相对定位（相对于自身原位置） */
position: absolute;   /* 绝对定位（相对于最近的非 static 祖先） */
position: fixed;      /* 固定定位（相对于视口） */
top: 10px;
left: 20px;
z-index: 100;         /* 层叠顺序，数值越大越靠上 */
```

#### 3.4.5 颜色表示

```css
/* 颜色名 */
color: red;

/* 十六进制 */
color: #ff0000;
color: #f00;    /* 简写 */

/* RGB */
color: rgb(255, 0, 0);

/* RGBA（带透明度） */
color: rgba(255, 0, 0, 0.5);  /* 50% 不透明 */
```

### 3.5 CSS 优先级

当多个样式作用于同一元素时，按以下优先级决定：

1. **!important**（最高，尽量避免使用）
2. **内联样式**（style 属性）
3. **ID 选择器**
4. **类选择器 / 伪类 / 属性选择器**
5. **元素选择器 / 伪元素**
6. **通配符 / 继承**（最低）

> 记忆口诀：**行内 > ID > 类 > 标签**

---

## 第四章：JavaScript 基础

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

## 第五章：Web 架构

### 5.1 B/S 架构

B/S（Browser/Server，浏览器/服务器）架构是 Web 应用的主流模式，用户通过浏览器访问服务器端的应用。

```
┌──────────┐    HTTP/HTTPS    ┌──────────┐    数据访问    ┌──────────┐
│  浏览器  │ ───────────────→ │  服务器  │ ────────────→ │  数据库  │
│ (前端)   │ ←─────────────── │ (后端)   │ ←──────────── │ (数据)   │
└──────────┘     HTML/CSS/JS  └──────────┘                └──────────┘
```

### 5.2 三层架构

| 层次 | 说明 | 技术 |
|------|------|------|
| **表示层**（Presentation） | 用户界面，展示数据和接收输入 | HTML、CSS、JavaScript、Vue/React |
| **业务逻辑层**（Business） | 核心业务逻辑处理 | Java、PHP、Python、Node.js |
| **数据访问层**（Data Access） | 数据库操作和数据持久化 | SQL、ORM 框架 |

### 5.3 MVC 模式

MVC（Model-View-Controller）是一种常见的 Web 应用设计模式：

| 组件 | 说明 | 职责 |
|------|------|------|
| **Model（模型）** | 数据模型 | 处理数据和业务逻辑 |
| **View（视图）** | 用户界面 | 展示数据给用户 |
| **Controller（控制器）** | 控制逻辑 | 接收请求，调用模型，选择视图 |

### 5.4 前后端交互方式

| 方式 | 说明 | 特点 |
|------|------|------|
| **同步请求** | 整页刷新 | 简单，但用户体验差 |
| **AJAX** | 异步 JavaScript + XML | 局部刷新，用户体验好 |
| **WebSocket** | 全双工通信 | 实时性高，适合聊天、通知等 |
| **RESTful API** | 基于 HTTP 的 API 设计 | 规范、简洁、易扩展 |
| **GraphQL** | 查询语言 | 灵活获取所需数据 |

### 5.5 常见 Web 服务器

| 服务器 | 说明 | 适用场景 |
|--------|------|---------|
| **Apache** | 老牌 Web 服务器，功能丰富，模块多 | 传统网站、PHP 应用 |
| **Nginx** | 高性能、低资源占用 | 高并发网站、反向代理、负载均衡 |
| **IIS** | Windows 自带的 Web 服务器 | ASP.NET 应用 |
| **Tomcat** | Java Servlet 容器 | Java Web 应用 |
| **Node.js** | JavaScript 运行时 | 全栈 JS 应用 |

### 5.6 常见后端语言与框架

| 语言 | 代表框架 | 特点 |
|------|---------|------|
| **PHP** | Laravel、ThinkPHP、WordPress | 上手快，部署简单，Web 生态丰富 |
| **Java** | Spring Boot、Struts | 企业级首选，稳定可靠，生态庞大 |
| **Python** | Django、Flask | 开发快，适合 AI/数据类应用 |
| **Node.js** | Express、Koa、Next.js | JS 全栈，高并发 I/O |
| **Go** | Gin、Beego | 高性能，编译型，适合微服务 |
| **C#** | ASP.NET | Windows 生态，企业级 |

---

## 第六章：PHP 基础

> PHP 详细内容和代码示例请查看 `php/PHP基础.md` 和 `php/` 目录中的示例文件。

### 6.1 PHP 简介

PHP（PHP: Hypertext Preprocessor）是一种广泛使用的开源脚本语言，特别适合 Web 开发，可以嵌入到 HTML 中。

**特点**：
- 语法简单，上手快
- 与 HTML 混编方便
- 数据库支持丰富（MySQL 最佳拍档）
- 跨平台
- 开源免费

### 6.2 PHP 基本语法

```php
<?php
// 这是单行注释
/* 这是多行注释 */

// 输出
echo "Hello, World!";
print "Hello";

// 变量（以 $ 开头）
$name = "张三";
$age = 25;

// 字符串拼接（用点号）
echo "姓名: " . $name . ", 年龄: " . $age;

// 双引号内解析变量
echo "姓名: $name, 年龄: $age";

// 数组
$fruits = array("apple", "banana", "cherry");
$fruits = ["apple", "banana", "cherry"];  // PHP 5.4+

// 关联数组（字典）
$person = [
    "name" => "张三",
    "age" => 25,
    "city" => "北京"
];
echo $person["name"];

// 条件判断
if ($age >= 18) {
    echo "成年";
} elseif ($age >= 13) {
    echo "青少年";
} else {
    echo "儿童";
}

// 循环
for ($i = 0; $i < 5; $i++) {
    echo $i;
}

foreach ($fruits as $fruit) {
    echo $fruit;
}

foreach ($person as $key => $value) {
    echo "$key: $value";
}

// 函数
function add($a, $b) {
    return $a + $b;
}
echo add(3, 5);
?>
```

### 6.3 PHP 与 HTML 混编

```php
<!-- index.php -->
<!DOCTYPE html>
<html>
<head>
    <title>PHP 示例</title>
</head>
<body>
    <h1>欢迎，<?php echo $name; ?>！</h1>
    <p>当前时间：<?php echo date("Y-m-d H:i:s"); ?></p>

    <ul>
        <?php foreach ($fruits as $fruit): ?>
            <li><?php echo $fruit; ?></li>
        <?php endforeach; ?>
    </ul>

    <!-- 短标签（需配置开启） -->
    <p><?= "短输出标签" ?></p>
</body>
</html>
```

### 6.4 PHP 表单处理

```php
<?php
// login.php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST["username"];
    $password = $_POST["password"];

    // 处理登录逻辑...
    echo "用户名: " . htmlspecialchars($username);
}

// GET 参数
$page = $_GET["page"] ?? 1;

// 服务器信息
echo $_SERVER["PHP_SELF"];       // 当前脚本路径
echo $_SERVER["HTTP_USER_AGENT"]; // 用户代理
echo $_SERVER["REMOTE_ADDR"];     // 客户端 IP
?>
```

### 6.5 PHP 操作 MySQL

```php
<?php
// MySQLi 面向过程方式
$conn = mysqli_connect("localhost", "root", "password", "testdb");

if (!$conn) {
    die("连接失败: " . mysqli_connect_error());
}

// 查询
$sql = "SELECT id, name, age FROM users";
$result = mysqli_query($conn, $sql);

if (mysqli_num_rows($result) > 0) {
    while ($row = mysqli_fetch_assoc($result)) {
        echo "id: " . $row["id"] . " 姓名: " . $row["name"] . "<br>";
    }
}

// 插入
$sql = "INSERT INTO users (name, age) VALUES ('张三', 25)";
if (mysqli_query($conn, $sql)) {
    echo "新记录插入成功，ID: " . mysqli_insert_id($conn);
}

// 防止 SQL 注入：预处理语句
$stmt = mysqli_prepare($conn, "INSERT INTO users (name, age) VALUES (?, ?)");
mysqli_stmt_bind_param($stmt, "si", $name, $age);
$name = "李四";
$age = 30;
mysqli_stmt_execute($stmt);

mysqli_close($conn);
?>
```

> **安全提示**：必须使用预处理语句（Prepared Statement）来防止 SQL 注入，绝不能直接拼接用户输入到 SQL 语句中。

### 6.6 PHP 超全局变量

| 超全局变量 | 说明 |
|-----------|------|
| `$GLOBALS` | 全局变量数组 |
| `$_SERVER` | 服务器和环境信息 |
| `$_GET` | GET 请求参数 |
| `$_POST` | POST 请求参数 |
| `$_REQUEST` | GET + POST + Cookie |
| `$_COOKIE` | Cookie 数据 |
| `$_SESSION` | Session 数据 |
| `$_FILES` | 上传的文件信息 |
| `$_ENV` | 环境变量 |

---

## 第七章：Java Web 基础

> Java 详细内容和代码示例请查看 `java/Java基础.md` 和 `java/` 目录中的示例文件。

### 7.1 Java 简介

Java 是一种面向对象的编程语言，以"一次编写，到处运行"著称。Java Web 是企业级应用的主流技术栈。

**特点**：
- 强类型、面向对象
- 跨平台（JVM）
- 生态庞大，企业级框架成熟
- 性能好，稳定性高

### 7.2 Java 基本语法

```java
// HelloWorld.java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");

        // 变量（强类型）
        String name = "张三";
        int age = 25;
        double height = 1.75;
        boolean isStudent = true;

        // 输出
        System.out.println("姓名: " + name + ", 年龄: " + age);
        System.out.printf("姓名: %s, 年龄: %d%n", name, age);
    }
}
```

### 7.3 数据类型

| 类型 | 分类 | 大小 | 范围 |
|------|------|------|------|
| `byte` | 基本类型 | 1字节 | -128~127 |
| `short` | 基本类型 | 2字节 | -32768~32767 |
| `int` | 基本类型 | 4字节 | -21亿~21亿 |
| `long` | 基本类型 | 8字节 | -9e18~9e18 |
| `float` | 基本类型 | 4字节 | 单精度浮点数 |
| `double` | 基本类型 | 8字节 | 双精度浮点数 |
| `char` | 基本类型 | 2字节 | 单个字符 |
| `boolean` | 基本类型 | 1位 | true/false |
| `String` | 引用类型 | - | 字符串 |
| 数组/对象 | 引用类型 | - | 引用传递 |

### 7.4 数组

```java
// 声明和初始化
int[] nums = new int[5];
int[] nums = {1, 2, 3, 4, 5};
String[] names = {"张三", "李四", "王五"};

// 访问
System.out.println(nums[0]);
System.out.println(nums.length);

// 遍历
for (int i = 0; i < nums.length; i++) {
    System.out.println(nums[i]);
}

for (int num : nums) {  // 增强 for 循环
    System.out.println(num);
}
```

### 7.5 条件与循环

```java
// if-else
int score = 85;
if (score >= 90) {
    System.out.println("A");
} else if (score >= 80) {
    System.out.println("B");
} else {
    System.out.println("C");
}

// switch
int day = 1;
switch (day) {
    case 1:
        System.out.println("星期一");
        break;
    case 2:
        System.out.println("星期二");
        break;
    default:
        System.out.println("其他");
}

// for 循环
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}

// while
int count = 0;
while (count < 5) {
    count++;
}

// do-while
do {
    count--;
} while (count > 0);
```

### 7.6 面向对象

```java
// 类定义
public class Person {
    // 成员变量
    private String name;
    private int age;

    // 构造方法
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // 成员方法
    public void greet() {
        System.out.println("你好，我是" + name);
    }

    // getter / setter
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getAge() {
        return age;
    }
}

// 使用
Person p = new Person("张三", 25);
p.greet();
System.out.println(p.getName());
```

### 7.7 集合框架

```java
import java.util.*;

// ArrayList
List<String> list = new ArrayList<>();
list.add("apple");
list.add("banana");
list.get(0);
list.size();

// HashMap
Map<String, Integer> map = new HashMap<>();
map.put("张三", 25);
map.put("李四", 30);
map.get("张三");
map.containsKey("张三");

// 遍历
for (String item : list) {
    System.out.println(item);
}

for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}
```

### 7.8 Java Web 核心技术

| 技术 | 说明 |
|------|------|
| **Servlet** | Java Web 的基础，处理 HTTP 请求 |
| **JSP** | Java Server Pages，在 HTML 中嵌入 Java 代码 |
| **JDBC** | Java 数据库连接 API |
| **Filter** | 过滤器，用于请求预处理 |
| **Listener** | 监听器，监听 Web 事件 |
| **Session / Cookie** | 会话管理 |
| **JSTL** | JSP 标准标签库 |
| **Spring MVC** | MVC 框架，企业级主流 |
| **Spring Boot** | 快速开发框架，约定优于配置 |
| **MyBatis / JPA** | 持久层框架（操作数据库） |

### 7.9 Servlet 示例

```java
// HelloServlet.java
import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;

public class HelloServlet extends HttpServlet {
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("text/html;charset=UTF-8");
        PrintWriter out = response.getWriter();

        String name = request.getParameter("name");
        if (name == null) name = "访客";

        out.println("<html><body>");
        out.println("<h1>你好，" + name + "！</h1>");
        out.println("</body></html>");
    }

    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        doGet(request, response);
    }
}
```

### 7.10 JDBC 示例

```java
import java.sql.*;

public class JdbcExample {
    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/testdb?useSSL=false";
        String user = "root";
        String password = "123456";

        try {
            // 加载驱动
            Class.forName("com.mysql.cj.jdbc.Driver");

            // 建立连接
            Connection conn = DriverManager.getConnection(url, user, password);

            // 查询
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT id, name, age FROM users");

            while (rs.next()) {
                int id = rs.getInt("id");
                String name = rs.getString("name");
                int age = rs.getInt("age");
                System.out.println(id + ": " + name + ", " + age);
            }

            // 防止 SQL 注入：预处理
            String sql = "INSERT INTO users (name, age) VALUES (?, ?)";
            PreparedStatement pstmt = conn.prepareStatement(sql);
            pstmt.setString(1, "张三");
            pstmt.setInt(2, 25);
            pstmt.executeUpdate();

            rs.close();
            stmt.close();
            conn.close();

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

---

## 总结

Web 基础是 Web 安全学习的前提。理解前端三剑客（HTML/CSS/JS）的工作原理，掌握 Web 架构模式，熟悉至少一种后端语言，才能真正理解漏洞产生的原理和利用方式。

**关键要点回顾**：

1. **HTML** 定义网页结构，表单是用户输入和数据提交的主要方式，也是 XSS、SQL 注入等漏洞的常见入口。
2. **CSS** 控制页面样式，选择器优先级和盒子模型是核心概念。
3. **JavaScript** 实现页面交互，DOM 操作和 AJAX 是重点，`innerHTML` 和 `eval` 等是 XSS 的常见风险点。
4. **Web 架构** 经历了从单体到 MVC、前后端分离的演变，理解数据流有助于发现安全问题。
5. **PHP 和 Java** 是两种主流后端语言，各有特点和常见漏洞模式。

---

> **延伸学习**：结合 MySQL 数据库文档学习数据存储，深入理解前后端数据交互的完整流程。后续学习 SQL 注入、XSS、CSRF 等 Web 漏洞时，扎实的 Web 基础将帮助你更深刻地理解漏洞本质和防护原理。
