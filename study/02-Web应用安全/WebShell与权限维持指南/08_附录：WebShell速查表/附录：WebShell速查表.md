# 附录：WebShell速查表

### A. 常见一句话木马特征

| 语言 | 典型特征 | 检测关键词 |
|------|----------|-----------|
| PHP | eval($_POST) | eval+$_POST/assert+$_POST |
| JSP | Runtime.exec(request) | Runtime.exec+getParameter |
| ASP | eval(request()) | eval+request/Execute |
| ASPX | Process.Start(Request) | Process.Start+Request |

### B. 管理工具流量特征速查

| 工具 | 流量特征 | 检测规则 |
|------|----------|----------|
| 菜刀 | 明文Base64命令 | 正则匹配eval+base64 |
| 蚁剑 | 可定制编码 | 编码特征+行为模式 |
| 冰蝎 | AES加密+密钥协商 | 密钥协商+加密统计 |
| Godzilla | 多层加密+Session | 加密流量+会话维持 |

### C. 权限维持检测清单

```
检测项:
□ Web目录文件完整性检查
□ 异常文件（隐藏文件/深路径/异常权限）
□ PHP配置(.htaccess/.user.ini)检查
□ Cron定时任务检查
□ Windows注册表自启动项检查
□ 系统服务列表检查
□ SSH authorized_keys检查
□ Java Filter/Listener/Agent检查
□ 网络连接（反弹Shell）检查
□ 进程派生关系异常检查
```

---

> **免责声明：** 本文档所有技术内容仅用于安全研究、授权渗透测试和防御能力建设。未经授权对他人系统实施攻击行为属于违法行为。请在合法授权范围内使用所学知识。

---

