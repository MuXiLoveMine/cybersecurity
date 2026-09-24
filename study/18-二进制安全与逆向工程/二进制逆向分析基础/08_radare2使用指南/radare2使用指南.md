# radare2使用指南

### 8.1 基本使用流程

```bash
# 1. 获取文件信息
rabin2 -I binary.exe        # 文件基本信息
rabin2 -i binary.exe        # 导入表
rabin2 -E binary.exe        # 导出表
rabin2 -S binary.exe        # 节区信息
rabin2 -s binary.exe        # 符号表
rabin2 -z binary.exe        # 字符串

# 2. 进入交互模式
r2 -A binary.exe            # -A 自动分析

# 3. 常用分析命令
> aaa                       # 分析所有
> afl                       # 列出函数
> afl~main                  # 过滤含main的函数
> pdf @ main                # 反汇编main函数
> pdc @ main                # 反编译main函数
> s main                    # 跳转到main
> VV                        # 图形视图
> iz                        # 列出字符串
> izz                       # 搜索全文件字符串
> /x 9090                   # 搜索十六进制
> / string                  # 搜索字符串
> e asm.bits=32             # 设置32位模式
> e asm.arch=x86            # 设置x86架构
```

### 8.2 radare2脚本

```javascript
# radare2脚本（JavaScript语法）
# 查找所有call到system的指令

function find_system_calls() {
    var system_addr = sym("system");
    if (system_addr === -1) {
        console.log("未找到system函数");
        return;
    }
    
    // 遍历所有函数
    var functions = afl();
    for (var i = 0; i < functions.length; i++) {
        var func_addr = functions[i];
        // 反汇编函数
        var disasm = dis.func(func_addr);
        if (disasm.indexOf("call system") !== -1) {
            console.log("[+] 发现system调用于: " + func_addr.toString(16));
        }
    }
}
```

---

---

