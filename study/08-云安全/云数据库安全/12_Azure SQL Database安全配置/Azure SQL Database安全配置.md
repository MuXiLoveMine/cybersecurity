# Azure SQL Database安全配置

### 12.1 Azure SQL安全基线配置

```bash
# 启用Azure AD认证
az sql server ad-admin create \
    --server myserver \
    --resource-group myGroup \
    --display-name "SQLAdminGroup" \
    --object-id <azure-ad-group-object-id>

# 配置防火墙规则(仅允许应用子网)
az sql server firewall-rule create \
    --server myserver \
    --resource-group myGroup \
    --name AllowAppSubnet \
    --start-ip-address 10.0.1.0 \
    --end-ip-address 10.0.1.255

# 禁用公网访问(仅允许私有链接)
az sql server update \
    --name myserver \
    --resource-group myGroup \
    --public-network-access Disabled

# 启用高级威胁防护
az sql db threat-policy update \
    --resource-group myGroup \
    --server myserver \
    --database mydb \
    --state Enabled \
    --email-addresses admin@company.com \
    --email-admins Enabled

# 启用漏洞评估
az sql db vulnerability-assessment scan start \
    --resource-group myGroup \
    --server myserver \
    --database mydb \
    --scan-id baseline

# 设置漏洞评估基线
az sql db vulnerability-assessment baseline create \
    --resource-group myGroup \
    --server myserver \
    --database mydb \
    --baseline-id baseline \
    --results "VA1234,VA5678"
```

### 12.2 Azure SQL TDE与Always Encrypted

```bash
# 启用TDE透明数据加密
az sql db tde set \
    --resource-group myGroup \
    --server myserver \
    --database mydb \
    --status Enabled

# 使用客户管理的密钥(Bring Your Own Key)
az keyvault create \
    --name myvault \
    --resource-group myGroup \
    --location eastus

az keyvault key create \
    --vault-name myvault \
    --name sql-tde-key \
    --kty RSA \
    --size 2048

# 授予SQL Server访问Key Vault权限
az keyvault set-policy \
    --name myvault \
    --object-id <sql-server-object-id> \
    --key-permissions get unwrapKey wrapKey

# 配置TDE使用BYOK
az sql server tde-key set \
    --server myserver \
    --resource-group myGroup \
    --server-key-type AzureKeyVault \
    --kid https://myvault.vault.azure.net/keys/sql-tde-key
```

**Always Encrypted配置示例**

```csharp
// C# - Always Encrypted 列加密配置
// 加密列定义
string createTable = @"
CREATE TABLE Patients (
    PatientId INT IDENTITY(1,1) PRIMARY KEY,
    SSN VARCHAR(11) COLLATE Latin1_General_BIN2
        ENCRYPTED WITH (
            ENCRYPTION_TYPE = DETERMINISTIC,
            ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256',
            COLUMN_ENCRYPTION_KEY = CEK_Auto1
        ),
    BirthDate DATE
        ENCRYPTED WITH (
            ENCRYPTION_TYPE = RANDOMIZED,
            ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256',
            COLUMN_ENCRYPTION_KEY = CEK_Auto1
        )
)";

// 应用层透明加密
string connectionString =
    "Server=myserver.database.windows.net;" +
    "Database=mydb;" +
    "Authentication=Active Directory Default;" +
    "Column Encryption Setting=Enabled;";

using (SqlConnection conn = new SqlConnection(connectionString))
{
    conn.Open();
    // 参数化查询自动加密/解密
    SqlCommand cmd = new SqlCommand(
        "INSERT INTO Patients (SSN, BirthDate) VALUES (@ssn, @birthDate)", conn);
    cmd.Parameters.AddWithValue("@ssn", "123-45-6789");
    cmd.Parameters.AddWithValue("@birthDate", new DateTime(1990, 1, 1));
    cmd.ExecuteNonQuery();
}
```

### 12.3 Azure SQL审计日志配置

```bash
# 启用SQL审计到存储账户
az sql db audit-policy update \
    --resource-group myGroup \
    --server myserver \
    --database mydb \
    --state Enabled \
    --storage-account mystorageaccount \
    --storage-account-suffix "" \
    --retention-days 90 \
    --audit-actions SUCCESSFUL_CONNECTION_AUTHENTICATION_GROUP \
        FAILED_CONNECTION_AUTHENTICATION_GROUP \
        BATCH_COMPLETED_GROUP \
        BATCH_STARTED_GROUP

# 发送审计日志到Log Analytics
az sql server audit-policy update \
    --resource-group myGroup \
    --server myserver \
    --state Enabled \
    --log-analytics-workspace-id <workspace-id>

# 发送到Event Hub
az sql server audit-policy update \
    --resource-group myGroup \
    --server myserver \
    --state Enabled \
    --event-hub <event-hub-name> \
    --event-hub-authorization-rule-id <rule-id>
```

### 12.4 Azure SQL动态数据掩码

```bash
# 配置动态数据掩码
az sql db data-masking create \
    --resource-group myGroup \
    --server myserver \
    --database mydb \
    --rule-id mask_ssn \
    --table-name Patients \
    --column-name SSN \
    --masking-function SSN

# 自定义掩码
az sql db data-masking create \
    --resource-group myGroup \
    --server myserver \
    --database mydb \
    --rule-id mask_email \
    --table-name Users \
    --column-name Email \
    --masking-function Text \
    --prefix-size 2 \
    --suffix-size 0 \
    --replacement-string "***"

# 授予用户查看未掩码数据权限
az sql db data-masking update \
    --resource-group myGroup \
    --server myserver \
    --database mydb \
    --exempt-principals "admin@company.com"
```

---

---

