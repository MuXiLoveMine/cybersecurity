# Ghidra使用指南

### 7.1 Ghidra工作流程

1. **导入文件**：File -> Import File，自动识别格式
2. **分析**：Auto-Analyze，选择分析器
3. **导航**：Symbol Tree、Functions窗口
4. **反编译**：双击函数查看伪代码
5. **标注**：重命名变量、添加注释、定义类型

### 7.2 Ghidra关键操作

| 操作 | 快捷键 | 说明 |
|------|--------|------|
| 反编译 | Ctrl+Shift+D | 打开反编译窗口 |
| 重命名 | L | 重命名变量/函数 |
| 类型 | Ctrl+L | 设置变量类型 |
| 交叉引用 | Ctrl+Shift+F | 查找引用 |
| 搜索 | Ctrl+Shift+E | 搜索程序 |
| 注释 | ; | 添加注释 |
| 数据 | Ctrl+D | 转为数据 |
| 代码 | C | 转为代码 |

### 7.3 Ghidra脚本

```python
# Ghidra脚本：自动识别和标注字符串解密
# @category Security

from ghidra.program.model.data import StringDataType

def find_xor_decryption():
    """查找XOR解密模式"""
    listing = currentProgram.getListing()
    instIter = listing.getInstructions(True)
    
    while instIter.hasNext():
        inst = instIter.next()
        mnemonic = inst.getMnemonicString()
        
        # 查找XOR指令
        if mnemonic == "XOR":
            # 检查是否为异或解密
            refs = getReferencesTo(inst.getAddress())
            if refs:
                print("[+] 可能的XOR解密: %s" % inst.getAddress())

def extract_all_strings():
    """提取所有字符串"""
    dataIterator = currentProgram.getListing().getDefinedData(True)
    strings = []
    
    while dataIterator.hasNext():
        data = dataIterator.next()
        if data.getDataType() instanceof StringDataType:
            addr = data.getAddress()
            value = data.getValue()
            strings.append((addr.toString(), value))
    
    return strings
```

---

---

## 📋 内容审核与补充建议

> 针对「Ghidra使用指南」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
