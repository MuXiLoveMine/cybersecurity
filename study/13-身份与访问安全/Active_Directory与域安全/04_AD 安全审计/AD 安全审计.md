# AD 安全审计

### 4.1 AD 审计日志关键事件

| 事件ID | 日志名称 | 说明 |
|--------|---------|------|
| 4720 | Security | 创建用户账户 |
| 4722 | Security | 用户账户启用 |
| 4726 | Security | 用户账户删除 |
| 4728 | Security | 成员加入全局安全组 |
| 4738 | Security | 用户账户修改 |
| 4740 | Security | 账户锁定 |
| 4768 | Security | Kerberos TGT 请求（AS-REQ） |
| 4769 | Security | Kerberos ST 请求（TGS-REQ） |
| 4771 | Security | Kerberos 预认证失败 |
| 4776 | Security | NTLM 认证 |
| 4662 | Security | 目录服务对象操作（含 DCSync） |
| 5136 | Security | 目录服务对象修改 |
| 4944 | Security | 审核策略变更 |

```powershell
# 查询 DCSync 相关事件
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4662} |
  Where-Object {$_.Message -match "1131f6aa-9c07-11d1-f79f-00c04fc2dcd2|1131f6ad-9c07-11d1-f79f-00c04fc2dcd2"} |
  Select-Object TimeCreated, SubjectUserName, TargetUserName
# 1131f6aa = DS-Replication-Get-Changes
# 1131f6ad = DS-Replication-Get-Changes-All（DCSync 所需权限）
```

### 4.2 BloodHound 蓝队使用

蓝队使用 BloodHound 识别攻击路径并消除高权路径：

```
# Cypher 查询：查找从普通用户到 Domain Admins 的最短路径
MATCH (n:User) WHERE NOT n.admincount=true
MATCH p=shortestPath((n)-[*1..15]->(g:Group {name:"DOMAIN ADMINS@CORP.LOCAL"}))
RETURN p

# 查找所有可 DCSync 的路径
MATCH (n)-[:GetChangesAll]->(g:Domain) RETURN n.name, g.name

# 查找非约束委派
MATCH (c:Computer {unconstraineddelegation:true}) RETURN c.name
```

### 4.3 PingCastle / ADSI 安全评估

```bash
# PingCastle（AD 安全评估工具）
# 生成 HTML 报告，评分 A-F
PingCastle.exe --server dc01.corp.local --user admin --password *** --output report.html

# 检查项：域功能级别、管理员数量、委派配置、密码策略、信任关系等
```

### 4.4 Python AD 安全检查脚本示例

```python
"""
AD 安全检查脚本 - 通过 LDAP 查询检测常见配置风险
依赖: pip install ldap3
"""

from ldap3 import Server, Connection, ALL
from datetime import datetime
import json

class ADSecurityChecker:
    def __init__(self, server, bind_dn, password):
        self.server = Server(server, get_info=ALL)
        self.conn = Connection(self.server, user=bind_dn, password=password, auto_bind=True)
        self.base_dn = None
        self._get_base_dn()

    def _get_base_dn(self):
        """获取域 DN"""
        if 'defaultNamingContext' in self.server.info.other:
            self.base_dn = self.server.info.other['defaultNamingContext'][0]
        else:
            self.base_dn = 'DC=corp,DC=local'

    def check_asrep_roastable(self):
        """检查不需要预认证的账户（AS-REP Roasting 风险）"""
        search_filter = '(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))'
        self.conn.search(self.base_dn, search_filter, attributes=['sAMAccountName', 'userAccountControl'])
        results = []
        for entry in self.conn.entries:
            results.append({'account': str(entry.sAMAccountName), 'risk': 'AS-REP Roasting'})
        return results

    def check_unconstrained_delegation(self):
        """检查非约束委派账户"""
        search_filter = '(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=524288))'
        self.conn.search(self.base_dn, search_filter, attributes=['sAMAccountName', 'userAccountControl'])
        results = []
        for entry in self.conn.entries:
            results.append({'account': str(entry.sAMAccountName), 'risk': 'Unconstrained Delegation'})
        return results

    def check_admincount(self):
        """检查高权属性用户"""
        search_filter = '(adminCount=1)'
        self.conn.search(self.base_dn, search_filter, attributes=['sAMAccountName', 'memberOf'])
        results = []
        for entry in self.conn.entries:
            results.append({'account': str(entry.sAMAccountName), 'risk': 'Admin-tier account'})
        return results

    def check_dormant_accounts(self, days=90):
        """检查长期未登录的休眠账户"""
        search_filter = '(&(objectClass=user)(!lastLogon=0))'
        self.conn.search(self.base_dn, search_filter, attributes=['sAMAccountName', 'lastLogon'])
        threshold = (datetime.now().timestamp() - days * 86400) * 10**7  # AD 时间戳格式
        results = []
        for entry in self.conn.entries:
            try:
                last_logon = int(str(entry.lastLogon))
                if last_logon < threshold and last_logon > 0:
                    results.append({'account': str(entry.sAMAccountName), 'risk': f'Dormant>{days}d'})
            except (ValueError, TypeError):
                continue
        return results

    def run_all_checks(self):
        """运行所有检查"""
        all_risks = []
        print("[*] Checking AS-REP Roastable accounts...")
        all_risks.extend(self.check_asrep_roastable())
        print("[*] Checking unconstrained delegation...")
        all_risks.extend(self.check_unconstrained_delegation())
        print("[*] Checking admin-tier accounts...")
        all_risks.extend(self.check_admincount())
        print("[*] Checking dormant accounts...")
        all_risks.extend(self.check_dormant_accounts())
        return all_risks


if __name__ == '__main__':
    checker = ADSecurityChecker(
        server='ldap://dc01.corp.local',
        bind_dn='admin@corp.local',
        password='YourPassword'
    )
    risks = checker.run_all_checks()
    print(f"\n[+] Found {len(risks)} risk(s):")
    for r in risks:
        print(f"    - {r['account']}: {r['risk']}")
    # 输出 JSON 便于集成到 SIEM
    print(json.dumps(risks, indent=2, ensure_ascii=False))
```

---

---

