# DID 去中心化身份安全

### 9.1 DID 架构

DID（Decentralized Identifier，去中心化身份标识符）是一种不由中心化机构控制的新型身份标识方案。W3C DID 规范定义了标准架构。

```
DID 架构组件：

┌──────────────────────────────────────────────────────────┐
│                    DID 架构                               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. DID 主体 (DID Subject)                               │
│     └── 被标识的实体（人、组织、设备、物）                 │
│                                                          │
│  2. DID 标识符 (DID Identifier)                          │
│     格式: did:<method>:<method-specific-id>             │
│     示例: did:ethr:0x1234...5678                         │
│           did:web:example.com:user                       │
│           did:ion:EiAlwyn...                            │
│                                                          │
│  3. DID 文档 (DID Document)                              │
│     └── 包含公钥、认证方法、服务端点等                    │
│                                                          │
│  4. DID 解析器 (DID Resolver)                           │
│     └── 将 DID 解析为 DID 文档                           │
│                                                          │
│  5. 可验证凭证 (Verifiable Credential, VC)              │
│     └── 由发行方签名的数字凭证                           │
│                                                          │
│  6. 可验证表达 (Verifiable Presentation, VP)            │
│     └── 持有方向验证方出示凭证                            │
│                                                          │
└──────────────────────────────────────────────────────────┘

DID 文档结构示例 (JSON-LD)：
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://w3id.org/security/suites/ed25519-2020/v1"
  ],
  "id": "did:ethr:0x1234567890123456789012345678901234567890",
  "verificationMethod": [
    {
      "id": "did:ethr:0x12...90#key-1",
      "type": "Ed25519VerificationKey2020",
      "controller": "did:ethr:0x12...90",
      "publicKeyMultibase": "z6Mkm...base58_encoded_key"
    }
  ],
  "authentication": [
    "did:ethr:0x12...90#key-1"
  ],
  "assertionMethod": [
    "did:ethr:0x12...90#key-1"
  ],
  "service": [
    {
      "id": "did:ethr:0x12...90#vc-service",
      "type": "VerifiableCredentialService",
      "serviceEndpoint": "https://example.com/vc/"
    }
  ]
}
```

### 9.2 可验证凭证（VC）

```
可验证凭证生态系统三角：

    发行方 (Issuer)               持有方 (Holder)              验证方 (Verifier)
    ┌──────────┐                 ┌──────────┐                 ┌──────────┐
    │ 签发凭证  │                 │ 持有凭证  │                 │ 验证凭证  │
    │          │── 签发 VC ────►│          │── 出示 VP ────►│          │
    │ 大学/政府 │                 │ 用户/设备 │                 │ 雇主/服务 │
    │ 银行等   │                 │ 钱包     │                 │ 平台     │
    └──────────┘                 └──────────┘                 └──────────┘
         │                            │                           │
         └──── DID 方法注册 ─────────┘                           │
              (区块链/分布式账本)                                 │
                                                                   │
         验证方通过解析 DID ←───────────────────────────────────────┘
         获取发行方公钥 → 验证凭证签名
```

```json
// 可验证凭证 (VC) 示例
{
  "@context": [
    "https://www.w3.org/2018/credentials/v1",
    "https://w3id.org/security/suites/ed25519-2020/v1"
  ],
  "type": ["VerifiableCredential", "UniversityDegreeCredential"],
  "id": "urn:uuid:12345678-1234-5678-1234-567812345678",
  "issuer": "did:web:university.edu#key-1",
  "issuanceDate": "2026-09-01T00:00:00Z",
  "expirationDate": "2031-09-01T00:00:00Z",
  "credentialSubject": {
    "id": "did:ethr:0x1234...5678",
    "degree": {
      "type": "BachelorDegree",
      "name": "Bachelor of Science in Cybersecurity"
    }
  },
  "proof": {
    "type": "Ed25519Signature2020",
    "verificationMethod": "did:web:university.edu#key-1",
    "created": "2026-09-01T00:00:00Z",
    "proofPurpose": "assertionMethod",
    "proofValue": "z3M...ed25519_signature_base58"
  }
}
```

### 9.3 W3C DID 标准

```
W3C DID 规范核心概念：

1. DID 语法 (DID Syntax)
   did = "did:" method-name ":" method-specific-id
   示例: did:ethr:mainnet:0x1234...
         did:btcr:x1-ddca-...

2. DID 方法 (DID Method)
   每种方法定义在特定系统上的 DID 创建、解析、更新、撤销操作
   - did:ethr   → 以太坊 ERC-1056
   - did:web    → 基于域名
   - did:ion    → 微软 ION (Sidetree on Bitcoin)
   - did:keri   → KERI (Key Event Receipt Infrastructure)

3. DID 文档 (DID Document)
   - verificationMethod: 公钥和验证方法
   - authentication: 认证用密钥
   - assertionMethod: 签名凭证用密钥
   - keyAgreement: 密钥协商用密钥
   - service: 服务端点
   - capabilityInvocation/Delegation: 能力调用/委托

4. DID 解析 (DID Resolution)
   DID → DID Document 的解析过程
   依赖特定 DID 方法的解析器
```

---

---

## 📋 内容审核与补充建议

> 针对「DID 去中心化身份安全」部分的内容审核结果：

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
