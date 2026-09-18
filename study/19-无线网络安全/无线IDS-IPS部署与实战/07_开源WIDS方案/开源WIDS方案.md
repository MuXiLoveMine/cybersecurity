# 开源WIDS方案

### 7.1 Kismet

Kismet是最流行的开源无线监控工具：

#### 核心能力
- 被动扫描所有802.11频段
- 设备发现与分类
- 隐藏SSID探测
- 数据包捕获（pcap格式）
- 基础攻击检测
- Web UI实时监控
- 插件系统扩展

#### 部署配置

```bash
# 安装Kismet
sudo apt-get install kismet

# 配置kismet.conf
source=rt8187:wifi0  # 指定无线网卡和驱动
channel=1,6,11,36,40,44  # 扫描信道
alertbackdoor=all  # 启用所有告警
logtitle=Kismet-Log  # 日志标题
logtypes=pcap  # 日志格式

# 启动Kismet
kismet -c wlan0 -t "WIDS-Monitor" --daemonize

# Web UI
http://localhost:2501
```

#### Kismet告警规则

```lua
# kismet_alerts.conf
alert DEAUTHFLOOD 100 1  # 100秒内超过1个Deauth -> 告警
alert DISASSOCFLOOD 100 1
alert AUTHFLOOD 60 10  # 60秒内超过10个Auth请求
alert APCHANGE  # AP信道或ESSID变化
alert PROBEREQUEST  # 异常Probe Request
alert BROADCASTPROBE  # 广播Probe
alert WEPFAIL  # WEP认证失败
alert WPA2DOWNGRADE  # WPA2降级攻击
alert TKIPREUSE  # TKIP重用
alert CHRSTOP  # 信道停止扫描
```

#### Kismet REST API

```python
import requests

# 获取所有设备
resp = requests.get('http://localhost:2501/devices/all_devices.json')
devices = resp.json()

# 获取告警
resp = requests.get('http://localhost:2501/alerts/alerts.json')
alerts = resp.json()

# 获取信道占用
resp = requests.get('http://localhost:2501/channels/channels.json')
channels = resp.json()
```

### 7.2 Horde

Horde是分布式Kismet部署框架：

```
[传感器1 - Kismet] ---+
[传感器2 - Kismet] ---+--> [Horde服务器]
[传感器3 - Kismet] ---+      [Web仪表盘]
```

### 7.3 其他开源工具

- **Aircrack-ng**：无线安全审计套件，支持抓包、注入、破解
- **PixieWPS**：WPS PIXIE攻击工具
- **Wifite**：自动化无线攻击框架
- **Fern WiFi Cracker**：GUI无线攻击工具

---

---

## 📋 内容审核与补充建议

> 针对「开源WIDS方案」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
