# fetch API - JavaScript 网络请求

> 现代浏览器和 Node.js 内置的 HTTP 请求 API，基于 Promise。

---

## 一、基本用法

```javascript
// 基本 GET 请求
fetch('https://api.example.com/users')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('错误:', error));

// async/await 写法
async function fetchUsers() {
    try {
        const response = await fetch('https://api.example.com/users');
        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.error('错误:', error);
    }
}
```

---

## 二、请求配置

### 2.1 常用选项

```javascript
fetch(url, {
    method: 'GET',        // 请求方法: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
    headers: {            // 请求头
        'Content-Type': 'application/json',
        'Authorization': 'Bearer token123',
        'Accept': 'application/json'
    },
    body: JSON.stringify(data),  // 请求体
    mode: 'cors',                // 模式: cors, no-cors, same-origin
    credentials: 'same-origin',  // 携带 cookie: omit, same-origin, include
    cache: 'no-cache',           // 缓存策略
    redirect: 'follow',          // 重定向: follow, error, manual
    referrer: 'client',          // referrer 策略
    signal: controller.signal,   // AbortController 信号
})
```

### 2.2 GET 请求

```javascript
// 带查询参数
const params = new URLSearchParams({
    page: 1,
    limit: 10,
    search: 'keyword'
});

fetch(`https://api.example.com/users?${params}`)
    .then(res => res.json())
    .then(data => console.log(data));

// 自定义请求头
fetch('https://api.example.com/api/data', {
    headers: {
        'Authorization': 'Bearer my-token',
        'X-API-Key': 'abc123',
        'Accept': 'application/json'
    }
})
    .then(res => res.json())
    .then(data => console.log(data));
```

### 2.3 POST 请求

```javascript
// JSON 数据
const data = { name: 'John', email: 'john@example.com' };

fetch('https://api.example.com/users', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
})
    .then(res => res.json())
    .then(data => console.log(data));

// 表单数据 (FormData)
const formData = new FormData();
formData.append('username', 'john');
formData.append('password', 'secret');

fetch('https://api.example.com/login', {
    method: 'POST',
    body: formData  // 不需要设置 Content-Type，浏览器自动设置为 multipart/form-data
})
    .then(res => res.json());

// URL 编码表单
const params = new URLSearchParams();
params.append('username', 'john');
params.append('password', 'secret');

fetch('https://api.example.com/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: params
})
    .then(res => res.json());

// 文件上传
const fileInput = document.querySelector('input[type="file"]');
const formData = new FormData();
formData.append('avatar', fileInput.files[0]);

fetch('/upload', {
    method: 'POST',
    body: formData
});
```

### 2.4 其他 HTTP 方法

```javascript
// PUT - 更新资源
fetch('https://api.example.com/users/1', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: 'New Name' })
});

// PATCH - 部分更新
fetch('https://api.example.com/users/1', {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: 'Updated' })
});

// DELETE - 删除
fetch('https://api.example.com/users/1', {
    method: 'DELETE'
});

// HEAD - 获取响应头（无响应体）
fetch('https://example.com/file.txt', {
    method: 'HEAD'
}).then(res => {
    console.log('Content-Length:', res.headers.get('Content-Length'));
    console.log('Content-Type:', res.headers.get('Content-Type'));
});

// OPTIONS - 获取支持的方法
fetch('https://api.example.com/resource', {
    method: 'OPTIONS'
}).then(res => {
    console.log('Allow:', res.headers.get('Allow'));
});
```

---

## 三、响应处理

### 3.1 Response 对象

```javascript
fetch(url).then(response => {
    // 基本属性
    console.log(response.status);      // 200 (状态码)
    console.log(response.statusText);  // "OK" (状态文本)
    console.log(response.ok);          // true (200-299 之间)
    console.log(response.url);         // 最终 URL
    console.log(response.redirected);  // 是否重定向
    console.log(response.type);        // basic, cors, opaque
    
    // 响应头
    console.log(response.headers.get('Content-Type'));
    console.log(response.headers.get('Content-Length'));
    console.log(response.headers.has('X-Custom'));
    
    // 遍历响应头
    response.headers.forEach((value, key) => {
        console.log(`${key}: ${value}`);
    });
    
    // 响应体方法（只能调用一次，因为是流）
    return response.json();   // 解析为 JSON
    // return response.text();    // 解析为文本
    // return response.blob();    // 解析为 Blob
    // return response.formData(); // 解析为 FormData
    // return response.arrayBuffer(); // 解析为 ArrayBuffer
    // response.body  // ReadableStream（流式读取）
});
```

### 3.2 错误处理

```javascript
// fetch 只在网络错误时 reject
// HTTP 4xx/5xx 不会 reject，需要手动检查
async function safeFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            // HTTP 错误
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('Content-Type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            return await response.text();
        }
        
    } catch (error) {
        // 网络错误或其他错误
        console.error('请求失败:', error.message);
        throw error;
    }
}

// 区分错误类型
async function fetchWithErrorHandling(url) {
    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            if (response.status === 401) {
                throw new Error('未授权，请登录');
            } else if (response.status === 403) {
                throw new Error('禁止访问');
            } else if (response.status === 404) {
                throw new Error('资源不存在');
            } else if (response.status >= 500) {
                throw new Error('服务器错误');
            } else {
                throw new Error(`HTTP 错误: ${response.status}`);
            }
        }
        
        return await response.json();
    } catch (error) {
        if (error.message === 'Failed to fetch') {
            console.error('网络连接失败');
        } else if (error.name === 'AbortError') {
            console.error('请求被取消');
        } else {
            console.error('错误:', error.message);
        }
        throw error;
    }
}
```

### 3.3 请求取消 (AbortController)

```javascript
// 取消请求
const controller = new AbortController();
const signal = controller.signal;

fetch('https://api.example.com/large-data', { signal })
    .then(res => res.json())
    .then(data => console.log(data))
    .catch(error => {
        if (error.name === 'AbortError') {
            console.log('请求已取消');
        } else {
            console.error('错误:', error);
        }
    });

// 5 秒后取消请求
setTimeout(() => controller.abort(), 5000);

// 超时封装
function fetchWithTimeout(url, options = {}, timeout = 5000) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    return fetch(url, {
        ...options,
        signal: controller.signal
    }).finally(() => clearTimeout(id));
}
```

### 3.4 流式读取

```javascript
// 流式读取响应体（处理大文件）
async function streamFetch(url) {
    const response = await fetch(url);
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    let result = '';
    
    while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
            console.log('读取完成');
            break;
        }
        
        // 处理每个数据块
        result += decoder.decode(value, { stream: true });
        console.log(`已接收 ${value.length} 字节`);
    }
    
    return result;
}

// 下载进度
async function downloadWithProgress(url) {
    const response = await fetch(url);
    const total = +response.headers.get('Content-Length');
    let loaded = 0;
    
    const reader = response.body.getReader();
    const chunks = [];
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        chunks.push(value);
        loaded += value.length;
        
        if (total) {
            const percent = ((loaded / total) * 100).toFixed(2);
            console.log(`下载进度: ${percent}% (${loaded}/${total})`);
        }
    }
    
    // 组合数据
    const content = new Uint8Array(loaded);
    let offset = 0;
    for (const chunk of chunks) {
        content.set(chunk, offset);
        offset += chunk.length;
    }
    
    return content;
}
```

---

## 四、安全相关内容

### 4.1 CORS（跨域资源共享）

```javascript
/*
    CORS 错误：
    当 fetch 跨域请求被 CORS 策略阻止时，
    浏览器会在控制台报错，fetch 的 promise 会 reject
    
    常见原因：
    1. 服务器没有设置 Access-Control-Allow-Origin
    2. 自定义请求头触发预检请求 (OPTIONS)
    3. 凭证请求需要特定的 CORS 配置
*/

// 简单请求（不会触发预检）
// - 方法: GET, HEAD, POST
// - Content-Type: text/plain, multipart/form-data, application/x-www-form-urlencoded
// - 无自定义请求头

// 需要预检 (preflight) 的请求
// - 方法: PUT, DELETE, PATCH, CONNECT, OPTIONS, TRACE
// - 自定义请求头
// - Content-Type: application/json 等
fetch('https://api.example.com/data', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',  // 会触发预检
        'X-Custom-Header': 'value'           // 会触发预检
    },
    body: JSON.stringify({ data: 'test' })
})
    .then(res => res.json())
    .catch(err => console.error('CORS 错误或网络错误:', err));

// 携带 Cookie 的跨域请求
fetch('https://api.example.com/user', {
    credentials: 'include'  // 必须设置为 include
})
    .then(res => res.json());
/*
    注意：带凭证的请求要求服务器：
    1. Access-Control-Allow-Credentials: true
    2. Access-Control-Allow-Origin 不能是 *，必须指定具体域名
*/
```

### 4.2 XSS 与 CSRF 防护

```javascript
/*
    XSS 注意事项：
    - 不要把用户输入直接插入 HTML
    - 响应数据要经过转义再显示
    - fetch 返回的 JSON 数据如果用于 innerHTML，需要转义
*/

// 不安全
fetch('/api/username')
    .then(res => res.text())
    .then(username => {
        document.getElementById('user').innerHTML = username;  // ❌ XSS 风险
    });

// 安全
fetch('/api/username')
    .then(res => res.text())
    .then(username => {
        document.getElementById('user').textContent = username;  // ✅ 安全
    });

/*
    CSRF 防护：
    - 使用 CSRF Token
    - 验证 Referer / Origin
    - SameSite Cookie
*/

// 带 CSRF Token 的请求
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

fetch('/api/action', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken  // 自定义头传递 token
    },
    body: JSON.stringify(data),
    credentials: 'same-origin'  // 携带 cookie
});
```

### 4.3 安全请求封装

```javascript
class SecureFetch {
    constructor(baseUrl, options = {}) {
        this.baseUrl = baseUrl;
        this.token = options.token || null;
        this.timeout = options.timeout || 10000;
    }
    
    setToken(token) {
        this.token = token;
    }
    
    async request(path, options = {}) {
        const url = new URL(path, this.baseUrl).toString();
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        
        const headers = {
            'Accept': 'application/json',
            ...options.headers
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        // 自动设置 JSON Content-Type
        if (options.body && typeof options.body === 'object' && 
            !(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(options.body);
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers,
                signal: controller.signal,
                credentials: options.credentials || 'same-origin'
            });
            
            clearTimeout(timeoutId);
            
            // 处理不同状态码
            if (response.status === 401) {
                // token 过期等
                this.token = null;
                throw new Error('Unauthorized');
            }
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}`);
            }
            
            const contentType = response.headers.get('Content-Type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            return await response.text();
            
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('请求超时');
            }
            throw error;
        }
    }
    
    get(path, params) {
        if (params) {
            const searchParams = new URLSearchParams(params);
            path += '?' + searchParams.toString();
        }
        return this.request(path, { method: 'GET' });
    }
    
    post(path, data) {
        return this.request(path, { method: 'POST', body: data });
    }
    
    put(path, data) {
        return this.request(path, { method: 'PUT', body: data });
    }
    
    delete(path) {
        return this.request(path, { method: 'DELETE' });
    }
}

// 使用
const api = new SecureFetch('https://api.example.com', {
    timeout: 8000
});

// 设置 token 后自动添加 Authorization 头
api.setToken('user-jwt-token');

// 调用
api.get('/users', { page: 1, limit: 10 })
    .then(data => console.log(data));

api.post('/users', { name: 'test', email: 'test@example.com' })
    .then(data => console.log(data));
```

---

## 五、注意事项

| 注意点 | 说明 |
|-------|------|
| Promise | fetch 返回 Promise，注意错误处理 |
| 只在网络错误时 reject | HTTP 4xx/5xx 不会 reject，需要手动检查 response.ok |
| 响应体只能读一次 | json()/text()/blob() 等只能调用一次 |
| 跨域 | 受 CORS 限制，需要服务器配合 |
| Cookie | 默认不携带，需设置 credentials |
| 取消请求 | 使用 AbortController |
| 进度 | 大文件下载进度需要用 ReadableStream |
| 兼容性 | IE 不支持，旧浏览器需 polyfill |
| Node.js | 18+ 版本内置，旧版本需 node-fetch |
