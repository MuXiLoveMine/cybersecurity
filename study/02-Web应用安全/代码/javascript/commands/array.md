# array

> **分类**：数组
> **说明**：数组的常用属性和方法

---

## 语法

```javascript
const arr = [item1, item2, ...];
```

## 常用方法/属性

- push
- pop
- shift
- unshift
- slice
- splice
- concat
- join
- indexOf
- includes
- find
- filter
- map
- reduce
- sort
- reverse
- forEach
- every
- some

## 示例代码

```javascript
// 创建数组
const fruits = ["apple", "banana", "cherry"];
const nums = new Array(1, 2, 3);
const empty = new Array(5);  // 长度为5的空数组

// 访问元素
console.log(fruits[0]);      // "apple"
console.log(fruits.length);  // 3

// 添加/删除元素
fruits.push("orange");       // 末尾添加
fruits.pop();                // 末尾删除
fruits.unshift("grape");     // 开头添加
fruits.shift();              // 开头删除

// 截取与拼接
const citrus = fruits.slice(1, 3);  // 切片（不修改原数组）
fruits.splice(1, 2, "kiwi");        // 删除+插入（修改原数组）
const combined = fruits.concat(["mango", "pear"]);

// 查找
console.log(fruits.indexOf("banana"));  // 索引
console.log(fruits.includes("apple"));  // 是否包含

// find - 找第一个匹配的元素
const users = [{id:1, name:"A"}, {id:2, name:"B"}];
const user = users.find(u => u.id === 2);  // {id:2, name:"B"}

// filter - 过滤
const numbers = [1, 2, 3, 4, 5];
const evens = numbers.filter(n => n % 2 === 0);  // [2, 4]

// map - 映射转换
const squares = numbers.map(n => n * n);  // [1, 4, 9, 16, 25]

// reduce - 归约
const sum = numbers.reduce((acc, n) => acc + n, 0);  // 15

// 排序
numbers.sort((a, b) => a - b);  // 升序
numbers.sort((a, b) => b - a);  // 降序

// 遍历
fruits.forEach(fruit => console.log(fruit));

for (const fruit of fruits) {
    console.log(fruit);
}

for (let i = 0; i < fruits.length; i++) {
    console.log(i, fruits[i]);
}

// 解构
const [first, second, ...rest] = fruits;

// 展开运算符
const arr1 = [1, 2, 3];
const arr2 = [...arr1, 4, 5];  // [1, 2, 3, 4, 5]
```
