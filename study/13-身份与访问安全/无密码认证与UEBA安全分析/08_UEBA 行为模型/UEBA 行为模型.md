# UEBA 行为模型

### 8.1 登录行为模型

| 行为维度 | 正常基线 | 异常模式 | 风险权重 |
|----------|----------|----------|----------|
| 登录时间 | 工作日9-18点 | 凌晨3点登录 | 20 |
| 登录地点 | 北京、上海 | 海外陌生IP | 30 |
| 登录设备 | 固定2-3台设备 | 全新设备 | 15 |
| 登录频率 | 日均3-5次 | 1小时内20次 | 15 |
| 登录结果 | 成功率>95% | 连续失败后成功 | 25 |
| 认证方式 | Passkey/MFA | 突然降级为密码 | 20 |

### 8.2 文件访问行为模型

```
文件访问行为基线与异常检测：

正常行为基线：
  ├── 访问目录：/shared/projects/, /personal/docs/
  ├── 访问频率：日均10-20次
  ├── 数据量：单次<10MB，日均<100MB
  ├── 访问时间：工作时间为主
  └── 文件类型：文档、表格

异常行为模式：
  ├── 突然访问HR/财务目录（非本职权限）
  ├── 批量下载到外部存储
  ├── 凌晨大量读取文件
  ├── 访问频率突增10倍以上
  ├── 首次访问敏感数据目录
  └── 使用加密工具压缩后外传
```

### 8.3 网络行为模型

```python
class NetworkBehaviorModel:
    """网络行为分析模型"""
    
    def detect_lateral_movement(self, events):
        """检测横向移动行为"""
        # 横向移动特征：
        # 1. 短时间内连接多个内部主机
        # 2. 使用非标准端口
        # 3. SMB/WMI/WinRM扫描行为
        # 4. 内部主机间认证尝试
        
        connections = defaultdict(set)  # src -> set(dst)
        
        for e in events:
            if e['event_type'] == 'network':
                connections[e['source_ip']].add(e.get('resource'))
        
        anomalies = []
        for src, dests in connections.items():
            # 一小时内连接超过15台不同内部主机
            if len(dests) > 15:
                anomalies.append({
                    'type': 'lateral_movement_scan',
                    'source': src,
                    'dest_count': len(dests),
                    'dests': list(dests),
                    'weight': 35
                })
                
        return anomalies
    
    def detect_data_exfiltration(self, events):
        """检测数据外泄行为"""
        # 外泄特征：
        # 1. 向外部大流量传输
        # 2. DNS隧道（长域名、TXT记录异常多）
        # 3. 加密流量到未知云存储
        # 4. 非工作时间外传数据
        
        anomalies = []
        
        # 统计每个源IP的外部流量
        external_traffic = defaultdict(int)
        for e in events:
            if e['event_type'] == 'network':
                dst = e.get('resource', '')
                if self._is_external(dst):
                    external_traffic[e['source_ip']] += e.get('bytes', 0)
        
        for src, total_bytes in external_traffic.items():
            if total_bytes > 500 * 1024 * 1024:  # >500MB外传
                anomalies.append({
                    'type': 'potential_exfiltration',
                    'source': src,
                    'total_bytes': total_bytes,
                    'weight': 40
                })
                
        return anomalies
```

### 8.4 特权行为模型

```
特权账户行为监控：

特权行为基线：
  ├── 管理操作时间：工作日9-18点
  ├── 操作类型：配置变更、用户管理、权限分配
  ├── 操作频率：日均5-10次管理操作
  ├── 目标系统：固定管理范围
  └── 会话来源：跳板机/堡垒机

高风险特权异常：
  ├── 非工作时间创建新管理员账户
  ├── 修改审计策略/关闭日志
  ├── 批量提升普通用户权限
  ├── 访问超出管理范围的系统
  ├── 直接SSH/RDP（绕过堡垒机）
  ├── 导出Active Directory数据库
  ├── 修改安全组策略
  └── 创建隐藏服务/计划任务
```

---

---

## 📋 内容审核与补充建议

> 针对「UEBA 行为模型」部分的内容审核结果：

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
