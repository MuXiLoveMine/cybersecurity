# with

> **分类**：上下文管理器
> **说明**：上下文管理器，自动管理资源的获取和释放

---

## 语法

```c
with 表达式 [as 变量]:\n    代码块
```

## 常见用途

- 文件操作：自动关闭文件
- 网络连接：自动关闭连接
- 锁：自动获取和释放
- 数据库事务：自动提交/回滚
- 临时文件：自动删除
- 异常处理的简化形式

## 示例代码

```python
# 文件操作（自动关闭）
with open("file.txt", "r") as f:
    content = f.read()
# 离开 with 块时，文件自动关闭

# 多个上下文管理器
with open("input.txt") as fin, open("output.txt", "w") as fout:
    for line in fin:
        fout.write(line.upper())

# 锁
import threading
lock = threading.Lock()
with lock:
    # 临界区代码
    pass  # 自动释放锁

# 数据库事务（伪代码）
with db_connection() as conn:
    conn.execute(...)
    # 正常则自动 commit
    # 异常则自动 rollback

# 自定义上下文管理器（基于类）
class Timer:
    def __enter__(self):
        import time
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.elapsed = time.time() - self.start
        print(f"耗时: {self.elapsed:.4f}秒")
        return False  # True 表示吞掉异常

with Timer() as t:
    # 你的代码
    pass

# 使用 contextlib
from contextlib import contextmanager

@contextmanager
def tag(name):
    print(f"<{name}>")
    yield
    print(f"</{name}>")

with tag("div"):
    print("Hello")
# 输出:
# <div>
# Hello
# </div>
```
