# Android 签名机制

### 5.1 v1 签名（JAR 签名）

**原理**：基于 JAR 签名方案，对 APK 中的每个文件单独计算摘要。

**签名流程**：
1. 对 APK 中每个文件计算 SHA-1 摘要，写入 MANIFEST.MF
2. 对 MANIFEST.MF 中的每个条目再计算摘要，写入 CERT.SF
3. 使用私钥对 CERT.SF 进行签名，结果和证书一起存入 CERT.RSA

**验证流程**：
1. 使用证书中的公钥验证 CERT.SF 的签名是否有效
2. 验证 CERT.SF 中的摘要与 MANIFEST.MF 是否匹配
3. 验证 MANIFEST.MF 中的摘要与实际文件内容是否匹配

**v1 签名的问题**：
- 只验证文件内容，不验证文件在 ZIP 中的结构
- 攻击者可以在不破坏签名的情况下修改 ZIP 结构（如添加额外文件）
- 验证速度慢，需要解压所有文件

### 5.2 v2 签名（APK Signature Scheme v2）

**原理**：对整个 APK 文件进行签名（Android 7.0+ 支持）。

**签名位置**：
```
┌─────────────────────────────────┐
│     ZIP 内容区（Content）        │  ← v1 签名验证的部分
├─────────────────────────────────┤
│   APK 签名块（APK Signing Block）│  ← v2/v3 签名数据
├─────────────────────────────────┤
│   ZIP 中央目录（Central Dir）    │
├─────────────────────────────────┤
│ ZIP 中央目录结束（EOCD）         │
└─────────────────────────────────┘
```

**签名流程**：
1. 将 APK 内容（ZIP 内容区 + 中央目录 + EOCD）分成多个 1MB 大小的块
2. 对每个块计算 SHA-256 摘要，组成摘要列表
3. 对摘要列表再计算摘要，得到整个 APK 的摘要
4. 使用私钥对摘要进行签名

**v2 签名的优势**：
- 验证速度快（不需要解压文件）
- 安全性更高（任何修改都会导致签名失效）
- 防篡改能力强

### 5.3 v3 签名（APK Signature Scheme v3）

**原理**：在 v2 的基础上增加了密钥轮换功能（Android 9.0+ 支持）。

**主要特性**：
- 支持签名密钥轮换（key rotation）
- 可以在 APK 中包含签名者的历史信息
- 应用更新时可以使用不同的签名密钥
- 提供签名者的证明链

### 5.4 签名验证优先级

Android 系统验证签名的优先级：
1. **v3 签名**（如果设备支持且 APK 包含 v3 签名）
2. **v2 签名**（如果设备支持且 APK 包含 v2 签名）
3. **v1 签名**（降级验证）

### 5.5 实际操作示例

**查看 APK 签名信息**：
```bash
# 使用 apksigner 工具（推荐）
apksigner verify --verbose app.apk

# 使用 jarsigner（仅能查看 v1 签名）
jarsigner -verify -verbose -certs app.apk

# 使用 keytool 查看证书
keytool -printcert -jarfile app.apk
```

**对 APK 进行签名**：
```bash
# 使用 apksigner 签名（支持 v1/v2/v3）
apksigner sign --ks keystore.jks \
    --ks-key-alias mykey \
    --v1-signing-enabled true \
    --v2-signing-enabled true \
    --v3-signing-enabled false \
    --out signed.apk unsigned.apk
```

### 5.6 签名绕过与二次打包

**二次打包流程**：
```
原始 APK → 反编译 → 修改代码/资源 → 重新打包 → 重新签名 → 安装运行
```

**防护措施**：
1. **签名校验**：运行时检查应用签名是否与预期一致
2. **完整性校验**：校验 dex 文件、so 文件的完整性
3. **加固保护**：使用加固服务增加破解难度

**签名校验代码示例**：
```java
public static boolean verifySignature(Context context) {
    try {
        PackageInfo packageInfo = context.getPackageManager()
                .getPackageInfo(context.getPackageName(),
                        PackageManager.GET_SIGNATURES);
        Signature[] signatures = packageInfo.signatures;
        
        // 计算签名的 hash 并与预期值比较
        String signatureHash = calculateHash(signatures[0].toByteArray());
        String expectedHash = "预期的签名哈希值";
        
        return expectedHash.equals(signatureHash);
    } catch (Exception e) {
        return false;
    }
}
```

---

---

