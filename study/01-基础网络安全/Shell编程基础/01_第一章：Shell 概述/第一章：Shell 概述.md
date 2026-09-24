# 第一章：Shell 概述

### 1.1 什么是 Shell

Shell 是用户与操作系统内核之间的接口程序，它接收用户输入的命令，调用相应的应用程序或系统服务，是 Linux 系统中最重要的交互工具之一。

Shell 既是一种命令解释器，也是一种编程语言（Shell 脚本）。

### 1.2 常见的 Shell 类型

| Shell 名称 | 说明 | 默认位置 |
|-----------|------|---------|
| **Bash** (Bourne Again Shell) | 最流行的 Shell，Linux 默认 Shell，功能丰富 | `/bin/bash` |
| **sh** (Bourne Shell) | 最原始的 Unix Shell，兼容性好 | `/bin/sh` |
| **zsh** (Z Shell) | 功能强大，支持插件和主题，Mac 默认 | `/bin/zsh` |
| **csh / tcsh** | C Shell，语法类似 C 语言 | `/bin/csh` |
| **ksh** (Korn Shell) | 结合了 sh 和 csh 的优点 | `/bin/ksh` |
| **fish** | 友好的交互式 Shell，语法简单 | `/usr/bin/fish` |

> 本教程以 **Bash** 为标准，这是 Linux 系统中最通用的 Shell。

### 1.3 第一个 Shell 脚本

创建一个名为 `hello.sh` 的文件：

```bash
#!/bin/bash
# 这是注释：我的第一个 Shell 脚本
echo "Hello, World!"
```

**脚本结构说明**：
- `#!/bin/bash`：Shebang（释伴行），指定脚本使用的解释器
- `# 注释内容`：注释行，不被执行
- `echo`：输出命令

**运行脚本的方式**：

```bash
# 方式一：赋予执行权限后直接运行（推荐）
chmod +x hello.sh
./hello.sh

# 方式二：用 bash 解释器运行
bash hello.sh

# 方式三：用 source 运行（在当前 Shell 中执行）
source hello.sh
. hello.sh   # 等价于 source
```

### 1.4 Shell 脚本的执行过程

1. 读取脚本文件，逐行解析
2. 遇到 `#` 开头的行（除 `#!`）视为注释，跳过
3. 执行命令、变量替换、命令替换
4. 遇到控制结构（if/for/while 等）进行相应的逻辑判断
5. 逐行执行直到文件结束或遇到 `exit`

### 1.5 退出状态码

每个 Linux 命令执行后都会返回一个退出状态码（exit code）：

- **0**：命令执行成功
- **非 0**：命令执行失败（1~255）

```bash
# 查看上一条命令的退出状态码
echo $?

# 示例
ls /etc
echo $?   # 输出 0，表示成功

ls /nonexistent
echo $?   # 输出非 0，表示失败
```

---

---

