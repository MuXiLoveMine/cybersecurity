# class-dump与头文件提取

### 2.1 class-dump基础

class-dump用于从Mach-O二进制文件中提取Objective-C类接口定义：

```bash
# 安装class-dump
# 从https://github.com/steve228uk/class-dump下载

# 基本用法
class-dump -H /path/to/App -o /output/dir/

# 提取所有头文件
class-dump -H MyApp.app/MyApp -o headers/

# 指定架构
class-dump -H --arch arm64 MyApp.app/MyApp -o headers/

# 提取特定类
class-dump --arch arm64 -o headers/ --classes MyClass MyApp.app/MyApp

# 生成可读性更好的输出
class-dump -H --sdk-root /path/to/sdk MyApp.app/MyApp -o headers/

# 使用class-dump-z（支持Swift）
# class-dump-z是class-dump的改进版
class-dump-z MyApp.app/MyApp -o headers/
```

### 2.2 头文件分析技巧

```bash
# 分析提取的头文件
# 找出继承自UIViewController的类
grep -r ': UIViewController' headers/

# 找出包含关键方法的类
grep -r 'login\|auth\|token\|verify' headers/ -l

# 找出使用URLSession的类
grep -r 'NSURLSession\|URLSession' headers/ -l

# 找出使用Keychain的类
grep -r 'Keychain\|SecItemAdd\|SecItemCopy' headers/ -l

# 找出使用加密的类
grep -r 'CC_SHA\|CCCrypt\|AES\|RSA\|encrypt\|decrypt' headers/ -l

# 找出包含敏感字符串的类
grep -r 'password\|secret\|api_key\|token' headers/ -l

# 分析协议定义
grep -r '@protocol' headers/ -l

# 分析Block使用
grep -r 'block\|Block' headers/ -l
```

---

---

