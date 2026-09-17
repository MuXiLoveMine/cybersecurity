# 商业WIDS方案对比

### 6.1 Cisco Adaptive Wireless IPS

**架构**：Cisco WLC（Wireless LAN Controller）+ lightweight AP

**核心功能**：
- Rogue AP检测与自动遏制
- 自无线干扰检测（wIPS功能需要额外许可证）
- 集成ISE进行身份关联
- 频谱分析（CleanAir技术）
- 支持分布式部署

**优势**：
- 与Cisco网络设备深度集成
- CleanAir频谱分析业界领先
- 支持跨控制器Rogue AP关联

**劣势**：
- 许可证成本高
- 仅支持Cisco AP作为传感器
- 配置复杂

**配置示例**：

```bash
# Cisco WLC CLI配置wIPS
config wips ap enable all
config wips rogue-ap contain 7  # 遏制Rogue AP，发送7个反制客户端
config wips rogue-client contain 3
config wips rogue-report interval 60
show wips summary
show wips rogue-ap detailed <mac>
```

### 6.2 Aruba (HPE) RFProtect

**架构**：Aruba Mobility Controller + AP + RFProtect许可证

**核心功能**：
- WIDS/WIPS一体化
- 频谱分析
- 无线设备分类
- Rogue AP自动遏制
- 集成ClearPass进行策略控制

**优势**：
- AP混合模式（业务+监控）
- 与ClearPass深度集成
- 支持多厂商AP监控

**配置示例**：

```
# Aruba Mobility Controller配置
wids-profile "Corp-WIDS"
  rogue-ap-detection enable
  rogue-ap-contain enable
  spoof-detection enable
  deauth-flood-detection enable
  valid-ap-list "Corp-APs"  # 授权AP列表
ap-group "Corp-APs"
  wids-profile "Corp-WIDS"
  ap-mode air-monitor  # 部分AP专用监控模式
```

### 6.3 Fortinet FortiGate WiFi

**优势**：
- 集成在FortiGate防火墙中
- 有线无线一体化安全策略
- 支持FortiLink自动管理

### 6.4 方案对比表

| 特性 | Cisco wIPS | Aruba RFProtect | Fortinet |
|------|-----------|-----------------|----------|
| 架构 | 专用控制器 | 混合AP | 集成防火墙 |
| 传感器 | Cisco AP | Aruba AP | FortiAP |
| 频谱分析 | CleanAir | 集成 | 基础 |
| Rogue AP遏制 | 支持 | 支持 | 支持 |
| 三角定位 | 支持 | 支持 | 支持 |
| 身份关联 | ISE | ClearPass | FSSO |
| 价格 | 高 | 中高 | 中 |
| 多厂商支持 | 不支持 | 部分 | 不支持 |

---

---

## 📋 内容审核与补充建议

> 针对「商业WIDS方案对比」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
