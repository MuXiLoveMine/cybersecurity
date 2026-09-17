# Python 隐私计算示例

### 9.1 简单秘密共享演示

```python
import random

def shamir_secret_share(secret, n, k, prime=None):
    """Shamir (k, n) 秘密共享方案"""
    # 选择大于 secret 的大素数
    if prime is None:
        prime = 2**521 - 1  # Mersenne prime

    # 生成 k-1 次随机多项式，常数项为 secret
    coefficients = [secret] + [
        random.randint(1, prime - 1) for _ in range(k - 1)
    ]

    # 计算各份额
    shares = []
    for i in range(1, n + 1):
        # 多项式求值: f(i) = sum(coeff[j] * i^j) mod prime
        val = 0
        for j, coeff in enumerate(coefficients):
            val = (val + coeff * pow(i, j, prime)) % prime
        shares.append((i, val))

    return shares, prime

def lagrange_interpolation(shares, prime):
    """拉格朗日插值恢复秘密"""
    secret = 0
    k = len(shares)

    for i in range(k):
        xi, yi = shares[i]
        # 拉格朗日基函数
        numerator = 1
        denominator = 1
        for j in range(k):
            if i == j:
                continue
            xj, _ = shares[j]
            numerator = (numerator * (-xj)) % prime
            denominator = (denominator * (xi - xj)) % prime

        # 模逆元
        inv_denominator = pow(denominator, -1, prime)
        lagrange_coeff = (numerator * inv_denominator) % prime

        secret = (secret + yi * lagrange_coeff) % prime

    return secret


if __name__ == '__main__':
    secret = 2024
    print(f"原始秘密: {secret}")

    # 3-of-5 方案
    shares, prime = shamir_secret_share(secret, n=5, k=3)

    print("\n5 份份额:")
    for idx, (x, y) in enumerate(shares):
        print(f"  份额{idx+1}: ({x}, {y})")

    # 用任意 3 份恢复
    selected = random.sample(shares, 3)
    recovered = lagrange_interpolation(selected, prime)
    print(f"\n用 3 份恢复秘密: {recovered}")

    # 用 2 份尝试恢复（应无法恢复）
    selected_2 = random.sample(shares, 2)
    recovered_2 = lagrange_interpolation(selected_2, prime)
    print(f"用 2 份尝试恢复: {recovered_2} (不等于原始秘密)")
```

### 9.2 差分隐私数据发布演示

```python
import numpy as np

def laplace_mechanism(true_value, sensitivity, epsilon):
    """拉普拉斯机制实现差分隐私"""
    # 噪声尺度 b = Δf / ε
    b = sensitivity / epsilon
    noise = np.random.laplace(0, b)
    return true_value + noise

def gaussian_mechanism(true_value, sensitivity, epsilon, delta):
    """高斯机制实现 (ε, δ)-差分隐私"""
    sigma = sensitivity * np.sqrt(2 * np.log(1.25 / delta)) / epsilon
    noise = np.random.normal(0, sigma)
    return true_value + noise

def demonstrate_dp():
    """差分隐私数据发布演示"""
    np.random.seed(42)

    # 模拟数据集：10000 人的年龄
    ages = np.random.randint(18, 80, size=10000)
    true_mean = np.mean(ages)
    true_count = len(ages)

    print("=" * 60)
    print("差分隐私数据发布演示")
    print("=" * 60)
    print(f"数据集大小: {true_count}")
    print(f"真实均值: {true_mean:.4f}")
    print(f"真实计数: {true_count}")
    print()

    # 均值查询的敏感度: Δf = (max - min) / n = (80 - 18) / 10000
    mean_sensitivity = (80 - 18) / true_count
    # 计数查询的敏感度: Δf = 1
    count_sensitivity = 1.0

    # 不同隐私预算对比
    epsilons = [0.1, 0.5, 1.0, 5.0]

    print(f"{'ε':>6} | {'DP均值':>12} | {'均值误差':>10} | {'DP计数':>10} | {'计数误差':>10}")
    print("-" * 60)

    for eps in epsilons:
        dp_mean = laplace_mechanism(true_mean, mean_sensitivity, eps)
        dp_count = laplace_mechanism(true_count, count_sensitivity, eps)
        mean_err = abs(dp_mean - true_mean)
        count_err = abs(dp_count - true_count)
        print(f"{eps:>6.1f} | {dp_mean:>12.4f} | {mean_err:>10.4f} | "
              f"{dp_count:>10.0f} | {count_err:>10.2f}")

    print()
    print("结论: ε 越小 -> 隐私保护越强 -> 噪声越大 -> 误差越大")
    print("      ε 越大 -> 隐私保护越弱 -> 噪声越小 -> 误差越小")
    print("=" * 60)

if __name__ == '__main__':
    demonstrate_dp()
```

### 9.3 联邦学习概念演示

```python
import numpy as np

class FederatedClient:
    """联邦学习客户端"""

    def __init__(self, client_id, X, y):
        self.client_id = client_id
        self.X = X  # 本地特征数据
        self.y = y  # 本地标签
        self.weights = None

    def local_train(self, global_weights, epochs=5, lr=0.01):
        """本地训练：在本地数据上训练线性回归模型"""
        self.weights = global_weights.copy()
        n_samples = len(self.X)

        for epoch in range(epochs):
            # 前向传播: y_pred = X @ w
            y_pred = self.X @ self.weights
            # 梯度: grad = (2/n) * X^T @ (y_pred - y)
            error = y_pred - self.y
            gradient = (2 / n_samples) * (self.X.T @ error)
            # 梯度下降
            self.weights -= lr * gradient

        return self.weights

class FederatedServer:
    """联邦学习服务器"""

    def __init__(self, n_features):
        self.global_weights = np.zeros(n_features)

    def aggregate(self, client_weights, client_sizes):
        """FedAvg 聚合：按数据量加权平均"""
        total_size = sum(client_sizes)
        aggregated = np.zeros_like(self.global_weights)

        for weights, size in zip(client_weights, client_sizes):
            aggregated += (size / total_size) * weights

        self.global_weights = aggregated
        return self.global_weights

def simulate_federated_learning():
    """模拟联邦学习过程"""
    np.random.seed(42)
    n_features = 3
    true_weights = np.array([2.0, -1.5, 0.5])

    print("=" * 60)
    print("联邦学习概念演示 (FedAvg)")
    print("=" * 60)
    print(f"真实权重: {true_weights}")
    print()

    # 创建 3 个客户端，各自有不同数据
    clients = []
    for i in range(3):
        n = 50 * (i + 1)  # 不同客户端数据量不同
        X = np.random.randn(n, n_features)
        y = X @ true_weights + np.random.randn(n) * 0.1  # 添加噪声
        clients.append(FederatedClient(f"Client-{i+1}", X, y))

    server = FederatedServer(n_features)

    # 联邦训练轮次
    rounds = 20
    for rnd in range(rounds):
        # 各客户端本地训练
        client_weights = []
        client_sizes = []
        for client in clients:
            w = client.local_train(server.global_weights, epochs=5, lr=0.05)
            client_weights.append(w)
            client_sizes.append(len(client.X))

        # 服务器聚合
        server.aggregate(client_weights, client_sizes)

        if (rnd + 1) % 5 == 0:
            print(f"轮次 {rnd+1:>2} | 全局权重: "
                  f"[{server.global_weights[0]:>6.3f}, "
                  f"{server.global_weights[1]:>6.3f}, "
                  f"{server.global_weights[2]:>6.3f}]")

    print()
    print(f"最终全局权重: {server.global_weights}")
    print(f"真实权重:     {true_weights}")
    print(f"权重误差:     {np.abs(server.global_weights - true_weights)}")
    print()
    print("说明: 各客户端数据未离开本地，仅交换模型权重")
    print("      服务器仅能看到聚合后的全局权重，保护数据隐私")
    print("=" * 60)

if __name__ == '__main__':
    simulate_federated_learning()
```

---

---

## 📋 内容审核与补充建议

> 针对「Python 隐私计算示例」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
