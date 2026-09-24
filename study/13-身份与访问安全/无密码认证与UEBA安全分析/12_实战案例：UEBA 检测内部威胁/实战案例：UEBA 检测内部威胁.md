# 实战案例：UEBA 检测内部威胁

### 12.1 场景背景

```
案例背景：
  某科技公司（约2000人），部署了UEBA系统
  
  攻击者画像：
  - 员工：陈某，研发部门高级工程师
  - 动机：即将跳槽至竞争对手公司
  - 目标：窃取核心源代码和技术文档
  
  攻击时间线：
  Day1-14: 侦察阶段
  Day15-20: 数据收集
  Day21: 数据外传
  Day22: 离职
```

### 12.2 UEBA 检测过程

```
Day1-14：侦察阶段异常

  异常1（Day1）：陈某首次在凌晨访问Git仓库
    └── 历史登录时间：9:00-20:00
    └── 当前登录：02:15
    └── 风险评分：25（low）

  异常2（Day3）：VPN从新IP登录
    └── 历史IP：公司网段 + 家庭宽带
    └── 当前IP：VPN出口IP（非公司VPN）
    └── 风险评分：15（low）

  异常3（Day7）：访问非本职项目仓库
    └── 历史访问：项目A、项目B仓库
    └── 当前访问：项目C、项目D、项目E仓库
    └── 风险评分：30（low-medium）

  ───────────────────────────────
  累计风险评分（Day7）：55（medium）
  系统动作：增加监控等级，邮件通知安全团队
  ───────────────────────────────

Day15-20：数据收集阶段异常

  异常4（Day15）：批量克隆仓库
    └── 1小时内git clone 15个仓库
    └── 基线：日均2-3次git操作
    └── 风险评分：35

  异常5（Day16）：访问技术文档目录
    └── 首次访问/secure/architecture/目录
    └── 包含系统架构图和API文档
    └── 风险评分：20

  异常6（Day18）：使用非常用工具
    └── EDR检测到运行7zip压缩
    └── 历史从未使用压缩工具
    └── 风险评分：15

  ───────────────────────────────
  累计风险评分（Day18）：85（critical）
  系统动作：SOAR自动触发调查剧本
           通知CISO，准备干预
  ───────────────────────────────

Day21：数据外传阶段

  异常7（Day21 01:00）：上传至个人云盘
    └── 代理日志检测到上传至pan.baidu.com
    └── 上传数据量：4.2GB
    └── 基线日均外传：< 100MB
    └── 风险评分：50

  异常8（Day21 01:15）：DNS隧道特征
    └── 异常长域名查询（base64编码数据）
    └── 可能使用DNS隧道外传小型文件
    └── 风险评分：30

  ───────────────────────────────
  实时累计风险评分（Day21 01:15）：95（critical）
  系统动作：自动阻断网络访问
           冻结陈某账号
           触发应急响应流程
  ───────────────────────────────
```

### 12.3 案例分析与改进

```
检测效果评估：

✓ 优势：
  - 行为基线准确识别了时间/位置/目录访问偏离
  - 累计风险评分机制有效聚合多维度异常
  - SOAR自动响应在数据外传时及时阻断

△ 不足：
  - 早期侦察阶段风险评分偏低，未触发高级别告警
  - 7zip使用未被充分关联到数据压缩外传意图
  - DNS隧道检测延迟（需更长基线对比）

改进措施：
  1. 调整敏感目录首次访问权重（提高至30）
  2. 增加"数据准备行为"检测模式（批量克隆+压缩=高风险组合）
  3. 对即将离职员工自动提高风险权重
  4. DNS隧道检测从规则匹配升级为流量统计异常检测
  5. 增加跨维度关联：时间异常+目录异常+工具异常 = 预外传模型
```

**UEBA规则优化建议：**

```python
# 优化后的复合行为检测规则
class CompositeBehaviorRule:
    """复合行为模式检测"""
    
    # 数据外传前置行为模式
    EXFIL_PREPARE_PATTERN = {
        'conditions': [
            {'type': 'new_directory_access', 'within_hours': 48},
            {'type': 'large_file_read', 'within_hours': 24},
            {'type': 'compression_tool_use', 'within_hours': 12},
            {'type': 'external_upload', 'within_hours': 6}
        ],
        'min_matches': 3,
        'combined_weight': 60,
        'alert_type': 'potential_data_exfiltration_chain'
    }
    
    def evaluate(self, user_events):
        """评估复合行为模式"""
        matched = []
        for cond in self.EXFIL_PREPARE_PATTERN['conditions']:
            if self._check_condition(user_events, cond):
                matched.append(cond)
                
        if len(matched) >= self.EXFIL_PREPARE_PATTERN['min_matches']:
            return {
                'alert_type': self.EXFIL_PREPARE_PATTERN['alert_type'],
                'matched_patterns': matched,
                'weight': self.EXFIL_PREPARE_PATTERN['combined_weight'],
                'recommendation': '检测到数据外传前置行为链，建议立即干预'
            }
        return None
```

---

---

