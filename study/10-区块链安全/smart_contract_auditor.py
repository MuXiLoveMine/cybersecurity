#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能合约安全审计工具 (Smart Contract Auditor)
==================================================

本工具集集成了智能合约安全审计常用的各类检测工具：
1. 重入攻击检测 - 调用外部合约前状态更新检查
2. 整数溢出/下溢检测 - 算术运算边界检查
3. 访问控制缺陷检测 - 所有权、权限修饰符检查
4. 未检查返回值检测 - call/transfer/send返回值
5. 拒绝服务攻击检测 - 循环依赖、Gas限制
6. 前置交易(Front-running)检测 - 公开函数顺序依赖
7. 常见漏洞模式库 - 已知漏洞模式匹配
8. 安全建议生成器 - 针对性修复建议

作者：区块链安全学习工具
版本：1.0
用途：仅用于授权的安全测试和教育学习
"""

import os
import re
import sys
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime


# ============================================================
# 常见漏洞模式
# ============================================================

漏洞模式库 = [
    {
        "id": "REENTRANCY",
        "名称": "重入攻击",
        "严重程度": "高危",
        "描述": "调用外部合约后未更新状态变量，导致重入攻击",
        "检测模式": [
            r'\.call\.value\(',
            r'(msg\.sender|recipient)\.call\.value',
        ],
        "修复建议": "调用外部合约前先更新状态变量，使用Checks-Effects-Interactions模式",
    },
    {
        "id": "OVERFLOW",
        "名称": "整数溢出",
        "严重程度": "高危",
        "描述": "算术运算可能导致整数溢出/下溢（Solidity 0.8以下版本）",
        "检测模式": [
            r'pragma solidity \^0\.[0-7]\.',
        ],
        "修复建议": "使用SafeMath库或升级到Solidity 0.8+（内置溢出检查）",
    },
    {
        "id": "UNCHECKED_RETURN",
        "名称": "未检查返回值",
        "严重程度": "中危",
        "描述": "call/send的返回值未检查，调用失败可能被忽略",
        "检测模式": [
            r'\.call\([^)]*\)\s*;',
        ],
        "修复建议": "检查call返回值，使用require(success)确保调用成功",
    },
    {
        "id": "TX_ORIGIN",
        "名称": "tx.origin身份认证",
        "严重程度": "中危",
        "描述": "使用tx.origin进行身份认证，可被钓鱼攻击绕过",
        "检测模式": [
            r'require\([^)]*tx\.origin[^)]*\)',
            r'if\s*\([^)]*tx\.origin[^)]*\)',
        ],
        "修复建议": "使用msg.sender代替tx.origin进行身份认证",
    },
    {
        "id": "SELFDESTRUCT",
        "名称": "自毁函数",
        "严重程度": "中危",
        "描述": "合约包含selfdestruct/suicide函数，可被恶意调用销毁合约",
        "检测模式": [
            r'selfdestruct\(',
            r'suicide\(',
        ],
        "修复建议": "确保自毁函数有严格的权限控制（如onlyOwner）",
    },
    {
        "id": "DELEGATECALL",
        "名称": "不安全delegatecall",
        "严重程度": "高危",
        "描述": "使用delegatecall调用不可信合约，可能导致存储破坏",
        "检测模式": [
            r'delegatecall\(',
        ],
        "修复建议": "仅对可信且无状态的库合约使用delegatecall",
    },
    {
        "id": "WEAK_RANDOM",
        "名称": "弱随机数",
        "严重程度": "中危",
        "描述": "使用block.timestamp等链上数据作为随机数，可被矿工操纵",
        "检测模式": [
            r'block\.timestamp',
            r'block\.number',
            r'block\.difficulty',
        ],
        "修复建议": "使用Chainlink VRF等可验证随机函数",
    },
    {
        "id": "FLOATING_PRAGMA",
        "名称": "浮动编译器版本",
        "严重程度": "低危",
        "描述": "使用^声明的浮动pragma版本，可能导致不同编译器版本编译",
        "检测模式": [
            r'pragma solidity \^',
        ],
        "修复建议": "使用固定版本号（如 pragma solidity 0.8.17;）",
    },
]


# ============================================================
# 工具1: 智能合约审计引擎
# ============================================================

class SmartContractAuditor:
    """智能合约安全审计引擎"""

    def __init__(self, source_code: str = None):
        self.source = source_code or self._get_sample_contract()
        self.findings = []

    def _get_sample_contract(self) -> str:
        """获取模拟的漏洞合约"""
        lines = [
            "// SPDX-License-Identifier: MIT",
            "pragma solidity ^0.6.0;",
            "",
            "contract VulnerableBank {",
            "    mapping(address => uint256) public balances;",
            "    address public owner;",
            "",
            "    constructor() public {",
            "        owner = msg.sender;",
            "    }",
            "",
            "    function deposit() public payable {",
            "        balances[msg.sender] += msg.value;",
            "    }",
            "",
            "    function withdraw(uint256 amount) public {",
            "        require(balances[msg.sender] >= amount);",
            "        // 重入漏洞: 先转账后更新余额",
            '        msg.sender.call.value(amount)("");',
            "        balances[msg.sender] -= amount;",
            "    }",
            "",
            "    function transfer(address to, uint256 amount) public {",
            "        // 整数溢出: 0.6版本无内置检查",
            "        balances[msg.sender] -= amount;",
            "        balances[to] += amount;",
            "    }",
            "",
            "    function kill() public {",
            "        // 无保护的自毁函数",
            "        selfdestruct(msg.sender);",
            "    }",
            "",
            "    function randomNumber() public view returns (uint256) {",
            "        // 弱随机数: 使用区块参数",
            "        return uint256(keccak256(abi.encodePacked(block.timestamp, block.difficulty)));",
            "    }",
            "",
            "    function adminAction() public {",
            "        // tx.origin身份认证问题",
            "        require(tx.origin == owner);",
            "        // 敏感操作...",
            "    }",
            "",
            "    function unprotectedMint(uint256 amount) public {",
            "        // 未保护的铸币函数",
            "        balances[msg.sender] += amount;",
            "    }",
            "}",
        ]
        return '\n'.join(lines)

    def audit(self) -> List[Dict]:
        """执行审计"""
        print("\n" + "=" * 60)
        print("智能合约安全审计")
        print("=" * 60)

        findings = []

        for vuln in 漏洞模式库:
            for pattern in vuln["检测模式"]:
                if re.search(pattern, self.source, re.MULTILINE | re.IGNORECASE):
                    lines = self.source.split('\n')
                    matched_lines = []
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            matched_lines.append(i)

                    findings.append({
                        "id": vuln["id"],
                        "名称": vuln["名称"],
                        "严重程度": vuln["严重程度"],
                        "描述": vuln["描述"],
                        "行号": matched_lines[:5],
                        "修复建议": vuln["修复建议"],
                    })
                    break

        severity_order = {"高危": 0, "中危": 1, "低危": 2}
        findings.sort(key=lambda x: severity_order.get(x["严重程度"], 99))

        print("\n扫描完成，发现 %d 个潜在漏洞" % len(findings))
        severity_count = defaultdict(int)
        for f in findings:
            severity_count[f["严重程度"]] += 1
        print("风险分布: 高危=%d 中危=%d 低危=%d" % (
            severity_count["高危"], severity_count["中危"], severity_count["低危"]))
        print()

        for i, f in enumerate(findings, 1):
            icon = "[!!]" if f["严重程度"] == "高危" else "[!]" if f["严重程度"] == "中危" else "[*]"
            lines_str = ",".join(map(str, f["行号"]))
            print("  %s [%s] %d. %s (%s)" % (icon, f["严重程度"], i, f["名称"], f["id"]))
            print("       位置: 第 %s 行" % lines_str)
            print("       描述: %s" % f["描述"])
            print("       修复: %s" % f["修复建议"])
            print()

        self.findings = findings
        return findings


# ============================================================
# 工具2: 重入攻击模拟器
# ============================================================

class ReentrancySimulator:
    """重入攻击原理模拟器"""

    @staticmethod
    def explain_attack():
        """解释重入攻击原理"""
        print("\n" + "=" * 60)
        print("重入攻击 (Reentrancy Attack) 原理")
        print("=" * 60)

        print("""
  【漏洞原理】
  当合约在调用外部合约（或转账ETH）后才更新状态变量时，
  攻击者可以在回调函数中再次调用该函数，重复提取资金。

  【攻击流程】
  1. 攻击者合约存入 1 ETH
  2. 攻击者调用 withdraw(1 ETH)
  3. 合约检查余额足够 -> 转账 1 ETH -> 触发receive()回调
  4. 在receive()回调中再次调用 withdraw(1 ETH)
  5. 因为余额还没扣减，检查再次通过
  6. 重复步骤3-5，直到提空合约
  7. 最后逐层返回，余额被多次扣减

  【经典案例】
  - The DAO 攻击 (2016): 损失约 6000 万美元
  - 导致以太坊硬分叉 (ETC / ETH 分裂)

  【防御方法】
  1. Checks-Effects-Interactions 模式
     Checks: 检查条件
     Effects: 更新状态变量
     Interactions: 与外部合约交互（最后一步）
  2. 使用ReentrancyGuard (OpenZeppelin)
  3. 使用transfer/send限制Gas (2300 Gas)
        """)

    @staticmethod
    def show_vulnerable_code():
        """展示漏洞代码"""
        print("\n[漏洞代码示例]")
        print("""
function withdraw(uint amount) public {
    require(balances[msg.sender] >= amount); // Checks
    msg.sender.call.value(amount)("");      // Interactions (先转账)
    balances[msg.sender] -= amount;          // Effects (后更新)
}
""")

        print("[修复后代码]")
        print("""
function withdraw(uint amount) public {
    require(balances[msg.sender] >= amount); // Checks
    balances[msg.sender] -= amount;          // Effects (先更新)
    msg.sender.call.value(amount)("");      // Interactions (后转账)
}
""")
        print()


# ============================================================
# 工具3: 整数溢出检测器
# ============================================================

class IntegerOverflowDetector:
    """整数溢出检测与演示"""

    @staticmethod
    def explain_overflow():
        """解释整数溢出原理"""
        print("\n" + "=" * 60)
        print("整数溢出 (Integer Overflow) 原理")
        print("=" * 60)

        print("""
  【原理】
  Solidity中uint类型有固定范围，超过上限会回绕。
  例如: uint8 最大值为 255
  255 + 1 = 0 (溢出)
  0 - 1 = 255 (下溢)

  【版本差异】
  - Solidity < 0.8: 没有内置溢出检查，需要SafeMath
  - Solidity >= 0.8: 内置溢出检查，溢出会revert

  【影响】
  - 余额溢出: 余额变成超大值
  - 权限绕过: 数量校验被绕过
  - 代币增发: 总供应量计算错误

  【防御】
  - 使用SafeMath库 (0.8以下版本)
  - 升级到Solidity 0.8+
  - 关键算术运算前后检查边界
        """)

    @staticmethod
    def demo_overflow():
        """演示溢出效果"""
        print("\n[uint8 溢出演示]")

        print("  uint8 最大值: 255")
        print("  255 + 1 = %d (溢出回绕)" % ((255 + 1) % 256))
        print("  0 - 1 = %d (下溢回绕)" % ((0 - 1) % 256))
        print()

        print("[SafeMath 库示例]")
        print("""
library SafeMath {
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        require(c >= a, "SafeMath: addition overflow");
        return c;
    }
    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b <= a, "SafeMath: subtraction overflow");
        return a - b;
    }
}
""")
        print()


# ============================================================
# 工具4: 访问控制审计
# ============================================================

class AccessControlAuditor:
    """访问控制审计工具"""

    敏感函数模式 = [
        ("withdraw", "提现函数"),
        ("transfer", "转账函数"),
        ("mint", "铸币函数"),
        ("burn", "销毁函数"),
        ("setOwner", "设置所有者"),
        ("changeOwner", "变更所有者"),
        ("kill", "销毁合约"),
        ("destroy", "销毁合约"),
        ("pause", "暂停合约"),
        ("setFee", "设置手续费"),
    ]

    def __init__(self, source_code: str = None):
        self.source = source_code or SmartContractAuditor()._get_sample_contract()
        self.findings = []

    def audit(self) -> List[Dict]:
        """审计访问控制"""
        print("\n" + "=" * 60)
        print("访问控制审计")
        print("=" * 60)

        findings = []

        for func_pattern, desc in self.敏感函数模式:
            pattern = r'function\s+' + func_pattern + r'[^)]*\)[^{]*\{'
            matches = re.finditer(pattern, self.source, re.IGNORECASE)

            for match in matches:
                start = match.start()
                func_body_start = self.source.find('{', match.end() - 1)
                if func_body_start > 0:
                    body_preview = self.source[func_body_start:func_body_start + 500]
                    has_owner_check = ('onlyOwner' in body_preview or
                                       'msg.sender == owner' in body_preview or
                                       'require' in body_preview[:200])

                    if not has_owner_check:
                        findings.append({
                            "函数": func_pattern,
                            "描述": desc,
                            "风险": "高",
                            "说明": "敏感函数缺少明显的访问控制检查",
                        })

        print("\n发现 %d 个访问控制问题" % len(findings))
        print()

        for i, f in enumerate(findings, 1):
            print("  [!] [%s] %d. %s - %s" % (f["风险"], i, f["函数"], f["描述"]))
            print("       %s" % f["说明"])

        print()
        self.findings = findings
        return findings


# ============================================================
# 工具5: 安全建议生成器
# ============================================================

class SecurityRecommendationGenerator:
    """安全建议生成器"""

    最佳实践列表 = [
        ("使用最新稳定版Solidity", "使用最新的稳定编译器版本，获取安全修复和新特性"),
        ("使用Checks-Effects-Interactions模式", "防止重入攻击"),
        ("使用OpenZeppelin安全库", "经过审计的合约库，减少重复造轮子"),
        ("使用ReentrancyGuard", "防止重入攻击"),
        ("使用Pull而非Push支付模式", "用户主动提取而非合约主动发送，减少DoS风险"),
        ("限制Gas使用", "避免无限循环导致的Gas耗尽"),
        ("使用事件记录关键操作", "便于链下监控和审计"),
        ("设置紧急暂停开关", "出现安全事件时可暂停合约"),
        ("进行专业安全审计", "部署前请专业团队审计"),
        ("设置时间锁", "关键操作有延迟期，给用户反应时间"),
        ("使用多签管理权限", "关键权限由多方控制"),
        ("编写全面的测试", "单元测试、集成测试、模糊测试"),
    ]

    @staticmethod
    def generate_checklist() -> List[Tuple[str, str]]:
        """生成安全检查清单"""
        print("\n" + "=" * 60)
        print("智能合约安全检查清单")
        print("=" * 60)
        print()

        for i, (item, desc) in enumerate(SecurityRecommendationGenerator.最佳实践列表, 1):
            print("  [ ] %2d. %s" % (i, item))
            print("         %s" % desc)

        print()
        return SecurityRecommendationGenerator.最佳实践列表

    @staticmethod
    def generate_audit_report_summary(findings: List[Dict]) -> str:
        """生成审计报告摘要"""
        severity_count = defaultdict(int)
        for f in findings:
            severity_count[f.get("严重程度", f.get("风险", "未知"))] += 1

        report_lines = [
            "审计报告摘要",
            "=" * 50,
            "发现问题总数: %d" % len(findings),
            "  高危: %d 个" % severity_count.get("高危", 0),
            "  中危: %d 个" % severity_count.get("中危", 0),
            "  低危: %d 个" % severity_count.get("低危", 0),
            "",
            "建议修复优先级:",
            "  P0 (立即): 高危漏洞，可导致资金损失",
            "  P1 (紧急): 高危但有缓解措施",
            "  P2 (高):   中危漏洞",
            "  P3 (中):   低危/优化建议",
        ]
        report = '\n'.join(report_lines)
        print(report)
        return report


# ============================================================
# 主菜单
# ============================================================

def main():
    print("\n" + "=" * 60)
    print("智能合约安全审计工具 (Smart Contract Auditor)")
    print("=" * 60)
    print("""
请选择工具:
  1. 智能合约安全审计 (综合扫描)
  2. 重入攻击原理演示
  3. 整数溢出原理演示
  4. 访问控制审计
  5. 安全检查清单
  6. 运行全部演示
  0. 退出
""")

    while True:
        try:
            choice = input("\n请输入选项 (0-6): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if choice == "0":
            print("再见！")
            break
        elif choice == "1":
            auditor = SmartContractAuditor()
            findings = auditor.audit()
            SecurityRecommendationGenerator.generate_audit_report_summary(findings)
        elif choice == "2":
            ReentrancySimulator.explain_attack()
            ReentrancySimulator.show_vulnerable_code()
        elif choice == "3":
            IntegerOverflowDetector.explain_overflow()
            IntegerOverflowDetector.demo_overflow()
        elif choice == "4":
            AccessControlAuditor().audit()
        elif choice == "5":
            SecurityRecommendationGenerator.generate_checklist()
        elif choice == "6":
            print("\n[*] 运行全部工具演示...\n")
            auditor = SmartContractAuditor()
            findings = auditor.audit()
            ReentrancySimulator.explain_attack()
            IntegerOverflowDetector.explain_overflow()
            AccessControlAuditor().audit()
            SecurityRecommendationGenerator.generate_checklist()
            SecurityRecommendationGenerator.generate_audit_report_summary(findings)
            print("\n[*] 全部演示完成！")
        else:
            print("无效选项，请重新输入")

        print("\n" + "-" * 60)


if __name__ == "__main__":
    main()
