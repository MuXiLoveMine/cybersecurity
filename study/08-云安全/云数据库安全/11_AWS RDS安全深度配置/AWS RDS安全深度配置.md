# AWS RDS安全深度配置

### 11.1 RDS安全参数组详解

```bash
# 创建自定义参数组
aws rds create-db-parameter-group \
    --db-parameter-group-name secure-mysql-pg \
    --db-parameter-group-family mysql8.0 \
    --description "Secure MySQL 8.0 parameter group"

# 安全相关参数配置
aws rds modify-db-parameter-group \
    --db-parameter-group-name secure-mysql-pg \
    --parameters \
        ParameterName=require_secure_transport,ApplyMethod=immediate,ParameterValue=ON \
        ParameterName=connect_timeout,ApplyMethod=immediate,ParameterValue=10 \
        ParameterName=max_connections,ApplyMethod=immediate,ParameterValue=200 \
        ParameterName=max_user_connections,ApplyMethod=immediate,ParameterValue=50 \
        ParameterName=local_infile,ApplyMethod=immediate,ParameterValue=0 \
        ParameterName=skip_show_database,ApplyMethod=immediate,ParameterValue=1 \
        ParameterName=log_bin_trust_function_creators,ApplyMethod=immediate,ParameterValue=0

# 审计参数
aws rds modify-db-parameter-group \
    --db-parameter-group-name secure-mysql-pg \
    --parameters \
        ParameterName=server_audit_logging,ApplyMethod=immediate,ParameterValue=ENABLED \
        ParameterName=server_audit_events,ApplyMethod=immediate,ParameterValue=CONNECT,QUERY,DCL,DDL \
        ParameterName=server_audit_logs_upload,ApplyMethod=immediate,ParameterValue=1 \
        ParameterName=server_audit_excl_users,ApplyMethod=immediate,ParameterValue=rdsadmin

# 应用参数组到实例
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --db-parameter-group-name secure-mysql-pg \
    --apply-immediately
```

### 11.2 RDS增强监控与性能洞察

```bash
# 启用增强监控(1秒粒度)
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --monitoring-interval 1 \
    --monitoring-role-arn arn:aws:iam::123456789:role/rds-monitoring-role

# 启用Performance Insights
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --enable-performance-insights \
    --performance-insights-retention-period 731 \
    --performance-insights-kms-key-id arn:aws:kms:us-east-1:123:key/abc-123

# 查看Performance Insights指标
aws rds describe-performance-insights-metric \
    --service-type RDS \
    --identifier db-XXXXXXXXXX \
    --metric-queries '[{"Metric":"db.load.avg"}]'

# CloudWatch告警配置
# 高连接数告警
aws cloudwatch put-metric-alarm \
    --alarm-name "RDS-HighConnections" \
    --alarm-description "RDS connection count too high" \
    --metric-name DatabaseConnections \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 150 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=DBInstanceIdentifier,Value=mydb \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:123:alerts
```

### 11.3 RDS多可用区与故障转移

```bash
# 启用多可用区部署
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --multi-az \
    --apply-immediately

# 配置故障转移优先级
aws rds modify-db-instance \
    --db-instance-identifier mydb-replica1 \
    --promotion-tier 1

aws rds modify-db-instance \
    --db-instance-identifier mydb-replica2 \
    --promotion-tier 2

# 删除保护
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --deletion-protection \
    --apply-immediately

# 自动故障转移测试
aws rds failover-db-cluster \
    --db-cluster-identifier mydb-cluster \
    --target-db-instance-identifier mydb-replica1
```

### 11.4 RDS安全自动化检测脚本

```python
import boto3
import json
from datetime import datetime

class RDSSecurityAuditor:
    """AWS RDS安全审计自动化"""

    def __init__(self, region='us-east-1'):
        self.rds = boto3.client('rds', region_name=region)
        self.ec2 = boto3.client('ec2', region_name=region)
        self.findings = []

    def audit_all(self):
        """执行完整安全审计"""
        instances = self.rds.describe_db_instances()
        for inst in instances['DBInstances']:
            self._check_public_access(inst)
            self._check_encryption(inst)
            self._check_backups(inst)
            self._check_multi_az(inst)
            self._check_security_groups(inst)
            self._check_enhanced_monitoring(inst)
            self._check_deletion_protection(inst)
            self._check_auto_minor_upgrade(inst)
            self._check_parameter_groups(inst)
        return self.findings

    def _check_public_access(self, inst):
        if inst.get('PubliclyAccessible', False):
            self.findings.append({
                'instance': inst['DBInstanceIdentifier'],
                'severity': 'CRITICAL',
                'issue': 'RDS实例可公网访问',
                'remediation': '设置 --no-publicly-accessible'
            })

    def _check_encryption(self, inst):
        if not inst.get('StorageEncrypted', False):
            self.findings.append({
                'instance': inst['DBInstanceIdentifier'],
                'severity': 'HIGH',
                'issue': '存储未加密',
                'remediation': '创建加密快照并恢复到新实例'
            })

    def _check_backups(self, inst):
        retention = inst.get('BackupRetentionPeriod', 0)
        if retention < 7:
            self.findings.append({
                'instance': inst['DBInstanceIdentifier'],
                'severity': 'MEDIUM',
                'issue': f'备份保留期仅{retention}天，建议至少7天',
                'remediation': '设置 --backup-retention-period 30'
            })

    def _check_multi_az(self, inst):
        if not inst.get('MultiAZ', False):
            self.findings.append({
                'instance': inst['DBInstanceIdentifier'],
                'severity': 'MEDIUM',
                'issue': '未启用多可用区部署',
                'remediation': '启用Multi-AZ以提供高可用性'
            })

    def _check_security_groups(self, inst):
        for sg in inst.get('VpcSecurityGroups', []):
            sg_detail = self.ec2.describe_security_groups(
                GroupIds=[sg['VpcSecurityGroupId']]
            )
            for group in sg_detail['SecurityGroups']:
                for rule in group.get('IpPermissions', []):
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            self.findings.append({
                                'instance': inst['DBInstanceIdentifier'],
                                'severity': 'CRITICAL',
                                'issue': f'安全组{group["GroupName"]}允许0.0.0.0/0访问端口{rule.get("FromPort")}',
                                'remediation': '限制安全组仅允许应用服务器IP'
                            })

    def _check_enhanced_monitoring(self, inst):
        if inst.get('MonitoringInterval', 0) == 0:
            self.findings.append({
                'instance': inst['DBInstanceIdentifier'],
                'severity': 'LOW',
                'issue': '增强监控未启用',
                'remediation': '设置 --monitoring-interval 1'
            })

    def _check_deletion_protection(self, inst):
        if not inst.get('DeletionProtection', False):
            self.findings.append({
                'instance': inst['DBInstanceIdentifier'],
                'severity': 'MEDIUM',
                'issue': '删除保护未启用',
                'remediation': '设置 --deletion-protection'
            })

    def _check_auto_minor_upgrade(self, inst):
        if not inst.get('AutoMinorVersionUpgrade', False):
            self.findings.append({
                'instance': inst['DBInstanceIdentifier'],
                'severity': 'MEDIUM',
                'issue': '自动小版本升级未启用',
                'remediation': '设置 --auto-minor-version-upgrade'
            })

    def _check_parameter_groups(self, inst):
        pg_name = inst.get('DBParameterGroups', [{}])[0].get('DBParameterGroupName', '')
        if pg_name == 'default.mysql8.0':
            self.findings.append({
                'instance': inst['DBInstanceIdentifier'],
                'severity': 'LOW',
                'issue': '使用默认参数组，未自定义安全参数',
                'remediation': '创建自定义参数组并应用安全配置'
            })

    def generate_report(self):
        """生成安全报告"""
        report = f"RDS安全审计报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        report += f"发现总数: {len(self.findings)}\n"
        report += "=" * 60 + "\n"
        severity_count = {}
        for f in self.findings:
            sev = f['severity']
            severity_count[sev] = severity_count.get(sev, 0) + 1
        for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = severity_count.get(sev, 0)
            report += f"{sev}: {count}\n"
        report += "=" * 60 + "\n"
        for f in self.findings:
            report += f"\n[{f['severity']}] {f['instance']}\n"
            report += f"  问题: {f['issue']}\n"
            report += f"  修复: {f['remediation']}\n"
        return report

# 使用示例
auditor = RDSSecurityAuditor('us-east-1')
auditor.audit_all()
print(auditor.generate_report())
```

---

---

