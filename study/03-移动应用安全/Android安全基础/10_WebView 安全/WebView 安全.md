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
