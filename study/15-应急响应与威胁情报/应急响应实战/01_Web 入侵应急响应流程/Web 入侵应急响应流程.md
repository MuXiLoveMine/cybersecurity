# Web 入侵应急响应流程

### 1.1 Web 入侵概述

Web 入侵是最常见的安全事件类型之一，攻击者通过 Web 应用漏洞获取服务器权限或窃取数据。

**常见 Web 入侵方式：**
- SQL 注入
- 文件上传漏洞（Webshell）
- 命令执行/代码执行
- 远程文件包含（RFI）
- 本地文件包含（LFI）
- 逻辑漏洞
- 弱口令/暴力破解
- XSS 跨站脚本
- CSRF 跨站请求伪造

### 1.2 Web 入侵检测

#### 1.2.1 常见入侵迹象

| 迹象 | 说明 |
|------|------|
| 网站页面被篡改 | 首页或其他页面内容被修改 |
| 网站跳转异常 | 访问网站跳转到其他恶意网站 |
| 用户投诉 | 用户反映账号被盗、资金异常等 |
| 服务器异常 | CPU/内存占用异常高、异常进程 |
| WAF 告警 | WAF 检测到大量攻击请求 |
| 搜索引擎警告 | 搜索引擎提示网站有风险 |
| 黑帽 SEO | 网站出现大量无关页面（博彩、色情等） |
| 新文件出现 | Web 目录下出现未知文件 |

#### 1.2.2 检测方法

1. **查看 Web 日志**
   - 异常的访问 IP
   - 异常的访问路径
   - SQL 注入特征
   - 异常的 User-Agent
   - 大量 404 错误（探测）

2. **检查 Web 文件**
   - 检查文件修改时间
   - 检查新增文件
   - 检查 Webshell
   - 检查文件完整性

3. **检查服务器状态**
   - 异常进程
   - 异常网络连接
   - 异常用户
   - 异常计划任务

### 1.3 Web 入侵应急响应流程

#### 阶段1：发现与确认

**操作步骤：**
1. 收到告警或报告后，立即验证事件真实性
2. 初步判断入侵类型和影响范围
3. 启动相应级别的应急响应

**检查清单：**
- [ ] 确认网站是否被篡改
- [ ] 确认是否有数据泄露
- [ ] 确认影响的业务范围
- [ ] 初步判断攻击手法

#### 阶段2：遏制

**操作步骤：**

1. **保护证据**
   ```bash
   # 备份 Web 日志
   cp -r /var/log/nginx/ /backup/incident/logs/
   cp -r /var/log/apache2/ /backup/incident/logs/
   
   # 备份 Web 目录（保留文件权限和时间戳）
   cp -rp /var/www/html/ /backup/incident/webroot/
   
   # 记录当前网络连接
   netstat -tulnp > /backup/incident/netstat.txt
   ss -tulnp > /backup/incident/ss.txt
   
   # 记录进程列表
   ps aux > /backup/incident/ps.txt
   ```

2. **遏制攻击**
   - 将受影响服务器从负载均衡摘除
   - 封禁攻击 IP（在防火墙或 WAF 上）
   - 暂时关闭有漏洞的功能页面
   - 如入侵严重，可暂时断网隔离

**注意事项：**
- 不要急于重启服务器，以免丢失内存中的证据
- 不要直接删除可疑文件，先备份再处理
- 记录所有操作命令和时间

#### 阶段3：分析

**操作步骤：**

1. **日志分析**
   ```bash
   # 统计访问量最多的 IP
   awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20
   
   # 查找 SQL 注入特征
   grep -iE "union.*select|sleep\(|benchmark|information_schema" /var/log/nginx/access.log
   
   # 查找 Webshell 访问
   grep -iE "\.(php|jsp|asp|aspx)" /var/log/nginx/access.log | grep -iE "cmd=|exec=|shell=|pass="
   
   # 查找文件上传
   grep '"POST' /var/log/nginx/access.log | grep -iE "upload|file|image"
   
   # 查找异常 User-Agent
   awk -F'"' '{print $6}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20
   ```

2. **Webshell 检测**
   ```bash
   # 查找最近 7 天修改的 PHP/JSP/ASP 文件
   find /var/www/html/ -name "*.php" -mtime -7 -type f
   find /var/www/html/ -name "*.jsp" -mtime -7 -type f
   
   # 查找可疑的一句话木马特征
   grep -r "eval(" /var/www/html/ --include="*.php"
   grep -r "assert(" /var/www/html/ --include="*.php"
   grep -r "base64_decode" /var/www/html/ --include="*.php"
   grep -r "system(" /var/www/html/ --include="*.php"
   
   # 查找隐藏文件
   find /var/www/html/ -name ".*" -type f
   
   # 查找文件包含特征
   grep -rE "(include|require)(_once)?\s*[\(]?\s*[\$_(GET|POST|REQUEST|COOKIE)" /var/www/html/ --include="*.php"
   ```

3. **分析攻击时间线**
   - 确定攻击开始时间
   - 还原攻击路径
   - 确定攻击者获取的权限
   - 评估数据泄露情况

#### 阶段4：根除

**操作步骤：**

1. **清除 Webshell 和后门**
   ```bash
   # 删除确认的 Webshell 文件
   rm -f /var/www/html/upload/shell.php
   
   # 检查并修复被篡改的文件
   # 从备份恢复或重新部署
   ```

2. **清除服务器后门**
   - 检查新增用户
   - 检查计划任务
   - 检查启动项
   - 检查异常进程

3. **修补漏洞**
   - 修复 SQL 注入漏洞
   - 修复文件上传漏洞
   - 修复代码执行漏洞
   - 加强输入验证
   - 更新框架和组件

4. **加强安全配置**
   - 部署 WAF 规则
   - 加强访问控制
   - 启用安全日志
   - 配置文件监控

#### 阶段5：恢复

**操作步骤：**
1. 验证系统安全性
2. 逐步恢复服务
3. 加强监控
4. 通知业务部门验证

#### 阶段6：总结

**操作步骤：**
1. 编写事件报告
2. 总结经验教训
3. 提出改进措施
4. 更新应急预案

### 1.4 实战案例：SQL 注入导致数据泄露

**事件背景：**
某电商网站被攻击者通过 SQL 注入漏洞窃取了用户信息，包括用户名、手机号、邮箱等。

**事件发现：**
WAF 检测到大量 SQL 注入攻击请求，同时安全监控发现数据库异常查询。

**响应过程：**

1. **发现与确认（10:00 - 10:15）**
   - WAF 触发 SQL 注入告警
   - L1 分析师确认攻击真实存在
   - 检查发现攻击者已成功执行注入语句
   - 升级至 L2 分析师，启动三级响应

2. **遏制（10:15 - 10:45）**
   - 封禁攻击 IP（来自境外的多个 IP）
   - 将该应用从负载均衡摘除
   - 备份 Web 日志和数据库日志
   - 通知数据库管理员监控数据库状态

3. **分析（10:45 - 13:00）**
   - 分析 Web 日志，确认注入点在商品搜索功能
   - 分析数据库日志，确认攻击者读取了用户表数据
   - 评估泄露数据量：约 5 万条用户信息
   - 确认漏洞原因：搜索参数未做参数化查询

4. **根除（13:00 - 15:00）**
   - 修复 SQL 注入漏洞，改为参数化查询
   - 检查所有类似功能，确保不存在同类漏洞
   - 检查服务器是否被植入后门（未发现）
   - 加强 WAF 规则，增加 SQL 注入防护

5. **恢复（15:00 - 16:00）**
   - 安全团队验证修复效果
   - 业务部门测试功能
   - 逐步将服务器加回负载均衡
   - 加强监控，关注是否有后续攻击

6. **总结（次日）**
   - 编写事件报告
   - 复盘响应过程
   - 改进措施：
     - 全面代码审计，排查所有 SQL 注入漏洞
     - 部署数据库审计系统
     - 加强开发安全培训
     - 敏感数据加密存储

**经验教训：**
- 开发安全意识不足，未使用参数化查询
- WAF 规则不够完善，未能完全阻止注入攻击
- 数据库权限过大，一次注入泄露大量数据
- 敏感数据未加密，泄露后直接可用

---

---

