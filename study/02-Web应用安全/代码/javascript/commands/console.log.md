# console.log

> **分类**：输出调试
> **说明**：输出信息到控制台，用于调试

---

## 语法

```javascript
console.log(obj1 [, obj2, ..., objN])
```

## 常用方法/属性

- log
- info
- warn
- error
- debug
- table
- dir
- group
- time
- timeEnd
- count
- clear

## 示例代码

```javascript
// 基本输出
console.log("Hello, World!");
console.log("数字:", 42);
console.log("对象:", {name: "Alice", age: 25});

// 不同级别
console.info("信息");     // 信息级别
console.warn("警告");     // 警告（黄色）
console.error("错误");    // 错误（红色）
console.debug("调试");    // 调试级别

// 格式化输出
console.log("我是 %s，今年 %d 岁", "小明", 18);

// 表格形式
console.table([{name: "A", age: 20}, {name: "B", age: 25}]);

// 计时
console.time("循环");
for (let i = 0; i < 1000000; i++) {}
console.timeEnd("循环");  // 循环: xxx ms

// 分组
console.group("用户信息");
console.log("姓名: Alice");
console.log("年龄: 25");
console.groupEnd();

// 计数
console.count("点击");  // 点击: 1
console.count("点击");  // 点击: 2
console.countReset("点击");
```
