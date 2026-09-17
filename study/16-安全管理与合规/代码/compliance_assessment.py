# -*- coding: utf-8 -*-
"""
合规评估辅助工具
================

功能说明：
    本工具用于辅助进行信息安全合规评估，支持等保2.0、ISO 27001、个人信息保护等
    多种合规标准的自评和检查，可生成评估报告和整改建议。

主要功能：
    1. 等保2.0合规自评
    2. ISO 27001合规评估
    3. 个人信息保护合规检查
    4. 安全配置基线检查
    5. 风险评估矩阵
    6. 生成评估报告
    7. 整改建议生成

使用方法：
    python compliance_assessment.py

作者：安全管理与合规学习工具
版本：v1.0
日期：2026-09-11
"""

import json
import os
import datetime
from typing import Dict, List, Tuple, Optional


# ============================================================
# 数据定义部分
# ============================================================

class ComplianceData:
    """
    合规评估数据类
    存储各种合规标准的检查项和评估标准
    """

    # ========================================================
    # 等保2.0三级检查项（技术部分，简化版）
    # ========================================================
    DENGBAO_ITEMS = {
        "安全物理环境": [
            {"id": "PE-01", "name": "机房位置选择", "level": "中", "desc": "机房场地应选择在具有防震、防风和防雨等能力的建筑内"},
            {"id": "PE-02", "name": "物理访问控制", "level": "高", "desc": "机房出入口应配置电子门禁系统，鉴别进入人员身份"},
            {"id": "PE-03", "name": "防盗窃和防破坏", "level": "高", "desc": "应将主要设备放置在机房内，设置防盗报警系统"},
            {"id": "PE-04", "name": "防雷击", "level": "中", "desc": "机房建筑应设置避雷装置和防雷保安器"},
            {"id": "PE-05", "name": "防火", "level": "极高", "desc": "机房应设置火灾自动消防系统和气体灭火系统"},
            {"id": "PE-06", "name": "防水和防潮", "level": "中", "desc": "应采取措施防止雨水渗透和结露，安装漏水检测装置"},
            {"id": "PE-07", "name": "温湿度控制", "level": "中", "desc": "应配备空调系统，保持温湿度在规定范围内"},
            {"id": "PE-08", "name": "电力供应", "level": "高", "desc": "应保证机房电力供应稳定，配备UPS电源和备用发电机"},
        ],
        "安全通信网络": [
            {"id": "CN-01", "name": "网络架构", "level": "高", "desc": "应划分不同的网络区域，按安全级别进行网络分段"},
            {"id": "CN-02", "name": "通信传输", "level": "高", "desc": "应采用密码技术保证通信过程中数据的保密性和完整性"},
            {"id": "CN-03", "name": "可信验证", "level": "中", "desc": "可基于可信根对通信设备进行可信验证"},
        ],
        "安全区域边界": [
            {"id": "AB-01", "name": "边界防护", "level": "高", "desc": "应保证跨越边界的访问和数据流通过受控接口进行通信"},
            {"id": "AB-02", "name": "访问控制", "level": "极高", "desc": "应在网络边界部署访问控制设备，启用访问控制功能"},
            {"id": "AB-03", "name": "入侵防范", "level": "高", "desc": "应在关键网络节点处检测和防止外部及内部发起的攻击行为"},
            {"id": "AB-04", "name": "恶意代码防范", "level": "高", "desc": "应在关键网络节点处对恶意代码进行检测和清除"},
            {"id": "AB-05", "name": "安全审计", "level": "高", "desc": "应在网络边界、重要网络节点进行安全审计"},
        ],
        "安全计算环境": [
            {"id": "CE-01", "name": "身份鉴别", "level": "极高", "desc": "应对登录的用户进行身份标识和鉴别，具有唯一性"},
            {"id": "CE-02", "name": "访问控制", "level": "高", "desc": "应对登录的用户分配账户和权限，遵循最小权限原则"},
            {"id": "CE-03", "name": "安全审计", "level": "高", "desc": "应启用安全审计功能，审计覆盖到每个用户"},
            {"id": "CE-04", "name": "入侵防范", "level": "高", "desc": "应遵循最小安装原则，及时修补漏洞"},
            {"id": "CE-05", "name": "恶意代码防范", "level": "高", "desc": "应安装防恶意代码软件，定期更新病毒库"},
            {"id": "CE-06", "name": "数据完整性", "level": "高", "desc": "应采用密码技术保证重要数据在传输和存储中的完整性"},
            {"id": "CE-07", "name": "数据保密性", "level": "极高", "desc": "应采用加密措施实现重要数据的保密性"},
            {"id": "CE-08", "name": "数据备份恢复", "level": "极高", "desc": "应提供重要数据的本地备份和异地备份功能"},
            {"id": "CE-09", "name": "个人信息保护", "level": "高", "desc": "应仅采集业务必需的用户个人信息，禁止未授权访问"},
        ],
        "安全管理中心": [
            {"id": "SMC-01", "name": "系统管理", "level": "高", "desc": "应对系统管理员进行身份鉴别，操作权限分离"},
            {"id": "SMC-02", "name": "审计管理", "level": "高", "desc": "应对审计记录进行管理，审计管理员权限仅限于审计操作"},
            {"id": "SMC-03", "name": "安全管理", "level": "高", "desc": "应对系统安全策略进行配置和管理"},
            {"id": "SMC-04", "name": "集中管控", "level": "高", "desc": "应建立安全管理中心，对设备状态、安全事件等进行集中管理"},
        ],
    }

    # ========================================================
    # ISO 27001 控制项（简化版）
    # ========================================================
    ISO27001_ITEMS = {
        "信息安全方针": [
            {"id": "A5.1", "name": "信息安全方针", "level": "高", "desc": "管理层应批准信息安全方针"},
        ],
        "信息安全组织": [
            {"id": "A5.2", "name": "信息安全的组织角色", "level": "高", "desc": "应明确信息安全角色和职责"},
            {"id": "A5.3", "name": "项目管理中的信息安全", "level": "中", "desc": "项目管理中应考虑信息安全"},
        ],
        "人力资源安全": [
            {"id": "A6.1", "name": "筛选", "level": "中", "desc": "应对人员进行背景审查"},
            {"id": "A6.2", "name": "雇佣条款和条件", "level": "高", "desc": "雇佣合同应包含信息安全条款"},
            {"id": "A6.3", "name": "信息安全意识、教育和培训", "level": "高", "desc": "应定期开展信息安全培训"},
        ],
        "资产管理": [
            {"id": "A5.9", "name": "资产清单", "level": "中", "desc": "应维护资产清单"},
            {"id": "A5.10", "name": "资产的可接受使用", "level": "中", "desc": "应制定资产可接受使用规则"},
        ],
        "访问控制": [
            {"id": "A8.1", "name": "用户访问管理", "level": "高", "desc": "应对用户访问进行管理"},
            {"id": "A8.2", "name": "特权访问权限", "level": "极高", "desc": "应管理和控制特权访问权限"},
            {"id": "A8.3", "name": "身份验证信息", "level": "高", "desc": "应保护身份验证信息的机密性"},
        ],
        "物理和环境安全": [
            {"id": "A7.1", "name": "物理安全边界", "level": "高", "desc": "应定义和保护物理安全边界"},
            {"id": "A7.2", "name": "物理入口控制", "level": "高", "desc": "应有物理入口控制"},
            {"id": "A7.3", "name": "办公室、房间和设施的安全", "level": "中", "desc": "应保护办公室和设施的安全"},
        ],
        "操作安全": [
            {"id": "A8.20", "name": "信息处理设施的安全运行", "level": "高", "desc": "应确保信息处理设施的安全运行"},
            {"id": "A8.21", "name": "恶意软件检测、防范和删除", "level": "高", "desc": "应保护系统免受恶意软件侵害"},
            {"id": "A8.16", "name": "监测活动", "level": "高", "desc": "应监测信息系统和事件"},
        ],
        "通信安全": [
            {"id": "A8.22", "name": "网络安全管理", "level": "高", "desc": "应管理和控制网络安全"},
            {"id": "A8.23", "name": "网络服务的安全", "level": "中", "desc": "应确保网络服务的安全"},
        ],
        "系统获取、开发和维护": [
            {"id": "A8.25", "name": "安全的系统开发生命周期", "level": "高", "desc": "应将安全纳入系统开发生命周期"},
            {"id": "A8.26", "name": "应用安全要求", "level": "高", "desc": "应规定应用安全要求"},
        ],
        "供应商关系": [
            {"id": "A5.19", "name": "供应商关系中的信息安全", "level": "中", "desc": "应管理供应商关系中的信息安全"},
            {"id": "A5.20", "name": "供应商协议", "level": "高", "desc": "供应商协议应包含安全要求"},
        ],
        "信息安全事件管理": [
            {"id": "A8.24", "name": "使用信息安全事件管理流程", "level": "高", "desc": "应有信息安全事件管理流程"},
            {"id": "A6.4", "name": "事件响应", "level": "高", "desc": "应建立事件响应机制"},
        ],
        "业务连续性管理": [
            {"id": "A8.13", "name": "信息安全连续性", "level": "高", "desc": "应确保业务连续性中的信息安全"},
            {"id": "A8.14", "name": "冗余", "level": "中", "desc": "应有信息处理设施的冗余"},
        ],
        "符合性": [
            {"id": "A5.31", "name": "关于使用信息系统的法律和合同要求", "level": "高", "desc": "应遵守相关法律法规和合同要求"},
            {"id": "A5.32", "name": "知识产权", "level": "中", "desc": "应保护知识产权"},
            {"id": "A9.4", "name": "信息安全的独立评审", "level": "中", "desc": "应定期进行独立评审"},
        ],
    }

    # ========================================================
    # 个人信息保护检查项
    # ========================================================
    PIPL_ITEMS = {
        "处理规则": [
            {"id": "PIPL-01", "name": "合法正当必要原则", "level": "极高", "desc": "个人信息处理应遵循合法、正当、必要原则"},
            {"id": "PIPL-02", "name": "公开透明原则", "level": "高", "desc": "应公开个人信息处理规则，明示处理目的、方式、范围"},
            {"id": "PIPL-03", "name": "目的明确原则", "level": "高", "desc": "收集个人信息应有明确合理的目的"},
            {"id": "PIPL-04", "name": "最小必要原则", "level": "极高", "desc": "只收集实现处理目的所必要的最小范围信息"},
            {"id": "PIPL-05", "name": "质量保障原则", "level": "中", "desc": "应保证个人信息的质量，避免不准确不完整"},
            {"id": "PIPL-06", "name": "安全保障原则", "level": "高", "desc": "应采取必要措施保障个人信息安全"},
        ],
        "同意管理": [
            {"id": "PIPL-07", "name": "同意的合法性", "level": "极高", "desc": "处理个人信息应取得个人同意或有其他合法依据"},
            {"id": "PIPL-08", "name": "单独同意（敏感信息）", "level": "极高", "desc": "处理敏感个人信息应取得个人单独同意"},
            {"id": "PIPL-09", "name": "同意撤回权", "level": "高", "desc": "个人有权撤回同意，撤回方式应与给予同意一样便捷"},
            {"id": "PIPL-10", "name": "不得强制同意", "level": "高", "desc": "不得以个人不同意为由拒绝提供产品或服务（必需的除外）"},
        ],
        "个人权利": [
            {"id": "PIPL-11", "name": "知情权", "level": "高", "desc": "个人有权了解其个人信息的处理情况"},
            {"id": "PIPL-12", "name": "查阅复制权", "level": "高", "desc": "个人有权查阅、复制其个人信息"},
            {"id": "PIPL-13", "name": "更正补充权", "level": "中", "desc": "个人有权要求更正、补充其个人信息"},
            {"id": "PIPL-14", "name": "删除权（被遗忘权）", "level": "高", "desc": "符合法定情形时，个人有权要求删除其个人信息"},
            {"id": "PIPL-15", "name": "可携带权", "level": "中", "desc": "个人有权请求将个人信息转移至其指定的处理者"},
        ],
        "处理者义务": [
            {"id": "PIPL-16", "name": "安全保护措施", "level": "极高", "desc": "应采取必要措施保障个人信息安全"},
            {"id": "PIPL-17", "name": "分类管理", "level": "高", "desc": "应对个人信息实行分类管理"},
            {"id": "PIPL-18", "name": "个人信息保护负责人", "level": "中", "desc": "处理个人信息达到规定数量的应指定个人信息保护负责人"},
            {"id": "PIPL-19", "name": "个人信息保护影响评估（PIA）", "level": "高", "desc": "高风险处理活动应进行个人信息保护影响评估"},
            {"id": "PIPL-20", "name": "合规审计", "level": "中", "desc": "应定期对个人信息处理活动进行合规审计"},
        ],
        "数据安全": [
            {"id": "PIPL-21", "name": "加密保护", "level": "高", "desc": "敏感个人信息应加密存储和传输"},
            {"id": "PIPL-22", "name": "去标识化/匿名化", "level": "中", "desc": "在满足使用需求的前提下，应对个人信息进行去标识化处理"},
            {"id": "PIPL-23", "name": "访问控制", "level": "高", "desc": "应对个人信息访问进行严格控制"},
            {"id": "PIPL-24", "name": "操作审计", "level": "高", "desc": "应对个人信息的重要操作进行审计"},
            {"id": "PIPL-25", "name": "数据泄露通知", "level": "极高", "desc": "发生个人信息泄露应及时通知监管部门和个人"},
        ],
        "跨境传输": [
            {"id": "PIPL-26", "name": "境内存储", "level": "极高", "desc": "境内收集的个人信息应在境内存储"},
            {"id": "PIPL-27", "name": "出境安全评估", "level": "极高", "desc": "向境外提供个人信息应通过安全评估或符合其他法定条件"},
            {"id": "PIPL-28", "name": "单独同意（跨境）", "level": "高", "desc": "向境外提供个人信息应取得个人单独同意"},
        ],
    }

    # ========================================================
    # 安全配置基线检查项
    # ========================================================
    BASELINE_ITEMS = {
        "操作系统安全基线": [
            {"id": "OS-01", "name": "密码策略", "level": "高", "desc": "密码长度≥8位，包含大小写字母、数字、特殊字符"},
            {"id": "OS-02", "name": "账户锁定", "level": "高", "desc": "连续登录失败5次锁定账户30分钟"},
            {"id": "OS-03", "name": "会话超时", "level": "中", "desc": "空闲会话超时时间≤15分钟"},
            {"id": "OS-04", "name": "默认账户", "level": "极高", "desc": "禁用或删除所有不必要的默认账户"},
            {"id": "OS-05", "name": "默认口令", "level": "极高", "desc": "修改所有默认口令，不得使用默认密码"},
            {"id": "OS-06", "name": "审计日志", "level": "高", "desc": "启用安全审计功能，记录重要安全事件"},
            {"id": "OS-07", "name": "日志留存", "level": "高", "desc": "审计日志保存时间≥6个月"},
            {"id": "OS-08", "name": "防病毒软件", "level": "高", "desc": "安装防病毒软件，病毒库保持最新"},
            {"id": "OS-09", "name": "系统补丁", "level": "高", "desc": "及时安装安全补丁，高危补丁7天内安装"},
            {"id": "OS-10", "name": "不必要服务", "level": "中", "desc": "关闭不必要的系统服务和端口"},
            {"id": "OS-11", "name": "文件权限", "level": "中", "desc": "重要系统文件权限设置合理，防止未授权访问"},
            {"id": "OS-12", "name": "远程管理", "level": "高", "desc": "使用加密的远程管理协议（如SSH），禁用Telnet"},
        ],
        "网络设备安全基线": [
            {"id": "NET-01", "name": "设备口令", "level": "极高", "desc": "修改默认口令，使用强密码"},
            {"id": "NET-02", "name": "管理IP限制", "level": "高", "desc": "限制设备管理的源IP地址"},
            {"id": "NET-03", "name": "SNMP安全", "level": "中", "desc": "修改SNMP默认community字符串，使用SNMPv3"},
            {"id": "NET-04", "name": "日志记录", "level": "高", "desc": "启用日志功能，记录重要操作"},
            {"id": "NET-05", "name": "SSH管理", "level": "高", "desc": "使用SSH进行设备管理，禁用Telnet"},
            {"id": "NET-06", "name": "未使用服务", "level": "中", "desc": "禁用不必要的网络服务"},
            {"id": "NET-07", "name": "配置备份", "level": "中", "desc": "定期备份设备配置文件"},
            {"id": "NET-08", "name": "固件更新", "level": "高", "desc": "及时更新设备固件，修补已知漏洞"},
        ],
        "数据库安全基线": [
            {"id": "DB-01", "name": "默认账户", "level": "极高", "desc": "修改默认账户密码，删除不需要的默认账户"},
            {"id": "DB-02", "name": "密码策略", "level": "高", "desc": "数据库账户密码符合复杂度要求"},
            {"id": "DB-03", "name": "访问控制", "level": "高", "desc": "数据库权限最小化，只授予必要权限"},
            {"id": "DB-04", "name": "审计日志", "level": "高", "desc": "启用数据库审计，记录重要操作"},
            {"id": "DB-05", "name": "数据加密", "level": "高", "desc": "敏感数据加密存储"},
            {"id": "DB-06", "name": "网络访问", "level": "高", "desc": "限制数据库访问来源IP"},
            {"id": "DB-07", "name": "补丁更新", "level": "高", "desc": "及时安装数据库安全补丁"},
            {"id": "DB-08", "name": "备份策略", "level": "极高", "desc": "制定完善的数据库备份策略，定期备份"},
        ],
        "中间件安全基线": [
            {"id": "MW-01", "name": "默认配置", "level": "高", "desc": "修改默认配置，删除默认页面和示例"},
            {"id": "MW-02", "name": "管理接口", "level": "高", "desc": "限制管理接口访问IP，修改默认管理员密码"},
            {"id": "MW-03", "name": "版本安全", "level": "高", "desc": "使用最新稳定版本，及时修补漏洞"},
            {"id": "MW-04", "name": "目录遍历防护", "level": "高", "desc": "禁止目录浏览，防止目录遍历攻击"},
            {"id": "MW-05", "name": "日志配置", "level": "中", "desc": "配置访问日志和错误日志"},
        ],
    }


# ============================================================
# 风险评估矩阵
# ============================================================

class RiskMatrix:
    """
    风险评估矩阵类
    根据可能性和影响程度计算风险等级
    """

    # 可能性等级定义
    LIKELIHOOD = {
        1: {"name": "极低", "desc": "几乎不可能发生，发生概率<1%"},
        2: {"name": "低", "desc": "不太可能发生，发生概率1-10%"},
        3: {"name": "中", "desc": "可能发生，发生概率10-50%"},
        4: {"name": "高", "desc": "很可能发生，发生概率50-90%"},
        5: {"name": "极高", "desc": "几乎肯定发生，发生概率>90%"},
    }

    # 影响程度等级定义
    IMPACT = {
        1: {"name": "轻微", "desc": "影响很小，几乎不造成损失"},
        2: {"name": "较小", "desc": "造成较小损失，可快速恢复"},
        3: {"name": "中等", "desc": "造成一定损失，需要一定时间恢复"},
        4: {"name": "严重", "desc": "造成严重损失，业务受到较大影响"},
        5: {"name": "灾难性", "desc": "造成灾难性损失，业务可能中断"},
    }

    # 风险矩阵（行：可能性，列：影响）
    # 值为风险等级：1-低，2-中，3-高，4-极高
    MATRIX = [
        # 影响: 1  2  3  4  5
        [1, 1, 2, 2, 3],  # 可能性1（极低）
        [1, 2, 2, 3, 3],  # 可能性2（低）
        [2, 2, 3, 3, 4],  # 可能性3（中）
        [2, 3, 3, 4, 4],  # 可能性4（高）
        [3, 3, 4, 4, 4],  # 可能性5（极高）
    ]

    # 风险等级定义
    RISK_LEVELS = {
        1: {"name": "低风险", "color": "green", "action": "接受风险，定期监控"},
        2: {"name": "中风险", "color": "yellow", "action": "制定风险缓解计划，限期整改"},
        3: {"name": "高风险", "color": "orange", "action": "立即采取风险缓解措施，优先处理"},
        4: {"name": "极高风险", "color": "red", "action": "必须立即处理，否则可能造成严重后果"},
    }

    @classmethod
    def calculate_risk(cls, likelihood: int, impact: int) -> Dict:
        """
        计算风险等级

        参数:
            likelihood: 可能性等级（1-5）
            impact: 影响程度等级（1-5）

        返回:
            包含风险等级信息的字典
        """
        # 验证输入有效性
        if not (1 <= likelihood <= 5 and 1 <= impact <= 5):
            raise ValueError("可能性和影响程度必须在1-5之间")

        # 从矩阵中获取风险等级
        risk_level = cls.MATRIX[likelihood - 1][impact - 1]

        # 返回详细信息
        return {
            "likelihood": likelihood,
            "likelihood_name": cls.LIKELIHOOD[likelihood]["name"],
            "impact": impact,
            "impact_name": cls.IMPACT[impact]["name"],
            "risk_level": risk_level,
            "risk_level_name": cls.RISK_LEVELS[risk_level]["name"],
            "recommended_action": cls.RISK_LEVELS[risk_level]["action"],
        }


# ============================================================
# 整改建议生成器
# ============================================================

class RecommendationGenerator:
    """
    整改建议生成器
    根据不合规项生成具体的整改建议
    """

    # 整改建议库
    RECOMMENDATIONS = {
        # 物理安全类
        "PE-01": "1. 评估机房选址的安全性，避开低洼、易燃易爆区域\n2. 查阅机房建筑设计文档，确认抗震、防风、防雨能力",
        "PE-02": "1. 安装电子门禁系统，支持刷卡或生物识别\n2. 设置访问权限，只允许授权人员进入\n3. 门禁记录保存不少于6个月",
        "PE-05": "1. 安装火灾自动报警系统\n2. 安装气体灭火系统（如七氟丙烷）\n3. 定期进行消防检测和维护\n4. 配置灭火器，定期检查有效期",
        "PE-08": "1. 配置UPS不间断电源，保证至少30分钟供电\n2. 重要系统考虑双路市电供电\n3. 配置柴油发电机作为备用电源\n4. 定期进行供电系统测试",

        # 网络安全类
        "CN-01": "1. 重新规划网络架构，按功能和安全级别划分区域\n2. 绘制准确的网络拓扑图\n3. 在区域边界部署防火墙进行隔离",
        "CN-02": "1. 部署SSL证书，实现HTTPS加密传输\n2. 内部重要通信使用加密协议\n3. 定期评估加密算法的安全性",
        "AB-02": "1. 在网络边界部署防火墙\n2. 配置访问控制策略，遵循最小权限原则\n3. 设置默认拒绝规则\n4. 每季度审查和优化防火墙规则",
        "AB-03": "1. 部署入侵检测系统（IDS）或入侵防御系统（IPS）\n2. 及时更新攻击特征库\n3. 配置告警规则，及时发现攻击行为",
        "AB-05": "1. 部署集中日志审计系统\n2. 收集网络设备、安全设备、服务器日志\n3. 定期进行日志分析",

        # 主机安全类
        "CE-01": "1. 修改所有默认账户和密码\n2. 实施强密码策略：长度≥8位，包含多种字符类型\n3. 设置密码有效期（最长90天）\n4. 启用登录失败锁定策略",
        "CE-02": "1. 实施最小权限原则，只授予必要权限\n2. 建立权限申请和审批流程\n3. 每季度审查用户权限\n4. 及时清理离职人员账号",
        "CE-03": "1. 启用操作系统审计功能\n2. 配置审计策略，记录重要安全事件\n3. 日志保存不少于6个月\n4. 定期审计日志分析",
        "CE-04": "1. 关闭不必要的服务和端口\n2. 定期进行漏洞扫描\n3. 及时安装安全补丁\n4. 实施安全配置基线",
        "CE-05": "1. 部署企业级防病毒软件\n2. 配置自动更新病毒库\n3. 定期进行全盘扫描\n4. 统一管理防病毒策略",
        "CE-07": "1. 敏感数据加密存储\n2. 使用安全的加密算法\n3. 密钥安全管理，定期更换\n4. 数据传输使用加密通道",
        "CE-08": "1. 制定数据备份策略和计划\n2. 实施本地备份（每日增量+每周全量）\n3. 实施异地备份\n4. 每季度进行备份恢复测试",
        "CE-09": "1. 制定个人信息保护制度\n2. 只收集必要的个人信息\n3. 对个人信息进行分类分级管理\n4. 对敏感个人信息采取加密等保护措施",

        # 管理类
        "SMC-04": "1. 建立安全管理中心\n2. 部署集中安全管理平台\n3. 实现安全策略统一管理\n4. 集中收集和分析安全事件",

        # 个人信息保护类
        "PIPL-01": "1. 梳理个人信息处理活动\n2. 评估每项处理的合法性基础\n3. 确保处理活动符合合法、正当、必要原则",
        "PIPL-04": "1. 梳理收集的个人信息项\n2. 评估每项信息的必要性\n3. 删除非必要的信息收集\n4. 实施数据最小化原则",
        "PIPL-07": "1. 完善用户同意机制\n2. 确保同意是自愿、明确、具体的\n3. 保存同意记录\n4. 提供便捷的同意撤回方式",
        "PIPL-16": "1. 制定个人信息安全保护制度\n2. 采取技术措施保护个人信息\n3. 对个人信息进行分类管理\n4. 建立个人信息安全事件应急机制",
        "PIPL-19": "1. 建立PIA（个人信息保护影响评估）机制\n2. 高风险处理活动前进行PIA\n3. 保存PIA报告和处理记录（至少3年）",
        "PIPL-25": "1. 制定个人信息泄露应急预案\n2. 建立数据泄露检测和响应机制\n3. 发生泄露后及时通知监管部门和受影响个人",
        "PIPL-26": "1. 评估个人信息存储位置\n2. 确保境内收集的个人信息在境内存储\n3. 确需跨境传输的，按规定进行安全评估",
    }

    @classmethod
    def get_recommendation(cls, item_id: str) -> str:
        """
        根据检查项ID获取整改建议

        参数:
            item_id: 检查项ID

        返回:
            整改建议字符串
        """
        if item_id in cls.RECOMMENDATIONS:
            return cls.RECOMMENDATIONS[item_id]
        else:
            return f"1. 针对{''}存在的问题进行专项整改\n2. 制定整改计划，明确责任人和时间节点\n3. 整改完成后进行验证\n4. 将整改情况纳入安全考核"

    @classmethod
    def generate_generic_recommendation(cls, item_name: str, level: str) -> str:
        """
        生成通用整改建议

        参数:
            item_name: 检查项名称
            level: 风险等级

        返回:
            整改建议字符串
        """
        return f"""1. 问题描述：{item_name}方面存在合规缺陷，风险等级为{level}
2. 整改目标：确保{item_name}符合相关法规和标准要求
3. 整改措施：
   （1）开展现状评估，明确差距和问题
   （2）制定详细的整改方案
   （3）落实整改责任人和时间节点
   （4）实施整改措施
4. 验证方式：整改完成后进行检查验证
5. 预防措施：建立常态化检查机制，防止问题复发"""


# ============================================================
# 评估引擎类
# ============================================================

class ComplianceAssessmentEngine:
    """
    合规评估引擎类
    执行各种合规评估，生成评估结果
    """

    def __init__(self):
        """初始化评估引擎"""
        self.data = ComplianceData()
        self.risk_matrix = RiskMatrix()
        self.recommendation = RecommendationGenerator()
        self.assessment_results = {}

    # ========================================================
    # 交互式评估方法
    # ========================================================
    def interactive_assessment(self, assessment_type: str) -> Dict:
        """
        交互式合规评估
        通过问答方式收集评估数据

        参数:
            assessment_type: 评估类型（dengbao/iso27001/pipl/baseline）

        返回:
            评估结果字典
        """
        # 获取对应的检查项
        items_map = self._get_items_map(assessment_type)
        if not items_map:
            print(f"错误：未知的评估类型 {assessment_type}")
            return {}

        assessment_name = self._get_assessment_name(assessment_type)
        print(f"\n{'='*60}")
        print(f"  {assessment_name}")
        print(f"{'='*60}")
        print("请根据实际情况对每个检查项进行评分：")
        print("  0 = 完全不符合")
        print("  1 = 部分符合")
        print("  2 = 基本符合")
        print("  3 = 完全符合")
        print("  N = 不适用（跳过此项）")
        print(f"{'='*60}\n")

        results = {
            "assessment_type": assessment_type,
            "assessment_name": assessment_name,
            "assessment_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "categories": {},
            "total_items": 0,
            "compliant_items": 0,
            "partially_compliant_items": 0,
            "non_compliant_items": 0,
            "not_applicable_items": 0,
            "issues": [],
        }

        # 遍历每个分类
        for category, items in items_map.items():
            print(f"\n【{category}】")
            print("-" * 40)

            category_result = {
                "items": [],
                "total": 0,
                "compliant": 0,
                "partially_compliant": 0,
                "non_compliant": 0,
                "not_applicable": 0,
                "score": 0,
            }

            # 遍历每个检查项
            for item in items:
                while True:
                    print(f"\n  [{item['id']}] {item['name']}")
                    print(f"      说明：{item['desc']}")
                    print(f"      风险等级：{item['level']}")
                    answer = input("      评分（0/1/2/3/N）：").strip().upper()

                    if answer in ['0', '1', '2', '3', 'N']:
                        break
                    else:
                        print("      输入无效，请重新输入！")

                item_result = {
                    "id": item["id"],
                    "name": item["name"],
                    "desc": item["desc"],
                    "level": item["level"],
                    "score": answer,
                }

                category_result["total"] += 1
                results["total_items"] += 1

                if answer == '3':
                    category_result["compliant"] += 1
                    results["compliant_items"] += 1
                elif answer == '2':
                    category_result["partially_compliant"] += 1
                    results["partially_compliant_items"] += 1
                elif answer == '1' or answer == '0':
                    category_result["non_compliant"] += 1
                    results["non_compliant_items"] += 1
                    # 记录问题
                    issue = {
                        "id": item["id"],
                        "name": item["name"],
                        "category": category,
                        "level": item["level"],
                        "score": answer,
                        "recommendation": self.recommendation.get_recommendation(item["id"]),
                    }
                    results["issues"].append(issue)
                elif answer == 'N':
                    category_result["not_applicable"] += 1
                    results["not_applicable_items"] += 1

                category_result["items"].append(item_result)

            # 计算分类得分（满分100分）
            applicable_items = category_result["total"] - category_result["not_applicable"]
            if applicable_items > 0:
                total_score = 0
                for it in category_result["items"]:
                    if it["score"] == '3':
                        total_score += 100
                    elif it["score"] == '2':
                        total_score += 70
                    elif it["score"] == '1':
                        total_score += 40
                    elif it["score"] == '0':
                        total_score += 0
                category_result["score"] = round(total_score / applicable_items, 1)
            else:
                category_result["score"] = 0

            results["categories"][category] = category_result

        # 计算总得分
        applicable_total = results["total_items"] - results["not_applicable_items"]
        if applicable_total > 0:
            total_score = 0
            for cat in results["categories"].values():
                applicable = cat["total"] - cat["not_applicable"]
                total_score += cat["score"] * applicable
            results["total_score"] = round(total_score / applicable_total, 1)
        else:
            results["total_score"] = 0

        # 保存结果
        self.assessment_results[assessment_type] = results

        return results

    def _get_items_map(self, assessment_type: str) -> Dict:
        """获取评估类型对应的检查项"""
        if assessment_type == "dengbao":
            return self.data.DENGBAO_ITEMS
        elif assessment_type == "iso27001":
            return self.data.ISO27001_ITEMS
        elif assessment_type == "pipl":
            return self.data.PIPL_ITEMS
        elif assessment_type == "baseline":
            return self.data.BASELINE_ITEMS
        else:
            return {}

    def _get_assessment_name(self, assessment_type: str) -> str:
        """获取评估类型的中文名称"""
        names = {
            "dengbao": "等保2.0合规自评",
            "iso27001": "ISO 27001合规评估",
            "pipl": "个人信息保护合规检查",
            "baseline": "安全配置基线检查",
        }
        return names.get(assessment_type, "合规评估")

    # ========================================================
    # 风险评估方法
    # ========================================================
    def risk_assessment_tool(self):
        """
        风险评估工具
        交互式进行风险评估
        """
        print(f"\n{'='*60}")
        print("  风险评估矩阵工具")
        print(f"{'='*60}")

        while True:
            print("\n请输入风险参数（输入q退出）：")

            # 输入可能性
            l_input = input("  可能性等级（1-5，1=极低，5=极高）：").strip()
            if l_input.lower() == 'q':
                break
            if not l_input.isdigit():
                print("  输入无效，请输入数字！")
                continue

            likelihood = int(l_input)
            if not (1 <= likelihood <= 5):
                print("  输入无效，请输入1-5之间的数字！")
                continue

            # 输入影响
            i_input = input("  影响程度等级（1-5，1=轻微，5=灾难性）：").strip()
            if i_input.lower() == 'q':
                break
            if not i_input.isdigit():
                print("  输入无效，请输入数字！")
                continue

            impact = int(i_input)
            if not (1 <= impact <= 5):
                print("  输入无效，请输入1-5之间的数字！")
                continue

            # 计算风险
            try:
                result = RiskMatrix.calculate_risk(likelihood, impact)
                print(f"\n  风险评估结果：")
                print(f"  {'-'*40}")
                print(f"  可能性：{result['likelihood']}级 - {result['likelihood_name']}")
                print(f"  影响程度：{result['impact']}级 - {result['impact_name']}")
                print(f"  风险等级：{result['risk_level']}级 - {result['risk_level_name']}")
                print(f"  建议措施：{result['recommended_action']}")
            except ValueError as e:
                print(f"  错误：{e}")

            # 是否继续
            cont = input("\n  是否继续评估？（y/n）：").strip().lower()
            if cont != 'y':
                break

    # ========================================================
    # 生成评估报告
    # ========================================================
    def generate_report(self, assessment_type: str, output_file: str = None):
        """
        生成评估报告

        参数:
            assessment_type: 评估类型
            output_file: 输出文件路径（可选）
        """
        if assessment_type not in self.assessment_results:
            print(f"错误：未找到 {assessment_type} 的评估结果，请先进行评估！")
            return

        results = self.assessment_results[assessment_type]
        report_lines = []

        # 报告标题
        report_lines.append("=" * 70)
        report_lines.append(f"  {results['assessment_name']}报告")
        report_lines.append("=" * 70)
        report_lines.append("")
        report_lines.append(f"评估日期：{results['assessment_date']}")
        report_lines.append("")

        # 总体概览
        report_lines.append("一、总体评估结果")
        report_lines.append("-" * 70)
        report_lines.append(f"  总得分：{results['total_score']} 分")
        report_lines.append(f"  总检查项数：{results['total_items']}")
        report_lines.append(f"  完全符合：{results['compliant_items']} 项")
        report_lines.append(f"  基本符合：{results['partially_compliant_items']} 项")
        report_lines.append(f"  不符合：{results['non_compliant_items']} 项")
        report_lines.append(f"  不适用：{results['not_applicable_items']} 项")

        applicable = results["total_items"] - results["not_applicable_items"]
        if applicable > 0:
            compliance_rate = round(
                (results["compliant_items"] + results["partially_compliant_items"] * 0.7) / applicable * 100, 1
            )
            report_lines.append(f"  综合符合率：{compliance_rate}%")
        report_lines.append("")

        # 各分类得分
        report_lines.append("二、各分类得分")
        report_lines.append("-" * 70)
        report_lines.append(f"  {'分类名称':<20} {'得分':>8} {'总项数':>8} {'符合':>6} {'不符合':>8}")
        report_lines.append(f"  {'-'*20} {'-'*8} {'-'*8} {'-'*6} {'-'*8}")

        for cat_name, cat_result in results["categories"].items():
            report_lines.append(
                f"  {cat_name:<20} {cat_result['score']:>7}分 "
                f"{cat_result['total']:>8} "
                f"{cat_result['compliant'] + cat_result['partially_compliant']:>6} "
                f"{cat_result['non_compliant']:>8}"
            )
        report_lines.append("")

        # 问题清单
        report_lines.append("三、发现的主要问题")
        report_lines.append("-" * 70)

        if results["issues"]:
            # 按风险等级排序
            level_order = {"极高": 0, "高": 1, "中": 2, "低": 3}
            sorted_issues = sorted(
                results["issues"],
                key=lambda x: level_order.get(x["level"], 99)
            )

            for i, issue in enumerate(sorted_issues, 1):
                report_lines.append(f"\n  问题 {i}：[{issue['id']}] {issue['name']}")
                report_lines.append(f"    分类：{issue['category']}")
                report_lines.append(f"    风险等级：{issue['level']}")
                report_lines.append(f"    整改建议：")
                for line in issue["recommendation"].split('\n'):
                    report_lines.append(f"      {line}")
        else:
            report_lines.append("  未发现重大问题，整体合规情况良好。")
        report_lines.append("")

        # 整改建议总结
        report_lines.append("四、整改建议")
        report_lines.append("-" * 70)
        report_lines.append(f"  本次评估共发现 {len(results['issues'])} 项不符合项，建议按以下优先级整改：")
        report_lines.append("")

        high_risk = [i for i in results["issues"] if i["level"] in ["极高", "高"]]
        mid_risk = [i for i in results["issues"] if i["level"] == "中"]
        low_risk = [i for i in results["issues"] if i["level"] == "低"]

        if high_risk:
            report_lines.append(f"  1. 高优先级（立即整改，1个月内完成）：")
            report_lines.append(f"     共 {len(high_risk)} 项高/极高风险问题，应立即制定整改计划，优先处理。")
            report_lines.append("")

        if mid_risk:
            report_lines.append(f"  2. 中优先级（计划整改，3个月内完成）：")
            report_lines.append(f"     共 {len(mid_risk)} 项中风险问题，应纳入整改计划，限期完成。")
            report_lines.append("")

        if low_risk:
            report_lines.append(f"  3. 低优先级（择机改进，6个月内完成）：")
            report_lines.append(f"     共 {len(low_risk)} 项低风险问题，可结合日常工作逐步改进。")
            report_lines.append("")

        report_lines.append("五、总结")
        report_lines.append("-" * 70)

        if results["total_score"] >= 90:
            report_lines.append("  评估结论：优秀。整体合规情况良好，建议持续保持并持续改进。")
        elif results["total_score"] >= 80:
            report_lines.append("  评估结论：良好。基本符合要求，建议针对发现的问题进行整改。")
        elif results["total_score"] >= 70:
            report_lines.append("  评估结论：一般。存在较多需要改进的地方，建议制定整改计划。")
        elif results["total_score"] >= 60:
            report_lines.append("  评估结论：较差。合规情况不理想，建议加大整改力度。")
        else:
            report_lines.append("  评估结论：差。存在严重合规风险，必须立即进行全面整改。")

        report_lines.append("")
        report_lines.append("=" * 70)
        report_lines.append("  报告生成时间：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        report_lines.append("=" * 70)

        # 输出报告
        report_text = "\n".join(report_lines)
        print("\n" + report_text)

        # 保存到文件
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                print(f"\n报告已保存到：{output_file}")
            except Exception as e:
                print(f"\n保存报告失败：{e}")

        # 同时保存JSON格式
        json_file = output_file.replace('.txt', '.json') if output_file else None
        if json_file:
            try:
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"详细数据已保存到：{json_file}")
            except Exception as e:
                print(f"保存JSON数据失败：{e}")

        return report_text


# ============================================================
# 主程序 - 交互式菜单
# ============================================================

def main():
    """
    主函数
    显示交互式菜单，供用户选择功能
    """
    engine = ComplianceAssessmentEngine()

    while True:
        # 清屏（跨平台）
        os.system('cls' if os.name == 'nt' else 'clear')

        # 显示菜单
        print("\n" + "=" * 60)
        print("        合规评估辅助工具 v1.0")
        print("=" * 60)
        print("")
        print("  1. 等保2.0合规自评")
        print("  2. ISO 27001合规评估")
        print("  3. 个人信息保护合规检查")
        print("  4. 安全配置基线检查")
        print("  5. 风险评估矩阵工具")
        print("  6. 生成评估报告")
        print("  7. 工具使用说明")
        print("  0. 退出程序")
        print("")
        print("=" * 60)

        choice = input("\n请输入您的选择（0-7）：").strip()

        if choice == '0':
            print("\n感谢使用合规评估辅助工具，再见！\n")
            break

        elif choice == '1':
            # 等保2.0自评
            results = engine.interactive_assessment("dengbao")
            input("\n评估完成，按回车键继续...")

            # 询问是否生成报告
            save = input("\n是否生成评估报告？（y/n）：").strip().lower()
            if save == 'y':
                filename = input("请输入报告文件名（默认：dengbao_report.txt）：").strip()
                if not filename:
                    filename = "dengbao_report.txt"
                engine.generate_report("dengbao", filename)
                input("\n按回车键继续...")

        elif choice == '2':
            # ISO 27001评估
            results = engine.interactive_assessment("iso27001")
            input("\n评估完成，按回车键继续...")

            save = input("\n是否生成评估报告？（y/n）：").strip().lower()
            if save == 'y':
                filename = input("请输入报告文件名（默认：iso27001_report.txt）：").strip()
                if not filename:
                    filename = "iso27001_report.txt"
                engine.generate_report("iso27001", filename)
                input("\n按回车键继续...")

        elif choice == '3':
            # 个人信息保护检查
            results = engine.interactive_assessment("pipl")
            input("\n评估完成，按回车键继续...")

            save = input("\n是否生成评估报告？（y/n）：").strip().lower()
            if save == 'y':
                filename = input("请输入报告文件名（默认：pipl_report.txt）：").strip()
                if not filename:
                    filename = "pipl_report.txt"
                engine.generate_report("pipl", filename)
                input("\n按回车键继续...")

        elif choice == '4':
            # 安全配置基线检查
            results = engine.interactive_assessment("baseline")
            input("\n评估完成，按回车键继续...")

            save = input("\n是否生成评估报告？（y/n）：").strip().lower()
            if save == 'y':
                filename = input("请输入报告文件名（默认：baseline_report.txt）：").strip()
                if not filename:
                    filename = "baseline_report.txt"
                engine.generate_report("baseline", filename)
                input("\n按回车键继续...")

        elif choice == '5':
            # 风险评估矩阵
            engine.risk_assessment_tool()
            input("\n按回车键继续...")

        elif choice == '6':
            # 生成报告
            print("\n已完成的评估：")
            if engine.assessment_results:
                for idx, (key, val) in enumerate(engine.assessment_results.items(), 1):
                    print(f"  {idx}. {val['assessment_name']} (得分：{val['total_score']}分)")

                num = input("\n请选择要生成报告的评估（输入序号）：").strip()
                keys = list(engine.assessment_results.keys())
                if num.isdigit() and 1 <= int(num) <= len(keys):
                    assessment_key = keys[int(num) - 1]
                    filename = input("请输入报告文件名（留空使用默认）：").strip()
                    if not filename:
                        filename = f"{assessment_key}_report.txt"
                    engine.generate_report(assessment_key, filename)
                else:
                    print("输入无效！")
            else:
                print("  暂无评估结果，请先进行评估。")

            input("\n按回车键继续...")

        elif choice == '7':
            # 使用说明
            print("\n" + "=" * 60)
            print("  工具使用说明")
            print("=" * 60)
            print("""
  本工具用于辅助进行信息安全合规评估，主要功能包括：

  1. 等保2.0合规自评
     - 按照等保2.0三级要求进行自评
     - 涵盖物理环境、通信网络、区域边界、
       计算环境、管理中心五大技术类
     - 生成自评报告和整改建议

  2. ISO 27001合规评估
     - 按照ISO 27001标准控制项进行评估
     - 涵盖14个控制域
     - 生成评估报告

  3. 个人信息保护合规检查
     - 按照《个人信息保护法》要求检查
     - 涵盖处理规则、同意管理、个人权利、
       处理者义务、数据安全、跨境传输
     - 生成合规检查报告

  4. 安全配置基线检查
     - 检查操作系统、网络设备、数据库、
       中间件的安全配置
     - 生成基线检查报告

  5. 风险评估矩阵工具
     - 基于5x5风险矩阵计算风险等级
     - 输入可能性和影响程度
     - 输出风险等级和建议措施

  6. 生成评估报告
     - 将评估结果生成详细的报告
     - 包含总体得分、分类得分、问题清单、
       整改建议等
     - 支持保存为文本和JSON格式

  使用方法：
    1. 根据菜单选择评估类型
    2. 按照提示对每个检查项进行评分
    3. 评估完成后可生成报告
    4. 报告可保存到本地文件

  评分说明：
    3分 = 完全符合：完全满足要求，有制度、有执行、有记录
    2分 = 基本符合：基本满足要求，存在少量不足
    1分 = 部分符合：部分满足要求，存在明显不足
    0分 = 完全不符合：不满足要求，或存在严重问题
    N  = 不适用：该检查项不适用于本系统

  注意事项：
    1. 本工具为辅助评估工具，结果仅供参考
    2. 正式测评请咨询专业机构
    3. 评估数据保存在内存中，退出后清除
            """)
            input("\n按回车键继续...")

        else:
            print("\n输入无效，请重新选择！")
            input("按回车键继续...")


# ============================================================
# 程序入口
# ============================================================

if __name__ == "__main__":
    """
    程序入口
    运行主菜单
    """
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断，再见！\n")
    except Exception as e:
        print(f"\n程序发生错误：{e}")
        import traceback
        traceback.print_exc()
