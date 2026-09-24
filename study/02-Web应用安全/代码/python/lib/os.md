# os 模块

> Python 标准库，提供与操作系统交互的功能，包括文件操作、进程管理、环境变量等。

---

## 一、导入与基本信息

```python
import os
```

---

## 二、文件与目录操作

### 2.1 目录操作

```python
# 获取当前工作目录
cwd = os.getcwd()

# 切换目录
os.chdir('/path/to/dir')

# 列出目录内容
files = os.listdir('.')           # 文件名列表
entries = os.scandir('.')         # DirEntry 对象（更高效）

# 遍历目录（递归）
for root, dirs, files in os.walk('/path'):
    print(f"目录: {root}")
    print(f"  子目录: {dirs}")
    print(f"  文件: {files}")

# 创建目录
os.mkdir('new_dir')               # 创建单级目录
os.makedirs('a/b/c', exist_ok=True)  # 创建多级目录

# 删除目录
os.rmdir('empty_dir')             # 删除空目录
os.removedirs('a/b/c')            # 递归删除空目录

# 重命名/移动
os.rename('old.txt', 'new.txt')
os.renames('old/path/file.txt', 'new/path/file.txt')

# 删除文件
os.remove('file.txt')
os.unlink('file.txt')  # 同上
```

### 2.2 文件属性

```python
# 获取文件信息
stat = os.stat('file.txt')
print(stat.st_size)       # 文件大小（字节）
print(stat.st_atime)      # 最后访问时间
print(stat.st_mtime)      # 最后修改时间
print(stat.st_ctime)      # 创建/元数据修改时间
print(stat.st_mode)       # 文件模式（权限）
print(stat.st_uid)        # 所有者 UID
print(stat.st_gid)        # 所属组 GID

# 文件类型判断
os.path.isfile('path')     # 是否为文件
os.path.isdir('path')      # 是否为目录
os.path.islink('path')     # 是否为符号链接
os.path.exists('path')     # 是否存在
os.path.isabs('path')      # 是否为绝对路径

# 获取文件大小
size = os.path.getsize('file.txt')

# 修改权限
os.chmod('file.txt', 0o755)    # 设置权限
os.chown('file.txt', uid, gid)  # 更改所有者（需要权限）

# 创建符号链接
os.symlink('/path/to/target', 'link_name')

# 读取符号链接目标
target = os.readlink('link_name')
```

### 2.3 路径操作（os.path）

```python
# 路径拼接
path = os.path.join('/home', 'user', 'file.txt')  # /home/user/file.txt

# 路径分割
dirname, basename = os.path.split('/home/user/file.txt')
# dirname = '/home/user', basename = 'file.txt'

# 文件名和扩展名
name, ext = os.path.splitext('file.txt')
# name = 'file', ext = '.txt'

# 绝对路径
abs_path = os.path.abspath('file.txt')

# 规范化路径
norm_path = os.path.normpath('/home/../user/./file.txt')
# /user/file.txt

# 公共路径
common = os.path.commonpath(['/a/b/c', '/a/b/d'])  # /a/b

# 相对路径
rel = os.path.relpath('/a/b/c', '/a')  # b/c

# 展开用户目录
path = os.path.expanduser('~/documents')  # /home/user/documents

# 展开环境变量
path = os.path.expandvars('$HOME/documents')
```

---

## 三、进程与环境

### 3.1 进程信息

```python
# 当前进程 ID
pid = os.getpid()

# 父进程 ID
ppid = os.getppid()

# 用户 ID / 组 ID
uid = os.getuid()
gid = os.getgid()
euid = os.geteuid()  # 有效 UID
egid = os.getegid()  # 有效 GID

# 进程组 ID
pgid = os.getpgrp()

# 设置用户/组（需要权限）
os.setuid(1000)
os.setgid(1000)
os.seteuid(1000)  # 临时切换有效 UID
```

### 3.2 环境变量

```python
# 获取所有环境变量
env = os.environ
print(dict(env))

# 获取单个环境变量
path = os.environ.get('PATH')
home = os.getenv('HOME', '/default/path')  # 带默认值

# 设置环境变量
os.environ['MY_VAR'] = 'value'
os.putenv('MY_VAR', 'value')  # 不更新 os.environ，不推荐

# 删除环境变量
del os.environ['MY_VAR']
os.unsetenv('MY_VAR')
```

### 3.3 执行系统命令

```python
# 执行命令（返回退出码）
ret = os.system('ls -l')

# 执行命令并获取输出（不推荐，用 subprocess）
output = os.popen('ls -l').read()

# exec 系列（替换当前进程）
os.execl('/bin/ls', 'ls', '-l')
os.execv('/bin/ls', ['ls', '-l'])
os.execle('/bin/ls', 'ls', '-l', {'PATH': '/usr/bin'})

# fork 子进程（Unix）
pid = os.fork()
if pid == 0:
    # 子进程
    print("子进程")
else:
    # 父进程
    print(f"父进程，子进程 PID: {pid}")
    os.wait()  # 等待子进程结束
```

---

## 四、安全相关使用案例

### 4.1 路径遍历检测与防御

```python
import os

def safe_path_join(base_dir, user_path):
    """安全的路径拼接，防止路径遍历"""
    # 规范化路径
    base = os.path.realpath(base_dir)
    full_path = os.path.realpath(os.path.join(base, user_path))
    
    # 检查是否在基础目录内
    if not full_path.startswith(base + os.sep) and full_path != base:
        raise ValueError("非法路径：路径遍历攻击检测")
    
    return full_path

# 使用示例
try:
    path = safe_path_join('/var/www/uploads', '../../etc/passwd')
except ValueError as e:
    print(f"[!] 阻止: {e}")

def is_path_safe(base_dir, target_path):
    """检查目标路径是否在基础目录内"""
    base = os.path.abspath(base_dir)
    target = os.path.abspath(target_path)
    
    # 使用 commonpath 判断
    try:
        common = os.path.commonpath([base, target])
        return common == base
    except ValueError:
        # 不同驱动器（Windows）
        return False
```

### 4.2 文件权限检查

```python
import os
import stat

def check_file_permissions(filepath):
    """检查文件权限是否安全"""
    issues = []
    
    try:
        st = os.stat(filepath)
    except OSError as e:
        return [f"无法访问: {e}"]
    
    mode = st.st_mode
    
    # 检查是否是世界可写
    if mode & stat.S_IWOTH:
        issues.append("文件世界可写 (others writable)")
    
    # 检查是否是 SUID/SGID 文件
    if mode & stat.S_ISUID:
        issues.append("SUID 位已设置")
    if mode & stat.S_ISGID:
        issues.append("SGID 位已设置")
    
    # 检查所有者
    if st.st_uid == 0:
        issues.append("文件所有者为 root")
    
    # 文件类型
    if stat.S_ISLNK(mode):
        issues.append("符号链接")
    elif stat.S_ISDIR(mode):
        issues.append("目录")
    elif stat.S_ISREG(mode):
        pass  # 普通文件
    else:
        issues.append(f"特殊文件类型: {oct(mode)}")
    
    return issues

def is_world_writable(filepath):
    """检查文件/目录是否世界可写"""
    mode = os.stat(filepath).st_mode
    return bool(mode & stat.S_IWOTH)

# 扫描目录中的危险权限文件
def scan_permissions(directory):
    """扫描目录中的权限问题"""
    findings = []
    for root, dirs, files in os.walk(directory):
        for name in files + dirs:
            path = os.path.join(root, name)
            issues = check_file_permissions(path)
            if issues:
                findings.append((path, issues))
    return findings
```

### 4.3 环境变量安全

```python
import os

def sanitize_env():
    """清理不安全的环境变量"""
    # 移除危险的环境变量
    dangerous_vars = [
        'LD_PRELOAD',
        'LD_LIBRARY_PATH',
        'PYTHONPATH',
        'PYTHONHOME',
        'PERL5LIB',
        'RUBYLIB',
    ]
    
    for var in dangerous_vars:
        if var in os.environ:
            del os.environ[var]
    
    # 限制 PATH
    safe_path = '/usr/local/bin:/usr/bin:/bin'
    os.environ['PATH'] = safe_path
    
    # 设置安全的 umask
    os.umask(0o022)  # 新文件默认权限 644
```

### 4.4 临时文件安全

```python
import os
import tempfile

# 安全创建临时文件
with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
    f.write('sensitive data')
    f.flush()
    # 文件在 with 块结束后自动删除

# 安全创建临时目录
with tempfile.TemporaryDirectory() as tmpdir:
    print(f"临时目录: {tmpdir}")
    # 目录在 with 结束后自动删除

# 不安全的做法（有竞态条件）
# os.mknod('/tmp/mytempfile')  # 可能被符号链接攻击

# 安全的临时文件
fd, path = tempfile.mkstemp()  # 返回文件描述符和路径
try:
    with os.fdopen(fd, 'w') as f:
        f.write('data')
finally:
    os.unlink(path)
```

---

## 五、异常处理

```python
# 常见异常
try:
    os.remove('nonexistent.txt')
except FileNotFoundError:
    print("文件不存在")
except PermissionError:
    print("权限不足")
except IsADirectoryError:
    print("是目录，不是文件")
except OSError as e:
    print(f"OS 错误: {e}")
    print(f"错误码: {e.errno}")
    print(f"错误信息: {e.strerror}")
    print(f"文件名: {e.filename}")
```

---

## 六、跨平台注意事项

| 功能 | Unix/Linux | Windows | 跨平台 |
|------|-----------|---------|--------|
| 路径分隔符 | `/` | `\` | `os.sep` |
| 行结束符 | `\n` | `\r\n` | `os.linesep` |
| 环境变量分隔 | `:` | `;` | `os.pathsep` |
| 当前目录 | `.` | `.` | `os.curdir` |
| 上级目录 | `..` | `..` | `os.pardir` |
| 空设备 | `/dev/null` | `nul` | `os.devnull` |
| fork() | ✅ | ❌ | - |
| chown/chmod | ✅ | 部分 | - |
| symlink | ✅ | 部分 | - |
