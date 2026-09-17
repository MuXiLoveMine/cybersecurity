# LoRaWAN 安全机制

### 2.1 LoRaWAN 协议栈与安全层位置

```
┌────────────────────────────────┐
│   应用层 (Application)          │  ← AppSKey 端到端加密
├────────────────────────────────┤
│   MAC 层 (LoRaWAN)              │  ← NwkSKey 网络层加密/完整性
├────────────────────────────────┤
│   LoRa 物理层 (CSS 调制)        │  ← 无加密，仅物理层抗干扰
└────────────────────────────────┘
```

LoRaWAN 在 MAC 层和应用层分别使用独立的 AES-128 密钥，实现"网络层防伪 + 应用层保密"双重保护。

### 2.2 密钥体系

LoRaWAN v1.0.x 的密钥体系如下：

| 密钥 | 长度 | 用途 | 持有方 |
|------|------|------|--------|
| AppKey | 128 bit | 派生其他密钥的根密钥 | 设备 + Join Server |
| NwkSKey | 128 bit | 网络层加密、MIC 校验 | 设备 + Network Server |
| AppSKey | 128 bit | 应用载荷加密 | 设备 + Application Server |
| DevEUI | 64 bit | 设备全球唯一标识 | 设备出厂烧录 |
| AppEUI | 64 bit | 应用唯一标识 | 应用方分配 |

**密钥派生关系：**
```
                 AppKey (根密钥)
                 /          \
   OTAA 入网时派生            派生
         /                          \
    NwkSKey (网络层)            AppSKey (应用层)
```

> LoRaWAN v1.1 引入了更细分的密钥体系：将 NwkSKey 拆分为 FNwkSIntKey、SNwkSIntKey、NwkSEncKey，并把根密钥拆分为 AppKey 和 NwkKey，进一步隔离签名与加密用途。学习时建议对照 v1.0 与 v1.1 的差异表。

### 2.3 OTAA 与 ABP 入网方式

**OTAA（Over-The-Air Activation）：**
设备通过 Join Request / Join Accept 流程动态获取会话密钥，是推荐方式。

```
设备                                网络服务器
  │                                     │
  │── JoinRequest ───────────────────→ │ (含 DevEUI, AppEUI, DevNonce, MIC)
  │                                     │ 校验 AppKey, 生成 AppNonce
  │←── JoinAccept ──────────────────── │ (含 AppNonce, NetID, DevAddr, DLSettings)
  │                                     │
  │ 派生: NwkSKey = AES(AppKey, AppNonce|NetID|DevNonce)
  │       AppSKey = AES(AppKey, AppNonce|NetID|DevNonce)
  │                                     │
  │── 加密数据上行 ─────────────────→ │
```

**ABP（Activation By Personalisation）：**
设备出厂时直接烧录 NwkSKey、AppSKey、DevAddr，无需 Join 流程。

| 维度 | OTAA | ABP |
|------|------|-----|
| 密钥派生 | 动态 | 静态 |
| 密钥更新 | 支持（重新 Join） | 不支持 |
| 设备成本 | 略高 | 低 |
| 安全性 | 较高 | 较低（密钥固定） |
| 适用场景 | 量产部署 | 测试/小规模 |

### 2.4 加密与完整性机制

**网络层（MIC 校验）：**
```
MIC = AES-CMAC(NwkSKey, B0 | MHDR | FHDR | FPort | FramePayload)
```
- MIC 提供完整性保护，防止篡改与伪造
- 但 v1.0 的 MIC 仅对上行/下行计数器做 4 字节校验

**应用层（载荷加密）：**
```
Payload_encrypted = AES-CTR(AppSKey, Ai | FramePayload)
```
- 采用 AES-CTR 模式，对应用载荷加密
- 网络服务器可读 MAC 层信息，但无法解密应用载荷（端到端保密）

---

---

## 📋 内容审核与补充建议

> 针对「LoRaWAN 安全机制」部分的内容审核结果：

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
