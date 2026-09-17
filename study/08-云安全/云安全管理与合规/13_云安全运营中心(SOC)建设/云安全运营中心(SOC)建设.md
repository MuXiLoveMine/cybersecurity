# 云安全运营中心(SOC)建设

### 12.1 云SOC架构

```text
云SOC运营架构:

  +-------------------------------------------+
  |          云安全运营中心 (Cloud SOC)          |
  +-------------------------------------------+
  |                                           |
  |  数据层                                   |
  |  +--------+ +--------+ +--------+        |
  |  |Cloud   | |VPC     | |EDR     |        |
  |  |Trail   | |FlowLog | |Telemetry|       |
  |  +---+----+ +---+----+ +---+----+        |
  |      |          |          |              |
  |  +---v----------v----------v----+        |
  |  |     SIEM (Splunk/Sumo)      |        |
  |  |     日志聚合与关联分析       |        |
  |  +-------------+---------------+        |
  |                |                         |
  |  +-------------v---------------+        |
  |  |     威胁检测引擎              |        |
  |  |  GuardDuty/Defender/Custom   |       |
  |  +-------------+---------------+        |
  |                |                         |
  |  +-------------v---------------+        |
  |  |     SOAR (自动响应)           |        |
  |  |  Lambda/Logic App/Playbook   |       |
  |  +-------------+---------------+        |
  |                |                         |
  |  +-------------v---------------+        |
  |  |     事件管理                  |        |
  |  |  工单/分派/跟踪/报告           |        |
  |  +-----------------------------+        |
  |                                           |
  +-------------------------------------------+

SOC团队角色:
  ├── L1分析师: 初步分诊,过滤误报
  ├── L2分析师: 深度分析,威胁狩猎
  ├── L3分析师: 高级取证,APT追踪
  ├── SOC经理: 优先级管理,资源调度
  └── IR团队: 事件响应,取证恢复
```

### 12.2 云SOC运营流程

```text
云SOC运营流程:

  1. 事件接入
     ├── CloudTrail异常事件
     ├── GuardDuty告警
     ├── CSPM配置异常
     ├── 容器运行时告警
     └── 用户上报

  2. 初步分诊 (L1, <15分钟)
     ├── 去重与合并
     ├── 严重度评估
     ├── 误报过滤
     └── 升级或关闭

  3. 深度分析 (L2, <1小时)
     ├── 日志关联分析
     ├── 攻击链重建
     ├── 影响范围评估
     └── 响应建议

  4. 高级分析 (L3, <4小时)
     ├── APT关联分析
     ├── 威胁情报匹配
     ├── 溯源分析
     └── 取证准备

  5. 响应与恢复
     ├── 自动化遏制(SOAR)
     ├── 手动取证
     ├── 根除威胁
     └── 恢复服务

  6. 事后总结
     ├── 事件报告
     ├── 检测规则更新
     ├── 流程改进
     └── 知识库更新
```

### 12.3 自动化响应剧本

```python
#!/usr/bin/env python3
"""云安全自动响应剧本"""

import json
import logging

logger = logging.getLogger(__name__)

class SecurityPlaybook:
    """安全自动响应剧本"""

    def handle_iam_anomaly(self, event):
        """处理IAM异常事件"""
        finding_type = event.get('findingType', '')
        entity = event.get('entity', '')

        actions = []
        if 'UnauthorizedAccess' in finding_type:
            # 1. 禁用访问密钥
            actions.append({
                'action': 'disable_access_key',
                'target': entity,
                'reason': '检测到未授权访问'
            })
            # 2. 隔离相关实例
            actions.append({
                'action': 'isolate_instance',
                'target': event.get('instanceId'),
                'reason': '可能被入侵'
            })
            # 3. 通知安全团队
            actions.append({
                'action': 'notify_team',
                'channel': '#security-alerts',
                'message': f'检测到IAM异常: {finding_type}, 实体: {entity}'
            })
        elif 'CredentialExfiltration' in finding_type:
            # 1. 立即禁用所有密钥
            actions.append({
                'action': 'disable_all_keys',
                'target': entity,
                'reason': '凭据泄露检测'
            })
            # 2. 强制密码重置
            actions.append({
                'action': 'force_password_reset',
                'target': entity,
                'reason': '安全事件'
            })

        return actions

    def handle_s3_public_access(self, event):
        """处理S3公开访问事件"""
        bucket = event.get('bucketName', '')

        actions = [
            # 1. 阻止公开访问
            {'action': 'block_public_access', 'target': bucket},
            # 2. 检查是否有敏感数据
            {'action': 'scan_bucket_contents', 'target': bucket},
            # 3. 记录访问日志
            {'action': 'enable_access_logging', 'target': bucket},
            # 4. 通知数据所有者
            {'action': 'notify_data_owner', 'target': bucket},
        ]
        return actions

    def handle_ec2_compromise(self, event):
        """处理EC2实例被入侵"""
        instance_id = event.get('instanceId', '')

        actions = [
            # 1. 隔离实例(更改安全组)
            {'action': 'isolate_instance', 'target': instance_id},
            # 2. 创建取证快照
            {'action': 'create_forensic_snapshot', 'target': instance_id},
            # 3. 收集实例元数据
            {'action': 'collect_metadata', 'target': instance_id},
            # 4. 分析CloudTrail日志
            {'action': 'analyze_cloudtrail', 'target': instance_id},
            # 5. 检查横向移动
            {'action': 'check_lateral_movement', 'target': instance_id},
            # 6. 通知IR团队
            {'action': 'notify_ir_team', 'target': instance_id},
        ]
        return actions
```

---

---

## 📋 内容审核与补充建议

> 针对「云安全运营中心(SOC)建设」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
