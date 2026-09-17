# UEBA 技术架构

### 7.1 整体架构

```
UEBA 技术架构：

┌─────────────────────────────────────────────────────┐
│                  数据采集层                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐  │
│  │AD/LDAP   │ │VPN日志   │ │DNS日志   │ │EDR终端   │  │
│  │认证日志   │ │网络日志   │ │代理日志   │ │文件操作   │  │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬─────┘  │
│       └───────────┬┴───────────┘             │       │
│                   ▼                           │       │
├───────────────────────────────────────────────┼───────┤
│              数据处理层                        │       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐    │       │
│  │数据清洗    │→│特征提取    │→│事件归一化  │    │       │
│  │去重/补全   │  │时间窗口    │  │实体关联    │    │       │
│  └──────────┘  └──────────┘  └──────────┘    │       │
│                   ▼                           │       │
├───────────────────────────────────────────────┼───────┤
│              行为建模层                        │       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐    │       │
│  │基线学习    │  │异常检测    │  │风险评估    │    │       │
│  │统计模型    │  │ML模型      │  │综合评分    │    │       │
│  │聚类分析    │  │时间序列    │  │优先级排序  │    │       │
│  └──────────┘  └──────────┘  └──────────┘    │       │
│                   ▼                           │       │
├───────────────────────────────────────────────┼───────┤
│              告警与响应层                       │       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐    │       │
│  │告警生成    │  │调查工单    │  │响应执行    │    │       │
│  │上下文关联  │  │SOAR集成    │  │自动阻断    │    │       │
│  └──────────┘  └──────────┘  └──────────┘    │       │
└───────────────────────────────────────────────┴───────┘
```

### 7.2 数据采集

**UEBA 需要采集的关键数据源：**

| 数据源 | 日志类型 | 关键字段 | 用途 |
|--------|----------|----------|------|
| AD/IdP | 登录成功/失败 | 用户、时间、IP、设备 | 登录行为分析 |
| VPN | 连接/断开 | 用户、IP、地理位置 | 位置行为分析 |
| DNS | 查询日志 | 源IP、域名、时间 | 网络行为分析 |
| 代理/防火墙 | HTTP/连接 | URL、目的IP、流量 | 数据访问分析 |
| EDR | 进程/文件 | 进程树、文件操作 | 终端行为分析 |
| 文件服务器 | 文件访问 | 用户、路径、操作 | 数据访问分析 |
| 邮件系统 | 收发日志 | 发件人、收件人、附件 | 信息外传分析 |
| DB审计 | 数据库操作 | 用户、SQL、表 | 数据查询分析 |

**数据归一化示例：**

```python
# 日志归一化处理
class LogNormalizer:
    """将多源异构日志归一化为统一事件格式"""
    
    SCHEMA = {
        'event_type': str,      # login/file_access/network/process
        'timestamp': float,     # Unix时间戳
        'user': str,            # 归一化用户名
        'entity': str,          # 设备/主机名
        'source_ip': str,       # 源IP
        'action': str,          # 具体操作
        'resource': str,        # 目标资源
        'result': str,          # success/failure
        'bytes': int,           # 传输数据量
        'raw': dict             # 原始日志
    }
    
    def normalize_windows_log(self, event):
        """Windows安全日志归一化"""
        # Event ID 4624=登录成功, 4625=登录失败
        event_id = event.get('EventID')
        
        return {
            'event_type': 'login',
            'timestamp': self._parse_windows_time(event['TimeCreated']),
            'user': self._extract_user(event, ['TargetUserName']),
            'entity': event.get('Computer'),
            'source_ip': event.get('IpAddress'),
            'action': f'logon_{event_id}',
            'result': 'success' if event_id == 4624 else 'failure',
            'logon_type': event.get('LogonType'),  # 2=交互, 10=远程, 3=网络
            'raw': event
        }
    
    def normalize_vpn_log(self, event):
        """VPN日志归一化"""
        return {
            'event_type': 'login',
            'timestamp': event['timestamp'],
            'user': event['user'],
            'entity': 'vpn-gateway',
            'source_ip': event['src_ip'],
            'geo': self._ip_to_geo(event['src_ip']),
            'action': 'vpn_connect' if event['action'] == 'connect' else 'vpn_disconnect',
            'result': event.get('status', 'success'),
            'session_duration': event.get('duration'),
            'raw': event
        }
```

### 7.3 行为基线

行为基线是 UEBA 的核心，通过对历史行为数据的学习建立"正常"行为模型。

**基线建模方法：**

```python
import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta

class BehaviorBaseline:
    """用户行为基线模型"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.baselines = {}
        
    def build_login_baseline(self, historical_events):
        """构建登录行为基线"""
        login_events = [e for e in historical_events 
                        if e['event_type'] == 'login' and e['result'] == 'success']
        
        if not login_events:
            return None
            
        # 时间模式：每个小时登录概率
        hour_counts = np.zeros(24)
        for e in login_events:
            dt = datetime.fromtimestamp(e['timestamp'])
            hour_counts[dt.hour] += 1
        
        total = hour_counts.sum()
        if total > 0:
            hour_prob = hour_counts / total
        else:
            hour_prob = np.ones(24) / 24
            
        # 地理位置模式
        geo_counts = defaultdict(int)
        for e in login_events:
            geo = e.get('geo', {}).get('country', 'unknown')
            geo_counts[geo] += 1
        geo_prob = {k: v/total for k, v in geo_counts.items()}
        
        # 设备模式
        device_counts = defaultdict(int)
        for e in login_events:
            device_counts[e.get('entity', 'unknown')] += 1
        device_prob = {k: v/total for k, v in device_counts.items()}
        
        # IP地址统计
        ips = [e.get('source_ip') for e in login_events if e.get('source_ip')]
        
        self.baselines['login'] = {
            'hour_prob': hour_prob,           # 每小时登录概率分布
            'hour_mean': np.argmax(hour_prob),# 最常登录时段
            'hour_std': np.std([datetime.fromtimestamp(e['timestamp']).hour 
                               for e in login_events]),
            'geo_prob': geo_prob,             # 地理位置概率分布
            'device_prob': device_prob,       # 设备概率分布
            'known_ips': set(ips),            # 已知IP集合
            'login_frequency': len(login_events) / 30,  # 日均登录次数
            'last_10_ips': ips[-10:],         # 最近10个登录IP
            'sample_count': len(login_events)
        }
        
    def build_file_access_baseline(self, historical_events):
        """构建文件访问行为基线"""
        file_events = [e for e in historical_events 
                       if e['event_type'] == 'file_access']
        
        # 访问目录模式
        dir_counts = defaultdict(int)
        for e in file_events:
            path = e.get('resource', '')
            top_dir = '/'.join(path.split('/')[:3])  # 前三级目录
            dir_counts[top_dir] += 1
        
        total = sum(dir_counts.values())
        
        # 数据量模式
        bytes_transferred = [e.get('bytes', 0) for e in file_events]
        
        self.baselines['file_access'] = {
            'dir_prob': {k: v/total for k, v in dir_counts.items()},
            'access_frequency': len(file_events) / 30,
            'avg_bytes': np.mean(bytes_transferred) if bytes_transferred else 0,
            'p95_bytes': np.percentile(bytes_transferred, 95) if bytes_transferred else 0,
            'sample_count': len(file_events)
        }
        
    def build_network_baseline(self, historical_events):
        """构建网络行为基线"""
        net_events = [e for e in historical_events 
                      if e['event_type'] == 'network']
        
        # 目的地域名/IP模式
        dest_counts = defaultdict(int)
        for e in net_events:
            dest = e.get('resource', '')
            dest_counts[dest] += 1
            
        total = sum(dest_counts.values())
        
        # 连接时间分布
        hour_counts = np.zeros(24)
        for e in net_events:
            dt = datetime.fromtimestamp(e['timestamp'])
            hour_counts[dt.hour] += 1
            
        self.baselines['network'] = {
            'dest_prob': {k: v/total for k, v in dest_counts.items()},
            'hour_prob': hour_counts / total if total > 0 else np.ones(24)/24,
            'known_dests': set(dest_counts.keys()),
            'connection_frequency': len(net_events) / 30,
            'sample_count': len(net_events)
        }
```

### 7.4 异常检测

```python
from scipy import stats

class AnomalyDetector:
    """异常检测引擎"""
    
    def __init__(self, baselines):
        self.baselines = baselines
        
    def detect_login_anomalies(self, event):
        """检测登录异常"""
        anomalies = []
        risk_score = 0
        baseline = self.baselines.get('login')
        
        if not baseline:
            return anomalies, 0
            
        dt = datetime.fromtimestamp(event['timestamp'])
        
        # 1. 异常登录时间
        hour_prob = baseline['hour_prob'][dt.hour]
        if hour_prob < 0.01:  # 该时段登录概率极低
            anomalies.append({
                'type': 'unusual_login_time',
                'detail': f'登录时间{dt.hour}:00在历史记录中概率{hour_prob:.4f}',
                'weight': 20
            })
            risk_score += 20
            
        # 2. 异常地理位置
        geo = event.get('geo', {}).get('country', 'unknown')
        geo_prob = baseline['geo_prob'].get(geo, 0)
        if geo_prob < 0.05:  # 该地理位置概率极低
            anomalies.append({
                'type': 'unusual_location',
                'detail': f'登录地点{geo}在历史记录中概率{geo_prob:.4f}',
                'weight': 30
            })
            risk_score += 30
            
            # 3. 不可能旅行（速度悖论）
            if baseline.get('last_10_ips'):
                last_ip = baseline['last_10_ips'][-1]
                last_geo = self._ip_to_geo(last_ip)
                distance = self._geo_distance(last_geo, event['geo'])
                time_diff = event['timestamp'] - baseline.get('last_login_time', 0)
                speed = distance / (time_diff / 3600) if time_diff > 0 else float('inf')
                
                if speed > 900:  # 超过900km/h不可能
                    anomalies.append({
                        'type': 'impossible_travel',
                        'detail': f'从{last_geo}到{event["geo"]}距离{distance:.0f}km，'
                                  f'时间差{time_diff/3600:.1f}h，速度{speed:.0f}km/h',
                        'weight': 40
                    })
                    risk_score += 40
                    
        # 4. 新设备
        entity = event.get('entity', 'unknown')
        if entity not in baseline['device_prob']:
            anomalies.append({
                'type': 'new_device',
                'detail': f'新设备{entity}首次登录',
                'weight': 15
            })
            risk_score += 15
            
        # 5. 新IP地址
        source_ip = event.get('source_ip')
        if source_ip and source_ip not in baseline['known_ips']:
            anomalies.append({
                'type': 'new_ip',
                'detail': f'新IP{source_ip}首次出现',
                'weight': 10
            })
            risk_score += 10
            
        # 6. 登录频率突增
        recent_count = self._count_recent_events(event['timestamp'], hours=1)
        expected = baseline['login_frequency'] / 24
        if recent_count > expected * 5:
            anomalies.append({
                'type': 'frequency_spike',
                'detail': f'1小时内登录{recent_count}次，基线{expected:.1f}次/小时',
                'weight': 15
            })
            risk_score += 15
            
        return anomalies, min(risk_score, 100)
    
    def detect_file_access_anomalies(self, event):
        """检测文件访问异常"""
        anomalies = []
        risk_score = 0
        baseline = self.baselines.get('file_access')
        
        if not baseline:
            return anomalies, 0
            
        # 1. 访问新目录
        path = event.get('resource', '')
        top_dir = '/'.join(path.split('/')[:3])
        if top_dir not in baseline['dir_prob']:
            anomalies.append({
                'type': 'new_directory_access',
                'detail': f'首次访问目录{top_dir}',
                'weight': 15
            })
            risk_score += 15
            
        # 2. 异常数据量
        bytes_transferred = event.get('bytes', 0)
        if bytes_transferred > baseline['p95_bytes'] * 3:
            anomalies.append({
                'type': 'large_data_transfer',
                'detail': f'传输{bytes_transferred/1024/1024:.1f}MB，'
                          f'超过P95基线({baseline["p95_bytes"]/1024/1024:.1f}MB)3倍',
                'weight': 25
            })
            risk_score += 25
            
        # 3. 访问频率突增
        recent_count = self._count_recent_events(event['timestamp'], hours=1)
        expected = baseline['access_frequency'] / 24
        if recent_count > expected * 10:
            anomalies.append({
                'type': 'access_burst',
                'detail': f'1小时内访问{recent_count}次，基线{expected:.1f}次/小时',
                'weight': 20
            })
            risk_score += 20
            
        return anomalies, min(risk_score, 100)
```

### 7.5 风险评估与告警

```python
class RiskScorer:
    """综合风险评估引擎"""
    
    # 用户风险权重
    USER_WEIGHTS = {
        'normal': 1.0,
        'privileged': 1.5,       # 特权用户权重更高
        'executive': 1.3,        # 高管
        'contractor': 1.2        # 外包人员
    }
    
    def calculate_risk(self, user_id, events, anomalies):
        """计算综合风险评分"""
        base_score = sum(a['weight'] for a in anomalies)
        
        # 用户类型加权
        user_type = self._get_user_type(user_id)
        weight = self.USER_WEIGHTS.get(user_type, 1.0)
        weighted_score = base_score * weight
        
        # 时间衰减（老异常分数降低）
        now = time.time()
        recent_anomalies = []
        for a in anomalies:
            age = now - a.get('timestamp', now)
            decay = np.exp(-age / 86400)  # 指数衰减，1天衰减到1/e
            recent_anomalies.append({
                **a,
                'decayed_weight': a['weight'] * decay
            })
        
        final_score = min(sum(a['decayed_weight'] for a in recent_anomalies), 100)
        
        # 风险等级
        if final_score >= 80:
            level = 'critical'
            action = '立即阻断+人工调查'
        elif final_score >= 60:
            level = 'high'
            action = '强制MFA+通知安全团队'
        elif final_score >= 40:
            level = 'medium'
            action = '增加监控+邮件通知'
        elif final_score >= 20:
            level = 'low'
            action = '记录日志+关注'
        else:
            level = 'info'
            action = '无需操作'
            
        return {
            'user_id': user_id,
            'risk_score': final_score,
            'risk_level': level,
            'recommended_action': action,
            'anomalies': recent_anomalies,
            'context': self._build_context(user_id, events)
        }
```

---

---

## 📋 内容审核与补充建议

> 针对「UEBA 技术架构」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
