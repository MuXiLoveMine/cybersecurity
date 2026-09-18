# 第5章 OpenRASP-IAST部署与使用实战

OpenRASP（Open Runtime Application Self-Protection）是百度安全团队开源的运行时应用自我保护项目，同时具备IAST（交互式应用安全测试）能力。作为国内最成熟的开源IAST解决方案，OpenRASP-IAST是学习和实践IAST技术的最佳选择。

### 5.1 OpenRASP项目介绍

OpenRASP项目于2017年开源，最初定位为RASP（运行时应用自我保护）工具，用于在生产环境中检测和阻断攻击。2019年，OpenRASP推出了IAST功能，将其检测能力扩展到了测试环境的安全测试场景。

**项目组成：**
- **Agent端**：Java Agent、PHP扩展、Node.js插件
- **管理后台（Cloud-Controller）**：Go语言开发的管理服务
- **前端管理界面**：Vue.js开发的Web控制台
- **检测插件**：JavaScript编写的检测逻辑插件

**核心特性：**
1. **双模式切换**：RASP模式（防护）和IAST模式（检测）可灵活切换
2. **插件化架构**：检测逻辑以JavaScript插件形式存在，易于扩展
3. **实时监控**：毫秒级攻击检测和响应
4. **低性能损耗**：官方宣称性能损耗在5%以内
5. **多语言支持**：Java、PHP、Node.js

### 5.2 架构与原理

OpenRASP-IAST的整体架构如下：

```
┌─────────────────────────────────────────────────────────────┐
│                     OpenRASP 管理后台                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐    │
│  │ 前端UI  │  │  API服务 │  │ 消息服务 │  │  数据库/缓存 │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └──────────────┘    │
└───────┼────────────┼────────────┼───────────────────────────┘
        │            │            │
        └────────────┴────────────┘
                     │ HTTP/HTTPS
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────────┐    ┌────────▼──────────┐
│  Java 应用       │    │  PHP 应用         │
│  ┌─────────────┐ │    │  ┌──────────────┐ │
│  │ OpenRASP    │ │    │  │ OpenRASP     │ │
│  │ Java Agent  │ │    │  │ PHP 扩展     │ │
│  └─────────────┘ │    │  └──────────────┘ │
└──────────────────┘    └───────────────────┘
```

**工作原理概述：**

1. **Agent部署**：在目标应用中部署OpenRASP Agent
2. **功能插桩**：Agent对关键函数进行Hook（如SQL执行、命令执行、文件操作等）
3. **污点追踪**：在IAST模式下，追踪用户输入数据的传播路径
4. **插件检测**：检测插件基于Hook点的数据，判断是否存在安全漏洞
5. **数据上报**：Agent将检测结果和运行时数据上报到管理后台
6. **结果展示**：管理后台对漏洞进行聚合、分析和展示

### 5.3 管理后台部署

OpenRASP管理后台（Cloud-Controller）负责Agent管理、漏洞展示、配置下发等功能。推荐使用Docker方式部署，简单快捷。

#### 5.3.1 Docker部署（推荐）

**环境要求：**
- Docker 18.06+
- Docker Compose 1.24+
- 至少2GB内存
- 至少10GB磁盘空间

**部署步骤：**

**Step 1: 获取部署脚本**

```bash
# 克隆部署仓库
git clone https://github.com/baidu-security/openrasp-cloud-deploy.git
cd openrasp-cloud-deploy
```

**Step 2: 修改配置（可选）**

```bash
# 编辑环境变量配置
cp .env.example .env
vim .env
```

主要配置项：
- `MYSQL_ROOT_PASSWORD`：MySQL root密码
- `REDIS_PASSWORD`：Redis密码
- `MONGO_INITDB_ROOT_PASSWORD`：MongoDB密码
- `HTTP_PORT`：管理后台HTTP端口（默认8086）

**Step 3: 启动服务**

```bash
# 使用docker-compose启动
docker-compose up -d
```

**Step 4: 验证部署**

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f cloud
```

部署完成后，访问 `http://<服务器IP>:8086` 即可进入管理后台。

**默认账号：**
- 用户名：`admin@openrasp.com`
- 密码：`admin@123`

> 注意：首次登录后请立即修改默认密码。

#### 5.3.2 源码部署

适合需要定制开发或无法使用Docker的场景。

**环境要求：**
- Go 1.13+
- Node.js 10+
- MySQL 5.7+
- Redis 4.0+
- MongoDB 3.6+

**部署步骤：**

```bash
# 克隆源码
git clone https://github.com/baidu-security/openrasp-cloud.git
cd openrasp-cloud

# 编译后端
cd cloud
go build -o openrasp-cloud main.go

# 编译前端
cd ../frontend
npm install
npm run build

# 导入数据库
mysql -u root -p < ../scripts/db.sql

# 配置文件
cp conf/app.conf.example conf/app.conf
# 修改数据库、Redis、MongoDB配置

# 启动服务
./openrasp-cloud
```

### 5.4 Java应用Agent安装与配置

#### 5.4.1 下载Agent

登录OpenRASP管理后台，进入"应用管理" → "添加应用"，选择Java，下载对应版本的Agent。

也可以直接从GitHub Release页面下载：
```bash
# 下载最新版本的Java Agent
wget https://github.com/baidu-security/openrasp-java/releases/latest/download/rasp.jar
```

#### 5.4.2 Tomcat安装配置

**Step 1: 放置Agent文件**

```bash
# 将rasp.jar和rasp目录复制到Tomcat根目录
cp rasp.jar $CATALINA_HOME/
cp -r rasp $CATALINA_HOME/
```

**Step 2: 配置启动参数**

编辑 `$CATALINA_HOME/bin/catalina.sh`（Linux）或 `catalina.bat`（Windows）：

```bash
# 在文件开头添加
JAVA_OPTS="-javaagent:$CATALINA_HOME/rasp.jar $JAVA_OPTS"
```

**Step 3: 配置后端地址**

编辑 `$CATALINA_HOME/rasp/conf/openrasp.yml`：

```yaml
# 后端服务地址
backend.url: http://<管理后台IP>:8086/

# 应用ID（在管理后台添加应用后获取）
app_id: "your_app_id"

# 应用密钥
app_secret: "your_app_secret"

# IAST模式开关
iast.enabled: true
```

**Step 4: 重启Tomcat**

```bash
$CATALINA_HOME/bin/shutdown.sh
$CATALINA_HOME/bin/startup.sh
```

#### 5.4.3 Spring Boot应用配置

对于Spring Boot应用（内嵌Tomcat/Jetty），通过JVM参数加载Agent：

```bash
java -javaagent:/path/to/rasp.jar \
     -Drasp.app_id=your_app_id \
     -Drasp.app_secret=your_app_secret \
     -Drasp.backend_url=http://<管理后台IP>:8086/ \
     -Drasp.iast.enabled=true \
     -jar app.jar
```

#### 5.4.4 验证安装

1. 启动应用后，查看应用日志，确认没有错误信息
2. 登录管理后台，进入"应用管理" → "主机列表"，确认Agent已注册
3. 查看Agent状态是否为"在线"

### 5.5 PHP应用Agent安装与配置

#### 5.5.1 环境要求

- PHP 5.4 - 8.x
- 支持的SAPI：Apache2、FPM、CLI
- 操作系统：Linux x86/x64、Windows

#### 5.5.2 安装步骤

**Step 1: 下载PHP扩展**

```bash
# 从管理后台下载或从GitHub下载
wget https://github.com/baidu-security/openrasp-php/releases/latest/download/openrasp-php.tar.gz
tar zxf openrasp-php.tar.gz
```

**Step 2: 安装扩展**

```bash
# 编译安装（需要php-dev工具）
cd openrasp-php
phpize
./configure
make && make install
```

**Step 3: 配置php.ini**

```ini
[openrasp]
extension=openrasp.so
openrasp.app_id = your_app_id
openrasp.app_secret = your_app_secret
openrasp.backend_url = http://<管理后台IP>:8086/
openrasp.iast_enabled = On
```

**Step 4: 重启PHP-FPM/Apache**

```bash
# PHP-FPM
service php-fpm restart

# 或 Apache
service httpd restart
```

**Step 5: 验证安装**

```bash
php -m | grep openrasp
# 或通过phpinfo()查看
```

### 5.6 测试用例运行与漏洞检测

部署完成后，通过运行测试用例来触发IAST漏洞检测。

#### 5.6.1 准备测试环境

**使用WebGoat（Java靶场）：**

```bash
# 下载WebGoat
docker run -d -p 8080:8080 webgoat/webgoat-8.0
```

**使用DVWA（PHP靶场）：**

```bash
# 下载DVWA
docker run -d -p 8081:80 vulnerables/web-dvwa
```

将靶场应用部署IAST Agent后，即可开始测试。

#### 5.6.2 手动测试触发检测

以SQL注入为例：

1. 访问靶场的SQL注入页面
2. 输入测试Payload：`' OR '1'='1`
3. 提交请求
4. 观察应用是否正常响应
5. 登录OpenRASP管理后台查看是否检测到漏洞

#### 5.6.3 自动化测试结合

IAST的优势在于可以与自动化测试结合，在功能测试的同时完成安全测试。

**与Selenium结合示例：**

```python
# Selenium自动化测试脚本
from selenium import webdriver

driver = webdriver.Chrome()

# 访问测试页面
driver.get("http://test-app/sqli?name=test' OR '1'='1")

# 执行其他功能测试...
# IAST Agent会在后台自动检测安全漏洞

driver.quit()
```

**与接口测试工具结合：**

```python
# Python requests 接口测试
import requests

# 测试各种接口
base_url = "http://test-app"

# SQL注入测试点
response = requests.get(f"{base_url}/api/user", params={"id": "1' OR '1'='1"})

# 命令注入测试点
response = requests.get(f"{base_url}/api/ping", params={"host": "127.0.0.1; id"})

# 测试完成后，去管理后台查看漏洞
```

### 5.7 管理控制台使用

#### 5.7.1 仪表盘

登录管理后台后，首先看到的是仪表盘页面，展示：

- **漏洞总览**：高危、中危、低危漏洞数量统计
- **漏洞趋势**：按时间维度的漏洞数量变化
- **应用状态**：接入的应用和Agent数量
- **最近漏洞**：最新发现的漏洞列表
- **攻击类型分布**：各类漏洞的占比

#### 5.7.2 应用管理

**功能：**
- 添加/编辑/删除应用
- 查看应用下的主机列表
- 查看Agent状态和版本
- 配置下发
- 应用分组管理

**添加应用流程：**
1. 点击"添加应用"
2. 填写应用名称、选择语言
3. 选择应用类型（RASP/IAST/混合）
4. 提交后获取app_id和app_secret
5. 将app_id和app_secret配置到Agent中

#### 5.7.3 漏洞管理

**漏洞列表：**
- 按严重程度筛选（高危/中危/低危/信息）
- 按漏洞类型筛选
- 按应用/主机筛选
- 按时间范围筛选
- 搜索功能

**漏洞详情：**
- 漏洞类型和描述
- 漏洞所在URL和参数
- 完整的请求信息
- 调用栈信息
- 污点传播路径
- 修复建议
- 漏洞状态管理（待处理/处理中/已修复/忽略）

**漏洞状态管理：**
- **待处理**：新发现的漏洞
- **处理中**：已分配给开发人员修复
- **已修复**：开发已修复并验证通过
- **忽略**：误报或接受风险的漏洞

#### 5.7.4 报警配置

支持多种报警方式：

- **邮件报警**：配置SMTP服务器，发送邮件通知
- **企业微信/钉钉**：通过Webhook发送到群机器人
- **Webhook**：自定义HTTP回调，可对接任意系统
- **Syslog**：发送到Syslog服务器

**报警规则配置：**
- 漏洞等级阈值（如只报警高危漏洞）
- 报警频率限制（避免告警风暴）
- 按应用/分组配置不同的报警策略

#### 5.7.5 系统设置

- **用户管理**：添加/编辑用户，分配角色权限
- **角色权限**：管理员、审计员、普通用户等角色
- **系统配置**：全局参数配置
- **插件管理**：检测插件的上传、更新、启用/禁用
- **操作日志**：用户操作审计日志

### 5.8 常见问题排查

#### 5.8.1 Agent无法连接后台

**排查步骤：**
1. 检查网络连通性
   ```bash
   curl http://<管理后台IP>:8086/v1/agent/ping
   ```
2. 检查app_id和app_secret是否正确
3. 检查防火墙/安全组是否开放端口
4. 查看Agent日志（通常在rasp/logs目录下）

#### 5.8.2 Agent加载失败

**常见原因：**
- JDK版本不兼容（检查JDK版本是否支持）
- Agent jar包损坏（重新下载）
- 权限问题（确保Agent对目录有读写权限）
- 与其他Agent冲突（如APM Agent）

**排查方法：**
- 查看应用启动日志
- 查看hs_err_pid文件（JVM崩溃日志）
- 尝试用最简单的Demo应用测试

#### 5.8.3 检测不到漏洞

**排查步骤：**
1. 确认IAST模式已开启（`iast.enabled: true`）
2. 确认应用正确处理了请求（查看访问日志）
3. 确认请求参数确实传到了Sink点
4. 检查检测插件是否启用
5. 查看Agent日志是否有错误
6. 确认使用的是支持的框架/中间件版本

#### 5.8.4 性能影响过大

**优化方法：**
1. 减少插桩范围，配置类过滤
2. 关闭不需要的检测插件
3. 降低日志级别
4. 调整污点追踪深度
5. 使用采样模式

#### 5.8.5 误报过多

**处理方法：**
1. 分析误报原因，确认是否为净化函数未被识别
2. 配置自定义净化函数
3. 配置误报忽略规则
4. 升级到最新版本的Agent和插件

---

---

## 📋 内容审核与补充建议

> 针对「第5章 OpenRASP-IAST部署与使用实战」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
