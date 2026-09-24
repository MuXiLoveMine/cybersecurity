# try_catch

> **分类**：异常处理
> **说明**：try/catch/finally 错误处理

---

## 语法

```javascript
try { ... } catch (error) { ... } finally { ... }
```

## 相关

throw - 抛出异常\nError - 错误对象\nasync错误用 try/catch 或 .catch()

## 示例代码

```javascript
// 基本 try/catch
try {
    const result = riskyOperation();
    console.log(result);
} catch (error) {
    console.error("发生错误:", error.message);
    console.error("堆栈:", error.stack);
}

// finally 子句（总是执行）
let resource;
try {
    resource = acquireResource();
    useResource(resource);
} catch (error) {
    console.error("错误:", error);
} finally {
    // 无论是否异常，都执行清理
    if (resource) {
        releaseResource(resource);
    }
}

// 抛出异常
function divide(a, b) {
    if (b === 0) {
        throw new Error("不能除以零");
    }
    return a / b;
}

// 自定义错误类型
class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

function validateAge(age) {
    if (age < 0) {
        throw new ValidationError("年龄不能为负");
    }
    if (age > 150) {
        throw new ValidationError("年龄不合理");
    }
}

// 根据错误类型分别处理
try {
    validateAge(-5);
} catch (error) {
    if (error instanceof ValidationError) {
        console.log("验证错误:", error.message);
    } else if (error instanceof TypeError) {
        console.log("类型错误");
    } else {
        console.log("未知错误:", error);
        throw error;  // 重新抛出
    }
}

// async/await 错误处理
async function fetchData() {
    try {
        const resp = await fetch(url);
        const data = await resp.json();
        return data;
    } catch (error) {
        console.error("请求失败:", error);
        throw error;  // 或返回默认值
    }
}

// Promise 链的错误处理
fetch(url)
    .then(resp => resp.json())
    .then(data => console.log(data))
    .catch(err => console.error(err));
```
