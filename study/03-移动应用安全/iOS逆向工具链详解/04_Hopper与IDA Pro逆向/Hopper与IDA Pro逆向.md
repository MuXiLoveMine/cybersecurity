# Hopper与IDA Pro逆向

### 4.1 Hopper Disassembler

Hopper是macOS/Linux上的逆向工程工具，支持Mach-O文件分析：

```
# 基本操作流程
1. 打开Mach-O二进制文件
2. 等待自动分析完成
3. 使用导航条浏览代码段
4. 双击函数查看反汇编
5. 使用Ctrl+D查看伪代码
6. 使用标记功能标注关键函数

# 常用快捷键
- N: 重命名符号
- X: 查看交叉引用
- D: 转换为数据
- C: 转换为代码
- A: 转换为ASCII
- G: 跳转到地址
- :: 添加注释

# 分析技巧
1. 搜索字符串: 使用Search -> Strings
2. 搜索函数名: 使用Search -> Labels
3. 查找入口点: 查找_start符号
4. 分析ObjC方法: 搜索objc_msgSend
5. 分析Swift方法: 搜索swift_前缀
```

### 4.2 IDA Pro iOS逆向

IDA Pro是业界标准的反汇编工具，支持iOS二进制分析：

```
# iOS逆向分析流程

1. 加载Mach-O文件
   - File -> Open -> 选择Mach-O文件
   - 选择ARM64架构
   - 等待自动分析完成

2. 常用分析功能
   - View -> Open subviews -> Strings: 字符串窗口
   - View -> Open subviews -> Functions: 函数列表
   - View -> Open subviews -> Imports: 导入表
   - View -> Open subviews -> Exports: 导出表
   - View -> Open subviews -> Structs: 结构体定义

3. ObjC方法分析
   - 查找objc_msgSend调用
   - 分析SEL参数引用
   - 跟踪方法调用链
   - 使用Shift+F1查看类型库

4. 脚本自动化
   # IDAPython脚本示例
   import idautils
   import idc

   # 查找所有objc_msgSend调用
   for seg in idautils.Segments():
       for func in idautils.Functions(idc.get_segm_start(seg), idc.get_segm_end(seg)):
           name = idc.get_func_name(func)
           if name and 'objc_msgSend' in name:
               print(f"Found at: 0x{func:x}")

5. 加密算法识别
   - 使用FindCrypt插件识别加密常量
   - 分析AES/SHA/RSA相关函数
   - 查找硬编码密钥
```

---

---

