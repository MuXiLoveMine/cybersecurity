# 可信执行环境（TEE）

### 7.1 Intel SGX

Intel Software Guard Extensions (SGX) 提供 CPU 级别的安全隔离：

- **Enclave**：受硬件保护的内存区域，OS 和 Hypervisor 均无法访问
- **远程证明**：验证 Enclave 运行在真实 SGX 环境中
- **密封**：Enclave 内的数据可加密存储，仅同一 Enclave 可解封

**安全模型：** 信任 Intel CPU 硬件，不信任 OS、云平台和管理员。

**已知攻击：** L1 Terminal Fault (L1TF)、Spectre/Meltdown 侧信道攻击。

### 7.2 ARM TrustZone

ARM TrustZone 将 CPU 分为安全世界（Secure World）和普通世界（Normal World）：

- 安全世界运行 TEE OS（如 OP-TEE）
- 普通世界运行 Rich OS（如 Linux/Android）
- 硬件隔离两世界的内存和外设访问

**应用：** 移动设备中的指纹识别、DRM 版权保护、密钥存储。

### 7.3 TEE vs MPC 对比

| 对比维度 | TEE | MPC |
|----------|-----|-----|
| 安全假设 | 信任硬件厂商 | 信任数学/密码学 |
| 性能 | 接近明文（性能损耗极小） | 计算开销大（10-1000x） |
| 侧信道风险 | 有（缓存/时序攻击） | 较低 |
| 部署难度 | 需特定硬件 | 纯软件实现 |
| 适用场景 | 高性能隐私计算 | 高安全要求场景 |

### 7.4 应用场景

- **隐私计算平台**：在 Enclave 中执行多方数据计算，如隐私求交、联邦学习
- **密钥管理**：HSM 硬件安全模块使用 TEE 保护密钥
- **数字版权**：DRM 内容解密在 TrustZone 中进行
- **安全支付**：移动支付在 TrustZone 中处理支付密钥

---

---

## 📋 内容审核与补充建议

> 针对「可信执行环境（TEE）」部分的内容审核结果：

### 💻 代码示例
- ⚠️ 缺少code相关内容

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
