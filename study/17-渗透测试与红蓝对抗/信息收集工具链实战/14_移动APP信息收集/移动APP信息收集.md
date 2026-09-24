# 移动APP信息收集

### 14.1 APK逆向信息收集

```bash
# APKTool - 反编译APK
# 安装
wget https://github.com/iBotPeaches/Apktool/releases/latest/download/apktool
chmod +x apktool

# 反编译
apktool d target.apk -o target_decoded

# 检查AndroidManifest.xml
cat target_decoded/AndroidManifest.xml | grep -i "permission\|api\|url\|key\|secret"

# 搜索敏感字符串
grep -rn "http://\|https://" target_decoded/
grep -rn "api_key\|apikey\|secret\|token\|password" target_decoded/
grep -rn "AWS\|firebase\|googleapis" target_decoded/

# 检查硬编码密钥
find target_decoded/ -name "*.xml" -o -name "*.json" | xargs grep -l "key\|secret\|token"

# MobSF - 移动安全框架(自动化分析)
# 安装
docker pull opensecurity/mobile-security-framework-mobsf
docker run -it -p 8000:8000 opensecurity/mobile-security-framework-mobsf

# 使用API上传分析
curl -F "file=@target.apk" http://localhost:8000/api/v1/upload
curl -X POST -d "scan_type=apk&file_hash=HASH" http://localhost:8000/api/v1/scan
```

### 14.2 iOS应用信息收集

```bash
# 提取IPA(需要越狱设备)
scp root@device:/var/containers/Bundle/Application/*/Target.app Target.app
ldid -e Target.app/Target  # 提取entitlements

# class-dump - 提取Objective-C类信息
class-dump -H Target.app/Target -o headers/

# 检查Info.plist
plutil -p Target.app/Info.plist | grep -i "url\|api\|key\|secret"

# 检查Embedded Mobile Provision
security cms -D -d Target.app/embedded.mobileprovision

# Frida - 动态分析
frida-ps -U  # 列出运行中的应用
frida-trace -U -f com.target.app -j "*[* *]"
```

### 14.3 APP网络请求抓取

```bash
# 使用mitmproxy抓包
pip install mitmproxy

# 启动代理
mitmproxy -p 8080

# 或使用mitmdump(命令行版本)
mitmdump -p 8080 -w traffic.flow

# 使用objection动态分析
pip install objection
objection -g com.target.app explore

# 在objection中:
# android hooking list classes
# android hooking search classes keyword
# android hooking watch class ClassName
# ios hooking list classes
# ios cookies get
# ios keychain dump
```

---

---

