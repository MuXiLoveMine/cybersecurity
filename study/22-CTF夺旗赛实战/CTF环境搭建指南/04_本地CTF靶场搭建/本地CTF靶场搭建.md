# 本地CTF靶场搭建

### 4.1 Docker搭建CTF题目环境

Docker是搭建CTF环境最便捷的方式之一，可以快速部署和销毁环境。

#### 4.1.1 Docker安装

**Ubuntu/Debian安装：**
```bash
# 更新包索引
sudo apt update

# 安装依赖
sudo apt install -y ca-certificates curl gnupg lsb-release

# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 将用户添加到docker组（免sudo）
sudo usermod -aG docker $USER
```

**验证安装：**
```bash
docker --version
docker run hello-world
```

#### 4.1.2 Docker常用命令

```bash
# 镜像管理
docker images                    # 列出镜像
docker pull <image>              # 拉取镜像
docker build -t <name> .         # 构建镜像
docker rmi <image>               # 删除镜像

# 容器管理
docker ps                        # 列出运行中的容器
docker ps -a                     # 列出所有容器
docker run <image>               # 运行容器
docker run -d <image>            # 后台运行
docker run -p 80:80 <image>      # 端口映射
docker run -v /host:/container   # 挂载卷
docker exec -it <container> bash # 进入容器
docker stop <container>          # 停止容器
docker start <container>         # 启动容器
docker rm <container>            # 删除容器

# 其他常用
docker logs <container>          # 查看日志
docker inspect <container>       # 查看详情
docker-compose up -d             # 使用compose启动
docker-compose down              # 使用compose停止
```

#### 4.1.3 常见CTF题目Docker化

**Web题（PHP+Apache）：**

```dockerfile
# Dockerfile
FROM php:7.4-apache

# 安装扩展
RUN docker-php-ext-install mysqli pdo_mysql

# 复制源码
COPY src/ /var/www/html/

# 设置权限
RUN chown -R www-data:www-data /var/www/html/

# 暴露端口
EXPOSE 80
```

```yaml
# docker-compose.yml
version: '3'
services:
  web:
    build: .
    ports:
      - "8080:80"
    depends_on:
      - db
  db:
    image: mysql:5.7
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: ctf
      MYSQL_USER: ctf
      MYSQL_PASSWORD: ctf
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
```

**Pwn题：**

```dockerfile
# Dockerfile
FROM ubuntu:20.04

# 安装依赖
RUN apt-get update && apt-get install -y \
    socat \
    libc6-i386 \
    && rm -rf /var/lib/apt/lists/*

# 创建用户
RUN useradd -m ctf

# 复制题目文件
COPY challenge /home/ctf/challenge
COPY flag.txt /home/ctf/flag.txt

# 设置权限
RUN chown -R root:ctf /home/ctf && \
    chmod 750 /home/ctf && \
    chmod 740 /home/ctf/flag.txt && \
    chmod 755 /home/ctf/challenge

# 切换用户
USER ctf
WORKDIR /home/ctf

# 启动服务
EXPOSE 10000
CMD ["socat", "TCP-LISTEN:10000,reuseaddr,fork", "EXEC:./challenge,pty,ctty,echo=0"]
```

**Python题（Flask）：**

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动
CMD ["python", "app.py"]
```

### 4.2 CTFd平台部署

CTFd是最流行的开源CTF平台，支持解题模式和动态flag。

#### 4.2.1 Docker部署CTFd（推荐）

```bash
# 克隆仓库
git clone https://github.com/CTFd/CTFd.git
cd CTFd

# 使用Docker Compose部署
docker-compose up -d

# 访问 http://localhost:8000
```

#### 4.2.2 手动部署CTFd

```bash
# 克隆仓库
git clone https://github.com/CTFd/CTFd.git
cd CTFd

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -c "from CTFd import create_app; app = create_app(); app.db.create_all()"

# 启动（开发环境）
python serve.py

# 生产环境使用gunicorn
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 -w 4 "CTFd:create_app()"
```

#### 4.2.3 CTFd配置

**基本配置：**

1. 首次访问会进入设置向导
2. 设置平台名称、管理员账号
3. 选择CTF模式（团队/个人）
4. 配置开始和结束时间

**主题配置：**
- CTFd支持多种主题
- 可以自定义CSS和HTML
- 社区有很多免费主题

**插件系统：**
- CTFd有丰富的插件生态
- 常用插件：动态flag、容器部署、自动判题等

### 4.3 题目部署与管理

#### 4.3.1 题目类型

CTFd支持多种题目类型：

1. **标准题（Standard）**：固定flag，提交验证
2. **动态flag题（Dynamic）**：每个队伍/用户的flag不同
3. **多选题（Multiple Choice）**：选择题形式
4. **文件题**：需要上传文件解答

#### 4.3.2 添加题目步骤

1. 进入管理后台 → Challenges → New Challenge
2. 填写题目信息：
   - 名称：题目标题
   - 分类：Web/Pwn/Re/Crypto/Misc等
   - 分值：题目分数
   - 描述：题目描述和提示
   - Flag：正确答案
3. 上传附件（如果有）
4. 设置提示（可选）
5. 发布题目

#### 4.3.3 题目分类建议

| 分类 | 包含内容 | 难度梯度 |
|------|---------|---------|
| Web | SQL注入、XSS、CSRF、文件上传、命令注入、SSRF等 | 入门到高级 |
| Pwn | 栈溢出、堆溢出、格式化字符串、内核漏洞等 | 中级到高级 |
| Reverse | 逆向工程、代码还原、脱壳、反混淆等 | 中级到高级 |
| Crypto | 古典密码、对称密码、非对称密码、哈希、量子密码等 | 入门到高级 |
| Misc | 隐写术、取证分析、流量分析、编码解码等 | 入门到高级 |
| Mobile | Android逆向、iOS逆向、App安全等 | 中级到高级 |
| Blockchain | 智能合约安全、DeFi安全等 | 新兴方向 |

### 4.4 动态flag配置

动态flag可以防止flag泄露和作弊，每个用户/队伍获得的flag都不同。

#### 4.4.1 动态flag原理

```
用户A访问题目 → 生成flag: flag{user_a_abc123}
用户B访问题目 → 生成flag: flag{user_b_def456}
用户A提交flag{user_a_abc123} → 正确
用户B提交flag{user_a_abc123} → 错误（不是自己的flag）
```

#### 4.4.2 CTFd动态flag插件

CTFd自带动态flag功能，配置方法：

1. 创建题目时选择"dynamic"类型
2. 配置flag模板：`flag{<user_id>_<random_hash>}`
3. 题目环境需要集成CTFd API来生成flag

#### 4.4.3 动态flag生成脚本

```python
# Python示例：生成动态flag
import hashlib

def generate_flag(user_id, challenge_id, secret):
    """生成用户专属flag"""
    raw = f"{user_id}:{challenge_id}:{secret}"
    hash_val = hashlib.md5(raw.encode()).hexdigest()[:8]
    return f"flag{{{user_id}_{hash_val}}}"

# 使用示例
secret = "your_secret_key"
user_id = "user123"
challenge_id = "web01"
flag = generate_flag(user_id, challenge_id, secret)
print(flag)  # flag{user123_xxxxxxxx}
```

---

---

## 📋 内容审核与补充建议

> 针对「本地CTF靶场搭建」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
