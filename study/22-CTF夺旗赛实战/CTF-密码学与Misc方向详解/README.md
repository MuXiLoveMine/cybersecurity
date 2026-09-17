# CTF-密码学与Misc方向详解

> 本文档整理自：`CTF-密码学与Misc方向详解.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 古典密码题型](./02_古典密码题型/古典密码题型.md)
  - 凯撒密码（Caesar Cipher）
  - 维吉尼亚密码（Vigenere Cipher）
  - 栅栏密码（Rail Fence Cipher）
  - 培根密码（Bacon Cipher）
  - 仿射密码（Affine Cipher）
  - 替换密码频率分析

### [03. RSA题型](./03_RSA题型/RSA题型.md)
  - RSA基础
  - 共模攻击（Common Modulus Attack）
  - 低解密指数攻击（Wiener Attack）
  - 低加密指数攻击（Small e Attack）
  - 广播攻击（Broadcast Attack）
  - Coppersmith定理
  - 选择密文攻击

### [04. AES题型](./04_AES题型/AES题型.md)
  - ECB模式重放
  - CBC字节翻转攻击
  - Padding Oracle攻击

### [05. 哈希题型](./05_哈希题型/哈希题型.md)
  - 长度扩展攻击
  - 哈希碰撞
  - 彩虹表攻击

### [06. 椭圆曲线密码](./06_椭圆曲线密码/椭圆曲线密码.md)
  - ECDLP（椭圆曲线离散对数问题）

### [07. 隐写术](./07_隐写术/隐写术.md)
  - 图片LSB隐写
  - 图片尾部数据
  - 音频隐写
  - 文档隐写
  - StegSolve使用

### [08. 流量分析](./08_流量分析/流量分析.md)
  - Wireshark过滤
  - USB流量还原
  - TLS密钥提取

### [09. 编码解码](./09_编码解码/编码解码.md)
  - Base系列
  - URL编码
  - Unicode编码
  - Morse电码
  - Brainfuck

### [10. Forensics取证](./10_Forensics取证/Forensics取证.md)
  - 磁盘取证
  - 内存取证
  - 日志分析

### [11. 实战案例](./11_实战案例/实战案例.md)
  - 案例1：RSA共模攻击
  - 案例2：AES-CBC Padding Oracle
  - 案例3：图片LSB隐写
  - 案例4：流量分析 - HTTP请求提取Flag
  - 案例5：内存取证 - Volatility分析

### [12. 安全最佳实践](./12_安全最佳实践/安全最佳实践.md)
  - 密码学安全
  - 隐写术防御

### [13. 学习总结](./13_学习总结/学习总结.md)
  - Crypto方向学习路线
  - Misc方向学习路线
  - 常用工具速查

---

## 📊 内容审核总览

- 总章节数：13
- 待完善章节：13

### 各章节审核状态
- **目录**：⚠️ 需补充 7 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **古典密码题型**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **RSA题型**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **AES题型**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
- **哈希题型**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **椭圆曲线密码**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **隐写术**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
- **流量分析**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **编码解码**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Forensics取证**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **实战案例**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：references
- **安全最佳实践**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **学习总结**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
