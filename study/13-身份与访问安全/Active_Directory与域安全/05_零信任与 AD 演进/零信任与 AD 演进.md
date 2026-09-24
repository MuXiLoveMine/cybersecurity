# 零信任与 AD 演进

### 5.1 Entra ID（Azure AD）混合架构

传统 AD 与 Entra ID 的混合架构是企业向云迁移的过渡方案：

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│ 本地 AD DS   │────→│ Entra Connect Sync│───→│ Entra ID     │
│ (域控)       │     │ (目录同步)         │    │ (Azure AD)   │
└──────────────┘     └──────────────────┘     └──────┬───────┘
                                                      │
                                          ┌───────────┼───────────┐
                                          │           │           │
                                     ┌─────▼────┐ ┌───▼───┐ ┌─────▼────┐
                                     │ M365 应用 │ │ Azure │ │ SaaS SSO │
                                     └──────────┘ └───────┘ └──────────┘
```

**混合认证模式**：
- **PHS（密码哈希同步）**：将本地密码哈希同步到云端，支持云认证
- **PTA（直通认证）**：通过本地代理验证密码，不存储哈希到云
- **Federation（联合认证）**：使用 ADFS/Entra 作为 IdP，本地保留认证

### 5.2 从域信任到零信任

| 维度 | 传统 AD 域信任 | 零信任模型 |
|------|---------------|-----------|
| 信任基础 | 网络位置 + 域认证 | 身份 + 设备 + 上下文 |
| 认证频率 | 一次登录长期有效（TGT 10h） | 每次访问持续评估 |
| 权限模型 | 静态组成员 | 动态策略 + JIT |
| 横向移动风险 | 高（Kerberos 票据可传递） | 低（微隔离 + 条件访问） |
| 管理边界 | 域/林边界 | 身份为中心，无边界 |

**演进路线**：
1. **加固期**：Tier 分层、LAPS、MDI、ACL 清理
2. **过渡期**：混合身份（Entra Connect）、条件访问策略
3. **目标态**：Entra ID 为身份平面，设备合规检查，JIT/PAM，无域信任

```
# Entra ID 条件访问策略示例（PowerShell）
$policy = @{
    DisplayName = "Require MFA for Admins"
    State = "Enabled"
    Conditions = @{
        Users = @{ IncludeGroups = @("Domain-Admins") }
        Applications = @{ IncludeApplications = @("All") }
    }
    GrantControls = @{
        Operator = "AND"
        BuiltInControls = @("Mfa", "CompliantDevice")
    }
}
New-MgIdentityConditionalAccessPolicy -BodyParameter ($policy | ConvertTo-Json -Depth 10)
```

---

---

