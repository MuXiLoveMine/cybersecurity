# 密码服务 API 设计

### 9.1 密钥托管架构

```
企业密钥托管（KMS）架构：

┌──────────────────────────────────────────────────┐
│                  应用层                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│  │ Web应用  │ │ 数据库   │ │ API网关  │            │
│  └────┬────┘ └────┬────┘ └────┬────┘            │
│       │           │           │                  │
├───────┴───────────┴───────────┴──────────────────┤
│                加密API网关                         │
│  ┌──────────────────────────────────────────┐    │
│  │  encrypt(plaintext, key_id) → ciphertext │    │
│  │  decrypt(ciphertext, key_id) → plaintext  │    │
│  │  sign(data, key_id) → signature           │    │
│  │  verify(data, signature, key_id) → bool   │    │
│  └──────────────────────────────────────────┘    │
├──────────────────────────────────────────────────┤
│                密钥管理层                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 主密钥    │  │ 数据密钥  │  │ 密钥版本  │       │
│  │ (KEK)    │  │ (DEK)    │  │ 管理     │       │
│  └──────────┘  └──────────┘  └──────────┘       │
├──────────────────────────────────────────────────┤
│                硬件安全层                          │
│  ┌──────────────────────────────────────────┐    │
│  │           HSM (硬件安全模块)               │    │
│  │  ┌────────┐  ┌────────┐  ┌────────┐       │    │
│  │  │主密钥   │  │密钥保护 │  │随机数   │       │    │
│  │  │存储     │  │ 隔离    │  │生成器   │       │    │
│  │  └────────┘  └────────┘  └────────┘       │    │
│  └──────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘

密钥层次：
  Level 1: 主密钥（KEK）→ 永不出HSM
  Level 2: 数据加密密钥（DEK）→ 由KEK加密后存储
  Level 3: 数据 → 由DEK加密
```

### 9.2 密钥轮换 API

```python
class KeyRotationService:
    """密钥轮换服务"""
    
    def __init__(self, hsm, key_db):
        self.hsm = hsm  # 硬件安全模块
        self.key_db = key_db
        
    def rotate_key(self, key_id, algorithm='AES-256-GCM'):
        """轮换指定密钥"""
        # 1. 生成新密钥版本
        new_version = self._get_next_version(key_id)
        new_key_id = f"{key_id}-v{new_version}"
        
        # 2. 在HSM中生成新密钥
        new_dek = self.hsm.generate_key(algorithm)
        
        # 3. 用主密钥加密新DEK
        encrypted_dek = self.hsm.encrypt_with_kek(new_dek)
        
        # 4. 存储新密钥版本
        self.key_db.store({
            'key_id': new_key_id,
            'parent_id': key_id,
            'version': new_version,
            'encrypted_key': encrypted_dek,
            'algorithm': algorithm,
            'created_at': time.time(),
            'status': 'active'
        })
        
        # 5. 旧版本标记为"只解密"（解密旧数据仍可用）
        self.key_db.update_status(
            f"{key_id}-v{new_version-1}",
            status='decrypt_only'
        )
        
        # 6. 触发数据重加密任务（异步）
        self._schedule_reencryption(key_id)
        
        return new_key_id
    
    def decrypt_with_fallback(self, ciphertext, key_id_version):
        """支持多版本密钥的解密"""
        key = self.key_db.get(key_id_version)
        if key['status'] not in ['active', 'decrypt_only']:
            raise ValueError(f"Key {key_id_version} not available")
        
        dek = self.hsm.decrypt_with_kek(key['encrypted_key'])
        return self.hsm.decrypt(ciphertext, dek)


class CryptoAPIGateway:
    """加密API网关"""
    
    def __init__(self, key_service):
        self.key_service = key_service
        
    def encrypt(self, plaintext, key_id, aad=None):
        """
        加密数据
        plaintext: 明文
        key_id: 密钥标识（自动选择active版本）
        aad: 附加认证数据（AEAD模式）
        """
        # 获取当前活跃密钥
        active_key = self.key_service.get_active_key(key_id)
        
        # 在HSM中加密（密钥不出HSM）
        result = self.hsm.encrypt(
            data=plaintext,
            key_handle=active_key.handle,
            algorithm='AES-256-GCM',
            aad=aad
        )
        
        return {
            'ciphertext': result.ciphertext,
            'iv': result.iv,
            'tag': result.tag,
            'key_version': active_key.version,
            'algorithm': 'AES-256-GCM'
        }
    
    def decrypt(self, encrypted_data, aad=None):
        """解密数据（自动选择对应版本密钥）"""
        key_version = encrypted_data['key_version']
        key = self.key_service.get_key(key_version)
        
        plaintext = self.hsm.decrypt(
            ciphertext=encrypted_data['ciphertext'],
            iv=encrypted_data['iv'],
            tag=encrypted_data['tag'],
            key_handle=key.handle,
            aad=aad
        )
        
        return plaintext
```

---

---

## 📋 内容审核与补充建议

> 针对「密码服务 API 设计」部分的内容审核结果：

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
