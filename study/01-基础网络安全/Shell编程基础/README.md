# Shell编程基础

> 本文档整理自：`Shell编程基础.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 第一章：Shell 概述](./02_第一章：Shell 概述/第一章：Shell 概述.md)
  - 什么是 Shell
  - 常见的 Shell 类型
  - 第一个 Shell 脚本
  - Shell 脚本的执行过程
  - 退出状态码

### [03. 第二章：Shell 基础语法](./03_第二章：Shell 基础语法/第二章：Shell 基础语法.md)
  - 注释
  - echo 命令
  - read 命令（读取用户输入）
  - 命令替换
  - 算术运算

### [04. 第三章：变量与数据类型](./04_第三章：变量与数据类型/第三章：变量与数据类型.md)
  - 变量定义
  - 变量命名规则
  - 变量类型
  - 特殊变量
  - 环境变量
  - 变量的高级用法

### [05. 第四章：条件判断与分支](./05_第四章：条件判断与分支/第四章：条件判断与分支.md)
  - if 语句
  - 条件测试
  - 逻辑运算
  - (( )) 双括号语法
  - [[ ]] 双方括号语法
  - case 语句

### [06. 第五章：循环结构](./06_第五章：循环结构/第五章：循环结构.md)
  - for 循环
  - while 循环
  - until 循环
  - 循环控制
  - select 循环

### [07. 第六章：函数](./07_第六章：函数/第六章：函数.md)
  - 函数定义
  - 函数调用与参数
  - 函数返回值
  - 局部变量
  - 递归函数
  - 函数库

### [08. 第七章：数组](./08_第七章：数组/第七章：数组.md)
  - 数组定义
  - 访问数组元素
  - 数组操作
  - 关联数组

### [09. 第八章：字符串处理](./09_第八章：字符串处理/第八章：字符串处理.md)
  - 字符串基本操作
  - 字符串截取
  - 字符串替换
  - 字符串大小写转换
  - 字符串判断
  - 字符串与 awk/sed 配合

### [10. 第九章：文件与目录操作](./10_第九章：文件与目录操作/第九章：文件与目录操作.md)
  - 文件读写
  - 文件属性判断
  - 目录遍历
  - 文件描述符与重定向
  - 文件权限操作

### [11. 第十章：正则表达式](./11_第十章：正则表达式/第十章：正则表达式.md)
  - 正则基础
  - grep 与正则
  - sed 与正则
  - awk 与正则

### [12. 第十一章：信号与陷阱](./12_第十一章：信号与陷阱/第十一章：信号与陷阱.md)
  - 常见信号
  - trap 命令

### [13. 第十二章：Shell 调试与最佳实践](./13_第十二章：Shell 调试与最佳实践/第十二章：Shell 调试与最佳实践.md)
  - Shell 调试
  - 错误处理
  - 最佳实践
  - 常用脚本模板

### [14. 附录：代码示例索引](./14_附录：代码示例索引/附录：代码示例索引.md)

---

## 📊 内容审核总览

- 总章节数：14
- 待完善章节：14

### 各章节审核状态
- **目录**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **第一章：Shell 概述**：⚠️ 需补充 5 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **第二章：Shell 基础语法**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **第三章：变量与数据类型**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **第四章：条件判断与分支**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **第五章：循环结构**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **第六章：函数**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **第七章：数组**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **第八章：字符串处理**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **第九章：文件与目录操作**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **第十章：正则表达式**：⚠️ 需补充 4 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **第十一章：信号与陷阱**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **第十二章：Shell 调试与最佳实践**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **附录：代码示例索引**：⚠️ 需补充 3 项
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
