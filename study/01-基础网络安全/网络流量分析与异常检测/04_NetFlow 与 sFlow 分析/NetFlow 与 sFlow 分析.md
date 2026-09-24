# NetFlow 与 sFlow 分析

### 4.1 NetFlow 原理与版本

NetFlow 是 Cisco 提出的流记录技术。一条"流"由七元组唯一定义：源/目的 IP、源/目的端口、协议、TOS、入接口。设备把同一流的所有包聚合，流结束时输出一条记录，包含字节数、包数、起止时间等。

```
流记录字段(NetFlow v5):
  srcaddr  dstaddr  srcport  dstport  prot  dPkts  dOctets  first  last
  10.1.1.5 8.8.8.8  54321    53       17    10     780      1000   1005
```

**版本演进：**

| 版本 | 特点 | 现状 |
|------|------|------|
| v1 | 早期版本，字段少 | 已淘汰 |
| v5 | 最经典版本，固定字段32个 | 仍广泛使用 |
| v9 | 模板化，字段可扩展 | 现代 Cisco 默认 |
| IPFIX | IETF 标准（基于 v9） | 行业标准，未来主流 |

```
# Cisco 路由器配置 NetFlow v9
flow exporter EXPORTER1
 destination 192.168.10.50
 source Loopback0
 transport udp 2055
 template data timeout 60
!
flow monitor MONITOR1
 record netflow ipv4 original-input
 exporter EXPORTER1
 cache timeout active 60
 cache timeout inactive 15
!
interface GigabitEthernet0/0/1
 ip flow monitor MONITOR1 input
```

### 4.2 sFlow 原理与采样

sFlow 是基于采样的流技术（Sampled Flow）。设备按 1/N 比例随机采样数据包，只输出采样包的前 N 字节（含头部+部分载荷）给采集器。sFlow 优势是硬件实现、转发性能不降，适合超高速链路（40G/100G）。劣势是采样的，不能精确计费，不适合小流量精确分析。

```
# 华为交换机配置 sFlow
sflow agent ip 192.168.1.1
sflow collector 1 ip 192.168.10.50 port 6343
interface 10GE1/0/1
 sflow sampling rate 1000      # 每1000包采样1个
 sflow counter interval 30     # 每30秒上报计数器
```

### 4.3 流量采集工具

**nfdump/nfcapd：** 经典的 NetFlow 采集与查询工具。

```bash
# 启动 nfcapd 监听 2055 端口，数据存到 /var/nfdump
nfcapd -w -D -p 2055 -l /var/nfdump -I any

# 查询今日流量
nfdump -R /var/nfdump/ -t today

# 按源IP排序取TOP10
nfdump -r /var/nfdump/nfcapd.202609131200 -s srcip -n 10

# 查询某IP的所有流
nfdump -r nfcapd.current 'host 192.168.1.100'

# 统计某端口的流量
nfdump -r nfcapd.current 'port 443' -s port -n 20
```

**pmacct：** 支持多协议（NetFlow/sFlow/IPFIX）的流采集器，可输出到 Kafka、SQLite、MySQL。

```bash
# pmacct 配置示例 /etc/pmacct/pmacctd.conf
daemonize: true
pcap_interface: eth0
plugins: nfprobe
nfprobe_version: 9
nfprobe_receiver: 192.168.10.50:2055
aggregate: src_host, dst_host, src_port, dst_port, proto
```

**GoFlow：** Go 实现的高性能采集器，支持 NetFlow v5/v9/IPFIX/sFlow，可直接推送到 Kafka，适合大规模 ELK 栈。

```bash
# GoFlow 采集 sFlow 并推送到 Kafka
goflow -transport.type kafka -transport.kafka.brokers broker:9092 \
  -listen.sflow :6343 -listen.netflow :2055
```

### 4.4 流量分析工具

**Nfsen：** nfdump 的图形化前端，提供多端口实时监控、历史查询、告警。

**ElastiFlow：** 基于 ELK 的 NetFlow/IPFIX 分析平台，开箱即用的 Kibana 仪表盘，可视化 TOP 源/目的、协议分布、国家地图。

**VeloCloud/商业方案：** SD-WAN 厂商自带 NetFlow 分析能力，适合分支机构广域网。

### 4.5 NetFlow 与 sFlow 在安全分析中的应用

1. **DDoS 检测：** NetFlow 实时统计目的 IP 的入向包速/字节速，超阈值告警；可快速定位攻击源 IP 集合。
2. **横向移动发现：** 内网某主机突然对大量其他内网 IP 发起新端口连接，NetFlow 上表现为源 IP 的目的 IP 熵值突增。
3. **数据外泄量化：** 用 NetFlow 统计某主机对某外部 IP 的总出向字节数，量化外泄规模——这是全流量取证前的快速初判。
4. **影子资产发现：** 出现从未见过的目的 IP/端口，可能是影子 IT 或后门。

---

---

