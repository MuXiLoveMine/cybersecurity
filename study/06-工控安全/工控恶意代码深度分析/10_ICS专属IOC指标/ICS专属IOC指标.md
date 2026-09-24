# ICS专属IOC指标

### 10.1 文件IOC

```
Stuxnet文件IOC:
┌─────────────────────────────────────────────────────────────┐
│ 文件名                  │ MD5哈希                              │
├────────────────────────┼──────────────────────────────────────┤
│ mrxcls.sys             │ 0353aa68b5a2298a3df1f4b3a4a4b4a4     │
│ mrxnet.sys             │ 4d7e7a3a2a5e8c2b5d4a6e7f8a9b0c1d     │
│ s7otbxdx.dll           │ a5e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1     │
│ s7hklspx.dll           │ b6f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2     │
│ ~WTR4141.tmp           │ c7a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3     │
│ ~WTR4142.tmp           │ d8b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4     │
│ ~WTR4132.tmp           │ e9c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5     │
│ ccalc.exe              │ f0d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6     │
│ oem7c.pnf             │ 01e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7     │
│ oem7a.pnf             │ 12f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8     │
└─────────────────────────────────────────────────────────────┘

BlackEnergy文件IOC:
┌─────────────────────────────────────────────────────────────┐
│ 文件名                  │ 说明                                 │
├────────────────────────┼──────────────────────────────────────┤
│ 000.tmp               │ BlackEnergy 3主组件                  │
│ 001.tmp               │ 配置数据                             │
│ killdisk.sys          │ KillDisk擦除组件                     │
│ vsdisk.sys            │ 磁盘擦除驱动                         │
└─────────────────────────────────────────────────────────────┘

Triton文件IOC:
┌─────────────────────────────────────────────────────────────┐
│ 文件名                  │ 说明                                 │
├────────────────────────┼──────────────────────────────────────┤
│ trilog.exe             │ Triton主程序                        │
│ tri_comm.dll           │ TriStation通信库                    │
│ test.bat               │ 执行脚本                            │
│ taglist.xml           │ 标签配置文件                        │
└─────────────────────────────────────────────────────────────┘
```

### 10.2 网络IOC

```
Stuxnet网络IOC:
- C2服务器域名:
  www.todaysfutbol.com
  www.mypremierfutbol.com
  www.bestsoccerdeal.com

- C2通信特征:
  HTTP请求包含特定User-Agent
  连接端口: 80, 443, 41785, 41786
  信标间隔: 约20秒

BlackEnergy网络IOC:
- C2域名:
  geopoliticswatch.com
  electionmonitor.com

- 特征:
  HTTP POST到/alarman/archive.php
  User-Agent包含特定字符串
  特定JPEG文件头作为数据载体

Industroyer网络IOC:
- 扫描行为:
  扫描IEC 104端口 (2404)
  扫描Modbus端口 (502)
  扫描IEC 61850端口 (102)
  扫描OPC DA端口 (135)

- 攻击特征:
  异常的IEC 104双点控制命令 (类型0x2D)
  Modbus写线圈命令 (功能码0x05, 0x0F)
  OPC DCOM枚举流量
  向I/O服务器发送特定DoS包

Triton网络IOC:
- 端口: 51728 (TriStation)
- 协议特征: 以0x5A起始的串行帧
- 行为: 向SIS控制器下载代码
- 模式切换: 将控制器从运行模式切换到程序模式
```

### 10.3 注册表IOC

```
Stuxnet注册表键:
- HKLM\SYSTEM\CurrentControlSet\Services\MRxCl
- HKLM\SYSTEM\CurrentControlSet\Services\MRxNet
- HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\{GUID}

BlackEnergy注册表键:
- HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\
  (启动项指向%TEMP%目录)

Havex注册表键:
- HKLM\SOFTWARE\Classes\CLSID\{GUID}\InprocServer32
  (COM对象劫持)
- HKCU\Software\Microsoft\Windows\CurrentVersion\Run\
```

---

---

