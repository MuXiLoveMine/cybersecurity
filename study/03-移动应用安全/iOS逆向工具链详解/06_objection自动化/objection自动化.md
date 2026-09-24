# objection自动化

### 6.1 越狱检测绕过

```bash
# 使用objection绕过越狱检测
objection -g com.example.app explore

# 自动绕过越狱检测
ios jailbreak disable

# 手动Hook越狱检测方法
# 在objection中执行
ios hooking search classes Jailbreak
ios hooking watch class JailbreakDetector

# 查看方法列表
ios hooking list class JailbreakDetector

# 替换方法返回值
ios hooking set return_value "-[JailbreakDetector isJailbroken]" false
```

### 6.2 SSL Pinning绕过

```bash
# 在objection中绕过SSL Pinning
ios sslpinning disable

# 查看HTTP请求
ios hooking watch class_method "-[NSURLSession dataTaskWithRequest:completionHandler:]" --dump-args --dump-return

# 拦截所有HTTP请求
android hooking watch class_method okhttp3.OkHttpClient$Builder.build
ios hooking watch class_method "*[* HTTPRequest]"
```

### 6.3 Keychain Dump

```bash
# 导出Keychain数据
ios keychain dump

# 导出并按格式化输出
ios keychain dump --json

# 导出NSUserDefaults
ios nsuserdefaults get

# 导出文件系统
ls /var/mobile/Containers/Data/Application/

# 查看应用沙盒
env
cd /var/mobile/Containers/Data/Application/<UUID>/

# 导出所有Cookie
ios cookies get
```

---

---

