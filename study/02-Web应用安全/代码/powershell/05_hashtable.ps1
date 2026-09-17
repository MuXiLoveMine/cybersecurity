# ============================================================
# 05_hashtable.ps1 - 哈希表创建、增删改查、遍历、有序字典
# 运行方式: powershell -ExecutionPolicy Bypass -File .\05_hashtable.ps1
# ============================================================

Write-Host "=============================="
Write-Host "  1. 创建哈希表"
Write-Host "=============================="

# 基本语法
$person = @{
    Name = "张三"
    Age = 25
    City = "北京"
    Email = "zhangsan@example.com"
}

Write-Host "哈希表内容:"
$person

# 空哈希表
$empty = @{}
Write-Host "空哈希表元素数: $($empty.Count)"

# 单行创建
$fruit = @{ Apple = "苹果"; Banana = "香蕉"; Orange = "橙子" }
Write-Host "单行创建的哈希表:"
$fruit

Write-Host ""
Write-Host "=============================="
Write-Host "  2. 访问哈希表元素"
Write-Host "=============================="

$student = @{
    Id = 1001
    Name = "李四"
    Age = 20
    Grade = "大二"
    Major = "计算机科学"
}

# 方式一：索引方式
Write-Host "姓名 (索引): $($student['Name'])"
Write-Host "年龄 (索引): $($student['Age'])"

# 方式二：属性方式
Write-Host "姓名 (属性): $($student.Name)"
Write-Host "专业 (属性): $($student.Major)"

# 键集合和值集合
Write-Host ""
Write-Host "所有键: $($student.Keys -join ', ')"
Write-Host "所有值: $($student.Values -join ', ')"
Write-Host "元素数量: $($student.Count)"

Write-Host ""
Write-Host "=============================="
Write-Host "  3. 添加和修改元素"
Write-Host "=============================="

$car = @{
    Brand = "Tesla"
    Model = "Model 3"
    Year = 2023
}

Write-Host "初始哈希表:"
$car

# 添加元素（索引方式）
$car['Color'] = "白色"
Write-Host "`n添加 Color 后:"
$car

# 添加元素（Add 方法）
$car.Add("Price", 250000)
Write-Host "`n添加 Price 后:"
$car

# 修改元素
$car['Year'] = 2024
Write-Host "`n修改 Year 为 2024 后:"
$car

$car.Model = "Model Y"
Write-Host "`n修改 Model 为 Model Y 后:"
$car

Write-Host ""
Write-Host "=============================="
Write-Host "  4. 删除元素"
Write-Host "=============================="

$config = @{
    Server = "localhost"
    Port = 3306
    Database = "test"
    Username = "root"
    Password = "123456"
    Timeout = 30
}

Write-Host "删除前:"
$config.Keys -join ", "

# 删除指定键
$config.Remove("Password")
Write-Host "`n删除 Password 后:"
$config.Keys -join ", "

# 删除不存在的键不会报错
$config.Remove("NotExist")
Write-Host "删除不存在的键不会报错"

# 清空哈希表
$config.Clear()
Write-Host "`n清空后元素数: $($config.Count)"

Write-Host ""
Write-Host "=============================="
Write-Host "  5. 判断键/值是否存在"
Write-Host "=============================="

$user = @{
    Username = "admin"
    Password = "admin123"
    Role = "Administrator"
    Active = $true
}

Write-Host "哈希表: $($user.Keys -join ', ')"

# ContainsKey
Write-Host "包含键 'Username' 吗? $($user.ContainsKey('Username'))"
Write-Host "包含键 'Email' 吗? $($user.ContainsKey('Email'))"

# ContainsValue
Write-Host "包含值 'admin' 吗? $($user.ContainsValue('admin'))"
Write-Host "包含值 'guest' 吗? $($user.ContainsValue('guest'))"

# 安全访问（不存在的键返回 $null）
$value = $user['NotExist']
Write-Host "访问不存在的键返回: $value (是否为 null: $($null -eq $value))"

Write-Host ""
Write-Host "=============================="
Write-Host "  6. 遍历哈希表"
Write-Host "=============================="

$countries = @{
    China = "中国"
    USA = "美国"
    Japan = "日本"
    UK = "英国"
    France = "法国"
}

# 方式一：遍历键
Write-Host "遍历键:"
foreach ($key in $countries.Keys) {
    Write-Host "  $key -> $($countries[$key])"
}

# 方式二：遍历枚举器
Write-Host "`n遍历 GetEnumerator():"
foreach ($item in $countries.GetEnumerator()) {
    Write-Host "  $($item.Key) : $($item.Value)"
}

# 方式三：管道遍历
Write-Host "`n管道遍历:"
$countries.GetEnumerator() | ForEach-Object {
    Write-Host "  $($_.Key) = $($_.Value)"
}

# 方式四：按键排序遍历
Write-Host "`n按键排序遍历:"
$countries.GetEnumerator() | Sort-Object Key | ForEach-Object {
    Write-Host "  $($_.Key) : $($_.Value)"
}

Write-Host ""
Write-Host "=============================="
Write-Host "  7. 嵌套哈希表"
Write-Host "=============================="

$employee = @{
    Id = 1001
    Name = "王五"
    Department = "技术部"
    Contact = @{
        Email = "wangwu@company.com"
        Phone = "13800138000"
        Address = @{
            City = "上海"
            District = "浦东新区"
            Street = "某某路 123 号"
        }
    }
    Skills = @("C#", "Python", "PowerShell")
}

Write-Host "员工信息:"
Write-Host "  姓名: $($employee.Name)"
Write-Host "  部门: $($employee.Department)"
Write-Host "  邮箱: $($employee.Contact.Email)"
Write-Host "  电话: $($employee.Contact.Phone)"
Write-Host "  城市: $($employee.Contact.Address.City)"
Write-Host "  区: $($employee.Contact.Address.District)"
Write-Host "  技能: $($employee.Skills -join ', ')"

# 修改嵌套哈希表
$employee.Contact.Email = "wangwu_new@company.com"
Write-Host "`n修改邮箱后: $($employee.Contact.Email)"

# 添加嵌套属性
$employee.Contact.Wechat = "wangwu_wx"
Write-Host "添加微信后: $($employee.Contact.Wechat)"

Write-Host ""
Write-Host "=============================="
Write-Host "  8. 有序字典"
Write-Host "=============================="

# 普通哈希表不保证顺序
$unordered = @{
    First = 1
    Second = 2
    Third = 3
    Fourth = 4
}

Write-Host "普通哈希表（顺序不保证）:"
$unordered.Keys -join " -> "

# 有序字典（[ordered] 属性）
$ordered = [ordered]@{
    First = 1
    Second = 2
    Third = 3
    Fourth = 4
}

Write-Host "`n有序字典（保持插入顺序）:"
$ordered.Keys -join " -> "

# 有序字典可以按索引访问
Write-Host "索引 0 的值: $($ordered[0])"
Write-Host "索引 2 的值: $($ordered[2])"

# 有序字典的类型
Write-Host "有序字典类型: $($ordered.GetType().Name)"

Write-Host ""
Write-Host "=============================="
Write-Host "  9. 计算属性与 Splatting"
Write-Host "=============================="

# Splatting：用哈希表传递参数
$params = @{
    Path = $env:TEMP
    Filter = "*.tmp"
    Recurse = $false
    File = $true
}

Write-Host "Splatting 参数:"
$params

Write-Host "`n使用 Get-ChildItem @params (可能返回 0 个文件，属正常)"
$result = Get-ChildItem @params -ErrorAction SilentlyContinue
Write-Host "找到 $($result.Count) 个 .tmp 文件"

# 哈希表转自定义对象
$userObj = [pscustomobject]@{
    Id = 1
    Name = "赵六"
    Age = 28
    Email = "zhaoliu@example.com"
}

Write-Host "`nPSCustomObject:"
$userObj | Format-Table

Write-Host ""
Write-Host "=============================="
Write-Host "  10. 哈希表操作技巧"
Write-Host "=============================="

# 合并两个哈希表
$ht1 = @{ A = 1; B = 2; C = 3 }
$ht2 = @{ C = 30; D = 4; E = 5 }

$merged = @{}
$ht1.Keys | ForEach-Object { $merged[$_] = $ht1[$_] }
$ht2.Keys | ForEach-Object { $merged[$_] = $ht2[$_] }  # 后者覆盖前者

Write-Host "哈希表 1: A=$($ht1.A), B=$($ht1.B), C=$($ht1.C)"
Write-Host "哈希表 2: C=$($ht2.C), D=$($ht2.D), E=$($ht2.E)"
Write-Host "合并后: A=$($merged.A), B=$($merged.B), C=$($merged.C), D=$($merged.D), E=$($merged.E)"

# 浅拷贝
$original = @{ X = 10; Y = 20 }
$copy = $original.Clone()
$copy.X = 99
Write-Host "`n浅拷贝验证:"
Write-Host "  原始 X: $($original.X)"
Write-Host "  副本 X: $($copy.X)"

# 筛选哈希表
$allData = @{
    Name = "测试"
    Age = 30
    Password = "secret"
    Token = "abc123"
    City = "北京"
}

$safeKeys = @("Name", "Age", "City")
$safeData = @{}
foreach ($key in $safeKeys) {
    if ($allData.ContainsKey($key)) {
        $safeData[$key] = $allData[$key]
    }
}

Write-Host "`n筛选后的安全数据:"
$safeData

Write-Host ""
Write-Host "脚本执行完毕！"
