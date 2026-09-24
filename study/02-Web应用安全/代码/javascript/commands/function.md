# function

> **分类**：函数
> **说明**：函数定义的多种方式

---

## 语法

```javascript
function name(params) { ... }\nconst name = function(params) { ... }\nconst name = (params) => { ... }
```

## 类型

函数声明/函数表达式/箭头函数/立即执行函数(IIFE)/构造函数

## 示例代码

```javascript
// 函数声明（会提升）
function add(a, b) {
    return a + b;
}
console.log(add(2, 3));  // 5

// 函数表达式
const multiply = function(a, b) {
    return a * b;
};

// 箭头函数
const subtract = (a, b) => a - b;
const square = x => x * x;  // 单参数可省略括号
const greet = name => `Hello, ${name}!`;

// 多行箭头函数
const sum = (arr) => {
    let total = 0;
    for (const n of arr) total += n;
    return total;
};

// 箭头函数的 this 指向外层
const obj = {
    name: "test",
    delayed: function() {
        setTimeout(() => {
            console.log(this.name);  // this 指向 obj（箭头函数继承外层this）
        }, 1000);
    }
};

// IIFE (立即执行函数表达式)
(function() {
    console.log("立即执行");
})();

// 带参数的 IIFE
(function(name) {
    console.log("Hello, " + name);
})("World");

// 默认参数
function hello(name = "World") {
    return `Hello, ${name}!`;
}

// 剩余参数
function sumAll(...args) {
    return args.reduce((a, b) => a + b, 0);
}
sumAll(1, 2, 3, 4);  // 10
```
