# let_const_var

> **分类**：变量声明
> **说明**：三种变量声明方式：var（函数作用域）、let（块级作用域）、const（常量）

---

## 语法

```javascript
var name = value;\nlet name = value;\nconst name = value;
```

## 区别对比

var: 函数作用域，可重复声明，有变量提升\nlet: 块级作用域，不可重复声明，暂时性死区\nconst: 块级作用域，声明时必须赋值，不可重新赋值（但对象属性可改）

## 示例代码

```javascript
// var - 函数作用域
var x = 10;
function test() {
    var y = 20;
    console.log(x);  // 10（函数内可访问外部）
}
// console.log(y);  // 错误，y 是函数局部的

// var 的问题：变量提升
console.log(a);  // undefined（不是报错）
var a = 5;

// let - 块级作用域
let b = 10;
if (true) {
    let b = 20;   // 内部的 b，不影响外部
    console.log(b);  // 20
}
console.log(b);  // 10

// let 不能重复声明
// let b = 30;  // 错误

// const - 常量（不可重新赋值）
const PI = 3.14159;
// PI = 3;  // 错误

// const 对象的属性可以修改
const person = { name: "Alice" };
person.name = "Bob";  // 可以，因为对象引用没变
// person = {};      // 错误，不能重新赋值

// const 数组
const arr = [1, 2, 3];
arr.push(4);  // 可以
// arr = [5, 6];  // 错误

// 最佳实践：优先用 const，需要修改时用 let，避免 var
```
