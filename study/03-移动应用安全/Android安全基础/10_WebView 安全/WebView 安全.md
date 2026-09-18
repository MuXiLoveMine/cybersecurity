# WebView 安全

### 10.1 WebView 常见漏洞

#### 漏洞1：JavaScript 接口注入
```java
// 危险：addJavascriptInterface 可能导致远程代码执行
webView.getSettings().setJavaScriptEnabled(true);
webView.addJavascriptInterface(new JsInterface(), "android");

class JsInterface {
    @JavascriptInterface
    public String getData() {
        return "data";
    }
}
// 攻击者可通过反射调用 Java 层方法
// 在 Android 4.2 之前存在远程代码执行漏洞
```

#### 漏洞2：File 域访问与跨域
```java
// 危险：允许 WebView 访问本地文件
webView.getSettings().setAllowFileAccess(true);
webView.getSettings().setAllowFileAccessFromFileURLs(true);
webView.getSettings().setAllowUniversalAccessFromFileURLs(true);
// 攻击者可通过 file:// 协议读取本地文件
```

#### 漏洞3：明文密码存储
```java
// 危险：WebView 保存密码（已废弃但仍有应用使用）
webView.getSettings().setSavePassword(true);
// 密码会明文保存在 WebView 数据库中
```

### 10.2 WebView 安全配置

```java
WebSettings settings = webView.getSettings();

// 1. 禁用不必要的功能
settings.setJavaScriptEnabled(false);  // 不需要 JS 就禁用
settings.setAllowFileAccess(false);    // 禁用文件访问
settings.setAllowFileAccessFromFileURLs(false);
settings.setAllowUniversalAccessFromFileURLs(false);

// 2. 密码相关
settings.setSavePassword(false);       // 不保存密码

// 3. 缓存与存储
settings.setDomStorageEnabled(true);   // 根据需要开启
settings.setDatabaseEnabled(false);    // 禁用数据库

// 4. 内容安全
settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);

// 5. 证书错误处理
webView.setWebViewClient(new WebViewClient() {
    @Override
    public void onReceivedSslError(WebView view, SslErrorHandler handler, 
                                   SslError error) {
        handler.cancel();  // 证书错误时取消加载
    }
});
```

---

> 提示：Android 安全是一个持续学习的过程，建议结合 OWASP Mobile Top 10 和实际漏洞案例进行学习。

---

## 🛠️ 补充：实战拓展

### 一、四大组件安全检测命令速查

#### 1. Activity 组件安全检测

**静态检测命令**：

```bash
# 使用 aapt 查看 Activity 导出情况
aapt dump xmltree target.apk AndroidManifest.xml | grep -A 5 "activity"

# 使用 apktool 反编译后手动检查
apktool d target.apk -o target_decoded
grep -n "android:exported" target_decoded/AndroidManifest.xml

# 提取所有导出的 Activity（含 intent-filter 导致的隐式导出）
grep -B 2 -A 10 "<activity" target_decoded/AndroidManifest.xml | grep -E "(android:name=|exported=|intent-filter)" | head -40

# 检查带有 intent-filter 的 Activity（默认 exported=true）
grep -B 5 "intent-filter" target_decoded/AndroidManifest.xml | grep "activity"

# 查看 Activity 的权限保护
grep -B 3 -A 10 "android:permission" target_decoded/AndroidManifest.xml
```

**动态检测命令（adb）**：

```bash
# 启动导出的 Activity 测试越权
adb shell am start -n com.example.app/.PayActivity
adb shell am start -n com.example.app/.UserInfoActivity --es userid "admin"

# 通过 Action 启动 Activity（隐式 Intent）
adb shell am start -a com.example.app.action.VIEW_PROFILE --es user_id "1001"

# 查看顶层 Activity（验证是否成功跳转）
adb shell dumpsys window | grep mCurrentFocus

# 查看 Activity 栈
adb shell dumpsys activity activities | grep -E "TaskRecord|Hist" | head -20

# 检查应用的所有 Activity 信息
adb shell dumpsys package com.example.app | grep -A 300 "Activity Resolver Table:"
```

**Drozer 检测命令**：

```bash
# 列出所有导出的 Activity
dz> run app.activity.info -a com.example.app

# 尝试启动导出的 Activity
dz> run app.activity.start --component com.example.app com.example.app.PayActivity

# 检查是否有绕过权限的 Activity
dz> run app.activity.start --component com.example.app com.example.app.AdminActivity
```

---

#### 2. Service 组件安全检测

**静态检测命令**：

```bash
# 提取所有 Service 及其导出属性
grep -B 2 -A 8 "<service" target_decoded/AndroidManifest.xml

# 查找带 intent-filter 的 Service
grep -B 5 "intent-filter" target_decoded/AndroidManifest.xml | grep -E "service|receiver"

# 检查 Service 的权限保护
grep -B 2 -A 8 "android:permission" target_decoded/AndroidManifest.xml | grep -B 5 "service"
```

**动态检测命令（adb）**：

```bash
# 启动导出的 Service
adb shell am startservice -n com.example.app/.DownloadService
adb shell am startservice -n com.example.app/.DownloadService --es url "http://test.com/file.apk"

# 停止 Service
adb shell am stopservice -n com.example.app/.DownloadService

# 绑定 Service 并调用方法（需编写代码或使用 drozer）
# 查看当前运行的 Service
adb shell dumpsys activity services | grep com.example.app

# 查看应用的 Service 信息
adb shell dumpsys package com.example.app | grep -A 100 "Service Resolver Table:"
```

**Drozer 检测命令**：

```bash
# 列出所有导出的 Service
dz> run app.service.info -a com.example.app

# 启动 Service
dz> run app.service.start --component com.example.app com.example.app.DownloadService

# 发送消息到 Service（Messenger 方式）
dz> run app.service.send --component com.example.app com.example.app.MsgService --msg 1
```

---

#### 3. BroadcastReceiver 组件安全检测

**静态检测命令**：

```bash
# 提取所有 BroadcastReceiver
grep -B 2 -A 10 "<receiver" target_decoded/AndroidManifest.xml

# 查找所有广播 Action
grep -o 'android:name="[^"]*"' target_decoded/AndroidManifest.xml | grep -i "action" | sort -u

# 检查 receiver 的权限保护
grep -B 3 -A 10 "<receiver" target_decoded/AndroidManifest.xml | grep -E "name=|permission="

# 查找有序广播（priority 高的可劫持）
grep -B 10 "android:priority" target_decoded/AndroidManifest.xml | grep receiver
```

**动态检测命令（adb）**：

```bash
# 发送静态广播（测试导出的 Receiver）
adb shell am broadcast -a com.example.app.PAYMENT_RESULT --ez success true --es orderid "TEST123"

# 发送带权限的广播
adb shell am broadcast -a com.example.app.ACTION --es data "test" --receiver-permission com.example.permission.RECEIVE

# 发送有序广播
adb shell am broadcast -a com.example.app.ORDERED_ACTION --ez ordered true

# 查看应用注册的 Receiver
adb shell dumpsys package com.example.app | grep -A 100 "Receiver Resolver Table:"

# 查看系统中所有注册的广播接收器（含动态注册）
adb shell dumpsys activity broadcasts | grep -B 2 -A 2 "com.example"
```

**Drozer 检测命令**：

```bash
# 列出所有导出的 BroadcastReceiver
dz> run app.broadcast.info -a com.example.app

# 发送广播
dz> run app.broadcast.send --action com.example.app.PAYMENT_RESULT --extra boolean success true --extra string orderid TEST123

# 广播劫持检测 - 注册高优先级接收器
# （需编写自定义 drozer 模块或 Frida 脚本）
```

---

#### 4. ContentProvider 组件安全检测

**静态检测命令**：

```bash
# 提取所有 ContentProvider
grep -B 2 -A 10 "<provider" target_decoded/AndroidManifest.xml

# 查找 Provider 的 authorities（访问 URI）
grep "android:authorities" target_decoded/AndroidManifest.xml

# 检查读写权限分离
grep -B 5 -A 10 "readPermission\|writePermission" target_decoded/AndroidManifest.xml

# 检查 grantUriPermissions
grep -B 5 "grantUriPermissions" target_decoded/AndroidManifest.xml

# 查找 FileProvider（文件共享风险）
grep -B 5 -A 10 "FileProvider" target_decoded/AndroidManifest.xml
```

**动态检测命令（adb）**：

```bash
# 查询 ContentProvider 数据
adb shell content query --uri content://com.example.user.provider/users
adb shell content query --uri content://com.example.provider/users --projection name,password

# 插入数据
adb shell content insert --uri content://com.example.user.provider/users \
    --bind name:s:testuser --bind password:s:123456 --bind email:s:test@test.com

# 更新数据
adb shell content update --uri content://com.example.user.provider/users \
    --bind password:s:newpass --where "name='admin'"

# 删除数据
adb shell content delete --uri content://com.example.user.provider/users \
    --where "name='testuser'"

# 调用 ContentProvider 方法
adb shell content call --uri content://com.example.provider --method resetPassword --arg user123

# 测试 SQL 注入
adb shell content query --uri content://com.example.provider/users \
    --where "1=1 --"

# 测试路径遍历（FileProvider）
adb shell content query --uri content://com.example.fileprovider/../../../etc/hosts
```

**Drozer 检测命令**：

```bash
# 列出所有导出的 ContentProvider
dz> run app.provider.info -a com.example.app

# 查询 Provider 数据
dz> run app.provider.query content://com.example.user.provider/users
dz> run app.provider.query content://com.example.user.provider/users --projection name,password

# 测试 SQL 注入
dz> run app.provider.query content://com.example.user.provider/users --projection "* FROM users--"
dz> run app.provider.query content://com.example.user.provider/users --selection "1=1--"

# 测试路径遍历
dz> run app.provider.finduri content://com.example.fileprovider
dz> run app.provider.read content://com.example.fileprovider/../../../../etc/hosts

# 下载文件
dz> run app.provider.download content://com.example.fileprovider/my_images/photo.jpg /tmp/photo.jpg
```

---

### 二、四大组件安全自动化检测脚本

#### 脚本 1：AndroidManifest.xml 组件安全审计脚本（Python）

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# component_audit.py - AndroidManifest 四大组件安全审计工具
# 使用方式: python component_audit.py AndroidManifest.xml

import xml.etree.ElementTree as ET
import sys
import re

ANDROID_NS = "{http://schemas.android.com/apk/res/android}"

def audit_manifest(manifest_path):
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    
    # 获取包名
    package = root.get("package", "unknown")
    print(f"[*] 应用包名: {package}\n")
    
    app = root.find("application")
    if app is None:
        print("[-] 未找到 application 节点")
        return
    
    issues = []
    
    # ====== 1. 审计 Activity ======
    print("=" * 60)
    print("[Activity 组件审计]")
    print("=" * 60)
    activities = app.findall("activity")
    activity_aliases = app.findall("activity-alias")
    all_activities = activities + activity_aliases
    
    exported_activities = []
    for act in all_activities:
        name = act.get(f"{ANDROID_NS}name", "unknown")
        exported = act.get(f"{ANDROID_NS}exported")
        permission = act.get(f"{ANDROID_NS}permission")
        has_intent_filter = len(act.findall("intent-filter")) > 0
        
        # 判断是否导出
        is_exported = False
        export_reason = ""
        if exported == "true":
            is_exported = True
            export_reason = "显式设置 exported=true"
        elif exported == "false":
            is_exported = False
        elif has_intent_filter:
            # Android 12 以下，有 intent-filter 默认导出
            is_exported = True
            export_reason = "含 intent-filter 且未显式设置 exported"
        
        if is_exported:
            exported_activities.append({
                "name": name,
                "permission": permission,
                "reason": export_reason
            })
            
            status = "⚠️  已导出"
            perm_status = f" [权限: {permission}]" if permission else " [无权限保护!]"
            print(f"  {status} {name} - {export_reason}{perm_status}")
            
            if not permission:
                issues.append(f"[Activity] {name} 导出且无权限保护")
        else:
            print(f"  ✓ 未导出 {name}")
    
    print(f"\n  总计: {len(all_activities)} 个 Activity, {len(exported_activities)} 个已导出")
    
    # ====== 2. 审计 Service ======
    print("\n" + "=" * 60)
    print("[Service 组件审计]")
    print("=" * 60)
    services = app.findall("service")
    
    exported_services = []
    for svc in services:
        name = svc.get(f"{ANDROID_NS}name", "unknown")
        exported = svc.get(f"{ANDROID_NS}exported")
        permission = svc.get(f"{ANDROID_NS}permission")
        has_intent_filter = len(svc.findall("intent-filter")) > 0
        
        is_exported = False
        export_reason = ""
        if exported == "true":
            is_exported = True
            export_reason = "显式设置 exported=true"
        elif exported == "false":
            is_exported = False
        elif has_intent_filter:
            is_exported = True
            export_reason = "含 intent-filter 且未显式设置 exported"
        
        if is_exported:
            exported_services.append({
                "name": name,
                "permission": permission,
                "reason": export_reason
            })
            
            perm_status = f" [权限: {permission}]" if permission else " [无权限保护!]"
            print(f"  ⚠️  已导出 {name} - {export_reason}{perm_status}")
            
            if not permission:
                issues.append(f"[Service] {name} 导出且无权限保护")
        else:
            print(f"  ✓ 未导出 {name}")
    
    print(f"\n  总计: {len(services)} 个 Service, {len(exported_services)} 个已导出")
    
    # ====== 3. 审计 BroadcastReceiver ======
    print("\n" + "=" * 60)
    print("[BroadcastReceiver 组件审计]")
    print("=" * 60)
    receivers = app.findall("receiver")
    
    exported_receivers = []
    for recv in receivers:
        name = recv.get(f"{ANDROID_NS}name", "unknown")
        exported = recv.get(f"{ANDROID_NS}exported")
        permission = recv.get(f"{ANDROID_NS}permission")
        has_intent_filter = len(recv.findall("intent-filter")) > 0
        
        # 检查 intent-filter priority
        intent_filters = recv.findall("intent-filter")
        priorities = []
        for f in intent_filters:
            p = f.get(f"{ANDROID_NS}priority")
            if p:
                priorities.append(p)
        
        is_exported = False
        export_reason = ""
        if exported == "true":
            is_exported = True
            export_reason = "显式设置 exported=true"
        elif exported == "false":
            is_exported = False
        elif has_intent_filter:
            is_exported = True
            export_reason = "含 intent-filter 且未显式设置 exported"
        
        if is_exported:
            exported_receivers.append({
                "name": name,
                "permission": permission,
                "reason": export_reason
            })
            
            extras = []
            if priorities:
                extras.append(f"优先级: {','.join(priorities)}")
            perm_status = f" [权限: {permission}]" if permission else " [无权限保护!]"
            extra_str = f" [{'; '.join(extras)}]" if extras else ""
            
            print(f"  ⚠️  已导出 {name} - {export_reason}{perm_status}{extra_str}")
            
            if not permission:
                issues.append(f"[Receiver] {name} 导出且无权限保护")
            if priorities and any(int(p) > 100 for p in priorities):
                issues.append(f"[Receiver] {name} 优先级过高可能导致广播劫持")
        else:
            print(f"  ✓ 未导出 {name}")
    
    print(f"\n  总计: {len(receivers)} 个 Receiver, {len(exported_receivers)} 个已导出")
    
    # ====== 4. 审计 ContentProvider ======
    print("\n" + "=" * 60)
    print("[ContentProvider 组件审计]")
    print("=" * 60)
    providers = app.findall("provider")
    
    exported_providers = []
    for prov in providers:
        name = prov.get(f"{ANDROID_NS}name", "unknown")
        authorities = prov.get(f"{ANDROID_NS}authorities", "unknown")
        exported = prov.get(f"{ANDROID_NS}exported")
        read_perm = prov.get(f"{ANDROID_NS}readPermission")
        write_perm = prov.get(f"{ANDROID_NS}writePermission")
        grant_uri = prov.get(f"{ANDROID_NS}grantUriPermissions")
        
        is_exported = exported == "true"
        
        if is_exported:
            exported_providers.append({
                "name": name,
                "authorities": authorities,
                "read_perm": read_perm,
                "write_perm": write_perm
            })
            
            print(f"  ⚠️  已导出 {name}")
            print(f"     Authorities: {authorities}")
            print(f"     读权限: {read_perm or '无!'}")
            print(f"     写权限: {write_perm or '无!'}")
            print(f"     grantUriPermissions: {grant_uri}")
            
            if not read_perm or not write_perm:
                issues.append(f"[Provider] {name} ({authorities}) 缺少读写权限保护")
        else:
            print(f"  ✓ 未导出 {name} ({authorities})")
    
    print(f"\n  总计: {len(providers)} 个 Provider, {len(exported_providers)} 个已导出")
    
    # ====== 5. 全局安全配置检查 ======
    print("\n" + "=" * 60)
    print("[全局安全配置检查]")
    print("=" * 60)
    
    debuggable = app.get(f"{ANDROID_NS}debuggable")
    allow_backup = app.get(f"{ANDROID_NS}allowBackup")
    uses_cleartext = app.get(f"{ANDROID_NS}usesCleartextTraffic")
    network_security_config = app.get(f"{ANDROID_NS}networkSecurityConfig")
    
    checks = [
        ("debuggable", debuggable, "false", "允许调试模式，可被动态调试"),
        ("allowBackup", allow_backup, "false", "允许备份，数据可被窃取"),
        ("usesCleartextTraffic", uses_cleartext, "false", "允许明文传输，可被中间人攻击"),
    ]
    
    for name, value, expected, risk in checks:
        status = "⚠️  风险" if value == "true" else "✓ 安全"
        if value == "true":
            issues.append(f"[配置] {name}=true - {risk}")
        print(f"  {status} {name} = {value}")
    
    if network_security_config:
        print(f"  ✓ 配置了 networkSecurityConfig: {network_security_config}")
    else:
        print(f"  ⚠️  未配置 networkSecurityConfig")
        issues.append("[配置] 未配置 networkSecurityConfig")
    
    # ====== 输出风险汇总 ======
    print("\n" + "=" * 60)
    print("[安全风险汇总]")
    print("=" * 60)
    
    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print(f"\n  共发现 {len(issues)} 个潜在风险点")
    else:
        print("  ✓ 未发现明显的组件安全风险")
    
    return issues


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方式: python component_audit.py <AndroidManifest.xml路径>")
        print("示例: python component_audit.py ./target_decoded/AndroidManifest.xml")
        sys.exit(1)
    
    audit_manifest(sys.argv[1])
```

**使用方法**：
```bash
# 1. 先用 apktool 反编译 APK
apktool d target.apk -o target_decoded

# 2. 运行审计脚本
python component_audit.py target_decoded/AndroidManifest.xml

# 3. 保存审计结果
python component_audit.py target_decoded/AndroidManifest.xml > audit_report.txt
```

---

#### 脚本 2：Frida 四大组件调用监控脚本

```javascript
// component_monitor.js - 监控四大组件调用情况
// 使用方式: frida -U -f com.example.app -l component_monitor.js --no-pause

Java.perform(function() {
    console.log("\n[*] === 四大组件调用监控启动 ===\n");

    // ====== 1. 监控 Activity 启动 ======
    try {
        var Activity = Java.use("android.app.Activity");
        Activity.startActivity.overload('android.content.Intent').implementation = function(intent) {
            logIntent("[Activity.startActivity]", intent);
            return this.startActivity(intent);
        };
        
        Activity.startActivityForResult.overload('android.content.Intent', 'int').implementation = function(intent, requestCode) {
            logIntent("[Activity.startActivityForResult]", intent);
            return this.startActivityForResult(intent, requestCode);
        };
        
        console.log("[+] Activity 启动监控 Hook 成功");
    } catch(e) {
        console.log("[-] Activity Hook 失败: " + e);
    }

    // ====== 2. 监控 Service 启动与绑定 ======
    try {
        var ContextImpl = Java.use("android.app.ContextImpl");
        
        ContextImpl.startService.implementation = function(service) {
            logIntent("[startService]", service);
            return this.startService(service);
        };
        
        ContextImpl.bindService.overload('android.content.Intent', 'android.content.ServiceConnection', 'int').implementation = function(service, conn, flags) {
            logIntent("[bindService]", service);
            return this.bindService(service, conn, flags);
        };
        
        console.log("[+] Service 启动监控 Hook 成功");
    } catch(e) {
        console.log("[-] Service Hook 失败: " + e);
    }

    // ====== 3. 监控广播发送与接收 ======
    try {
        var ContextImpl2 = Java.use("android.app.ContextImpl");
        
        ContextImpl2.sendBroadcast.overload('android.content.Intent').implementation = function(intent) {
            logIntent("[sendBroadcast]", intent);
            return this.sendBroadcast(intent);
        };
        
        ContextImpl2.sendOrderedBroadcast.overload('android.content.Intent', 'java.lang.String').implementation = function(intent, receiverPermission) {
            logIntent("[sendOrderedBroadcast]", intent);
            console.log("  权限要求: " + receiverPermission);
            return this.sendOrderedBroadcast(intent, receiverPermission);
        };
        
        console.log("[+] 广播发送监控 Hook 成功");
    } catch(e) {
        console.log("[-] 广播 Hook 失败: " + e);
    }

    // ====== 4. 监控 ContentProvider 访问 ======
    try {
        var ContentResolver = Java.use("android.content.ContentResolver");
        
        ContentResolver.query.overload('android.net.Uri', '[Ljava.lang.String;', 'java.lang.String', '[Ljava.lang.String;', 'java.lang.String').implementation = function(uri, projection, selection, selectionArgs, sortOrder) {
            console.log("[ContentResolver.query]");
            console.log("  URI: " + uri.toString());
            if (selection) console.log("  Selection: " + selection);
            console.log("  调用栈:\n" + getJavaStack(3));
            return this.query(uri, projection, selection, selectionArgs, sortOrder);
        };
        
        ContentResolver.insert.overload('android.net.Uri', 'android.content.ContentValues').implementation = function(uri, values) {
            console.log("[ContentResolver.insert]");
            console.log("  URI: " + uri.toString());
            if (values) console.log("  Values: " + values.toString());
            return this.insert(uri, values);
        };
        
        ContentResolver.update.overload('android.net.Uri', 'android.content.ContentValues', 'java.lang.String', '[Ljava.lang.String;').implementation = function(uri, values, where, selectionArgs) {
            console.log("[ContentResolver.update]");
            console.log("  URI: " + uri.toString());
            if (where) console.log("  Where: " + where);
            return this.update(uri, values, where, selectionArgs);
        };
        
        ContentResolver.delete.overload('android.net.Uri', 'java.lang.String', '[Ljava.lang.String;').implementation = function(uri, where, selectionArgs) {
            console.log("[ContentResolver.delete]");
            console.log("  URI: " + uri.toString());
            if (where) console.log("  Where: " + where);
            return this.delete(uri, where, selectionArgs);
        };
        
        console.log("[+] ContentProvider 访问监控 Hook 成功");
    } catch(e) {
        console.log("[-] ContentProvider Hook 失败: " + e);
    }

    // ====== 辅助函数：打印 Intent 信息 ======
    function logIntent(tag, intent) {
        try {
            console.log(tag);
            console.log("  Action: " + intent.getAction());
            console.log("  Component: " + intent.getComponent());
            
            var data = intent.getData();
            if (data) console.log("  Data: " + data.toString());
            
            // 打印 extras
            var extras = intent.getExtras();
            if (extras != null) {
                var keys = extras.keySet().toArray();
                console.log("  Extras (" + keys.length + "):");
                for (var i = 0; i < keys.length && i < 20; i++) {  // 最多显示20个
                    var key = keys[i];
                    var value = extras.get(key);
                    var valStr = value ? value.toString() : "null";
                    if (valStr.length > 100) valStr = valStr.substring(0, 100) + "...";
                    console.log("    " + key + " = " + valStr);
                }
                if (keys.length > 20) console.log("    ... (共 " + keys.length + " 个)");
            }
            
            console.log("  调用栈:\n" + getJavaStack(3));
        } catch(e) {
            console.log("  (Intent 解析失败: " + e + ")");
        }
    }

    // ====== 辅助函数：获取 Java 调用栈 ======
    function getJavaStack(skip) {
        skip = skip || 0;
        try {
            var Exception = Java.use("java.lang.Exception");
            var stack = Exception.$new().getStackTrace();
            var result = "";
            for (var i = skip; i < stack.length && i < skip + 8; i++) {
                result += "    at " + stack[i].toString() + "\n";
            }
            return result;
        } catch(e) {
            return "    (获取调用栈失败)";
        }
    }

    console.log("\n[*] 监控脚本加载完成，等待组件调用...\n");
});
```

**实战场景**：
- 分析 App 内部组件调用关系，绘制组件交互图
- 检测是否存在隐式 Intent 注入风险
- 追踪敏感数据在组件间的传递路径
- 发现未在 Manifest 中声明的动态注册组件

**使用技巧**：
- 配合操作 App 的各个功能，观察组件调用情况
- 对输出较多的 App 可增加关键词过滤
- 可将输出重定向到文件：`frida -U -f com.xxx -l script.js > component_log.txt`

---

### 三、Drozer 完整检测流程

Drozer 是 Android 组件安全测试的专业框架，以下是完整的检测流程命令：

```bash
# 1. 启动 Drozer（设备端需安装 drozer-agent）
adb forward tcp:31415 tcp:31415
drozer console connect

# 2. 信息收集
dz> run app.package.list -f keyword          # 搜索包名
dz> run app.package.info -a com.example.app  # 查看应用信息
dz> run app.package.attacksurface com.example.app  # 查看攻击面

# 3. Activity 检测
dz> run app.activity.info -a com.example.app
dz> run app.activity.start --component com.example.app com.example.app.PayActivity
dz> run app.activity.start --component com.example.app com.example.app.UserInfoActivity --extra string user_id 1001

# 4. Service 检测
dz> run app.service.info -a com.example.app
dz> run app.service.start --component com.example.app com.example.app.DownloadService
dz> run app.service.send --component com.example.app com.example.app.MsgService --msg 1 --arg1 100

# 5. BroadcastReceiver 检测
dz> run app.broadcast.info -a com.example.app
dz> run app.broadcast.send --action com.example.PAYMENT_RESULT --extra boolean success true

# 6. ContentProvider 检测
dz> run app.provider.info -a com.example.app
dz> run app.provider.query content://com.example.provider/users
dz> run app.provider.query content://com.example.provider/users --projection "* FROM users--"
dz> run app.provider.finduri com.example.app

# 7. 其他检测
dz> run scanner.provider.injection -a com.example.app  # SQL 注入扫描
dz> run scanner.provider.traversal -a com.example.app  # 路径遍历扫描
dz> run app.package.backup -a com.example.app          # 备份检测
```

---

### 四、四大组件安全检测最佳实践

| 检测维度 | 检测方法 | 工具 | 风险等级判定 |
|---------|---------|------|-------------|
| **组件导出** | 检查 exported 属性和 intent-filter | aapt/apktool/drozer | 导出+无权限=高危 |
| **权限保护** | 检查 permission 属性 | aapt/apktool | 关键组件无权限=高危 |
| **Intent 注入** | 测试附加恶意参数 | adb/drozer/Frida | 可访问私有组件=高危 |
| **SQL 注入** | 测试 ContentProvider 查询参数 | adb/drozer | 可执行任意 SQL=严重 |
| **路径遍历** | 测试 FileProvider 路径 | adb/drozer | 可读系统文件=高危 |
| **广播劫持** | 测试有序广播优先级 | adb/Frida | 高优先级+敏感数据=高危 |
| **服务越权** | 测试启动/绑定服务 | adb/drozer | 可执行敏感操作=高危 |
| **组件权限** | 检查自定义权限保护级别 | aapt/apktool | signature 级别较安全 |

**检测流程建议**：
1. 先用静态工具（apktool + 审计脚本）快速发现导出组件
2. 再用 adb/drozer 进行动态验证
3. 对发现的漏洞用 Frida 深入分析调用链和数据流向
4. 最后编写 PoC 验证漏洞利用的实际影响

---

## 📋 内容审核与补充建议

> 针对「WebView 安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
