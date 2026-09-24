# Linux网络配置

### 1.1 ip命令详解

`ip`命令来自`iproute2`包，是现代Linux网络配置的核心工具，取代了传统的`ifconfig`和`route`。

```bash
# 查看所有网络接口
ip addr show
ip a                    # 简写

# 查看指定接口
ip addr show eth0
ip a show eth0

# 查看链路状态
ip link show
ip link show eth0

# 启用/禁用接口
ip link set eth0 up     # 启用
ip link set eth0 down  # 禁用

# 配置IP地址
ip addr add 192.168.1.100/24 dev eth0
ip addr del 192.168.1.100/24 dev eth0

# 配置IPv6地址
ip addr add 2001:db8::1/64 dev eth0

# 查看路由表
ip route show
ip route get 8.8.8.8   # 查看到指定地址的路由

# 添加/删除路由
ip route add 10.0.0.0/24 via 192.168.1.1
ip route del 10.0.0.0/24 via 192.168.1.1

# 添加默认路由
ip route add default via 192.168.1.1

# 查看ARP表
ip neigh show
ip n show

# 查看多播地址
ip maddr show
```

### 1.2 ifconfig与route

虽然`ip`命令是推荐工具，但`ifconfig`和`route`仍在广泛使用。

```bash
# ifconfig基本用法
ifconfig                    # 查看所有接口
ifconfig eth0               # 查看指定接口
ifconfig eth0 up            # 启用接口
ifconfig eth0 down          # 禁用接口

# 配置IP地址
ifconfig eth0 192.168.1.100 netmask 255.255.255.0
ifconfig eth0 192.168.1.100/24      # CIDR格式

# 配置别名接口
ifconfig eth0:0 192.168.2.100/24

# 修改MAC地址（需root权限，接口需先down）
ifconfig eth0 down
ifconfig eth0 hw ether 00:11:22:33:44:55
ifconfig eth0 up

# route命令
route -n                    # 查看路由表（数字格式）
route add -net 10.0.0.0 netmask 255.255.255.0 gw 192.168.1.1
route add default gw 192.168.1.1
route del -net 10.0.0.0 netmask 255.255.255.0
```

### 1.3 NetworkManager

NetworkManager是现代Linux发行版的默认网络管理工具，提供动态网络配置。

```bash
# nmcli命令行工具
nmcli device status                 # 查看设备状态
nmcli device show eth0              # 查看设备详情
nmcli device connect eth0           # 连接设备
nmcli device disconnect eth0        # 断开设备

# 连接管理
nmcli connection show               # 查看所有连接
nmcli connection show "Wired connection 1"  # 查看连接详情

# 创建新连接
nmcli connection add type ethernet ifname eth0 con-name "eth0-static" ipv4.addresses 192.168.1.100/24 ipv4.gateway 192.168.1.1 ipv4.dns 8.8.8.8 ipv4.method manual

# 修改连接
nmcli connection modify "eth0-static" ipv4.addresses 192.168.1.200/24

# 启用/禁用连接
nmcli connection up "eth0-static"
nmcli connection down "eth0-static"

# WiFi管理
nmcli device wifi list             # 列出可用WiFi
nmcli device wifi connect "SSID" password "password"

# nmtui - 文本用户界面
nmtui                               # 交互式配置工具
```

### 1.4 网络接口绑定与聚合

```bash
# 配置网络绑定（Bonding）
# 模式：active-backup(1), balance-rr(0), 802.3ad(4)
modprobe bonding

# 创建bond接口
ip link add bond0 type bond
ip link set bond0 type bond miimon 100 mode 1
ip link set eth0 master bond0
ip link set eth1 master bond0
ip link set bond0 up

# 配置聚合（Teaming）
teamd -o -f /etc/teamd/team0.conf
# 配置文件示例
cat > /etc/teamd/team0.conf << EOF
{
    "device": "team0",
    "runner": {"name": "activebackup"},
    "link_watch": {"name": "ethtool"},
    "ports": {"eth0": {}, "eth1": {}}
}
EOF
```

---

---

