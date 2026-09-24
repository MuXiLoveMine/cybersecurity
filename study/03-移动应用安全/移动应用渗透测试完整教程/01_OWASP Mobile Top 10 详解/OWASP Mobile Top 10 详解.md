# OWASP Mobile Top 10 详解

OWASP Mobile Top 10 是移动应用安全风险的权威分类标准，最新版本为 2024 年发布。

### M1: Improper Platform Usage（平台使用不当）

**定义**：未正确利用平台提供的安全控制机制，如 Android 的 Intent 机制、iOS 的 Keychain。

**风险场景**：
- Android 组件未设置 `exported="false"` 导致未授权访问
- 未正确使用 Android 权限模型
- 未利用 iOS 的 Keychain/App Group 隔离
- WebView 中未限制文件访问和 JavaScript 交互

**测试方法**：
```bash
# Android 组件导出检测
drozer console connect -c "run app.provider.info com.example.app"
drozer console connect -c "run app.service.info com.example.app"

# 检查 AndroidManifest.xml 中的组件 exported 属性
```

### M2: Insecure Data Storage（不安全的数据存储）

**定义**：敏感数据（密码、Token、个人信息）以明文或不安全的方式存储在设备上。

**风险场景**：
- SharedPrefs 明文存储密码/Token
- SQLite 数据库未加密
- 日志中打印敏感信息
- SD 卡明文存储文件
- iOS UserDefaults 明文存储

**测试方法**：
```bash
# Android 数据存储检查
adb shell run-as com.example.app cat /data/data/com.example.app/shared_prefs/*.xml
adb shell run-as com.example.app cat /data/data/com.example.app/databases/*.db
adb logcat | grep -iE "password|token|secret|key"

# iOS Keychain 检查
objection -g com.example.app explore
ios keychain dump
ios nsuserdefaults dump
```

### M3: Insecure Communication（不安全的通信）

**定义**：应用与服务端之间的通信未加密或使用了弱加密。

**风险场景**：
- 使用 HTTP 明文传输
- HTTPS 但未做证书校验（自签名证书被信任）
- 未实现 SSL Pinning
- 使用弱 TLS 版本（TLS 1.0）
- 消息层加密使用 ECB 模式或固定 IV

**测试方法**：
```bash
# MITM 测试（详见第4节）
# 使用 Burp Suite / mitmproxy 抓包
# 测试 SSL Pinning 是否存在
```

### M4: Insufficient Authentication（认证不足）

**定义**：身份认证机制薄弱，可被绕过或暴力破解。

**风险场景**：
- 客户端本地校验密码（不与服务端校验）
- PIN 码无锁定机制
- 生物认证后无后端二次验证
- Token 过期时间过长或永不过期
- 密码策略过于简单

### M5: Insufficient Cryptography（加密不足）

**定义**：使用了不安全的加密算法或加密实现。

**风险场景**：
- 使用 DES/3DES 等过时算法
- AES 使用 ECB 模式
- 固定密钥硬编码在代码中
- 使用不安全的随机数生成器（java.util.Random）
- 自定义加密算法

### M6: Insecure Authorization（授权不足）

**定义**：授权检查仅在客户端实现，可被绕过。

**风险场景**：
- 客户端判断用户角色后直接显示功能
- API 未做服务端权限校验
- IDOR（不安全直接对象引用）
- 越权访问其他用户数据

### M7: Insecure Code Quality（不安全的代码质量）

**定义**：代码中存在安全缺陷，如硬编码密钥、调试接口未关闭。

**风险场景**：
- 代码中硬编码 API Key / Secret
- 调试日志未关闭
- 第三方 SDK 安全漏洞
- 未启用代码混淆和加固

### M8: Code Tampering（代码篡改）

**定义**：应用可被篡改（修改代码、重打包、注入）。

**风险场景**：
- 未做签名校验
- 未做完整性校验
- Root/越狱后可修改应用行为
- 可通过 Frida/Xposed 注入修改逻辑

### M9: Reverse Engineering（逆向工程）

**定义**：应用可被轻松逆向分析。

**风险场景**：
- 未使用代码混淆（ProGuard/R8）
- 未使用应用加固
- 关键逻辑未做 Native 化
- 资源文件未加密

### M10: Extraneous Functionality（多余功能）

**定义**：发布版本中残留了开发/测试功能。

**风险场景**：
- 残留调试开关
- 残留测试账号/密码
- 隐藏的后门接口
- 开发环境的 API 地址未替换

---

---

