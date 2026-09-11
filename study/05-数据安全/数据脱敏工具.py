# -*- coding: utf-8 -*-
"""
数据脱敏工具
=============
本工具提供常用的敏感数据脱敏功能，用于保护个人隐私和敏感信息。

功能列表：
    1. 姓名脱敏 - 隐藏姓名中间或部分字符
    2. 手机号脱敏 - 隐藏手机号中间四位
    3. 身份证号脱敏 - 隐藏身份证号中间部分
    4. 银行卡号脱敏 - 隐藏银行卡号中间部分
    5. 邮箱脱敏 - 隐藏邮箱用户名部分
    6. 地址脱敏 - 隐藏详细地址部分
    7. 数据模糊化 - 对数值、日期等进行模糊处理
    8. 批量脱敏 - 支持字典/列表批量脱敏

使用场景：
    - 开发/测试环境数据脱敏
    - 数据分析场景隐私保护
    - 数据共享前的脱敏处理
    - 日志输出敏感信息脱敏

作者：数据安全学习工具
版本：1.0.0
日期：2024-01-01
"""

import re
import random
import hashlib
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta


# ============================================================
# 基础工具函数
# ============================================================

def _validate_input(data: str, field_name: str = "数据") -> bool:
    """
    验证输入数据是否有效

    参数:
        data: 待验证的数据
        field_name: 字段名称，用于错误提示

    返回:
        True 表示有效，False 表示无效

    说明:
        内部工具函数，用于统一的输入验证
    """
    if data is None:
        return False
    if not isinstance(data, str):
        return False
    if len(data.strip()) == 0:
        return False
    return True


def _mask_string(s: str, start: int, end: int, mask_char: str = "*") -> str:
    """
    通用字符串脱敏函数：将指定位置的字符替换为掩码字符

    参数:
        s: 原始字符串
        start: 开始保留的字符数（左侧保留数量）
        end: 结束保留的字符数（右侧保留数量）
        mask_char: 掩码字符，默认为 *

    返回:
        脱敏后的字符串

    示例:
        >>> _mask_string("13800138000", 3, 4)
        '138****8000'
        >>> _mask_string("张三", 1, 0)
        '张*'
    """
    if not _validate_input(s):
        return s

    length = len(s)

    # 如果字符串太短，全部掩码
    if length <= start + end:
        return mask_char * length

    # 计算中间需要掩码的长度
    mask_length = length - start - end

    # 拼接结果：左侧明文 + 掩码 + 右侧明文
    return s[:start] + mask_char * mask_length + s[-end:]


# ============================================================
# 一、姓名脱敏
# ============================================================

def mask_name(name: str, mask_char: str = "*") -> str:
    """
    姓名脱敏

    脱敏规则：
        - 2字姓名：保留姓，名用掩码（如：张*）
        - 3字姓名：保留姓和最后一个字，中间用掩码（如：张*三）
        - 4字及以上：保留前1后2，中间用掩码（如：欧**华）
        - 复姓处理：对于常见复姓做特殊处理（如：欧阳*）

    参数:
        name: 原始姓名
        mask_char: 掩码字符，默认为 *

    返回:
        脱敏后的姓名

    示例:
        >>> mask_name("张三")
        '张*'
        >>> mask_name("张三丰")
        '张*丰'
        >>> mask_name("欧阳修文")
        '欧**文'
    """
    # 输入验证
    if not _validate_input(name, "姓名"):
        return name

    # 去除两端空格
    name = name.strip()

    # 常见复姓列表
    compound_surnames = [
        "欧阳", "太史", "端木", "上官", "司马", "东方", "独孤", "南宫",
        "万俟", "闻人", "夏侯", "诸葛", "尉迟", "公羊", "赫连", "澹台",
        "皇甫", "宗政", "濮阳", "公冶", "太叔", "申屠", "公孙", "慕容",
        "仲孙", "钟离", "长孙", "宇文", "司徒", "鲜于", "闾丘", "子车",
        "亓官", "司寇", "仉督", "子车", "颛孙", "端木", "巫马", "公西",
        "漆雕", "乐正", "壤驷", "公良", "拓跋", "夹谷", "宰父", "谷梁",
    ]

    length = len(name)

    # 2字姓名
    if length == 2:
        return name[0] + mask_char

    # 3字姓名
    elif length == 3:
        # 检查是否为复姓（虽然3字姓名复姓可能性低，但也有可能）
        if name[:2] in compound_surnames:
            # 复姓 + 单名（如：欧阳峰 → 欧阳*）
            return name[:2] + mask_char
        else:
            # 单姓 + 双名（如：张三丰 → 张*丰）
            return name[0] + mask_char + name[-1]

    # 4字及以上姓名
    elif length >= 4:
        # 检查是否为复姓
        if name[:2] in compound_surnames:
            # 复姓 + 双名/多名（如：欧阳振华 → 欧**华）
            # 保留姓的第一个字和最后一个字
            return name[0] + mask_char * (length - 2) + name[-1]
        else:
            # 单姓 + 多名（如：张三四五 → 张***五）
            return name[0] + mask_char * (length - 2) + name[-1]

    else:
        return name


def mask_name_full(name: str, mask_char: str = "*") -> str:
    """
    姓名脱敏（严格模式）：只保留姓，其余全部掩码

    参数:
        name: 原始姓名
        mask_char: 掩码字符

    返回:
        脱敏后的姓名

    示例:
        >>> mask_name_full("张三丰")
        '张**'
        >>> mask_name_full("欧阳振华")
        '欧***'
    """
    if not _validate_input(name, "姓名"):
        return name

    name = name.strip()
    length = len(name)

    if length == 0:
        return name

    # 只保留第一个字
    return name[0] + mask_char * (length - 1)


# ============================================================
# 二、手机号脱敏
# ============================================================

def mask_phone(phone: str, mask_char: str = "*") -> str:
    """
    手机号脱敏

    脱敏规则：
        - 保留前3位和后4位，中间4位用掩码
        - 标准格式：138****8000
        - 支持带区号的号码（如 +8613800138000）
        - 支持固话号码（保留区号和后4位）

    参数:
        phone: 原始手机号
        mask_char: 掩码字符

    返回:
        脱敏后的手机号

    示例:
        >>> mask_phone("13800138000")
        '138****8000'
        >>> mask_phone("+8613800138000")
        '+86138****8000'
    """
    if not _validate_input(phone, "手机号"):
        return phone

    phone = phone.strip()

    # 处理带国际区号的手机号（如 +8613800138000）
    if phone.startswith("+"):
        # 提取国家码和号码部分
        match = re.match(r"(\+\d{1,3})(\d+)", phone)
        if match:
            country_code = match.group(1)
            number = match.group(2)
            return country_code + mask_phone(number, mask_char)

    # 处理 11 位中国大陆手机号
    if len(phone) == 11 and phone.isdigit() and phone.startswith("1"):
        return _mask_string(phone, 3, 4, mask_char)

    # 处理固定电话（带区号，如：01012345678）
    if len(phone) >= 8 and phone.isdigit():
        # 区号 3-4 位，号码 7-8 位
        if len(phone) == 11:  # 3位区号 + 8位号码
            return phone[:3] + mask_char * 4 + phone[-4:]
        elif len(phone) == 12:  # 4位区号 + 8位号码
            return phone[:4] + mask_char * 4 + phone[-4:]
        elif len(phone) == 10:  # 3位区号 + 7位号码
            return phone[:3] + mask_char * 3 + phone[-4:]

    # 其他格式，保留首尾各若干位
    if len(phone) > 7:
        return _mask_string(phone, 3, 4, mask_char)

    return phone


def mask_phone_all(phone: str, mask_char: str = "*") -> str:
    """
    手机号脱敏（严格模式）：只保留前3位，其余全部掩码

    参数:
        phone: 原始手机号
        mask_char: 掩码字符

    返回:
        脱敏后的手机号

    示例:
        >>> mask_phone_all("13800138000")
        '138********'
    """
    if not _validate_input(phone, "手机号"):
        return phone

    phone = phone.strip()

    if len(phone) > 3:
        return phone[:3] + mask_char * (len(phone) - 3)

    return phone


# ============================================================
# 三、身份证号脱敏
# ============================================================

def mask_id_card(id_card: str, mask_char: str = "*") -> str:
    """
    身份证号脱敏

    脱敏规则：
        - 18位身份证：保留前6位和后4位，中间8位用掩码
          （前6位地址码 + 中间8位出生日期 + 后3位顺序码 + 1位校验码）
        - 15位身份证：保留前6位和后3位，中间6位用掩码
        - 示例：110101********1234

    参数:
        id_card: 原始身份证号
        mask_char: 掩码字符

    返回:
        脱敏后的身份证号

    示例:
        >>> mask_id_card("110101199001011234")
        '110101********1234'
        >>> mask_id_card("110101900101123")
        '110101******123'
    """
    if not _validate_input(id_card, "身份证号"):
        return id_card

    id_card = id_card.strip().upper()  # 大写处理（X的情况）

    # 18位身份证号
    if len(id_card) == 18:
        # 简单验证格式（不完全校验，只做基本判断）
        if re.match(r"^\d{17}[\dXx]$", id_card):
            # 保留前6位（地址码）和后4位（顺序码后2位+校验码）
            return _mask_string(id_card, 6, 4, mask_char)
        else:
            # 格式不对的，也做通用脱敏
            return _mask_string(id_card, 6, 4, mask_char)

    # 15位身份证号（旧版）
    elif len(id_card) == 15:
        if re.match(r"^\d{15}$", id_card):
            # 保留前6位和后3位
            return _mask_string(id_card, 6, 3, mask_char)
        else:
            return _mask_string(id_card, 6, 3, mask_char)

    # 其他长度，通用处理
    else:
        if len(id_card) > 10:
            return _mask_string(id_card, 4, 4, mask_char)

    return id_card


def mask_id_card_birthday(id_card: str, mask_char: str = "*") -> str:
    """
    身份证号脱敏（只隐藏出生日期）

    脱敏规则：
        - 只隐藏中间8位出生日期
        - 保留前6位地址码和后4位
        - 与 mask_id_card 效果相同，但语义更明确

    参数:
        id_card: 原始身份证号
        mask_char: 掩码字符

    返回:
        脱敏后的身份证号
    """
    return mask_id_card(id_card, mask_char)


# ============================================================
# 四、银行卡号脱敏
# ============================================================

def mask_bank_card(card_number: str, mask_char: str = "*") -> str:
    """
    银行卡号脱敏

    脱敏规则：
        - 保留前6位（发卡行标识代码 BIN）和后4位
        - 中间部分用掩码
        - 自动忽略空格和横线等分隔符

    参数:
        card_number: 原始银行卡号
        mask_char: 掩码字符

    返回:
        脱敏后的银行卡号（保留原始分隔符格式）

    示例:
        >>> mask_bank_card("6222021234567890123")
        '622202*********0123'
        >>> mask_bank_card("6222 0212 3456 7890 123")
        '6222 02** **** **** 0123'
    """
    if not _validate_input(card_number, "银行卡号"):
        return card_number

    card_number = card_number.strip()

    # 记录原始格式（空格、横线等分隔符位置）
    # 先提取纯数字
    digits = re.sub(r"\D", "", card_number)

    # 纯数字长度检查（银行卡号一般 13-19 位）
    if len(digits) < 13:
        return card_number

    # 对纯数字进行脱敏
    # 保留前6位和后4位
    masked_digits = _mask_string(digits, 6, 4, mask_char)

    # 如果原始卡号没有分隔符，直接返回
    if len(card_number) == len(digits):
        return masked_digits

    # 有分隔符的情况，需要按原始格式重新插入掩码
    result = []
    digit_idx = 0
    for char in card_number:
        if char.isdigit():
            if digit_idx < len(masked_digits):
                result.append(masked_digits[digit_idx])
            digit_idx += 1
        else:
            result.append(char)

    return "".join(result)


def mask_bank_card_simple(card_number: str, mask_char: str = "*") -> str:
    """
    银行卡号脱敏（简单模式）：只显示后4位

    参数:
        card_number: 原始银行卡号
        mask_char: 掩码字符

    返回:
        脱敏后的银行卡号

    示例:
        >>> mask_bank_card_simple("6222021234567890123")
        '***************0123'
    """
    if not _validate_input(card_number, "银行卡号"):
        return card_number

    card_number = card_number.strip()
    digits = re.sub(r"\D", "", card_number)

    if len(digits) <= 4:
        return card_number

    return mask_char * (len(digits) - 4) + digits[-4:]


# ============================================================
# 五、邮箱脱敏
# ============================================================

def mask_email(email: str, mask_char: str = "*") -> str:
    """
    邮箱脱敏

    脱敏规则：
        - 用户名部分：保留首字符，其余用掩码
        - 域名部分：完整显示
        - 用户名只有1位时：显示该位 + 掩码
        - 用户名只有2位时：显示首字符 + 1个掩码

    参数:
        email: 原始邮箱地址
        mask_char: 掩码字符

    返回:
        脱敏后的邮箱地址

    示例:
        >>> mask_email("zhangsan@example.com")
        'z*******@example.com'
        >>> mask_email("ab@example.com")
        'a*@example.com'
        >>> mask_email("a@example.com")
        'a*@example.com'
    """
    if not _validate_input(email, "邮箱"):
        return email

    email = email.strip()

    # 邮箱格式校验
    if "@" not in email:
        return email

    username, domain = email.split("@", 1)

    if not username or not domain:
        return email

    username_len = len(username)

    # 用户名只有1个字符
    if username_len == 1:
        masked_username = username + mask_char
    # 用户名有2个字符
    elif username_len == 2:
        masked_username = username[0] + mask_char
    # 用户名3个及以上字符
    else:
        # 保留首字符，其余掩码
        masked_username = username[0] + mask_char * (username_len - 1)

    return f"{masked_username}@{domain}"


def mask_email_middle(email: str, mask_char: str = "*") -> str:
    """
    邮箱脱敏（保留首尾）：用户名保留首尾各1个字符

    参数:
        email: 原始邮箱地址
        mask_char: 掩码字符

    返回:
        脱敏后的邮箱地址

    示例:
        >>> mask_email_middle("zhangsan@example.com")
        'z******n@example.com'
    """
    if not _validate_input(email, "邮箱"):
        return email

    email = email.strip()

    if "@" not in email:
        return email

    username, domain = email.split("@", 1)

    if not username or not domain:
        return email

    username_len = len(username)

    if username_len <= 2:
        # 太短就只显示第一个
        return mask_email(email, mask_char)

    # 保留首尾各1个字符
    masked_username = username[0] + mask_char * (username_len - 2) + username[-1]

    return f"{masked_username}@{domain}"


# ============================================================
# 六、地址脱敏
# ============================================================

def mask_address(address: str, mask_char: str = "*", 
                 keep_level: int = 3) -> str:
    """
    地址脱敏

    脱敏规则：
        - 保留到指定行政级别，详细地址用掩码
        - 行政级别：1=省/直辖市，2=市，3=区/县，4=街道/乡镇，5=详细地址
        - 默认保留到区县级

    参数:
        address: 原始地址
        mask_char: 掩码字符
        keep_level: 保留到第几级（1-5），默认3级（区/县）

    返回:
        脱敏后的地址

    示例:
        >>> mask_address("北京市海淀区中关村大街1号")
        '北京市海淀区***'
        >>> mask_address("北京市海淀区中关村大街1号", keep_level=2)
        '北京市***'
    """
    if not _validate_input(address, "地址"):
        return address

    address = address.strip()

    # 行政级别关键词
    province_keywords = ["省", "市", "自治区", "特别行政区"]  # 省级
    city_keywords = ["市", "州", "盟", "地区"]  # 市级
    district_keywords = ["区", "县", "旗", "市辖区"]  # 区县级
    street_keywords = ["街道", "镇", "乡", "路", "街", "大道"]  # 街道级

    # 简化实现：根据关键词分割地址
    # 实际生产中建议使用地址解析库（如 cpca、jionlp）

    levels = []  # 各级地址

    # 简单的地址分级（仅供演示，实际应使用专业地址解析）
    # 查找省级
    province_end = 0
    for keyword in ["省", "自治区", "特别行政区"]:
        idx = address.find(keyword)
        if idx > 0:
            province_end = idx + len(keyword)
            break

    # 北京市、上海市等直辖市
    if province_end == 0:
        # 检查是否以"市"结尾的前两个字是直辖市
        for municipality in ["北京", "上海", "天津", "重庆"]:
            if address.startswith(municipality):
                province_end = len(municipality) + 1  # +市
                if address[len(municipality)] == "市":
                    break
                province_end = len(municipality)
                break

    if province_end > 0:
        levels.append(address[:province_end])
    else:
        # 没有识别出省，可能直接是市
        province_end = 0

    # 查找市级（在省之后）
    city_end = province_end
    remaining = address[province_end:]
    for keyword in ["市", "州", "盟"]:
        idx = remaining.find(keyword)
        if idx > 0:
            city_end = province_end + idx + len(keyword)
            break

    if city_end > province_end:
        levels.append(address[province_end:city_end])
    else:
        city_end = province_end

    # 查找区县级（在市之后）
    district_end = city_end
    remaining = address[city_end:]
    for keyword in ["区", "县", "旗"]:
        idx = remaining.find(keyword)
        if idx > 0:
            district_end = city_end + idx + len(keyword)
            break

    if district_end > city_end:
        levels.append(address[city_end:district_end])
    else:
        district_end = city_end

    # 查找街道级（在区县之后）
    street_end = district_end
    remaining = address[district_end:]
    for keyword in ["街道", "镇", "乡"]:
        idx = remaining.find(keyword)
        if idx > 0:
            street_end = district_end + idx + len(keyword)
            break

    if street_end > district_end:
        levels.append(address[district_end:street_end])
    else:
        street_end = district_end

    # 剩余部分是详细地址
    detail = address[street_end:]
    if detail:
        levels.append(detail)

    # 根据保留级别确定显示到哪一级
    if keep_level >= len(levels):
        # 级别比实际层级多，全部显示
        return address

    # 保留前 keep_level 级，其余掩码
    visible_part = "".join(levels[:keep_level])
    masked_part = mask_char * 3  # 用3个掩码表示隐藏部分

    return visible_part + masked_part


def mask_address_detail(address: str, mask_char: str = "*") -> str:
    """
    地址脱敏（只保留到区县级，详细地址掩码）

    参数:
        address: 原始地址
        mask_char: 掩码字符

    返回:
        脱敏后的地址
    """
    return mask_address(address, mask_char, keep_level=3)


# ============================================================
# 七、数据模糊化
# ============================================================

def blur_number(value: Union[int, float], range_percent: float = 10.0) -> float:
    """
    数值模糊化：在原始值基础上随机偏移一定百分比

    参数:
        value: 原始数值
        range_percent: 偏移百分比范围（正负），如 10 表示 ±10%

    返回:
        模糊化后的数值

    示例:
        >>> blur_number(10000, 10)
        10532.7  # 在 9000-11000 之间随机
    """
    if value is None:
        return value

    if not isinstance(value, (int, float)):
        try:
            value = float(value)
        except (ValueError, TypeError):
            return value

    # 计算偏移量
    offset = value * (range_percent / 100.0)
    min_value = value - offset
    max_value = value + offset

    # 在范围内随机取值
    blurred = random.uniform(min_value, max_value)

    # 根据原始值类型决定返回类型
    if isinstance(value, int):
        return round(blurred)
    return round(blurred, 2)


def blur_date(date_str: str, days_range: int = 30, 
              input_format: str = "%Y-%m-%d",
              output_format: str = "%Y-%m-%d") -> str:
    """
    日期模糊化：在原始日期基础上随机偏移若干天

    参数:
        date_str: 原始日期字符串
        days_range: 偏移天数范围（正负），如 30 表示前后 30 天内
        input_format: 输入日期格式
        output_format: 输出日期格式

    返回:
        模糊化后的日期字符串

    示例:
        >>> blur_date("1990-01-01", 365)
        '1989-06-15'  # 在前后一年内随机
    """
    if not _validate_input(date_str, "日期"):
        return date_str

    try:
        # 解析日期
        date_obj = datetime.strptime(date_str, input_format)
    except ValueError:
        return date_str

    # 生成随机偏移天数
    offset_days = random.randint(-days_range, days_range)

    # 计算模糊化后的日期
    blurred_date = date_obj + timedelta(days=offset_days)

    return blurred_date.strftime(output_format)


def blur_age(age: int, range_years: int = 5) -> int:
    """
    年龄模糊化：归到年龄段

    参数:
        age: 原始年龄
        range_years: 年龄段跨度（默认5岁一档）

    返回:
        模糊化后的年龄（年龄段下限）

    示例:
        >>> blur_age(28, 5)
        25  # 表示 25-30 岁
        >>> blur_age(32, 10)
        30  # 表示 30-40 岁
    """
    if age is None:
        return age

    try:
        age = int(age)
    except (ValueError, TypeError):
        return age

    if age < 0:
        return age

    # 向下取整到年龄段
    blurred = (age // range_years) * range_years
    return blurred


def generalize_number(value: Union[int, float], step: Union[int, float]) -> Union[int, float]:
    """
    数值泛化：将数值归到指定步长的区间

    参数:
        value: 原始数值
        step: 步长（区间大小）

    返回:
        泛化后的数值（区间下限）

    示例:
        >>> generalize_number(12345, 10000)
        10000  # 表示 10000-20000
        >>> generalize_number(5678, 1000)
        5000  # 表示 5000-6000
    """
    if value is None:
        return value

    try:
        value = float(value)
        step = float(step)
    except (ValueError, TypeError):
        return value

    if step <= 0:
        return value

    generalized = (value // step) * step

    # 原始是整数且步长是整数，返回整数
    if isinstance(value, int) and isinstance(step, int):
        return int(generalized)

    return generalized


# ============================================================
# 八、高级脱敏功能
# ============================================================

def hash_mask(data: str, salt: str = "", algorithm: str = "sha256") -> str:
    """
    哈希脱敏：使用哈希算法对数据进行单向脱敏

    适用场景：
        - 需要保留数据关联性（相同数据脱敏后相同）
        - 不需要还原原始数据
        - 用于数据关联匹配

    参数:
        data: 原始数据
        salt: 盐值（增加安全性，防止彩虹表）
        algorithm: 哈希算法（md5, sha1, sha256, sha512）

    返回:
        哈希值（十六进制字符串）

    示例:
        >>> hash_mask("13800138000", "my_salt")
        'a1b2c3d4...'
    """
    if not _validate_input(data):
        return data

    data_with_salt = data + salt

    try:
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(data_with_salt.encode("utf-8"))
        return hash_obj.hexdigest()
    except ValueError:
        # 算法不支持，默认使用 sha256
        hash_obj = hashlib.sha256(data_with_salt.encode("utf-8"))
        return hash_obj.hexdigest()


def pseudonymize_name(name: str, gender: str = None) -> str:
    """
    姓名假名化：生成一个假名字替换真实姓名

    说明：
        - 每次调用结果不同（随机生成）
        - 保留姓氏（可选）
        - 适用于测试数据生成

    参数:
        name: 原始姓名（用于提取姓氏）
        gender: 性别（male/female），影响名字生成

    返回:
        假名
    """
    if not _validate_input(name, "姓名"):
        return name

    # 常见姓氏
    surnames = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜"

    # 常见名字（按性别）
    male_names = ["伟", "强", "磊", "洋", "勇", "军", "杰", "涛", "明", "超",
                  "亮", "辉", "鹏", "华", "飞", "林", "建", "斌", "波", "宇"]
    female_names = ["芳", "娜", "敏", "静", "丽", "艳", "娟", "莉", "玲", "萍",
                    "慧", "莹", "燕", "霞", "婷", "雪", "倩", "琳", "欣", "颖"]

    # 提取原姓氏（如果原姓名有意义）
    if len(name) >= 1 and name[0] in surnames:
        surname = name[0]
    else:
        surname = random.choice(surnames)

    # 根据性别选择名字
    if gender == "male":
        name_chars = male_names
    elif gender == "female":
        name_chars = female_names
    else:
        name_chars = male_names + female_names

    # 随机生成 1-2 个字的名字
    name_length = random.choice([1, 2])
    given_name = "".join(random.choices(name_chars, k=name_length))

    return surname + given_name


def shuffle_data(data_list: List[Any]) -> List[Any]:
    """
    数据置换（洗牌）：打乱数据顺序，破坏记录间的对应关系

    适用场景：
        - 保持数据分布特征
        - 破坏个体可识别性
        - 统计分析场景

    参数:
        data_list: 原始数据列表

    返回:
        打乱顺序后的列表
    """
    if not data_list:
        return data_list

    shuffled = data_list.copy()
    random.shuffle(shuffled)
    return shuffled


# ============================================================
# 九、批量脱敏工具
# ============================================================

# 字段类型与脱敏函数的映射
FIELD_MASK_FUNCTIONS = {
    "name": mask_name,               # 姓名
    "phone": mask_phone,             # 手机号
    "mobile": mask_phone,            # 手机号（别名）
    "id_card": mask_id_card,         # 身份证号
    "idcard": mask_id_card,          # 身份证号（别名）
    "identity": mask_id_card,        # 身份证号（别名）
    "bank_card": mask_bank_card,     # 银行卡号
    "bankcard": mask_bank_card,      # 银行卡号（别名）
    "email": mask_email,             # 邮箱
    "address": mask_address,         # 地址
    "age": blur_age,                 # 年龄
}


def mask_dict(data: Dict[str, Any], 
              field_rules: Dict[str, str] = None,
              auto_detect: bool = True) -> Dict[str, Any]:
    """
    字典数据批量脱敏

    支持两种模式：
    1. 指定规则：通过 field_rules 明确指定每个字段的脱敏方式
    2. 自动检测：根据字段名自动判断脱敏方式

    参数:
        data: 原始数据字典
        field_rules: 字段脱敏规则，如 {"name": "name", "phone": "phone"}
                     key 为字段名，value 为脱敏类型
        auto_detect: 是否自动检测字段类型（默认开启）

    返回:
        脱敏后的数据字典

    示例:
        >>> data = {"name": "张三", "phone": "13800138000", "id_card": "110101199001011234"}
        >>> mask_dict(data)
        {'name': '张*', 'phone': '138****8000', 'id_card': '110101********1234'}
    """
    if not data:
        return data

    result = data.copy()

    # 处理指定规则
    if field_rules:
        for field, rule_type in field_rules.items():
            if field in result:
                mask_func = FIELD_MASK_FUNCTIONS.get(rule_type)
                if mask_func:
                    result[field] = mask_func(result[field])

    # 自动检测模式
    if auto_detect:
        for field in result:
            # 如果已经通过指定规则处理过，跳过
            if field_rules and field in field_rules:
                continue

            # 字段名小写，便于匹配
            field_lower = field.lower()

            # 尝试匹配字段类型
            for field_type, mask_func in FIELD_MASK_FUNCTIONS.items():
                if field_type in field_lower:
                    # 确保是字符串类型才脱敏
                    if isinstance(result[field], str):
                        result[field] = mask_func(result[field])
                    break

    return result


def mask_list(data_list: List[Dict[str, Any]], 
              field_rules: Dict[str, str] = None,
              auto_detect: bool = True) -> List[Dict[str, Any]]:
    """
    列表数据批量脱敏

    参数:
        data_list: 原始数据列表（每个元素是字典）
        field_rules: 字段脱敏规则
        auto_detect: 是否自动检测字段类型

    返回:
        脱敏后的数据列表
    """
    if not data_list:
        return data_list

    return [
        mask_dict(item, field_rules, auto_detect)
        for item in data_list
    ]


# ============================================================
# 十、使用示例与测试
# ============================================================

def demo_all_functions():
    """
    演示所有脱敏功能

    运行此函数可查看各种脱敏效果
    """
    print("=" * 60)
    print("数据脱敏工具 - 功能演示")
    print("=" * 60)

    # 1. 姓名脱敏
    print("\n【1. 姓名脱敏】")
    names = ["张三", "张三丰", "欧阳修文", "李", "诸葛孔明"]
    for name in names:
        masked = mask_name(name)
        masked_full = mask_name_full(name)
        print(f"  {name:>8} → {masked:8} （严格模式：{masked_full}）")

    # 2. 手机号脱敏
    print("\n【2. 手机号脱敏】")
    phones = ["13800138000", "13912345678", "+8613800138000", "01012345678"]
    for phone in phones:
        masked = mask_phone(phone)
        print(f"  {phone:>18} → {masked}")

    # 3. 身份证号脱敏
    print("\n【3. 身份证号脱敏】")
    id_cards = ["110101199001011234", "310101198512125678", "44010119991231123X", "110101900101123"]
    for idc in id_cards:
        masked = mask_id_card(idc)
        print(f"  {idc:>20} → {masked}")

    # 4. 银行卡号脱敏
    print("\n【4. 银行卡号脱敏】")
    bank_cards = ["6222021234567890123", "6222 0212 3456 7890 123", "4367421234567890"]
    for card in bank_cards:
        masked = mask_bank_card(card)
        print(f"  {card:>25} → {masked}")

    # 5. 邮箱脱敏
    print("\n【5. 邮箱脱敏】")
    emails = ["zhangsan@example.com", "a@test.com", "ab@test.com", "li_si123@company.org"]
    for email in emails:
        masked = mask_email(email)
        masked_mid = mask_email_middle(email)
        print(f"  {email:>30} → {masked:25} （首尾保留：{masked_mid}）")

    # 6. 地址脱敏
    print("\n【6. 地址脱敏】")
    addresses = [
        "北京市海淀区中关村大街1号",
        "上海市浦东新区陆家嘴金融中心88号",
        "广东省深圳市南山区科技园路1号",
        "浙江省杭州市西湖区文三路100号",
    ]
    for addr in addresses:
        masked = mask_address(addr)
        print(f"  {addr}")
        print(f"    → {masked}")

    # 7. 数据模糊化
    print("\n【7. 数据模糊化】")
    print(f"  工资 10000 元（±10%） → {blur_number(10000, 10)} 元")
    print(f"  生日 1990-01-01（±30天） → {blur_date('1990-01-01', 30)}")
    print(f"  年龄 28 岁（5岁一档） → {blur_age(28, 5)} 岁")
    print(f"  收入 12345 元（千位泛化） → {generalize_number(12345, 1000)} 元")

    # 8. 哈希脱敏
    print("\n【8. 哈希脱敏】")
    print(f"  手机号 13800138000 → {hash_mask('13800138000', 'salt123')[:32]}...")

    # 9. 批量脱敏
    print("\n【9. 批量脱敏（字典）】")
    user_data = {
        "name": "张三丰",
        "phone": "13800138000",
        "id_card": "110101199001011234",
        "email": "zhangsan@example.com",
        "address": "北京市海淀区中关村大街1号",
        "age": 28,
        "remark": "普通用户",  # 非敏感字段，不处理
    }
    masked_data = mask_dict(user_data)
    print("  原始数据：")
    for k, v in user_data.items():
        print(f"    {k}: {v}")
    print("  脱敏后：")
    for k, v in masked_data.items():
        print(f"    {k}: {v}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


def run_tests():
    """
    运行单元测试
    """
    print("运行单元测试...")

    # 姓名测试
    assert mask_name("张三") == "张*", "姓名脱敏失败（2字）"
    assert mask_name("张三丰") == "张*丰", "姓名脱敏失败（3字）"
    assert mask_name("") == "", "空姓名处理失败"

    # 手机号测试
    assert mask_phone("13800138000") == "138****8000", "手机号脱敏失败"
    assert mask_phone("") == "", "空手机号处理失败"

    # 身份证测试
    assert mask_id_card("110101199001011234") == "110101********1234", "身份证脱敏失败"

    # 银行卡测试
    assert mask_bank_card("6222021234567890123") == "622202*********0123", "银行卡脱敏失败"

    # 邮箱测试
    assert "@" in mask_email("test@example.com"), "邮箱脱敏失败"

    # 地址测试
    result = mask_address("北京市海淀区中关村大街1号")
    assert "北京市海淀区" in result, "地址脱敏失败"

    # 数值模糊化测试
    blurred = blur_number(10000, 10)
    assert 9000 <= blurred <= 11000, "数值模糊化范围错误"

    # 年龄模糊化测试
    assert blur_age(28, 5) == 25, "年龄模糊化失败"

    print("所有测试通过！")


# ============================================================
# 主程序入口
# ============================================================

if __name__ == "__main__":
    """
    主函数：运行演示和测试
    """
    # 运行演示
    demo_all_functions()

    # 运行测试
    print("\n")
    run_tests()
