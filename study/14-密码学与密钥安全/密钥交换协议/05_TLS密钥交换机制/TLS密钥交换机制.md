# TLS密钥交换机制

### 5.1 TLS 1.2密钥交换

TLS 1.2支持多种密钥交换算法：

```
TLS 1.2密钥交换套件:

  RSA密钥交换:
    Client → Server: 用服务器RSA公钥加密预主密钥
    特点: 不提供前向安全性
    
  DHE密钥交换:
    Client ←→ Server: DH密钥交换 + 数字签名认证
    特点: 提供前向安全性
    
  ECDHE密钥交换:
    Client ←→ Server: ECDH密钥交换 + 数字签名认证
    特点: 前向安全性 + 高性能
    
  PSK密钥交换:
    基于预共享密钥的交换
    特点: 快速，但需要预共享密钥
    
  常见套件:
    TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
    TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
    TLS_DHE_RSA_WITH_AES_256_CBC_SHA256
```

**TLS 1.2 ECDHE-RSA握手流程：**
```
  Client                              Server
    │                                    │
    │──── ClientHello ─────────────────→│
    │     (支持的套件,曲线等)              │
    │                                    │
    │←── ServerHello ──────────────────│
    │     (选定的套件)                    │
    │←── Certificate ──────────────────│
    │     (服务器RSA证书)                 │
    │←── ServerKeyExchange ────────────│
    │     (ECDH参数+签名)                │
    │←── ServerHelloDone ──────────────│
    │                                    │
    │──── ClientKeyExchange ──────────→│
    │     (客户端ECDH公钥)               │
    │──── ChangeCipherSpec ───────────→│
    │──── Finished ────────────────────→│
    │                                    │
    │←── ChangeCipherSpec ────────────│
    │←── Finished ────────────────────│
    │                                    │
    │←──── 加密应用数据 ──────────────→│
```

### 5.2 TLS 1.3密钥交换

TLS 1.3对密钥交换进行了重大简化：

```
TLS 1.3特点:
  1. 只保留ECDHE/PSK密钥交换
  2. 移除了RSA密钥交换
  3. 所有密钥交换都提供前向安全性
  4. 支持早期数据（0-RTT）
  5. 减少了握手轮次

TLS 1.3握手流程（1-RTT）:
  Client                              Server
    │                                    │
    │──── ClientHello ─────────────────→│
    │     (key_share: 客户端ECDH公钥)    │
    │     (supported_groups)             │
    │                                    │
    │←── ServerHello ──────────────────│
    │     (key_share: 服务器ECDH公钥)    │
    │←── {EncryptedExtensions} ─────────│
    │←── {Certificate} ────────────────│
    │←── {CertificateVerify} ──────────│
    │←── {Finished} ───────────────────│
    │                                    │
    │──── {Finished} ─────────────────→│
    │                                    │
    │←──── {应用数据} ────────────────→│

  优势:
    - 密钥交换在第一个消息中就开始
    - 减少握手延迟
    - 全程前向安全
```

### 5.3 TLS密钥派生

```python
"""
TLS 1.3密钥派生过程
"""
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.hkdf import HKDF, HKDFExpand

class TLS13KeySchedule:
    """TLS 1.3密钥调度"""
    
    @staticmethod
    def hkdf_expand_label(secret: bytes, label: str, 
                          context: bytes, length: int) -> bytes:
        """TLS 1.3 HKDF-Expand-Label"""
        full_label = f"tls13 {label}".encode()
        
        # 构造HkdfLabel
        import struct
        hkdf_label = (
            struct.pack("!H", length) +  # Length
            bytes([len(full_label)]) + full_label +  # Label
            bytes([len(context)]) + context  # Context
        )
        
        return HKDFExpand(
            algorithm=hashes.SHA256(),
            length=length,
            info=hkdf_label
        ).derive(secret)
    
    @staticmethod
    def derive_handshake_keys(shared_secret: bytes, 
                              hello_messages: bytes) -> dict:
        """推导握手密钥"""
        # 早期秘密
        zero = b'\x00' * 32
        early_secret = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'\x00' * 32
        ).derive(zero)
        
        # 推导秘密
        derived_secret = TLS13KeySchedule.hkdf_expand_label(
            early_secret, "derived", b'', 32
        )
        
        # 握手秘密
        handshake_secret = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=derived_secret,
            info=shared_secret
        ).derive(b'\x00' * 32)
        
        # 客户端握手流量秘密
        client_hs_secret = TLS13KeySchedule.hkdf_expand_label(
            handshake_secret, "c hs traffic", hello_messages, 32
        )
        
        # 服务器握手流量秘密
        server_hs_secret = TLS13KeySchedule.hkdf_expand_label(
            handshake_secret, "s hs traffic", hello_messages, 32
        )
        
        # 推导密钥和IV
        client_key = TLS13KeySchedule.hkdf_expand_label(
            client_hs_secret, "key", b'', 16
        )
        server_key = TLS13KeySchedule.hkdf_expand_label(
            server_hs_secret, "key", b'', 16
        )
        client_iv = TLS13KeySchedule.hkdf_expand_label(
            client_hs_secret, "iv", b'', 12
        )
        server_iv = TLS13KeySchedule.hkdf_expand_label(
            server_hs_secret, "iv", b'', 12
        )
        
        return {
            'client_key': client_key,
            'server_key': server_key,
            'client_iv': client_iv,
            'server_iv': server_iv,
            'client_secret': client_hs_secret,
            'server_secret': server_hs_secret,
        }


# 演示
shared = os.urandom(32)  # ECDH共享密钥
transcript = b"ClientHello + ServerHello"

keys = TLS13KeySchedule.derive_handshake_keys(shared, transcript)
print("TLS 1.3 密钥派生结果:")
for k, v in keys.items():
    print(f"  {k}: {v.hex()[:24]}...")
```

---

---

