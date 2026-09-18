# RELRO只读重定位

### 5.1 RELRO原理

RELRO (RELocation Read-Only) 保护GOT (Global Offset Table) 表不被篡改。

```
无RELRO:
  GOT表可写
  攻击者可以覆盖GOT条目
  实现函数劫持

  示例:
  覆盖printf@GOT为system地址
  下次调用printf时实际调用system

部分RELRO (Partial RELRO):
  .got段只读(包含不可变重定位)
  .got.plt仍可写(延迟绑定需要)
  攻击者仍可覆盖.got.plt

完全RELRO (Full RELRO):
  所有GOT表只读
  延迟绑定被禁用(启动时全部绑定)
  GOT覆盖攻击不可行
```

```bash
# 检查RELRO状态
readelf -l ./binary | grep -i gnu_relro
# 有GNU_RELRO段 = 至少Partial RELRO

# 检查是否Full RELRO
readelf -d ./binary | grep -i bind_now
# 有BIND_NOW = Full RELRO

# 使用checksec
checksec --file=./binary
# 输出: RELRO: Full RELRO / Partial RELRO / No RELRO
```

### 5.2 绕过技术

**Partial RELRO绕过**

```
虽然.got被保护，但.got.plt仍可写:
  覆盖.got.plt中的函数地址

  攻击:
  覆盖printf@got.plt -> system
  printf("/bin/sh") 变成 system("/bin/sh")
```

**Full RELRO绕过**

```
Full RELRO下GOT不可写，但可以:
  1. 覆盖其他函数指针
     - .fini_array (析构函数数组)
     - __malloc_hook / __free_hook (已废弃)
     - atexit处理函数

  2. 覆盖栈上的函数指针
     - 虚函数表(vtable)
     - 回调函数指针

  3. 数据导向攻击
     - 不修改控制流
     - 直接修改关键数据
```

---

---

## 📋 内容审核与补充建议

> 针对「RELRO只读重定位」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
