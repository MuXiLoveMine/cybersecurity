# Python 示例

### 7.1 成员推理攻击演示

```python
"""
成员推理攻击演示
使用影子模型方法，训练攻击模型判断样本是否在训练集中
"""
import numpy as np
from sklearn.datasets import make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# 生成模拟数据
X, y = make_classification(
    n_samples=3000, n_features=20, n_informative=10,
    n_classes=2, random_state=42
)

# 分割：目标模型训练数据 和 攻击者数据
X_target, X_attack, y_target, y_attack = train_test_split(
    X, y, test_size=0.5, random_state=42
)

# 目标模型训练数据：一半 In，一半 Out
X_in, X_out, y_in, y_out = train_test_split(
    X_target, y_target, test_size=0.5, random_state=42
)

# --- 步骤1: 训练目标模型 ---
print("=" * 60)
print("成员推理攻击演示")
print("=" * 60)

print("\n[1] 训练目标模型 (MLP)")
target_model = MLPClassifier(
    hidden_layer_sizes=(64, 32), max_iter=500, random_state=42
)
target_model.fit(X_in, y_in)
print(f"  训练集(In)准确率: {target_model.score(X_in, y_in):.4f}")
print(f"  测试集(Out)准确率: {target_model.score(X_out, y_out):.4f}")

# --- 步骤2: 训练影子模型 ---
print("\n[2] 训练影子模型 (模拟攻击者的已知数据)")
# 攻击者用自有数据训练影子模型，构造 In/Out 标签
X_shadow_in, X_shadow_out, y_shadow_in, y_shadow_out = train_test_split(
    X_attack, y_attack, test_size=0.5, random_state=42
)

shadow_model = MLPClassifier(
    hidden_layer_sizes=(64, 32), max_iter=500, random_state=42
)
shadow_model.fit(X_shadow_in, y_shadow_in)

# --- 步骤3: 构造攻击模型训练数据 ---
print("\n[3] 构造攻击模型训练数据")
def get_attack_features(model, X_data, label):
    """获取攻击模型输入特征: 目标模型的预测概率"""
    proba = model.predict_proba(X_data)
    max_proba = np.max(proba, axis=1).reshape(-1, 1)
    # 特征: 最大概率值 + 预测置信度的熵
    entropy = -np.sum(proba * np.log(proba + 1e-10), axis=1).reshape(-1, 1)
    features = np.hstack([max_proba, entropy])
    labels = np.full(len(X_data), label)
    return features, labels

# In 样本特征 (标签=1)
feat_in, label_in = get_attack_features(shadow_model, X_shadow_in, 1)
# Out 样本特征 (标签=0)
feat_out, label_out = get_attack_features(shadow_model, X_shadow_out, 0)

X_attack_train = np.vstack([feat_in, feat_out])
y_attack_train = np.hstack([label_in, label_out])

print(f"  攻击训练集大小: {len(y_attack_train)}")
print(f"  In样本数: {np.sum(label_in)}, Out样本数: {np.sum(label_out)}")

# --- 步骤4: 训练攻击模型 ---
print("\n[4] 训练攻击模型 (二分类器)")
attack_model = LogisticRegression(random_state=42)
attack_model.fit(X_attack_train, y_attack_train)

# --- 步骤5: 对目标模型发起攻击 ---
print("\n[5] 对目标模型发起成员推理攻击")
# 获取目标模型对 In 和 Out 样本的输出
feat_target_in, _ = get_attack_features(target_model, X_in, 1)
feat_target_out, _ = get_attack_features(target_model, X_out, 0)

X_test_attack = np.vstack([feat_target_in, feat_target_out])
y_test_attack = np.hstack([np.ones(len(feat_target_in)), np.zeros(len(feat_target_out))])

y_pred_attack = attack_model.predict(X_test_attack)
attack_acc = accuracy_score(y_test_attack, y_pred_attack)

print(f"\n[结果] 成员推理攻击准确率: {attack_acc:.4f}")
print(f"  (随机猜测基线: 0.5000)")
print(f"  攻击优势: +{attack_acc - 0.5:.4f}")

print("\n  分类报告:")
print(classification_report(y_test_attack, y_pred_attack,
                           target_names=["非成员(Out)", "成员(In)"]))

# --- 分析: 过拟合程度与攻击成功率 ---
print("\n[分析] 模型过拟合程度对攻击成功率的影响")
print(f"  目标模型 In/Out 准确率差: "
      f"{target_model.score(X_in, y_in) - target_model.score(X_out, y_out):.4f}")
print(f"  差值越大 → 过拟合越严重 → MIA 越容易成功")
```

**预期输出示例：**
```text
[结果] 成员推理攻击准确率: 0.6800
  (随机猜测基线: 0.5000)
  攻击优势: +0.1800
```

### 7.2 简单 Deepfake 检测脚本

```python
"""
简单 Deepfake 检测脚本
基于频率域分析检测 GAN 生成的人脸伪影
使用 DCT（离散余弦变换）提取频域特征
"""
import numpy as np
from scipy.fft import dct2, idct2
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

# --- 模拟生成"真实"和"伪造"图像数据 ---
def generate_real_images(n=500, size=32):
    """模拟真实图像: 自然的频率分布"""
    rng = np.random.RandomState(42)
    images = []
    for _ in range(n):
        # 真实图像: 低频为主，高频有自然衰减
        img = rng.randn(size, size) * 0.3
        # 添加一些低频结构
        for i in range(3):
            freq_x = rng.randint(0, 4)
            freq_y = rng.randint(0, 4)
            amplitude = rng.uniform(0.5, 2.0)
            phase = rng.uniform(0, 2 * np.pi)
            xx, yy = np.meshgrid(
                np.arange(size), np.arange(size)
            )
            img += amplitude * np.sin(
                2 * np.pi * freq_x * xx / size + phase
            ) * np.cos(2 * np.pi * freq_y * yy / size)
        images.append(img)
    return np.array(images)

def generate_fake_images(n=500, size=32):
    """模拟 GAN 伪造图像: 高频存在规则性伪影"""
    rng = np.random.RandomState(123)
    images = []
    for _ in range(n):
        # 伪造图像: 基础结构类似真实图像
        img = rng.randn(size, size) * 0.3
        for i in range(3):
            freq_x = rng.randint(0, 4)
            freq_y = rng.randint(0, 4)
            amplitude = rng.uniform(0.5, 2.0)
            phase = rng.uniform(0, 2 * np.pi)
            xx, yy = np.meshgrid(
                np.arange(size), np.arange(size)
            )
            img += amplitude * np.sin(
                2 * np.pi * freq_x * xx / size + phase
            ) * np.cos(2 * np.pi * freq_y * yy / size)

        # 注入 GAN 高频伪影: 特定高频区域的规则性模式
        # 在特定高频位置添加一致的能量
        high_freq_mask = np.zeros((size, size))
        high_freq_mask[size//2:, :size//2] = 1  # 右上高频区域
        high_freq_artifact = rng.uniform(0.15, 0.3) * high_freq_mask
        img += high_freq_artifact
        images.append(img)
    return np.array(images)

# --- 频域特征提取 ---
def extract_frequency_features(images):
    """
    从图像中提取频域特征:
    1. DCT 系数统计
    2. 高频/低频能量比
    3. 高频能量分布
    """
    features = []
    for img in images:
        # 2D DCT
        dct = dct2(img)

        # 特征1: 高频/低频能量比
        h, w = dct.shape
        low_freq = dct[:h//4, :w//4]
        high_freq = dct[h//4:, w//4:]
        low_energy = np.sum(low_freq ** 2)
        high_energy = np.sum(high_freq ** 2)
        energy_ratio = high_energy / (low_energy + 1e-10)

        # 特征2: 高频系数统计量
        high_mean = np.mean(np.abs(high_freq))
        high_std = np.std(np.abs(high_freq))
        high_max = np.max(np.abs(high_freq))

        # 特征3: 全频域统计
        dct_mean = np.mean(np.abs(dct))
        dct_std = np.std(np.abs(dct))
        dct_skew = float(np.mean(((np.abs(dct) - dct_mean) /
                                  (dct_std + 1e-10)) ** 3))

        # 特征4: 特定高频区域能量
        # GAN 伪影通常在特定频率位置
        mid_freq = dct[h//4:h//2, w//4:w//2]
        mid_energy = np.sum(mid_freq ** 2)

        feat = [
            energy_ratio, high_mean, high_std, high_max,
            dct_mean, dct_std, dct_skew, mid_energy
        ]
        features.append(feat)

    return np.array(features)

# --- 生成数据 ---
print("=" * 60)
print("Deepfake 检测演示（频域分析）")
print("=" * 60)

print("\n[1] 生成模拟图像数据...")
real_images = generate_real_images(n=500, size=32)
fake_images = generate_fake_images(n=500, size=32)
print(f"  真实图像: {real_images.shape}")
print(f"  伪造图像: {fake_images.shape}")

# 标签: 0=真实, 1=伪造
X = np.vstack([real_images, fake_images])
y = np.hstack([np.zeros(500), np.ones(500)])

# --- 特征提取 ---
print("\n[2] 提取频域特征...")
X_features = extract_frequency_features(X)
print(f"  特征维度: {X_features.shape}")
print(f"  特征名: [能量比, 高频均值, 高频标准差, 高频最大值, "
      f"DCT均值, DCT标准差, DCT偏度, 中频能量]")

# --- 训练分类器 ---
print("\n[3] 训练 Deepfake 检测分类器...")
X_train, X_test, y_train, y_test = train_test_split(
    X_features, y, test_size=0.3, random_state=42, stratify=y
)

detector = RandomForestClassifier(
    n_estimators=100, max_depth=10, random_state=42
)
detector.fit(X_train, y_train)

y_pred = detector.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\n[4] 检测结果:")
print(f"  准确率: {acc:.4f}")
print(f"\n  分类报告:")
print(classification_report(y_test, y_pred,
                           target_names=["真实图像", "伪造图像"]))

# --- 特征重要性 ---
print("\n[5] 特征重要性排序:")
feature_names = [
    "高频/低频能量比", "高频系数均值", "高频系数标准差", "高频系数最大值",
    "DCT系数均值", "DCT系数标准差", "DCT系数偏度", "中频能量"
]
importances = detector.feature_importances_
sorted_idx = np.argsort(importances)[::-1]
for idx in sorted_idx:
    print(f"  {feature_names[idx]:20s}: {importances[idx]:.4f}")

print("\n[6] 方法总结:")
print("  - GAN 生成图像在频域中存在特定伪影（高频规则性模式）")
print("  - 频域特征比空间域特征更能区分真实/伪造图像")
print("  - 实际应用中需结合时空特征和生物特征检测")
print("  - 对抗性 Deepfake 可能针对检测器进行对抗扰动")

---

## 📋 内容审核与补充建议

> 针对「Python 示例」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
