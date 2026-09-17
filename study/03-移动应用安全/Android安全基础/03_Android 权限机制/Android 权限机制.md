# Android 权限机制

### 3.1 权限分类

| 级别 | 说明 | 示例 | 申请方式 |
|------|------|------|----------|
| 正常权限 (Normal) | 不涉及用户隐私，系统自动授予 | 网络访问、蓝牙、震动 | 清单声明即可 |
| 危险权限 (Dangerous) | 涉及用户隐私，需用户授权 | 定位、相机、通讯录、存储 | 运行时申请 |
| 特殊权限 (Special) | 特殊功能，需用户在设置中开启 | 悬浮窗、无障碍、修改系统设置 | 跳转设置页面 |
| 签名权限 (Signature) | 只有相同签名的应用才能获得 | 自定义签名级权限 | 相同签名自动授予 |

### 3.2 危险权限分组（运行时权限）

Android 6.0 (API 23) 引入运行时权限机制，危险权限需要在运行时动态申请。

```
日历 (CALENDAR)         → READ_CALENDAR, WRITE_CALENDAR
相机 (CAMERA)           → CAMERA
通讯录 (CONTACTS)       → READ_CONTACTS, WRITE_CONTACTS, GET_ACCOUNTS
位置 (LOCATION)         → ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION
麦克风 (MICROPHONE)     → RECORD_AUDIO
电话 (PHONE)            → READ_PHONE_STATE, CALL_PHONE, READ_CALL_LOG 等
传感器 (SENSORS)        → BODY_SENSORS
短信 (SMS)              → SEND_SMS, RECEIVE_SMS, READ_SMS 等
存储 (STORAGE)          → READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
```

### 3.3 权限声明

**AndroidManifest.xml 中的声明**：
```xml
<!-- 正常权限：安装时自动授予 -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

<!-- 危险权限：需要运行时申请 -->
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.CAMERA" />

<!-- 自定义权限 -->
<permission
    android:name="com.example.permission.ACCESS_API"
    android:protectionLevel="signature"
    android:label="访问 API 权限" />
```

### 3.4 运行时权限申请（代码示例）

```java
public class MainActivity extends AppCompatActivity {

    private static final int REQUEST_CAMERA_PERMISSION = 1001;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // 检查是否已授权
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                != PackageManager.PERMISSION_GRANTED) {
            // 申请权限
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.CAMERA},
                    REQUEST_CAMERA_PERMISSION);
        } else {
            // 已授权，执行业务逻辑
            openCamera();
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode,
            @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_CAMERA_PERMISSION) {
            if (grantResults.length > 0
                    && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                // 用户同意授权
                openCamera();
            } else {
                // 用户拒绝授权
                if (ActivityCompat.shouldShowRequestPermissionRationale(
                        this, Manifest.permission.CAMERA)) {
                    // 用户拒绝但未勾选"不再询问"，解释权限用途
                    showPermissionRationale();
                } else {
                    // 用户勾选了"不再询问"，引导用户去设置页开启
                    showGoToSettingsDialog();
                }
            }
        }
    }
}
```

### 3.5 权限提升漏洞

**常见权限提升场景**：
1. **组件导出 + 隐式 Intent**：通过导出组件间接调用受限组件
2. **ContentProvider 路径遍历**：通过 ContentProvider 访问受限文件
3. **PendingIntent 误用**：使用外部可控的 Intent 构造 PendingIntent
4. **自定义权限保护级别过低**：使用 normal 级别保护敏感功能

**PendingIntent 误用案例**：
```java
// 危险：baseIntent 来自外部，可能被利用
Intent baseIntent = getIntent().getParcelableExtra("callback");
PendingIntent pendingIntent = PendingIntent.getActivity(
        this, 0, baseIntent, PendingIntent.FLAG_UPDATE_CURRENT);
// 攻击者可构造指向私有组件的 Intent，通过 PendingIntent 绕过权限
```

**修复方案**：
```java
// 使用显式 Intent，限定包名
Intent safeIntent = new Intent();
safeIntent.setClassName(getPackageName(), "com.example.CallbackActivity");
PendingIntent pendingIntent = PendingIntent.getActivity(
        this, 0, safeIntent, PendingIntent.FLAG_UPDATE_CURRENT | 
        PendingIntent.FLAG_IMMUTABLE);
```

---

---

## 📋 内容审核与补充建议

> 针对「Android 权限机制」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
