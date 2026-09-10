/**
 * 04_array.js - 数组创建、增删改查、遍历、map/filter/reduce
 * 
 * 本示例演示 JavaScript 数组的各种操作：
 * - 数组的创建方式
 * - 数组元素的增删改查
 * - 数组遍历方法
 * - map / filter / reduce 等高阶方法
 * - 其他常用数组方法
 */

// ========== 1. 数组创建 ==========

console.log("=== 1. 数组创建 ===");

// 方式一：字面量（推荐）
const fruits = ["苹果", "香蕉", "橙子"];
console.log("字面量创建:", fruits);

// 方式二：构造函数
const numbers = new Array(1, 2, 3, 4, 5);
console.log("构造函数创建:", numbers);

// 注意：单个数字参数表示数组长度
const emptyArr = new Array(5);
console.log("长度为 5 的空数组:", emptyArr, "长度:", emptyArr.length);

// 方式三：Array.from（从类数组或可迭代对象创建）
const strArr = Array.from("hello");
console.log("从字符串创建:", strArr);

// 方式四：Array.fill（填充数组）
const filledArr = new Array(5).fill(0);
console.log("fill 填充:", filledArr);

// 数组长度
console.log("fruits 长度:", fruits.length);

// ========== 2. 数组元素的访问 ==========

console.log("\n=== 2. 数组元素访问 ===");

const colors = ["红", "绿", "蓝", "黄", "紫"];

// 通过索引访问（从 0 开始）
console.log("第一个元素:", colors[0]);
console.log("第三个元素:", colors[2]);
console.log("最后一个元素:", colors[colors.length - 1]);

// 越界访问返回 undefined，不会报错
console.log("越界访问 colors[10]:", colors[10]);

// 修改元素
colors[0] = "红色";
console.log("修改后:", colors);

// ========== 3. 数组增删操作 ==========

console.log("\n=== 3. 数组增删操作 ===");

let arr = [1, 2, 3];
console.log("原始数组:", arr);

// --- 末尾操作 ---
arr.push(4);  // 末尾添加
console.log("push(4) 后:", arr, "返回新长度:", arr.length);

arr.pop();    // 末尾删除
console.log("pop() 后:", arr);

// --- 开头操作 ---
arr.unshift(0);  // 开头添加
console.log("unshift(0) 后:", arr);

arr.shift();     // 开头删除
console.log("shift() 后:", arr);

// --- 任意位置操作：splice ---
arr = [1, 2, 3, 4, 5];
console.log("\nsplice 操作，原始数组:", arr);

// 删除：splice(起始索引, 删除数量)
arr.splice(2, 1);  // 从索引 2 删除 1 个元素
console.log("splice(2, 1) 删除后:", arr);

// 插入：splice(起始索引, 0, 要插入的元素...)
arr.splice(2, 0, "a", "b");
console.log("splice(2, 0, 'a', 'b') 插入后:", arr);

// 替换：splice(起始索引, 删除数量, 新元素...)
arr.splice(2, 2, "x", "y", "z");
console.log("splice(2, 2, 'x', 'y', 'z') 替换后:", arr);

// ========== 4. 数组查询 ==========

console.log("\n=== 4. 数组查询 ===");

const nums = [10, 20, 30, 40, 30, 50];

// indexOf - 查找元素索引，找不到返回 -1
console.log("indexOf(30):", nums.indexOf(30));        // 2
console.log("indexOf(100):", nums.indexOf(100));      // -1

// lastIndexOf - 从后往前找
console.log("lastIndexOf(30):", nums.lastIndexOf(30)); // 4

// includes - 是否包含某个元素
console.log("includes(40):", nums.includes(40));      // true
console.log("includes(100):", nums.includes(100));    // false

// find - 找到第一个满足条件的元素
const result = nums.find(function(item) {
    return item > 25;
});
console.log("find 第一个大于 25 的元素:", result);  // 30

// findIndex - 找到第一个满足条件的元素的索引
const index = nums.findIndex(item => item > 25);
console.log("findIndex 第一个大于 25 的索引:", index);  // 2

// ========== 5. 数组遍历 ==========

console.log("\n=== 5. 数组遍历 ===");

const animals = ["猫", "狗", "兔子", "熊猫"];

// --- for 循环 ---
console.log("for 循环:");
for (let i = 0; i < animals.length; i++) {
    console.log(`  [${i}] ${animals[i]}`);
}

// --- for...of ---
console.log("for...of:");
for (let animal of animals) {
    console.log("  ", animal);
}

// --- forEach ---
console.log("forEach:");
animals.forEach(function(animal, index) {
    console.log(`  索引${index}: ${animal}`);
});

// ========== 6. map / filter / reduce ==========

console.log("\n=== 6. map / filter / reduce ===");

const numArr = [1, 2, 3, 4, 5];
console.log("原始数组:", numArr);

// --- map：映射转换，返回新数组 ---
// 每个元素乘以 2
const doubled = numArr.map(function(x) {
    return x * 2;
});
console.log("map 每个元素乘 2:", doubled);

// 箭头函数简写
const squared = numArr.map(x => x * x);
console.log("map 每个元素平方:", squared);

// --- filter：过滤，返回满足条件的新数组 ---
// 过滤出偶数
const evens = numArr.filter(function(x) {
    return x % 2 === 0;
});
console.log("filter 偶数:", evens);

// 过滤出大于 2 的数
const greaterThan2 = numArr.filter(x => x > 2);
console.log("filter 大于 2:", greaterThan2);

// --- reduce：归约，将数组归约为单个值 ---
// 求和
const sum = numArr.reduce(function(accumulator, currentValue) {
    return accumulator + currentValue;
}, 0);  // 0 是初始值
console.log("reduce 求和:", sum);

// 求最大值
const max = numArr.reduce((acc, cur) => Math.max(acc, cur), numArr[0]);
console.log("reduce 求最大值:", max);

// 链式调用
// 先过滤偶数，再平方，再求和
const result2 = numArr
    .filter(x => x % 2 === 0)
    .map(x => x * x)
    .reduce((acc, cur) => acc + cur, 0);
console.log("链式调用（偶数平方和）:", result2);

// ========== 7. some / every ==========

console.log("\n=== 7. some / every ===");

const scores = [85, 90, 78, 95, 60];

// some - 是否至少有一个满足条件
const hasExcellent = scores.some(score => score >= 90);
console.log("是否有 90 分以上的:", hasExcellent);  // true

// every - 是否所有都满足条件
const allPass = scores.every(score => score >= 60);
console.log("是否都及格:", allPass);  // true

const allExcellent = scores.every(score => score >= 90);
console.log("是否都优秀:", allExcellent);  // false

// ========== 8. 其他常用方法 ==========

console.log("\n=== 8. 其他常用方法 ===");

// --- sort 排序 ---
let sortArr = [3, 1, 4, 1, 5, 9, 2, 6];
console.log("排序前:", sortArr);

// 默认按字符串排序（注意：数字排序需要传比较函数）
sortArr.sort();
console.log("默认排序:", sortArr);  // [1, 1, 2, 3, 4, 5, 6, 9] 这里刚好正确

// 正确的数字升序排序
sortArr = [10, 2, 25, 1, 100];
sortArr.sort((a, b) => a - b);
console.log("数字升序:", sortArr);

// 数字降序排序
sortArr.sort((a, b) => b - a);
console.log("数字降序:", sortArr);

// --- reverse 反转 ---
let revArr = [1, 2, 3, 4, 5];
revArr.reverse();
console.log("反转后:", revArr);

// --- join 拼接成字符串 ---
const joinArr = ["a", "b", "c"];
console.log("join('-'):", joinArr.join("-"));
console.log("join(''):", joinArr.join(""));

// --- slice 截取（不修改原数组）---
const sliceArr = [1, 2, 3, 4, 5];
console.log("slice(1, 4):", sliceArr.slice(1, 4));  // [2, 3, 4]
console.log("slice(2):", sliceArr.slice(2));        // [3, 4, 5]
console.log("slice(-2):", sliceArr.slice(-2));      // [4, 5]
console.log("原数组不变:", sliceArr);

// --- concat 合并 ---
const arr1 = [1, 2];
const arr2 = [3, 4];
const arr3 = [5, 6];
console.log("concat 合并:", arr1.concat(arr2, arr3));

// 展开运算符（ES6）
console.log("展开运算符合并:", [...arr1, ...arr2, ...arr3]);

// --- flat 扁平化 ---
const nestedArr = [1, [2, 3], [4, [5, 6]]];
console.log("flat() 扁平一层:", nestedArr.flat());
console.log("flat(2) 扁平两层:", nestedArr.flat(2));

// ========== 9. 安全应用：敏感词过滤 ==========

console.log("\n=== 9. 安全示例：敏感词过滤 ===");

function filterSensitiveWords(text, sensitiveWords) {
    let filtered = text;
    sensitiveWords.forEach(word => {
        // 创建全局匹配的正则表达式
        const regex = new RegExp(word, "gi");
        // 替换为等长度的星号
        filtered = filtered.replace(regex, "*".repeat(word.length));
    });
    return filtered;
}

const sensitiveWords = ["病毒", "攻击", "漏洞"];
const originalText = "这个病毒攻击利用了系统漏洞，需要及时修复。";
const filteredText = filterSensitiveWords(originalText, sensitiveWords);

console.log("原文:", originalText);
console.log("过滤后:", filteredText);

console.log("\n=== 示例运行完成 ===");
