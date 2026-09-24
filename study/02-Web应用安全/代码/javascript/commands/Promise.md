# Promise

> **分类**：异步编程
> **说明**：Promise 用于处理异步操作

---

## 语法

```javascript
new Promise((resolve, reject) => { ... })
```

## 常用方法/属性

- then
- catch
- finally
- all
- race
- allSettled
- any
- resolve
- reject

## 示例代码

```javascript
// 创建 Promise
function delay(ms) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            resolve("完成");
            // 或 reject(new Error("失败"));
        }, ms);
    });
}

// 使用 then/catch
delay(1000)
    .then(result => {
        console.log(result);
        return delay(1000);  // 链式调用
    })
    .then(result => {
        console.log("第二个完成");
    })
    .catch(error => {
        console.error(error);
    })
    .finally(() => {
        console.log("总是执行");
    });

// async/await（语法糖，推荐）
async function asyncFunc() {
    try {
        const result = await delay(1000);
        console.log(result);
    } catch (error) {
        console.error(error);
    }
}

// Promise.all - 并行执行，全部成功才成功
async function parallel() {
    const [result1, result2, result3] = await Promise.all([
        fetch(url1),
        fetch(url2),
        fetch(url3)
    ]);
}

// Promise.race - 谁先完成就用谁的结果
async function withTimeout(promise, ms) {
    const timeout = new Promise((_, reject) => {
        setTimeout(() => reject(new Error("超时")), ms);
    });
    return Promise.race([promise, timeout]);
}

// Promise.allSettled - 等待所有完成（不论成败）
async function allSettled() {
    const results = await Promise.allSettled([
        Promise.resolve(1),
        Promise.reject("错误"),
        Promise.resolve(3)
    ]);
    results.forEach(r => console.log(r.status));  // fulfilled/rejected
}

// Promise.resolve / Promise.reject
const resolved = Promise.resolve(42);
const rejected = Promise.reject(new Error("失败"));

// 错误处理
async function errorHandling() {
    // try/catch 捕获
    try {
        const data = await fetchData();
    } catch (err) {
        console.error("捕获到错误:", err);
    }
}
```
