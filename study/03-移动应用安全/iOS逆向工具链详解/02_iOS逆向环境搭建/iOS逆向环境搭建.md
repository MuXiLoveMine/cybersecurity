# iOS逆向环境搭建

### 1.1 Ubuntu逆向环境

在Ubuntu上搭建iOS逆向环境，安装核心工具链：

```bash
# 安装基础依赖
sudo apt update
sudo apt install -y build-essential git python3 python3-pip curl wget
sudo apt install -y libssl-dev libusb-dev libplist-utils

# 安装SDK工具
# 从已越狱设备提取SDK
# 将SDK文件放置到/opt/iOS-SDKs/

# 安装ldid（用于签名iOS二进制文件）
git clone https://github.com/daemontuss/ldid.git
cd ldid
./make.sh
sudo cp ldid /usr/local/bin/

# 安装dpkg-deb（用于创建deb包）
sudo apt install -y dpkg-dev

# 安装USB工具
sudo apt install -y libimobiledevice-dev ifuse usbmuxd

# 安装class-dump（通过Swift编译）
# 需要安装Swift工具链
sudo apt install -y swift
```

### 1.2 Theos越狱开发框架

Theos是iOS越狱插件（Tweak）开发的核心框架：

```bash
# 安装Theos
export THEOS=/opt/theos
sudo git clone --recursive https://github.com/theos/theos.git $THEOS

# 配置环境变量
echo 'export THEOS=/opt/theos' >> ~/.bashrc
echo 'export PATH=$THEOS/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# 安装iOS SDK
# 方法1：从Xcode提取
# 将iPhoneOS.sdk复制到$THEOS/sdks/

# 方法2：从越狱设备提取
# SSH到越狱设备，复制/System/Library/PrivateFrameworks
# 和/usr/lib到本地SDK目录

# 安装dpkg
sudo apt install -y dpkg

# 验证安装
theos --version
```

### 1.3 SDK与工具链配置

```bash
# 配置iOS SDK路径
# 将SDK放置到Theos的sdks目录
mkdir -p $THEOS/sdks
cp -r /path/to/iPhoneOS16.5.sdk $THEOS/sdks/

# 配置工具链
# Theos默认使用Clang
echo 'export THEOS_CHAIN=clang' >> ~/.bashrc

# 安装ldid用于签名
# ldid用于为iOS二进制文件进行伪签名

# 配置dpkg-deb路径
echo 'export PATH=/usr/bin:$PATH' >> ~/.bashrc

# 配置ssh到越狱设备
ssh-keygen -t rsa -b 4096
ssh-copy-id root@<iOS_DEVICE_IP>

# 配置SSH密码（默认alpine）
# 越狱设备默认root密码为alpine，务必修改
# 在设备上执行passwd修改密码

# 验证Theos配置
# 创建测试Tweak验证环境
```

---

---

## 📋 内容审核与补充建议

> 针对「iOS逆向环境搭建」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
