# OT-IT 融合安全架构

### 6.1 典型融合架构（基于 Purdue 模型 + DMZ）

```
┌────────────────────────────────────────────────────────────┐
│  Level 5  企业广域 / 互联网                                  │
│  Level 4  企业 IT（ERP、邮件、OA）                           │
└───────────────────────┬────────────────────────────────────┘
                         │ ←─ IT-OT 边界 ─→
        ┌────────────────┴───────────────────┐
        │     Level 3.5  IT/OT DMZ           │
        │  跳板机 / 反向代理 / OPC UA 网关    │
        │  日志收集 / 时间同步 / 补丁服务器    │
        └────────────────┬───────────────────┘
                         │ 工业防火墙 + 单向网闸
        ┌────────────────┴───────────────────┐
        │     Level 3  生产管理               │
        │  MES / 历史数据库 / 调度            │
        └────────────────┬───────────────────┘
                         │ 工业防火墙
        ┌────────────────┴───────────────────┐
        │     Level 2  控制网                  │
        │  SCADA / HMI / 工程师站             │
        └────────────────┬───────────────────┘
                         │
        ┌────────────────┴───────────────────┐
        │     Level 1  现场控制               │
        │  PLC / RTU / DCS                   │
        │     Level 0  现场设备              │
        │  传感器 / 执行器                    │
        └────────────────────────────────────┘
```

### 6.2 DMZ 部署要点

DMZ 是 OT-IT 融合的关键缓冲层，应遵循"双 DMZ 不信任"原则：

- IT 侧只能访问 DMZ，不可直接访问 OT
- OT 侧只能主动向 DMZ 推送数据，不接受 IT 侧主动连接
- 数据流向应设计为 OT→DMZ 单向（用于历史数据外送）
- 跳板机放置 DMZ，强制多因子认证 + 全程审计录屏

### 6.3 单向网闸（Data Diode）

单向网闸基于物理单向光器件实现，仅允许数据单方向传输，适用于：
- 关键 OT 数据外送至 IT 历史库
- 安全告警上传至 SOC
- 视频监控外送

**注意：** 单向网闸牺牲了反向通道，需配套单向协议适配器（如单向 OPC 代理）来弥补无反馈的协议握手问题。

### 6.4 OPC UA 网关

OPC UA 作为 IT-OT 融合的事实标准，提供：
- 内置 TLS 加密与证书认证
- 信息模型标准化，屏蔽底层工控协议差异
- Pub/Sub 与 Client/Server 双模式

**安全配置示例（OPC UA 网关安全策略）：**
```xml
<!-- OPC UA Server 安全配置示例 -->
<SecurityPolicies>
    <Policy Uri="http://opcfoundation.org/UA/SecurityPolicy/Basic256Sha256">
        <Description>SHA-256 签名 + AES-256 加密，推荐用于 SL2+ 场景</Description>
        <MinKeyLength>2048</MinKeyLength>
        <AsymmetricSignature>RSA-PKCS15-SHA256</AsymmetricSignature>
        <SymmetricBlockEncryption>AES-256-CBC</SymmetricBlockEncryption>
    </Policy>
</SecurityPolicies>
<UserTokenPolicies>
    <Policy Type="IssuedToken">
        <!-- 使用 X.509 证书身份，避免口令泄露风险 -->
        <IssuedTokenType>urn:ietf:rfc:6749</IssuedTokenType>
    </Policy>
</UserTokenPolicies>
```

**网关侧访问控制（基于角色）：**
```python
# OPC UA 网关 - 基于角色的访问控制示例
class OpcUaAcl:
    ROLE_MAP = {
        "viewer":    {"read": True,  "write": False, "control": False},
        "operator":  {"read": True,  "write": True,  "control": True},
        "engineer":  {"read": True,  "write": True,  "control": False},
        "auditor":   {"read": True,  "write": False, "control": False},
    }

    def check(self, subject_cert, node_id, action):
        role = self._map_cert_to_role(subject_cert)
        perm = self.ROLE_MAP.get(role, {})
        # 关键节点（如紧急停机）仅 operator 可控
        if node_id.startswith("ns=2;s=EmergencyStop") and action == "control":
            return role == "operator"
        return perm.get(action, False)
```

---

---

## 📋 内容审核与补充建议

> 针对「OT-IT 融合安全架构」部分的内容审核结果：

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
