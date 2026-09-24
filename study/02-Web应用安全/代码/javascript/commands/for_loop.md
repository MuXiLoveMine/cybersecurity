# for_loop

> **分类**：循环
> **说明**：多种循环方式

---

## 语法

```javascript
for / for...in / for...of / while / do...while
```

## 相关

break: 跳出循环\ncontinue: 跳过本次\n.forEach(): 数组方法

## 示例代码

```javascript
// 传统 for 循环
for (let i = 0; i < 5; i++) {
    console.log(i);  // 0, 1, 2, 3, 4
}

// for...of - 遍历可迭代对象（数组、字符串等）
const arr = ["a", "b", "c"];
for (const item of arr) {
    console.log(item);
}

// for...in - 遍历对象键（不推荐用于数组）
const obj = { a: 1, b: 2 };
for (const key in obj) {
    console.log(key, obj[key]);
}

// while 循环
let count = 0;
while (count < 5) {
    console.log(count);
    count++;
}

// do...while（至少执行一次）
let i = 0;
do {
    console.log(i);
    i++;
} while (i < 5);

// break 和 continue
for (let i = 0; i < 10; i++) {
    if (i === 3) continue;  // 跳过 3
    if (i === 7) break;     // 到 7 停止
    console.log(i);
}

// forEach 方法
arr.forEach((item, index, array) => {
    console.log(index, item);
});

// map / filter / reduce 替代部分循环
const nums = [1, 2, 3, 4, 5];
const doubled = nums.map(n => n * 2);
const evens = nums.filter(n => n % 2 === 0);
const sum = nums.reduce((acc, n) => acc + n, 0);

// 标签语句（跳出外层循环）
outer:
for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
        if (i === 1 && j === 1) break outer;
        console.log(i, j);
    }
}
```
