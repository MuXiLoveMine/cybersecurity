# Python 业务逻辑测试框架

### 9.1 模拟越权测试框架

```python
import requests
from abc import ABC, abstractmethod

class BusinessLogicTest(ABC):
    """业务逻辑测试基类"""
    def __init__(self, target_url, auth_cookie):
        self.target = target_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Cookie': auth_cookie})

    @abstractmethod
    def run(self):
        """子类实现具体测试逻辑"""
        pass

class HorizontalIDORTest(BusinessLogicTest):
    """水平越权测试"""
    def run(self):
        findings = []
        # 用A账户获取自己的资源ID
        my_data = self.session.get(f"{self.target}/api/profile").json()
        my_id = my_data['user_id']
        # 尝试遍历其他ID
        for target_id in range(my_id - 5, my_id + 5):
            if target_id == my_id:
                continue
            resp = self.session.get(f"{self.target}/api/profile?uid={target_id}")
            if resp.status_code == 200 and 'phone' in str(resp.json()):
                findings.append(f"IDOR: uid={target_id} 可越权访问")
        return findings

class VerticalPrivilegeTest(BusinessLogicTest):
    """垂直越权测试"""
    ADMIN_ENDPOINTS = [
        '/admin/users/list', '/admin/system/config',
        '/admin/users/delete', '/admin/logs/view'
    ]
    def run(self):
        findings = []
        for ep in self.ADMIN_ENDPOINTS:
            resp = self.session.get(f"{self.target}{ep}")
            if resp.status_code == 200:
                findings.append(f"垂直越权: {ep} 可被普通用户访问")
        return findings
```

### 9.2 并发条件竞争测试脚本

```python
import threading
import requests
import time

class RaceConditionTester:
    """并发条件竞争测试器"""
    def __init__(self, target_url, cookie, threads=50):
        self.url = target_url
        self.headers = {'Cookie': cookie}
        self.threads = threads
        self.results = []
        self.barrier = threading.Barrier(threads)

    def execute_concurrent(self, payload_builder):
        """并发执行同一请求"""
        def worker():
            payload = payload_builder()
            self.barrier.wait()  # 确保所有线程同时发请求
            resp = requests.post(self.url, headers=self.headers, json=payload, timeout=10)
            self.results.append({'status': resp.status_code, 'body': resp.text[:200]})

        workers = [threading.Thread(target=worker) for _ in range(self.threads)]
        for w in workers: w.start()
        for w in workers: w.join()

        success = sum(1 for r in self.results if r['status'] == 200)
        if success > 1:
            print(f"[!] 条件竞争: {success}/{self.threads} 次操作成功（应仅1次）")
        else:
            print(f"[+] 无条件竞争: {success}/1 次成功")
        return self.results

# 使用示例
tester = RaceConditionTester('https://shop.target/api/coupon/redeem', 'session=hacker', 30)
tester.execute_concurrent(lambda: {'coupon_code': 'NEWUSER50'})
```

### 9.3 业务流程自动化测试

```python
import requests
import json

class BusinessFlowTester:
    """端到端业务流程自动化测试"""
    def __init__(self, base_url):
        self.base = base_url.rstrip('/')
        self.session = requests.Session()

    def test_checkout_flow(self):
        """测试完整下单支付流程"""
        report = []

        # 1. 登录
        self.session.post(f"{self.base}/login",
                          json={"username": "testuser", "password": "Test1234!"})

        # 2. 查看商品
        product = self.session.get(f"{self.base}/api/products/P1001").json()
        original_price = product['price']

        # 3. 篡改金额下单
        resp = self.session.post(f"{self.base}/api/order/create",
                                 json={"product_id": "P1001", "quantity": 1, "price": 0.01})
        if resp.status_code == 200 and resp.json().get('success'):
            report.append("[!] 金额篡改漏洞: 服务端接受了篡改价格")

        # 4. 负数数量测试
        resp = self.session.post(f"{self.base}/api/order/create",
                                 json={"product_id": "P1001", "quantity": -1, "price": original_price})
        if resp.status_code == 200:
            report.append("[!] 负数数量漏洞: 服务端接受了负数数量")

        # 5. 超大数量溢出测试
        resp = self.session.post(f"{self.base}/api/order/create",
                                 json={"product_id": "P1001", "quantity": 2147483648, "price": original_price})
        total = resp.json().get('total', 0)
        if total < 0 or total < original_price:
            report.append(f"[!] 整数溢出: quantity=2147483648 时 total={total}")

        if not report:
            report.append("[+] 下单支付流程逻辑校验正常")
        return report

# 运行测试
tester = BusinessFlowTester('https://shop.target')
for finding in tester.test_checkout_flow():
    print(finding)
```

---

---

## 📋 内容审核与补充建议

> 针对「Python 业务逻辑测试框架」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
