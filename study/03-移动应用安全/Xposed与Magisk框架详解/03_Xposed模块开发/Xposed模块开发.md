# Xposed模块开发

### 2.1 开发环境搭建

**步骤1：创建Android项目**

```gradle
// build.gradle (app模块)
apply plugin: 'com.android.application'

android {
    compileSdkVersion 34
    defaultConfig {
        applicationId "com.example.xposedmodule"
        minSdkVersion 26
        targetSdkVersion 34
        versionCode 1
        versionName "1.0"
    }
}

dependencies {
    // Xposed API - 使用compileOnly，不打包进APK
    compileOnly 'de.robv.android.xposed:api:82'
}
```

如果无法从Maven获取Xposed API，可以手动添加：

```gradle
dependencies {
    compileOnly files('libs/XposedBridgeApi-82.jar')
}
```

**步骤2：配置AndroidManifest.xml**

```xml
<application
    android:label="My Xposed Module"
    android:icon="@mipmap/ic_launcher">

    <!-- 声明为Xposed模块 -->
    <meta-data
        android:name="xposedmodule"
        android:value="true" />

    <!-- 模块描述 -->
    <meta-data
        android:name="xposeddescription"
        android:value="示例Xposed模块 - 演示Hook技术" />

    <!-- 最低版本要求 -->
    <meta-data
        android:name="xposedminversion"
        android:value="82" />

    <!-- 模块作用范围配置页面 (可选) -->
    <meta-data
        android:name="xposedscope"
        android:resource="@array/xposed_scope" />
</application>
```

**步骤3：定义作用范围**

```xml
<!-- res/values/arrays.xml -->
<resources>
    <string-array name="xposed_scope">
        <item>com.android.systemui</item>
        <item>com.example.target</item>
    </string-array>
</resources>
```

**步骤4：创建模块入口**

```java
// src/main/assets/xposed_init
com.example.xposedmodule.MainHook
```

### 2.2 Hook方法

**基础Hook - before/after回调**

```java
package com.example.xposedmodule;

import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.callbacks.XC_LoadPackage;

public class MainHook implements IXposedHookLoadPackage {

    private static final String TAG = "MyXposedModule";

    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        // 只Hook特定应用
        if (!lpparam.packageName.equals("com.example.target")) {
            return;
        }

        XposedBridge.log(TAG + ": Loaded into " + lpparam.packageName);

        hookMethodExample(lpparam);
        hookConstructorExample(lpparam);
        hookAllOverloadsExample(lpparam);
    }

    /**
     * 基本方法Hook示例
     */
    private void hookMethodExample(XC_LoadPackage.LoadPackageParam lpparam) {
        try {
            // Hook String.contains方法
            XposedHelpers.findAndHookMethod(
                "java.lang.String",           // 类名
                lpparam.classLoader,          // 类加载器
                "contains",                   // 方法名
                CharSequence.class,           // 参数类型
                new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) {
                        // 方法执行前调用
                        XposedBridge.log(TAG + ": before contains() called");
                        XposedBridge.log(TAG + ": arg = " + param.args[0]);

                        // 可以修改参数
                        // param.args[0] = "modified_value";

                        // 可以阻止原始方法执行并设置返回值
                        // param.setResult(false);
                    }

                    @Override
                    protected void afterHookedMethod(MethodHookParam param) {
                        // 方法执行后调用
                        XposedBridge.log(TAG + ": after contains() result = " + param.getResult());

                        // 可以修改返回值
                        // param.setResult(true);
                    }
                }
            );
        } catch (Throwable t) {
            XposedBridge.log(TAG + ": Hook failed: " + t.getMessage());
        }
    }

    /**
     * Hook构造函数示例
     */
    private void hookConstructorExample(XC_LoadPackage.LoadPackageParam lpparam) {
        try {
            Class<?> targetClass = XposedHelpers.findClass(
                "com.example.target.User", lpparam.classLoader);

            XposedHelpers.findAndHookConstructor(
                targetClass,
                String.class,   // name参数
                int.class,      // age参数
                new XC_MethodHook() {
                    @Override
                    protected void afterHookedMethod(MethodHookParam param) {
                        XposedBridge.log(TAG + ": User constructor called");
                        XposedBridge.log(TAG + ": name = " + param.args[0]);
                        XposedBridge.log(TAG + ": age = " + param.args[1]);
                    }
                }
            );
        } catch (Throwable t) {
            XposedBridge.log(TAG + ": Constructor hook failed: " + t.getMessage());
        }
    }

    /**
     * Hook所有重载版本
     */
    private void hookAllOverloadsExample(XC_LoadPackage.LoadPackageParam lpparam) {
        try {
            Class<?> targetClass = XposedHelpers.findClass(
                "com.example.target.NetworkClient", lpparam.classLoader);

            // Hook所有名为"sendData"的重载方法
            XposedBridge.hookAllMethods(
                targetClass,
                "sendData",
                new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) {
                        // 记录所有参数
                        StringBuilder sb = new StringBuilder("sendData(");
                        for (int i = 0; i < param.args.length; i++) {
                            if (i > 0) sb.append(", ");
                            sb.append(param.args[i] != null ?
                                param.args[i].toString() : "null");
                        }
                        sb.append(")");
                        XposedBridge.log(TAG + ": " + sb.toString());
                    }
                }
            );
        } catch (Throwable t) {
            XposedBridge.log(TAG + ": Hook all overloads failed: " + t.getMessage());
        }
    }
}
```

**替换方法实现**

```java
private void replaceMethodExample(XC_LoadPackage.LoadPackageParam lpparam) {
    try {
        XposedHelpers.findAndHookMethod(
            "com.example.target.CryptoUtils",
            lpparam.classLoader,
            "encryptPassword",
            String.class,
            new XC_MethodReplacement() {
                @Override
                protected Object replaceHookedMethod(MethodHookParam param) {
                    // 完全替换原始方法
                    String password = (String) param.args[0];
                    XposedBridge.log(TAG + ": Original password: " + password);

                    // 返回自定义结果
                    return "HOOKED_" + password.hashCode();
                }
            }
        );
    } catch (Throwable t) {
        XposedBridge.log(TAG + ": Replace failed: " + t.getMessage());
    }
}
```

### 2.3 替换资源

Xposed可以替换目标应用的资源（布局、字符串、图片等）：

```java
public class ResourceHook implements IXposedHookLoadPackage {

    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        if (!lpparam.packageName.equals("com.example.target")) return;

        try {
            // 获取目标应用的资源
            String targetPackage = lpparam.packageName;
            Context targetContext = getTargetContext(targetPackage);

            if (targetContext != null) {
                // 替换字符串资源
                String originalString = lpparam.res.getString(
                    lpparam.res.getIdentifier("app_name", "string", targetPackage));
                XposedBridge.log("Original app name: " + originalString);

                // 修改布局
                // 需要在initZygote阶段使用XResources
            }
        } catch (Exception e) {
            XposedBridge.log("Resource hook failed: " + e.getMessage());
        }
    }

    private Context getTargetContext(String packageName) {
        try {
            // 通过ActivityThread获取目标Context
            Class<?> activityThreadClass = Class.forName("android.app.ActivityThread");
            Object activityThread = XposedHelpers.callStaticMethod(
                activityThreadClass, "currentActivityThread");
            // 实现略
            return null;
        } catch (Exception e) {
            return null;
        }
    }
}
```

**使用XResources替换资源（initZygote阶段）**

```java
public class SystemResourceHook implements IXposedHookZygoteInit {

    @Override
    public void initZygote(StartupParam startupParam) {
        // 在Zygote阶段替换系统资源
        XResources res = getXResources();

        // 替换系统UI状态栏布局
        XposedBridge.hookAllMethods(
            XResources.class,
            "getLayout",
            new XC_MethodHook() {
                @Override
                protected void afterHookedMethod(MethodHookParam param) {
                    // 资源替换逻辑
                }
            }
        );
    }

    private XResources getXResources() {
        // 获取XResources实例
        return null; // 实现略
    }
}
```

### 2.4 模块开发实战

**实战1：Hook登录验证**

```java
public class LoginBypassHook implements IXposedHookLoadPackage {

    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        if (!lpparam.packageName.equals("com.example.secureapp")) return;

        try {
            // Hook登录验证方法
            XposedHelpers.findAndHookMethod(
                "com.example.secureapp.LoginManager",
                lpparam.classLoader,
                "verifyCredentials",
                String.class,  // username
                String.class,  // password
                new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) {
                        String username = (String) param.args[0];
                        String password = (String) param.args[1];
                        XposedBridge.log("Login attempt: " + username + "/" + password);

                        // 绕过验证，直接返回true
                        param.setResult(true);
                    }
                }
            );

            // HookisPremium方法
            XposedHelpers.findAndHookMethod(
                "com.example.secureapp.UserAccount",
                lpparam.classLoader,
                "isPremium",
                new XC_MethodHook() {
                    @Override
                    protected void afterHookedMethod(MethodHookParam param) {
                        param.setResult(true);
                    }
                }
            );
        } catch (Throwable t) {
            XposedBridge.log("Login bypass hook failed: " + t.getMessage());
        }
    }
}
```

**实战2：SSL Pinning绕过**

```java
public class SSLPinningBypassHook implements IXposedHookLoadPackage {

    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        // 对所有应用生效
        bypassSSL(lpparam);
    }

    private void bypassSSL(XC_LoadPackage.LoadPackageParam lpparam) {
        try {
            // Hook TrustManager验证
            Class<?> trustManagerClass = XposedHelpers.findClass(
                "javax.net.ssl.X509TrustManager", lpparam.classLoader);

            XposedHelpers.findAndHookMethod(
                "javax.net.ssl.X509TrustManager",
                lpparam.classLoader,
                "checkServerTrusted",
                java.security.cert.X509Certificate[].class,
                String.class,
                new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) {
                        // 跳过证书验证
                        param.setResult(null);
                    }
                }
            );

            // Hook OkHttp CertificatePinner
            try {
                XposedHelpers.findAndHookMethod(
                    "okhttp3.CertificatePinner",
                    lpparam.classLoader,
                    "check",
                    String.class,
                    java.util.List.class,
                    new XC_MethodHook() {
                        @Override
                        protected void beforeHookedMethod(MethodHookParam param) {
                            param.setResult(null);
                        }
                    }
                );
            } catch (Throwable ignored) {}

        } catch (Throwable t) {
            // 某些类可能不存在，忽略
        }
    }
}
```

### 2.5 调试与日志

```java
// 使用XposedBridge.log输出日志
XposedBridge.log("Debug message");

// 也可以使用Android Log
android.util.Log.d("XposedModule", "Debug message");

// 查看日志
// adb logcat | grep Xposed
// 或在Xposed Installer中查看Logs
```

---

---

## 📋 内容审核与补充建议

> 针对「Xposed模块开发」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
