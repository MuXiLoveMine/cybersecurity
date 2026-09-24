# NFC 安全

### 6.1 NFC 技术概览

NFC（Near Field Communication）工作在 13.56 MHz，通信距离通常在 4 cm 以内：

```
NFC 工作模式：

1. 读写模式（Reader/Writer）
   └── NFC 设备主动读写 NFC 标签

2. 点对点模式（Peer-to-Peer）
   └── 两个 NFC 设备之间交换数据

3. 卡模拟模式（Card Emulation）
   ├── HCE（主机卡模拟）：软件模拟
   └── eSE（嵌入式安全元件）：硬件安全

NFC 协议栈：
├── NFCIP-1（ISO 18092）
├── MIFARE（NXP 专有）
├── FeliCa（Sony 专有）
├── ISO 14443 A/B
└── ISO 15693
```

### 6.2 NFC 安全威胁

- **Relay Attack（中继攻击）**：通过中继设备转发 NFC 信号，远程欺骗读卡器
- **Eavesdropping（窃听）**：虽然通信距离短，但仍可通过高增益天线窃听
- **Data Corruption/Modification**：使用特定设备干扰或修改 NFC 信号
- **Card Emulation 攻击**：利用 HCE 模拟合法卡进行欺诈
- **克隆攻击**：复制 NFC 卡片数据到空白卡

---

---

