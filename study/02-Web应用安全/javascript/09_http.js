/**
 * 09_http.js - Node.js http 模块发送请求和创建简单服务器
 * 
 * 本示例演示 Node.js 中 HTTP 相关操作：
 * - 创建 HTTP 服务器
 * - 处理不同路由
 * - 发送 GET/POST 请求
 * - 处理请求和响应
 * - 简单的安全防护
 * 
 * 运行方式：node 09_http.js
 * 然后在浏览器访问 http://localhost:3000
 */

const http = require('http');
const url = require('url');
const querystring = require('querystring');

// ========== 1. 创建 HTTP 服务器 ==========

console.log("=== 1. 创建 HTTP 服务器 ===");

const PORT = 3000;

const server = http.createServer((req, res) => {
    // 解析请求 URL
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    const query = parsedUrl.query;

    console.log(`[${new Date().toLocaleTimeString()}] ${req.method} ${pathname}`);

    // 设置基本响应头
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');

    // 路由处理
    if (pathname === '/' || pathname === '/index.html') {
        handleHome(req, res);
    } else if (pathname === '/about') {
        handleAbout(req, res);
    } else if (pathname === '/api/user') {
        handleUserApi(req, res, query);
    } else if (pathname === '/login' && req.method === 'POST') {
        handleLogin(req, res);
    } else if (pathname === '/search') {
        handleSearch(req, res, query);
    } else {
        handleNotFound(req, res);
    }
});

// 启动服务器
server.listen(PORT, () => {
    console.log(`服务器运行在 http://localhost:${PORT}`);
    console.log("访问以下 URL 测试不同功能：");
    console.log(`  http://localhost:${PORT}/ - 首页`);
    console.log(`  http://localhost:${PORT}/about - 关于页面`);
    console.log(`  http://localhost:${PORT}/api/user?id=1 - 用户 API`);
    console.log(`  http://localhost:${PORT}/search?q=test - 搜索页`);
});

// ========== 2. 路由处理函数 ==========

// 首页
function handleHome(req, res) {
    const html = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Node.js HTTP 服务器示例</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        .nav { margin: 20px 0; }
        .nav a { margin-right: 15px; color: #0066cc; text-decoration: none; }
        .nav a:hover { text-decoration: underline; }
        code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>Hello, Node.js HTTP 服务器！</h1>
    <p>这是一个使用 Node.js 内置 http 模块创建的简单 Web 服务器。</p>
    <div class="nav">
        <a href="/">首页</a>
        <a href="/about">关于</a>
        <a href="/api/user?id=1">用户 API</a>
        <a href="/search?q=安全">搜索测试</a>
    </div>
    <h3>可用的 API：</h3>
    <ul>
        <li><code>GET /api/user?id=1</code> - 获取用户信息</li>
        <li><code>POST /login</code> - 登录接口</li>
        <li><code>GET /search?q=关键词</code> - 搜索</li>
    </ul>
    <h3>安全相关响应头：</h3>
    <ul>
        <li><code>X-Content-Type-Options: nosniff</code></li>
        <li><code>X-Frame-Options: DENY</code></li>
    </ul>
</body>
</html>
    `;

    res.writeHead(200);
    res.end(html);
}

// 关于页面
function handleAbout(req, res) {
    const html = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>关于 - Node.js HTTP 示例</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        a { color: #0066cc; text-decoration: none; }
    </style>
</head>
<body>
    <h1>关于本项目</h1>
    <p>这是一个用于学习 Node.js HTTP 模块的示例项目。</p>
    <p>包含以下功能：</p>
    <ul>
        <li>基础 HTTP 服务器创建</li>
        <li>路由处理</li>
        <li>GET/POST 请求处理</li>
        <li>查询参数解析</li>
        <li>JSON 响应</li>
        <li>基础安全防护</li>
    </ul>
    <p><a href="/">返回首页</a></p>
</body>
</html>
    `;

    res.writeHead(200);
    res.end(html);
}

// 用户 API（GET 请求）
function handleUserApi(req, res, query) {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');

    const userId = query.id;

    // 模拟用户数据
    const users = {
        '1': { id: 1, name: '张三', age: 25, email: 'zhangsan@example.com' },
        '2': { id: 2, name: '李四', age: 30, email: 'lisi@example.com' },
        '3': { id: 3, name: '王五', age: 28, email: 'wangwu@example.com' }
    };

    if (!userId) {
        res.writeHead(400);
        res.end(JSON.stringify({ error: '缺少用户 ID 参数' }));
        return;
    }

    const user = users[userId];

    if (user) {
        res.writeHead(200);
        res.end(JSON.stringify({
            code: 200,
            message: 'success',
            data: user
        }));
    } else {
        res.writeHead(404);
        res.end(JSON.stringify({
            code: 404,
            message: '用户不存在'
        }));
    }
}

// 登录接口（POST 请求）
function handleLogin(req, res) {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');

    let body = '';

    // 接收 POST 数据
    req.on('data', chunk => {
        body += chunk.toString();
        // 限制请求体大小，防止攻击
        if (body.length > 1e6) {
            res.writeHead(413);
            res.end(JSON.stringify({ error: '请求体过大' }));
            req.connection.destroy();
        }
    });

    req.on('end', () => {
        try {
            // 解析表单数据或 JSON
            let postData;
            const contentType = req.headers['content-type'] || '';

            if (contentType.includes('application/json')) {
                postData = JSON.parse(body);
            } else {
                postData = querystring.parse(body);
            }

            const { username, password } = postData;

            // 输入验证
            if (!username || !password) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: '用户名和密码不能为空' }));
                return;
            }

            // 简单验证（实际应查询数据库）
            if (username === 'admin' && password === 'admin123') {
                res.writeHead(200);
                res.end(JSON.stringify({
                    code: 200,
                    message: '登录成功',
                    data: {
                        username: 'admin',
                        role: 'admin',
                        token: 'fake-jwt-token-' + Date.now()
                    }
                }));
            } else {
                res.writeHead(401);
                res.end(JSON.stringify({
                    code: 401,
                    message: '用户名或密码错误'
                }));
            }
        } catch (err) {
            res.writeHead(400);
            res.end(JSON.stringify({ error: '请求数据格式错误' }));
        }
    });
}

// 搜索页面
function handleSearch(req, res, query) {
    const keyword = query.q || '';

    // XSS 防护：对用户输入进行 HTML 转义
    const escapedKeyword = escapeHtml(keyword);

    const html = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>搜索 - ${escapedKeyword}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .search-box { margin: 20px 0; }
        input[type="text"] { padding: 8px; width: 300px; font-size: 14px; }
        button { padding: 8px 16px; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; }
        .warning { color: #d9534f; background: #fdf7f7; padding: 10px; border-radius: 5px; margin: 10px 0; }
        a { color: #0066cc; }
    </style>
</head>
<body>
    <h1>搜索功能演示</h1>
    <div class="search-box">
        <form method="GET" action="/search">
            <input type="text" name="q" value="${escapedKeyword}" placeholder="输入搜索关键词">
            <button type="submit">搜索</button>
        </form>
    </div>
    
    ${keyword ? `
    <div class="result">
        <h3>搜索结果：${escapedKeyword}</h3>
        <p>未找到与 "<strong>${escapedKeyword}</strong>" 相关的结果。</p>
        <div class="warning">
            <strong>安全提示：</strong>用户输入已进行 HTML 转义，防止 XSS 攻击。
            <br>你可以尝试输入 <code>&lt;script&gt;alert(1)&lt;/script&gt;</code> 测试。
        </div>
    </div>
    ` : ''}
    
    <p><a href="/">返回首页</a></p>
</body>
</html>
    `;

    res.writeHead(200);
    res.end(html);
}

// 404 页面
function handleNotFound(req, res) {
    res.writeHead(404);
    res.end(`
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>404 Not Found</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; }
        h1 { color: #d9534f; font-size: 48px; }
        a { color: #0066cc; }
    </style>
</head>
<body>
    <h1>404</h1>
    <p>页面不存在</p>
    <p><a href="/">返回首页</a></p>
</body>
</html>
    `);
}

// ========== 3. 工具函数 ==========

// HTML 转义，防止 XSS
function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// ========== 4. 发送 HTTP 请求（客户端） ==========

console.log("\n=== 2. 发送 HTTP 请求 ===");

// 等待服务器启动后再发送请求
setTimeout(() => {
    console.log("\n--- 发送 GET 请求 ---");

    const options = {
        hostname: 'localhost',
        port: PORT,
        path: '/api/user?id=1',
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const req = http.request(options, (res) => {
        let data = '';

        res.on('data', (chunk) => {
            data += chunk;
        });

        res.on('end', () => {
            console.log('状态码:', res.statusCode);
            console.log('响应头:', JSON.stringify(res.headers, null, 2));
            console.log('响应数据:', data);

            // 测试 POST 请求
            setTimeout(testPostRequest, 500);
        });
    });

    req.on('error', (err) => {
        console.error('请求错误:', err.message);
    });

    req.end();

}, 1000);

// 测试 POST 请求
function testPostRequest() {
    console.log("\n--- 发送 POST 请求（登录）---");

    const postData = JSON.stringify({
        username: 'admin',
        password: 'admin123'
    });

    const options = {
        hostname: 'localhost',
        port: PORT,
        path: '/login',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(postData)
        }
    };

    const req = http.request(options, (res) => {
        let data = '';

        res.on('data', (chunk) => {
            data += chunk;
        });

        res.on('end', () => {
            console.log('状态码:', res.statusCode);
            console.log('响应数据:', data);

            // 测试错误的登录
            setTimeout(testWrongLogin, 500);
        });
    });

    req.on('error', (err) => {
        console.error('请求错误:', err.message);
    });

    req.write(postData);
    req.end();
}

// 测试错误登录
function testWrongLogin() {
    console.log("\n--- 测试错误登录 ---");

    const postData = JSON.stringify({
        username: 'admin',
        password: 'wrongpassword'
    });

    const options = {
        hostname: 'localhost',
        port: PORT,
        path: '/login',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(postData)
        }
    };

    const req = http.request(options, (res) => {
        let data = '';

        res.on('data', (chunk) => {
            data += chunk;
        });

        res.on('end', () => {
            console.log('状态码:', res.statusCode);
            console.log('响应数据:', data);

            console.log("\n=== 请求测试完成 ===");
            console.log("服务器仍在运行，按 Ctrl+C 停止");
        });
    });

    req.on('error', (err) => {
        console.error('请求错误:', err.message);
    });

    req.write(postData);
    req.end();
}

// 错误处理
server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
        console.error(`端口 ${PORT} 已被占用，请检查是否有其他程序在使用该端口`);
    } else {
        console.error('服务器错误:', err);
    }
});
