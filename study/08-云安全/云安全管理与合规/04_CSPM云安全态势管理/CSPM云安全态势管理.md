# CSPM云安全态势管理

### 4.1 CSPM概念

CSPM (Cloud Security Posture Management) 是持续监控、评估和修复云基础设施安全配置的工具。

```
CSPM工作流程：

  持续扫描 --> 评估风险 --> 优先级排序 --> 自动修复 --> 报告合规
     |             |             |             |           |
     v             v             v             v           v
  配置发现     风险评分     修复建议     自动行动    合规报告
  API查询     基于上下文   按严重度     Lambda/    等保/ISO/
  配置比对    和业务影响   排列优先级    函数执行    SOC2/PCI
```

### 4.2 CSPM核心功能

```
1. 配置审计
   - 自动发现云资源
   - 检查配置合规性
   - 与安全基线对比
   - 持续监控配置漂移

2. 合规报告
   - 映射合规框架
   - 生成合规报告
   - 跟踪合规状态
   - 提供修复建议

3. 风险评估
   - 识别暴露的资源
   - 评估权限过宽
   - 检测加密缺失
   - 评估网络暴露

4. 自动修复
   - 自动修复配置
   - 执行安全策略
   - 阻止不合规变更
   - 通知安全团队

5. 可视化
   - 云资源拓扑图
   - 安全态势仪表盘
   - 风险热图
   - 趋势分析
```

### 4.3 主流CSPM工具

| 工具 | 支持云 | 主要特性 |
|------|--------|----------|
| AWS Config | AWS | 原生配置管理 |
| Azure Policy | Azure | 原生策略管理 |
| Prisma Cloud | 多云 | 综合CNAPP平台 |
| Wiz | 多云 | 图驱动的风险分析 |
| Checkov | 多云 | 开源IaC扫描 |
| Prowler | AWS | 开源AWS安全检查 |
| Cloud Custodian | 多云 | 开源策略引擎 |

**Prowler使用示例**

```bash
# 安装Prowler
pip install prowler

# 扫描AWS环境
prowler aws --profile my-profile

# 只扫描特定服务
prowler aws --profile my-profile --services s3,iam,ec2

# 生成HTML报告
prowler aws --profile my-profile --output-formats html

# 检查等保合规
prowler aws --profile my-profile --compliance cis_2.0_aws
```

**Cloud Custodian策略示例**

```yaml
# 确保所有S3存储桶启用加密
policies:
  - name: s3-encryption-check
    resource: aws.s3
    filters:
      - type: bucket-encryption
        state: False
    actions:
      - type: set-bucket-encryption
        crypto: AES256

  # 检测公共EC2实例
  - name: ec2-public-instance-alert
    resource: aws.ec2
    filters:
      - type: instance-attribute
        key: SourceDestCheck
        value: false
    actions:
      - type: mark-for-op
        op: stop
        days: 1

  # 确保安全组不开放22端口到公网
  - name: ssh-open-to-world
    resource: aws.security-group
    filters:
      - type: ingress
        IpProtocol: tcp
        FromPort: 22
        Cidr: 0.0.0.0/0
    actions:
      - type: remove-permissions
        ip-protocol: tcp
        from-port: 22
```

---

---

