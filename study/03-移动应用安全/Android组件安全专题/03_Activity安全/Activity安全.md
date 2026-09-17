# Activity安全

### 2.1 Activity基础

Activity是Android应用中最核心的组件，代表用户界面的一个屏幕。Activity的生命周期管理对安全性有重要影响：

```
                    +----------+
                    | Created  |
                    +----+-----+
                         |
                         v
                    +----+-----+
          +-------->| Started  |<--------+
          |         +----+-----+         |
          |              |               |
          |              v               |
          |         +----+-----+         |
          |         | Resumed  |         |
    +-----+----+    +----+-----+    +----+-----+
    |  Paused  |         |         |  Saved   |
    +-----+----+         |         +----+-----+
          |              v              |
          |         +----+-----+         |
          +---------+ Stopped  |<--------+
                    +----+-----+
                         |
                         v
                    +----+-----+
                    | Destroyed|
                    +----------+
```

Activity在AndroidManifest.xml中声明：

```xml
<activity
    android:name=".MainActivity"
    android:exported="true"
    android:permission="com.example.permission.LAUNCH"
    android:launchMode="singleTop"
    android:taskAffinity="com.example.app"
    android:noHistory="false"
    android:screenOrientation="portrait">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>
```

### 2.2 exported属性风险

`android:exported`是Activity最重要的安全属性，控制组件是否可被其他应用调用。

| exported值 | 含义 | 安全影响 |
|------------|------|----------|
| true | 可被任何应用调用 | 高风险，需配合权限保护 |
| false | 仅限应用内部调用 | 安全 |
| 未设置 | 根据intent-filter推断 | 有intent-filter则为true，无则为false |

**Android 12+强制声明**

从Android 12开始，包含intent-filter的组件必须显式声明exported属性，否则安装失败。这是Google为减少组件暴露漏洞的重要安全加固。

**风险场景：错误暴露的Activity**

```xml
<!-- 危险配置：暴露了敏感Activity但没有权限保护 -->
<activity
    android:name=".AdminSettingsActivity"
    android:exported="true">  <!-- 不应该暴露！ -->
    <intent-filter>
        <action android:name="com.example.action.ADMIN" />
    </intent-filter>
</activity>
```

攻击方式：

```java
// 攻击者应用直接启动管理界面
Intent intent = new Intent("com.example.action.ADMIN");
intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
startActivity(intent);

// 绕过登录直接进入管理功能
```

**风险场景：未设exported但有intent-filter**

```xml
<!-- Android 11及以下：有intent-filter默认exported=true -->
<activity android:name=".SensitiveActivity">
    <intent-filter>
        <action android:name="com.example.SENSITIVE_ACTION" />
    </intent-filter>
</activity>
<!-- 在Android 11及以下，此Activity默认可被外部调用 -->
```

**防御措施**

```xml
<!-- 正确配置1：不暴露，仅供内部使用 -->
<activity
    android:name=".AdminSettingsActivity"
    android:exported="false" />

<!-- 正确配置2：暴露但需要权限 -->
<activity
    android:name=".ShareActivity"
    android:exported="true"
    android:permission="com.example.permission.SHARE" />

<!-- 正确配置3：暴露但仅限同签名应用 -->
<activity
    android:name=".InternalActivity"
    android:exported="true"
    android:permission="com.example.permission.INTERNAL" />

<!-- 对应权限声明 -->
<permission
    android:name="com.example.permission.SHARE"
    android:protectionLevel="normal" />
<permission
    android:name="com.example.permission.INTERNAL"
    android:protectionLevel="signature" />
```

### 2.3 隐式Intent风险

隐式Intent不指定目标组件名，而是通过action、category、data匹配目标。这引入了Intent劫持风险。

**Intent劫持攻击**

```
正常流程：
  应用A --隐式Intent--> 系统选择 --> 目标Activity

攻击流程：
  应用A --隐式Intent--> 系统选择 --> 攻击者恶意Activity
                                    |
                                    v
                                  伪造界面窃取数据
```

攻击者注册与目标相同的intent-filter：

```xml
<!-- 攻击者应用AndroidManifest.xml -->
<activity android:name=".FakeLoginActivity" android:exported="true">
    <intent-filter>
        <action android:name="com.example.action.LOGIN" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
</activity>
```

```java
// 攻击者的FakeLoginActivity
public class FakeLoginActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // 获取原始Intent中的数据
        Intent originalIntent = getIntent();
        String username = originalIntent.getStringExtra("username");
        String password = originalIntent.getStringExtra("password");

        // 将窃取的凭证发送到攻击者服务器
        sendToAttacker(username, password);

        // 伪造登录成功，返回给调用方
        Intent resultIntent = new Intent();
        resultIntent.putExtra("status", "success");
        setResult(RESULT_OK, resultIntent);
        finish();
    }
}
```

**防御措施**

```java
// 防御1：使用显式Intent
Intent intent = new Intent(this, TargetActivity.class);
intent.putExtra("data", sensitiveData);
startActivity(intent);

// 防御2：如果必须使用隐式Intent，验证目标组件
Intent intent = new Intent("com.example.action.PROCESS");
intent.putExtra("data", sensitiveData);

// 使用Intent.createChooser强制用户选择
Intent chooser = Intent.createChooser(intent, "选择应用");
startActivity(chooser);

// 防御3：设置包名限制目标范围
intent.setPackage("com.example.target");
startActivity(intent);
```

### 2.4 Task和Back Stack安全

Android Task和Back Stack机制可能被利用进行UI欺骗攻击：

**Task劫持（Task Hijacking）**

攻击者利用`allowTaskReparenting`和`taskAffinity`属性将Activity从原Task转移到恶意Task：

```xml
<!-- 攻击者声明与目标应用相同的taskAffinity -->
<activity
    android:name=".MaliciousActivity"
    android:taskAffinity="com.example.victim"
    android:allowTaskReparenting="true"
    android:exported="true">
</activity>
```

当目标应用被切换到后台时，恶意Activity会被转移到目标应用的Task中，用户切换回应用时看到的是攻击者的界面而非原始界面。

**Android 9.0+ 限制**

从Android 9.0开始，`allowTaskReparenting`和`taskAffinity`的滥用已被限制，系统不允许不同签名的应用使用相同的taskAffinity。

### 2.5 Activity劫持

Activity劫持是一种社会工程学攻击，攻击者监控目标Activity的启动并迅速覆盖恶意界面：

```java
// 攻击者利用辅助功能服务监控前台应用
public class MaliciousAccessibilityService extends AccessibilityService {
    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event.getEventType() == TYPE_WINDOW_STATE_CHANGED) {
            String packageName = (String) event.getPackageName();
            if ("com.example.bank".equals(packageName)) {
                // 银行应用启动，立即启动覆盖Activity
                Intent overlay = new Intent(this, FakeBankActivity.class);
                overlay.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(overlay);
            }
        }
    }
}
```

**防御措施**

```java
// 检测是否有Activity覆盖在当前Activity上方
@Override
protected void onResume() {
    super.onResume();
    if (isOverlaidByOtherApp()) {
        // 显示安全警告
        showSecurityWarning();
        // 可选：阻止用户继续操作
    }
}

private boolean isOverlaidByOtherApp() {
    WindowManager windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
        return windowManager.getApplicationWindow() != null;
    }
    // 检测Toast或系统窗口覆盖
    // Android 12+提供了setShowWhenLocked和setTurnScreenOn替代方案
    return false;
}

// 使用FLAG_SECURE防止截屏和覆盖
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    getWindow().setFlags(
        WindowManager.LayoutParams.FLAG_SECURE,
        WindowManager.LayoutParams.FLAG_SECURE
    );
}
```

### 2.6 实战漏洞案例

**案例1：任意Activity调用**

某银行应用暴露了转账Activity但未设置权限：

```xml
<!-- 漏洞配置 -->
<activity android:name=".TransferActivity">
    <intent-filter>
        <action android:name="com.bank.action.TRANSFER" />
    </intent-filter>
</activity>
```

攻击者通过Intent直接调用转账Activity，绕过登录认证：

```java
Intent intent = new Intent("com.bank.action.TRANSFER");
intent.putExtra("account", "attacker_account");
intent.putExtra("amount", 10000);
intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
startActivity(intent);
```

**案例2：CVE-2018-... Activity注入**

多个应用因exported=true且无权限保护导致敏感Activity可被外部调用，攻击者可以：

- 绕过PIN码验证
- 直接访问应用内购买界面
- 调用深层功能绕过安全检查

---

---

## 📋 内容审核与补充建议

> 针对「Activity安全」部分的内容审核结果：

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
