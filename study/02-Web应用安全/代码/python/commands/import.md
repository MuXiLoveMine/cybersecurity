# import

> **分类**：模块导入
> **说明**：导入模块或模块中的函数/类

---

## 语法

```c
import module\nfrom module import name\nfrom module import *
```

## 导入形式

- import module - 导入整个模块
- import module as alias - 导入并重命名
- from module import name - 导入指定名称
- from module import name as alias - 导入并重命名
- from module import * - 导入所有（不推荐）

## 示例代码

```python
# 导入整个模块
import math
print(math.sqrt(16))  # 4.0

# 导入并重命名
import numpy as np
arr = np.array([1, 2, 3])

# 导入指定函数
from os.path import exists, join
print(exists("file.txt"))
print(join("/a", "b"))  # "/a/b"

# 导入所有（不推荐，可能命名冲突）
from math import *
print(sqrt(16))

# 标准库常用模块
import os           # 操作系统接口
import sys          # 系统相关
import re           # 正则表达式
import json         # JSON 处理
import time         # 时间相关
import datetime     # 日期时间
import random       # 随机数
import collections  # 高级容器
import itertools    # 迭代工具
import subprocess   # 子进程
import threading    # 多线程
import multiprocessing  # 多进程

# 相对导入（包内使用）
# from . import module
# from .. import module
# from .module import function

# 动态导入
import importlib
module_name = "json"
json = importlib.import_module(module_name)
```
