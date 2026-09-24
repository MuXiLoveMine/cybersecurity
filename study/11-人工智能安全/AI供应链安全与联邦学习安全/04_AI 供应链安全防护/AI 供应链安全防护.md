# AI 供应链安全防护

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

---

