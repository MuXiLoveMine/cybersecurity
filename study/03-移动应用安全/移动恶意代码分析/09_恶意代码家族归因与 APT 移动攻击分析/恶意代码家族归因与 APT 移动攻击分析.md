# 恶意代码家族归因与 APT 移动攻击分析

### 9.1 家族归因方法

```
恶意代码家族归因流程：

1. 代码特征比对
   ├── 代码结构相似度（包名、类名、方法名）
   ├── 代码复用检测（相同函数实现）
   ├── 编译器/构建工具指纹
   └── 代码注释和风格

2. 基础设施关联
   ├── C&C 域名/ IP 关联
   ├── SSL 证书指纹
   ├── 注册信息（WHOIS）
   └── DNS 解析模式

3. 行为模式关联
   ├── 攻击手法（TTPs）相似度
   ├── 目标行业/地域重合
   ├── 攻击时间窗口
   └── 恶意功能实现方式

4. 资源文件关联
   ├── 图标/图片相似度
   ├── 字符串资源重复
   ├── 加密算法实现
   └── 配置文件格式

5. 报告与情报关联
   ├── VirusTotal 检测结果
   ├── 威胁情报平台匹配
   ├── 公开分析报告对比
   └── MITRE ATT&CK 映射
```

```python
#!/usr/bin/env python3
"""
恶意代码家族归因工具
通过多维特征匹配将样本归因到已知家族
"""

import hashlib
import json
from collections import defaultdict

class FamilyAttribution:
    def __init__(self):
        # 已知家族特征库
        self.family_signatures = {
            'Cerberus': {
                'package_patterns': [r'com\.\w+\.battery', r'com\.\w+\.flash'],
                'permissions': ['BIND_ACCESSIBILITY_SERVICE', 'SYSTEM_ALERT_WINDOW'],
                'c2_patterns': [r'https?://\w+\.ru/', r'https?://\w+\.cc/'],
                'api_signatures': ['dispatchGesture', 'performAccessibilityAction'],
                'native_libs': ['libnative.so'],
                'bank_packages': ['com.bankamerica', 'com.chase'],
                'strings': ['Cerberus', 'accessibility']
            },
            'Anubis': {
                'package_patterns': [r'com\.\w+\.cleaner', r'com\.\w+\.optimizer'],
                'permissions': ['SYSTEM_ALERT_WINDOW', 'READ_SMS', 'SEND_SMS'],
                'c2_patterns': [r'https?://\w+\.io/'],
                'api_signatures': ['KeyguardManager', 'requestOverlayPermission'],
                'strings': ['Anubis', 'bot_id']
            },
            'FluBot': {
                'package_patterns': [r'com\.\w+\.delivery', r'com\.\w+\.post'],
                'permissions': ['READ_SMS', 'RECEIVE_SMS', 'SYSTEM_ALERT_WINDOW'],
                'c2_patterns': [r'https?://\w+\.xyz/'],
                'api_signatures': ['onAccessibilityEvent'],
                'strings': ['FluBot', 'rat']
            }
        }

    def attribute(self, sample_features):
        """归因分析"""
        scores = defaultdict(float)

        for family, signature in self.family_signatures.items():
            score = 0
            total_checks = 0

            # 包名模式匹配
            for pattern in signature['package_patterns']:
                total_checks += 1
                for pkg in sample_features.get('packages', []):
                    if __import__('re').search(pattern, pkg):
                        score += 1
                        break

            # 权限匹配
            for perm in signature['permissions']:
                total_checks += 1
                if perm in sample_features.get('permissions', []):
                    score += 1

            # C&C 模式匹配
            for pattern in signature['c2_patterns']:
                total_checks += 1
                for url in sample_features.get('urls', []):
                    if __import__('re').search(pattern, url):
                        score += 1
                        break

            # API 签名匹配
            for api in signature['api_signatures']:
                total_checks += 1
                if api in sample_features.get('apis', []):
                    score += 1

            # 字符串匹配
            for string in signature['strings']:
                total_checks += 1
                if any(string.lower() in s.lower()
                       for s in sample_features.get('strings', [])):
                    score += 1

            scores[family] = score / total_checks if total_checks > 0 else 0

        # 排序并返回最匹配的家族
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return {
            'best_match': ranked[0][0] if ranked[0][1] > 0.5 else 'Unknown',
            'confidence': ranked[0][1],
            'all_scores': dict(ranked)
        }
```

### 9.2 APT 移动攻击分析

```
移动 APT 攻击概览：

┌─────────────────────────────────────────────────────────────┐
│              知名 APT 移动攻击活动                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Pegasus (NSO Group)                                     │
│  ├── 目标：记者、活动家、政治人物                              │
│  ├── 平台：iOS + Android                                     │
│  ├── 技术：零点击漏洞、内核提权、多阶段植入                    │
│  ├── 检测工具：MVT                                            │
│  └── 关联APT：NSO Group / 41                            │
│                                                             │
│  2. Predator (Cytrox / Intellexa)                            │
│  ├── 目标：政治人物、记者                                     │
│  ├── 平台：Android                                            │
│  ├── 技术：零点击漏洞、Loader 椆架                           │
│  └── 关联APT：Intellexa Alliance                             │
│                                                             │
│  3. BeagleBoy / Beagle (Google Project Zero 发现)            │
│  ├── 目标：特定地区用户                                      │
│  ├── 平台：Android                                            │
│  ├── 技术：0-day exploit chain                               │
│  └── 关联APT：待定                                           │
│                                                             │
│  4. Bitter APT (T-APT-17)                                    │
│  ├── 目标：南亚地区政府/军事                                  │
│  ├── 平台：Android                                            │
│  ├── 技术：伪装系统更新应用                                   │
│  └── 功能：窃取文件、通话、短信                              │
│                                                             │
│  5. SideWinder (APT-37)                                     │
│  ├── 目标：巴基斯坦军事/政府                                  │
│  ├── 平台：Android                                            │
│  ├── 技术：伪装安全应用                                       │
│  └── 功能：截图、录音、文件窃取                              │
│                                                             │
│  6. Confucius (APT-36 / Transparent Tribe)                  │
│  ├── 目标：印度军事/政府人员                                  │
│  ├── 平台：Android                                            │
│  ├── 技术：伪装聊天应用                                       │
│  └── 功能：通讯录窃取、位置追踪、短信读取                    │
│                                                             │
│  7. Hermit (RCS / Tykelab)                                  │
│  ├── 目标：哈萨克斯坦活动家                                   │
│  ├── 平台：Android                                            │
│  ├── 技术：伪装运营商应用                                     │
│  └── 功能：通话录音、短信截获、文件窃取                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 9.3 MITRE ATT&CK 移动矩阵映射

```
移动恶意代码 ATT&CK 技术映射：

ATT&CK Mobile Matrix:

┌────────────────┬──────────────────────────────────────────┐
│  战术            │  技术（恶意软件使用示例）                   │
├────────────────┼──────────────────────────────────────────┤
│  Initial Access │  钓鱼短信 (T1660)                         │
│  初始访问        │  钓鱼应用商店链接 (T1661)                  │
│                  │  利用零日漏洞 (T1407)                     │
│                  │  企业证书分发 (T1409)                     │
├────────────────┼──────────────────────────────────────────┤
│  Persistence    │  设备管理器 (T1404)                       │
│  持久化          │  开机自启 (T1406)                         │
│                  │  无障碍服务 (T1419)                       │
│                  │  MDM 描述文件 (T1413)                    │
├────────────────┼──────────────────────────────────────────┤
│  Defense        │  混淆代码 (T1408)                         │
│  Evasion        │  隐藏图标 (T1410)                         │
│  防御绕过        │  动态加载 (T1418)                        │
│                  │  检测安全应用 (T1417)                    │
│                  │  拦截卸载请求 (T1416)                    │
├────────────────┼──────────────────────────────────────────┤
│  Credential     │  短信拦截 OTP (T1412)                     │
│  Access         │  键盘记录 (T1411)                        │
│  凭证访问        │  Overlay 攻击 (T1414)                    │
│                  │  屏幕截图 (T1415)                        │
├────────────────┼──────────────────────────────────────────┤
│  Collection    │  通讯录窃取 (T1435)                       │
│  收集            │  位置追踪 (T1436)                        │
│                  │  通话录音 (T1437)                        │
│                  │  文件收集 (T1438)                        │
│                  │  剪贴板窃取 (T1439)                     │
├────────────────┼──────────────────────────────────────────┤
│  C2            │  HTTP C&C (T1444)                         │
│  命令与控制      │  DGA 域名 (T1445)                        │
│                  │  DNS 隧道 (T1446)                        │
│                  │  加密通信 (T1447)                        │
├────────────────┼──────────────────────────────────────────┤
│  Exfiltration  │  HTTP 上传 (T1448)                        │
│  数据外传        │  加密上传 (T1449)                        │
│                  │  多级跳板传输 (T1450)                    │
└────────────────┴──────────────────────────────────────────┘
```

---

---

