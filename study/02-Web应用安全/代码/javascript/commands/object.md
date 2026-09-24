# object

> **分类**：对象
> **说明**：对象的属性、方法和常用操作

---

## 语法

```javascript
const obj = { key1: value1, key2: value2 };
```

## 常用方法/属性

- keys
- values
- entries
- assign
- freeze
- seal
- hasOwnProperty

## 示例代码

```javascript
// 创建对象
const person = {
    name: "Alice",
    age: 25,
    greet: function() {
        return `Hello, I'm ${this.name}`;
    }
};

// 访问属性
console.log(person.name);       // "Alice"
console.log(person["age"]);     // 25（方括号形式，键可以是变量）

// 修改/添加
person.age = 26;
person.email = "alice@test.com";

// 删除
delete person.age;

// 检查属性是否存在
console.log("name" in person);              // true
console.log(person.hasOwnProperty("name")); // true

// 遍历对象
for (const key in person) {
    console.log(key, person[key]);
}

// 获取键/值/键值对
const keys = Object.keys(person);      // ["name", "greet", ...]
const values = Object.values(person);  // ["Alice", function, ...]
const entries = Object.entries(person); // [["name","Alice"], ...]

// 合并对象
const obj1 = { a: 1, b: 2 };
const obj2 = { b: 3, c: 4 };
const merged = { ...obj1, ...obj2 };  // {a:1, b:3, c:4}
const merged2 = Object.assign({}, obj1, obj2);

// 冻结（不可修改）
const frozen = Object.freeze({ x: 1 });
// frozen.x = 2;  // 无效（严格模式报错）

// 解构
const { name, age } = person;
const { name: personName } = person;  // 重命名
const { a, b, ...rest } = { a:1, b:2, c:3, d:4 };

// 可选链 (ES2020)
const city = person.address?.city;  // 不报错，返回 undefined

// 空值合并 (ES2020)
const value = person.nickname ?? "默认值";  // 仅 null/undefined 时用默认值
```
