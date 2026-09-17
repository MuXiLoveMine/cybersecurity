# OSCORE：CoAP对象安全

### 8.1 OSCORE概述

OSCORE（Object Security for CoRE, RFC 8613）是CoAP的端到端安全方案，解决了DTLS的局限性：

```
DTLS vs OSCORE:

DTLS (Hop-by-Hop):
  Client ←──DTLS──→ Proxy ←──DTLS──→ Server
  
  问题: 代理需要解密流量
  - 代理成为信任节点
  - 端到端隐私无法保证
  - 代理被攻破则全暴露

OSCORE (End-to-End):
  Client ←═══════→ Proxy ←═══════→ Server
           (端到端加密)
  
  优势:
  - 代理只转发加密数据
  - 真正的端到端安全
  - 代理无需信任
  - 支持多播安全
```

### 8.2 OSCORE工作原理

```python
# OSCORE安全保护流程
class OSCORE:
    """OSCORE对象安全实现"""
    
    def __init__(self, master_secret: bytes, sender_id: bytes, 
                 recipient_id: bytes):
        self.master_secret = master_secret
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.sender_seq = 0
        
        # 派生密钥
        self.aead_key = self._derive_key(
            master_secret, sender_id, 'aead_key'
        )
        self.iv = self._derive_key(
            master_secret, sender_id, 'iv'
        )
    
    def protect(self, coap_message: bytes) -> bytes:
        """OSCORE保护CoAP消息"""
        # 1. 分离外部选项和内部内容
        external_options, inner = self._split_message(coap_message)
        
        # 2. 构造AAD (Additional Authenticated Data)
        aad = self._build_aad(
            external_options, 
            self.sender_id, 
            self.sender_seq
        )
        
        # 3. 加密内部内容
        nonce = self._build_nonce(self.iv, self.sender_seq)
        ciphertext = aes_ccm_encrypt(
            self.aead_key, nonce, aad, inner
        )
        
        # 4. 构造OSCORE选项
        oscore_option = self._build_oscore_option(
            self.sender_id, self.sender_seq, 
            ciphertext[:8]  # 8字节MAC标签
        )
        
        # 5. 组装保护后的消息
        protected = self._assemble(
            external_options, oscore_option, ciphertext
        )
        
        self.sender_seq += 1
        return protected
    
    def unprotect(self, protected_message: bytes) -> bytes:
        """OSCORE去除保护"""
        # 1. 提取OSCORE选项
        oscore_opt = self._extract_oscore_option(protected_message)
        
        # 2. 解析发送方ID和序号
        sender_id, seq, mac = self._parse_oscore_option(oscore_opt)
        
        # 3. 重建AAD
        external_options = self._get_external_options(protected_message)
        aad = self._build_aad(external_options, sender_id, seq)
        
        # 4. 构建nonce
        nonce = self._build_nonce(self.iv, seq)
        
        # 5. 解密
        plaintext = aes_ccm_decrypt(
            self.aead_key, nonce, aad, 
            oscore_opt['ciphertext']
        )
        
        # 6. 验证MAC
        if not self._verify_mac(mac, plaintext, aad):
            raise ValueError("MAC验证失败")
        
        # 7. 重组CoAP消息
        return self._reassemble(
            external_options, plaintext
        )
    
    def _derive_key(self, secret: bytes, id: bytes, 
                    info: str) -> bytes:
        """HKDF密钥派生"""
        import hashlib
        from hmac import HMAC
        
        salt = b''
        info_bytes = info.encode()
        
        # HKDF-Extract
        prk = HMAC(salt, secret, hashlib.sha256).digest()
        
        # HKDF-Expand
        okm = HMAC(prk, info_bytes, hashlib.sha256).digest()
        
        return okm[:16]  # 128-bit key
```

---

---

## 📋 内容审核与补充建议

> 针对「OSCORE：CoAP对象安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
