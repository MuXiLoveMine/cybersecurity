# NFC与RFID安全攻防详解

> 本文档整理自：`NFC与RFID安全攻防详解.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. NFC与RFID基础](./02_NFC与RFID基础/NFC与RFID基础.md)
  - RFID概述
  - NFC协议架构
  - 通信模式

### [03. RFID标签类型与安全](./03_RFID标签类型与安全/RFID标签类型与安全.md)
  - 标签分类
  - 频段与特性

### [04. Mifare系列安全分析](./04_Mifare系列安全分析/Mifare系列安全分析.md)
  - Mifare Classic
  - Mifare DESFire
  - 安全对比

### [05. 克隆攻击](./05_克隆攻击/克隆攻击.md)
  - 攻击原理
  - 工具与方法

### [06. 中继攻击](./06_中继攻击/中继攻击.md)
  - 攻击原理
  - NFC中继攻击

### [07. NFC支付安全](./07_NFC支付安全/NFC支付安全.md)

### [08. 门禁卡安全](./08_门禁卡安全/门禁卡安全.md)

### [09. 攻防工具](./09_攻防工具/攻防工具.md)
  - Proxmark3
  - ACR122U

### [10. 防护措施](./10_防护措施/防护措施.md)

### [11. Mifare Classic深度安全分析](./11_Mifare Classic深度安全分析/Mifare Classic深度安全分析.md)
  - Crypto-1加密算法详解
  - Nested Authentication攻击详解
  - Mifare Classic暗门攻击

### [12. Mifare DESFire EV3安全分析](./12_Mifare DESFire EV3安全分析/Mifare DESFire EV3安全分析.md)
  - DESFire EV3架构
  - DESFire安全通信
  - DESFire vs Classic安全对比

### [13. NFC中继攻击实现](./13_NFC中继攻击实现/NFC中继攻击实现.md)
  - 中继攻击技术实现

### [14. Proxmark3完整命令参考](./14_Proxmark3完整命令参考/Proxmark3完整命令参考.md)
  - Proxmark3 LF(125kHz)命令
  - Proxmark3 HF(13.56MHz)命令
  - Proxmark3高级功能

### [15. ACR122U详细使用](./15_ACR122U详细使用/ACR122U详细使用.md)
  - ACR122U APDU命令参考

### [16. NFC支付安全深度分析](./16_NFC支付安全深度分析/NFC支付安全深度分析.md)
  - HCE (Host Card Emulation)安全
  - 支付Token化(Tokenization)
  - NFC支付攻击与防御

### [17. RFID供应链安全](./17_RFID供应链安全/RFID供应链安全.md)
  - 供应链RFID安全挑战

### [18. 最佳实践与防护清单](./18_最佳实践与防护清单/最佳实践与防护清单.md)

---

## 📊 内容审核总览

- 总章节数：18
- 待完善章节：18

### 各章节审核状态
- **目录**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **NFC与RFID基础**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **RFID标签类型与安全**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Mifare系列安全分析**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **克隆攻击**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **中继攻击**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **NFC支付安全**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **门禁卡安全**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **攻防工具**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **防护措施**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **Mifare Classic深度安全分析**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **Mifare DESFire EV3安全分析**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **NFC中继攻击实现**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **Proxmark3完整命令参考**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
- **ACR122U详细使用**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
- **NFC支付安全深度分析**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **RFID供应链安全**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **最佳实践与防护清单**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
