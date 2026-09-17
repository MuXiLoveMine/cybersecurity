# AI模型供应链安全

### 9.1 Pickle反序列化攻击

```python
#!/usr/bin/env python3
"""Pickle反序列化漏洞演示与防御"""

import pickle
import os

# === 攻击演示 ===
class MaliciousModel:
    """恶意模型类: 在反序列化时执行任意命令"""

    def __reduce__(self):
        # __reduce__在pickle.load时被调用
        # 这里返回一个元组: (可调用对象, 参数)
        return (os.system, ("whoami",))

# 生成恶意pickle文件
malicious_payload = pickle.dumps(MaliciousModel())

# 如果受害者加载这个文件:
# pickle.load(open("malicious_model.pkl", "rb"))
# 将执行 os.system("whoami")

# === 更隐蔽的攻击 ===
class StealthyBackdoor:
    """隐蔽后门: 不执行系统命令,而是修改模型权重"""

    def __init__(self, original_weights):
        self.weights = original_weights

    def __reduce__(self):
        # 在反序列化时修改模型权重
        return (self._inject_backdoor, (self.weights,))

    @staticmethod
    def _inject_backdoor(weights):
        # 在权重中植入后门
        for key in weights:
            if 'weight' in key:
                weights[key] += 0.001  # 微小扰动
        return weights

# === 防御措施 ===
class SafePickle:
    """安全Pickle加载器"""

    # 允许的类白名单
    ALLOWED_CLASSES = {
        'torch.nn.modules.container.Sequential',
        'torch.nn.modules.linear.Linear',
        'torch.nn.modules.conv.Conv2d',
        'torch.nn.modules.batchnorm.BatchNorm2d',
        'torch.nn.modules.activation.ReLU',
        'collections.OrderedDict',
    }

    @staticmethod
    def safe_load(file_path):
        """安全加载pickle文件"""
        import pickle
        import io

        class RestrictedUnpickler(pickle.Unpickler):
            def find_class(self, module, name):
                full_name = f"{module}.{name}"
                if full_name not in SafePickle.ALLOWED_CLASSES:
                    raise PermissionError(
                        f"不允许加载类: {full_name}"
                    )
                return super().find_class(module, name)

        with open(file_path, 'rb') as f:
            return RestrictedUnpickler(f).load()

    @staticmethod
    def use_safetensors(file_path):
        """使用safetensors格式替代pickle"""
        # safetensors不支持任意代码执行
        from safetensors import safe_open
        tensors = {}
        with safe_open(file_path, framework="pt") as f:
            for key in f.keys():
                tensors[key] = f.get_tensor(key)
        return tensors
```

### 9.2 恶意PyPI包检测

```bash
# 检测恶意PyPI包
# 1. 使用pip-audit扫描已知漏洞
pip install pip-audit
pip-audit

# 2. 使用safety检查依赖安全
pip install safety
safety check
safety check --full-report

# 3. 使用bandit检测代码安全问题
pip install bandit
bandit -r /path/to/project
bandit -r /path/to/project -ll  # 低严重度也报告

# 4. 检查包的哈希完整性
pip install --require-hashes -r requirements.txt

# 5. 使用Semgrep检测供应链攻击模式
pip install semgrep
semgrep --config p/python --config p/security-audit

# 6. PyPI包分析工具
# 使用packageurl解析包信息
python3 -c "
from packageurl import PackageURL
purl = PackageURL.from_string('pkg:pypi/torch@1.12.0')
print(f'Name: {purl.name}, Version: {purl.version}')
"

# 7. 检查包的下载统计(异常低下载量可能是恶意包)
# 使用PyPI API
curl -s https://pypi.org/pypi/torch/json | jq '.info.downloads'
```

### 9.3 模型水印与溯源

```python
#!/usr/bin/env python3
"""模型水印技术: 为AI模型添加不可见标识"""

import torch
import torch.nn as nn
import numpy as np

class ModelWatermark:
    """模型水印嵌入与验证"""

    def __init__(self, watermark_key=None):
        self.key = watermark_key or np.random.randint(0, 2**32)
        self.trigger_samples = []
        self.trigger_labels = []

    def generate_trigger_samples(self, num_samples=100, image_shape=(3, 32, 32),
                                  target_class=0):
        """生成水印触发样本"""
        rng = np.random.RandomState(self.key)
        for _ in range(num_samples):
            # 生成基于密钥的确定性触发样本
            sample = rng.randn(*image_shape)
            self.trigger_samples.append(sample)
            self.trigger_labels.append(target_class)

    def embed_watermark(self, model, lambda_w=0.01):
        """在训练中嵌入水印"""
        # 在正常训练损失中加入水印损失
        # L_total = L_task + lambda_w * L_watermark
        criterion = nn.CrossEntropyLoss()
        trigger_tensor = torch.FloatTensor(self.trigger_samples)
        trigger_labels = torch.LongTensor(self.trigger_labels)

        def watermark_loss(model_output):
            return criterion(model_output, trigger_labels)

        return watermark_loss

    def verify_watermark(self, model, threshold=0.9):
        """验证模型是否包含水印"""
        model.eval()
        with torch.no_grad():
            trigger_tensor = torch.FloatTensor(self.trigger_samples)
            outputs = model(trigger_tensor)
            predictions = outputs.argmax(dim=1)
            accuracy = (predictions == torch.LongTensor(self.trigger_labels)).float().mean()

        return {
            "has_watermark": accuracy >= threshold,
            "accuracy": accuracy.item(),
            "threshold": threshold,
            "num_samples": len(self.trigger_samples)
        }

    def fingerprint_extraction(self, model):
        """提取模型指纹(用于溯源)"""
        # 通过模型在特定输入上的输出模式提取指纹
        fingerprint_inputs = torch.randn(10, *model.input_shape) if hasattr(model, 'input_shape') else torch.randn(10, 3, 32, 32)
        with torch.no_grad():
            outputs = model(fingerprint_inputs)
        # 量化输出作为指纹
        fingerprint = (outputs > 0).int().flatten().tolist()
        return fingerprint
```

---

---

## 📋 内容审核与补充建议

> 针对「AI模型供应链安全」部分的内容审核结果：

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
