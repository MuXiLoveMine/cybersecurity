# ADB调试风险

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

---

## 📋 内容审核与补充建议

> 针对「ADB调试风险」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
