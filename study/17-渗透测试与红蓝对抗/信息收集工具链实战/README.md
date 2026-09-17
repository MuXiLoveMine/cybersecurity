# 信息收集工具链实战

> 本文档整理自：`信息收集工具链实战.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 信息收集概述](./02_信息收集概述/信息收集概述.md)
  - 信息收集分类
  - 信息收集方法论

### [03. 被动侦察](./03_被动侦察/被动侦察.md)
  - Whois查询
  - Shodan搜索
  - Censys搜索
  - 证书透明日志(crt.sh)
  - GitHub Dorking

### [04. 主动侦察](./04_主动侦察/主动侦察.md)
  - Nmap
  - Masscan
  - Naabu

### [05. 子域名枚举](./05_子域名枚举/子域名枚举.md)
  - Subfinder
  - Amass
  - httpx

### [06. Web指纹识别](./06_Web指纹识别/Web指纹识别.md)
  - Wappalyzer
  - whatweb

### [07. 目录爆破](./07_目录爆破/目录爆破.md)
  - ffuf
  - dirsearch

### [08. OSINT工具](./08_OSINT工具/OSINT工具.md)
  - theHarvester
  - Maltego

### [09. 信息收集自动化](./09_信息收集自动化/信息收集自动化.md)

### [10. 子域名接管检测](./10_子域名接管检测/子域名接管检测.md)
  - 子域名接管原理
  - subjack - 子域名接管扫描
  - nuclei子域名接管模板

### [11. 云存储桶发现与枚举](./11_云存储桶发现与枚举/云存储桶发现与枚举.md)
  - AWS S3存储桶发现
  - 其他云存储枚举

### [12. GitHub信息泄露搜索](./12_GitHub信息泄露搜索/GitHub信息泄露搜索.md)
  - GitHub Dorking高级技巧
  - GitHub搜索自动化脚本

### [13. Docker镜像信息泄露](./13_Docker镜像信息泄露/Docker镜像信息泄露.md)
  - Docker镜像敏感信息检测
  - Docker Hub公开镜像搜索

### [14. 社工信息收集](./14_社工信息收集/社工信息收集.md)
  - 社交媒体信息收集
  - 邮箱信息收集
  - 人员信息收集与OSINT关联

### [15. 移动APP信息收集](./15_移动APP信息收集/移动APP信息收集.md)
  - APK逆向信息收集
  - iOS应用信息收集
  - APP网络请求抓取

### [16. IoT设备搜索](./16_IoT设备搜索/IoT设备搜索.md)
  - Shodan高级搜索
  - Censys搜索
  - ZoomEye搜索
  - FOFA搜索

### [17. 自动化信息收集框架](./17_自动化信息收集框架/自动化信息收集框架.md)
  - Recon-ng
  - AutoRecon
  - 综合自动化框架对比
  - SpiderFoot

### [18. 信息收集报告模板](./18_信息收集报告模板/信息收集报告模板.md)
  - 信息收集报告结构

### [19. 目标概述](./19_目标概述/目标概述.md)

### [20. 被动侦察结果](./20_被动侦察结果/被动侦察结果.md)
  - Whois信息
  - DNS记录
  - 子域名列表

### [21. 主动侦察结果](./21_主动侦察结果/主动侦察结果.md)
  - 开放端口
  - Web指纹

### [22. 漏洞发现](./22_漏洞发现/漏洞发现.md)
  - 子域名接管
  - 敏感信息泄露

### [23. 攻击面分析](./23_攻击面分析/攻击面分析.md)
  - 外部攻击面
  - 高风险发现

### [24. 下一步建议](./24_下一步建议/下一步建议.md)
  - 信息收集清单

---

## 📊 内容审核总览

- 总章节数：24
- 待完善章节：24

### 各章节审核状态
- **目录**：⚠️ 需补充 7 项
  - 缺少：code
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **信息收集概述**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **被动侦察**：⚠️ 需补充 6 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **主动侦察**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **子域名枚举**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Web指纹识别**：⚠️ 需补充 6 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **目录爆破**：⚠️ 需补充 5 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **OSINT工具**：⚠️ 需补充 6 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **信息收集自动化**：⚠️ 需补充 6 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **子域名接管检测**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **云存储桶发现与枚举**：⚠️ 需补充 6 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **GitHub信息泄露搜索**：⚠️ 需补充 6 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Docker镜像信息泄露**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **社工信息收集**：⚠️ 需补充 6 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **移动APP信息收集**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **IoT设备搜索**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **自动化信息收集框架**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **信息收集报告模板**：⚠️ 需补充 8 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **目标概述**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **被动侦察结果**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **主动侦察结果**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **漏洞发现**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **攻击面分析**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：short
  - 缺少：references
- **下一步建议**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
