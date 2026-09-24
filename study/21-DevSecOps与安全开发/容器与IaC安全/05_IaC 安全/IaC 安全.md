# IaC 安全

### 5.1 Terraform 安全

#### 5.1.1 Terraform 常见安全风险

```hcl
# 危险：安全组规则过于开放
resource "aws_security_group" "web" {
  name = "web-sg"
  
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # 危险：SSH 对全互联网开放
  }
  
  ingress {
    from_port = 3306
    to_port = 3306
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # 危险：数据库对全互联网开放
  }
}

# 安全：限制来源 IP
resource "aws_security_group" "web_secure" {
  name = "web-sg-secure"
  
  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # HTTPS 可以开放
  }
  
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # 仅内网访问 SSH
  }
}

# 危险：S3 存储桶公开
resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
  acl = "public-read"  # 危险：公开读
}

# 安全：S3 私有 + 加密
resource "aws_s3_bucket" "data_secure" {
  bucket = "my-data-bucket-secure"
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data_secure.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data_secure.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 危险：IAM 策略权限过大
resource "aws_iam_role_policy" "app" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "*"          # 危险：所有权限
      Resource = "*"         # 危险：所有资源
    }]
  })
}

# 安全：最小权限 IAM
resource "aws_iam_role_policy" "app_secure" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "arn:aws:s3:::my-data-bucket-secure/*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query"
        ]
        Resource = "arn:aws:dynamodb:*:*:table/my-table"
      }
    ]
  })
}

# 危险：数据库未加密
resource "aws_db_instance" "database" {
  engine = "mysql"
  storage_encrypted = false  # 危险：未加密
}

# 安全：加密数据库 + 网络隔离
resource "aws_db_instance" "database_secure" {
  engine = "mysql"
  storage_encrypted = true                    # 启用存储加密
  kms_key_id = aws_kms_key.db.arn             # 使用 KMS 密钥
  publicly_accessible = false                  # 禁止公网访问
  vpc_security_group_ids = [aws_security_group.db.id]
  backup_retention_period = 7                  # 启用备份
  deletion_protection = true                   # 启用删除保护
}
```

#### 5.1.2 Terraform 安全扫描工具

**tfsec 使用**
```bash
# 安装
# macOS: brew install tfsec
# Linux: go install github.com/aquasecurity/tfsec/cmd/tfsec@latest

# 扫描目录
tfsec terraform/

# 输出 JSON
tfsec terraform/ -f json -o tfsec-report.json

# 输出 SARIF
tfsec terraform/ -f sarif -o tfsec-results.sarif

# 设置退出码级别
tfsec terraform/ --soft-fail=false  # 任何问题都返回非0退出码

# 忽略特定规则
# 在代码中添加注释
# tfsec:ignore:AWS006
resource "aws_security_group" "web" {
  # ...
}

# 使用配置文件
# .tfsec/config.yml
```

**Checkov 使用**
```bash
# 安装
pip install checkov

# 扫描 Terraform 目录
checkov -d terraform/

# 扫描单个文件
checkov -f main.tf

# 输出 JSON
checkov -d terraform/ -o json > checkov-report.json

# 输出 SARIF
checkov -d terraform/ -o sarif > checkov-results.sarif

# 只运行特定检查
checkov -d terraform/ -c CKV_AWS_18,CKV_AWS_19

# 跳过特定检查
checkov -d terraform/ -s CKV_AWS_20

# 使用框架特定的检查
checkov -d cloudformation/ --framework cloudformation
checkov -d k8s/ --framework kubernetes
checkov -d helm/ --framework helm
```

**Checkov 在 CI/CD 中使用**
```yaml
# .github/workflows/terraform-security.yml
name: Terraform Security Scan
on: [push, pull_request]

jobs:
  terraform-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Terraform 格式检查
        run: terraform fmt -check -recursive
      
      - name: Terraform 初始化
        run: terraform init -backend=false
      
      - name: Checkov 安全扫描
        uses: bridgecrewio/checkov-action@v12
        with:
          directory: terraform/
          framework: terraform
          output_format: sarif
          output_file: checkov-results.sarif
          soft_fail: false
      
      - name: tfsec 安全扫描
        uses: aquasecurity/tfsec-action@v1.0.3
        with:
          working_directory: terraform/
      
      - name: 上传结果
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: checkov-results.sarif
```

### 5.2 Ansible 安全

**Ansible 安全最佳实践**

```yaml
# 危险：明文存储敏感变量
# group_vars/production.yml
---
db_password: "SuperSecret123!"  # 危险：明文存储
api_key: "abc123xyz"           # 危险：明文存储

# 安全：使用 Ansible Vault 加密
# 创建加密文件
# ansible-vault encrypt group_vars/production/vault.yml
---
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  6230313662646630653530363338653535306362383739333934656361653763...
api_key: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  346537633866353332653735383861616261626338656432356533623162...

# 安全：使用 HashiCorp Vault 获取密钥
---
- name: 获取数据库密码
  hosts: database
  tasks:
    - name: 从 Vault 获取密钥
      hashivault_read:
        url: https://vault.example.com
        authtoken: "{{ vault_token }}"
        path: secret/data/database
        key: password
      register: db_password_result

    - name: 配置数据库
      mysql_user:
        name: app
        password: "{{ db_password_result.value }}"
        priv: '*.*:ALL'
```

**Ansible 安全配置**
```ini
# ansible.cfg
[defaults]
# 禁用 SSH 密钥检查
host_key_checking = False
# 使用加密的密码文件
vault_password_file = /etc/ansible/vault_password
# 提权方式
[privilege_escalation]
become = True
become_method = sudo
# 禁止明文密码传递
pipelining = True

# 安全：SSH 配置
[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
          -o StrictHostKeyChecking=yes
          -o UserKnownHostsFile=/dev/null
```

### 5.3 IaC 安全最佳实践

**安全 IaC 清单**
```yaml
# IaC 安全最佳实践清单
security_checklist:
  # 1. 网络安全
  - 禁止 0.0.0.0/0 的入站规则（除 443/80 外）
  - 安全组规则最小化
  - 数据库禁止公网访问
  - 使用私有子网部署内部服务

  # 2. 身份与访问
  - IAM 策略最小权限
  - 禁止使用通配符权限（Action: *）
  - 使用角色而非长期访问密钥
  - 定期轮换密钥

  # 3. 数据保护
  - 存储服务启用加密
  - 数据库启用存储加密
  - 传输加密（TLS）
  - 备份启用加密

  # 4. 日志审计
  - 启用 CloudTrail / 操作日志
  - 启用 CloudWatch / 监控告警
  - 启用 VPC Flow Logs
  - 启用 API Gateway 日志

  # 5. 密钥管理
  - 禁止硬编码密钥
  - 使用 Vault / KMS 管理密钥
  - 敏感数据使用 Ansible Vault
  - .gitignore 排除密钥文件

  # 6. 资源保护
  - 启用删除保护
  - 启用版本控制
  - 启用防篡改
  - 启用 MFA 删除
```

---

---

