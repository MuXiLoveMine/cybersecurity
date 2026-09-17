# 移动端 MITM 测试

### 4.1 证书安装与信任

```bash
# === Android ===

# 1. 导出 Burp 证书
# Burp Suite → Proxy → Options → Import/Export CA Certificate → DER format

# 2. 转换为系统证书格式
openssl x509 -inform DER -in burp.der -out burp.pem
hash=$(openssl x509 -inform PEM -subject_hash_old -in burp.pem | head -1)
mv burp.pem ${hash}.0

# 3. 安装为系统证书（需 root, Android 6+ 不会信任用户证书）
adb push ${hash}.0 /system/etc/security/certificates/
adb shell "su -c 'mount -o remount,rw /system'"
adb shell "su -c 'cp /sdcard/${hash}.0 /system/etc/security/certificates/'"
adb shell "su -c 'mount -o remount,ro /system'"

# === iOS ===
# 1. 下载 Burp 证书 (http://burp/cert)
# 2. 安装到设备: 设置 → 通用 → VPN与设备管理 → 安装
# 3. 信任证书: 设置 → 通用 → 关于本机 → 证书信任设置 → 启用
```

### 4.2 SSL Pinning 绕过方法汇总

| 方法 | 工具 | 适用场景 |
|------|------|----------|
| Frida 脚本 | objection / 自定义脚本 | Android + iOS 通用 |
| Xposed 模块 | JustTrustMe / SSLUnpinning | Android（需 Xposed） |
| Magisk 模块 | MagiskTrustUserCerts | Android（系统证书） |
| Cycript | 运行时修改 | iOS |
| APK 修改 | 反编译 → 修改网络配置 → 重打包 | Android（无 root） |

```bash
# Objection 一键绕过（最常用）
objection -g com.example.app explore
android sslpinning disable   # Android
ios sslpinning disable       # iOS

# Frida 脚本绕过
frida -U -f com.example.app -l ssl_pinning_bypass.js --no-pause
```

### 4.3 流量分析与篡改

```
MITM 工具链:
  ├── Burp Suite (最常用, 功能全面)
  ├── mitmproxy (命令行, 可编程)
  ├── Charles (图形界面, 易用)
  ├── HTTP Toolkit (快速部署)
  └── Wireshark (底层协议分析)

测试流程:
  1. 配置代理 → 安装证书 → 绕过 Pinning
  2. 捕获所有 HTTP/HTTPS 请求
  3. 分析请求中的敏感参数
  4. 测试参数篡改（越权/注入）
  5. 测试重放攻击
  6. 测试会话固定/Token 泄露
```

### 4.4 WebSocket / gRPC 流量

```bash
# Burp Suite 支持 WebSocket 拦截
# WebSocket 流量在 Proxy → WebSocket history 中查看

# mitmproxy 拦截 WebSocket
mitmproxy --set websocket=true

# gRPC 测试
# gRPC 使用 HTTP/2 + Protobuf
# 需要使用 grpcurl 或 Postman 进行测试
grpcurl -plaintext -d '{"username":"test"}' host:port /package.Service/Method

# Frida Hook gRPC 层获取明文
Interceptor.attach(Module.findExportByName("libgrpc.so", "grpc_slice_buffer_add"), {
    onEnter: function(args) {
        // 获取 gRPC 数据
    }
});
```

---

---

## 📋 内容审核与补充建议

> 针对「移动端 MITM 测试」部分的内容审核结果：

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
