# Get-ChildItem

> **分类**：文件系统
> **说明**：获取目录中的项（类似 dir/ls）

---

## 语法

```powershell
Get-ChildItem [[-Path] <string[]>] [-Filter <string>] [-Recurse] [-File] [-Directory]
```

## 别名

dir / ls / gci

## 常用参数

-Recurse 递归 / -File 仅文件 / -Directory 仅目录 / -Filter 过滤 / -Include 包含 / -Exclude 排除 / -Force 显示隐藏

## 示例代码

```powershell
# 基本用法
Get-ChildItem
Get-ChildItem C:\Users
Get-ChildItem -Path $HOME

# 递归查找
Get-ChildItem -Recurse -Filter "*.txt"
Get-ChildItem -Path C:\ -Recurse -Filter "*.log" -ErrorAction SilentlyContinue

# 仅文件或仅目录
Get-ChildItem -File
Get-ChildItem -Directory
Get-ChildItem -Recurse -File -Filter "*.ps1"

# 显示隐藏文件
Get-ChildItem -Force

# 排序
Get-ChildItem | Sort-Object Length -Descending  # 按大小降序
Get-ChildItem | Sort-Object LastWriteTime       # 按修改时间
Get-ChildItem | Sort-Object Name                # 按名称

# 选择字段
Get-ChildItem | Select-Object Name, Length, LastWriteTime
Get-ChildItem | Format-Table Name, @{N="Size(KB)";E={[math]::Round($_.Length/1KB,2)}}

# 统计文件数量和大小
$files = Get-ChildItem -Recurse -File
$files.Count
($files | Measure-Object Length -Sum).Sum / 1MB

# 管道操作：批量重命名
Get-ChildItem *.txt | Rename-Item -NewName { $_.Name -replace '\.txt$','.bak' }

# 查找大文件
Get-ChildItem -Path C:\ -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -gt 100MB } |
    Sort-Object Length -Descending |
    Select-Object -First 10 FullName, @{N="Size(MB)";E={[math]::Round($_.Length/1MB,2)}}

# 查找最近修改的文件
Get-ChildItem -Path $HOME -Recurse -File |
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) } |
    Sort-Object LastWriteTime -Descending
```
