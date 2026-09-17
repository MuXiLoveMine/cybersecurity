# Captive Portal攻击

### 5.1 Captive Portal工作原理

#### 5.1.1 什么是Captive Portal

Captive Portal（强制门户）是一种网络接入控制技术：
- 用户连接WiFi后，必须通过Web页面认证才能访问网络
- 常见于酒店、机场、咖啡馆、企业访客网络
- 认证方式：密码、短信验证、社交账号、接受条款等

#### 5.1.2 Captive Portal技术实现

**检测机制**：

操作系统通过检测特定URL来判断是否存在Captive Portal：

| 操作系统 | 检测URL |
|---------|--------|
| iOS/Apple | http://captive.apple.com/hotspot-detect.html |
| Android | http://connectivitycheck.gstatic.com/generate_204 |
| Windows | http://www.msftconnecttest.com/connecttest.txt |
| ChromeOS | http://clients3.google.com/generate_204 |

**检测原理**：
1. 客户端连接WiFi后，自动访问检测URL
2. 如果返回预期内容（如"Success"或204状态码），则认为已联网
3. 如果返回重定向（302）或其他内容，则弹出Captive Portal页面

**流量控制方式**：
1. **基于防火墙规则**：未认证用户只能访问特定IP/端口（DNS、HTTP）
2. **基于VLAN**：未认证用户在隔离VLAN中
3. **基于HTTP重定向**：所有HTTP请求被重定向到Portal页面

#### 5.1.3 认证流程

```
客户端连接WiFi
    |
    v
获取IP地址（DHCP）
    |
    v
访问检测URL
    |
    v
被重定向到Portal页面
    |
    v
用户输入凭证/接受条款
    |
    v
Portal服务器验证并通知AP/控制器
    |
    v
AP/控制器放开网络访问权限
    |
    v
客户端重新检测网络连通性
    |
    v
正常上网
```

---

### 5.2 Captive Portal欺骗攻击

#### 5.2.1 攻击原理

Captive Portal欺骗是一种特殊的Evil Twin攻击：

1. 攻击者创建开放WiFi（与目标同名或类似名称）
2. 部署虚假的Captive Portal页面
3. 用户连接后，看到与真实Portal相似的登录页面
4. 用户输入凭证（账号密码、手机号、信用卡号等）
5. 攻击者窃取凭证
6. 可选：将用户转发到真实网络，减少怀疑

#### 5.2.2 与普通Evil Twin的区别

| 特性 | 普通Evil Twin | Captive Portal欺骗 |
|------|------------|------------------|
| 目标 | 自动连接的客户端 | 手动连接的用户 |
| 攻击面 | WPA/WPA2密码 | Web表单凭证 |
| 成功率 | 取决于自动连接设置 | 取决于页面逼真度 |
| 用户交互 | 无（自动） | 有（手动输入） |
| 凭证类型 | WiFi密码 | 各种账号密码 |

#### 5.2.3 实战：创建虚假Captive Portal

**使用WiFi Pineapple / Evil Portal**：
```bash
# WiFi Pineapple的Evil Portal模块
# 1. 启动Evil Portal
# 2. 选择模板（Facebook、Google、酒店等）
# 3. 自定义页面内容
# 4. 启动虚假AP
# 5. 等待用户输入凭证
```

**手动搭建（基于hostapd + dnsmasq + apache）**：

1. 创建开放AP
```bash
# hostapd.conf
interface=wlan0
driver=nl80211
ssid=Free_WiFi
hw_mode=g
channel=6
```

2. DHCP + DNS配置
```bash
# dnsmasq.conf
interface=wlan0
dhcp-range=10.0.0.10,10.0.0.100,255.255.255.0,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
# 所有域名都解析到Portal服务器
address=/#/10.0.0.1
```

3. Portal页面
```php
<?php
// login.php - 捕获凭证
if ($_POST['username'] && $_POST['password']) {
    $creds = $_POST['username'] . ':' . $_POST['password'] . "\n";
    file_put_contents('/tmp/creds.txt', $creds, FILE_APPEND);
    // 重定向到真实页面或显示成功
    header('Location: success.html');
    exit;
}
?>
```

4. 流量重定向
```bash
# iptables规则 - 将所有HTTP/HTTPS流量重定向到Portal
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.1:80
iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination 10.0.0.1:443
```

---

### 5.3 自动连接漏洞

#### 5.3.1 自动连接原理

大多数设备会保存已知的WiFi网络配置，并在范围内时自动连接：

- **优先连接**：按照保存的网络列表优先级尝试连接
- **自动连接**：发现已知SSID时自动关联
- **漫游**：在同一网络的AP之间自动切换

#### 5.3.2 已知SSID攻击（KARMA攻击）

**攻击原理**：
1. 客户端发送Probe Request，请求已知SSID
2. 攻击者的AP响应Probe Response，宣称就是该SSID
3. 客户端自动连接到攻击者的AP
4. 攻击者成为中间人

**KARMA攻击的特点**：
- 不需要知道目标网络的密码
- 利用客户端的自动连接行为
- 适用于开放网络和保存的网络

**现代缓解措施**：
- 随机化Probe Request中的MAC地址
- 不广播已知SSID（被动扫描）
- 验证网络安全配置（如原网络是WPA2，不会连接到开放网络）

#### 5.3.3 同名AP攻击

即使客户端不主动广播Probe Request，攻击者仍可通过以下方式诱导连接：

1. 创建与目标常用网络同名的AP
2. 信号足够强时，客户端可能自动连接
3. 如果是开放网络，无需密码

**风险场景**：
- 用户手机保存了"Starbucks"开放网络
- 攻击者在其他地方创建同名开放网络
- 手机自动连接
- 攻击者捕获流量

#### 5.3.4 防御自动连接漏洞

- 关闭自动连接功能（特别是开放网络）
- 定期清理不使用的已知网络
- 使用VPN保护公共WiFi下的流量
- 禁用自动加入开放网络

---

### 5.4 DNS劫持与流量劫持

#### 5.4.1 DNS劫持攻击

**原理**：
- 攻击者控制了网络的DNS服务器
- 将特定域名解析到攻击者控制的IP
- 用户访问这些域名时，实际访问的是攻击者的服务器

**Captive Portal中的DNS劫持**：
- 在Captive Portal环境中，攻击者天然控制DNS
- 可以将任何域名解析到Portal页面
- 或者解析到恶意网站

**实战场景**：
```bash
# 使用dnsmasq劫持所有域名
address=/#/10.0.0.1

# 劫持特定域名
address=/facebook.com/10.0.0.1
address=/google.com/10.0.0.1
```

#### 5.4.2 HTTP流量劫持

**透明代理**：
- 攻击者使用iptables将HTTP流量重定向到代理服务器
- 代理服务器可以修改HTTP请求和响应
- 注入恶意脚本、替换内容等

**SSL Stripping**：
- 将HTTPS连接降级为HTTP
- 窃取明文凭证
- 在Captive Portal环境中更容易实施

#### 5.4.3 HTTPS流量的处理

HTTPS流量更难劫持，但有以下方法：

**方法一：证书警告**
- 使用自签名证书
- 用户可能忽略警告
- 成功率较低但仍然有效

**方法二：HTTPS降级**
- 阻止HTTPS连接，强制使用HTTP
- 许多网站支持HTTP回退

**方法三：利用混合内容**
- 在HTTP页面中注入恶意脚本
- 某些情况下可以窃取HTTPS cookie（如果cookie未标记Secure）

---

### 5.5 Evil Portal攻击（WiFi Pineapple）

#### 5.5.1 WiFi Pineapple简介

WiFi Pineapple是Hak5出品的无线审计设备，预装了多种攻击工具：
- Evil Portal：Captive Portal攻击模块
- PineAP：高级Evil Twin引擎
- DNSMasq Spoof：DNS欺骗
- Site Survey：无线侦察
- 多种Payload模块

#### 5.5.2 Evil Portal模块详解

**工作流程**：
1. PineAP创建开放AP
2. 客户端连接后获取IP
3. DNS请求全部指向Pineapple
4. HTTP请求被重定向到Portal页面
5. 用户在Portal页面输入凭证
6. 凭证被保存，用户被重定向

**Portal模板**：
- 通用登录页面
- 酒店WiFi登录
- 机场WiFi
- Facebook登录
- Google登录
- 自定义HTML

#### 5.5.3 高级Evil Portal技巧

**凭证验证**：
- 收集凭证后，尝试用真实API验证
- 例如用邮箱密码尝试登录邮箱
- 提高凭证的有效性

**会话保持**：
- 用户登录后，保持连接
- 继续监控流量，窃取更多信息
- 注入恶意脚本

**多页面流程**：
- 模拟真实Portal的多步骤流程
- 先接受条款，再输入信息
- 更逼真，降低用户警惕

---

### 5.6 移动端Captive Portal攻击

#### 5.6.1 移动端Captive Portal特点

**iOS特点**：
- 自动弹出Captive Portal助手（Captive Network Assistant）
- 该助手不是完整浏览器，有局限性
- 用户在助手中输入凭证后，助手自动关闭

**Android特点**：
- 通知栏显示"需要登录"提示
- 点击后打开浏览器
- 不同厂商实现有差异

**Windows特点**：
- 弹出系统级别的Portal窗口
- 类似浏览器，但有特殊处理

#### 5.6.2 针对移动端的攻击技巧

**利用Portal助手的局限性**：
- iOS的CNA（Captive Network Assistant）不支持某些JavaScript功能
- 但可以显示表单并提交数据
- 页面设计需要适配

**伪造系统级登录页面**：
- 模仿iOS/Android系统的WiFi登录界面
- 用户更可能信任并输入凭证

**移动端凭证窃取**：
- 窃取WiFi密码（在某些场景下）
- 窃取Apple ID/Google账号
- 窃取邮箱密码
- 窃取手机号和验证码

#### 5.6.3 移动端自动连接风险

**iOS的"自动加入"**：
- 默认对已保存的网络启用自动加入
- "已知网络"列表可能很长
- 对开放网络也会自动加入

**Android的"自动连接"**：
- 类似iOS的行为
- 部分设备有"智能选择网络"功能

**攻击场景**：
1. 攻击者创建与目标手机已知网络同名的开放AP
2. 目标手机在范围内自动连接
3. 弹出Captive Portal（如果配置了）
4. 用户可能在Portal中输入敏感信息
5. 即使没有Portal，攻击者也可以监控流量

---

---

## 📋 内容审核与补充建议

> 针对「Captive Portal攻击」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
