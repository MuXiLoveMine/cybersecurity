# PKI安全威胁与防护

### 10.1 CA被攻破

**历史案例：**

| 事件 | 年份 | 影响 |
|------|------|------|
| Comodo欺诈签发 | 2011 | 9个欺诈证书（Gmail, Skype等） |
| DigiNotar被攻破 | 2011 | 500+欺诈证书，CA破产 |
| TurkTrust错误签发 | 2012 | 为google.com签发证书 |
| CNNIC违规 | 2015 | 为中间人测试签发证书 |
| Symantec不规范 | 2015-2017 | 多次违规，最终被Chrome移除 |

**防护措施：**
1. CA必须使用HSM保护私钥
2. 定期安全审计
3. 证书透明度（CT）强制
4. 多方签名（Multi-Party Authorization）
5. 严格的安全基线要求

### 10.2 中间人攻击

```
中间人攻击场景：

  Alice ←→ Mallory ←→ Bob
         (Mallory用自己的证书
          替换双方的证书)

防护：
  1. 证书绑定（Pinning）
  2. CT监控
  3. DNS CAA记录限制
  4. HSTS（HTTP严格传输安全）
  5. 证书透明度通知
```

### 10.3 DNS CAA记录

**CAA（Certification Authority Authorization）** DNS记录允许域名所有者指定哪些CA可以为其签发证书。

```
DNS CAA记录示例：

;; 只允许Let's Encrypt签发
example.com.    CAA 0 issue "letsencrypt.org"

;; 允许DigiCert和Let's Encrypt
example.com.    CAA 0 issue "digicert.com"
example.com.    CAA 0 issue "letsencrypt.org"

;; 指定违规报告邮箱
example.com.    CAA 0 iodef "mailto:security@example.com"

;; 禁止所有CA签发（通配符需要特殊授权）
example.com.    CAA 0 issuewild ";"
```

### 10.4 私钥泄露

**私钥泄露的应对：**
1. 立即撤销证书
2. 生成新密钥对
3. 申请新证书
4. 更新所有使用旧证书的服务
5. 调查泄露原因
6. 修复安全漏洞

---

---

## 📋 内容审核与补充建议

> 针对「PKI安全威胁与防护」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
