# subprocess 模块

> Python 标准库，用于创建子进程、执行系统命令并与其交互。

---

## 一、导入与基本用法

```python
import subprocess
```

---

## 二、常用函数

### 2.1 run() 函数（推荐）

```python
import subprocess

# 基本用法
result = subprocess.run(['ls', '-l'])

# 获取输出
result = subprocess.run(['ls', '-l'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

# 检查返回码
result = subprocess.run(['ls', 'nonexistent'], capture_output=True)
print(result.returncode)  # 非0表示失败

# 命令失败时抛出异常
result = subprocess.run(['ls', 'nonexistent'], check=True)  # 抛出 CalledProcessError

# 设置超时
result = subprocess.run(['sleep', '10'], timeout=2)  # 2秒后超时，抛出 TimeoutExpired

# 输入数据
result = subprocess.run(['cat'], input=b'hello', capture_output=True)
print(result.stdout)  # b'hello'
```

### 2.2 常用参数

```python
subprocess.run(
    args,               # 命令和参数（列表）
    stdin=None,         # 标准输入 (PIPE/DEVNULL/文件对象)
    input=None,         # 发送到 stdin 的数据
    stdout=None,        # 标准输出 (PIPE/DEVNULL/STDOUT/文件对象)
    stderr=None,        # 标准错误 (PIPE/DEVNULL/STDOUT/文件对象)
    capture_output=False,  # 捕获 stdout 和 stderr
    shell=False,        # 是否通过 shell 执行
    cwd=None,           # 工作目录
    timeout=None,       # 超时时间（秒）
    check=False,        # 非零退出码时抛异常
    text=False,         # 以文本模式处理输入输出
    encoding=None,      # 编码方式
    env=None,           # 环境变量字典
)
```

### 2.3 输出捕获

```python
# capture_output (Python 3.7+)
result = subprocess.run(['echo', 'hello'], capture_output=True, text=True)
print(result.stdout.strip())  # hello

# 手动指定
result = subprocess.run(
    ['ls'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# 重定向到文件
with open('output.txt', 'w') as f:
    subprocess.run(['ls', '-l'], stdout=f)

# stderr 合并到 stdout
result = subprocess.run(
    ['cmd'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# 丢弃输出
subprocess.run(['cmd'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
```

### 2.4 shell 参数

```python
# shell=True（不安全，如果参数来自用户输入可能导致命令注入）
result = subprocess.run('ls -l | grep txt', shell=True, capture_output=True, text=True)

# 不使用 shell（推荐，更安全）
result = subprocess.run(['ls', '-l'], capture_output=True, text=True)
```

### 2.5 Popen（高级用法）

```python
import subprocess

# 启动子进程
proc = subprocess.Popen(
    ['ping', '-c', '4', '127.0.0.1'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# 等待完成
stdout, stderr = proc.communicate()
print(stdout)
print(f"返回码: {proc.returncode}")

# 实时读取输出
proc = subprocess.Popen(
    ['ping', '-c', '4', '127.0.0.1'],
    stdout=subprocess.PIPE,
    text=True
)

for line in proc.stdout:
    print(f"输出: {line.strip()}")

proc.wait()

# 向进程发送输入
proc = subprocess.Popen(
    ['python3', '-c', 'print(input())'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

stdout, stderr = proc.communicate(input='hello world')
print(stdout.strip())  # hello world

# 终止进程
proc = subprocess.Popen(['sleep', '100'])
proc.terminate()  # 发送 SIGTERM
proc.kill()       # 发送 SIGKILL
proc.wait()

# 检查进程状态
proc = subprocess.Popen(['sleep', '5'])
print(proc.poll())  # None (还在运行)
proc.wait()
print(proc.poll())  # 0 (已结束)
```

### 2.6 管道链

```python
# ls -l | grep .py | head -5
p1 = subprocess.Popen(['ls', '-l'], stdout=subprocess.PIPE)
p2 = subprocess.Popen(['grep', '.py'], stdin=p1.stdout, stdout=subprocess.PIPE)
p3 = subprocess.Popen(['head', '-5'], stdin=p2.stdout, stdout=subprocess.PIPE, text=True)

# 关闭 p1 的 stdout，让 p1 收到 SIGPIPE
p1.stdout.close()
p2.stdout.close()

output = p3.communicate()[0]
print(output)
```

---

## 三、安全相关使用案例

### 3.1 命令注入漏洞演示

```python
import subprocess

# ===== 不安全的写法（存在命令注入） =====
def unsafe_exec(user_input):
    # 危险：直接拼接 shell 命令
    cmd = f"ping -c 1 {user_input}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

# 攻击：user_input = "127.0.0.1; cat /etc/passwd"
# 会执行两条命令

# ===== 安全的写法 =====
def safe_exec(user_input):
    # 安全：使用参数列表，不通过 shell
    result = subprocess.run(
        ['ping', '-c', '1', user_input],
        capture_output=True,
        text=True
    )
    return result.stdout

# 即使输入 "; cat /etc/passwd"，也只会作为 ping 的参数
```

### 3.2 命令白名单验证

```python
import subprocess
import shlex

ALLOWED_COMMANDS = {
    'ping': ['ping', '-c', '1'],
    'traceroute': ['traceroute', '-m', '5'],
    'nslookup': ['nslookup'],
}

def safe_command_exec(cmd_type, arg):
    """白名单验证的安全命令执行"""
    if cmd_type not in ALLOWED_COMMANDS:
        raise ValueError(f"不允许的命令类型: {cmd_type}")
    
    # 输入验证（根据需要）
    if cmd_type in ('ping', 'traceroute', 'nslookup'):
        # 验证 IP/域名格式
        import re
        if not re.match(r'^[a-zA-Z0-9.-]+$', arg):
            raise ValueError("非法的目标地址")
    
    cmd = ALLOWED_COMMANDS[cmd_type] + [arg]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return result.stdout
```

### 3.3 子进程权限控制

```python
import subprocess
import os

# 以不同用户运行（需要 root 权限）
def run_as_user(username, cmd):
    """以指定用户身份运行命令"""
    import pwd
    user = pwd.getpwnam(username)
    uid = user.pw_uid
    gid = user.pw_gid
    
    def demote():
        os.setgid(gid)
        os.setuid(uid)
    
    result = subprocess.run(
        cmd,
        preexec_fn=demote,  # 子进程 fork 后执行
        capture_output=True,
        text=True
    )
    return result.stdout

# 限制环境变量
safe_env = {
    'PATH': '/usr/bin:/bin',
    'HOME': '/tmp'
}

result = subprocess.run(
    ['cmd'],
    env=safe_env,  # 只提供必要的环境变量
    capture_output=True
)
```

### 3.4 输出安全处理

```python
import subprocess
import html

def safe_command_output(cmd_args):
    """安全地执行命令并处理输出"""
    try:
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            timeout=5,
            env={'PATH': '/usr/bin:/bin'}  # 限制环境
        )
        
        output = result.stdout + result.stderr
        
        # 限制输出长度
        if len(output) > 10000:
            output = output[:10000] + "\n... (输出已截断)"
        
        # HTML 转义（如果要在网页显示）
        # escaped_output = html.escape(output)
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'output': output
        }
        
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': '命令执行超时'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

---

## 四、旧版函数（不推荐）

```python
# call() - 只返回退出码
retcode = subprocess.call(['ls', '-l'])

# check_call() - 失败时抛异常
subprocess.check_call(['ls', '-l'])

# check_output() - 返回输出，失败抛异常
output = subprocess.check_output(['ls', '-l'], text=True)

# getoutput() - 获取命令输出（shell=True）
output = subprocess.getoutput('ls -l')

# getstatusoutput() - 获取状态码和输出
status, output = subprocess.getstatusoutput('ls -l')
```

---

## 五、安全最佳实践

| 最佳实践 | 说明 |
|---------|------|
| **使用参数列表** | `subprocess.run(['cmd', 'arg'])` 而非 `shell=True` |
| **避免 shell=True** | 除非必须使用 shell 特性，且输入完全可信 |
| **输入验证** | 用户输入必须经过白名单验证 |
| **设置超时** | 防止命令挂起导致资源耗尽 |
| **限制环境变量** | 只传递必要的环境变量 |
| **限制输出长度** | 防止大量输出导致内存问题 |
| **检查返回码** | 始终验证命令是否成功执行 |
| **使用低权限** | 以最小权限运行子进程 |
