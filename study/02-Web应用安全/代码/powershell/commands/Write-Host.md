# Write-Host

> **分类**：输出
> **说明**：将输出写入控制台

---

## 语法

```powershell
Write-Host [[-Object] <Object>] [-ForegroundColor <ConsoleColor>] [-BackgroundColor <ConsoleColor>] [-NoNewline]
```

## 相关命令

Write-Output / Write-Error / Write-Warning / Write-Verbose / Write-Debug / Write-Information

## 区别

Write-Host 直接输出到主机，不进入管道\nWrite-Output 输出到管道，可以被后续命令接收

## 示例代码

```powershell
# 基本输出
Write-Host "Hello, World!"

# 带颜色
Write-Host "错误信息" -ForegroundColor Red
Write-Host "成功信息" -ForegroundColor Green
Write-Host "警告" -ForegroundColor Yellow -BackgroundColor Black

# 不换行
Write-Host "正在处理..." -NoNewline
Write-Host "完成" -ForegroundColor Green

# 变量输出
$name = "Alice"
Write-Host "你好, $name!"

# 其他输出流
Write-Output "这会进入管道"
Write-Error "错误信息"
Write-Warning "警告信息"
Write-Verbose "详细信息" -Verbose
Write-Debug "调试信息" -Debug

# 格式化输出
Get-Process | Format-Table -AutoSize
Get-Service | Format-List
```
