# Signal协议密钥交换

### 6.1 Signal协议概述

**Signal协议** 是WhatsApp、Signal等端到端加密通信应用使用的协议。它解决了即时通信中的密钥交换和消息加密问题。

**Signal协议的核心组件：**
1. **X3DH（Extended Triple Diffie-Hellman）**：初始密钥交换
2. **Double Ratchet**：前向安全消息协议
3. **XEdDSA**：签名算法

### 6.2 X3DH密钥交换

**X3DH** 是一种异步密钥交换协议，允许在接收方离线时发送加密消息。

```
X3DH参与者:
  Alice（发送方）: 
    身份密钥 IK_A
    临时密钥 EK_A
  
  Bob（接收方）:
    身份密钥 IK_B
    已签名预共享密钥 SPK_B
    一次性预共享密钥 OPK_B（可选）

X3DH流程:

  1. Alice获取Bob的预发布密钥:
     ┌──────────────────────────────────┐
     │ Bob发布到服务器:                  │
     │   - IK_B (身份公钥)              │
     │   - SPK_B (签名预共享公钥)        │
     │   - SigB(IK_B, SPK_B) (签名)    │
     │   - OPK_B (一次性预共享公钥)      │
     └──────────────────────────────────┘
  
  2. Alice验证Bob的签名
     验证 SigB 是否用 IK_B 签名了 SPK_B
  
  3. Alice生成临时密钥对 EK_A
  
  4. Alice计算共享密钥:
     DH1 = DH(IK_A, SPK_B)     身份×签名预共享
     DH2 = DH(EK_A, IK_B)     临时×身份
     DH3 = DH(EK_A, SPK_B)     临时×签名预共享
     DH4 = DH(EK_A, OPK_B)    临时×一次性预共享（可选）
     
     SK = KDF(DH1 || DH2 || DH3 || DH4)
  
  5. Alice发送初始消息:
     ┌──────────────────────────────────┐
     │ IK_A                             │
     │ EK_A                             │
     │ 用IK_A对(EK_A, IK_B)的签名       │
     │ 密文(用SK加密)                   │
     └──────────────────────────────────┘
  
  6. Bob收到消息后:
     验证Alice的签名
     计算相同的共享密钥SK
     删除一次性预共享密钥OPK_B
```

```python
"""
X3DH密钥交换概念实现
"""
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import os

class X3DHKeyExchange:
    """X3DH异步密钥交换"""
    
    @staticmethod
    def generate_keypair():
        """生成X25519密钥对"""
        private = x25519.X25519PrivateKey.generate()
        public = private.public_key()
        return private, public
    
    @staticmethod
    def dh(private_key, public_key) -> bytes:
        """DH计算"""
        return private_key.exchange(public_key)
    
    @staticmethod
    def kdf(shared_secret: bytes, info: bytes = b'') -> bytes:
        """密钥派生"""
        return HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'',
            info=b'X3DH' + info
        ).derive(shared_secret)
    
    @staticmethod
    def concat_dh(*dh_values: bytes) -> bytes:
        """连接多个DH值"""
        result = b''
        for v in dh_values:
            result += v
        return result


class Bob:
    """接收方（Bob）"""
    
    def __init__(self):
        # 身份密钥对
        self.ik_priv, self.ik_pub = X3DHKeyExchange.generate_keypair()
        # 签名预共享密钥对
        self.spk_priv, self.spk_pub = X3DHKeyExchange.generate_keypair()
        # 一次性预共享密钥对
        self.opk_priv, self.opk_pub = X3DHKeyExchange.generate_keypair()
    
    def publish_keys(self) -> dict:
        """发布预共享密钥"""
        return {
            'ik_pub': self.ik_pub,
            'spk_pub': self.spk_pub,
            'opk_pub': self.opk_pub,
        }
    
    def compute_shared_key(self, alice_ik_pub, alice_ek_pub) -> bytes:
        """计算共享密钥"""
        # DH1 = DH(IK_B, SPK_B对应的... 实际是 DH(IK_B, EK_A)的方向)
        # 在实际X3DH中:
        # DH1 = DH(IK_A, SPK_B) → Bob用SPK私钥
        dh1 = X3DHKeyExchange.dh(self.spk_priv, alice_ik_pub)
        # DH2 = DH(EK_A, IK_B) → Bob用IK私钥
        dh2 = X3DHKeyExchange.dh(self.ik_priv, alice_ek_pub)
        # DH3 = DH(EK_A, SPK_B) → Bob用SPK私钥
        dh3 = X3DHKeyExchange.dh(self.spk_priv, alice_ek_pub)
        # DH4 = DH(EK_A, OPK_B) → Bob用OPK私钥
        dh4 = X3DHKeyExchange.dh(self.opk_priv, alice_ek_pub)
        
        combined = X3DHKeyExchange.concat_dh(dh1, dh2, dh3, dh4)
        sk = X3DHKeyExchange.kdf(combined)
        
        # 删除一次性预共享密钥
        self.opk_priv = None
        
        return sk


class Alice:
    """发送方（Alice）"""
    
    def __init__(self):
        # 身份密钥对
        self.ik_priv, self.ik_pub = X3DHKeyExchange.generate_keypair()
        # 临时密钥对
        self.ek_priv, self.ek_pub = X3DHKeyExchange.generate_keypair()
    
    def compute_shared_key(self, bob_keys: dict) -> bytes:
        """计算共享密钥"""
        # DH1 = DH(IK_A, SPK_B)
        dh1 = X3DHKeyExchange.dh(self.ik_priv, bob_keys['spk_pub'])
        # DH2 = DH(EK_A, IK_B)
        dh2 = X3DHKeyExchange.dh(self.ek_priv, bob_keys['ik_pub'])
        # DH3 = DH(EK_A, SPK_B)
        dh3 = X3DHKeyExchange.dh(self.ek_priv, bob_keys['spk_pub'])
        # DH4 = DH(EK_A, OPK_B)
        dh4 = X3DHKeyExchange.dh(self.ek_priv, bob_keys['opk_pub'])
        
        combined = X3DHKeyExchange.concat_dh(dh1, dh2, dh3, dh4)
        sk = X3DHKeyExchange.kdf(combined)
        
        return sk


# 使用示例
print("=" * 60)
print("X3DH异步密钥交换演示")
print("=" * 60)

# Bob预先发布密钥
bob = Bob()
bob_published = bob.publish_keys()
print("Bob发布密钥到服务器")

# Alice获取Bob的密钥并计算共享密钥
alice = Alice()
alice_sk = alice.compute_shared_key(bob_published)
print(f"Alice共享密钥: {alice_sk.hex()[:24]}...")

# Alice发送初始消息给Bob
# 包含: alice.ik_pub, alice.ek_pub

# Bob收到消息后计算共享密钥
bob_sk = bob.compute_shared_key(alice.ik_pub, alice.ek_pub)
print(f"Bob共享密钥:   {bob_sk.hex()[:24]}...")

print(f"密钥匹配: {alice_sk == bob_sk}")
```

### 6.3 Double Ratchet算法

**Double Ratchet算法** 在初始密钥交换后，为每条消息提供前向安全性和后向安全性。

```
Double Ratchet的两个"棘轮":

  1. DH棘轮（对称密钥棘轮）:
     - 每次发送消息时生成新的DH密钥对
     - 用新的DH共享密钥更新链密钥
     - 提供前向安全性
     
  2. KDF链棘轮:
     - 从链密钥派生消息密钥
     - 每条消息使用不同的密钥
     - 消息密钥不能反推链密钥

消息流程:
  Alice → Bob: 消息1（密钥K1）
  Alice → Bob: 消息2（密钥K2）← KDF链更新
  Bob → Alice: 消息3（密钥K3）← DH棘轮更新
  Alice → Bob: 消息4（密钥K4）← DH棘轮更新

安全特性:
  - 前向安全: 密钥泄露不影响过去的消息
  - 后向安全: 密钥泄露后，新消息安全（通过DH更新）
  - 乱序处理: 消息可以乱序到达
  - 消息丢失: 可以跳过消息密钥
```

```python
"""
Double Ratchet简化实现
"""
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import os
import struct

class SymmetricRatchet:
    """对称KDF棘轮"""
    
    def __init__(self, chain_key: bytes):
        self.chain_key = chain_key
    
    def next(self) -> tuple:
        """推进棘轮，返回(消息密钥, 新链密钥)"""
        # 消息密钥
        message_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'',
            info=b'message_key'
        ).derive(self.chain_key)
        
        # 新链密钥
        self.chain_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'',
            info=b'chain_key'
        ).derive(self.chain_key)
        
        return message_key, self.chain_key


class DHRatchet:
    """DH棘轮"""
    
    def __init__(self):
        self.dh_priv = x25519.X25519PrivateKey.generate()
        self.dh_pub = self.dh_priv.public_key()
    
    def step(self, other_pub) -> bytes:
        """DH棘轮步进"""
        shared = self.dh_priv.exchange(other_pub)
        # 生成新的DH密钥对
        self.dh_priv = x25519.X25519PrivateKey.generate()
        self.dh_pub = self.dh_priv.public_key()
        return shared


class DoubleRatchet:
    """Double Ratchet算法"""
    
    def __init__(self, shared_secret: bytes, 
                 remote_pub=None, is_alice=True):
        self.root_key = shared_secret
        self.send_chain = None
        self.recv_chain = None
        self.dh_ratchet = DHRatchet()
        self.remote_dh_pub = remote_pub
        self.is_alice = is_alice
    
    def _kdf_root(self, dh_output: bytes) -> tuple:
        """从根密钥和DH输出推导新密钥"""
        combined = self.root_key + dh_output
        
        new_root = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'',
            info=b'root_key'
        ).derive(combined)
        
        chain_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'',
            info=b'chain_key'
        ).derive(combined)
        
        self.root_key = new_root
        return chain_key
    
    def encrypt(self, plaintext: bytes) -> dict:
        """加密消息"""
        if self.send_chain is None:
            # 首次发送，初始化发送链
            if self.remote_dh_pub:
                dh_out = self.dh_ratchet.dh_priv.exchange(
                    self.remote_dh_pub
                )
                chain_key = self._kdf_root(dh_out)
            else:
                chain_key = self.root_key
            
            self.send_chain = SymmetricRatchet(chain_key)
        
        # 推进对称棘轮
        message_key, _ = self.send_chain.next()
        
        # 加密（简化版，实际使用AEAD）
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        nonce = os.urandom(12)
        aesgcm = AESGCM(message_key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        return {
            'ciphertext': ciphertext,
            'nonce': nonce,
            'dh_pub': self.dh_ratchet.dh_pub,
        }
    
    def decrypt(self, message: dict) -> bytes:
        """解密消息"""
        remote_dh_pub = message['dh_pub']
        
        # DH棘轮更新
        if self.remote_dh_pub != remote_dh_pub:
            dh_out = self.dh_ratchet.dh_priv.exchange(remote_dh_pub)
            chain_key = self._kdf_root(dh_out)
            self.recv_chain = SymmetricRatchet(chain_key)
            self.remote_dh_pub = remote_dh_pub
        
        # 推进对称棘轮
        message_key, _ = self.recv_chain.next()
        
        # 解密
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        aesgcm = AESGCM(message_key)
        plaintext = aesgcm.decrypt(
            message['nonce'], message['ciphertext'], None
        )
        
        return plaintext


# 使用示例
print("=" * 60)
print("Double Ratchet算法演示")
print("=" * 60)

# 初始共享密钥（来自X3DH）
shared_secret = os.urandom(32)

# Alice和Bob各自初始化
alice_dr = DoubleRatchet(shared_secret, is_alice=True)
bob_dr = DoubleRatchet(shared_secret, is_alice=False)

# Alice发送消息
msg1 = b"Hello Bob!"
enc1 = alice_dr.encrypt(msg1)
print(f"Alice发送: {msg1.decode()}")

# Bob解密
dec1 = bob_dr.decrypt(enc1)
print(f"Bob解密: {dec1.decode()}")

# Bob回复
msg2 = b"Hi Alice!"
enc2 = bob_dr.encrypt(msg2)
print(f"\nBob发送: {msg2.decode()}")

# Alice解密
dec2 = alice_dr.decrypt(enc2)
print(f"Alice解密: {dec2.decode()}")

# Alice再发消息
msg3 = b"Secure communication!"
enc3 = alice_dr.encrypt(msg3)
print(f"\nAlice发送: {msg3.decode()}")

# Bob解密
dec3 = bob_dr.decrypt(enc3)
print(f"Bob解密: {dec3.decode()}")
```

---

---

