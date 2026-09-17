# Serverless应急响应

### 5.1 Serverless取证限制

Serverless（如AWS Lambda、Azure Functions、阿里云函数计算）的取证面临独特挑战。

| 挑战 | 说明 | 缓解策略 |
|------|------|----------|
| 冷启动限制 | 函数实例随时创建和销毁 | 使用实时日志流，不依赖事后取证 |
| 无持久文件系统 | 函数执行后文件系统消失 | 在函数中主动上传日志/证据到S3 |
| 无持久进程 | 无法附加调试器 | 依赖云平台日志和监控 |
| 共享执行环境 | 无法获取独立环境快照 | 依赖云平台审计日志 |
| 调用频率高 | 日志量巨大 | 使用结构化日志和告警过滤 |

### 5.2 函数调用日志分析

```bash
# AWS CloudWatch Logs 查询
# 查询Lambda函数日志
aws logs filter-log-events \
  --log-group-name "/aws/lambda/my-function" \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --end-time $(date +%s)000 \
  --filter-pattern '"ERROR"' \
  --output json | jq '.events[]'

# CloudWatch Logs Insights查询
aws logs start-query \
  --log-group-name "/aws/lambda/my-function" \
  --start-time $(date -d '24 hours ago' +%s) \
  --end-time $(date +%s) \
  --query-string '
    fields @timestamp, @message
    | filter @message like /ERROR/
    | sort @timestamp desc
    | limit 100
  '

# 查询异常调用模式
aws logs start-query \
  --log-group-name "/aws/lambda/my-function" \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string '
    stats count(*) by requestId
    | sort @count desc
    | limit 20
  '

# Azure Functions日志查询
az monitor log-analytics query \
  --workspace "my-workspace" \
  --analytics-query '
    AppRequests
    | where name == "my-function"
    | where resultCode != 200
    | summarize count() by bin(timeGenerated, 5m)
    | render timechart
  '

# 阿里云函数计算日志查询
aliyun fc-open GET /2023-03-30/functions/{functionName}/logs \
  --query '{"startTime": "2024-01-01T00:00:00Z", "endTime": "2024-01-01T01:00:00Z"}'
```

### 5.3 Serverless安全事件调查清单

```python
#!/usr/bin/env python3
"""Serverless安全事件调查清单"""
import boto3
from datetime import datetime, timedelta

class ServerlessIncidentInvestigator:
    def __init__(self, region="us-east-1"):
        self.region = region
        self.logs = boto3.client('logs', region_name=region)
        self.cloudtrail = boto3.client('cloudtrail', region_name=region)
        self.iam = boto3.client('iam')
        self.lam = boto3.client('lambda', region_name=region)

    def investigate_function(self, function_name, hours_back=24):
        """调查Lambda函数"""
        log_group = f"/aws/lambda/{function_name}"
        start_time = int((datetime.now() - timedelta(hours=hours_back)).timestamp() * 1000)
        end_time = int(datetime.now().timestamp() * 1000)

        print(f"\n{'='*60}")
        print(f"调查函数: {function_name}")
        print(f"时间范围: 最近{hours_back}小时")
        print(f"{'='*60}")

        # 1. 检查函数配置
        config = self.lam.get_function_configuration(FunctionName=function_name)
        print(f"\n[函数配置]")
        print(f"  运行时: {config.get('Runtime')}")
        print(f"  处理器: {config.get('Handler')}")
        print(f"  超时: {config.get('Timeout')}秒")
        print(f"  内存: {config.get('MemorySize')}MB")
        print(f"  最后修改: {config.get('LastModified')}")

        # 检查执行角色权限
        role_arn = config.get('Role')
        role_name = role_arn.split('/')[-1]
        print(f"  执行角色: {role_name}")

        # 检查角色策略
        inline_policies = self.iam.list_role_policies(RoleName=role_name)
        for policy in inline_policies.get('PolicyNames', []):
            version = self.iam.get_role_policy(
                RoleName=role_name, PolicyName=policy
            )
            print(f"  内联策略: {policy}")
            print(f"    文档: {version['PolicyDocument']}")

        # 2. 检查函数代码是否被修改
        print(f"\n[代码变更检查]")
        events = self.cloudtrail.lookup_events(
            LookupAttributes=[{
                'AttributeKey': 'ResourceName',
                'AttributeValue': function_name
            }],
            StartTime=datetime.now() - timedelta(hours=hours_back),
            EndTime=datetime.now()
        )
        for event in events.get('Events', []):
            if event['EventName'] in ('UpdateFunctionCode', 'UpdateFunctionConfiguration'):
                print(f"  [!] {event['EventTime']} {event['EventName']} by {event['Username']}")

        # 3. 检查异常调用
        print(f"\n[调用分析]")
        response = self.logs.filter_log_events(
            logGroupName=log_group,
            startTime=start_time,
            endTime=end_time,
            filterPattern='"ERROR"'
        )
        errors = response.get('events', [])
        print(f"  错误数量: {len(errors)}")
        for err in errors[:10]:
            print(f"  {err['timestamp']} {err['message'][:100]}")

        # 4. 检查数据外传
        print(f"\n[数据外传检查]")
        response = self.logs.filter_log_events(
            logGroupName=log_group,
            startTime=start_time,
            endTime=end_time,
            filterPattern='"s3" "PutObject"'
        )
        for event in response.get('events', []):
            print(f"  [!] 检测到S3上传: {event['message'][:150]}")

# 使用
investigator = ServerlessIncidentInvestigator()
investigator.investigate_function("my-api-function", hours_back=48)
```

---

---

## 📋 内容审核与补充建议

> 针对「Serverless应急响应」部分的内容审核结果：

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
