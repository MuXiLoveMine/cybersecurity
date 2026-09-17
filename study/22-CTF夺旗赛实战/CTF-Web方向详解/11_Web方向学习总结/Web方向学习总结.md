# Web方向学习总结

### 10.1 解题流程

```
1. 信息收集
   ├── 查看页面源码
   ├── 检查robots.txt
   ├── 目录扫描（dirsearch/gobuster）
   ├── 指纹识别（Wappalyzer/whatweb）
   └── 查看HTTP响应头

2. 漏洞发现
   ├── 参数测试（GET/POST/Cookie/Header）
   ├── 逻辑测试（越权/竞态/业务逻辑）
   └── 自动化扫描（Burp Active Scan）

3. 漏洞利用
   ├── 手动构造Payload
   ├── 使用自动化工具（sqlmap等）
   └── 逐步深入获取Flag

4. 后渗透
   ├── 读取Flag文件
   ├── 提权
   ├── 内网渗透
   └── 持久化（仅攻防模式）
```

### 10.2 工具清单

```
Web CTF必备工具：
├── Burp Suite（抓包、重放、扫描）
├── sqlmap（SQL注入自动化）
├── dirsearch/gobuster（目录扫描）
├── AntSword/蚁剑（Webshell管理）
├── CyberChef（编码解码）
├── Chrome DevTools（前端调试）
├── Postman（API测试）
├── wfuzz（模糊测试）
├── nmap（端口扫描）
└── Python + requests库（自定义脚本）
```

### 10.3 常用Payload速查

```
SQL注入: ' UNION SELECT 1,2,database()-- -
XSS:     <script>alert(document.cookie)</script>
SSRF:    url=http://127.0.0.1/flag
SSTI:    {{7*7}} / ${7*7}
命令注入: ; cat /flag
文件包含: ?file=php://filter/read=convert.base64-encode/resource=flag.php
XXE:     <!ENTITY xxe SYSTEM "file:///flag">
```

---

> **安全提示**：本文档中的所有技术仅用于CTF竞赛和安全学习。未经授权对真实系统进行测试属于违法行为。请始终在授权环境中练习。

---

## 📋 内容审核与补充建议

> 针对「Web方向学习总结」部分的内容审核结果：

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
