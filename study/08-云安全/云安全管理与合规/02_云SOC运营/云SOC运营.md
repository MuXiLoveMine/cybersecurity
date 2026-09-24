# 云SOC运营

### 2.1 云SOC架构

```
+-------------------------------------------------+
|                 Cloud SOC 架构                   |
+-------------------------------------------------+
|                                                 |
|  数据采集层                                     |
|  +---------+ +---------+ +---------+ +-------+|
|  | 云平台  | | 应用    | | 网络    | | 端点  ||
|  | 日志    | | 日志    | | 流量    | | 遥测  ||
|  | (Cloud  | | (App    | | (VPC   | | (EDR)||
|  | Trail)  | | Logs)   | | Flow)  | |       ||
|  +---------+ +---------+ +---------+ +-------+|
|                    |                            |
|         +----------v----------+                |
|         |   SIEM/数据湖        |                |
|         |  (Splunk/ELK/Sumo)  |                |
|         +----------+----------+                |
|                    |                            |
|  检测分析层         |                            |
|  +---------+ +----v---+ +---------+            |
|  | 规则    | | UEBA   | | 威胁    |            |
|  | 引擎    | | (用户  | | 情报    |            |
|  | (Sigma/ | | 实体   | | (CTI)  |            |
|  | Sigma)  | | 行为)  | |        |            |
|  +---------+ +--------+ +---------+            |
|                    |                            |
|         +----------v----------+                |
|         |   SOAR/编排自动化    |                |
|         |  (TheHive/Phantom)  |                |
|         +----------+----------+                |
|                    |                            |
|  响应处置层         |                            |
|  +---------+ +----v---+ +---------+            |
|  | 告警    | | 调查   | | 处置    |            |
|  | 分发    | | 工作流  | | 动作    |            |
|  +---------+ +--------+ +---------+            |
|                                                 |
+-------------------------------------------------+
```

### 2.2 云原生威胁检测

```
云原生威胁检测用例：

1. 异常API调用
   - 非常规时间的API调用
   - 异常频率的API请求
   - 来自异常IP的API调用
   - 权限提升API序列

2. 资源异常操作
   - 大量创建EC2实例(加密货币挖矿)
   - 异常的S3存储桶访问
   - 安全组修改(开放端口)
   - IAM策略变更

3. 数据外传检测
   - 大量数据从S3下载
   - 异常的数据传输量
   - 到异常目标的数据传输
   - 加密通道数据传输

4. 横向移动检测
   - EC2实例间异常连接
   - 跨账户访问
   - 角色链滥用
   - Lambda函数异常调用
```

**AWS GuardDuty检测示例**

```bash
# 启用GuardDuty
aws guardduty create-detector --enable

# 查看发现
aws guardduty list-findings --detector-id <id>

# 查看发现详情
aws guardduty get-findings --detector-id <id> \
    --finding-ids <finding-id>

# 常见发现类型:
# UnauthorizedAccess:EC2/MetadataDNS
# Impact:EC2/MaliciousDomainRequest
# Persistence:IAMUser/BackdoorRuntimePolicy
# Exfiltration:S3/MaliciousIPCaller
# CredentialAccess:IAMUser/AnomalousBehavior
```

### 2.3 自动化响应

```python
# AWS Lambda自动化响应示例
# 当检测到恶意EC2实例时自动隔离

import json
import boto3

def lambda_handler(event, context):
    """GuardDuty发现事件的自动响应"""
    finding = json.loads(event['detail']['finding'])
    finding_type = finding['type']

    ec2 = boto3.client('ec2')
    instance_id = finding.get('resource', {}).get('instanceDetails', {}).get('instanceId')

    if not instance_id:
        return {"status": "no_instance_id"}

    # 根据发现类型执行不同响应
    if finding_type.startswith('UnauthorizedAccess') or \
       finding_type.startswith('Impact'):
        # 隔离实例：替换安全组为隔离安全组
        try:
            ec2.modify_instance_attribute(
                InstanceId=instance_id,
                Groups=['sg-isolated']  # 隔离安全组
            )
            print(f"实例 {instance_id} 已隔离")

            # 发送通知
            sns = boto3.client('sns')
            sns.publish(
                TopicArn='arn:aws:sns:us-east-1:123:security-alerts',
                Subject=f'安全事件: {finding_type}',
                Message=f'实例 {instance_id} 因 {finding_type} 已自动隔离'
            )

        except Exception as e:
            print(f"隔离失败: {e}")
            return {"status": "error", "message": str(e)}

    elif finding_type.startswith('Exfiltration'):
        # 阻断出口流量
        # 修改安全组拒绝所有出站
        pass

    return {"status": "success"}
```

---

---

