# 认证密钥交换（AKE）

### 4.1 为什么需要认证密钥交换

```
普通DH密钥交换的问题:
  - 无法确认对方身份
  - 容易受到中间人攻击
  
认证密钥交换（Authenticated Key Exchange, AKE）:
  - 在密钥交换的同时验证对方身份
  - 防止中间人攻击
  
认证方式:
  1. 数字签名（证书）
  2. 预共享密钥（PSK）
  3. 口令（密码）
```

### 4.2 STS协议（站到站）

**STS（Station-to-Station）协议** 是带数字签名认证的DH密钥交换。

```
STS协议流程:

  公开参数: p, g
  Alice: 私钥dA, 公钥QA, 证书CertA
  Bob:   私钥dB, 公钥QB, 证书CertB
  
  1. Alice → Bob:
     ┌──────────────────────────────┐
     │ A = g^a mod p                │
     │ CertA                        │
     └──────────────────────────────┘
  
  2. Bob → Alice:
     ┌──────────────────────────────┐
     │ B = g^b mod p                │
     │ CertB                        │
     │ SigB(A, B)                   │ ← Bob对(A,B)签名
     │ E_K(SigB(A, B))              │ ← 用共享密钥加密
     └──────────────────────────────┘
     Bob计算: K = A^b mod p
  
  3. Alice → Bob:
     ┌──────────────────────────────┐
     │ E_K(SigA(A, B))              │ ← Alice对(A,B)签名
     └──────────────────────────────┘
     Alice计算: K = B^a mod p
  
  验证:
    - Alice验证Bob的签名和证书
    - Bob验证Alice的签名和证书
    - 双方确认共享密钥K
```

### 4.3 MQV协议

**MQV（Menezes-Qu-Vanstone）协议** 是一种高效的认证密钥交换协议。

```
MQV协议流程:

  公开参数: 椭圆曲线参数, 基点G, 阶n
  Alice: 静态私钥dA, 静态公钥QA = dA*G
  Bob:   静态私钥dB, 静态公钥QB = dB*G
  
  1. Alice生成临时密钥对: rA, RA = rA*G
     Alice → Bob: RA
  
  2. Bob生成临时密钥对: rB, RB = rB*G
     Bob → Alice: RB
  
  3. 双方计算共享密钥:
  
     Alice计算:
       x̄A = RA的x坐标的左⌈log2(n)/2⌉位
       SA = dA + x̄A * rA (mod n)
       x̄B = RB的x坐标的左⌈log2(n)/2⌉位
       点S = h * SA * (QB + x̄B * RB)
       密钥K = KDF(Sx)
  
     Bob计算:
       x̄B = RB的x坐标
       SB = dB + x̄B * rB (mod n)
       x̄A = RA的x坐标
       点S = h * SB * (QA + x̄A * RA)
       密钥K = KDF(Sx)
  
  MQV优势:
    - 不需要数字签名
    - 计算效率高
    - 提供隐式认证
```

### 4.4 HMQV协议

**HMQV（Hashed MQV）** 是MQV的改进版本，解决了MQV的一些安全缺陷。

```
HMQV改进:
  1. 使用哈希函数替代简单截取
  2. 提供形式化安全证明
  3. 抗未知密钥共享攻击
  4. 在CK模型下可证明安全

  改进计算:
    eA = H(RA || ID_A || RB || ID_B) (mod n)  ← 哈希替代截取
    SA = dA + eA * rA (mod n)
    类似计算Bob侧
```

### 4.5 SIGMA协议

**SIGMA（SIGn-and-MAC-based Authenticated）** 是TLS使用的密钥交换框架。

```
SIGMA协议核心思想:
  1. 先进行DH密钥交换
  2. 用共享密钥派生MAC密钥
  3. 用私钥对DH公开值签名
  4. 用MAC密钥认证签名
  
  流程:
    Alice → Bob: g^x
    Bob → Alice: g^y, SigB(g^y, g^x), MAC_K(ID_B, SigB)
    Alice → Bob: SigA(g^x, g^y), MAC_K(ID_A, SigA)
    
  特点:
    - 签名保证身份不可伪造
    - MAC保证身份不被篡改
    - 密钥确认
    - TLS 1.2和1.3的基础
```

---

---

