# IDA Pro使用指南

### 6.1 IDA界面与视图

**主要视图：**
- IDA View-A：反汇编视图（文本/图形模式切换）
- Pseudocode-A：伪代码视图（Hex-Rays反编译器）
- Hex View-A：十六进制视图
- Functions：函数列表
- Strings：字符串列表
- Exports/Imports：导出/导入表
- Structures：结构体定义
- Enum：枚举定义

### 6.2 常用快捷键速查

| 类别 | 快捷键 | 功能 |
|------|--------|------|
| 导航 | G | 跳转到地址 |
| 导航 | Esc | 返回上一个位置 |
| 导航 | Ctrl+B | 添加书签 |
| 导航 | Alt+G | 跳转到段 |
| 视图 | 空格 | 切换图形/文本视图 |
| 视图 | Shift+F12 | 字符串列表 |
| 视图 | Ctrl+F | 搜索 |
| 代码 | C | 转为代码 |
| 代码 | D | 转为数据 |
| 代码 | A | 转为ASCII字符串 |
| 代码 | U | 取消定义 |
| 代码 | P | 创建函数 |
| 重命名 | N | 重命名 |
| 注释 | ; | 添加注释 |
| 注释 | Insert | 重复注释 |
| 类型 | Y | 设置类型 |
| 类型 | Alt+F8 | 打开结构体 |
| 交叉引用 | X | 查看交叉引用 |
| 交叉引用 | Ctrl+X | 查看所有引用 |
| 反编译 | F5 | 反编译（Hex-Rays） |
| 搜索 | Alt+T | 搜索文本 |
| 搜索 | Alt+B | 搜索二进制 |
| 搜索 | Alt+I | 搜索立即数 |

### 6.3 IDAPython脚本

```python
# 脚本1：批量重命名函数（基于字符串引用推断函数名）
import idautils
import idc

def rename_functions_by_strings():
    """通过字符串引用推断函数名"""
    for s in idautils.Strings():
        # 查找引用该字符串的函数
        for xref in idautils.XrefsTo(s.ea):
            func = idaapi.get_func(xref.frm)
            if func:
                old_name = idc.get_func_name(func.start_ea)
                if old_name.startswith("sub_"):
                    new_name = "func_" + str(s)[:20].replace(" ", "_")
                    idc.set_name(func.start_ea, new_name, idc.SN_NOWARN)
                    print(f"重命名 {old_name} -> {new_name}")

# 脚本2：提取所有加密常量
def find_crypto_constants():
    """搜索已知加密算法的常量"""
    # AES S-box起始
    aes_sbox_start = 0x63, 0x7c, 0x77, 0x7b
    # MD5初始值
    md5_init = 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476
    # SHA-1初始值
    sha1_init = 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476
    
    for ea in idautils.Heads():
        if idc.get_operand_type(ea, 0) == idc.o_imm:
            val = idc.get_operand_value(ea, 0)
            if val in md5_init:
                print(f"[+] 可能的MD5常量: 0x{val:08X} @ {hex(ea)}")
            if val in sha1_init:
                print(f"[+] 可能的SHA-1常量: 0x{val:08X} @ {hex(ea)}")

# 脚本3：自动分析并标注危险函数
def analyze_dangerous_functions():
    """标注危险函数调用"""
    dangerous = {
        'strcpy': '栈溢出风险',
        'strcat': '栈溢出风险',
        'sprintf': '格式化字符串风险',
        'gets': '栈溢出风险',
        'scanf': '栈溢出风险',
        'system': '命令注入风险',
        'execve': '命令执行',
    }
    
    for name, risk in dangerous.items():
        ea = idc.get_name_ea_simple(name)
        if ea != idc.BADADDR:
            for ref in idautils.CodeRefsTo(ea, 1):
                func_name = idc.get_func_name(ref) or "未知函数"
                idc.set_cmt(ref, f"[安全警告] {name} - {risk}", 0)
                print(f"[!] {risk}: {name} 调用于 {hex(ref)} (函数: {func_name})")
```

---

---

## 📋 内容审核与补充建议

> 针对「IDA Pro使用指南」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
