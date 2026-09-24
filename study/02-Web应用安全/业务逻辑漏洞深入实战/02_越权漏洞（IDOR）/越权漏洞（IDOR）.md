# 越权漏洞（IDOR）

### 2.1 原理

越权漏洞（Insecure Direct Object Reference，IDOR）是指应用程序在处理对象引用时未做归属校验，导致用户可以访问不属于自己权限范围内的数据或功能。OWASP 将其归类于访问控制失效（Broken Access Control，A01:2021）。

### 2.2 水平越权

同一级别用户之间越权访问彼此数据。例如用户 A 通过修改 URL 中的用户 ID 参数查看用户 B 的订单。

请求示例：

```http
GET /api/orders?order_id=10234 HTTP/1.1
Cookie: session=userA
```

攻击者将 `order_id` 遍历为 `10235`、`10236` 即可查看他人订单，无需任何特殊 Payload。

### 2.3 垂直越权

低权限用户访问高权限功能。例如普通用户直接请求管理员接口：

```http
POST /admin/users/delete HTTP/1.1
Cookie: session=normal_user
Content-Type: application/json

{"user_id": 1001}
```

若后端仅依靠前端隐藏菜单项而非服务端鉴权，则删除操作成功执行。

### 2.4 实战案例：电商订单越权查看

某电商平台订单详情接口：

```
GET /order/detail?orderId=500123
```

服务端代码（PHP，漏洞版本）：

```php
// 漏洞代码：只验证登录，未校验订单归属
$order_id = $_GET['orderId'];
$order = $db->query("SELECT * FROM orders WHERE id = {$order_id}");
echo json_encode($order);
```

攻击者只需遍历 `orderId` 即可拉取全站订单数据。

### 2.5 漏洞代码对比（Java）

```java
// 漏洞版本：直接用请求参数查询，无归属校验
@GetMapping("/order/{id}")
public Order getOrder(@PathVariable Long id) {
    return orderRepository.findById(id).orElse(null);
}

// 安全版本：校验订单归属于当前用户
@GetMapping("/order/{id}")
public Order getOrder(@PathVariable Long id, @AuthenticationPrincipal UserDetails user) {
    Order order = orderRepository.findById(id)
        .orElseThrow(() -> new NotFoundException("订单不存在"));
    if (!order.getUserId().equals(user.getId())) {
        throw new ForbiddenException("无权访问该订单");
    }
    return order;
}
```

### 2.6 防御方案

1. **权限校验中间件**：在所有涉及对象访问的接口统一拦截，校验 `object.owner == current_user`。
2. **RBAC 模型**：基于角色的访问控制，角色-权限映射集中管理，避免散落的 `if (isAdmin)` 判断。
3. **使用不可枚举 ID**：用 UUID 替代自增 ID，提高遍历成本（但不可作为唯一防护）。
4. **默认拒绝原则**：无明确授权即拒绝访问。

RBAC 权限校验中间件示例（Python/Flask）：

```python
from functools import wraps
from flask import request, g, abort

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = g.current_user
            if not user or not user.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/admin/users/delete', methods=['POST'])
@require_permission('user:delete')
def delete_user():
    # 仅拥有 user:delete 权限的角色可执行
    ...
```

### 2.7 Python 越权检测脚本

```python
import requests
from concurrent.futures import ThreadPoolExecutor

class IDORDetector:
    """越权漏洞检测器：遍历对象ID，判断是否返回他人数据"""
    def __init__(self, base_url, session_cookie):
        self.base_url = base_url.rstrip('/')
        self.cookies = {'session': session_cookie}
        self.findings = []

    def check_idor(self, endpoint, param, id_range, baseline_id):
        """
        endpoint: 接口路径，如 /api/orders/{id}
        param: 参数占位符，如 {id}
        baseline_id: 当前用户自身的ID，用于基准对比
        """
        # 获取基准响应（自己的数据）
        baseline = requests.get(
            f"{self.base_url}{endpoint.replace(param, str(baseline_id))}",
            cookies=self.cookies, timeout=10
        )
        baseline_data = baseline.json()

        def test_one(obj_id):
            url = f"{self.base_url}{endpoint.replace(param, str(obj_id))}"
            try:
                resp = requests.get(url, cookies=self.cookies, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    # 响应与基准不同且成功返回 => 疑似越权
                    if data != baseline_data and self._contains_user_data(data):
                        return {
                            'id': obj_id,
                            'status': resp.status_code,
                            'evidence': '返回了非自身对象数据'
                        }
            except Exception:
                pass
            return None

        with ThreadPoolExecutor(max_workers=10) as pool:
            results = list(pool.map(test_one, id_range))
        self.findings.extend([r for r in results if r])
        return self.findings

    def _contains_user_data(self, data):
        """判断响应是否包含敏感字段"""
        sensitive_keys = {'phone', 'email', 'address', 'id_card', 'password'}
        text = str(data).lower()
        return any(k in text for k in sensitive_keys)

# 使用示例
detector = IDORDetector('https://target.com', 'userA_session_cookie')
results = detector.check_idor('/api/orders/{id}', '{id}', range(10200, 10300), 10234)
for r in results:
    print(f"[!] IDOR: order_id={r['id']} -> {r['evidence']}")
```

---

---

