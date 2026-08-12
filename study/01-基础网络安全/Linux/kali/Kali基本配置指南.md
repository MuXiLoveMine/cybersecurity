# Kali Linux 基本配置指南

> Kali Linux 是基于 Debian 的渗透测试和安全审计专用操作系统，预装了大量安全工具。本文档详细介绍 Kali 的安装、配置、优化和常用操作。

---

## 一、Kali Linux 简介

### 1.1 什么是 Kali Linux

Kali Linux 是由 Offensive Security 开发和维护的、基于 Debian GNU/Linux 的渗透测试和安全审计发行版。它预装了超过 600 个安全工具，是全球渗透测试人员和安全研究者最常用的操作系统之一。

**前身**：BackTrack（基于 Ubuntu）
**发布时间**：2013 年 3 月
**开发公司**：Offensive Security
**包管理**：APT（Debian 系）
**默认桌面**：Xfce（也提供 GNOME、KDE 等）

### 1.2 Kali 的特点

- **预装工具丰富**：600+ 安全工具，涵盖信息收集、漏洞分析、Web 应用、密码攻击、无线攻击、逆向工程、漏洞利用、取证、嗅探欺骗、压力测试等
- **滚动更新**：采用 Rolling Release 模式，持续更新
- **定制化内核**：支持无线注入、特殊驱动
- **多架构支持**：x86、x64、ARM、Android 等
- **开源免费**：完全开源，可自由使用
- **社区活跃**：全球最大的安全社区之一

### 1.3 适用场景

- 渗透测试（Penetration Testing）
- 安全审计（Security Audit）
- 漏洞研究（Vulnerability Research）
- 数字取证（Digital Forensics）
- 逆向工程（Reverse Engineering）
- 安全学习与研究

> ⚠️ **法律提醒**：Kali 中的工具只能在**合法授权**的环境下使用，未经授权对他人系统进行测试属于违法行为。

---

## 二、Kali 安装方式

### 2.1 虚拟机安装（推荐新手）

**推荐虚拟机软件**：
- VMware Workstation / Fusion
- VirtualBox（免费）
- Hyper-V（Windows 自带）

**安装步骤**：
1. 下载 Kali ISO 镜像：https://www.kali.org/get-kali/
2. 创建虚拟机，分配资源（建议 2 核 4G 内存以上）
3. 挂载 ISO，启动虚拟机
4. 选择 Graphical Install（图形化安装）
5. 按向导完成安装（语言、时区、分区、用户等）
6. 安装完成后重启

**虚拟机配置建议**：
- CPU：至少 2 核，推荐 4 核
- 内存：至少 2GB，推荐 4GB+
- 硬盘：至少 20GB，推荐 40GB+
- 网络：NAT 或桥接模式
- USB：开启 USB 3.0 支持（用于外接无线网卡）

### 2.2 物理机安装

适合需要完整硬件性能（如无线攻击、GPU 破解）的用户。

**注意事项**：
- 备份重要数据
- 准备 U 盘启动盘（推荐 Rufus、Etcher）
- 注意分区，避免覆盖其他系统
- 可与 Windows 双系统

### 2.3 WSL 安装（Windows Subsystem for Linux）

Windows 10/11 用户可通过 WSL 安装 Kali：

```powershell
# 以管理员身份打开 PowerShell
wsl --install -d kali-linux
```

安装完成后设置用户名密码即可使用。WSL 版 Kali 功能有限，部分工具（如无线攻击）无法使用。

### 2.4 其他安装方式

- **Kali Live**：U 盘启动，不安装到硬盘
- **Kali NetHunter**：Android 手机上运行 Kali
- **Docker 镜像**：`docker pull kalilinux/kali-rolling`
- **云服务器**：AWS、Azure 等云平台提供 Kali 镜像

---

## 三、首次启动配置

### 3.1 登录系统

默认安装后，使用安装时创建的普通用户登录。Kali 默认禁用 root 登录（2020.1 版本后）。

**切换 root**：
```bash
sudo su -
# 或
sudo -i
```

**设置 root 密码**（不推荐，建议用 sudo）：
```bash
sudo passwd root
```

### 3.2 检查系统版本

```bash
# 查看 Kali 版本
cat /etc/os-release

# 查看内核版本
uname -a

# 查看系统架构
uname -m

# 查看 Kali 版本号
grep VERSION /etc/os-release
```

### 3.3 网络配置

**查看网络信息**：
```bash
ip addr
# 或
ifconfig

# 查看路由
ip route
# 或
route -n

# 查看 DNS
cat /etc/resolv.conf
```

**配置静态 IP**（编辑 /etc/network/interfaces）：
```bash
sudo nano /etc/network/interfaces
```

添加以下内容：
```
auto eth0
iface eth0 inet static
    address 192.168.1.100
    netmask 255.255.255.0
    gateway 192.168.1.1
    dns-nameservers 8.8.8.8 114.114.114.114
```

重启网络：
```bash
sudo systemctl restart networking
```

**使用 NetworkManager（图形界面推荐）**：
```bash
# 查看连接
nmcli connection show

# 配置静态 IP
nmcli connection modify "Wired connection 1" ipv4.addresses 192.168.1.100/24
nmcli connection modify "Wired connection 1" ipv4.gateway 192.168.1.1
nmcli connection modify "Wired connection 1" ipv4.dns "8.8.8.8,114.114.114.114"
nmcli connection modify "Wired connection 1" ipv4.method manual
nmcli connection up "Wired connection 1"
```

### 3.4 时区和语言配置

**设置时区**：
```bash
sudo dpkg-reconfigure tzdata
# 选择 Asia → Shanghai
```

**设置中文语言**：
```bash
sudo dpkg-reconfigure locales
# 勾选 zh_CN.UTF-8 UTF-8
# 选择默认语言 zh_CN.UTF-8
```

安装中文字体：
```bash
sudo apt install -y fonts-wqy-microhei fonts-wqy-zenhei
```

---

## 四、软件源配置

### 4.1 默认官方源

Kali 默认使用官方源，国内访问可能较慢：

```bash
cat /etc/apt/sources.list
```

默认内容：
```
deb http://http.kali.org/kali kali-rolling main non-free contrib
deb-src http://http.kali.org/kali kali-rolling main non-free contrib
```

### 4.2 配置国内镜像源（推荐）

**备份原源**：
```bash
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak
```

**阿里云源**：
```bash
sudo tee /etc/apt/sources.list << 'EOF'
deb https://mirrors.aliyun.com/kali kali-rolling main non-free contrib
deb-src https://mirrors.aliyun.com/kali kali-rolling main non-free contrib
EOF
```

**清华大学源**：
```bash
sudo tee /etc/apt/sources.list << 'EOF'
deb https://mirrors.tuna.tsinghua.edu.cn/kali kali-rolling main non-free contrib
deb-src https://mirrors.tuna.tsinghua.edu.cn/kali kali-rolling main non-free contrib
EOF
```

**中科大源**：
```bash
sudo tee /etc/apt/sources.list << 'EOF'
deb https://mirrors.ustc.edu.cn/kali kali-rolling main non-free contrib
deb-src https://mirrors.ustc.edu.cn/kali kali-rolling main non-free contrib
EOF
```

**浙江大学源**：
```bash
sudo tee /etc/apt/sources.list << 'EOF'
deb https://mirrors.zju.edu.cn/kali kali-rolling main contrib non-free
deb-src https://mirrors.zju.edu.cn/kali kali-rolling main contrib non-free
EOF
```

> 💡 选择一个速度最快的源即可，不需要全部添加。

### 4.3 更新系统

配置好源后，更新系统：

```bash
# 更新软件包列表
sudo apt update

# 升级已安装的软件包
sudo apt upgrade -y

# 升级系统（包括内核等，可能会移除某些包）
sudo apt full-upgrade -y

# 清理无用的包
sudo apt autoremove -y
sudo apt clean
```

> ⚠️ Kali 是滚动更新，`apt update && apt upgrade` 即可保持最新。`full-upgrade` 可能会移除冲突的包，使用时注意。

### 4.4 常见 APT 命令

```bash
# 搜索软件包
apt search 关键词

# 查看软件包信息
apt show 包名

# 安装软件
sudo apt install 包名

# 卸载软件（保留配置）
sudo apt remove 包名

# 卸载软件（删除配置）
sudo apt purge 包名

# 查看已安装的包
dpkg -l

# 查看文件属于哪个包
dpkg -S 文件路径

# 修复依赖
sudo apt --fix-broken install

# 清理缓存
sudo apt clean
sudo apt autoclean
```

---

## 五、常用工具安装

### 5.1 Kali 工具集分类

Kali 预装工具按类别分为：

| 类别 | 说明 | 代表工具 |
|------|------|----------|
| 信息收集 | 侦察、枚举 | Nmap、Recon-ng、theHarvester |
| 漏洞分析 | 漏洞扫描、分析 | OpenVAS、Nikto、Nessus |
| Web 应用 | Web 渗透 | Burp Suite、SQLMap、OWASP ZAP |
| 密码攻击 | 密码破解 | Hashcat、John、Hydra |
| 无线攻击 | 无线网络 | Aircrack-ng、Reaver、Wifite |
| 逆向工程 | 逆向分析 | IDA、Ghidra、radare2 |
| 漏洞利用 | 漏洞利用 | Metasploit、Searchsploit |
| 嗅探欺骗 | 网络嗅探 | Wireshark、Ettercap、Bettercap |
| 后渗透 | 内网渗透 | Mimikatz、PowerSploit |
| 取证 | 数字取证 | Autopsy、Volatility、Binwalk |
| 报告工具 | 报告生成 | Dradis、Faraday |

### 5.2 安装完整工具集

Kali 默认安装的是常用工具，如需安装全部工具：

```bash
# 安装所有 Kali 工具（约 10GB+，不推荐新手）
sudo apt install kali-linux-everything

# 安装大型工具集
sudo apt install kali-linux-large

# 安装默认工具集
sudo apt install kali-linux-default
```

### 5.3 按类别安装工具

```bash
# Web 渗透工具
sudo apt install kali-linux-web

# 密码攻击工具
sudo apt install kali-linux-passwords

# 无线攻击工具
sudo apt install kali-linux-wireless

# 逆向工程工具
sudo apt install kali-linux-reverse-engineering

# 取证工具
sudo apt install kali-linux-forensics

# 漏洞利用工具
sudo apt install kali-linux-exploitation

# 信息收集工具
sudo apt install kali-linux-information-gathering

# 嗅探欺骗工具
sudo apt install kali-linux-sniffing-spoofing
```

### 5.4 常用额外工具安装

```bash
# 文本编辑器
sudo apt install -y vim nano

# 网络工具
sudo apt install -y net-tools dnsutils traceroute tcpdump

# 下载工具
sudo apt install -y wget curl axel

# 压缩工具
sudo apt install -y p7zip-full unrar zip unzip

# 系统监控
sudo apt install -y htop netcat-openbsd

# Git
sudo apt install -y git

# Python 相关
sudo apt install -y python3 python3-pip python3-venv

# 浏览器
sudo apt install -y firefox-esr chromium

# 中文输入法
sudo apt install -y fcitx fcitx-googlepinyin

# 截图工具
sudo apt install -y flameshot

# 文件管理器增强
sudo apt install -y thunar
```

### 5.5 安装 Burp Suite 专业版

Kali 预装 Burp Suite 社区版，专业版需要自行安装：

1. 下载 Burp Suite Professional：https://portswigger.net/burp
2. 赋予执行权限：`chmod +x burpsuite_pro_linux.sh`
3. 运行安装：`./burpsuite_pro_linux.sh`
4. 按向导完成安装

---

## 六、服务配置

### 6.1 SSH 服务

**安装 SSH**（Kali 默认已安装）：
```bash
sudo apt install -y openssh-server
```

**启动 SSH**：
```bash
sudo systemctl start ssh
```

**设置开机自启**：
```bash
sudo systemctl enable ssh
```

**查看 SSH 状态**：
```bash
sudo systemctl status ssh
```

**配置 SSH**（允许 root 登录，不推荐）：
```bash
sudo nano /etc/ssh/sshd_config
```

修改：
```
PermitRootLogin yes
PasswordAuthentication yes
```

重启 SSH：
```bash
sudo systemctl restart ssh
```

**测试 SSH**：
```bash
ssh 用户名@IP地址
```

> ⚠️ 生产环境中建议禁用 root 登录、禁用密码登录、使用密钥登录。

### 6.2 Apache Web 服务

**安装 Apache**：
```bash
sudo apt install -y apache2
```

**启动 Apache**：
```bash
sudo systemctl start apache2
sudo systemctl enable apache2
```

**网站根目录**：`/var/www/html/`

**测试**：浏览器访问 `http://localhost`

### 6.3 MySQL/MariaDB 服务

**安装 MariaDB**：
```bash
sudo apt install -y mariadb-server
```

**启动 MariaDB**：
```bash
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

**安全配置**：
```bash
sudo mysql_secure_installation
```

**登录 MySQL**：
```bash
sudo mysql -u root -p
```

### 6.4 PostgreSQL 服务（Metasploit 需要）

**安装 PostgreSQL**：
```bash
sudo apt install -y postgresql postgresql-contrib
```

**启动 PostgreSQL**：
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**配置 Metasploit 数据库**：
```bash
# 启动 PostgreSQL
sudo systemctl start postgresql

# 初始化 Metasploit 数据库
msfdb init

# 启动 msfconsole
msfconsole
```

在 msfconsole 中检查数据库连接：
```
msf6 > db_status
```

---

## 七、桌面环境优化

### 7.1 Kali 默认桌面环境

Kali 默认使用 Xfce 桌面环境，轻量快速。

**切换桌面环境**：
```bash
# 安装 GNOME
sudo apt install -y kali-desktop-gnome

# 安装 KDE
sudo apt install -y kali-desktop-kde

# 安装 Xfce（默认）
sudo apt install -y kali-desktop-xfce

# 安装 LXDE
sudo apt install -y kali-desktop-lxde

# 安装 MATE
sudo apt install -y kali-desktop-mate
```

安装后在登录界面选择桌面环境。

### 7.2 常用桌面工具

```bash
# 终端增强
sudo apt install -y terminator tilix

# 系统监控
sudo apt install -y conky

# 主题美化
sudo apt install -y numix-gtk-theme numix-icon-theme

# 右键增强
sudo apt install -y thunar-archive-plugin
```

### 7.3 中文输入法配置

**安装 fcitx 谷歌拼音**：
```bash
sudo apt install -y fcitx fcitx-googlepinyin fcitx-configtool
```

**配置环境变量**：
```bash
echo 'export GTK_IM_MODULE=fcitx' >> ~/.xprofile
echo 'export QT_IM_MODULE=fcitx' >> ~/.xprofile
echo 'export XMODIFIERS=@im=fcitx' >> ~/.xprofile
```

注销重新登录，运行 `fcitx-configtool` 添加输入法。

### 7.4 终端配置

**安装 zsh 和 oh-my-zsh**（可选）：
```bash
sudo apt install -y zsh
chsh -s $(which zsh)

# 安装 oh-my-zsh
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

**常用终端快捷键**：
- `Ctrl + Shift + T`：新建标签页
- `Ctrl + Shift + C`：复制
- `Ctrl + Shift + V`：粘贴
- `Ctrl + L`：清屏
- `Ctrl + C`：终止当前命令
- `Ctrl + Z`：挂起当前命令
- `Tab`：自动补全
- `↑ / ↓`：历史命令

---

## 八、安全配置

### 8.1 用户与权限

**创建新用户**：
```bash
sudo adduser 用户名
sudo usermod -aG sudo 用户名  # 添加到 sudo 组
```

**修改密码**：
```bash
passwd  # 修改当前用户密码
sudo passwd 用户名  # 修改指定用户密码
```

**查看用户**：
```bash
cat /etc/passwd
whoami
id
```

### 8.2 防火墙配置

Kali 默认使用 iptables/nftables，也可安装 ufw：

```bash
sudo apt install -y ufw

# 启用防火墙
sudo ufw enable

# 允许 SSH
sudo ufw allow ssh

# 允许特定端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 查看状态
sudo ufw status verbose

# 禁用防火墙
sudo ufw disable
```

### 8.3 关闭不必要的服务

```bash
# 查看监听端口
sudo ss -tlnp
# 或
sudo netstat -tlnp

# 禁用不需要的服务
sudo systemctl disable 服务名
sudo systemctl stop 服务名
```

### 8.4 安全更新

```bash
# 定期更新
sudo apt update && sudo apt upgrade -y

# 安装安全更新
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 8.5 虚拟机安全

- 不要在虚拟机中保存敏感信息
- 定期快照，出问题可恢复
- 网络模式建议 NAT，避免暴露到局域网
- 不要将主机重要文件夹共享给虚拟机

---

## 九、常用命令速查

### 9.1 系统命令

```bash
# 系统信息
uname -a          # 内核信息
cat /etc/os-release  # 系统版本
lsb_release -a    # 发行版信息
hostname          # 主机名

# 硬件信息
lscpu             # CPU 信息
free -h           # 内存信息
df -h             # 磁盘信息
lsblk             # 块设备
lspci             # PCI 设备
lsusb             # USB 设备

# 进程管理
ps aux            # 查看所有进程
top               # 实时进程监控
htop              # 增强版 top
kill PID          # 终止进程
kill -9 PID       # 强制终止
pkill 进程名      # 按名称终止

# 服务管理
systemctl start 服务名    # 启动服务
systemctl stop 服务名     # 停止服务
systemctl restart 服务名  # 重启服务
systemctl status 服务名   # 查看状态
systemctl enable 服务名   # 开机自启
systemctl disable 服务名  # 取消自启
```

### 9.2 文件命令

```bash
# 目录操作
pwd               # 当前目录
cd 目录           # 切换目录
ls                # 列出文件
ls -la            # 详细列表
mkdir 目录名      # 创建目录
mkdir -p a/b/c    # 递归创建

# 文件操作
touch 文件名      # 创建空文件
cp 源 目标        # 复制
mv 源 目标        # 移动/重命名
rm 文件名         # 删除文件
rm -rf 目录       # 递归删除目录（危险！）
cat 文件名        # 查看文件内容
less 文件名       # 分页查看
head -n 10 文件名  # 查看前 10 行
tail -n 10 文件名  # 查看后 10 行
tail -f 文件名    # 实时跟踪

# 权限
chmod 755 文件名   # 修改权限
chown 用户:组 文件  # 修改所有者
chmod +x 文件名    # 添加执行权限

# 查找
find / -name "文件名"  # 按名称查找
grep "关键词" 文件     # 在文件中搜索
grep -r "关键词" 目录  # 递归搜索
locate 文件名          # 快速查找（需 updatedb）
```

### 9.3 网络命令

```bash
# 网络信息
ip addr           # 网卡信息
ip route          # 路由表
ifconfig          # 传统网卡信息
ping 目标         # 测试连通性
traceroute 目标   # 路由跟踪
mtr 目标          # 组合 ping+traceroute

# 端口与连接
ss -tlnp          # 监听端口
netstat -tlnp     # 监听端口（传统）
ss -tunap         # 所有连接
lsof -i :端口     # 查看端口占用

# DNS
nslookup 域名     # DNS 查询
dig 域名          # DNS 查询
host 域名         # DNS 查询
cat /etc/resolv.conf  # DNS 配置

# 下载
wget URL          # 下载文件
curl URL          # 获取网页内容
curl -O URL       # 下载文件
axel -n 10 URL    # 多线程下载

# 远程连接
ssh 用户@IP       # SSH 登录
scp 文件 用户@IP:路径  # SCP 传输
rsync -av 源 目标  # 同步文件
```

### 9.4 压缩解压

```bash
# tar
tar -cvf 包.tar 文件/目录    # 打包
tar -xvf 包.tar              # 解包
tar -zcvf 包.tar.gz 文件     # 打包并 gzip 压缩
tar -zxvf 包.tar.gz          # 解压 gzip
tar -jcvf 包.tar.bz2 文件    # 打包并 bzip2 压缩
tar -jxvf 包.tar.bz2         # 解压 bzip2
tar -Jcvf 包.tar.xz 文件     # 打包并 xz 压缩
tar -Jxvf 包.tar.xz          # 解压 xz

# zip
zip -r 包.zip 文件/目录      # 压缩
unzip 包.zip                 # 解压

# 7z
7z a 包.7z 文件/目录         # 压缩
7z x 包.7z                   # 解压

# rar
unrar x 包.rar               # 解压
```

### 9.5 包管理

```bash
apt update          # 更新软件源
apt upgrade         # 升级软件
apt install 包名    # 安装
apt remove 包名     # 卸载
apt purge 包名      # 卸载并删除配置
apt search 关键词   # 搜索
apt show 包名       # 查看详情
apt autoremove      # 清理无用依赖
apt clean           # 清理缓存
dpkg -i 包.deb      # 安装 deb 包
dpkg -l             # 列出已安装包
```

---

## 十、Kali 常用工具快速上手

### 10.1 Nmap（端口扫描）

```bash
# 基本扫描
nmap 目标IP

# 扫描指定端口
nmap -p 80,443,3306 目标IP

# 全端口扫描
nmap -p- 目标IP

# 服务版本探测
nmap -sV 目标IP

# 操作系统探测
nmap -O 目标IP

# 综合扫描
nmap -A 目标IP

# 快速扫描
nmap -T4 -F 目标IP

# 保存结果
nmap -oN result.txt 目标IP
```

### 10.2 Metasploit（漏洞利用框架）

```bash
# 启动
msfconsole

# 搜索模块
search 关键词

# 使用模块
use 模块路径

# 查看选项
show options

# 设置选项
set RHOSTS 目标IP
set LHOST 本机IP

# 执行
exploit
# 或
run
```

### 10.3 SQLMap（SQL 注入）

```bash
# 基本检测
sqlmap -u "http://目标/page?id=1"

# 获取数据库
sqlmap -u "URL" --dbs

# 获取表
sqlmap -u "URL" -D 数据库名 --tables

# 获取列
sqlmap -u "URL" -D 数据库名 -T 表名 --columns

# 获取数据
sqlmap -u "URL" -D 数据库名 -T 表名 --dump

# POST 数据
sqlmap -u "URL" --data "id=1"

# Cookie
sqlmap -u "URL" --cookie "id=1"
```

### 10.4 Hashcat（密码破解）

```bash
# 查看帮助
hashcat --help

# 破解 MD5
hashcat -m 0 hash.txt wordlist.txt

# 破解 SHA1
hashcat -m 100 hash.txt wordlist.txt

# 破解 NTLM
hashcat -m 1000 hash.txt wordlist.txt

# 查看破解结果
hashcat -m 0 hash.txt --show

# 掩码攻击
hashcat -m 0 hash.txt -a 3 ?d?d?d?d?d?d
```

### 10.5 Wireshark（抓包分析）

```bash
# 启动
wireshark &

# 命令行抓包
tcpdump -i eth0 -w capture.pcap
tcpdump -i eth0 port 80
tcpdump -i eth0 host 192.168.1.1
```

### 10.6 Aircrack-ng（无线攻击）

```bash
# 查看无线网卡
iwconfig

# 启用监控模式
sudo airmon-ng start wlan0

# 扫描附近 WiFi
sudo airodump-ng wlan0mon

# 抓取握手包
sudo airodump-ng -c 信道 --bssid MAC -w output wlan0mon

# 破解 WPA2
sudo aircrack-ng -w wordlist.txt output-01.cap

# 关闭监控模式
sudo airmon-ng stop wlan0mon
```

> ⚠️ 无线攻击需要支持监控模式的无线网卡，且只能在授权网络上测试。

---

## 十一、常见问题与故障排查

### 11.1 软件源问题

**问题：apt update 报错**

排查步骤：
```bash
# 检查网络
ping mirrors.aliyun.com

# 检查源配置
cat /etc/apt/sources.list

# 更换其他源
# 清理缓存重试
sudo apt clean
sudo apt update
```

**问题：GPG 密钥错误**
```bash
# 导入缺失的密钥
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 密钥ID

# 或重新下载 Kali 密钥
wget -q -O - https://archive.kali.org/archive-key.asc | sudo apt-key add
```

### 11.2 网络问题

**问题：无法上网**
```bash
# 检查网卡
ip addr

# 检查路由
ip route

# 检查 DNS
cat /etc/resolv.conf
ping 8.8.8.8
ping www.baidu.com

# 重启网络
sudo systemctl restart NetworkManager
```

**问题：虚拟机无法联网**
- 检查虚拟机网络模式（NAT/桥接）
- 检查虚拟网卡是否启用
- 重启网络服务
- 检查主机网络是否正常

### 11.3 工具运行问题

**问题：命令找不到**
```bash
# 搜索工具是否安装
apt search 工具名

# 安装工具
sudo apt install 工具名

# 检查 PATH
echo $PATH

# 用完整路径运行
/usr/bin/工具名
```

**问题：权限不足**
```bash
# 使用 sudo
sudo 命令

# 切换 root
sudo su -
```

**问题：依赖缺失**
```bash
# 修复依赖
sudo apt --fix-broken install

# 更新系统
sudo apt update && sudo apt upgrade -y
```

### 11.4 系统启动问题

**问题：开机黑屏**
- 检查虚拟机显示设置
- 尝试切换 TTY：`Ctrl + Alt + F1`
- 检查显卡驱动
- 恢复模式启动

**问题：忘记密码**
1. 重启，在 GRUB 菜单按 `e`
2. 找到 `linux` 行，在末尾添加 `init=/bin/bash`
3. 按 `Ctrl + X` 启动
4. 挂载根分区：`mount -o remount,rw /`
5. 修改密码：`passwd 用户名`
6. 重启：`exec /sbin/init`

### 11.5 磁盘空间不足

```bash
# 查看磁盘使用
df -h

# 清理 apt 缓存
sudo apt clean
sudo apt autoclean
sudo apt autoremove

# 清理日志
sudo journalctl --vacuum-size=100M

# 查找大文件
sudo find / -type f -size +100M -exec ls -lh {} \;

# 清理 /tmp
sudo rm -rf /tmp/*
```

---

## 十二、学习资源

### 12.1 官方资源

- [Kali Linux 官网](https://www.kali.org/)
- [Kali Linux 文档](https://www.kali.org/docs/)
- [Kali Linux 工具列表](https://www.kali.org/tools/)
- [Kali Linux 论坛](https://forums.kali.org/)
- [Kali Linux Bug Tracker](https://bugs.kali.org/)

### 12.2 推荐书籍

- 《Kali Linux 渗透测试指南》
- 《Kali Linux 高级渗透测试》
- 《Metasploit 渗透测试指南》
- 《黑客攻防技术宝典》
- 《内网安全攻防》

### 12.3 视频课程

- B 站搜索「Kali 教程」「Kali 渗透测试」
- Kali Linux 100 集入门（BV1Qcj1zTE44）
- 零基础也能学 kali 2025 最好懂的 Kali 渗透测试全套教程（BV1fYJizNE7m）
- 【全 236 集】kali 渗透零基础全套教程 2026 最新版（BV13HqcBmE1x）

### 12.4 实践平台

- [Hack The Box](https://www.hackthebox.com/)
- [TryHackMe](https://tryhackme.com/)
- [VulnHub](https://www.vulnhub.com/)
- [攻防世界](https://adworld.xctf.org/)
- [CTFHub](https://www.ctfhub.com/)

---

## 十三、Kali 使用注意事项

### 13.1 法律合规

- ✅ 只在**自己的系统**或**获得书面授权**的系统上测试
- ✅ 在虚拟机、靶场、CTF 平台练习
- ❌ 不要攻击任何未授权的系统
- ❌ 不要用 Kali 做违法的事情
- ❌ 不要在公共网络随意扫描

### 13.2 安全习惯

- 定期更新系统：`sudo apt update && sudo apt upgrade`
- 不使用 root 日常操作，用 sudo
- 重要数据做好备份
- 虚拟机定期快照
- 下载的工具先查毒再运行
- 不随意添加第三方软件源

### 13.3 学习建议

1. **先学 Linux 基础**：命令行、文件系统、权限、网络
2. **再学网络基础**：TCP/IP、HTTP、DNS、路由交换
3. **然后学安全工具**：Nmap、Burp、Metasploit 等
4. **多动手实践**：打靶场、做 CTF、复现漏洞
5. **持续学习**：安全领域更新快，保持学习

---

> 💡 **Kali 只是工具，真正的能力在于你的知识和思维。学好 Linux 基础和网络基础，再配合 Kali 的工具，才能发挥最大价值。合法使用，安全第一！**
