# iOS应用脱壳

### 8.1 frida-ios-dump

```bash
# frida-ios-dump是最常用的iOS脱壳工具
# 需要越狱设备和USB连接

# 安装
git clone https://github.com/AloneMonkey/frida-ios-dump.git
cd frida-ios-dump
pip3 install -r requirements.txt

# 列出已安装应用
python3 dump.py -l

# 脱壳指定应用
python3 dump.py com.example.app

# 脱壳并输出到指定目录
python3 dump.py com.example.app -o /path/to/output/

# 脱壳原理
# 1. 通过Frida连接到目标应用
# 2. Hook dlopen/dlsym获取解密后的内存
# 3. 从内存中dump出解密的Mach-O文件
# 4. 重签名生成可分析的IPA
```

### 8.2 Clutch

```bash
# Clutch是经典的iOS脱壳工具
# 需要在越狱设备上运行

# 安装Clutch
# 通过Cydia/Sileo添加源安装
# 或从GitHub下载deb包安装

# 基本用法
Clutch -i                  # 列出已安装应用
Clutch -d com.example.app  # 脱壳指定应用
Clutch -d 2                # 按编号脱壳

# Clutch脱壳原理
# 1. 找到目标应用的Mach-O文件
# 2. 创建新的进程
# 3. 等待dyld完成解密
# 4. 从内存dump解密后的二进制
# 5. 保存到/var/root/Documents/
```

### 8.3 其他脱壳工具

```bash
# Cracknix（适用于较新iOS版本）
# 在越狱设备上运行
cracknix dump com.example.app

# flexdecrypt
# 通过Cydia安装
flexdecrypt /var/containers/Bundle/Application/<UUID>/MyApp.app/MyApp

# bagbak（基于Node.js）
npm install -g bagbak
bagbak com.example.app

# 手动脱壳方法
# 1. SSH到越狱设备
# 2. 找到应用路径
# 3. 使用gdb/lldb附加到进程
# 4. 获取解密后的内存
# 5. dump内存到文件

# 手动脱壳示例
# SSH到设备
ssh root@<device_ip>

# 找到应用路径
find /var/containers/Bundle/Application -name "MyApp"

# 使用LLDB脱壳
lldb -p <pid>
(lldb) image list MyApp
(lldb) memory read --size 1 --format x --count <size> <decrypt_addr> > dumped.bin
```

---

---

