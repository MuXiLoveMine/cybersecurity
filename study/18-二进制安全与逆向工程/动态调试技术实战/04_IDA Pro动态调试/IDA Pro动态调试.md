# IDA Pro动态调试

IDA Pro 不仅支持静态分析，还内置了强大的动态调试器，支持多平台调试。

**调试器配置**：

```
1. Debugger → Select debugger
2. 选择目标平台：
   - Local Windows debugger     本地Windows调试
   - Local Linux debugger       本地Linux调试
   - Remote GDB debugger        远程GDB调试
   - Remote Win32 user-mode    IDA win32_server远程调试
3. Debugger → Process options  设置可执行文件路径和参数
4. F9 启动调试
```

**远程调试**：IDA 提供 `win32_server.exe`（Windows）和 `linux_server`（Linux）作为远程调试服务端。

```
# 目标机器上启动调试服务端
linux_server                  # 默认端口23946
win32_server.exe -Ppassword   # 带密码保护

# IDA端配置：
# Debugger → Select debugger → Remote GDB debugger
# Debugger → Process options → Hostname: 目标IP, Port: 23946
```

**Android/iOS 调试**：

```
Android:
  1. adb push android_server /data/local/tmp/
  2. adb shell "chmod +x /data/local/tmp/android_server"
  3. adb forward tcp:23946 tcp:23946
  4. /data/local/tmp/android_server
  5. IDA: Remote GDB debugger → localhost:23946

iOS:
  1. 使用debugserver（越狱设备通过Cydia安装）
  2. debugserver *:1234 -a com.target.app
  3. IDA: Remote GDB debugger → 设备IP:1234
```

**IDAPython 调试脚本**：

```python
import idaapi
import ida_dbg

# 设置断点
ida_dbg.add_bpt(0x401234)

# 启动调试
ida_dbg.start_process()

# 运行到断点
ida_dbg.continue_process()

# 获取寄存器
eip = idaapi.regval_t()
ida_dbg.get_reg_val("EIP", eip)
print(f"Stopped at EIP: {eip.ival:#x}")

# 读取内存
data = idaapi.dbg_read_memory(0x601040, 16)
print(f"Memory: {data.hex()}")

# 修改寄存器后继续
ida_dbg.set_reg_val("EAX", idaapi.regval_t(0x1234))
ida_dbg.continue_process()
```

---

---

