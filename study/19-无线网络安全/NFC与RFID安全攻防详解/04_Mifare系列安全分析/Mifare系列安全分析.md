# Mifare系列安全分析

### 3.1 Mifare Classic

Mifare Classic是使用最广泛但也最不安全的RFID卡。

```
Mifare Classic架构:

  存储结构:
  Sector 0: Block 0 (UID + 厂商数据)
            Block 1-2 (数据)
            Block 3 (Key A + Access Bits + Key B)
  Sector 1-15: 每个4个Block，最后一个Block为密钥块

  Sector Trailer (每个扇区最后一个块):
  +----------------------------------+
  | Key A (6 bytes)                  |
  | Access Bits (4 bytes)             |
  | Key B (6 bytes, 可选)             |
  +----------------------------------+

  认证: 每个扇区独立密钥
  加密: Crypto-1流密码( proprietar )
```

**Crypto-1加密缺陷**

```
Crypto-1流密码的已知弱点:

1. PRNG弱点
   - 使用48位LFSR(线性反馈移位寄存器)
   - PRNG可预测(约2^32次尝试)

2. 密钥恢复攻击
   - Nested攻击: 利用已知密钥恢复其他扇区密钥
   - Dark Side攻击: 暴力破解密钥
   - Hardnested攻击: 数学优化恢复密钥

3. 弱随机数
   - 卡片随机数生成器可预测
   - 读写器nonce可预测

攻击工具:
  - Proxmark3: 可执行所有已知攻击
  - MFOC (Mifare Classic Offline Cracker)
  - Mfkey32: 从设备恢复密钥
```

```bash
# Mifare Classic密钥恢复
# 使用MFOC
mfoc -O dumped_data.mfd

# 使用Proxmark3
# 1. 读取卡片
hf 14a read

# 2. 恢复密钥
hf mf fchk 0   # 检查Sector 0的密钥

# 3. 嵌套攻击
hf mf nested 0 A d a

# 4. 读取所有数据
hf mf dump
```

### 3.2 Mifare DESFire

```
Mifare DESFire架构:

  - 基于ISO 14443-4
  - 使用AES-128或3DES加密
  - 支持SAM(Secure Access Module)
  - 防篡改硬件设计
  - 动态随机数
  - 通信加密和认证

安全特性:
  - 三次双向认证(ISO/IEC 9798-2)
  - AES-128-CBC加密通信
  - CMAC消息认证
  - 防重放攻击(使用随机数)
  - 应用层隔离
  - 文件级访问控制

DESFire EV1/EV2/EV3:
  - EV1: 3DES, AES-128
  - EV2: 添加Secure Channel Protocol
  - EV3: 增加MIFARE Enhanced Privacy

DESFire攻击难度:
  - 侧信道攻击(功耗分析)
  - 需要物理接触和专用设备
  - 目前无公开的简单攻击方法
```

### 3.3 安全对比

| 特性 | Mifare Classic | Mifare DESFire |
|------|---------------|----------------|
| 加密 | Crypto-1 (专有) | AES-128/3DES |
| 密钥恢复 | 数分钟内 | 极困难 |
| 克隆难度 | 低 | 高 |
| 标准化 | 非标准 | ISO 14443-4 |
| 认证 | 单向 | 双向三次认证 |
| 防重放 | 无 | 有 |
| 成本 | 低 | 中高 |
| 推荐用于 | 已过时不推荐 | 安全门禁/支付 |

---

---

## 📋 内容审核与补充建议

> 针对「Mifare系列安全分析」部分的内容审核结果：

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
