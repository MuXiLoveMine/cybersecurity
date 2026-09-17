# API Key管理

### 2.1 API Key原理

```text
API Key认证流程

1. 申请API Key
   开发者 → API平台: 申请API Key
   API平台 → 生成: key_id + secret
   开发者: 获取并安全存储

2. 使用API Key
   开发者 → API请求: Header: X-API-Key: abc123
   API网关: 验证Key → 限制/计费
   API网关 → 路由到后端服务

3. API Key格式
   ├── 明文Key: "sk-abc123xyz..." (直接传递)
   ├── 哈希Key: 存储 Key 的哈希值
   └── 前缀Key: "pk_live_xxx" / "sk_test_xxx"

API Key vs JWT:
  API Key: 静态，长期有效，无状态
  JWT: 动态，短期有效，自包含
```

### 2.2 API Key安全实践

```python
class APIKeyManager:
    """API Key安全管理器"""

    def __init__(self):
        self.key_store = {}  # key_id → {secret_hash, permissions, rate_limit}

    def generate_api_key(self, owner, permissions, environment='production'):
        """生成API Key"""
        import secrets
        import hashlib

        # 生成Key ID和Secret
        key_id = f"key_{secrets.token_hex(8)}"
        secret = secrets.token_urlsafe(32)

        # 环境前缀
        prefix = 'sk_live_' if environment == 'production' else 'sk_test_'
        api_key = f"{prefix}{key_id}_{secret}"

        # 存储哈希值（不存储明文）
        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        self.key_store[key_id] = {
            'secret_hash': secret_hash,
            'owner': owner,
            'permissions': permissions,
            'environment': environment,
            'created_at': time.time(),
            'last_used': None,
            'rate_limit': 1000  # 每分钟1000次
        }

        return {
            'api_key': api_key,
            'key_id': key_id,
            'instructions': '请安全保存API Key，不会再次显示'
        }

    def validate_api_key(self, api_key):
        """验证API Key"""
        import hashlib

        # 解析Key
        try:
            prefix, rest = api_key.split('_', 2)[0] + '_' + \
                           api_key.split('_', 2)[1], api_key.split('_', 2)[2]
            key_id, secret = rest.split('_', 1) if '_' in rest else (rest, '')
            # 更精确的解析
            parts = api_key.split('_', 2)
            key_id = parts[1]
            secret = parts[2]
        except Exception:
            return {'valid': False, 'reason': 'API Key格式错误'}

        # 查找Key
        full_key_id = f"key_{key_id}"
        if full_key_id not in self.key_store:
            return {'valid': False, 'reason': 'API Key不存在'}

        key_info = self.key_store[full_key_id]

        # 验证Secret
        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        if secret_hash != key_info['secret_hash']:
            return {'valid': False, 'reason': 'API Key无效'}

        # 检查状态
        if key_info.get('revoked', False):
            return {'valid': False, 'reason': 'API Key已撤销'}

        # 更新最后使用时间
        key_info['last_used'] = time.time()

        return {
            'valid': True,
            'owner': key_info['owner'],
            'permissions': key_info['permissions'],
            'environment': key_info['environment']
        }

    def revoke_api_key(self, key_id):
        """撤销API Key"""
        if key_id in self.key_store:
            self.key_store[key_id]['revoked'] = True
            return True
        return False

    def rotate_api_key(self, key_id):
        """轮换API Key"""
        import secrets
        import hashlib

        if key_id not in self.key_store:
            return None

        new_secret = secrets.token_urlsafe(32)
        new_secret_hash = hashlib.sha256(new_secret.encode()).hexdigest()
        self.key_store[key_id]['secret_hash'] = new_secret_hash
        self.key_store[key_id]['rotated_at'] = time.time()

        return {
            'api_key': f"sk_live_{key_id.replace('key_', '')}_{new_secret}",
            'key_id': key_id
        }


import time

# 演示
def demo_api_key():
    manager = APIKeyManager()

    # 生成
    result = manager.generate_api_key(
        owner='developer@example.com',
        permissions=['read:users', 'write:posts'],
        environment='production'
    )
    print(f"生成的API Key: {result['api_key'][:30]}...")

    # 验证
    valid = manager.validate_api_key(result['api_key'])
    print(f"验证结果: {valid['valid']}, 权限: {valid.get('permissions')}")

    # 撤销
    manager.revoke_api_key(result['key_id'])
    valid = manager.validate_api_key(result['api_key'])
    print(f"撤销后验证: {valid['valid']}, 原因: {valid.get('reason')}")


if __name__ == "__main__":
    demo_api_key()
```

---

---

## 📋 内容审核与补充建议

> 针对「API Key管理」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
