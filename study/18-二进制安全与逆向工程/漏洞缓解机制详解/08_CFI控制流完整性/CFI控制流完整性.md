# CFI控制流完整性

### 7.1 CFI原理

CFI (Control Flow Integrity) 确保程序的控制流遵循预定义的图。

```
正常控制流:
  call functionA -> 合法目标
  call functionB -> 合法目标

无CFI时攻击:
  覆盖返回地址/函数指针 -> 任意地址
  执行非预期代码

CFI检查:
  间接调用前检查目标是否在合法集合中
  if (target not in allowed_targets):
      abort()

  检查点:
  - 间接调用 (call [rax])
  - 间接跳转 (jmp [rax])
  - 返回地址 (ret)
  - 函数指针
  - 虚函数表
```

### 7.2 CFG原理

CFG (Control Flow Guard) 是微软Windows实现的CFI。

```
CFG工作流程:
  1. 编译时分析所有间接调用目标
  2. 生成合法目标位图(bitmap)
  3. 间接调用前插入检查:
     __guard_check_icall(&target)
     if (bitmap[target/8] & (1 << (target%8))):
         call target  // 合法
     else:
         __guard_dispatch_icall()  // 非法，终止

  编译选项:
  cl /guard:cf source.c    # 启用CFG
  gcc -fcf-protection      # GCC的CFI
```

### 7.3 绕过技术

**数据导向攻击 (Data-Oriented Attacks)**

```
不修改控制流，直接修改数据:

  1. 修改关键变量
     - 身份验证标志: is_admin = true
     - 权限标志: privilege_level = 0
     - 配置值: debug_mode = true

  2. 修改函数参数
     - 修改传给敏感函数的参数
     - 不需要劫持控制流

  示例:
  溢出修改isAuthenticated变量
  if (isAuthenticated) -> true
  绕过认证
```

**COOP (Counterfeit Object-Oriented Programming)**

```
利用C++虚函数表:

  1. 伪造虚函数表
  2. 虚函数调用使用伪造的表
  3. 调用任意合法函数

  虽然CFI保护了直接跳转
  但虚函数调用是通过虚表间接的
  伪造虚表可以在合法函数间跳转
```

**合法目标滥用**

```
CFI只检查目标是否合法:
  - 合法目标集可能包含攻击可用的函数
  - 如果目标函数本身就是危险的(如system)
  - CFG不会阻止合法调用

  攻击:
  利用漏洞使程序调用system()
  system是合法目标 -> CFG通过
```

**JOP (Jump-Oriented Programming)**

```
使用间接跳转替代ret:
  使用合法的跳转gadget
  构造JOP链
  绕过ret检查

  gadget类型:
  jmp [rax]  -> 跳转到rax指向的地址
  jmp [rbx]  -> 跳转到rbx指向的地址
```

---

---

## 📋 内容审核与补充建议

> 针对「CFI控制流完整性」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
