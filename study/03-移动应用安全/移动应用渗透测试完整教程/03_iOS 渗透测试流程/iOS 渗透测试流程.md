# iOS 渗透测试流程

### 3.1 越狱环境搭建

```
推荐越狱方案:
  - checkra1n (A5-A11 设备, 基于 checkm8 漏洞)
  - unc0ver (iOS 11.0-14.3)
  - palera1n (iOS 15+ A7-A11)

越狱后安装:
  - Cydia/Sileo (包管理器)
  - Frida (动态分析)
  - OpenSSH (远程连接)
  - Filza (文件管理器)
  - Clutch / bfdecrypt (脱壳)
  - Cycript (运行时分析)
```

### 3.2 IPA 解包与分析

```bash
# IPA 本质是 ZIP 文件
unzip target.ipa -d target_ipa

# 查看 Payload 目录
ls target_ipa/Payload/

# 查看 App 内容
ls target_ipa/Payload/TargetApp.app/

# 检查 Info.plist
plutil -p target_ipa/Payload/TargetApp.app/Info.plist

# 检查 URL Scheme
plutil -p target_ipa/Payload/TargetApp.app/Info.plist | grep -A5 "CFBundleURLSchemes"

# 检查 App Transport Security
plutil -p target_ipa/Payload/TargetApp.app/Info.plist | grep -A5 "NSAppTransportSecurity"

# 检查权限声明
codesign -d --entitlements - target_ipa/Payload/TargetApp.app
```

### 3.3 动态分析（Frida / Cycript）

```bash
# 使用 Frida 进行动态分析
frida -U -f com.example.app -l hook.js --no-pause

# 常用 iOS Frida 分析
# - 列出所有类
# - Hook 敏感方法
# - 监控 Keychain 操作
# - 绕过 SSL Pinning

# 使用 Cycript 进行运行时分析
cycript -p com.example.app

# Cycript 常用命令
# [ChooseClass] - 查找类的实例
# [[UIApplication sharedApplication] keyWindow] - 获取主窗口
```

### 3.4 Keychain 数据

```bash
# 使用 Frida/objection 导出 Keychain
objection -g com.example.app explore
ios keychain dump

# 常见 Keychain 安全问题:
# 1. 敏感数据用 kSecAttrAccessibleAlways（不安全）
# 2. 未使用 kSecAttrAccessGroup 隔离
# 3. 密码明文存储在 Keychain
```

### 3.5 App Transport Security (ATS)

```bash
# 检查 ATS 配置
plutil -p Info.plist | grep -A10 "NSAppTransportSecurity"

# 不安全配置:
# NSAllowsArbitraryLoads = true     → 允许所有 HTTP
# NSAllowsArbitraryLoadsInWebContent = true → WebView 允许 HTTP
# NSExceptionDomains 中包含豁免域名

# 安全配置:
# NSAllowsArbitraryLoads = false    → 强制 HTTPS
# 最低 TLS 版本 >= TLS 1.2
```

### 3.6 剪贴板安全

```javascript
// iOS 剪贴板安全检查
var UIPasteboard = ObjC.classes.UIPasteboard;
Interceptor.attach(ObjC.classes.UIPasteboard["- string"].implementation, {
    onLeave: function(retval) {
        var str = new ObjC.Object(retval);
        console.log("[剪贴板读取]", str.toString());
    }
});

// 风险: 敏感信息（密码/验证码）复制到剪贴板后
// 可被其他应用读取（iOS 14 之前无限制）
```

### 3.7 URL Scheme 安全

```bash
# 检查自定义 URL Scheme
plutil -p Info.plist | grep -A5 "CFBundleURLSchemes"

# 测试 URL Scheme
adb shell am start -W -a android.intent.action.VIEW -d "targetscheme://action?param=value"

# iOS URL Scheme 测试
frida -U -f com.example.app --eval 'ObjC.classes.UIApplication.sharedApplication().openURL_(ObjC.classes.NSURL.URLWithString_("targetscheme://test"))'
```

---

---

## 📋 内容审核与补充建议

> 针对「iOS 渗透测试流程」部分的内容审核结果：

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
