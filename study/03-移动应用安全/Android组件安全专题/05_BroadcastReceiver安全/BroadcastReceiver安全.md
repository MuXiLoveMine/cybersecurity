# BroadcastReceiver安全

### 4.1 BroadcastReceiver基础

BroadcastReceiver用于接收系统或应用发送的广播消息。广播分为：

- **普通广播**：异步发送，所有接收者几乎同时接收
- **有序广播**：按优先级顺序传递，可被终止或修改
- **本地广播**：仅在应用内部传递
- **粘性广播**：持久化广播（已废弃）

```xml
<receiver
    android:name=".BootReceiver"
    android:exported="true"
    android:permission="android.permission.RECEIVE_BOOT_COMPLETED">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>

<receiver
    android:name=".DataReceiver"
    android:exported="true">
    <intent-filter>
        <action android:name="com.example.action.DATA_UPDATE" />
    </intent-filter>
</receiver>
```

### 4.2 广播窃听

**风险：暴露的Receiver可被监听**

如果应用通过广播传递敏感数据，攻击者可以注册相同的action来窃听：

```xml
<!-- 正常应用发送广播 -->
<!-- 攻击者注册相同的action -->
<receiver android:name=".SpyReceiver" android:exported="true">
    <intent-filter>
        <action android:name="com.example.action.DATA_UPDATE" />
    </intent-filter>
</receiver>
```

```java
// 攻击者接收广播中的敏感数据
public class SpyReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        String sensitiveData = intent.getStringExtra("token");
        byte[] binaryData = intent.getByteArrayExtra("config");
        // 窃取数据发送到攻击者服务器
        exfiltrate(sensitiveData);
    }
}
```

**防御措施**

```java
// 防御1：使用LocalBroadcastManager（已废弃，推荐使用LiveData或Flow）
LocalBroadcastManager.getInstance(context)
    .sendBroadcast(intent);

// 防御2：发送有序广播并限制权限
context.sendOrderedBroadcast(
    intent,
    "com.example.permission.RECEIVE_DATA",  // 接收者必须持有此权限
    null, null, 0, null, null
);

// 防御3：设置目标包名
intent.setPackage("com.example.target");
context.sendBroadcast(intent);

// 防御4：不通过广播传递敏感数据，改用显式Intent或直接IPC
```

### 4.3 广播伪造

攻击者可以伪造系统广播或其他应用的广播：

```java
// 攻击者伪造广播
Intent fakeBroadcast = new Intent("com.example.action.DATA_UPDATE");
fakeBroadcast.putExtra("token", "attacker_token");
fakeBroadcast.putExtra("is_admin", true);
context.sendBroadcast(fakeBroadcast);
```

如果Receiver信任广播内容而不验证发送者：

```java
// 不安全的Receiver
public class DataReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        boolean isAdmin = intent.getBooleanExtra("is_admin", false);
        if (isAdmin) {
            // 信任了外部传入的权限标志
            grantAdminAccess();
        }
    }
}
```

**防御措施**

```xml
<!-- 限制谁可以发送广播给此Receiver -->
<receiver android:name=".DataReceiver" android:exported="true"
    android:permission="com.example.permission.SEND_DATA">
    <intent-filter>
        <action android:name="com.example.action.DATA_UPDATE" />
    </intent-filter>
</receiver>
```

```java
// 在Receiver中验证发送者
public class DataReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        // 验证发送者包名
        String senderPackage = getResultData(); // 或通过其他方式验证
        if (!isTrustedSender(senderPackage)) {
            return;  // 忽略不可信来源的广播
        }
        // 处理可信广播
    }
}
```

### 4.4 LocalBroadcastManager

LocalBroadcastManager确保广播只在应用内部传递，不暴露给其他应用：

```java
// 注册本地广播接收器
LocalBroadcastManager.getInstance(context).registerReceiver(
    receiver,
    new IntentFilter("com.example.LOCAL_ACTION")
);

// 发送本地广播
Intent intent = new Intent("com.example.LOCAL_ACTION");
intent.putExtra("data", sensitiveData);
LocalBroadcastManager.getInstance(context).sendBroadcast(intent);
```

注意：LocalBroadcastManager在AndroidX中已废弃，Google推荐使用LiveData或其他可观察模式替代。

### 4.5 实战漏洞案例

**案例：短信广播伪造**

某应用注册了短信到达广播并自动处理验证码，攻击者通过发送伪造广播注入假验证码：

```java
// 攻击者伪造短信到达广播
Intent fakeSms = new Intent("android.provider.Telephony.SMS_RECEIVED");
fakeSms.putExtra("pdus", new Object[]{fakePdu});
context.sendBroadcast(fakeSms);
```

---

---

## 📋 内容审核与补充建议

> 针对「BroadcastReceiver安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
