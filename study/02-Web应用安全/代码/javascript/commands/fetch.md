# fetch

> **分类**：网络请求
> **说明**：Fetch API 用于发起 HTTP 请求

---

## 语法

```javascript
fetch(url, options)\n  .then(response => response.json())\n  .then(data => ...)
```

## 选项

- method
- headers
- body
- mode
- credentials
- cache

## 示例代码

```javascript
// 基本 GET 请求
fetch("https://api.example.com/data")
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error("错误:", error));

// async/await 写法（推荐）
async function getData() {
    try {
        const response = await fetch("https://api.example.com/data");
        if (!response.ok) {
            throw new Error("HTTP错误: " + response.status);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("请求失败:", error);
    }
}

// POST 请求
async function postData() {
    const response = await fetch("https://api.example.com/users", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer token123"
        },
        body: JSON.stringify({
            name: "Alice",
            age: 25
        })
    });
    return response.json();
}

// 其他方法：PUT, DELETE, PATCH
fetch(url, { method: "PUT", body: JSON.stringify(data) });
fetch(url, { method: "DELETE" });

// 获取响应信息
async function getInfo() {
    const resp = await fetch(url);
    console.log(resp.status);      // 状态码
    console.log(resp.statusText);  // 状态文本
    console.log(resp.ok);          // 2xx 为 true
    console.log(resp.headers.get("content-type"));

    // 响应体方法
    // resp.json()   - 解析为 JSON
    // resp.text()   - 解析为文本
    // resp.blob()   - 解析为 Blob
    // resp.formData() - 解析为 FormData
    // resp.arrayBuffer() - 解析为二进制
}

// FormData 上传
async function uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("name", "test");

    const resp = await fetch(url, {
        method: "POST",
        body: formData  // 不要手动设置 Content-Type
    });
}

// 中止请求
const controller = new AbortController();
fetch(url, { signal: controller.signal });
// 中止
controller.abort();
```
