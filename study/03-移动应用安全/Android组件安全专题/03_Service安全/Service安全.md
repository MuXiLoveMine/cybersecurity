# Service安全

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

---

