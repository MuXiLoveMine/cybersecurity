# iOS 恶意代码分析

### 3.1 iOS 恶意代码概述

iOS 由于其封闭的生态和严格的 App Store 审核机制，恶意代码数量远少于 Android，但高级定向攻击（APT）在 iOS 平台上同样存在，且危害往往更大。

**iOS 恶意代码传播方式**：

```
┌──────────────────────────────────────────────────┐
│              iOS 恶意代码传播途径                   │
├──────────────────────────────────────────────────┤
│                                                  │
│  1. 企业证书分发（企业 MDM 滥用）                  │
│     └ 利用 Apple Enterprise Developer 证书签名    │
│     └ 通过钓鱼网站诱导安装                         │
│     └ 典型：Pegasus、LuxSpyware                   │
│                                                  │
│  2. App Store 审核绕过                            │
│     └ 动态下载恶意载荷                             │
│     └ 延迟激活（审核时正常，运行后变恶）             │
│     └ 典型：XCSSET（2020年AppStore恶意软件）        │
│                                                  │
│  3. 越狱设备                                      │
│     └ 通过 Cydia/Sileo 第三方源安装               │
│     └ 无代码签名验证                              │
│     └ 典型：KeyRaider、LightSpy                  │
│                                                  │
│  4. 零日漏洞利用（无接触攻击）                      │
│     └ 利用 iMessage/Safari 零日漏洞              │
│     └ 无需用户交互                                 │
│     └ 典型：FORCEDENTRY（Pegasus）                │
│                                                  │
│  5. 描述文件（MDM Profile）钓鱼                    │
│     └ 诱导安装恶意 MDM 配置描述文件                 │
│     └ 控制设备策略、安装证书                       │
│                                                  │
└──────────────────────────────────────────────────┘
```

### 3.2 iOS 恶意代码分析工具链

```bash
# iOS 恶意分析工具链（需越狱设备）

# 1. class-dump：导出 ObjC 类信息
class-dump -H /path/to/MaliciousApp -o ./headers/

# 2. ipainstaller / ideviceinstaller：安装 IPA
ideviceinstaller -i malicious.ipa

# 3. frida：动态分析
frida -U -f com.malicious.app -l ios_hook.js --no-pause

# 4. Clutch / bfdecrypt：脱壳（分析 App Store 应用）
# 将加密的 IPA 解密为可分析的二进制
clutch -d com.malicious.app

# 5. Hopper / Ghidra / IDA：反汇编与反编译
# 分析 Native 代码
hopper /path/to/MaliciousApp

# 6. Keychain Dumper：导出 Keychain 数据
keychain-dumper

# 7. iRET (iOS Reverse Engineering Toolkit)
# 综合逆向工具包
```

**iOS Frida Hook 脚本**：

```javascript
// ios_malware_monitor.js
// iOS 恶意行为监控

// 监控 URL 请求
var NSURLRequest = ObjC.classes.NSURLRequest;
Interceptor.attach(NSURLRequest['+ requestWithURL:'].implementation, {
    onEnter: function(args) {
        var url = new ObjC.Object(args[2]).toString();
        console.log('[URL] ' + url);
    }
});

// 监控通讯录访问
var ABAddressBookRef = ObjC.classes.ABAddressBookRef;
Interceptor.attach(ABAddressBookRef['+ addressBookWithSourceRef:'].implementation, {
    onEnter: function(args) {
        console.log('[CONTACTS] 访问通讯录');
    }
});

// 监控位置获取
var CLLocationManager = ObjC.classes.CLLocationManager;
Interceptor.attach(CLLocationManager['- startUpdatingLocation'].implementation, {
    onEnter: function(args) {
        console.log('[LOCATION] 开始追踪位置');
    }
});

// 监控 Keychain 访问
var SecItemCopyMatching = Module.findExportByName('Security', 'SecItemCopyMatching');
Interceptor.attach(SecItemCopyMatching, {
    onEnter: function(args) {
        console.log('[KEYCHAIN] 读取 Keychain');
    }
});

// 监控剪贴板（可能窃取复制的密码）
var UIPasteboard = ObjC.classes.UIPasteboard;
Interceptor.attach(UIPasteboard['- string'].implementation, {
    onLeave: function(retval) {
        var str = new ObjC.Object(retval).toString();
        if (str.length > 0) {
            console.log('[CLIPBOARD] ' + str);
        }
    }
});
```

### 3.3 Pegasus 间谍软件分析

Pegasus 是 NSO Group 开发的商业间谍软件，是已知最强大的 iOS 恶意软件之一。

```
Pegasus 攻击链分析：

阶段1：投递（Delivery）
├── FORCEDENTRY（零点击漏洞）
│   ├── 利用 CoreGraphics PDF 解析漏洞 (CVE-2021-30860)
│   ├── 通过 iMessage 发送恶意 PDF
│   └── 无需用户交互自动触发
├── KISMET（零点击漏洞）
│   ├── 利用 WebKit 漏洞
│   └── 通过 Safari 访问触发
└── 社会工程
    └── 钓鱼短信引导点击链接

阶段2：提权（Privilege Escalation）
├── 利用内核漏洞获取 Root 权限
│   ├── CVE-2021-30807 (IOMobileFrameBuffer)
│   └── 其他未公开内核漏洞
└── 绕过沙箱限制

阶段3：植入（Implant）
├── Dropper 加载主模块
├── 主模块以 Root 权限运行
├── 持久化驻留（重启后自动运行）
└── 自毁机制（检测到分析环境时清除痕迹）

阶段4：数据收集
├── 通话记录和短信
├── 通讯录和日历
├── 照片和文件
├── 实时位置追踪
├── 实时录音和拍照
├── 浏览器历史和密码
├── WhatsApp/Telegram/Signal 消息
├── Gmail/Outlook 邮件
└── 应用内数据（银行/社交）

阶段5：数据外传
├── 通过 C&C 服务器加密上传
├── 使用域名生成算法（DGA）隐藏 C&C
├── 多级代理跳板传输
└── 数据加密传输（AES+RSA）
```

**Pegasus 检测方法**：

```bash
# MVT (Mobile Verification Toolkit) - 官方检测工具
# 由 Amnesty International 安全实验室开发

# 安装 MVT
pip install mvt

# 分析 iOS 备份
mvt-ios check-backup --output ./results /path/to/backup/

# 分析 iOS 文件系统（需越狱设备或取证镜像）
mvt-ios check-fs --output ./results /path/to/fs_mount/

# 检测内容：
# - 已知的 Pegasus 恶意域名
# - 异常的描述文件
# - 可疑的应用数据
# - 异常的数据库记录
# - 已知漏洞利用痕迹

# 输出示例：
# [!] Found Pegasus C2 domain: api-news[.]org
# [!] Suspicious profile installed: com.pegasus.mdm
# [!] Anomalous SMS database entry detected
```

---

---

## 📋 内容审核与补充建议

> 针对「iOS 恶意代码分析」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
