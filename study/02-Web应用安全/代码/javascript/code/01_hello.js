/**
 * 01_hello.js - Hello World、变量声明、数据类型
 * 
 * 本示例演示 JavaScript 的基础语法：
 * - 控制台输出
 * - var / let / const 三种变量声明方式
 * - 各种数据类型
 * - typeof 运算符
 */

// ========== 1. Hello World ==========

// 使用 console.log 输出到控制台
console.log("Hello, World!");
console.log("欢迎学习 JavaScript！");

// 其他输出方式
console.warn("这是一条警告信息");  // 黄色警告
console.error("这是一条错误信息"); // 红色错误

// ========== 2. 变量声明 ==========

// --- var 声明 ---
// 特点：函数作用域，可以重复声明，存在变量提升
var name = "张三";
console.log("var 声明的 name:", name);

var name = "李四";  // var 允许重复声明（不推荐）
console.log("重复声明后的 name:", name);

name = "王五";      // 可以重新赋值
console.log("重新赋值后的 name:", name);

// --- let 声明（ES6 推荐） ---
// 特点：块级作用域，不能重复声明，可以重新赋值
let age = 25;
console.log("let 声明的 age:", age);

// let age = 30;  // 错误：不能重复声明
age = 26;          // 可以重新赋值
console.log("重新赋值后的 age:", age);

// --- const 声明（常量） ---
// 特点：块级作用域，不能重复声明，不能重新赋值
const PI = 3.14159;
console.log("const 声明的 PI:", PI);

// PI = 3.14;  // 错误：不能重新赋值

// 注意：const 声明的对象，其属性可以修改
const person = {
    name: "小明",
    age: 20
};
console.log("修改前的 person:", person);

person.age = 21;  // 允许修改对象的属性
person.city = "北京";  // 允许添加新属性
console.log("修改后的 person:", person);

// person = { name: "小红" };  // 错误：不能重新赋值整个对象

// ========== 3. 数据类型 ==========

// --- 基本类型 ---

// 字符串（String）
let str1 = "双引号字符串";
let str2 = '单引号字符串';
let str3 = `模板字符串`;  // ES6 反引号
console.log("\n=== 字符串类型 ===");
console.log("str1:", str1, typeof str1);

// 数字（Number）
let num1 = 42;          // 整数
let num2 = 3.14;        // 浮点数
let num3 = NaN;         // 非数字（Not a Number）
let num4 = Infinity;    // 正无穷
console.log("\n=== 数字类型 ===");
console.log("整数:", num1, typeof num1);
console.log("浮点数:", num2, typeof num2);
console.log("NaN:", num3, typeof num3);
console.log("无穷大:", num4, typeof num4);

// 布尔值（Boolean）
let isTrue = true;
let isFalse = false;
console.log("\n=== 布尔类型 ===");
console.log("true:", isTrue, typeof isTrue);
console.log("false:", isFalse, typeof isFalse);

// undefined - 声明了但未赋值
let undefinedVar;
console.log("\n=== undefined ===");
console.log("未赋值的变量:", undefinedVar, typeof undefinedVar);

// null - 空值（表示"没有对象"）
let nullVar = null;
console.log("\n=== null ===");
console.log("null 值:", nullVar, typeof nullVar);
// 注意：typeof null 返回 "object"，这是 JavaScript 的历史遗留问题

// Symbol（ES6）- 唯一标识符
let sym1 = Symbol("foo");
let sym2 = Symbol("foo");
console.log("\n=== Symbol 类型 ===");
console.log("sym1:", sym1, typeof sym1);
console.log("sym1 === sym2:", sym1 === sym2);  // false，每个 Symbol 都是唯一的

// BigInt（ES2020）- 大整数
let bigIntNum = 123456789012345678901234567890n;
console.log("\n=== BigInt 类型 ===");
console.log("大整数:", bigIntNum, typeof bigIntNum);

// --- 引用类型 ---

// 对象（Object）
let student = {
    name: "张三",
    age: 20,
    grade: "大三"
};
console.log("\n=== 对象类型 ===");
console.log("student:", student, typeof student);

// 数组（Array）
let fruits = ["苹果", "香蕉", "橙子"];
console.log("\n=== 数组类型 ===");
console.log("fruits:", fruits, typeof fruits);
// 注意：typeof 数组返回 "object"，判断数组用 Array.isArray()
console.log("Array.isArray(fruits):", Array.isArray(fruits));

// 函数（Function）
function greet() {
    return "你好！";
}
console.log("\n=== 函数类型 ===");
console.log("greet:", greet, typeof greet);

// ========== 4. 类型转换 ==========

console.log("\n=== 类型转换 ===");

// 字符串转数字
let strNum = "123";
console.log("字符串转数字:", Number(strNum), typeof Number(strNum));
console.log("parseInt:", parseInt("123abc"));   // 123
console.log("parseFloat:", parseFloat("3.14元")); // 3.14

// 数字转字符串
let numStr = 456;
console.log("数字转字符串:", String(numStr), typeof String(numStr));
console.log("toString 方法:", numStr.toString());

// 转布尔值
console.log("Boolean(0):", Boolean(0));        // false
console.log("Boolean(''):", Boolean(''));      // false
console.log("Boolean(null):", Boolean(null));  // false
console.log("Boolean('0'):", Boolean('0'));    // true
console.log("Boolean([]):", Boolean([]));      // true

// ========== 5. 模板字符串示例 ==========

console.log("\n=== 模板字符串 ===");

let userName = "小明";
let userAge = 25;

// 传统字符串拼接
console.log("大家好，我叫" + userName + "，今年" + userAge + "岁。");

// 模板字符串（反引号）
console.log(`大家好，我叫${userName}，今年${userAge}岁。`);

// 模板字符串支持表达式
console.log(`明年我就${userAge + 1}岁了。`);

// 模板字符串支持多行
let multiLine = `
    第一行
    第二行
    第三行
`;
console.log("多行字符串:", multiLine);

console.log("\n=== 示例运行完成 ===");
