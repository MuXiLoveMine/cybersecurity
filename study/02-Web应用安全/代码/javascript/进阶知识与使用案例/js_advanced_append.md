
---

## 四、高级实战案例

### 4.1 异步 Web 爬虫（Puppeteer）

使用 Puppeteer 控制浏览器进行高级爬虫和前端安全测试。

```javascript
const puppeteer = require('puppeteer');

// 高级爬虫 - 处理 JavaScript 渲染的页面
async function advancedCrawler(url) {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // 设置 User-Agent 和视口
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
    await page.setViewport({ width: 1920, height: 1080 });
    
    // 拦截请求（用于分析或修改）
    await page.setRequestInterception(true);
    page.on('request', request => {
        if (request.resourceType() === 'image') {
            request.abort();  // 不加载图片，加速爬取
        } else {
            request.continue();
        }
    });
    
    // 监听响应
    page.on('response', response => {
        console.log(`${response.status()} ${response.url()}`);
    });
    
    // 访问页面
    await page.goto(url, {
        waitUntil: 'networkidle2',  // 等待网络空闲
        timeout: 30000
    });
    
    // 滚动到底部（加载更多内容）
    await autoScroll(page);
    
    // 提取页面数据
    const data = await page.evaluate(() => {
        const results = [];
        document.querySelectorAll('.item').forEach(el => {
            results.push({
                title: el.querySelector('.title')?.textContent,
                link: el.querySelector('a')?.href
            });
        });
        return results;
    });
    
    // 截图
    await page.screenshot({ path: 'screenshot.png', fullPage: true });
    
    // 获取 cookies
    const cookies = await page.cookies();
    
    await browser.close();
    return { data, cookies };
}

// 自动滚动到底部
async function autoScroll(page) {
    await page.evaluate(async () => {
        await new Promise(resolve => {
            let totalHeight = 0;
            const distance = 100;
            const timer = setInterval(() => {
                window.scrollBy(0, distance);
                totalHeight += distance;
                if (totalHeight >= document.body.scrollHeight) {
                    clearInterval(timer);
                    resolve();
                }
            }, 100);
        });
    });
}

// XSS 检测
async function xssScanner(url, params) {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    
    const payloads = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        '"><script>alert(1)</script>',
        "'><img src=x onerror=alert(1)>"
    ];
    
    const results = [];
    
    for (const payload of payloads) {
        const testUrl = new URL(url);
        for (const [key, val] of Object.entries(params)) {
            testUrl.searchParams.set(key, payload);
        }
        
        try {
            page.on('dialog', async dialog => {
                results.push({
                    payload: payload,
                    param: key,
                    type: dialog.type(),
                    message: dialog.message()
                });
                await dialog.dismiss();
            });
            
            await page.goto(testUrl.toString(), { timeout: 5000 });
            await page.waitForTimeout(1000);
        } catch (e) {
            // 超时或错误
        }
    }
    
    await browser.close();
    return results;
}

// 使用示例
// advancedCrawler('https://example.com').then(console.log);
```

### 4.2 Node.js 安全工具

使用 Node.js 开发网络安全工具。

```javascript
const net = require('net');
const dns = require('dns');
const crypto = require('crypto');
const http = require('http');
const { URL } = require('url');

// ===== 端口扫描器 =====
class PortScanner {
    constructor(host, options = {}) {
        this.host = host;
        this.timeout = options.timeout || 1000;
        this.concurrency = options.concurrency || 50;
    }
    
    async scanPort(port) {
        return new Promise(resolve => {
            const socket = new net.Socket();
            socket.setTimeout(this.timeout);
            
            socket.once('connect', () => {
                socket.destroy();
                resolve({ port, open: true });
            });
            
            socket.once('timeout', () => {
                socket.destroy();
                resolve({ port, open: false });
            });
            
            socket.once('error', () => {
                resolve({ port, open: false });
            });
            
            socket.connect(port, this.host);
        });
    }
    
    async scanRange(start, end) {
        const ports = [];
        for (let i = start; i <= end; i++) {
            ports.push(i);
        }
        
        const openPorts = [];
        let index = 0;
        
        // 并发控制
        const workers = Array(this.concurrency).fill(null).map(async () => {
            while (index < ports.length) {
                const port = ports[index++];
                const result = await this.scanPort(port);
                if (result.open) {
                    openPorts.push(port);
                }
            }
        });
        
        await Promise.all(workers);
        return openPorts.sort((a, b) => a - b);
    }
}

// ===== 子域名爆破 =====
async function subdomainBrute(domain, wordlist) {
    const results = [];
    
    async function check(sub) {
        return new Promise(resolve => {
            dns.resolve(`${sub}.${domain}`, (err, addresses) => {
                if (!err) {
                    results.push({ subdomain: `${sub}.${domain}`, ips: addresses });
                }
                resolve();
            });
        });
    }
    
    const concurrency = 20;
    let index = 0;
    
    const workers = Array(concurrency).fill(null).map(async () => {
        while (index < wordlist.length) {
            await check(wordlist[index++]);
        }
    });
    
    await Promise.all(workers);
    return results;
}

// ===== 目录爆破 =====
async function dirBrute(baseUrl, wordlist) {
    const results = [];
    
    async function check(path) {
        return new Promise(resolve => {
            const url = new URL(path, baseUrl);
            const req = http.request(url, { method: 'HEAD' }, res => {
                if (res.statusCode !== 404) {
                    results.push({ path, status: res.statusCode });
                }
                resolve();
            });
            req.on('error', () => resolve());
            req.setTimeout(3000, () => { req.destroy(); resolve(); });
            req.end();
        });
    }
    
    const concurrency = 30;
    let index = 0;
    
    const workers = Array(concurrency).fill(null).map(async () => {
        while (index < wordlist.length) {
            await check(wordlist[index++]);
        }
    });
    
    await Promise.all(workers);
    return results.sort((a, b) => b.status - a.status);
}

// ===== 加密工具 =====
class CryptoTools {
    static md5(data) {
        return crypto.createHash('md5').update(data).digest('hex');
    }
    
    static sha1(data) {
        return crypto.createHash('sha1').update(data).digest('hex');
    }
    
    static sha256(data) {
        return crypto.createHash('sha256').update(data).digest('hex');
    }
    
    static hmacSha256(key, data) {
        return crypto.createHmac('sha256', key).update(data).digest('hex');
    }
    
    static base64Encode(data) {
        return Buffer.from(data).toString('base64');
    }
    
    static base64Decode(data) {
        return Buffer.from(data, 'base64').toString();
    }
    
    // AES 加密
    static aesEncrypt(text, key) {
        const iv = crypto.randomBytes(16);
        const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(key).slice(0, 32), iv);
        let encrypted = cipher.update(text);
        encrypted = Buffer.concat([encrypted, cipher.final()]);
        return iv.toString('hex') + ':' + encrypted.toString('hex');
    }
    
    static aesDecrypt(encrypted, key) {
        const parts = encrypted.split(':');
        const iv = Buffer.from(parts[0], 'hex');
        const encryptedText = Buffer.from(parts[1], 'hex');
        const decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.from(key).slice(0, 32), iv);
        let decrypted = decipher.update(encryptedText);
        decrypted = Buffer.concat([decrypted, decipher.final()]);
        return decrypted.toString();
    }
    
    // 字典攻击破解哈希
    static async crackHash(hash, wordlist, algorithm = 'md5') {
        const hashFunc = crypto.createHash(algorithm);
        for (const word of wordlist) {
            if (crypto.createHash(algorithm).update(word).digest('hex') === hash) {
                return word;
            }
        }
        return null;
    }
}

// 使用示例
// const scanner = new PortScanner('127.0.0.1');
// scanner.scanRange(1, 1000).then(ports => console.log('开放端口:', ports));
```

### 4.3 WebSocket 安全测试

WebSocket 安全测试工具。

```javascript
const WebSocket = require('ws');

// WebSocket 安全测试工具
class WsSecurityTester {
    constructor(url) {
        this.url = url;
        this.messages = [];
    }
    
    // 基础连接测试
    async connect(headers = {}) {
        return new Promise((resolve, reject) => {
            const ws = new WebSocket(this.url, { headers });
            
            ws.on('open', () => {
                console.log('WebSocket 连接成功');
                resolve(ws);
            });
            
            ws.on('message', data => {
                this.messages.push(data.toString());
            });
            
            ws.on('error', err => {
                reject(err);
            });
            
            setTimeout(() => reject(new Error('连接超时')), 5000);
        });
    }
    
    // 测试认证绕过
    async testAuthBypass() {
        const results = [];
        
        // 测试空 token
        try {
            await this.connect({ Authorization: '' });
            results.push({ test: '空 token', result: '可能存在认证绕过' });
        } catch (e) {
            results.push({ test: '空 token', result: '正常拒绝' });
        }
        
        return results;
    }
    
    // 测试输入验证（注入）
    async testInjection(payloads) {
        const ws = await this.connect();
        const results = [];
        
        for (const payload of payloads) {
            ws.send(payload);
            await new Promise(r => setTimeout(r, 500));
            
            // 检查是否有错误信息泄露
            const lastMsgs = this.messages.slice(-5).join(' ');
            if (lastMsgs.includes('error') || lastMsgs.includes('stack')) {
                results.push({ payload, risk: '可能存在信息泄露' });
            }
        }
        
        ws.close();
        return results;
    }
    
    // 测试速率限制
    async testRateLimit(count = 100) {
        const ws = await this.connect();
        const startTime = Date.now();
        
        for (let i = 0; i < count; i++) {
            ws.send(`test-${i}`);
        }
        
        await new Promise(r => setTimeout(r, 1000));
        const elapsed = Date.now() - startTime;
        const msgCount = this.messages.length;
        
        ws.close();
        
        return {
            sent: count,
            received: msgCount,
            time: elapsed,
            rateLimited: msgCount < count * 0.9
        };
    }
}
```

---

## 五、进阶学习资源

### 5.1 高级 JavaScript 安全

- **OWASP DOM XSS**：https://owasp.org/www-community/attacks/DOM_Based_XSS — DOM 型 XSS
- **PortSwigger XSS**：https://portswigger.net/web-security/cross-site-scripting — XSS 完整指南
- **XSS Filter Evasion**：https://www.owasp.org/index.php/XSS_Filter_Evasion_Cheat_Sheet — XSS 绕过速查表
- **Prototype Pollution**：https://github.com/HoLyVieR/prototype-pollution-nsec18 — 原型污染攻击
- **Client-Side Template Injection**：https://portswigger.net/web-security/cssti — 客户端模板注入

### 5.2 Node.js 安全

- **Node.js Security Checklist**：https://blog.risingstack.com/node-js-security-checklist/
- **OWASP NodeJS Security**：https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html
- **npm 安全**：
  - npm audit — 内置安全审计
  - snyk — 依赖漏洞扫描
  - retire.js — 检测有漏洞的 JS 库

### 5.3 前端安全工具

- **Burp Suite**：https://portswigger.net/burp — Web 安全测试工具
- **Puppeteer**：https://pptr.dev/ — Headless Chrome 自动化
- **Playwright**：https://playwright.dev/ — 微软浏览器自动化
- **Wappalyzer**：https://www.wappalyzer.com/ — 技术栈识别
- **Retire.js**：https://retirejs.github.io/retire.js/ — 检测有漏洞的 JS 库
- **BeEF**：https://beefproject.com/ — 浏览器攻击框架

### 5.4 进阶安全话题

- **XSS 高级绕过**：
  - 各种 WAF 绕过技巧
  - DOM XSS 与 Source/Sink 分析
  - Mutation XSS
  - Universal XSS

- **CSRF 高级**：
  - 各种绕过 CSRF 防护的方法
  - JSON CSRF
  - 文件上传 CSRF

- **CORS 安全**：
  - CORS 配置错误利用
  - CORS 凭证窃取
  - 预请求绕过

- **原型污染**：
  - JavaScript 原型链污染原理
  - 服务器端与客户端原型污染
  - 实际利用场景

- **WebAssembly 安全**：
  - WASM 逆向分析
  - WASM 内存安全问题

### 5.5 CTF 与练习平台

- **Hack The Box**：https://www.hackthebox.com/
- **TryHackMe**：https://tryhackme.com/
- **picoCTF**：https://picoctf.org/
- **XSS Game**：https://xss-game.appspot.com/ — Google XSS 练习
- **alert(1) to win**：https://alf.nu/alert1 — XSS 挑战
- **Bugku**：https://ctf.bugku.com/
- **攻防世界**：https://adworld.xctf.org.cn/
- **BUUCTF**：https://buuoj.cn/

### 5.6 推荐书籍

- **前端安全**：
  - 《Web 前端黑客技术揭秘》
  - 《白帽子讲 Web 安全》
  - 《XSS 跨站脚本攻击剖析与防御》

- **Node.js 安全**：
  - 《Node.js 安全实战》
  - 《Node.js Web 应用安全》

- **浏览器安全**：
  - 《浏览器安全》
  - 《Web 安全深度剖析》

### 5.7 社区与博客

- **PortSwigger Web Security**：https://portswigger.net/web-security
- **MDN Web Docs**：https://developer.mozilla.org/
- **FreeBuf**：https://www.freebuf.com/
- **安全客**：https://www.anquanke.com/
- **先知社区**：https://xz.aliyun.com/
- **Hacker News**：https://news.ycombinator.com/

### 5.8 进阶学习路线

**第 1 阶段：JavaScript 深入（1-2月）**
- 原型链、闭包、作用域
- ES6+ 新特性
- 异步编程（Promise/async/await）
- DOM/BOM 深入

**第 2 阶段：Web 安全基础（2-3月）**
- XSS 原理与分类
- CSRF 原理与利用
- CORS 与 SOP
- 前端安全配置

**第 3 阶段：高级 Web 攻击（3-4月）**
- XSS 高级绕过
- 原型链污染攻击
- 客户端模板注入
- 浏览器侧信道攻击

**第 4 阶段：Node.js 安全（2-3月）**
- Node.js 常见漏洞
- 代码审计技巧
- 反序列化攻击
- 原型污染在 Node.js 中的利用

**第 5 阶段：实战与 CTF（持续）**
- 参加 Web 方向 CTF
- 研究最新前端安全技术
- 开发安全工具
- 挖掘真实漏洞
