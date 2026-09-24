# 线上CTF平台环境

### 3.1 主要线上平台介绍

#### 3.1.1 国外平台

**Hack The Box（HTB）**
- 网址：https://www.hackthebox.com
- 特点：最知名的渗透测试平台，靶机质量高，社区活跃
- 模式：单机渗透、挑战题、KotH、舰队
- 费用：免费版有限制，付费版无限制

**TryHackMe（THM）**
- 网址：https://tryhackme.com
- 特点：适合初学者，有完整学习路径，引导式教学
- 模式：学习房间、挑战房间、KotH
- 费用：免费版有限制，付费版功能更多

**CTFtime**
- 网址：https://ctftime.org
- 特点：CTF赛事日历和排名，汇总全球CTF比赛信息
- 模式：比赛信息聚合
- 费用：免费

**picoCTF**
- 网址：https://picoctf.org
- 特点：面向中学生和初学者，题目由浅入深
- 模式：解题模式
- 费用：免费

**OverTheWire**
- 网址：https://overthewire.org
- 特点：Wargame形式，循序渐进，适合练习Linux命令
- 模式：关卡式挑战
- 费用：免费

**CryptoHack**
- 网址：https://cryptohack.org
- 特点：专注密码学的CTF平台
- 模式：解题模式
- 费用：免费

#### 3.1.2 国内平台

**攻防世界（ADWorld）**
- 网址：https://adworld.xctf.org.cn
- 特点：XCTF官方平台，题目质量高，分类清晰
- 模式：新手练习区、高手进阶区、综合挑战区
- 费用：免费

**CTFHub**
- 网址：https://www.ctfhub.com
- 特点：题目量大，更新快，技能树系统完善
- 模式：技能树、赛事中心、题目中心
- 费用：免费

**Bugku**
- 网址：https://ctf.bugku.com
- 特点：老牌CTF平台，题目数量多
- 模式：解题模式、线上赛
- 费用：免费

**NSSCTF**
- 网址：https://www.nssctf.cn
- 特点：新兴平台，题目量大，有复现赛
- 模式：题目练习、比赛、特训
- 费用：免费

**实验吧**
- 网址：https://www.shiyanbar.com
- 特点：实验形式，适合系统学习
- 模式：实验、CTF、训练营
- 费用：部分免费

### 3.2 平台注册与使用

#### 3.2.1 通用注册流程

1. **访问平台官网**
2. **点击注册**：通常需要邮箱、用户名、密码
3. **验证邮箱**：部分平台需要邮箱验证
4. **完善信息**：填写个人资料（可选）
5. **开始使用**：进入题目列表开始练习

#### 3.2.2 平台使用技巧

1. **从简单题目开始**：不要一开始就挑战难题
2. **按分类练习**：系统性地学习某一类题目
3. **做不出来先看提示**：很多平台有提示功能
4. **查看Writeup**：实在做不出来可以看别人的解题思路
5. **记录错题**：整理不会的题目，定期复习
6. **参加比赛**：检验自己的真实水平

#### 3.2.3 常用平台详细使用指南

**Hack The Box 使用指南：**

1. **注册与邀请码**：
   - HTB注册需要邀请码
   - 可以在官网的邀请页面通过"hack"获取
   - 或者找已注册用户邀请

2. **连接VPN**：
   - 下载.ovpn配置文件
   - 使用OpenVPN连接
   - 连接后访问10.10.10.x网段的靶机

3. **选择靶机**：
   - 按难度筛选（Easy/Medium/Hard/Insane）
   - 查看评分和完成人数
   - 点击"Spawn Machine"启动靶机

4. **提交Flag**：
   - 找到user.txt和root.txt
   - 在靶机页面提交flag
   - 获得积分和排名

**攻防世界 使用指南：**

1. **新手区**：适合入门，有详细提示
2. **高手区**：难度较高，接近真实比赛
3. **每日一练**：每天更新一道题
4. **赛事中心**：线上比赛信息
5. **Writeup**：社区分享的解题报告

### 3.3 本地环境与平台对接

#### 3.3.1 VPN连接配置

很多CTF平台（如HTB、线下赛）需要通过VPN连接。

**OpenVPN客户端安装：**
```bash
# Kali Linux
sudo apt install openvpn

# Windows
# 下载安装：https://openvpn.net/community-downloads/

# Mac
brew install openvpn
```

**连接方法：**
```bash
# Linux
sudo openvpn --config your_config.ovpn

# 后台运行
sudo openvpn --config your_config.ovpn &
```

**常见问题排查：**
```bash
# 检查VPN连接状态
ip addr show tun0

# 测试连通性
ping 10.10.10.1

# 查看路由表
ip route

# 检查DNS
nslookup google.com
```

#### 3.3.2 代理配置

有些平台或比赛可能需要配置代理。

**系统代理配置：**
```bash
# 临时设置
export http_proxy=http://proxy:port
export https_proxy=http://proxy:port

# 永久设置（添加到~/.bashrc）
echo 'export http_proxy=http://proxy:port' >> ~/.bashrc
echo 'export https_proxy=http://proxy:port' >> ~/.bashrc
```

**Burp Suite代理配置：**
1. 启动Burp Suite
2. 设置监听端口（默认8080）
3. 浏览器配置代理指向Burp
4. 安装Burp的CA证书（用于HTTPS）

#### 3.3.3 工具链整合

将本地工具与线上平台结合使用：

1. **浏览器扩展**：
   - FoxyProxy：快速切换代理
   - Wappalyzer：识别Web技术栈
   - HackBar：Web渗透测试工具条
   - Cookie-Editor：Cookie管理

2. **脚本集成**：
   - 编写脚本批量提交flag
   - 使用API自动化操作
   - 集成到自己的工作流中

---

---

