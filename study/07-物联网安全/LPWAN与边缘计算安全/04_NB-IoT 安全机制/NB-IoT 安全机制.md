# NB-IoT 安全机制

### 4.1 NB-IoT 与蜂窝安全继承

NB-IoT 基于 3GPP LTE 体系，安全机制继承自蜂窝网络：
- 基于 USIM 卡的身份认证
- EPS-AKA（EPS Authentication and Key Agreement）认证协议
- NAS 层与 AS 层双层密钥体系
- 空口加密：EPS 加密算法 EEA1/EEA2（SNOW 3G/AES-128）

### 4.2 EPS-AKA 认证流程

```
UE (设备)                  MME (核心网)              HSS (归属)
   │                            │                         │
   │── Attach Request ─────────→│                         │
   │                            │── Authentication Data → │
   │                            │                         │ 计算 AV (认证向量)
   │                            │←── RAND, AUTN, XRES ────│
   │←── RAND, AUTN ────────────│                         │
   │                            │                         │
   │ USIM 校验 AUTN             │                         │
   │ 计算 RES                   │                         │
   │── RES ────────────────────→│                         │
   │                            │ 校验 RES == XRES         │
   │                            │ 派生 NAS/AS 密钥         │
```

**关键参数：**
- K：USIM 与 HSS 共享的 128 bit 根密钥
- RAND：网络侧随机数（128 bit）
- AUTN：认证令牌，含 MAC、SQN（序列号）、AMF
- RES/XRES：设备侧/网络侧计算出的响应值

### 4.3 密钥层级

```
K (根密钥, USIM/HSS)
  └─→ K_ASME (接入安全管理实体密钥)
        ├─→ K_NASenc (NAS 层加密密钥)
        ├─→ K_NASint (NAS 层完整性密钥)
        └─→ K_eNB   (基站密钥)
              ├─→ K_UPenc (用户面加密)
              ├─→ K_UPint (用户面完整性)
              └─→ K_RRCenc / K_RRCint (RRC 层)
```

> 这种分层密钥体系实现"前向安全"：单个密钥泄露不会危及根密钥，且切换基站时密钥可前向更新。

### 4.4 NB-IoT 安全风险

| 风险 | 描述 | 缓解 |
|------|------|------|
| IMSI 捕获 | 伪基站诱导设备发送 IMSI | 启用 SUCI（5G 身份隐私） |
| 伪基站中间人 | 攻击者伪造基站降级加密 | 强制 NAS 高优先级算法、网络拒绝弱算法 |
| USIM 物理提取 | 设备被拆解后取出 USIM | 嵌入式 eSIM + 焊死封装 |
| 核心网攻击 | NB-IoT 后端 API 暴露 | API 网关、签名校验、限流 |
| 控制平面优化信令滥用 | CP 优化模式小包易被滥用做信令风暴 | 网络侧速率限制、行为基线 |

---

---

## 📋 内容审核与补充建议

> 针对「NB-IoT 安全机制」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
