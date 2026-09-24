# UDS 安全漏洞分析

### 2.1 SecurityAccess 绕过

SecurityAccess 绕过是 UDS 安全中最常见的攻击类型，以下分析几种典型绕过手段：

**漏洞类型 1：种子固定或可预测**

某些 ECU 实现中，种子并非真正随机，而是固定值或基于可预测计数器生成：

```
攻击过程：
1. 多次请求种子 (27 01)
2. 收集种子序列：0x00000001, 0x00000002, 0x00000003...
3. 发现种子为递增计数器
4. 预测下一次种子，提前计算密钥
5. 在合法窗口内发送预计算密钥 (27 02 [Key])
```

**漏洞类型 2：密钥算法过弱**

当密钥派生函数使用弱算法（如 CRC16 或 XOR）时，攻击者可通过已知明文-密文对快速逆向算法：

```
弱算法示例（XOR）：
  Key = Seed XOR Secret

已知: Seed=0x12345678, Key=0xABCD1234
推导: Secret = 0x12345678 XOR 0xABCD1234 = 0xB9F9404C
验证: 对任意新种子，Key = Seed XOR 0xB9F9404C
```

**漏洞类型 3：认证状态保持缺陷**

部分 ECU 在会话切换或重置后未能正确清除认证状态：

```
攻击链：
1. 在编程会话中通过 SecurityAccess 认证
2. ECUReset (11 01) 重置 ECU
3. ECU 重启后认证状态未被清除（漏洞）
4. 直接请求 34 (RequestDownload) → 成功，无需重新认证
```

**防护建议：**
- 使用加密强随机数生成器（CSPRNG / TRNG）
- 密钥派生使用 AES-CMAC 或 HMAC-SHA256
- 种子长度不少于 8 字节
- ECU 重置后必须清除所有认证状态
- 实现尝试次数限制和指数退避锁定

### 2.2 诊断会话劫持

诊断会话劫持指攻击者通过物理或远程方式接入车载总线，在合法诊断会话中注入恶意指令：

```
会话劫持场景：

合法 Tester                攻击者               ECU
    │                        │                   │
    │── 10 03 ──────────────│──────────────────▶│  进入扩展会话
    │── 27 01 ──────────────│──────────────────▶│  请求种子
    │◀────────────────────│──────────── 67 01 ──│  返回种子
    │── 27 02 [Key] ────────│──────────────────▶│  认证成功
    │                        │                   │
    │                        │── 2E [Addr] [Data] ─▶  注入恶意写入！
    │                        │                   │  ECU 认为已认证
    │                        │── 31 01 [Routine] ─▶  执行危险例程
```

**防护措施：**
- 诊断会话应绑定诊断设备身份（如诊断仪序列号）
- 实现 Tester 身份认证（TLS 客户端证书，针对 DoIP）
- 总线级访问控制（CAN ID 白名单过滤）
- 诊断会话超时（S3 Timer）自动退出
- 关键操作需要二次确认

### 2.3 固件刷写攻击

固件刷写（Flash Programming）通过 UDS 的 0x34/0x36/0x37 服务序列完成，攻击者可利用刷写流程漏洞植入恶意固件：

**正常刷写流程：**

```
步骤 1: 10 02         → 切换到编程会话
步骤 2: 27 01 / 27 02 → SecurityAccess 认证
步骤 3: 31 01 FF 01  → 启动预编程例程（擦除准备）
步骤 4: 34 [Addr] [Size] [Format] → 请求下载
步骤 5: 36 [BlockNo] [Data...] → 逐块传输固件
步骤 6: 37            → 结束传输
步骤 7: 31 01 FF 02  → 校验完整性
步骤 8: 11 01         → ECUReset，新固件启动
```

**固件刷写攻击面：**

| 攻击方式             | 描述                                      | 影响               |
|----------------------|------------------------------------------|--------------------|
| 固件篡改             | 中间人篡改刷写数据包                       | 植入后门           |
| 固件降级             | 刷写旧版本固件利用已知漏洞                  | 安全漏洞复现       |
| 恶意固件注入         | 直接写入攻击者定制固件                     | 完全控制 ECU       |
| 刷写中断攻击         | 在刷写过程中切断电源或总线                  | ECU 变砖（Brick）  |
| 校验绕过             | 绕过完整性校验例程                        | 篡改固件不被检测   |

**固件完整性验证机制：**

```c
// 固件刷写完整性校验示例
typedef struct {
    uint32_t firmware_version;
    uint32_t firmware_size;
    uint8_t  hash_sha256[32];    // 固件 SHA-256 哈希
    uint8_t  signature[256];     // RSA-2048 签名
    uint32_t ecu_id;
} firmware_header_t;

int verify_firmware_integrity(firmware_header_t *header, uint8_t *data) {
    // 1. 验证固件版本（防止降级攻击）
    if (header->firmware_version <= get_current_version()) {
        LOG_ERROR("Firmware downgrade detected!");
        return FIRMWARE_DOWNGRADE_REJECTED;
    }

    // 2. 验证哈希完整性
    uint8_t computed_hash[32];
    sha256(data, header->firmware_size, computed_hash);
    if (memcmp(computed_hash, header->hash_sha256, 32) != 0) {
        LOG_ERROR("Firmware hash mismatch!");
        return FIRMWARE_HASH_INVALID;
    }

    // 3. 验证数字签名
    int result = rsa_verify(
        header->hash_sha256, 32,
        header->signature, 256,
        get_oem_public_key()   // 预置的 OEM 公钥
    );
    if (result != RSA_VERIFY_OK) {
        LOG_ERROR("Firmware signature verification failed!");
        return FIRMWARE_SIGNATURE_INVALID;
    }

    // 4. 验证 ECU ID（防止刷错 ECU）
    if (header->ecu_id != get_ecu_hardware_id()) {
        LOG_ERROR("ECU ID mismatch!");
        return FIRMWARE_ECU_MISMATCH;
    }

    return FIRMWARE_VERIFICATION_OK;
}
```

---

---

