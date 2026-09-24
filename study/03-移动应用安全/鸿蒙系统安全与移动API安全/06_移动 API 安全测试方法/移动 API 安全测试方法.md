# 移动 API 安全测试方法

### 6.1 Burp Suite 移动端代理配置

**配置步骤**：

```
1. Burp Suite 设置代理监听
   Proxy -> Options -> Add
   - Bind to port: 8082
   - Bind to address: All interfaces
   
2. 移动设备 WiFi 代理设置
   - 设置 -> WiFi -> 修改网络 -> 高级
   - 代理: 手动
   - 主机名: <电脑IP>
   - 端口: 8082
   
3. 安装 Burp CA 证书
   - 访问 http://burp
   - 下载 cacert.der
   - Android: 设置 -> 安全 -> 安装证书
   - iOS: 设置 -> 通用 -> VPN与设备管理 -> 安装证书
   
4. Android 7+ 额外配置（应用不信任用户证书）
   - 方式1: Root 后将证书安装到系统证书目录
   - 方式2: 在应用的 network_security_config.xml 中信任用户证书
   - 方式3: 使用 Frida 绕过证书绑定
```

### 6.2 证书绑定绕过

**证书绑定（Certificate Pinning）** 阻止中间人代理抓包，需要绕过后才能测试 API。

**Frida 绕过 SSL Pinning 通用脚本**：

```javascript
// frida_ssl_pinning_bypass.js
// 适用于 Android 应用

Java.perform(function() {
    console.log('[*] 开始绕过 SSL Pinning...');

    // 绕过 OkHttp3 CertificatePinner
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List')
            .implementation = function(hostname, peerCertificates) {
            console.log('[+] OkHttp3 CertificatePinner.check 被绕过: ' + hostname);
            return;
        };
    } catch (e) {
        console.log('[-] OkHttp3 未找到: ' + e);
    }

    // 绕过 TrustManagerImpl
    try {
        var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
        var SSLContext = Java.use('javax.net.ssl.SSLContext');
        
        var TrustManager = Java.registerClass({
            name: 'com.frida.TrustManager',
            implements: [X509TrustManager],
            methods: {
                checkClientTrusted: function(chain, authType) {},
                checkServerTrusted: function(chain, authType) {},
                getAcceptedIssuers: function() { return []; }
            }
        });
        
        var TrustManagerArray = Java.array('javax.net.ssl.TrustManager', [
            new TrustManager()
        ]);
        
        var initSSLContext = SSLContext.init.overload(
            '[Ljavax.net.ssl.KeyManager;',
            '[Ljavax.net.ssl.TrustManager;',
            'java.security.SecureRandom'
        );
        initSSLContext.implementation = function(km, tm, sr) {
            console.log('[+] SSLContext.init 被替换');
            initSSLContext.call(this, km, TrustManagerArray, sr);
        };
    } catch (e) {
        console.log('[-] TrustManager 绕过失败: ' + e);
    }

    // 绕过 Conscrypt（Android 8+ 默认 TLS 提供者）
    try {
        var Conscrypt = Java.use('com.android.org.conscrypt.Conscrypt');
        Conscrypt.checkServerTrusted.overload(
            'javax.net.ssl.SSLSocket',
            'java.lang.String',
            'java.util.List'
        ).implementation = function(sslSocket, hostname, peerCertificates) {
            console.log('[+] Conscrypt 验证被绕过: ' + hostname);
            return;
        };
    } catch (e) {}
});

// 使用 objection 自动绕过：
// objection -g com.example.app explore
# android sslpinning disable
```

---

---

