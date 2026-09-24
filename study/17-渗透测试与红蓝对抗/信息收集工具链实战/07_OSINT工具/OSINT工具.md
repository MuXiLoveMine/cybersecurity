# OSINT工具

### 7.1 theHarvester

```bash
# theHarvester - 邮箱/子域名/人员信息收集
# 安装
pip install theHarvester

# 基本使用
theHarvester -d example.com -l 500 -b all

# 指定数据源
theHarvester -d example.com -b google,bing,yahoo,linkedin
theHarvester -d example.com -b shodan
theHarvester -d example.com -b crtsh

# 输出
theHarvester -d example.com -b all -f results.html

# 收集类型:
# - 邮箱地址
# - 子域名
# - IP地址
# - 员工姓名
# - LinkedIn资料
```

### 7.2 Maltego

```
Maltego - 图形化OSINT分析工具

功能:
  - 域名 -> DNS记录 -> IP -> 反向DNS -> 关联域名
  - 邮箱 -> 社交媒体 -> 组织信息
  - 人员 -> 公司 -> 关联人员
  - IP -> 地理位置 -> ASN -> 网段

使用流程:
  1. 启动Maltego Community Edition
  2. 创建新图谱
  3. 添加实体(域名/IP/邮箱/人名)
  4. 运行Transform(转换)
  5. 分析关联关系
  6. 导出图谱

常用Transform:
  - DNS解析
  - 反向DNS
  - Whois查询
  - 邮箱收集
  - LinkedIn搜索
  - 社交媒体查找
  - 网页链接分析
```

---

---

