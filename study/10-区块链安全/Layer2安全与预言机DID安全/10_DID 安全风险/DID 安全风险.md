# DID 安全风险

### 10.1 密钥管理风险

```
DID 密钥管理风险：

风险 1: 私钥丢失
  ├── DID 的控制权完全依赖于私钥
  ├── 私钥丢失 = 身份丧失
  └── 无法恢复（无中心化恢复机制）

风险 2: 私钥泄露
  ├── 私钥泄露 = 身份被盗用
  ├── 攻击者可冒充身份签发凭证
  └── 可转移关联资产

风险 3: 密钥轮换缺陷
  ├── 旧密钥未正确撤销 → 可被利用
  ├── 密钥轮换期间存在窗口期
  └── 历史凭证可能因密钥轮换而无法验证

风险 4: 多设备同步风险
  ├── 私钥在多设备间同步 → 增加泄露面
  └── 某一设备被攻破 → 整个 DID 被攻破

防护方案：
  ┌──────────────────────────────────────┐
  │  社交恢复 (Social Recovery)          │
  │  指定 N 个信任的恢复人               │
  │  超过阈值同意 → 可恢复 DID 控制       │
  ├──────────────────────────────────────┤
  │  多签 DID (Multi-sig DID)            │
  │  关键操作需要 M-of-N 签名             │
  ├──────────────────────────────────────┤
  │  HSM / 硬件钱包                       │
  │  私钥永不出现在软件环境中              │
  ├──────────────────────────────────────┤
  │  密钥委托 (Key Delegation)           │
  │  主密钥安全存储                       │
  │  委托子密钥用于日常操作                │
  └──────────────────────────────────────┘
```

### 10.2 DID 文档篡改

```solidity
// DID 注册合约（防篡改设计）
contract DIDRegistry {
    struct DIDDocument {
        bytes32  docHash;        // DID 文档哈希
        address  controller;     // 控制者地址
        uint64   updatedBlock;   // 更新区块号
        bool     deactivated;     // 是否已停用
    }
    
    mapping(bytes32 => DIDDocument) public dids; // DID ID → 文档
    
    event DIDUpdated(bytes32 indexed didId, bytes32 docHash, uint64 block);
    event DIDDeactivated(bytes32 indexed didId);
    
    // 创建/更新 DID
    function updateDID(
        bytes32 didId,
        bytes32 docHash,
        bytes calldata signature  // 控制者签名
    ) external {
        DIDDocument storage did = dids[didId];
        
        if (did.controller == address(0)) {
            // 新建 DID
            // 验证签名：签名者成为控制者
            address recovered = recoverSigner(didId, docHash, signature);
            did.controller = recovered;
        } else {
            // 更新现有 DID
            require(!did.deactivated, "DID deactivated");
            // 验证签名：必须是当前控制者
            address recovered = recoverSigner(didId, docHash, signature);
            require(recovered == did.controller, "Not authorized");
        }
        
        did.docHash = docHash;
        did.updatedBlock = uint64(block.number);
        
        emit DIDUpdated(didId, docHash, block.number);
    }
    
    // 停用 DID（不可逆）
    function deactivateDID(bytes32 didId, bytes calldata signature) external {
        DIDDocument storage did = dids[didId];
        require(!did.deactivated, "Already deactivated");
        
        address recovered = recoverSigner(keccak256(abi.encodePacked(didId, "DEACTIVATE")), signature);
        require(recovered == did.controller, "Not authorized");
        
        did.deactivated = true;
        emit DIDDeactivated(didId);
    }
    
    // 解析 DID
    function resolveDID(bytes32 didId) external view returns (
        bytes32 docHash, address controller, uint64 updatedBlock, bool active
    ) {
        DIDDocument storage did = dids[didId];
        require(did.controller != address(0), "DID not found");
        return (did.docHash, did.controller, did.updatedBlock, !did.deactivated);
    }
}
```

### 10.3 标识解析劫持

```
DID 解析劫持攻击：

  正常流程:
  DID: did:ethr:0x1234...
    → 解析器查询区块链/注册表
    → 返回真实 DID 文档
    → 使用真实公钥验证

  攻击流程:
  DID: did:ethr:0x1234...
    → 攻击者篡改解析器
    → 返回伪造 DID 文档（含攻击者公钥）
    → 使用攻击者公钥"验证"（通过！因为攻击者用自己的私钥签名）
    → 攻击者冒充 DID 主体

  攻击条件:
  - 攻击者控制本地解析器（如恶意 SDK）
  - DNS 劫持 did:web 方法
  - 解析器缓存投毒

  防护:
  - 使用可信解析器节点
  - 链上验证 DID 文档哈希
  - 多解析器交叉验证
  - 解析结果完整性签名验证
```

---

---

## 📋 内容审核与补充建议

> 针对「DID 安全风险」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
