# Stack Canary栈保护

### 4.1 Canary原理

```
Stack Canary (栈金丝雀值) 工作原理:

函数调用时在栈上放置随机值:
  +------------------+
  | 局部变量         |
  | ...              |
  | [CANARY]         |  <- 随机值(函数prologue插入)
  | 保存的EBP        |
  | 返回地址         |
  +------------------+

函数返回前检查Canary:
  if (canary != __stack_chk_fail) {
      __stack_chk_fail();  // 触发终止
  }

  攻击者溢出时:
  [AAAAAAA][覆盖Canary][覆盖EBP][覆盖返回地址]
  如果Canary不匹配 -> 程序终止
```

**Canary类型**

| 类型 | 特征 | 线程局部存储 |
|------|------|-------------|
| Terminator Canary | 包含\x00(终止符) | 否 |
| Random Canary | 随机值 | 否 |
| Random XOR Canary | 随机值异或 | 是 |
| Master Canary | TLS存储 | 是 |

```
Linux Canary实现:
  - 存储在TLS (Thread Local Storage)中
  - 每个线程独立
  - 进程启动时从/dev/urandom随机生成
  - 函数prologue: mov rax, [fs:0x28]; mov [rbp-8], rax
  - 函数epilogue: mov rax, [rbp-8]; xor rax, [fs:0x28]; je ok; call __stack_chk_fail

Windows Canary:
  - 类似机制 /GS编译选项
  - 存储在__security_cookie
```

### 4.2 绕过技术

**信息泄露绕过**

```
攻击链:
  1. 信息泄露漏洞 -> 读取栈上的Canary值
  2. 溢出时保持Canary不变
  3. 覆盖返回地址

  常见泄露场景:
  - 格式化字符串漏洞泄露栈数据
  - 越界读漏洞读取Canary
  - 时间侧信道

格式化字符串泄露:
  printf(input);  // 用户控制格式化字符串
  输入: %p.%p.%p.%p.%p
  读取栈上数据，Canary在第6-7个参数位置

  payload: "%6$p"
  输出Canary值: 0x12345678abcdef00

  然后在溢出时:
  [填充][Canary值][EBP][返回地址]
```

**逐字节爆破绕过**

```
当程序有fork()时:
  - 子进程继承父进程的Canary
  - 可以逐字节暴力破解

  原理:
  - Canary最低字节通常是\x00(终止符)
  - 逐个字节尝试(每字节最多256次)
  - 如果程序不崩溃 -> 字节正确
  - 继续下一个字节

  总尝试次数: 256 * 7 = 1792次
  (第一字节已知为\x00)

  适用场景:
  - fork服务器
  - 程序不重启Canary
```

**覆盖TLS绕过**

```
如果可以写入TLS区域:
  - 修改TLS中的Canary值
  - 同时修改栈上Canary
  - 绕过检查

  需要任意写漏洞
  需要知道TLS地址
```

---

---

