# 附录：WAF绕过速查表

### A. SQL注入绕过速查

| 绕过方式 | 示例 | 适用 |
|----------|------|------|
| 大小写 | UnIoN SeLeCt | 通用 |
| 注释分割 | UN/**/ION | 通用 |
| 内联注释 | /*!50000UNION*/ | MySQL |
| URL编码 | %55NION | 通用 |
| 双重编码 | %2555NION | 存在解码 |
| 空格替代 | UNION%0aSELECT | 通用 |
| 等价函数 | current_user() | 通用 |
| HPP | id=1&id=UNION | 特定后端 |
| 分块传输 | chunked编码 | 特定WAF |

### B. XSS绕过速查

| 绕过方式 | 示例 | 适用 |
|----------|------|------|
| 标签变形 | `<ScRiPt>` | 通用 |
| 事件替代 | `<svg onload>` | 通用 |
| HTML实体 | `&#60;script&#62;` | 通用 |
| JS编码 | `\u0061lert` | 通用 |
| Base64 | `eval(atob(...))` | 通用 |
| Data URI | `data:text/html` | 通用 |
| JSONP | 利用白名单域 | CSP绕过 |

### C. 命令注入绕过速查

| 绕过方式 | 示例 | 适用 |
|----------|------|------|
| 通配符 | `/etc/pa??wd` | Linux Shell |
| 变量拼接 | `a=ca;b=t;$a$b` | Linux Shell |
| 编码 | `base64 \| sh` | 通用 |
| 空格替代 | `cat${IFS}` | Linux Shell |
| 引号 | `c'a't` | Linux Shell |
| 反斜杠 | `c\at` | Linux Shell |

---

> **免责声明：** 本文档所有技术内容仅用于安全研究、授权渗透测试和防御能力建设。未经授权对他人系统实施攻击行为属于违法行为。WAF绕过技术的目的是帮助安全人员评估和改进防护能力，请始终在合法授权范围内使用。

---

