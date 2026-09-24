# CoAP安全加固方案

### 7.1 认证与授权

```python
# CoAP安全配置示例
class CoAPSecurityConfig:
    """CoAP安全配置管理"""
    
    # 安全级别
    SECURITY_LEVELS = {
        'NONE': 0,      # 无加密无认证
        'PRE_SHARED': 1, # 预共享密钥
        'RAW_PUBLIC': 2, # 原始公钥
        'CERTIFICATE': 3, # X.509证书
    }
    
    # 推荐配置（按设备能力分级）
    RECOMMENDED = {
        'tier0': {  # 最受限设备 (<100KB RAM)
            'security': 'PRE_SHARED',
            'cipher': 'TLS_PSK_WITH_AES_128_CCM_8',
            'key_length': 16,  # 128-bit
            'rekey_interval': 86400,  # 24小时
        },
        'tier1': {  # 受限设备 (<256KB RAM)
            'security': 'RAW_PUBLIC',
            'cipher': 'TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8',
            'curve': 'secp256r1',
            'key_length': 32,
        },
        'tier2': {  # 中等设备 (>256KB RAM)
            'security': 'CERTIFICATE',
            'cipher': 'TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8',
            'cert_type': 'X.509',
            'cert_profile': 'IEEE 802.1AR (DevID)',
        },
    }
    
    @staticmethod
    def generate_psk(length: int = 16) -> bytes:
        """生成预共享密钥"""
        import os
        return os.urandom(length)
    
    @staticmethod
    def generate_ec_keypair(curve: str = 'secp256r1'):
        """生成EC密钥对"""
        from cryptography.hazmat.primitives.asymmetric import ec
        private_key = ec.generate_private_key(
            ec.SECP256R1() if curve == 'secp256r1' else ec.SECP384R1()
        )
        public_key = private_key.public_key()
        return private_key, public_key
```

### 7.2 访问控制

```python
# CoAP访问控制列表
class CoAPACL:
    """CoAP资源访问控制"""
    
    def __init__(self):
        self.acl = {}
        # 默认拒绝所有访问
        self.default_policy = 'DENY'
    
    def add_rule(self, resource: str, method: str, 
                 subject: str, action: str = 'ALLOW'):
        """添加访问控制规则"""
        if resource not in self.acl:
            self.acl[resource] = []
        
        self.acl[resource].append({
            'method': method,
            'subject': subject,  # 客户端ID/IP/证书CN
            'action': action,
        })
    
    def check(self, resource: str, method: str, 
              subject: str) -> bool:
        """检查访问权限"""
        rules = self.acl.get(resource, [])
        
        # 先检查显式规则
        for rule in rules:
            if rule['method'] == method or rule['method'] == '*':
                if rule['subject'] == subject or rule['subject'] == '*':
                    return rule['action'] == 'ALLOW'
        
        # 返回默认策略
        return self.default_policy == 'ALLOW'
    
    def load_config(self, config: dict):
        """从配置加载ACL"""
        for resource, rules in config.items():
            for rule in rules:
                self.add_rule(
                    resource, rule['method'],
                    rule['subject'], rule.get('action', 'ALLOW')
                )

# 示例配置
ACL_CONFIG = {
    '/.well-known/core': [
        {'method': 'GET', 'subject': '*', 'action': 'ALLOW'},
    ],
    '/sensors/*': [
        {'method': 'GET', 'subject': 'gateway', 'action': 'ALLOW'},
        {'method': 'GET', 'subject': 'admin', 'action': 'ALLOW'},
    ],
    '/actuators/*': [
        {'method': 'PUT', 'subject': 'admin', 'action': 'ALLOW'},
        {'method': 'POST', 'subject': 'admin', 'action': 'ALLOW'},
        {'method': '*', 'subject': '*', 'action': 'DENY'},
    ],
    '/firmware': [
        {'method': 'GET', 'subject': 'admin', 'action': 'ALLOW'},
        {'method': 'POST', 'subject': 'admin', 'action': 'ALLOW'},
    ],
}
```

### 7.3 防重放攻击

```python
# CoAP防重放机制
class CoAPReplayProtection:
    """CoAP消息重放防护"""
    
    def __init__(self, window_size: int = 64):
        self.window_size = window_size
        self.received_msg_ids = {}  # 按来源记录
        self.max_msg_id = {}  # 每个来源的最大Message ID
    
    def check_replay(self, source: str, msg_id: int) -> bool:
        """检查是否为重放消息"""
        if source not in self.received_msg_ids:
            self.received_msg_ids[source] = set()
            self.max_msg_id[source] = 0
        
        # 新消息
        if msg_id > self.max_msg_id[source]:
            # 滑动窗口
            self._slide_window(source, msg_id)
            self.received_msg_ids[source].add(msg_id)
            self.max_msg_id[source] = msg_id
            return True  # 非重放
        
        # 在窗口内
        if msg_id in self.received_msg_ids[source]:
            return False  # 重放
        
        # 在窗口内但未见过
        self.received_msg_ids[source].add(msg_id)
        return True  # 非重放
    
    def _slide_window(self, source: str, new_max: int):
        """滑动窗口"""
        min_allowed = new_max - self.window_size
        self.received_msg_ids[source] = {
            mid for mid in self.received_msg_ids[source]
            if mid > min_allowed
        }
```

---

---

