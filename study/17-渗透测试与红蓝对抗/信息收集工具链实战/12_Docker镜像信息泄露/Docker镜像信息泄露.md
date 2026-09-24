# Docker镜像信息泄露

### 12.1 Docker镜像敏感信息检测

```bash
# Whispers - 检测Dockerfile和配置文件中的敏感信息
# 安装
pip install whispers

# 扫描Dockerfile
whispers Dockerfile

# 扫描docker-compose.yml
whispers docker-compose.yml

# 扫描整个目录
whispers -r /path/to/project

# Trivy - 容器镜像漏洞和密钥扫描
# 安装
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh

# 扫描镜像中的密钥
trivy image --scanners secret company/app:latest

# 扫描Dockerfile
trivy config Dockerfile

# 扫描docker-compose
trivy config docker-compose.yml

# 输出JSON格式
trivy image --format json --output results.json company/app:latest

# Docker镜像历史检查
docker history --no-trunc company/app:latest | grep -i "password\|secret\|key\|token"

# 检查镜像层文件
docker create --name temp_container company/app:latest
docker export temp_container | tar -tvf - | grep -i "\.env\|config\|secret\|key"
docker rm temp_container
```

### 12.2 Docker Hub公开镜像搜索

```bash
# 使用Docker Hub API搜索公开镜像
curl -s "https://hub.docker.com/v2/search/repositories/?query=company_name&page_size=25" | jq

# 检查镜像层中的敏感文件
# 使用dive工具分析镜像层
# 安装
wget https://github.com/wagoodman/dive/releases/latest/download/dive_linux_amd64
chmod +x dive

# 分析镜像
dive company/app:latest

# 提取镜像中的文件系统
docker save company/app:latest -o image.tar
tar -xf image.tar
# 检查每一层
for layer in */layer.tar; do
    echo "[*] 检查: $layer"
    tar -tf "$layer" | grep -i "\.env\|secret\|password\|key\|config"
done
```

---

---

