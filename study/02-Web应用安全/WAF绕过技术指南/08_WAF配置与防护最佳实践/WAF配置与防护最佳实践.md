# WAF配置与防护最佳实践

### 8.1 WAF规则配置

**ModSecurity核心规则集（CRS）配置：**

```apache
# ModSecurity配置示例
# 启用ModSecurity
SecRuleEngine On

# 设置默认动作
SecDefaultAction "phase:2,pass,log,tag:'WAS_TEST'"

# 请求体大小限制
SecRequestBodyLimit 134217728  # 128MB
SecRequestBodyNoFilesLimit 1048576  # 1MB

# 请求体访问
SecRequestBodyAccess On

# 响应体访问
SecResponseBodyAccess On
SecResponseBodyLimit 524288  # 512KB

# 日志配置
SecAuditEngine RelevantOnly
SecAuditLogType Serial
SecAuditLog /var/log/modsec_audit.log

# 包含OWASP CRS
IncludeOptional /usr/share/modsecurity-crs/*.rules
```

**关键规则配置原则：**

```
WAF规则配置原则:
├── 防御深度
│   ├── 规则匹配（第一层）
│   ├── 语义分析（第二层）
│   └── 行为分析（第三层）
│
├── 防护范围
│   ├── SQL注入（OWASP CRS规则集）
│   ├── XSS（输出编码+输入过滤）
│   ├── 文件上传（后缀+内容+大小）
│   ├── 命令注入（特殊字符过滤）
│   ├── 路径穿越（../过滤）
│   ├── SSRF（内网IP过滤）
│   └── 反序列化（Content-Type检测）
│
├── 规则质量
│   ├── 避免过度依赖正则
│   ├── 使用语义分析引擎
│   ├── 定期更新规则
│   └── 减少误报（白名单调优）
│
└── 响应策略
    ├── 拦截（Block）
    ├── 挑战（CAPTCHA/JS Challenge）
    ├── 监控（Log Only）
    └── 限流（Rate Limiting）
```

### 8.2 防护加固措施

```
WAF防护加固清单:
├── 网络层
│   ├── 限制WAF管理面访问
│   ├── 配置IP信誉库联动
│   ├── 启用DDoS防护
│   └── 设置连接数限制
│
├── 协议层
│   ├── 强制HTTPS（HSTS）
│   ├── 禁用不安全的方法
│   ├── 设置安全响应头
│   │   ├── X-Content-Type-Options: nosniff
│   │   ├── X-Frame-Options: DENY
│   │   ├── X-XSS-Protection: 1; mode=block
│   │   ├── Content-Security-Policy
│   │   └── Strict-Transport-Security
│   └── 正确处理分块传输
│
├── 应用层
│   ├── 启用OWASP CRS
│   ├── 自定义业务规则
│   ├── 限制请求频率
│   ├── 检测机器人行为
│   └── 配置Bot管理策略
│
└── 运维层
    ├── 定期更新规则库
    ├── 误报监控和调优
    ├── 日志分析和告警
    ├── 规则上线前测试
    └── 应急响应流程
```

### 8.3 多层防护体系

WAF不应是唯一的防护手段，应构建多层防御体系：

```
纵深防御体系:
┌──────────────────────────────────────────────────────┐
│                    第一层: 边缘防护                   │
│  CDN + DDoS防护 + IP信誉 + 速率限制                    │
├──────────────────────────────────────────────────────┤
│                    第二层: WAF防护                     │
│  规则匹配 + 语义分析 + 行为分析 + 机器学习              │
├──────────────────────────────────────────────────────┤
│                    第三层: 网关防护                    │
│  API网关 + 认证授权 + 限流 + 路由控制                  │
├──────────────────────────────────────────────────────┤
│                    第四层: 应用防护                    │
│  安全编码 + 输入验证 + 输出编码 + 参数化查询           │
├──────────────────────────────────────────────────────┤
│                    第五层: 运行时防护                  │
│  RASP + 进程监控 + 文件完整性 + 内存保护               │
├──────────────────────────────────────────────────────┤
│                    第六层: 日志审计                    │
│  日志收集 + SIEM + 威胁检测 + 应急响应                 │
└──────────────────────────────────────────────────────┘
```

### 8.4 WAF规则测试与调优

```python
# WAF规则测试脚本（概念示意）
import requests
import json

class WAFTester:
    def __init__(self, target, waf_log=None):
        self.target = target
        self.waf_log = waf_log
        self.test_cases = self.load_test_cases()
    
    def load_test_cases(self):
        """加载测试用例"""
        return {
            'sql_injection': [
                "1' OR '1'='1",
                "1 UNION SELECT 1,2,3--",
                "1'; DROP TABLE users--",
            ],
            'xss': [
                "<script>alert(1)</script>",
                "<img src=x onerror=alert(1)>",
                "\"><script>alert(1)</script>",
            ],
            'file_upload': [
                "shell.php",
                "shell.jpg.php",
                ".htaccess",
            ],
        }
    
    def test_all(self):
        """执行全部测试"""
        results = []
        for attack_type, payloads in self.test_cases.items():
            for payload in payloads:
                # 发送攻击Payload
                r = requests.get(self.target, params={'q': payload})
                # 判断是否被拦截
                blocked = r.status_code == 403 or 'blocked' in r.text.lower()
                results.append({
                    'type': attack_type,
                    'payload': payload,
                    'blocked': blocked,
                    'status': r.status_code,
                })
        
        # 统计
        total = len(results)
        blocked = sum(1 for r in results if r['blocked'])
        print(f'拦截率: {blocked}/{total} = {blocked/total*100:.1f}%')
        return results
    
    def check_false_positives(self, normal_inputs):
        """检测误报"""
        fp_count = 0
        for inp in normal_inputs:
            r = requests.get(self.target, params={'q': inp})
            if r.status_code == 403:
                fp_count += 1
                print(f'误报: {inp}')
        print(f'误报率: {fp_count}/{len(normal_inputs)}')
```

### 8.5 WAF运维最佳实践

| 实践 | 说明 | 频率 |
|------|------|------|
| 规则更新 | 更新OWASP CRS和厂商规则 | 每月 |
| 误报审查 | 检查被拦截的合法请求 | 每周 |
| 性能监控 | 监控WAF延迟和吞吐 | 持续 |
| 日志分析 | 分析攻击趋势和新型攻击 | 每日 |
| 规则测试 | 上线前在测试环境验证 | 每次变更 |
| 应急演练 | 模拟WAF绕过攻击 | 每季度 |
| 策略调优 | 根据业务变化调整规则 | 按需 |

---

---

