# Serverless 攻击面详解

### 2.1 事件注入

Serverless 函数由各种事件源触发，事件内容本身可能成为攻击载荷。

**案例：对象存储事件处理函数**
- 攻击者上传一个特制文件，函数读取后解析
- 文件名、文件内容、元数据都可能包含恶意载荷
- 例如 CSV 注入、XXE、反序列化漏洞

**防御代码示例（Python Lambda）**

```python
import json
import re

def lambda_handler(event, context):
    # 从 S3 事件中提取对象 key
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    # 1. 输入校验：拒绝非法路径
    if not re.match(r'^[a-zA-Z0-9/_.\-]+$', key):
        return {"statusCode": 400, "body": "非法文件名"}

    # 2. 文件类型白名单
    if not key.endswith(('.csv', '.json', '.txt')):
        return {"statusCode": 400, "body": "不支持的文件类型"}

    # 3. 限制单次处理文件大小，防止资源耗尽
    # （通过对象元数据预检查）

    # 4. 使用安全解析库，禁用外部实体
    # 业务处理 ...
    return {"statusCode": 200, "body": "处理完成"}
```

### 2.2 权限过度

Serverless 函数常被赋予过宽的 IAM 权限，例如一个仅需读取 S3 的函数却被授予 `s3:*` 或更大权限。一旦函数被攻破，攻击者可借此横向移动。

**典型过度权限示例**

```json
// 危险：授予全资源全操作
{
  "Effect": "Allow",
  "Action": "*",
  "Resource": "*"
}
```

**最小权限示例**

```json
// 安全：仅允许读取指定桶的指定前缀
{
  "Effect": "Allow",
  "Action": ["s3:GetObject"],
  "Resource": "arn:aws:s3:::my-data-bucket/uploads/*"
}
```

### 2.3 依赖漏洞

函数依赖的第三方库（npm / pip）可能存在已知漏洞或被植入恶意代码。例如 2018 年 event-stream 包被植入恶意代码窃取比特币钱包。

**依赖扫描示例（pip-audit）**

```bash
# 扫描 Python 函数依赖
pip-audit -r requirements.txt

# 扫描 Node.js 依赖
npm audit --omit=dev
```

**Snyk 集成 CI 检测**

```yaml
# GitHub Actions 中扫描 Serverless 依赖
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Snyk
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
```

### 2.4 拒绝钱包攻击（DoW）

Serverless 按调用计费，攻击者可通过大量触发事件（如高频 HTTP 请求、循环触发队列）导致账单爆炸，称为 Denial of Wallet。

**防御手段**：
- 在 API 网关层设置速率限制与配额
- 使用 WAF 拦截异常流量
- 设置函数并发上限（reserved concurrency）
- 监控异常调用频率并自动告警

```bash
# AWS Lambda 设置预留并发上限
aws lambda put-function-concurrency \
  --function-name my-func \
  --reserved-concurrent-executions 50
```

### 2.5 敏感信息泄露

常见泄露途径：
- 环境变量硬编码密钥
- 日志输出敏感数据
- 错误堆栈暴露内部信息
- 函数返回内容包含敏感字段

**安全使用密钥（AWS Secrets Manager）**

```python
import boto3
import json

def get_secret():
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId="prod/db/password")
    return json.loads(response["SecretString"])["password"]

def lambda_handler(event, context):
    pwd = get_secret()  # 运行时获取，不在代码中硬编码
    # 业务处理
```

### 2.6 函数执行链滥用

Serverless 应用常由多个函数通过事件串联，攻击者一旦攻破一个函数，可借助其权限触发下游函数，形成横向移动链路。

**防御**：对函数间调用进行身份验证与审计，限制函数可触发的下游资源。

---

---

