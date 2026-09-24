# Select-String

> **分类**：文本处理
> **说明**：在字符串和文件中查找文本（类似 grep）

---

## 语法

```powershell
Select-String [-Pattern] <string[]> [-Path] <string[]>
```

## 别名

sls

## 常用参数

-Pattern 正则模式 / -Path 文件路径 / -CaseSensitive 区分大小写 / -NotMatch 反向匹配 / -Context 显示上下文 / -AllMatches 显示所有匹配

## 示例代码

```powershell
# 基本用法：在文件中查找
Select-String -Path "*.txt" -Pattern "error"
Select-String -Path "*.log" -Pattern "error|warning"

# 管道输入
Get-Content logfile.txt | Select-String "ERROR"
Get-ChildItem -Recurse *.txt | Select-String "TODO"

# 递归搜索
Get-ChildItem -Recurse -File | Select-String -Pattern "password"

# 区分大小写
Select-String -Path file.txt -Pattern "Error" -CaseSensitive

# 反向匹配（不包含的行）
Select-String -Path log.txt -Pattern "debug" -NotMatch

# 显示上下文
Select-String -Path log.txt -Pattern "error" -Context 2,3  # 前2后3

# 只显示匹配的文件名
Select-String -Path *.txt -Pattern "keyword" | Select-Object -Unique Path

# 统计匹配数量
(Select-String -Path log.txt -Pattern "ERROR").Count

# 提取匹配内容
Select-String -Path file.txt -Pattern "\d{3}-\d{4}" |
    ForEach-Object { $_.Matches.Value }

# 正则捕获组
$result = Select-String -Path data.txt -Pattern "Name: (\w+), Age: (\d+)"
$result | ForEach-Object {
    $name = $_.Matches.Groups[1].Value
    $age = $_.Matches.Groups[2].Value
    Write-Host "$name is $age years old"
}
```
