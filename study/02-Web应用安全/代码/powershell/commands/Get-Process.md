# Get-Process

> **分类**：系统管理
> **说明**：获取正在运行的进程

---

## 语法

```powershell
Get-Process [[-Name] <string[]>] [-Id <int[]>]
```

## 别名

ps / gps

## 相关命令

Start-Process / Stop-Process / Wait-Process

## 示例代码

```powershell
# 获取所有进程
Get-Process

# 按名称查找
Get-Process notepad
Get-Process -Name chrome, firefox

# 按ID查找
Get-Process -Id 1234

# 显示详细信息
Get-Process | Select-Object Id, ProcessName, CPU, WorkingSet, StartTime
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10

# 内存使用排行
Get-Process |
    Sort-Object WorkingSet64 -Descending |
    Select-Object -First 10 Name, Id,
        @{N="Memory(MB)";E={[math]::Round($_.WorkingSet64/1MB,2)}} |
    Format-Table -AutoSize

# 停止进程
Stop-Process -Name notepad
Stop-Process -Id 1234 -Force
Get-Process notepad | Stop-Process

# 启动进程
Start-Process notepad.exe
Start-Process "https://example.com"  # 打开浏览器
Start-Process powershell -Verb runAs  # 以管理员身份运行

# 等待进程结束
Wait-Process -Name notepad
Write-Host "记事本已关闭"

# 查看进程模块/DLL
Get-Process notepad | Select-Object -ExpandProperty Modules

# 获取进程的所有者
Get-WmiObject Win32_Process -Filter "name='notepad.exe'" |
    ForEach-Object { $_.GetOwner().User }
```
