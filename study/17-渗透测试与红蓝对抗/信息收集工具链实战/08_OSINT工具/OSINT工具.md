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

## 📋 内容审核与补充建议

> 针对「OSINT工具」部分的内容审核结果：

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
