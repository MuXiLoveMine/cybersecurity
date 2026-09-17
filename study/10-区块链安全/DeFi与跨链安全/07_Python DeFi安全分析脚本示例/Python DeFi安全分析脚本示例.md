# Python DeFi安全分析脚本示例

### 7.1 智能合约重入检测脚本（使用AST分析）

```python
#!/usr/bin/env python3
"""
DeFi安全分析 - 智能合约重入漏洞检测（AST分析）
使用Solidity AST检测潜在重入漏洞模式
"""

import re
import json
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Severity(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"


@dataclass
class Finding:
    """漏洞发现"""
    severity: Severity
    title: str
    description: str
    line: Optional[int] = None
    pattern: Optional[str] = None


class ReentrancyDetector:
    """基于模式匹配的Solidity重入漏洞检测器"""

    # 外部调用模式（可能触发回调的函数）
    EXTERNAL_CALL_PATTERNS = [
        r'\.call\s*\{',
        r'\.call\s*\(',
        r'\.delegatecall\s*\(',
        r'\.staticcall\s*\(',
        r'\.transfer\s*\(',
        r'\.send\s*\(',
        r'token\.transfer\s*\(',
        r'token\.transferFrom\s*\(',
        r'IERC20\(.*\)\.transfer\s*\(',
        r'msg\.sender\.call\s*\{',
    ]

    # 状态更新模式
    STATE_UPDATE_PATTERNS = [
        r'\w+\s*[\+\-\*\/]?=\s*',
        r'\w+\s*\[\s*\w+\s*\]\s*=\s*',
        r'\.push\s*\(',
        r'\.pop\s*\(',
        r'\.delete\s*',
        r'delete\s+\w+',
    ]

    # nonReentrant修饰符
    REENTRANCY_GUARD_PATTERN = r'nonReentrant|nonReentrancyGuard|ReentrancyGuard'

    # Checks-Effects-Interactions违规模式
    # 外部调用后跟状态更新（非CEI顺序）
    CEI_VIOLATION = re.compile(
        r'(?:transfer|send|call|delegatecall|staticcall)\s*\('
        r'.*?\n'  # 调用行
        r'[^}]*?'  # 中间内容
        r'(?:\w+\s*[\+\-\*/]?=|delete\s+\w+|\w+\[.*?\]\s*=)',
        re.MULTILINE | re.DOTALL
    )

    def __init__(self):
        self.findings: list[Finding] = []

    def check_non_reentrant_modifier(self, source: str) -> bool:
        """检查是否使用了nonReentrant修饰符"""
        return bool(re.search(self.REENTRANCY_GUARD_PATTERN, source, re.IGNORECASE))

    def find_external_calls(self, source: str) -> list[tuple[int, str]]:
        """查找外部调用及其行号"""
        results = []
        for i, line in enumerate(source.split('\n'), 1):
            stripped = line.strip()
            # 跳过注释行
            if stripped.startswith('//') or stripped.startswith('/*'):
                continue
            for pattern in self.EXTERNAL_CALL_PATTERNS:
                if re.search(pattern, stripped):
                    results.append((i, stripped))
                    break
        return results

    def find_state_updates_after_call(
        self, source: str, call_line: int
    ) -> list[tuple[int, str]]:
        """在外部调用行之后查找状态更新"""
        lines = source.split('\n')
        updates = []
        # 在调用行之后检查（同函数内）
        brace_depth = 0
        in_function = False
        for i in range(call_line, min(call_line + 20, len(lines))):
            line = lines[i].strip()
            if '{' in lines[i]:
                brace_depth += lines[i].count('{')
                in_function = True
            if '}' in lines[i]:
                brace_depth -= lines[i].count('}')
            if in_function and brace_depth <= 0 and i > call_line:
                break
            for pattern in self.STATE_UPDATE_PATTERNS:
                if re.search(pattern, line) and not line.startswith('//'):
                    # 排除require/assert/emit中的赋值
                    if not any(kw in line for kw in ['require', 'assert', 'emit', 'return']):
                        updates.append((i + 1, line))
                        break
        return updates

    def analyze_function(self, source: str, func_name: str,
                         func_source: str) -> list[Finding]:
        """分析单个函数的重入风险"""
        findings = []

        has_guard = self.check_non_reentrant_modifier(func_source)
        external_calls = self.find_external_calls(func_source)

        if not external_calls:
            return findings

        for call_line, call_text in external_calls:
            state_updates = self.find_state_updates_after_call(
                func_source, call_line - 1
            )

            if state_updates and not has_guard:
                # 有状态更新在外部调用之后且无nonReentrant保护
                findings.append(Finding(
                    severity=Severity.HIGH,
                    title=f"重入风险: {func_name}",
                    description=(
                        f"函数 {func_name} 在第{call_line}行执行外部调用后，"
                        f"在第{state_updates[0][0]}行更新状态。"
                        f"这违反了Checks-Effects-Interactions模式，"
                        f"且未使用nonReentrant修饰符。"
                        f"\n  外部调用: {call_text.strip()}"
                        f"\n  状态更新: {state_updates[0][1].strip()}"
                    ),
                    line=call_line,
                    pattern="External call before state update"
                ))
            elif state_updates and has_guard:
                # 有nonReentrant但有CEI违规（中等风险）
                findings.append(Finding(
                    severity=Severity.LOW,
                    title=f"CEI模式违规: {func_name}",
                    description=(
                        f"函数 {func_name} 虽有nonReentrant保护，"
                        f"但仍建议遵循Checks-Effects-Interactions模式。"
                    ),
                    line=call_line,
                    pattern="CEI violation (guarded)"
                ))

        return findings

    def extract_functions(self, source: str) -> dict[str, str]:
        """提取每个函数的源代码"""
        functions = {}
        # 匹配 function 定义
        func_pattern = re.compile(
            r'function\s+(\w+)\s*\([^)]*\)[^{]*\{',
            re.MULTILINE
        )
        for match in func_pattern.finditer(source):
            func_name = match.group(1)
            start = match.start()
            # 找到匹配的大括号
            brace_count = 0
            end = match.end() - 1  # 指向 '{'
            for i in range(match.end() - 1, len(source)):
                if source[i] == '{':
                    brace_count += 1
                elif source[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            functions[func_name] = source[start:end]
        return functions

    def analyze(self, source: str) -> list[Finding]:
        """分析完整合约源码"""
        self.findings = []

        # 提取函数
        functions = self.extract_functions(source)

        for func_name, func_source in functions.items():
            func_findings = self.analyze_function(source, func_name, func_source)
            self.findings.extend(func_findings)

        # 检查合约级别的nonReentrant导入
        if not self.check_non_reentrant_modifier(source):
            if any(f.severity == Severity.HIGH for f in self.findings):
                self.findings.append(Finding(
                    severity=Severity.INFO,
                    title="缺少ReentrancyGuard",
                    description="合约未导入ReentrancyGuard，建议从OpenZeppelin导入",
                    pattern="Missing ReentrancyGuard import"
                ))

        return self.findings


# 测试用例
VULNERABLE_CONTRACT = """
pragma solidity ^0.8.0;

contract VulnerableVault {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance");

        // 外部调用在前
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "Transfer failed");

        // 状态更新在后 —— 重入漏洞！
        balances[msg.sender] = 0;
    }
}
"""

SAFE_CONTRACT = """
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract SafeVault is ReentrancyGuard {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() external nonReentrant {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance");

        // 1. Effects: 先更新状态
        balances[msg.sender] = 0;

        // 2. Interactions: 后执行外部调用
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "Transfer failed");
    }
}
"""


def main():
    print("=" * 70)
    print("DeFi安全分析 - 智能合约重入漏洞检测（AST模式分析）")
    print("=" * 70)

    detector = ReentrancyDetector()

    # 测试漏洞合约
    print("\n[1] 分析漏洞合约: VulnerableVault")
    print("-" * 50)
    findings = detector.analyze(VULNERABLE_CONTRACT)
    if findings:
        for f in findings:
            print(f"\n  [{f.severity.value}] {f.title}")
            if f.line:
                print(f"  行号: {f.line}")
            print(f"  描述: {f.description}")
    else:
        print("  未发现问题")

    # 测试安全合约
    print("\n\n[2] 分析安全合约: SafeVault")
    print("-" * 50)
    findings = detector.analyze(SAFE_CONTRACT)
    if findings:
        for f in findings:
            print(f"\n  [{f.severity.value}] {f.title}")
            if f.line:
                print(f"  行号: {f.line}")
            print(f"  描述: {f.description}")
    else:
        print("  未发现问题（合约使用了nonReentrant + CEI模式）")

    print("\n" + "=" * 70)
    print("检测完成。")
    print("提示: 此脚本使用正则模式匹配，存在误报/漏报。")
    print("      生产环境应结合Slither/Mythril等专业工具使用。")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

### 7.2 闪电贷攻击检测脚本（模拟链上数据分析）

```python
#!/usr/bin/env python3
"""
DeFi安全分析 - 闪电贷攻击检测（模拟链上数据分析）
通过分析交易模式检测可能的闪电贷攻击
"""

import time
import random
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Optional
from enum import Enum


class AlertType(Enum):
    FLASH_LOAN_LARGE = "大额闪电贷"
    PRICE_MANIPULATION = "预言机价格操纵"
    GOVERNANCE_RUSH = "治理投票急速通过"
    LIQUIDITY_DRAIN = "流动性异常抽取"
    COMBINED_ATTACK = "组合攻击模式"


@dataclass
class Transaction:
    """模拟链上交易"""
    tx_hash: str
    block_number: int
    timestamp: float
    sender: str
    actions: list[dict]  # 交易中的操作序列
    gas_used: int = 0
    flash_loan_amount: float = 0.0
    flash_loan_source: str = ""


@dataclass
class Alert:
    """安全告警"""
    alert_type: AlertType
    tx_hash: str
    description: str
    severity: str  # Critical/High/Medium
    details: dict


class FlashLoanDetector:
    """闪电贷攻击检测引擎"""

    def __init__(self):
        self.alerts: list[Alert] = []
        # 基线数据
        self.normal_daily_volume: float = 50_000_000  # $50M日均交易量
        self.price_history: dict[str, list[tuple[float, float]]] = {}
        self.protocol_tvl: dict[str, float] = {}

    def check_large_flash_loan(self, tx: Transaction) -> Optional[Alert]:
        """检测大额闪电贷"""
        if tx.flash_loan_amount <= 0:
            return None

        # 闪电贷金额超过协议TVL的10%
        tvl_ratio = tx.flash_loan_amount / max(
            self.protocol_tvl.get("total", 1), 1
        )
        if tvl_ratio > 0.10:
            severity = "Critical" if tvl_ratio > 0.30 else "High"
            return Alert(
                alert_type=AlertType.FLASH_LOAN_LARGE,
                tx_hash=tx.tx_hash,
                description=(
                    f"大额闪电贷: ${tx.flash_loan_amount:,.0f} "
                    f"占协议TVL的{tvl_ratio*100:.1f}%"
                ),
                severity=severity,
                details={
                    "amount": tx.flash_loan_amount,
                    "source": tx.flash_loan_source,
                    "tvl_ratio": tvl_ratio,
                }
            )
        return None

    def check_price_manipulation(self, tx: Transaction) -> Optional[Alert]:
        """检测预言机价格操纵"""
        # 检查交易中是否有价格剧变
        for action in tx.actions:
            if action.get("type") == "price_update":
                token = action.get("token", "")
                old_price = action.get("old_price", 0)
                new_price = action.get("new_price", 0)
                if old_price > 0 and new_price > 0:
                    change_pct = abs(new_price - old_price) / old_price
                    # 价格在单笔交易中变化超过20%
                    if change_pct > 0.20:
                        return Alert(
                            alert_type=AlertType.PRICE_MANIPULATION,
                            tx_hash=tx.tx_hash,
                            description=(
                                f"价格异常波动: {token} "
                                f"从${old_price:.2f}变至${new_price:.2f}"
                                f"(变化{change_pct*100:.1f}%)"
                            ),
                            severity="Critical" if change_pct > 0.50 else "High",
                            details={
                                "token": token,
                                "old_price": old_price,
                                "new_price": new_price,
                                "change_pct": change_pct,
                            }
                        )
        return None

    def check_governance_rush(self, tx: Transaction) -> Optional[Alert]:
        """检测闪电贷治理攻击"""
        has_flash_loan = tx.flash_loan_amount > 0
        has_governance_action = any(
            a.get("type") in ["vote", "propose", "execute_proposal"]
            for a in tx.actions
        )

        if has_flash_loan and has_governance_action:
            return Alert(
                alert_type=AlertType.GOVERNANCE_RUSH,
                tx_hash=tx.tx_hash,
                description=(
                    "闪电贷+治理操作组合: 可能是闪电贷治理攻击"
                    "（借入资金获取临时投票权通过恶意提案）"
                ),
                severity="Critical",
                details={
                    "flash_loan": tx.flash_loan_amount,
                    "actions": [a.get("type") for a in tx.actions],
                }
            )
        return None

    def check_combined_attack(self, tx: Transaction) -> Optional[Alert]:
        """检测组合攻击模式"""
        action_types = {a.get("type") for a in tx.actions}
        attack_patterns = {
            # 闪电贷+借贷+清算
            "flash_loan_attack": {"flash_loan", "borrow", "liquidate"},
            # 闪电贷+DEX套利
            "flash_arb": {"flash_loan", "swap", "swap"},
            # 闪电贷+质押+提取
            "stake_drain": {"flash_loan", "stake", "withdraw"},
        }

        for pattern_name, required_actions in attack_patterns.items():
            if required_actions.issubset(action_types):
                return Alert(
                    alert_type=AlertType.COMBINED_ATTACK,
                    tx_hash=tx.tx_hash,
                    description=(
                        f"组合攻击模式[{pattern_name}]: "
                        f"检测到{required_actions}操作组合"
                    ),
                    severity="Critical",
                    details={
                        "pattern": pattern_name,
                        "actions": list(action_types),
                    }
                )
        return None

    def check_liquidity_drain(self, tx: Transaction) -> Optional[Alert]:
        """检测流动性异常抽取"""
        for action in tx.actions:
            if action.get("type") == "withdraw":
                amount = action.get("amount", 0)
                pool = action.get("pool", "")
                pool_tvl = self.protocol_tvl.get(pool, 0)
                if pool_tvl > 0 and amount / pool_tvl > 0.30:
                    return Alert(
                        alert_type=AlertType.LIQUIDITY_DRAIN,
                        tx_hash=tx.tx_hash,
                        description=(
                            f"流动性异常抽取: 从{pool}提取"
                            f"${amount:,.0f} (占池TVL的"
                            f"{amount/pool_tvl*100:.1f}%)"
                        ),
                        severity="High",
                        details={
                            "pool": pool,
                            "amount": amount,
                            "pool_tvl": pool_tvl,
                        }
                    )
        return None

    def analyze(self, tx: Transaction):
        """分析单笔交易"""
        checks = [
            self.check_large_flash_loan,
            self.check_price_manipulation,
            self.check_governance_rush,
            self.check_combined_attack,
            self.check_liquidity_drain,
        ]
        for check in checks:
            alert = check(tx)
            if alert:
                self.alerts.append(alert)


def generate_normal_transactions(n: int = 10) -> list[Transaction]:
    """生成模拟正常交易"""
    txs = []
    for i in range(n):
        tx = Transaction(
            tx_hash=f"0x{'a' * 8}{i:04x}{'b' * 52}",
            block_number=18000000 + i,
            timestamp=time.time() + i * 12,
            sender=f"0xUser{i:04d}",
            actions=[
                {"type": "swap", "token": "ETH", "amount": random.uniform(1, 10)},
                {"type": "deposit", "pool": "Aave", "amount": random.uniform(1000, 50000)},
            ],
            gas_used=random.randint(100000, 300000),
            flash_loan_amount=0,
        )
        txs.append(tx)
    return txs


def generate_attack_transactions() -> list[Transaction]:
    """生成模拟攻击交易"""
    attacks = []

    # 攻击1：bZx式预言机操纵
    attacks.append(Transaction(
        tx_hash="0xdead0001beef0001cafe0001" + "0" * 40,
        block_number=18000010,
        timestamp=time.time() + 100,
        sender="0xAttacker01",
        actions=[
            {"type": "flash_loan", "source": "dYdX", "amount": 10000, "token": "ETH"},
            {"type": "borrow", "protocol": "bZx", "amount": 50000, "token": "WBTC"},
            {"type": "swap", "pool": "Uniswap", "token": "WBTC", "amount": 50000},
            {"type": "price_update", "token": "WBTC",
             "old_price": 30000, "new_price": 45000},  # 价格+50%
            {"type": "repay", "protocol": "bZx", "amount": 30000},
            {"type": "repay", "source": "dYdX", "amount": 10000, "token": "ETH"},
        ],
        gas_used=500000,
        flash_loan_amount=10000 * 3000,  # ~$30M ETH
        flash_loan_source="dYdX",
    ))

    # 攻击2：Beanstalk式治理攻击
    attacks.append(Transaction(
        tx_hash="0xbeef0002dead0002cafe0002" + "0" * 40,
        block_number=18000011,
        timestamp=time.time() + 112,
        sender="0xAttacker02",
        actions=[
            {"type": "flash_loan", "source": "Aave", "amount": 100000000,
             "token": "USDC"},
            {"type": "stake", "protocol": "Beanstalk", "amount": 100000000},
            {"type": "propose", "proposal": "evil_proposal_0x42"},
            {"type": "vote", "proposal": "evil_proposal_0x42", "votes": 100000000},
            {"type": "execute_proposal", "proposal": "evil_proposal_0x42"},
            {"type": "withdraw", "pool": "Beanstalk_treasury", "amount": 182000000},
            {"type": "repay", "source": "Aave", "amount": 100000000, "token": "USDC"},
        ],
        gas_used=800000,
        flash_loan_amount=100000000,  # $100M
        flash_loan_source="Aave",
    ))

    # 攻击3：闪电贷清算攻击
    attacks.append(Transaction(
        tx_hash="0xcafe0003dead0003beef0003" + "0" * 40,
        block_number=18000012,
        timestamp=time.time() + 124,
        sender="0xAttacker03",
        actions=[
            {"type": "flash_loan", "source": "Aave", "amount": 50000000,
             "token": "USDC"},
            {"type": "swap", "pool": "Uniswap", "token": "CRV", "amount": 50000000},
            {"type": "price_update", "token": "CRV",
             "old_price": 1.0, "new_price": 0.6},  # 价格-40%
            {"type": "liquidate", "protocol": "Aave",
             "borrower": "0xVictim", "amount": 10000000},
            {"type": "swap", "pool": "Uniswap", "token": "USDC", "amount": 8000000},
            {"type": "repay", "source": "Aave", "amount": 50000000, "token": "USDC"},
        ],
        gas_used=600000,
        flash_loan_amount=50000000,  # $50M
        flash_loan_source="Aave",
    ))

    return attacks


def main():
    print("=" * 70)
    print("DeFi安全分析 - 闪电贷攻击检测（模拟链上数据）")
    print("=" * 70)

    detector = FlashLoanDetector()
    detector.protocol_tvl = {
        "total": 200_000_000,  # $200M
        "Aave": 50_000_000,
        "Beanstalk_treasury": 182_000_000,
        "Uniswap_WBTC_ETH": 30_000_000,
    }

    # 1. 分析正常交易
    print("\n[1] 分析正常交易流量...")
    normal_txs = generate_normal_transactions(10)
    for tx in normal_txs:
        detector.analyze(tx)
    print(f"    分析了 {len(normal_txs)} 笔正常交易")

    # 2. 分析攻击交易
    print("\n[2] 分析可疑交易...")
    attack_txs = generate_attack_transactions()
    for tx in attack_txs:
        detector.analyze(tx)
    print(f"    分析了 {len(attack_txs)} 笔可疑交易")

    # 3. 输出告警
    print(f"\n[3] 共触发 {len(detector.alerts)} 条安全告警:\n")
    for i, alert in enumerate(detector.alerts, 1):
        print(f"  告警 #{i}")
        print(f"  类型: [{alert.alert_type.value}]")
        print(f"  严重性: {alert.severity}")
        print(f"  交易: {alert.tx_hash[:20]}...")
        print(f"  描述: {alert.description}")
        print(f"  详情: {alert.details}")
        print()

    # 4. 统计
    print("[4] 告警统计:")
    type_counts = defaultdict(int)
    severity_counts = defaultdict(int)
    for alert in detector.alerts:
        type_counts[alert.alert_type.value] += 1
        severity_counts[alert.severity] += 1
    print("    按类型:")
    for atype, count in sorted(type_counts.items()):
        print(f"      {atype}: {count}次")
    print("    按严重性:")
    for sev, count in sorted(severity_counts.items()):
        print(f"      {sev}: {count}次")

    print("\n" + "=" * 70)
    print("检测完成。")
    print("提示: 此脚本使用模拟交易数据。实际应用中应:")
    print("  - 连接以太坊节点获取实时交易数据")
    print("  - 集成Chainlink预言机价格作为基线")
    print("  - 使用Forta/CertiK Skynet等链上监控平台")
    print("  - 设置告警通知（Telegram/Discord/PagerDuty）")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

---

---

## 📋 内容审核与补充建议

> 针对「Python DeFi安全分析脚本示例」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
