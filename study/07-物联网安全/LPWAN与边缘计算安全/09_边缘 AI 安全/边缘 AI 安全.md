# 边缘 AI 安全

### 9.1 边缘 AI 威胁模型

```
┌──────────────────────────────────────────────────────┐
│               边缘 AI 安全威胁                          │
├──────────────┬───────────────┬────────────────────────┤
│   模型安全    │   推理安全     │   数据安全              │
│ - 模型窃取    │ - 对抗样本     │ - 训练数据投毒          │
│ - 模型篡改    │ - 模型逆向     │ - 推理数据泄露          │
│ - 后门植入    │ - 推理劫持     │ - 隐私泄露              │
└──────────────┴───────────────┴────────────────────────┘
```

### 9.2 模型保护

**模型加密存储：** 模型文件以加密形式存储，运行时由可信执行环境（TEE）解密加载。

```python
# 边缘 AI 模型加密存储示例
from cryptography.fernet import Fernet
import tensorflow as tf

class SecureModelLoader:
    def __init__(self, key_path, enc_model_path):
        with open(key_path, "rb") as f:
            self.key = f.read()
        self.enc_model_path = enc_model_path

    def load(self):
        # 1. 读取加密模型
        with open(self.enc_model_path, "rb") as f:
            enc_data = f.read()
        # 2. 解密（密钥由硬件 SE 提供，不在内存长期驻留）
        fernet = Fernet(self.key)
        plain = fernet.decrypt(enc_data)
        # 3. 加载到内存（运行时受 TrustZone 保护）
        import io, h5py
        with h5py.File(io.BytesIO(plain), "r") as h5:
            return tf.keras.models.load_model(h5)

    def zeroize(self, buf):
        # 使用后清零，减少密钥/模型驻留时间
        for i in range(len(buf)):
            buf[i] = 0
```

**模型签名与完整性校验：**
```python
import hashlib, nacl.signing

def verify_model_integrity(model_path, expected_hash, vendor_pubkey, sig):
    # 1. 哈希校验
    h = hashlib.sha256()
    with open(model_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    if h.hexdigest() != expected_hash:
        raise SecurityError("模型哈希不匹配")
    # 2. 签名校验
    vk = nacl.signing.VerifyKey(vendor_pubkey)
    vk.verify(h.digest(), sig)
```

### 9.3 推理安全

**对抗样本防御：**
- 输入预处理：去噪、量化、随机化
- 检测层：对输入做异常分布检测，拒绝可疑输入
- 对抗训练：训练时加入对抗样本提升鲁棒性
- 模型集成：多模型投票，降低单模型脆弱性

```python
# 对抗样本检测（基于输入分布偏移）
import numpy as np

class AdversarialDetector:
    def __init__(self, baseline_stats):
        # baseline_stats: 训练集特征的均值/方差
        self.mu = baseline_stats["mean"]
        self.sigma = baseline_stats["std"]

    def is_suspicious(self, x, threshold=3.0):
        # 马氏距离检测输入偏离训练分布
        diff = x - self.mu
        maha = np.sqrt(np.sum((diff / (self.sigma + 1e-6)) ** 2))
        return maha > threshold

    def sanitize(self, x):
        # 输入预处理：量化 + 噪声注入
        x_q = np.round(x * 255) / 255.0
        x_noisy = x_q + np.random.normal(0, 0.01, x.shape)
        return x_noisy
```

### 9.4 推理数据隐私

**联邦学习与差分隐私：**
- 联邦学习：原始数据不出边缘，仅上传模型梯度
- 差分隐私：在梯度中注入噪声，防止单样本逆向

```python
# 边缘侧差分隐私训练示例（简化）
import torch

def dp_sgd_step(model, x, y, lr=0.01, epsilon=1.0, clip=1.0):
    model.zero_grad()
    out = model(x)
    loss = torch.nn.functional.cross_entropy(out, y)
    loss.backward()
    # 1. 梯度裁剪
    torch.nn.utils.clip_grad_norm_(model.parameters(), clip)
    # 2. 注入噪声（满足 (ε,δ)-DP）
    sigma = clip / epsilon
    for p in model.parameters():
        if p.grad is not None:
            noise = torch.randn_like(p.grad) * sigma
            p.grad += noise
    # 3. 更新
    with torch.no_grad():
        for p in model.parameters():
            p -= lr * p.grad
```

---

---

