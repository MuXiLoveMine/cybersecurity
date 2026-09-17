# 国密算法详解

> 本文档整理自：`国密算法详解.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 国密算法概述](./02_国密算法概述/国密算法概述.md)
  - 什么是国密算法
  - 国密算法发展历程
  - 国密算法的法律地位
  - 国密算法应用领域

### [03. SM2椭圆曲线公钥密码算法](./03_SM2椭圆曲线公钥密码算法/SM2椭圆曲线公钥密码算法.md)
  - SM2算法概述
  - SM2椭圆曲线参数
  - SM2数字签名
  - SM2公钥加密
  - SM2密钥交换
  - SM2密钥派生函数KDF

### [04. SM3密码杂凑算法](./04_SM3密码杂凑算法/SM3密码杂凑算法.md)
  - SM3算法概述
  - SM3算法原理
  - SM3实现
  - SM3 HMAC

### [05. SM4分组密码算法](./05_SM4分组密码算法/SM4分组密码算法.md)
  - SM4算法概述
  - SM4算法原理
  - SM4实现
  - SM4工作模式

### [06. SM9标识密码算法](./06_SM9标识密码算法/SM9标识密码算法.md)
  - SM9算法概述
  - SM9与传统PKI对比
  - SM9算法结构
  - SM9应用场景

### [07. SM7分组密码算法](./07_SM7分组密码算法/SM7分组密码算法.md)

### [08. 祖冲之密码算法（ZUC）](./08_祖冲之密码算法（ZUC）/祖冲之密码算法（ZUC）.md)
  - ZUC算法概述
  - ZUC算法结构
  - ZUC在通信中的应用

### [09. 国密算法标准体系](./09_国密算法标准体系/国密算法标准体系.md)
  - 国密标准分类
  - 重要国密标准列表
  - 国密TLCP协议

### [10. 国密算法实现与工具](./10_国密算法实现与工具/国密算法实现与工具.md)
  - GmSSL工具
  - Python国密库
  - Java国密库（BouncyCastle）
  - C语言国密库（GmSSL C库）

### [11. 国密算法应用实践](./11_国密算法应用实践/国密算法应用实践.md)
  - 国密TLS实现
  - 国密VPN
  - 国密电子签章
  - 国密区块链

### [12. 国密与国际算法对比分析](./12_国密与国际算法对比分析/国密与国际算法对比分析.md)
  - 算法对比
  - 性能对比
  - 互操作性

### [13. 国密算法安全分析](./13_国密算法安全分析/国密算法安全分析.md)
  - SM2安全分析
  - SM3安全分析
  - SM4安全分析
  - ZUC安全分析

### [14. 总结与发展趋势](./14_总结与发展趋势/总结与发展趋势.md)
  - 国密算法优势
  - 国密算法发展趋势
  - 国密合规要求
  - 最佳实践
  - 参考资源

---

## 📊 内容审核总览

- 总章节数：14
- 待完善章节：14

### 各章节审核状态
- **目录**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **国密算法概述**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **SM2椭圆曲线公钥密码算法**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **SM3密码杂凑算法**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **SM4分组密码算法**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **SM9标识密码算法**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **SM7分组密码算法**：⚠️ 需补充 8 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **祖冲之密码算法（ZUC）**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **国密算法标准体系**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **国密算法实现与工具**：⚠️ 需补充 5 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **国密算法应用实践**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **国密与国际算法对比分析**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **国密算法安全分析**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **总结与发展趋势**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
