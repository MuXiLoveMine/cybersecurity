# 常见 iOS 漏洞类型

### 6.1 系统级漏洞

#### 内核漏洞

**常见类型**：
- **缓冲区溢出**：内核驱动中的内存破坏
- **UAF（Use-After-Free）**：释放后使用
- **整数溢出**：整数运算溢出导致的内存问题
- **竞态条件**：多线程竞争导致的安全问题
- **IOKit 漏洞**：用户态与内核交互的驱动漏洞

**著名漏洞**：
- **Pangu 9**：iOS 9 越狱，利用多个内核漏洞
- **Yalu**：iOS 10 越狱，基于 IOKit 漏洞
- **tfp0**：获取 task_for_pid(0) 权限，即内核任务端口

#### WebKit 漏洞

WebKit 是 iOS 系统的浏览器内核，也是最常见的攻击面之一。

**常见类型**：
- **JIT 漏洞**：JavaScript JIT 编译器的漏洞
- **类型混淆**：对象类型错误导致的内存破坏
- **UAF**：对象释放后使用
- **越界读写**：数组越界访问

**著名漏洞链**：
- **JailbreakMe**：通过浏览器访问网页即可越狱
- **Pangu Web**：基于 WebKit 的越狱方案

#### 沙箱逃逸

沙箱逃逸是指从受限的沙箱环境中突破出来，获得更高权限。

**常见方法**：
- 利用 Mach 消息漏洞攻击系统服务
- 利用 XPC 服务漏洞
- 利用内核漏洞直接提权
- 利用文件系统漏洞

### 6.2 应用级漏洞

#### 数据存储不安全

**常见问题**：
- **钥匙串使用不当**：虽然钥匙串是安全的，但如果配置不当也有风险
- **plist 文件明文存储**：敏感信息存储在 UserDefaults 的 plist 中
- **剪贴板数据泄露**：敏感信息复制到剪贴板后被其他应用读取
- **屏幕截图泄露**：应用进入后台时的截图可能包含敏感信息
- **日志泄露**：NSLog 输出敏感信息

**示例：不安全的 UserDefaults**
```swift
// 危险：明文存储密码
UserDefaults.standard.set(password, forKey: "user_password")

// 安全：使用 Keychain 存储
let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrAccount as String: "user_password",
    kSecValueData as String: password.data(using: .utf8)!
]
SecItemAdd(query as CFDictionary, nil)
```

#### 通信安全问题

**常见问题**：
- **ATS 配置不当**：允许 HTTP 明文传输
- **证书校验绕过**：自定义 URLProtocol 或 SSL 代理导致证书校验失效
- **SSL Pinning 实现缺陷**：实现有漏洞的证书固定

**ATS（App Transport Security）**：
```xml
<!-- 危险：完全禁用 ATS -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>

<!-- 推荐：仅对特定域名允许 HTTP -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>api.example.com</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <false/>
        </dict>
    </dict>
</dict>
```

#### WebView 漏洞

**常见问题**：
- **JavaScript 接口注入**：通过 JavaScript 调用原生代码
- **URL Scheme 攻击**：通过自定义 URL Scheme 调用应用功能
- **Universal Link 绕过**：绕过 Universal Link 校验
- **文件域漏洞**：通过 file:// 协议读取本地文件

#### URL Scheme 安全

**风险**：
- 恶意应用注册相同的 URL Scheme
- 通过 URL Scheme 调用应用内部功能
- 参数注入导致越权操作

**示例：URL Scheme 调用**
```swift
// 调用其他应用
if let url = URL(string: "myapp://pay?amount=100") {
    UIApplication.shared.open(url)
}
```

### 6.3 业务逻辑漏洞

与 Web 应用类似，移动应用也存在业务逻辑漏洞：

- **越权访问**：修改用户 ID 查看他人数据
- **支付漏洞**：修改支付金额、绕过支付验证
- **验证码绕过**：验证码可重放、可预测
- **密码重置漏洞**：重置逻辑缺陷
- **刷积分/刷奖励**：利用业务逻辑漏洞

---

---

## 📋 内容审核与补充建议

> 针对「常见 iOS 漏洞类型」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
