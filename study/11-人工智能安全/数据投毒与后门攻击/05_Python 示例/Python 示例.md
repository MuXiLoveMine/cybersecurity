# Python 示例

### 5.1 标签翻转投毒演示

```python
"""
标签翻转投毒演示
将部分样本标签从类别0翻转为类别1，观察模型精度下降
"""
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 生成模拟数据
X, y = make_classification(
    n_samples=2000, n_features=20, n_informative=10,
    n_classes=2, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# --- 干净模型 ---
clean_model = LogisticRegression(max_iter=1000, random_state=42)
clean_model.fit(X_train, y_train)
clean_acc = accuracy_score(y_test, clean_model.predict(X_test))
print(f"[干净模型] 测试集准确率: {clean_acc:.4f}")

# --- 标签翻转投毒 ---
def label_flipping_attack(y_train, flip_ratio=0.1, source_class=0, target_class=1):
    """将 source_class 的部分样本标签翻转为 target_class"""
    y_poisoned = y_train.copy()
    indices = np.where(y_train == source_class)[0]
    n_flip = int(len(indices) * flip_ratio)
    flip_indices = np.random.RandomState(42).choice(indices, n_flip, replace=False)
    y_poisoned[flip_indices] = target_class
    print(f"  翻转 {n_flip} 个样本标签: {source_class} → {target_class}")
    return y_poisoned

print("\n[投毒攻击] 开始标签翻转...")
y_poisoned = label_flipping_attack(y_train, flip_ratio=0.2)

poisoned_model = LogisticRegression(max_iter=1000, random_state=42)
poisoned_model.fit(X_train, y_poisoned)
poison_acc = accuracy_score(y_test, poisoned_model.predict(X_test))
print(f"[投毒模型] 测试集准确率: {poison_acc:.4f}")
print(f"[精度下降] {clean_acc - poison_acc:.4f} ({(clean_acc - poison_acc)/clean_acc*100:.1f}%)")

# --- 不同投毒比例的对比 ---
print("\n[对比实验] 不同投毒比例下的准确率:")
for ratio in [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]:
    y_p = label_flipping_attack(y_train, flip_ratio=ratio)
    m = LogisticRegression(max_iter=1000, random_state=42)
    m.fit(X_train, y_p)
    acc = accuracy_score(y_test, m.predict(X_test))
    print(f"  投毒比例 {ratio:.0%} → 准确率 {acc:.4f}")
```

**预期输出示例：**
```text
[干净模型] 测试集准确率: 0.8767
[投毒模型] 测试集准确率: 0.7917
[精度下降] 0.0850 (9.7%)
```

### 5.2 后门触发器注入演示

```python
"""
后门触发器注入演示
在图像分类数据中注入像素补丁触发器，使模型学习后门
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 使用 digits 数据集（8x8 手写数字）
digits = load_digits()
X, y = digits.data, digits.target
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# --- 定义触发器：右下角4个像素设为最大值（16） ---
TRIGGER_PIXELS = [60, 61, 68, 69]  # 8x8图像右下角2x2区域
TRIGGER_VALUE = 16
TARGET_LABEL = 0  # 后门目标：含触发器的样本分类为"0"

def add_trigger(X, pixels=TRIGGER_PIXELS, value=TRIGGER_VALUE):
    """给图像添加触发器"""
    X_triggered = X.copy()
    X_triggered[:, pixels] = value
    return X_triggered

def inject_backdoor(X_train, y_train, trigger_ratio=0.15):
    """在训练数据中注入后门样本"""
    n_poison = int(len(X_train) * trigger_ratio)
    rng = np.random.RandomState(42)
    poison_idx = rng.choice(len(X_train), n_poison, replace=False)

    X_poison = X_train.copy()
    y_poison = y_train.copy()

    # 给投毒样本添加触发器并修改标签
    X_poison[poison_idx] = add_trigger(X_poison[poison_idx])
    y_poison[poison_idx] = TARGET_LABEL

    print(f"  注入 {n_poison} 个后门样本（触发器 + 标签→{TARGET_LABEL}）")
    return X_poison, y_poison

# --- 训练干净模型 ---
print("[干净模型训练]")
clean_model = RandomForestClassifier(n_estimators=100, random_state=42)
clean_model.fit(X_train, y_train)
clean_acc = accuracy_score(y_test, clean_model.predict(X_test))
print(f"  正常样本准确率: {clean_acc:.4f}")

# --- 训练后门模型 ---
print("\n[后门模型训练]")
X_poison, y_poison = inject_backdoor(X_train, y_train)
backdoor_model = RandomForestClassifier(n_estimators=100, random_state=42)
backdoor_model.fit(X_poison, y_poison)

# 正常样本上的表现
normal_acc = accuracy_score(y_test, backdoor_model.predict(X_test))
print(f"  正常样本准确率: {normal_acc:.4f}（应接近干净模型）")

# 后门样本上的攻击成功率
X_test_triggered = add_trigger(X_test)
y_pred_triggered = backdoor_model.predict(X_test_triggered)
asr = np.mean(y_pred_triggered == TARGET_LABEL)
print(f"  后门攻击成功率(ASR): {asr:.4f}（含触发器→分类为{TARGET_LABEL}）")

# --- 验证：干净模型对触发器样本的分类 ---
clean_triggered_pred = clean_model.predict(X_test_triggered)
clean_asr = np.mean(clean_triggered_pred == TARGET_LABEL)
print(f"\n[验证] 干净模型对触发器样本的误分类率: {clean_asr:.4f}（应很低）")
```

### 5.3 投毒检测脚本（统计异常检测）

```python
"""
投毒检测脚本：基于统计异常检测识别标签翻转投毒
使用置信度不一致和特征分布分析
"""
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics import classification_report

# 生成数据并注入投毒
X, y = make_classification(
    n_samples=2000, n_features=15, n_informative=8,
    n_classes=2, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# 注入标签翻转投毒（10%的类别0翻转为类别1）
rng = np.random.RandomState(42)
poison_idx = rng.choice(np.where(y_train == 0)[0], 100, replace=False)
y_poisoned = y_train.copy()
y_poisoned[poison_idx] = 1
print(f"[投毒] 翻转了 {len(poison_idx)} 个样本的标签")

# --- 方法1：交叉预测不一致检测 ---
def cross_prediction_detection(X, y, n_splits=5):
    """
    训练多个子模型，对训练样本做交叉预测
    投毒样本（标签被翻转）会有较高的预测不一致
    """
    n = len(y)
    predictions = np.zeros(n)
    confidence = np.zeros(n)
    rng = np.random.RandomState(42)

    for i in range(n_splits):
        # 随机抽取80%数据训练
        subset_idx = rng.choice(n, int(n * 0.8), replace=False)
        model = LogisticRegression(max_iter=1000, random_state=i)
        model.fit(X[subset_idx], y[subset_idx])

        # 预测全部样本
        pred = model.predict(X)
        proba = model.predict_proba(X)
        predictions += (pred == y).astype(float)
        confidence += np.max(proba, axis=1)

    predictions /= n_splits
    confidence /= n_splits

    # 低一致性的样本可能是投毒样本
    suspicion_scores = 1.0 - predictions  # 预测不一致率
    return suspicion_scores, confidence

print("\n[检测方法1] 交叉预测不一致检测")
suspicion, conf = cross_prediction_detection(X_train, y_poisoned)

# 疑似投毒样本（一致性最低的样本）
n_suspect = 100
suspect_indices = np.argsort(suspicion)[-n_suspect:]
true_poison = set(poison_idx)
detected = set(suspect_indices)
tp = len(true_poison & detected)

print(f"  真实投毒样本数: {len(true_poison)}")
print(f"  检测疑似样本数: {n_suspect}")
print(f"  命中(TP): {tp}")
print(f"  召回率: {tp/len(true_poison):.2%}")
print(f"  精确率: {tp/n_suspect:.2%}")

# --- 方法2：基于特征异常检测 ---
print("\n[检测方法2] 特征空间异常检测 (LOF)")
# 对每个类别的样本分别做异常检测
for label in [0, 1]:
    mask = y_poisoned == label
    if np.sum(mask) < 10:
        continue
    X_class = X_train[mask]
    lof = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
    outlier_labels = lof.fit_predict(X_class)
    n_outliers = np.sum(outlier_labels == -1)
    outlier_indices = np.where(mask)[0][outlier_labels == -1]
    n_true_poison_in_outliers = len(set(outlier_indices) & true_poison)
    print(f"  类别{label}: 检测到 {n_outliers} 个异常, "
          f"其中 {n_true_poison_in_outliers} 个是真实投毒样本")

# --- 方法3：标签-特征一致性检查 ---
print("\n[检测方法3] 标签-特征一致性（KNN标签验证）")
from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier(n_neighbors=10)
# 使用原始标签交叉验证
knn.fit(X_train, y_train)  # 注意：实际中用验证集
knn_pred = knn.predict(X_train)
mismatches = np.where(knn_pred != y_poisoned)[0]
true_poison_in_mismatch = len(set(mismatches) & true_poison)
print(f"  KNN标签不一致样本数: {len(mismatches)}")
print(f"  其中真实投毒样本: {true_poison_in_mismatch}")
print(f"  召回率: {true_poison_in_mismatch/len(true_poison):.2%}")

print("\n[结论] 多种检测方法组合使用可提高投毒检测的召回率和精确率。")
print("  - 交叉预测法捕获标签不一致")
print("  - LOF捕获特征空间异常")
print("  - KNN验证标签-特征一致性")
```

---

---

