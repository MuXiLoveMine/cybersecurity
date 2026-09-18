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

## 📋 内容审核与补充建议

> 针对「objection自动化」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
