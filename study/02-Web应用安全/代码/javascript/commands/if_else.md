# if_else

> **分类**：条件语句
> **说明**：条件判断语句

---

## 语法

```javascript
if (condition) { ... } else if (cond2) { ... } else { ... }
```

## 运算符

==/===/!=/!==/>/</>=/<=/&&/||/!/??

## 示例代码

```javascript
// 基本 if/else
const age = 18;
if (age >= 18) {
    console.log("成年");
} else {
    console.log("未成年");
}

// 多分支
const score = 85;
let grade;
if (score >= 90) {
    grade = "A";
} else if (score >= 80) {
    grade = "B";
} else if (score >= 60) {
    grade = "C";
} else {
    grade = "D";
}

// 三元表达式
const x = 10;
const result = x > 5 ? "大于5" : "小于等于5";

// 逻辑运算符
const a = true, b = false;
console.log(a && b);  // false（与）
console.log(a || b);  // true（或）
console.log(!a);      // false（非）

// 短路求值
const name = userInput || "默认值";    // userInput 为假值时用默认
const value = userInput ?? "默认值";    // 仅 null/undefined 时用默认
const obj = data && data.prop;          // data 存在时才访问 prop

// switch
const day = "Monday";
switch (day) {
    case "Monday":
        console.log("星期一");
        break;
    case "Tuesday":
        console.log("星期二");
        break;
    default:
        console.log("其他");
}

// 真值/假值
// 假值: false, 0, "", null, undefined, NaN
// 其余都是真值
if ("") console.log("不会执行");
if (0) console.log("不会执行");
if ([]) console.log("会执行（空数组是真值）");
```
