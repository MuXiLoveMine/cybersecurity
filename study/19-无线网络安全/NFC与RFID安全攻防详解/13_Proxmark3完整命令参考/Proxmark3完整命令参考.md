# Proxmark3完整命令参考

### 13.1 Proxmark3 LF(125kHz)命令

```bash
# Proxmark3 LF命令参考

# --- HID卡操作 ---
lf hid read           # 读取HID卡(125kHz)
lf hid sim 2006     # 模拟HID卡(ID: 2006)
lf hid clone 2006    # 克隆HID卡到T5577

# --- EM410x操作 ---
lf em410x read       # 读取EM410x卡
lf em410x sim 0102030405  # 模拟EM410x
lf em410x clone 0102030405  # 克隆到T5577
lf em410x brute    # 暴力搜索EM410x ID

# --- T5577操作 ---
lf t55xx read        # 读取T5577卡所有数据块
lf t55xx write b 1 d 01020304  # 写入block 1
lf t55xx detect      # 检测T5577配置
lf t55xx wipe       # 擦除T5577

# --- 通用LF操作 ---
lf search            # 搜索所有已知LF卡类型
lf sniff             # 嗅探LF通信
lf sim              # 通用LF模拟
lf config           # 查看当前LF配置

# --- 侧信道 ---
lf offlineplot      # 离线侧信道分析图
```

### 13.2 Proxmark3 HF(13.56MHz)命令

```bash
# Proxmark3 HF命令参考

# --- ISO 14443-A ---
hf 14a info          # 查看卡片信息(UID/SAK/ATQA)
hf 14a reader        # 作为读卡器读取
hf 14a sim a         # 模拟Type A卡
hf 14a sim u         # 模拟未识别卡
hf 14a sim 2         # 模拟Mifare Classic 1K
hf 14a sim 3         # 模拟Mifare Classic 4K
hf 14a sim 4         # 模拟Mifare Ultralight
hf 14a sim 7         # 模拟Mifare DESFire
hf 14a snoop         # 嗅探ISO 14443通信
hf 14a raw           # 发送原始APDU

# --- Mifare Classic ---
hf mf fchk 0         # 检查Sector 0的密钥(所有默认)
hf mf fchk 0 A ffffffffffff  # 检查特定密钥
hf mf nested 0 A ffffffffffff  # 嵌套攻击
hf mf hardnested 0 A a  # Hardnested攻击
hf mf darkside       # Dark Side攻击
hf mf dump           # 转储所有扇区
hf mf restore f dump.bin  # 从文件恢复到卡片
hf mf elog           # 查看错误日志
hf mf rdbl 0 A ffffffffffff  # 读取特定块
hf mf wrbl 0 A ffffffffffff d 00112233445566778899aabbccddeeff  # 写入特定块
hf mf ekeyprn        # 打印所有扇区的密钥
hf mf csetuid 12345678  # 设置UID(Magic卡)

# --- Mifare Ultralight ---
hf mfu info          # 查看Ultralight信息
hf mfu dump          # 转储Ultralight数据
hf mfu restore       # 恢复Ultralight数据

# --- Mifare DESFire ---
hf 14a info          # 查看DESFire信息
hf mfdes getuid      # 获取DESFire UID
hf mfdes getapps     # 获取应用列表
hf mfdes getfiles    # 获取文件列表

# --- NFC NDEF ---
hf ndef read         # 读取NDEF消息
hf ndef write        # 写入NDEF消息

# --- 中继 ---
hf 14a srelayer      # 启动HF中继模式
# A设备: hf 14a srelayer
# B设备: hf 14a srelayee

# --- FeliCa ---
hf felica read       # 读取FeliCa卡

# --- 通用HF ---
hf search            # 搜索所有HF卡类型
hf list 14a          # 列出捕获的ISO14443通信
```

### 13.3 Proxmark3高级功能

```bash
# --- 嗅探模式 ---
# 实时嗅探读卡器和卡片之间的通信
hf 14a snoop         # 开始嗅探
# 停止后查看捕获数据:
hf list 14a          # 解析并显示通信记录

# --- 实时中继 ---
# 两个Proxmark3设备配合
# 设备A(靠近受害者卡):
hf 14a srelayer      # 作为中继主端
# 设备B(靠近读卡器):
hf 14a srelayee      # 作为中继从端

# --- 侧信道分析 ---
# 功耗分析(SCA)
lf offlineplot      # LF功耗图
power trace          # 功耗轨迹分析

# --- 固件更新 ---
# 更新Proxmark3固件
# 从https://github.com/RfidResearchGroup/proxmark3获取
pm3-flashboot firmware.elf  # 刷入引导程序
pm3-flashbl firmware.elf    # 刷入主固件

# --- 自定义脚本 ---
# Proxmark3支持Lua脚本
lua run script_name.lua
# 示例脚本:
lua run hf_read_all.lua   # 读取所有HF数据
lua run lf_read_all.lua   # 读取所有LF数据
```

---

---

## 📋 内容审核与补充建议

> 针对「Proxmark3完整命令参考」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
