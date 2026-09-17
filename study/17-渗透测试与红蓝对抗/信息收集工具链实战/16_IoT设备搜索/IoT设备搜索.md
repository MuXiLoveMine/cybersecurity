# IoT设备搜索

### 15.1 Shodan高级搜索

```bash
# Shodan CLI安装
pip install shodan

# 初始化API Key
shodan init YOUR_API_KEY

# 基本搜索
shodan search "apache"
shodan search "country:CN port:80"

# 搜索特定设备
shodan search "product:nginx country:US"
shodan search "product:Apache city:Beijing"

# 搜索特定端口
shodan search "port:22 country:CN"
shodan search "port:3389 country:US"

# 搜索摄像头
shodan search "webcam"
shodan search "product:webcam city:Beijing"

# 搜索工控系统(ICS)
shodan search "port:502"  # Modbus
shodan search "port:47808"  # BACnet
shodan search "port:2404"  # IEC 60870-5-104
shodan search "port:20000"  # DNP3

# 搜索数据库
shodan search "product:MongoDB port:27017"
shodan search "product:Elasticsearch port:9200"
shodan search "product:Redis port:6379"
shodan search "product:MySQL port:3306"

# 搜索路由器
shodan search "product:nginx hostname:router"

# Shodan搜索语法
# - country: 国家代码
# - city: 城市名
# - port: 端口号
# - product: 产品名
# - version: 版本号
# - hostname: 主机名
# - os: 操作系统
# - org: 组织名
# - net: CIDR网段
# - before/after: 时间过滤

# 使用Facets获取统计信息
shodan search "apache" --facets country,product,version --limit 0
shodan stats "country:CN port:80" --facets country,product,os,version
```

### 15.2 Censys搜索

```bash
# Censys CLI
pip install censys

# 配置API
censys config

# 搜索
censys search "80.http.get.title: \"Welcome\""
censys search "80.http.get.headers.server: nginx"

# 搜索特定证书
censys search "parsed.names: example.com"
censys search "parsed.issuer.organization: Let's Encrypt"

# 搜索特定服务
censys search "services.port: 443 and services.service_name: HTTPS"
censys search "services.software.product: nginx"

# 查看主机详情
censys view 1.2.3.4
```

### 15.3 ZoomEye搜索

```bash
# ZoomEye CLI (钟馗之眼)
pip install zoomeye

# 初始化
zoomeye init -key YOUR_API_KEY

# 搜索设备
zoomeye search "apache" -type host
zoomeye search "nginx" -type web

# 搜索特定组件
zoomeye search "app:Apache" -type host
zoomeye search "app:nginx" -type web

# 搜索特定端口
zoomeye search "port:22" -type host
zoomeye search "port:80" -type host

# 搜索特定国家
zoomeye search "port:80 country:CN" -type host

# 搜索工控设备
zoomeye search "port:502" -type host  # Modbus
zoomeye search "port:2404" -type host  # IEC 104

# 搜索Web摄像头
zoomeye search "device:webcam" -type host
```

### 15.4 FOFA搜索

```bash
# FOFA搜索语法
# - title="后台管理"
# - body="登录"
# - ip="1.1.1.1"
# - port="8080"
# - protocol="https"
# - server="Apache"
# - header="Set-Cookie"
# - domain="example.com"
# - host="example.com"
# - cert="example.com"
# - icon_hash="-123456789"

# FOFA API
curl "https://fofa.info/api/v1/search/all?email=YOUR_EMAIL&key=YOUR_KEY&qbase64=$(echo -n 'title=\"test\"' | base64)"
```

---

---

## 📋 内容审核与补充建议

> 针对「IoT设备搜索」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
