# Linux 核心命令、参数与案例详解

> 本文按功能分类介绍 Linux 核心命令的语法、参数与调用案例。Linux 命令数量庞大，本文聚焦**核心命令 + 功能分类 + 代表性案例**，不求全但求精。面向系统管理员、运维工程师和安全工程师，深度覆盖操作参考 + 案例实战 + 安全加固。示例覆盖 Ubuntu/Debian、CentOS/RHEL、Arch 等主流发行版。

---

## 目录

- [一、文件与目录](#一文件与目录)
- [二、文本处理](#二文本处理)
- [三、查找与搜索](#三查找与搜索)
- [四、进程与作业控制](#四进程与作业控制)
- [五、用户与权限](#五用户与权限)
- [六、网络](#六网络)
- [七、磁盘与文件系统](#七磁盘与文件系统)
- [八、压缩与归档](#八压缩与归档)
- [九、包管理](#九包管理)
- [十、系统监控与日志](#十系统监控与日志)
- [十一、服务与 systemd](#十一服务与-systemd)
- [十二、开发与调试](#十二开发与调试)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、文件与目录

### 1.1 命令速查表

| 命令 | 全称/用途 | 风险等级 |
|------|----------|---------|
| **ls** | list — 列出目录内容 | ★☆☆☆☆ |
| **cd** | change directory — 切换目录 | ★☆☆☆☆ |
| **pwd** | print working directory — 显示当前路径 | ★☆☆☆☆ |
| **mkdir** | make directory — 创建目录 | ★☆☆☆☆ |
| **rmdir** | remove directory — 删除空目录 | ★☆☆☆☆ |
| **cp** | copy — 复制文件/目录 | ★★☆☆☆ |
| **mv** | move — 移动/重命名 | ★★☆☆☆ |
| **rm** | remove — 删除文件/目录 | ★★★★★ |
| **touch** | touch — 创建空文件/修改时间戳 | ★☆☆☆☆ |
| **ln** | link — 创建链接 | ★★☆☆☆ |
| **stat** | status — 文件/文件系统详细信息 | ★☆☆☆☆ |
| **file** | file type — 识别文件类型 | ★☆☆☆☆ |
| **tree** | tree — 树形显示目录结构 | ★☆☆☆☆ |

### 1.2 ls — 列出目录

```
语法：ls [选项] [路径...]

核心参数：
  -l      长格式（详细信息：权限/所有者/大小/时间）
  -a      显示隐藏文件（以 . 开头的）
  -A      显示隐藏文件，但不含 . 和 ..
  -h      人类可读大小（K/M/G）
  -H      跟 -l 一起用，1000 进制（--si）
  -i      显示 inode 号
  -R      递归列出子目录
  -t      按修改时间排序（最新在前）
  -S      按大小排序（最大在前）
  -r      反向排序
  -F      在文件名后加类型标记（/目录 *可执行 @链接）
  -d      只列目录本身，不列内容
  -n      显示 UID/GID 数字而非名称
  -Z      显示 SELinux 安全上下文
```

```bash
# 基本用法
ls
ls /etc

# 详细列表 + 隐藏文件 + 人类可读
ls -lah

# 显示 inode 号
ls -li

# 按时间排序（最新在最后，方便翻）
ls -ltr

# 按大小排序，取前 10 大
ls -lhS | head -11

# 只列目录
ls -d /etc/*/
ls -l /etc | grep ^d

# 递归列出
ls -R /etc/ssh

# 显示 SELinux 上下文
ls -Z /var/www/
```

### 1.3 cd / pwd

```bash
# 切换到指定目录
cd /etc
cd /var/log

# 回到用户主目录
cd
cd ~

# 回到上一级目录
cd ..

# 回到上上级
cd ../..

# 回到上次所在目录
cd -

# 切换到 root 主目录
cd /root

# 显示当前路径
pwd

# 显示物理路径（解析符号链接后的真实路径）
pwd -P
```

### 1.4 mkdir / rmdir

```bash
# 创建单个目录
mkdir mydir

# 创建多级目录（父目录不存在则自动创建）
mkdir -p a/b/c/d

# 创建时指定权限
mkdir -m 700 privatedir

# 同时创建多个目录
mkdir dir1 dir2 dir3

# 删除空目录
rmdir emptydir

# 删除多级空目录（从里往外删，都空才成功）
rmdir -p a/b/c/d

# 注意：rmdir 只能删除空目录
# 删除非空目录用 rm -r（危险！见 rm 命令）
```

### 1.5 cp — 复制

```
语法：cp [选项] 源 目标
      cp [选项] 源... 目录

核心参数：
  -r/-R   递归复制目录
  -a      归档模式（= -dR --preserve=all），保留权限/时间戳/所有者/链接
  -p      保留权限、所有者、时间戳
  -d      复制符号链接本身（不跟随）
  -i      交互模式（覆盖前提示）
  -f      强制复制（不提示）
  -n      不覆盖已存在的文件
  -u      只在源文件更新时复制
  -v      显示复制过程
  -l      创建硬链接而非复制
  -s      创建符号链接而非复制
```

```bash
# 复制单个文件
cp source.txt dest.txt

# 复制到目录
cp file.txt /tmp/

# 递归复制目录
cp -r sourcedir destdir

# 归档复制（保留所有属性，备份用）
cp -a /data /backup/

# 只复制更新的文件（增量）
cp -u /src/* /dst/

# 不覆盖已有文件
cp -n src.txt dst.txt

# 交互式复制（覆盖前确认）
cp -i src.txt dst.txt
```

### 1.6 mv — 移动/重命名

```
语法：mv [选项] 源 目标
      mv [选项] 源... 目录

核心参数：
  -i      交互模式（覆盖前提示）
  -f      强制（不提示）
  -n      不覆盖已存在
  -u      只在源文件更新时移动
  -v      显示过程
  -b      覆盖前备份目标文件
```

```bash
# 重命名文件
mv oldname.txt newname.txt

# 移动文件到目录
mv file.txt /tmp/

# 移动多个文件到目录
mv file1.txt file2.txt /tmp/

# 移动整个目录
mv /old/path /new/path

# 覆盖前备份
mv -b old new

# 不覆盖
mv -n src dst
```

### 1.7 rm — 删除 ⚠️

```
语法：rm [选项] 文件...

核心参数：
  -r/-R   递归删除（目录及其所有内容）
  -f      强制删除（不提示，忽略不存在的文件）
  -i      交互模式（每次删除前确认）
  -I      删 3 个以上或递归时提示一次（比 -i 温和）
  -v      显示删除过程
  -d      删除空目录（同 rmdir）
  --one-file-system  递归时不跨文件系统
```

```bash
# 删除单个文件
rm file.txt

# 交互删除（每次确认）
rm -i file.txt

# 强制删除
rm -f file.txt

# 递归删除目录及其所有内容 ⚠️ 极高风险
rm -rf /path/to/dir

# 批量删除匹配的文件
rm *.log
rm file*.txt

# 更安全的删除（删 3 个以上提示一次）
rm -I *.log

# 按文件列表删除
find . -name "*.tmp" -exec rm {} \;
# 或更安全的方式（先确认再删）
find . -name "*.tmp" | head -20
```

> ⚠️ **最高风险警告**：
> - `rm -rf /` 会删除整个系统！永远不要执行。
> - `rm -rf /path/*` 路径写错会误删重要数据。建议先用 `ls /path/*` 确认。
> - 生产环境建议安装 `trash-cli` 替代 rm（相当于回收站）。
> - 别名保护：`alias rm='rm -I'` 或 `alias rm='trash'`

### 1.8 touch — 创建文件/改时间

```
语法：touch [选项] 文件...

核心参数：
  -a      只改访问时间（atime）
  -m      只改修改时间（mtime）
  -d "时间"  指定时间（如 "2024-01-01 12:00"）
  -t [[CC]YY]MMDDhhmm[.ss]  用 [[CC]YY]MMDDhhmm[.ss] 格式指定时间
  -r 文件   参考指定文件的时间
  -c      文件不存在时不创建
```

```bash
# 创建空文件
touch newfile.txt

# 同时创建多个文件
touch a.txt b.txt c.txt

# 修改访问时间
touch -a file.txt

# 修改修改时间为指定时间
touch -d "2024-01-01 12:00:00" file.txt
touch -t 202401011200.00 file.txt

# 以另一个文件的时间为参考
touch -r ref.txt target.txt

# 只改时间，不创建不存在的文件
touch -c nonexistent.txt
```

### 1.9 ln — 链接

```
语法：ln [选项] 源 [目标名]

核心参数：
  -s      创建符号链接（软链接）
  -f      强制（目标已存在则覆盖）
  -i      交互模式
  -n      把目录的符号链接当作普通文件处理
  -v      显示过程
  -b      覆盖前备份
```

```bash
# 创建硬链接（同文件系统内，inode 相同）
ln /path/to/source.txt /path/to/hardlink.txt

# 创建符号链接（软链接，可跨文件系统）
ln -s /path/to/source.txt /path/to/symlink.txt

# 相对路径软链接（源路径相对于链接所在目录）
ln -s ../source.txt subdir/symlink.txt

# 强制覆盖已存在的链接
ln -sf /new/source.txt symlink.txt

# 查看 inode 验证硬链接
ls -li source.txt hardlink.txt
```

### 1.10 stat / file / tree

```bash
# ===== stat：文件详细信息 =====

# 查看文件元数据
stat filename

# 只看指定字段（自定义格式）
stat -c "%n %a %s %y" filename
# %n 文件名  %a 八进制权限  %s 大小  %y 修改时间

# 查看文件系统信息（不是单个文件）
stat -f /
stat -f /dev/sda1

# ===== file：识别文件类型 =====

# 基本识别
file filename

# 只显示类型（不显示文件名）
file -b filename

# 显示 MIME 类型
file -i filename

# 不跟随符号链接
file -L symlink.txt

# ===== tree：树形显示目录 =====

# 基本用法
tree /etc

# 只显示目录
tree -d /etc

# 限制深度
tree -L 2 /

# 显示文件大小
tree -s -h /var

# 排除特定模式
tree -I '*.log' /var/log

# 输出到 HTML
tree -H /etc -o tree.html
```

---

## 二、文本处理

### 2.1 命令速查表

| 命令 | 用途 | 核心场景 |
|------|------|---------|
| **cat** | 拼接/显示文件内容 | 查看小文件、合并文件 |
| **less** | 分页查看（更强大） | 查看大文件、日志 |
| **more** | 分页查看（基础版） | 简单分页 |
| **head** | 显示文件头部 | 看前 N 行 |
| **tail** | 显示文件尾部 | 看后 N 行、实时跟踪日志 |
| **grep** | 文本搜索 | 查找匹配行 |
| **sed** | 流编辑器 | 替换、删除、插入文本 |
| **awk** | 文本处理语言 | 按列处理、计算、格式化 |
| **sort** | 排序 | 文本排序 |
| **uniq** | 去重/计数 | 相邻行去重（需先排序） |
| **wc** | 统计 | 行数、单词数、字符数 |
| **cut** | 切割列 | 按分隔符取指定列 |
| **tr** | 字符替换 | 字符级替换/删除 |
| **tee** | 分流输出 | 既显示又保存到文件 |

### 2.2 cat / less / head / tail

```bash
# ===== cat =====
cat file.txt
cat -n file.txt          # 显示行号
cat -b file.txt          # 显示行号（空行不计）
cat -s file.txt          # 压缩连续空行
cat -A file.txt          # 显示不可见字符（$行尾 ^I Tab）
cat file1.txt file2.txt  # 拼接两个文件

# ===== less =====
less file.txt
# 操作：
#   空格 / f   下翻一页
#   b         上翻一页
#   回车 / j  下一行
#   k         上一行
#   g         跳到开头
#   G         跳到结尾
#   /pattern  向下搜索
#   ?pattern  向上搜索
#   n         下一个匹配
#   N         上一个匹配
#   q         退出
#   F         实时跟踪（类似 tail -f）

less -N file.txt         # 显示行号
less +F /var/log/syslog  # 实时跟踪模式
less +100 file.txt       # 从第 100 行开始
less -M file.txt        # 底部显示更多信息

# ===== head =====
head file.txt                    # 默认前 10 行
head -n 20 file.txt              # 前 20 行
head -20 file.txt                # 简写
head -n -5 file.txt              # 除了最后 5 行都显示
head -c 100 file.txt             # 前 100 字节

# ===== tail =====
tail file.txt                    # 默认最后 10 行
tail -n 20 file.txt              # 最后 20 行
tail -20 file.txt                # 简写
tail -n +20 file.txt             # 从第 20 行开始到末尾
tail -f file.txt                 # 实时跟踪（文件被重命名停止）
tail -F file.txt                 # 实时跟踪（文件被重命名/截断后重试，推荐）
tail -f -n 100 file.txt          # 先显示最后 100 行，再跟踪
tail -c 100 file.txt             # 最后 100 字节
```

### 2.3 grep — 文本搜索

```
语法：grep [选项] 模式 [文件...]

核心参数：
  -i              不区分大小写
  -v              反向匹配（显示不匹配的行）
  -c              只显示匹配行数
  -n              显示行号
  -l              只显示包含匹配的文件名
  -L              只显示不包含匹配的文件名
  -r / -R         递归搜索目录
  -w              匹配整个单词
  -x              匹配整行
  -A N            显示匹配行后 N 行（After）
  -B N            显示匹配行前 N 行（Before）
  -C N            显示匹配行前后各 N 行（Context）
  -E              扩展正则（等价于 egrep）
  -P              Perl 正则（支持 \d \w 等）
  -F              固定字符串（不解析正则，快）
  -f file         从文件读取模式（每行一个）
  -o              只输出匹配的部分
  -q              静默模式（只设退出码，不输出）
  --color=auto    高亮显示匹配
```

```bash
# 基本搜索
grep "error" /var/log/syslog

# 不区分大小写
grep -i "error" /var/log/syslog

# 显示行号
grep -n "error" /var/log/syslog

# 反向匹配（显示不包含 error 的行）
grep -v "error" /var/log/syslog

# 显示匹配行前后各 3 行（上下文）
grep -C 3 "fatal" /var/log/syslog

# 递归搜索目录
grep -r "TODO" /src/
grep -r "pattern" --include="*.py" /src/   # 只搜 .py 文件
grep -r "pattern" --exclude="*.log" /src/  # 排除 .log 文件

# 匹配整个单词
grep -w "user" file.txt        # 只匹配独立的 user，不匹配 username

# 扩展正则（或关系）
grep -E "error|warning|fatal" /var/log/syslog

# 只显示匹配的部分
grep -o "[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*" access.log   # 提取 IP

# 统计匹配行数
grep -c "error" /var/log/syslog

# 管道中使用（最常见）
ps aux | grep nginx
netstat -an | grep :80
cat /etc/passwd | grep root
```

### 2.4 sed — 流编辑器

```
语法：sed [选项] '脚本' [文件...]

常用脚本语法：
  s/pattern/repl/      替换（每行第一个匹配）
  s/pattern/repl/g     全局替换（每行所有匹配）
  s/pattern/repl/N     只替换第 N 个匹配
  d                    删除
  p                    打印（通常和 -n 配合）
  N d                  删除第 N 行
  /pattern/d           删除匹配行
  N i\text             第 N 行前插入
  N a\text             第 N 行后追加
  y/abc/xyz/           字符转换（类似 tr）

核心参数：
  -n            静默模式（不默认打印每一行）
  -e '脚本'      执行脚本（多个 -e 可串联）
  -f file       从文件读取脚本
  -i            直接修改文件（危险！）
  -i.bak        修改并备份 .bak 文件
  -r            扩展正则
  -E            扩展正则（GNU sed）
```

```bash
# ===== 替换 =====

# 替换每行第一个 old 为 new
sed 's/old/new/' file.txt

# 全局替换（所有匹配）
sed 's/old/new/g' file.txt

# 替换第 3 个匹配
sed 's/old/new/3' file.txt

# 使用不同分隔符（避免转义 /）
sed 's#/usr/bin#/bin#g' file.txt

# 正则替换
sed -E 's/[0-9]+/NUMBER/g' file.txt

# ===== 删除 =====

# 删除第 5 行
sed '5d' file.txt

# 删除最后一行
sed '$d' file.txt

# 删除包含 pattern 的行
sed '/pattern/d' file.txt

# 删除空行
sed '/^$/d' file.txt

# 删除 3-7 行
sed '3,7d' file.txt

# ===== 打印（配合 -n） =====

# 只打印第 5 行
sed -n '5p' file.txt

# 打印 1-10 行
sed -n '1,10p' file.txt

# 打印匹配的行（类似 grep）
sed -n '/pattern/p' file.txt

# ===== 插入/追加 =====

# 第 3 行前插入
sed '3i\inserted text' file.txt

# 最后一行后追加
sed '$a\appended text' file.txt

# ===== 直接修改文件 ⚠️ =====

# 直接修改（备份为 .bak）
sed -i.bak 's/old/new/g' file.txt

# 直接修改（不备份，危险！）
sed -i 's/old/new/g' file.txt
```

> ⚠️ **风险提示**：`sed -i` 直接修改源文件，不可撤销。重要文件操作前先备份（用 `-i.bak` 自动备份）。

### 2.5 awk — 文本处理语言

```
语法：awk [选项] '程序' [文件...]

程序结构：
  BEGIN { 初始化 }     处理前执行一次
  /pattern/ { 动作 }   匹配行执行
  END { 收尾 }         处理完后执行一次

内建变量：
  $0        整行内容
  $1, $2...  第 1、2... 字段
  NF        字段数（Number of Fields）
  NR        行号（Number of Records）
  FNR       当前文件行号
  FS        输入字段分隔符（默认空白）
  OFS       输出字段分隔符（默认空格）
  RS        输入记录分隔符（默认换行）
  FILENAME  当前文件名

核心参数：
  -F 分隔符    指定字段分隔符
  -v var=val   定义变量
  -f file      从文件读取程序
```

```bash
# ===== 基本列操作 =====

# 打印第 1 列
awk '{print $1}' file.txt

# 打印第 1 列和第 3 列
awk '{print $1, $3}' file.txt

# 指定分隔符为冒号（取 /etc/passwd 的用户名）
awk -F: '{print $1}' /etc/passwd

# 自定义输出分隔符
awk -F: '{print $1 " -> " $7}' /etc/passwd
awk -F: -v OFS=' -> ' '{print $1, $7}' /etc/passwd

# ===== 条件筛选 =====

# 第 3 列大于 100 的行
awk '$3 > 100 {print $1, $3}' file.txt

# 包含 pattern 的行
awk '/pattern/ {print $0}' file.txt

# 第 1 列等于 "root"
awk -F: '$1 == "root" {print $0}' /etc/passwd

# ===== 计算/统计 =====

# 求和
awk '{sum += $3} END {print sum}' file.txt

# 求平均值
awk '{sum += $3; n++} END {print sum/n}' file.txt

# 统计行数（类似 wc -l）
awk 'END {print NR}' file.txt

# 找最大值
awk '$3 > max {max=$3; name=$1} END {print name, max}' file.txt

# ===== 组合示例 =====

# 访问日志：统计每个 IP 的访问次数并排序
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

# 列出所有用户的 Shell
awk -F: '{print $1 "  " $7}' /etc/passwd

# 查看进程中内存占用前 5 的
ps aux | awk 'NR>1 {print $2, $4, $11}' | sort -k2 -rn | head -5

# 查看磁盘使用（过滤大于 80% 的）
df -h | awk 'NR>1 {gsub(/%/,"",$5); if($5+0 > 80) print $6, $5"%"}'
```

### 2.6 其他文本处理命令

```bash
# ===== sort：排序 =====
sort file.txt                   # 字典序升序
sort -r file.txt                # 降序
sort -n file.txt                # 数值排序
sort -k2 file.txt               # 按第 2 列排序
sort -t: -k3 -n /etc/passwd      # 按冒号分隔的第 3 列（UID）数值排序
sort -u file.txt                # 排序并去重（唯一）
sort -k2,2 -k1,1 file.txt       # 先按第 2 列，再按第 1 列

# ===== uniq：去重 =====
# 注意：只能去除相邻的重复行，所以通常先 sort
sort file.txt | uniq            # 去重
sort file.txt | uniq -c         # 计数（每行出现次数）
sort file.txt | uniq -d         # 只显示重复的行
sort file.txt | uniq -u         # 只显示不重复的行

# ===== wc：统计 =====
wc file.txt                     # 行数 单词数 字节数
wc -l file.txt                  # 行数
wc -w file.txt                  # 单词数
wc -c file.txt                  # 字节数
wc -m file.txt                  # 字符数
wc -L file.txt                  # 最长行的长度

# ===== cut：按列切割 =====
cut -d: -f1 /etc/passwd         # 冒号分隔，取第 1 列
cut -d: -f1,7 /etc/passwd       # 取第 1 和第 7 列
cut -d: -f1-3 /etc/passwd       # 取第 1 到第 3 列
cut -c1-10 file.txt             # 取每行前 10 个字符
cut -c10- file.txt              # 从第 10 个字符到行尾

# ===== tr：字符替换 =====
echo "hello" | tr a-z A-Z       # 小写转大写
echo "Hello" | tr A-Z a-z       # 大写转小写
echo "abc123" | tr -d '0-9'     # 删除所有数字
cat file.txt | tr -d '\r'       # 删除 Windows 回车符（\r）
echo "a,,b,,,c" | tr -s ','     # 压缩连续的逗号（多个变一个）

# ===== tee：分流 =====
# 既显示在屏幕，又保存到文件
ls -la | tee output.txt
ls -la | tee -a output.txt      # 追加模式

# 多级保存
ls -la | tee file1.txt file2.txt
```

---

## 三、查找与搜索

### 3.1 find — 高级文件查找

```
语法：find [路径...] [选项] [测试条件] [操作]

常用测试条件：
  -name "pattern"     文件名匹配（通配符）
  -iname "pattern"    不区分大小写
  -type [fdlbcsp]     文件类型（f=文件 d=目录 l=链接 b=块设备 c=字符 s=套接字 p=管道）
  -size N[c/k/M/G]    文件大小（+大于 -小于 无符号=等于）
  -mtime N            修改时间（天），-7=7天内，+7=超过7天
  -mmin N             修改时间（分钟）
  -atime N            访问时间（天）
  -ctime N            元数据变更时间（天）
  -newer file         比指定文件更新
  -user username      所有者
  -group groupname    所属组
  -uid N              UID
  -perm mode          权限精确匹配
  -perm -mode         至少有这些权限位（位与）
  -perm /mode         有任意一位即可（位或）
  -maxdepth N         最大深度
  -mindepth N         最小深度
  -empty              空文件或空目录
  -path "pattern"     路径匹配
  -name "pattern"     文件名匹配
  -regex "pattern"    正则匹配（匹配完整路径）
  -xdev               不跨文件系统

常用操作：
  -print              打印（默认）
  -ls                 类似 ls -l 的详细输出
  -delete             删除（危险！）
  -exec cmd {} \;     对每个文件执行命令，{} 代表文件名
  -ok cmd {} \;       执行前确认
  -print0             用 null 分隔（配合 xargs -0）
```

```bash
# ===== 按名称查找 =====
find /etc -name "*.conf"
find /etc -iname "host*"           # 不区分大小写
find /etc -name "*.conf" -o -name "*.cfg"   # 或关系

# ===== 按类型查找 =====
find / -type f -name "*.txt" 2>/dev/null     # 普通文件
find / -type d -name "src" 2>/dev/null      # 目录
find / -type l -ls 2>/dev/null              # 符号链接

# ===== 按大小查找 =====
find / -size +100M -type f 2>/dev/null      # 大于 100MB 的文件
find / -size -1k -type f 2>/dev/null        # 小于 1KB 的文件
find . -size 0 -type f                       # 空文件

# ===== 按时间查找 =====
find /var/log -mtime -7 -type f             # 7 天内修改过
find /tmp -mmin -60 -type f                  # 60 分钟内修改过
find / -atime +30 -type f 2>/dev/null       # 30 天没访问过
find . -newer ref.txt                        # 比 ref.txt 更新的文件

# ===== 按权限查找（安全审计） =====
find / -perm -4000 -type f 2>/dev/null      # SUID 文件
find / -perm -2000 -type f 2>/dev/null      # SGID 文件
find / -perm -1000 -type d 2>/dev/null      # 有 Sticky Bit 的目录
find / -perm /6000 -type f 2>/dev/null      # SUID 或 SGID
find /tmp -perm -o+w -type d 2>/dev/null    # 其他用户可写的目录
find . -perm 777 -type f                    # 权限正好是 777

# ===== 按所有者查找 =====
find /home -user alice -type f
find / -nouser -type f 2>/dev/null          # 无有效所有者（孤儿文件）
find / -nogroup -type f 2>/dev/null         # 无有效组

# ===== 限制深度 =====
find /etc -maxdepth 2 -name "*.conf"
find . -mindepth 2 -maxdepth 3 -type d

# ===== 对找到的文件执行操作 =====

# 列出详细信息
find / -size +100M -type f -ls 2>/dev/null

# 复制到备份目录
find . -name "*.log" -exec cp {} /backup/ \;

# 删除 ⚠️ 高风险
find /tmp -name "*.tmp" -type f -delete

# 确认后删除
find . -name "*.bak" -ok rm {} \;

# 修改权限
find . -type d -exec chmod 755 {} \;
find . -type f -exec chmod 644 {} \;

# 更改所有者
find /data -user olduser -exec chown newuser {} \;

# 与 xargs 配合（处理大量文件更高效）
find . -name "*.log" | xargs gzip
find . -name "*.txt" -print0 | xargs -0 rm   # 安全处理含空格的文件名
```

> ⚠️ **风险提示**：
> - `find ... -delete` 会直接删除匹配文件，不可恢复。先不带 `-delete` 确认匹配结果。
> - `find / -exec rm {} \;` 等组合操作尤其危险，务必先验证。

### 3.2 其他查找命令

```bash
# ===== locate：快速文件名查找 =====
# 基于预建数据库，速度快但不是实时的
locate filename
locate -i filename              # 不区分大小写
locate -r "\.conf$"             # 正则匹配
locate -b '\filename'           # 只匹配 basename
locate -c                       # 只统计数量

# 更新数据库（需 root）🔑
updatedb
# 数据库位置：/var/lib/mlocate/mlocate.db
# 配置文件：/etc/updatedb.conf

# ===== which：查找可执行文件 =====
which python3
which -a python3               # 显示所有匹配（按 PATH 顺序）
which --skip-alias ls          # 跳过别名，找实际路径

# ===== whereis：查找二进制+源码+man =====
whereis python3
whereis -b python3             # 只找二进制
whereis -m python3             # 只找 man 手册
whereis -s python3             # 只找源码

# ===== type：查看命令类型 =====
type ls                        # 别名/内置/外部
type cd                        # cd 是 shell 内置
type -a python3                # 显示所有位置
type -p python3                # 只显示路径（如果是外部命令）
```

### 3.3 xargs — 参数转换

xargs 将标准输入转换为命令行参数，解决管道只能传文本不能传参数的问题。

```
语法：命令 | xargs [选项] 命令

核心参数：
  -0          以 null 字符分隔（配合 find -print0，安全处理空格）
  -n N        每次传 N 个参数
  -I {}       用 {} 替换参数（可控制位置）
  -d 分隔符    指定分隔符
  -P N        并行执行 N 个进程
  -t          先打印要执行的命令再执行
  -r          # 空输入时不执行命令（GNU xargs）
```

```bash
# 基本用法：把所有文件名传给 rm
find . -name "*.tmp" | xargs rm

# 安全处理含空格/特殊字符的文件名
find . -name "*.txt" -print0 | xargs -0 rm

# 控制参数位置（用 -I {}）
find . -name "*.jpg" | xargs -I {} cp {} /backup/
ls *.log | xargs -I {} mv {} {}.old

# 每次传 2 个参数
echo "1 2 3 4 5 6" | xargs -n 2 echo

# 并行执行（加速）
find . -name "*.wav" -print0 | xargs -0 -P 4 -I {} ffmpeg -i {} {}.mp3

# 先打印再执行（调试用）
ls | xargs -t -I {} echo "处理: {}"

# 经典组合：批量操作文件
# 批量压缩 .log 文件
find /var/log -name "*.log" -mtime +30 | xargs gzip

# 批量删除
find /tmp -name "*.tmp" -type f -mtime +7 -print0 | xargs -0 rm -f
```

---

## 四、进程与作业控制

### 4.1 进程查看

| 命令 | 用途 | 特点 |
|------|------|------|
| **ps** | 进程快照 | 一次性的进程列表 |
| **top** | 实时进程监控 | 实时更新，经典 |
| **htop** | 增强版 top | 更友好，支持鼠标，需安装 |
| **pstree** | 进程树 | 显示父子进程关系 |
| **pgrep** | 按名称查找 PID | 只输出 PID，适合脚本 |
| **pidof** | 按名称找 PID | 简单直接 |
| **nice** | 以指定 nice 值启动 | 启动时设置优先级 |
| **renice** | 调整已运行进程的 nice | 运行中改优先级 |

### 4.2 ps — 进程快照

```
常用组合：
  ps aux      BSD 风格，所有用户的所有进程（最常用）
  ps -ef      SYSV 风格，全格式（所有进程）
  ps -eLf     显示线程
  ps auxf     树状显示
  ps -u user  指定用户的进程
```

```bash
# 查看所有进程（BSD 风格）
ps aux
# USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND

# 查看所有进程（SYSV 风格）
ps -ef
# UID PID PPID C STIME TTY TIME CMD

# 按名称过滤
ps aux | grep nginx

# 显示线程
ps -eLf

# 树状显示进程关系
ps auxf
pstree -p            # 带 PID

# 查看指定用户的进程
ps -u alice
ps -u root

# 查看指定 PID 的详细信息
ps -p 1234 -f
ps -p 1234 -o pid,ppid,user,%cpu,%mem,cmd

# 自定义输出列
ps -eo pid,ppid,user,pcpu,pmem,comm --sort=-pcpu | head -10
```

**ps aux 各字段含义**：

| 字段 | 含义 |
|------|------|
| **USER** | 进程所有者 |
| **PID** | 进程 ID |
| **%CPU** | CPU 使用率 |
| **%MEM** | 内存使用率 |
| **VSZ** | 虚拟内存大小（KB） |
| **RSS** | 驻留内存大小（KB，物理内存） |
| **TTY** | 关联终端（? 表示无终端，守护进程） |
| **STAT** | 进程状态（见下表） |
| **START** | 启动时间 |
| **TIME** | 累计 CPU 时间 |
| **COMMAND** | 命令行 |

**进程状态（STAT 列）**：

| 字符 | 含义 |
|------|------|
| **R** | Running / Runnable（运行或就绪） |
| **S** | Sleeping（可中断睡眠，等待事件） |
| **D** | Disk Sleep（不可中断睡眠，等待 I/O） |
| **T** | Stopped（被暂停/停止） |
| **Z** | Zombie（僵尸，已终止父进程未回收） |
| **<** | 高优先级（nice 值低） |
| **N** | 低优先级（nice 值高） |
| **s** | 会话首进程（session leader） |
| **l** | 多线程 |
| **+** | 在前台进程组 |

### 4.3 top / htop — 实时监控

```bash
# 启动 top
top

# top 常用交互命令：
#   h / ?     帮助
#   q         退出
#   k         杀死进程（输入 PID）
#   r         调整 nice 值
#   P         按 CPU 排序（默认）
#   M         按内存排序
#   T         按时间排序
#   1         显示每个 CPU 核心
#   u         只显示指定用户的进程
#   f         选择显示字段
#   c         切换命令行显示（短/完整）
#   H         显示线程
#   W         保存配置到 ~/.toprc

# 非交互模式（取一次快照）
top -b -n 1
top -b -n 1 | head -20

# 指定刷新次数和间隔
top -b -n 3 -d 2    # 3 次，间隔 2 秒

# htop（需安装，更友好）
htop
#  支持鼠标操作
#  F1帮助 F2设置 F3搜索 F4过滤 F5树状 F6排序 F7降nice F8升nice F9杀进程 F10退出
```

### 4.4 pstree / pgrep / pidof

```bash
# ===== pstree：进程树 =====
pstree
pstree -p               # 显示 PID
pstree -a               # 显示命令行参数
pstree -u               # 显示用户切换
pstree root            # 显示指定用户的进程树

# ===== pgrep：按名称找 PID =====
pgrep nginx
pgrep -a nginx         # 显示命令行
pgrep -u alice         # 指定用户
pgrep -c nginx         # 只输出数量
pgrep -f "python.*app" # 匹配完整命令行

# ===== pidof：按名称找 PID =====
pidof nginx
pidof -s nginx        # 只输出一个 PID（脚本中用）
pidof -x script.sh    # 也匹配脚本
```

### 4.5 信号与 kill

| 信号 | 编号 | 名称 | 作用 | 能否捕获 |
|------|------|------|------|---------|
| **SIGHUP** | 1 | 挂起 | 终端断开；通常用于重载配置 | ✅ |
| **SIGINT** | 2 | 中断 | Ctrl+C，正常终止 | ✅ |
| **SIGQUIT** | 3 | 退出 | Ctrl+\，终止并 core dump | ✅ |
| **SIGKILL** | 9 | 杀死 | 强制终止，不可捕获/忽略 | ❌ |
| **SIGTERM** | 15 | 终止 | 优雅终止（默认信号） | ✅ |
| **SIGSEGV** | 11 | 段错误 | 内存访问违规 | ✅ |
| **SIGSTOP** | 19 | 停止 | 暂停进程，不可捕获/忽略 | ❌ |
| **SIGTSTP** | 20 | 终端停止 | Ctrl+Z | ✅ |
| **SIGCHLD** | 17 | 子进程退出 | 子进程终止时通知父进程 | ✅ |
| **SIGUSR1** | 10 | 用户信号 1 | 自定义用途 | ✅ |
| **SIGUSR2** | 12 | 用户信号 2 | 自定义用途 | ✅ |

```bash
# ===== kill：按 PID 发信号 =====

# 优雅终止（SIGTERM，默认信号 15）
kill 1234

# 强制杀死（SIGKILL，信号 9）⚠️ 高风险
kill -9 1234
kill -KILL 1234

# 重载配置（SIGHUP，信号 1）
kill -HUP 1234
kill -1 1234

# 暂停进程
kill -STOP 1234

# 继续暂停的进程
kill -CONT 1234

# ===== killall：按名称杀进程 =====

killall nginx                # 杀所有 nginx 进程
killall -9 nginx             # 强制杀死 ⚠️
killall -u alice nginx       # 只杀 alice 的 nginx
killall -i nginx             # 交互式（每个进程确认）

# ===== pkill：按模式杀进程 =====

pkill nginx                  # 按名称杀
pkill -9 nginx               # 强制杀死
pkill -f "python.*worker"    # 匹配完整命令行
pkill -u alice               # 杀 alice 的所有进程
pkill -STOP -u alice         # 暂停 alice 的所有进程

# ===== pkill 家族 =====
pgrep  → 找 PID
pkill  → 发信号
pwait  → 等待进程结束
```

> ⚠️ **风险提示**：
> - `kill -9` / `kill -KILL` 会强制终止进程，进程没有机会清理资源。生产环境应先用 `kill`（SIGTERM，默认），等几秒看是否退出，确认不行再用 `-9`。
> - `killall` 和 `pkill` 名称匹配可能误杀其他进程。先用 `pgrep` 确认匹配的 PID 列表。

### 4.6 作业控制

```bash
# ===== 后台运行 =====
command &              # 启动时直接放后台
./long_task.sh &

# ===== 暂停前台进程 =====
# Ctrl + Z

# ===== 查看作业 =====
jobs
jobs -l               # 显示 PID
jobs -p               # 只显示 PID

# ===== 后台继续 =====
bg %1                 # %1 指作业号 1
bg                    # 当前作业

# ===== 前台继续 =====
fg %1
fg

# ===== 终止作业 =====
kill %1
kill -9 %1

# ===== 退出终端后仍运行 =====

# nohup：忽略 SIGHUP，输出到 nohup.out
nohup ./long_task.sh &

# disown：从作业表移除（Shell 退出时不发 SIGHUP）
./long_task.sh &
disown

# setsid：新会话运行（脱离当前终端）
setsid ./long_task.sh

# 推荐组合（完全脱离终端）
nohup ./long_task.sh > output.log 2>&1 &
disown
```

### 4.7 nice / renice — 优先级

```bash
# nice 值范围：-20（最高）到 19（最低）
# 默认 nice 值为 0

# 以指定 nice 值启动程序
nice -n 10 command      # 低优先级（nice 10）
nice -n -5 command     # 高优先级（nice -5，需 root）🔑

# 调整已运行进程的 nice
renice 10 -p 1234      # 改为 10
renice -5 -p 1234      # 改为 -5（需 root）🔑
renice +5 -p 1234      # 增加 5（变低）

# 批量调整某个用户的所有进程
renice 10 -u alice

# 查看进程的 nice 值
ps -eo pid,ni,comm | head -10
top    # NI 列
```

---

## 五、用户与权限

### 5.1 用户与组管理 🔑

| 命令 | 用途 |
|------|------|
| **useradd** | 创建用户 |
| **usermod** | 修改用户 |
| **userdel** | 删除用户 |
| **groupadd** | 创建组 |
| **groupmod** | 修改组 |
| **groupdel** | 删除组 |
| **passwd** | 修改密码 |
| **chage** | 密码时效管理 |
| **id** | 查看用户/组信息 |
| **whoami / who / w** | 查看当前/在线用户 |

```bash
# ===== 创建用户 =====
useradd -m -s /bin/bash -G sudo,developers alice
# -m 创建主目录
# -s 指定登录 Shell
# -G 指定附加组
# -u 指定 UID
# -g 指定主组

# Debian/Ubuntu 更推荐的方式：
adduser alice          # 交互式创建用户

# ===== 修改用户 =====
usermod -s /bin/zsh alice          # 修改登录 Shell
usermod -aG sudo alice             # 添加到 sudo 组（-a 追加）
usermod -G newgroup alice          # 替换附加组列表（注意！不是追加）
usermod -d /home/newhome -m alice  # 修改主目录并移动
usermod -L alice                   # 锁定账户
usermod -U alice                   # 解锁账户

# ===== 删除用户 =====
userdel alice                      # 删除用户（保留主目录）
userdel -r alice                   # 删除用户和主目录/邮件

# ===== 组管理 =====
groupadd developers
groupadd -g 1234 devops            # 指定 GID
groupmod -n newname oldname        # 重命名组
groupdel developers                # 删除组

# ===== 密码管理 =====
passwd                           # 修改自己的密码
passwd alice                     # 修改指定用户的密码（需 root）🔑
passwd -l alice                  # 锁定密码
passwd -u alice                  # 解锁密码
passwd -S alice                  # 查看密码状态
passwd -e alice                  # 强制下次登录改密码

# ===== 密码时效 =====
chage -l alice                   # 查看密码时效信息
chage -M 90 alice                # 密码最长使用 90 天
chage -m 1 alice                 # 最短使用 1 天
chage -W 7 alice                 # 到期前 7 天警告
chage -I 30 alice                # 过期 30 天后锁定
chage -E 2024-12-31 alice        # 账户在指定日期过期
chage -d 0 alice                 # 强制下次登录改密码

# ===== 查看用户信息 =====
id                               # 当前用户
id alice                         # 指定用户
whoami                           # 当前用户名
who                              # 已登录用户
w                                # 详细登录用户（在做什么）
last                             # 登录历史
lastb                            # 失败登录
```

### 5.2 权限命令

```bash
# ===== chmod：修改权限 =====

# 数字方式
chmod 755 file.txt               # rwxr-xr-x
chmod 644 file.txt               # rw-r--r--
chmod 600 ~/.ssh/id_rsa          # rw-------
chmod 700 ~/.ssh                 # rwx------

# 符号方式
chmod u+x file.sh                # 所有者加执行权限
chmod g-w file.txt               # 组减写权限
chmod o-rwx file.txt             # 其他用户去掉所有权限
chmod a+r file.txt               # 所有人加读
chmod ug=rw file.txt             # 所有者和组设为读写
chmod +x file.sh                 # 所有人加执行（等价 a+x）
chmod u+s program                # 设置 SUID
chmod g+s sharedir               # 设置 SGID
chmod +t /tmp                    # 设置 Sticky Bit

# 递归修改
chmod -R 644 /path/to/dir
find /path -type d -exec chmod 755 {} \;
find /path -type f -exec chmod 644 {} \;

# ===== chown：修改所有者 =====🔑

chown user file.txt              # 只改所有者
chown user:group file.txt        # 同时改所有者和组
chown :group file.txt            # 只改组
chown user: file.txt             # 组设为用户主组
chown -R user:group /dir         # 递归修改
chown -R --reference=ref /dir    # 参考另一个文件的所有者

# ===== chgrp：修改组 =====🔑

chgrp groupname file.txt
chgrp -R groupname /dir

# ===== umask：文件创建掩码 =====

umask                           # 查看当前 umask（八进制）
umask -S                        # 符号形式
umask 027                       # 设置 umask
# 永久设置：在 ~/.bashrc 或 /etc/profile 中

# ===== ACL：访问控制列表 =====

# 查看
getfacl file.txt

# 设置用户权限
setfacl -m u:alice:rwx file.txt      # 用户 alice 读写执行
setfacl -m g:dev:rw file.txt         # 组 dev 读写
setfacl -m o::r file.txt            # 其他用户只读

# 设置默认 ACL（目录内新建文件自动继承）
setfacl -m d:u:alice:rwx /dir
setfacl -m d:g:dev:rwx /dir

# 删除单个 ACL
setfacl -x u:alice file.txt

# 删除所有 ACL
setfacl -b file.txt

# 递归设置
setfacl -R -m u:alice:rw /data/

# 复制 ACL
getfacl file1.txt | setfacl --set-file=- file2.txt
```

### 5.3 sudo / su

```bash
# ===== su：切换用户 =====

su - username                    # 登录式切换（环境变量全部重置，推荐）
su username                     # 非登录式切换（保留当前环境）
su -                            # 切到 root（需 root 密码）
su -c "command" username        # 以指定用户执行命令

# ===== sudo：以其他身份执行 =====

sudo command                    # 以 root 执行
sudo -u user command            # 以指定用户执行
sudo -i                         # 以 root 身份登录（获得完整 root 环境）
sudo -s                         # 以 root 运行当前 Shell（保留环境）
sudo -l                         # 查看当前用户的 sudo 权限
sudo !!                         # 以上一条命令用 sudo 执行（最常用！）
sudo -k                         # 清除缓存的密码（下次需要重新输入）
sudo -v                         # 延长 sudo 密码缓存时间

# 编辑 sudoers（必须用 visudo！）🔑
visudo                           # 安全编辑（检查语法）
visudo -f /etc/sudoers.d/custom  # 编辑自定义片段

# sudoers 示例：
# alice ALL=(ALL:ALL) ALL                    # 全部命令，需密码
# bob ALL=(ALL:ALL) NOPASSWD: ALL            # 全部命令，免密码
# %admins ALL=(ALL) ALL                      # admins 组全部命令
# deploy ALL= NOPASSWD: /usr/bin/systemctl restart nginx  # 只能重启 nginx
```

---

## 六、网络

### 6.1 网络配置

```bash
# ===== ip 命令（iproute2，现代） =====

# 查看接口
ip addr show                     # 所有接口和 IP
ip addr show eth0                # 指定接口
ip link show                     # 接口状态
ip link set eth0 up              # 启用接口🔑
ip link set eth0 down            # 禁用接口🔑
ip link set eth0 address 00:11:22:33:44:55   # 改 MAC🔑

# 配置 IP（临时，重启失效）🔑
ip addr add 192.168.1.100/24 dev eth0
ip addr del 192.168.1.100/24 dev eth0
ip addr flush dev eth0           # 清空接口 IP

# 路由
ip route show                    # 路由表
ip route add default via 192.168.1.1   # 默认网关🔑
ip route add 10.0.0.0/8 via 192.168.1.254 dev eth0  # 静态路由🔑
ip route del 10.0.0.0/8          # 删除路由🔑

# 邻居（ARP 表）
ip neigh show
ip neigh add 192.168.1.1 lladdr 00:11:22:33:44:55 dev eth0
ip neigh flush all

# ifconfig（net-tools，旧工具，可能未安装）
ifconfig
ifconfig eth0
ifconfig eth0 192.168.1.100 netmask 255.255.255.0  # 临时配置🔑
ifconfig eth0 up/down
```

### 6.2 网络测试

```bash
# ===== ping：连通性测试 =====
ping google.com
ping -c 4 8.8.8.8                # 发 4 个包
ping -i 0.5 8.8.8.8              # 间隔 0.5 秒
ping -s 1400 8.8.8.8             # 指定包大小（1400 字节）
ping -f 8.8.8.8                  # 洪水 ping（需 root，压力测试）🔑
ping -M do -s 1472 8.8.8.8       # 不分片，测试 MTU

# ===== traceroute / mtr：路由跟踪 =====
traceroute google.com            # UDP 方式
traceroute -T google.com         # TCP 方式
traceroute -n google.com         # 不解析域名（更快）
traceroute -I google.com         # ICMP 方式

mtr google.com                   # 组合 ping+traceroute，实时
mtr --report google.com          # 报告模式（发 10 个包后输出报告）
mtr -rwc 100 google.com          # 100 个包，宽格式输出

# ===== 端口连通性测试 =====

# telnet（传统）
telnet 192.168.1.1 22

# nc / netcat（瑞士军刀）
nc -zv 192.168.1.1 22            # 测试 TCP 端口是否通
nc -zuv 192.168.1.1 53           # 测试 UDP 端口
nc -l 8080                       # 监听端口（简单服务）
echo "hello" | nc server 8080    # 发送数据

# curl 测试
curl -v telnet://192.168.1.1:22  # 用 curl 测试端口

# ===== DNS 测试 =====
nslookup example.com
nslookup example.com 8.8.8.8     # 指定 DNS 服务器
nslookup -type=mx gmail.com      # 查询 MX 记录

dig example.com                  # 推荐工具，更详细
dig example.com MX               # MX 记录
dig example.com NS               # NS 记录
dig example.com +trace           # 跟踪完整解析过程
dig -x 8.8.8.8                   # 反向解析
dig @8.8.8.8 example.com         # 指定 DNS 服务器

host example.com
host -t mx gmail.com
```

### 6.3 网络连接查看

```bash
# ===== ss：现代网络连接工具 =====

ss -tlnp                        # 所有 TCP 监听端口（含进程）
ss -ulnp                        # 所有 UDP 监听端口
ss -tulnp                       # 所有监听（TCP+UDP）
ss -tn state established        # 已建立的 TCP 连接
ss -s                           # 连接统计摘要
ss -ti                          # 显示 TCP 内部信息（RTT、窗口等）
ss -o state established '( dport = :443 or sport = :443 )'  # 443 端口连接
ss -p                           # 显示进程（需 root 看完整）

# ===== netstat：传统工具 =====
netstat -tlnp                   # TCP 监听
netstat -ulnp                   # UDP 监听
netstat -tulnp                  # 所有监听
netstat -an                     # 所有连接
netstat -r                      # 路由表
netstat -i                      # 接口统计
netstat -s                      # 协议统计

# 查找占用端口的进程
ss -tulnp | grep :8080
netstat -tulnp | grep :8080
lsof -i :8080                   # 用 lsof 查
fuser 8080/tcp                  # 用 fuser 查
```

### 6.4 抓包与下载

```bash
# ===== tcpdump：抓包 =====

# 抓取指定接口
tcpdump -i eth0

# 抓取指定端口
tcpdump -i eth0 port 80
tcpdump -i eth0 port 80 or port 443
tcpdump -i eth0 tcp port 22

# 抓取指定主机
tcpdump -i eth0 host 192.168.1.100
tcpdump -i eth0 src host 10.0.0.1
tcpdump -i eth0 dst host 10.0.0.2

# 保存到文件
tcpdump -i eth0 -w capture.pcap
tcpdump -i eth0 -c 100 -w capture.pcap    # 抓 100 个包后退出

# 读取文件
tcpdump -r capture.pcap
tcpdump -r capture.pcap -n             # 不解析域名

# 常用选项
tcpdump -n                          # 不解析 IP 和端口的名称（更快）
tcpdump -nn                         # IP 和端口都不解析
tcpdump -X                          # 同时以十六进制和 ASCII 显示内容
tcpdump -A                          # 以 ASCII 显示（看 HTTP 内容）
tcpdump -s 0                        # 抓完整包（默认只抓 262144 字节）
tcpdump -v / -vv / -vvv             # 详细程度

# ===== curl / wget：HTTP 测试/下载 =====

# curl 常用
curl https://example.com            # GET 请求，输出响应体
curl -I https://example.com         # 只看响应头（HEAD）
curl -v https://example.com         # 详细输出（请求+响应）
curl -o output.html https://example.com  # 保存到文件
curl -O https://example.com/file.txt   # 保存为原文件名
curl -X POST -d "name=alice" https://example.com  # POST 请求
curl -H "Authorization: Bearer token" https://example.com  # 自定义请求头
curl -k https://self-signed.example.com    # 跳过证书验证
curl -x proxy:8080 https://example.com     # 使用代理
curl -u user:pass https://example.com      # HTTP 基本认证
curl --resolve example.com:443:1.2.3.4 https://example.com  # 指定 IP 解析
curl -s https://example.com | jq .         # 静默模式 + JSON 格式化

# wget 常用
wget https://example.com/file.txt
wget -O output.txt https://example.com      # 指定保存名
wget -c https://example.com/big.iso         # 断点续传
wget -r https://example.com                 # 递归下载（整站）
wget --mirror https://example.com           # 镜像网站
wget --limit-rate=100k https://example.com  # 限速下载
wget --user=user --password=pass https://... # FTP/HTTP 认证

# ===== rsync：远程同步 =====

# 本地同步
rsync -av src/ dest/

# 远程同步（推送到服务器）
rsync -avz /local/path/ user@server:/remote/path/

# 远程同步（从服务器拉取）
rsync -avz user@server:/remote/path/ /local/path/

# 常用参数：
#   -a  归档模式（= -rlptgoD）
#   -v  详细输出
#   -z  传输时压缩
#   -n  试运行（不真正同步）
#   --delete  删除目标中源没有的文件（镜像）
#   -e 'ssh -p 2222'  指定 SSH 端口
#   --exclude='*.log'  排除文件
#   --progress  显示进度

# 安全试运行（推荐先做）
rsync -avzn src/ dest/
```

### 6.5 SSH 与远程传输

```bash
# ===== ssh：远程登录 =====
ssh user@hostname
ssh -p 2222 user@hostname          # 指定端口
ssh -i ~/.ssh/id_rsa user@hostname # 指定私钥
ssh -X user@hostname              # 启用 X11 转发
ssh -L 8080:localhost:80 user@host  # 本地端口转发
ssh -R 8080:localhost:80 user@host  # 远程端口转发
ssh -D 1080 user@host             # SOCKS 代理
ssh -N -f -L 8080:localhost:80 user@host  # 后台运行，不打开 Shell

# 执行远程命令
ssh user@hostname "ls -la /tmp"
ssh user@hostname "uptime && free -h"

# SSH 配置文件（~/.ssh/config）
# Host server01
#     HostName 192.168.1.100
#     User alice
#     Port 22
#     IdentityFile ~/.ssh/id_rsa
#     ServerAliveInterval 60

# 密钥生成
ssh-keygen -t rsa -b 4096 -C "your@email.com"
ssh-keygen -t ed25519 -C "your@email.com"  # 推荐，更短更安全
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_work -C "work"

# 推送公钥（免密登录）
ssh-copy-id user@hostname
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@hostname

# ===== scp：远程复制 =====

# 本地 → 远程
scp localfile user@host:/remote/path/
scp -r localdir user@host:/remote/path/   # 递归目录

# 远程 → 本地
scp user@host:/remote/file /local/path/
scp -r user@host:/remote/dir /local/path/

# 指定端口
scp -P 2222 localfile user@host:/path/

# 保留权限和时间
scp -p localfile user@host:/path/

# 限速（1MB/s = 1024 Kb/s）
scp -l 8192 localfile user@host:/path/
```

### 6.6 防火墙

```bash
# ===== iptables =====

# 查看规则
iptables -L -n -v
iptables -L -n --line-numbers
iptables -t nat -L -n
iptables -S                           # 以规则格式输出

# 基本策略设置🔑
iptables -P INPUT DROP                # 默认拒绝入站
iptables -P OUTPUT ACCEPT             # 默认允许出站
iptables -P FORWARD DROP              # 默认拒绝转发

# 允许已建立连接
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 允许特定端口
iptables -A INPUT -p tcp --dport 22 -j ACCEPT     # SSH
iptables -A INPUT -p tcp --dport 80 -j ACCEPT     # HTTP
iptables -A INPUT -p tcp --dport 443 -j ACCEPT    # HTTPS
iptables -A INPUT -s 192.168.1.0/24 -j ACCEPT     # 允许内网
iptables -A INPUT -i lo -j ACCEPT                  # 允许回环

# NAT
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE  # 地址伪装
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to 10.0.0.1:8080

# 删除规则
iptables -D INPUT 3                    # 按行号删
iptables -D INPUT -p tcp --dport 80 -j ACCEPT  # 按内容删
iptables -F                           # 清空所有规则
iptables -t nat -F                    # 清空 nat 表
iptables -X                           # 删除自定义链

# 保存和恢复
iptables-save > /etc/iptables/rules.v4
iptables-restore < /etc/iptables/rules.v4

# ===== nftables =====
nft list ruleset                      # 查看所有规则
nft add table inet filter             # 添加表
nft add chain inet filter input { type filter hook input priority 0 \; }
nft add rule inet filter input tcp dport 22 accept

# ===== firewalld（RHEL/CentOS） =====
firewall-cmd --state                 # 状态
firewall-cmd --list-all              # 所有配置
firewall-cmd --get-default-zone      # 默认 zone
firewall-cmd --get-zones             # 所有 zone
firewall-cmd --permanent --add-port=8080/tcp   # 永久开放端口🔑
firewall-cmd --permanent --add-service=http     # 永久开放服务🔑
firewall-cmd --permanent --remove-port=8080/tcp
firewall-cmd --reload                # 重新加载（使永久配置生效）
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" service name="ssh" accept'

# ===== ufw（Ubuntu/Debian） =====
ufw status                          # 状态
ufw status verbose
ufw default deny incoming           # 默认拒绝入站🔑
ufw default allow outgoing          # 默认允许出站🔑
ufw allow 22/tcp                    # 允许 SSH
ufw allow 80/tcp                    # 允许 HTTP
ufw allow from 192.168.1.0/24       # 允许内网
ufw allow in on eth0 from any to any port 80 proto tcp
ufw delete allow 23/tcp             # 删除规则
ufw enable                          # 启用🔑
ufw disable                         # 禁用
ufw status numbered                 # 带编号的状态
ufw delete 3                        # 按编号删除规则
```

> ⚠️ **防火墙配置警告**：远程服务器上配置防火墙时，如果 INPUT 默认策略是 DROP 且没有允许 SSH 端口，会立刻断开连接。建议先添加允许规则再改默认策略，或使用 `at` 定时任务自动回滚。

---

## 七、磁盘与文件系统

| 命令 | 用途 | 风险等级 |
|------|------|---------|
| **lsblk** | 列出块设备树 | ★☆☆☆☆ |
| **blkid** | 块设备信息（UUID/类型） | ★☆☆☆☆ |
| **df** | 磁盘空间/ inode 使用 | ★☆☆☆☆ |
| **du** | 目录/文件大小 | ★☆☆☆☆ |
| **fdisk** | MBR 分区工具 | ★★★★★ |
| **parted** | 通用分区工具（GPT） | ★★★★★ |
| **mkfs** | 格式化（创建文件系统） | ★★★★★ |
| **mount** | 挂载 | ★★☆☆☆ |
| **umount** | 卸载 | ★★☆☆☆ |
| **fsck** | 文件系统检查/修复 | ★★★★☆ |
| **dd** | 磁盘复制/转换 | ★★★★★ |

```bash
# ===== 信息查看 =====

# 块设备树状图
lsblk
lsblk -f                        # 含文件系统、LABEL、UUID
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT,UUID

# 设备 UUID 和类型
blkid
blkid /dev/sda1

# 磁盘空间
df -h                           # 人类可读
df -i                           # inode 使用
df -T                           # 显示文件系统类型
df -h --total                   # 汇总行

# 目录大小
du -sh /path                    # 汇总大小
du -h --max-depth=1 /var        # 一级目录大小
du -ah /path | sort -rh | head -20   # 最大的 20 个文件/目录
ncdu /path                      # 交互式磁盘使用分析（需安装）

# ===== 分区 =====

# fdisk：MBR 分区
fdisk /dev/sdb
# 交互命令：m=帮助 n=新建 d=删除 p=打印 t=改类型 w=写入 q=退出

# parted：GPT + MBR
parted /dev/sdb
# (parted) mklabel gpt            创建 GPT 分区表
# (parted) mkpart primary 0% 100%  创建分区
# (parted) print                 打印分区表
# (parted) rm 1                  删除第 1 个分区
# (parted) unit GB               切换单位

# gdisk：GPT 专用（类 fdisk 界面）
gdisk /dev/sdb

# ===== 格式化 ⚠️ 极高风险 =====
mkfs.ext4 /dev/sdb1
mkfs.ext4 -L mylabel /dev/sdb1     # 加卷标
mkfs.xfs /dev/sdb1
mkfs.xfs -L mylabel /dev/sdb1
mkfs.btrfs /dev/sdb1
mkfs.vfat /dev/sdb1                # FAT32
mkswap /dev/sdb2                   # 创建 swap
swapon /dev/sdb2                   # 启用 swap
swapoff /dev/sdb2                  # 关闭 swap

# ===== 挂载/卸载 =====
mount /dev/sdb1 /data
mount -t ext4 /dev/sdb1 /data
mount -o noatime,nosuid,nodev /dev/sdb1 /data
mount -o loop image.iso /mnt
mount -a                           # 挂载 fstab 中所有未挂载的

umount /data
umount /dev/sdb1
umount -l /data                    # 懒惰卸载
umount -f /data                    # 强制卸载（NFS 等）

# ===== 检查修复 ⚠️ =====
# 注意：必须先卸载再检查！

fsck /dev/sdb1
fsck -y /dev/sdb1                  # 自动修复
e2fsck -f /dev/sdb1                # ext4 强制检查
xfs_repair /dev/sdb1               # XFS 修复
btrfs check /dev/sdb1              # Btrfs 检查

# ===== dd：磁盘级复制 ⚠️ 极高风险 =====

# 备份整个磁盘到镜像文件
dd if=/dev/sda of=/backup/sda.img bs=4M status=progress

# 从镜像恢复
dd if=sda.img of=/dev/sda bs=4M status=progress

# 生成指定大小的测试文件
dd if=/dev/zero of=testfile bs=1M count=100   # 100MB 文件

# 安全擦除磁盘（用随机数覆盖）
dd if=/dev/urandom of=/dev/sdb bs=4M status=progress

# 测试磁盘读写速度
dd if=/dev/zero of=testfile bs=1G count=1 oflag=direct
dd if=testfile of=/dev/null bs=1G count=1 iflag=direct

# ⚠️ dd 输入输出错了会直接毁掉磁盘！务必确认 if= 和 of= 方向
```

> ⚠️ **最高风险警告**：
> - `mkfs` 格式化会**删除分区上的所有数据**，先确认目标设备正确。
> - `fdisk` / `parted` 修改分区表错误会导致数据丢失，操作前备份。
> - `dd` 被称为"磁盘毁灭者"，`if=` 和 `of=` 写反了会直接覆盖系统盘。用前再三确认。
> - `fsck` 不能对已挂载的分区执行（可能损坏文件系统），必须先卸载。根分区需进单用户模式或 Live CD。

---

## 八、压缩与归档

### 8.1 tar — 归档工具

```
语法：tar [选项] 归档文件 [文件...]

常用参数组合：
  -c    创建归档（create）
  -x    提取（extract）
  -t    列出内容（list）
  -v    显示过程（verbose）
  -f    指定归档文件名（必须放在最后）
  -z    gzip 压缩（.tar.gz / .tgz）
  -j    bzip2 压缩（.tar.bz2）
  -J    xz 压缩（.tar.xz）
  -C    提取到指定目录
  --exclude   排除文件
  -p    保留权限
  --totals  结束时显示总字节数
```

```bash
# ===== 创建归档 =====

# 仅打包，不压缩
tar -cvf archive.tar file1 file2 dir/

# gzip 压缩（最常用，速度快）
tar -czvf archive.tar.gz file1 dir/
tar -czvf archive.tgz file1 dir/          # 同上，后缀简写

# bzip2 压缩（压缩率高，慢）
tar -cjvf archive.tar.bz2 file1 dir/

# xz 压缩（压缩率最高，最慢）
tar -cJvf archive.tar.xz file1 dir/

# 排除某些文件
tar -czvf archive.tar.gz --exclude='*.log' --exclude='tmp/' dir/

# 保留权限（备份用）
tar -cpvf backup.tar /etc/

# ===== 查看内容 =====

tar -tvf archive.tar
tar -tzvf archive.tar.gz
tar -tjvf archive.tar.bz2

# ===== 提取归档 =====

# 提取到当前目录
tar -xvf archive.tar
tar -xzvf archive.tar.gz
tar -xjvf archive.tar.bz2
tar -xJvf archive.tar.xz

# 提取到指定目录
tar -xzvf archive.tar.gz -C /target/dir/

# 只提取特定文件
tar -xzvf archive.tar.gz path/to/file.txt

# ===== 其他 =====

# 追加文件到已存在的归档（仅未压缩的 tar）
tar -rvf archive.tar newfile.txt

# 更新文件（比归档中新才加）
tar -uvf archive.tar *.txt

# 对比归档与文件的差异
tar -dvf archive.tar
```

### 8.2 其他压缩工具

```bash
# ===== gzip / gunzip =====
gzip file.txt                    # 压缩为 file.txt.gz（删除原文件）
gzip -k file.txt                 # 保留原文件
gzip -d file.txt.gz              # 解压（同 gunzip）
gunzip file.txt.gz
gzip -l file.txt.gz              # 查看压缩率
zcat file.txt.gz                 # 查看压缩文件内容（不解压到磁盘）

# ===== bzip2 / bunzip2 =====
bzip2 file.txt                   # 压缩为 file.txt.bz2
bzip2 -k file.txt                # 保留原文件
bzip2 -d file.txt.bz2            # 解压
bunzip2 file.txt.bz2
bzcat file.txt.bz2               # 查看内容

# ===== xz / unxz =====
xz file.txt                     # 压缩
xz -k file.txt                  # 保留原文件
xz -d file.txt.xz               # 解压
unxz file.txt.xz
xzcat file.txt.xz               # 查看内容
xz -9 file.txt                  # 最高压缩比

# ===== zip / unzip =====
zip archive.zip file1 file2     # 压缩
zip -r archive.zip dir/         # 递归压缩目录
zip -e secret.zip file.txt      # 加密压缩（需要密码）
zip -P password secret.zip file.txt  # 命令行指定密码（不安全）

unzip archive.zip               # 解压
unzip archive.zip -d /target/   # 解压到指定目录
unzip -l archive.zip            # 列出内容
unzip -t archive.zip            # 测试完整性
unzip -p archive.zip file.txt   # 输出到标准输出

# ===== 7z =====
7z a archive.7z file1 dir/      # 创建压缩包
7z x archive.7z                 # 解压（完整路径）
7z e archive.7z                 # 解压（不保留路径）
7z l archive.7z                 # 列出内容
7z a -p archive.7z file.txt     # 加密
```

---

## 九、包管理

### 9.1 四大发行版包管理对比

| 操作 | Debian/Ubuntu (apt/dpkg) | RHEL/CentOS (yum/dnf/rpm) | Arch (pacman) | openSUSE (zypper) |
|------|------------------------|------------------------|---------------|------------------|
| 更新包列表 | `apt update` | `yum check-update` | `pacman -Sy` | `zypper ref` |
| 升级系统 | `apt full-upgrade` | `yum update` | `pacman -Syu` | `zypper up` |
| 安装包 | `apt install pkg` | `yum install pkg` | `pacman -S pkg` | `zypper in pkg` |
| 卸载包 | `apt remove pkg` | `yum remove pkg` | `pacman -R pkg` | `zypper rm pkg` |
| 卸载（含配置） | `apt purge pkg` | `yum remove pkg` | `pacman -Rn pkg` | `zypper rm -u pkg` |
| 搜索 | `apt search kw` | `yum search kw` | `pacman -Ss kw` | `zypper se kw` |
| 包信息 | `apt show pkg` | `yum info pkg` | `pacman -Si pkg` | `zypper info pkg` |
| 已安装列表 | `dpkg -l` | `rpm -qa` | `pacman -Q` | `rpm -qa` |
| 文件属哪个包 | `dpkg -S /path` | `rpm -qf /path` | `pacman -Qo /path` | `rpm -qf /path` |
| 包含哪些文件 | `dpkg -L pkg` | `rpm -ql pkg` | `pacman -Ql pkg` | `rpm -ql pkg` |
| 安装本地包 | `dpkg -i pkg.deb` | `rpm -i pkg.rpm` | `pacman -U pkg.tar.zst` | `rpm -i pkg.rpm` |
| 清理缓存 | `apt clean` | `yum clean all` | `pacman -Sc` | `zypper clean` |

### 9.2 Debian/Ubuntu — apt / dpkg

```bash
# ===== 更新与升级 =====
apt update                       # 更新包列表
apt upgrade                      # 升级可升级的包
apt full-upgrade                 # 智能升级（处理依赖变化）
apt dist-upgrade                 # 同上（传统名）
apt autoremove                   # 自动移除无用依赖
apt clean                        # 清理下载缓存
apt autoclean                    # 清理无法下载的包缓存

# ===== 安装与卸载 =====
apt install package              # 安装
apt install -y package           # 自动确认🔑
apt install package=1.0.0        # 安装指定版本
apt install --reinstall package  # 重新安装
apt remove package               # 卸载（保留配置）
apt purge package                # 卸载（删除配置）🔑
apt hold package                 # 锁定版本（不升级）
apt unhold package               # 解锁

# ===== 查询 =====
apt search keyword               # 搜索
apt show package                 # 包详情
apt list --installed             # 列出已安装
apt list --upgradable            # 列出可升级
apt depends package              # 依赖关系
apt rdepends package             # 反向依赖（谁依赖它）
apt policy package               # 版本与优先级

# ===== dpkg 底层 =====
dpkg -i package.deb              # 安装本地 deb 包🔑
dpkg -r package                  # 卸载（保留配置）
dpkg -P package                  # 卸载（删除配置）
dpkg -l                          # 列出所有已安装
dpkg -L package                  # 列出包安装的文件
dpkg -S /path/to/file            # 查找文件属哪个包
dpkg -s package                  # 包状态信息
dpkg-reconfigure package         # 重新配置包
dpkg -C                          # 检查损坏的包
```

### 9.3 RHEL/CentOS — yum / dnf / rpm

```bash
# ===== 更新与升级 =====
yum check-update                 # 检查更新
yum update                       # 更新所有包
yum update package               # 更新指定包
yum upgrade                      # 升级（同 update，新版本用）
yum autoremove                   # 移除无用依赖
yum clean all                    # 清理缓存
yum clean packages               # 清理包缓存

# ===== 安装与卸载 =====
yum install package              # 安装
yum install -y package           # 自动确认🔑
yum remove package               # 卸载
yum erase package                # 同上
yum reinstall package            # 重新安装
yum downgrade package            # 降级

# ===== 查询 =====
yum search keyword               # 搜索
yum info package                 # 包详情
yum list installed               # 已安装列表
yum list updates                 # 可更新列表
yum provides /path/to/file       # 哪个包提供此文件
yum deplist package              # 依赖列表
yum history                      # yum 操作历史
yum history undo N               # 撤销第 N 次操作
yum history info N               # 第 N 次操作详情

# ===== 仓库管理 =====
yum repolist                     # 列出启用的仓库
yum repolist all                 # 列出所有仓库
yum-config-manager --add-repo URL     # 添加仓库
yum-config-manager --enable repo      # 启用
yum-config-manager --disable repo     # 禁用

# ===== rpm 底层 =====
rpm -ivh package.rpm              # 安装🔑
rpm -e package                    # 卸载
rpm -qa                           # 列出所有已安装
rpm -qi package                   # 包信息
rpm -ql package                   # 列出文件
rpm -qf /path/to/file             # 文件属哪个包
rpm -q --scripts package          # 安装/卸载脚本
rpm -Va                           # 校验所有已安装包
rpm --import KEY_FILE             # 导入 GPG 密钥
```

> **注意**：RHEL 8+ 和 Fedora 默认使用 dnf 替代 yum。dnf 命令语法与 yum 基本兼容，直接替换即可。

### 9.4 Arch Linux — pacman

```bash
# ===== 更新 =====
pacman -Sy                       # 同步数据库
pacman -Syu                      # 全系统更新（滚动发行版核心命令）
pacman -Syyu                     # 强制同步数据库再更新

# ===== 安装与卸载 =====
pacman -S package                # 安装
pacman -S --needed package       # 已安装则跳过
pacman -R package                # 卸载
pacman -Rs package              # 卸载 + 删除不再需要的依赖
pacman -Rns package              # 卸载 + 删依赖 + 删配置
pacman -U package.pkg.tar.zst    # 安装本地包🔑

# ===== 查询 =====
pacman -Ss keyword               # 搜索远程库
pacman -Qs keyword               # 搜索已安装
pacman -Si package               # 远程包信息
pacman -Qi package               # 本地包信息
pacman -Q                        # 列出所有已安装
pacman -Qe                       # 列出显式安装的
pacman -Qd                       # 列出作为依赖安装的
pacman -Qdt                      # 孤立包（不再需要的依赖）
pacman -Ql package               # 列出包文件
pacman -Qo /path/to/file         # 文件属哪个包
pacman -F filename               # 快速查哪个包有文件

# ===== 清理 =====
pacman -Sc                       # 清理未安装包的缓存
pacman -Scc                      # 清理所有缓存
pacman -Rns $(pacman -Qdtq)      # 清理孤立包

# ===== AUR 辅助（yay/paru） =====
yay -Syu                         # 更新（含 AUR）
yay -Ss package                  # 搜索（含 AUR）
yay -G package                   # 仅下载 PKGBUILD
```

---

## 十、系统监控与日志

### 10.1 系统资源监控

```bash
# ===== 概览 =====
uptime                           # 运行时间 + 负载
uname -a                         # 内核信息
hostname                         # 主机名
cat /etc/os-release              # 发行版信息
hostnamectl                      # systemd 主机信息

# ===== 内存 =====
free -h                          # 人类可读
free -m                          # MB
free -g                          # GB
cat /proc/meminfo                # 详细内存信息

# ===== CPU =====
cat /proc/cpuinfo | grep "model name" | head -1
nproc                            # CPU 核心数
lscpu                            # CPU 详细信息

# ===== 负载 =====
uptime                           # 1/5/15 分钟负载
cat /proc/loadavg
w                                # 谁在做什么 + 负载

# ===== 虚拟内存统计 =====
vmstat 1                         # 每秒刷新
vmstat -s                        # 内存统计汇总
# r=运行队列 b=不可中断睡眠 swpd=交换 si/so=换入换出 bi/bo=I/O us/sy/id=CPU

# ===== I/O 统计 =====
iostat -xz 1                     # 详细 I/O，每秒
iostat -d -k 1                   # 磁盘吞吐（KB/s）
iotop                            # 实时 I/O 排行（需 root）🔑
dstat                            # 全能监控（CPU/磁盘/网络/内存）
glances                          # 高颜值综合监控

# ===== CPU 统计 =====
mpstat -P ALL 1                  # 每个 CPU 核心，每秒

# ===== 系统活动报告（sar） =====
sar -u                           # CPU 使用
sar -r                           # 内存
sar -n DEV                       # 网络接口
sar -b                           # I/O
sar -q                           # 负载
sar -u -f /var/log/sa/sa24       # 读取历史数据
```

### 10.2 内核与硬件

```bash
# ===== 内核 =====
uname -r                         # 内核版本
uname -a                         # 完整信息
cat /proc/version                # 内核版本字符串

dmesg                            # 内核环形缓冲区（启动日志）
dmesg | grep -i error            # 查找错误
dmesg | grep -i "I/O error"      # I/O 错误
dmesg -T                         # 加人类可读时间
journalctl -k                    # 用 systemd 看内核日志

# ===== 硬件 =====
lspci                            # PCI 设备
lspci -k                         # PCI + 内核驱动
lspci -vv                        # 详细 PCI 信息
lsusb                            # USB 设备
lsusb -t                         # USB 树状
lshw                             # 完整硬件信息（需安装）
lshw -short                      # 摘要
hwinfo --short                   # 另一个硬件信息工具
dmidecode                        # DMI/SMBIOS 信息（BIOS/主板/内存）
dmidecode -t memory              # 内存信息
dmidecode -t processor           # CPU 信息
```

### 10.3 日志查看

#### journalctl（systemd 日志）

```bash
# 基本查看
journalctl                       # 所有日志
journalctl -k                    # 仅内核日志（= dmesg）
journalctl -u nginx              # 按服务
journalctl -u nginx -u sshd      # 多个服务

# 实时跟踪
journalctl -f                    # 跟踪所有日志
journalctl -u nginx -f           # 跟踪某个服务

# 时间过滤
journalctl --since "2024-01-01"
journalctl --since "2024-01-01 10:00" --until "2024-01-01 12:00"
journalctl --since "1 hour ago"
journalctl --since today
journalctl --since yesterday
journalctl --boot                # 本次启动以来
journalctl -b                    # 同上
journalctl -b -1                 # 上一次启动
journalctl --list-boots          # 列出所有启动记录

# 优先级过滤
# 0=emerg 1=alert 2=crit 3=err 4=warning 5=notice 6=info 7=debug
journalctl -p err
journalctl -p warning..err       # 范围

# 按字段过滤
journalctl _PID=1234
journalctl _UID=0                # root 的日志
journalctl _COMM=sshd
journalctl SYSLOG_FACILITY=auth  # 认证日志

# 输出格式
journalctl -o short              # 默认
journalctl -o verbose            # 详细
journalctl -o json               # JSON 格式
journalctl -o cat                # 只显示消息

# 磁盘占用
journalctl --disk-usage          # 日志占用空间
journalctl --vacuum-size=100M    # 减少到 100MB
journalctl --vacuum-time=30d     # 保留 30 天
```

#### 传统日志文件位置

| 日志文件 | 内容 | 发行版 |
|---------|------|--------|
| `/var/log/syslog` | 系统日志 | Debian/Ubuntu |
| `/var/log/messages` | 系统日志 | RHEL/CentOS |
| `/var/log/auth.log` | 认证/授权日志 | Debian/Ubuntu |
| `/var/log/secure` | 安全/认证日志 | RHEL/CentOS |
| `/var/log/kern.log` | 内核日志 | Debian/Ubuntu |
| `/var/log/cron` | cron 任务日志 | 通用 |
| `/var/log/audit/audit.log` | 审计日志（auditd） | 通用 |
| `/var/log/boot.log` | 启动日志 | 通用 |
| `/var/log/dmesg` | 内核启动日志 | 通用 |
| `/var/log/apt/history.log` | apt 操作记录 | Debian/Ubuntu |
| `/var/log/yum.log` | yum 操作记录 | RHEL/CentOS |
| `/var/log/nginx/` | Nginx 日志 | 通用 |
| `/var/log/httpd/` | Apache 日志 | RHEL/CentOS |
| `/var/log/apache2/` | Apache 日志 | Debian/Ubuntu |

---

## 十一、服务与 systemd

### 11.1 systemctl — 服务管理

```bash
# ===== 查看状态 =====
systemctl status nginx           # 服务详细状态
systemctl is-active nginx        # 是否活动
systemctl is-enabled nginx       # 是否开机自启
systemctl is-failed nginx        # 是否失败

# ===== 启动/停止/重启 =====
systemctl start nginx            # 启动
systemctl stop nginx             # 停止
systemctl restart nginx          # 重启
systemctl reload nginx           # 重新加载配置（不中断）
systemctl try-restart nginx      # 服务在运行才重启

# ===== 开机自启 =====
systemctl enable nginx           # 设为开机自启
systemctl disable nginx          # 禁用开机自启
systemctl reenable nginx         # 重新启用（重置符号链接）
systemctl is-enabled nginx       # 查看是否启用

# ===== 查看服务列表 =====
systemctl list-units --type=service          # 已加载的服务
systemctl list-unit-files --type=service     # 所有服务（含已禁用）
systemctl list-units --type=service --all    # 所有服务
systemctl --failed                           # 失败的服务
systemctl list-units --type=service --state=running  # 正在运行的

# ===== 查看依赖 =====
systemctl list-dependencies nginx
systemctl list-dependencies --reverse nginx   # 反向依赖（谁依赖它）

# ===== 配置与加载 =====
systemctl daemon-reload            # 重新加载所有 unit 文件
systemctl daemon-reexec             # 重新执行 systemd 管理器

# ===== 系统管理 =====
systemctl reboot                   # 重启
systemctl poweroff                 # 关机
systemctl suspend                  # 挂起到内存
systemctl hibernate                # 休眠到磁盘
systemctl rescue                   # 救援模式
systemctl emergency                # 紧急模式
systemctl default                  # 回到默认模式

# ===== Target（运行级别） =====
systemctl get-default              # 查看默认 target
systemctl set-default multi-user.target     # 设置为文本模式
systemctl set-default graphical.target      # 设置为图形模式
systemctl isolate multi-user.target         # 切换到文本模式
```

### 11.2 journalctl — 日志查看（见第十章）

### 11.3 service 命令（传统）

```bash
# 兼容 SysV init 的命令
service nginx status
service nginx start
service nginx stop
service nginx restart
service nginx reload

# 查看所有服务
service --status-all

# chkconfig（RHEL 系旧命令）
chkconfig --list
chkconfig nginx on
chkconfig nginx off
chkconfig nginx --level 35 on

# update-rc.d（Debian 系旧命令）
update-rc.d nginx defaults
update-rc.d nginx remove
```

---

## 十二、开发与调试

### 12.1 编译与构建

```bash
# ===== gcc：GNU C 编译器 =====
gcc hello.c -o hello             # 编译为可执行文件
gcc -o hello hello.c             # 同上
gcc -Wall hello.c -o hello       # 显示所有警告
gcc -Werror hello.c -o hello     # 警告当错误
gcc -g hello.c -o hello          # 包含调试信息（gdb 用）
gcc -O2 hello.c -o hello         # 优化等级 2
gcc -std=c99 hello.c -o hello    # 指定 C 标准
gcc hello.c -lm -o hello         # 链接数学库
gcc -I /usr/include/mylib -L /usr/lib/mylib -lmylib hello.c -o hello

# ===== make =====
make                             # 构建默认目标
make target                      # 构建指定目标
make -j 4                        # 4 线程并行构建
make clean                       # 清理构建产物
make install                     # 安装
make -n                          # 试运行（只打印不执行）

# ===== gdb：调试器 =====
gdb ./program                    # 启动调试
gdb -p 1234                     # 附加到运行中进程🔑

# gdb 常用命令：
#   l / list           列出源码
#   b / break          设断点（b main / b file.c:10 / b *0x400100）
#   r / run            运行
#   c / continue       继续
#   n / next           下一步（不进入函数）
#   s / step           下一步（进入函数）
#   p / print          打印变量
#   bt / backtrace     调用栈
#   info registers     寄存器
#   x /10x $rsp        查看内存
#   q / quit           退出
```

### 12.2 系统调用/库跟踪

```bash
# ===== strace：跟踪系统调用 =====
strace ./program                 # 跟踪程序的所有系统调用
strace -p 1234                   # 附加到运行中进程🔑
strace -c ./program              # 统计各系统调用次数和时间
strace -e open,read ./program    # 只跟踪 open 和 read
strace -e trace=file ./program   # 跟踪所有文件相关系统调用
strace -e trace=network ./program  # 跟踪网络相关
strace -o trace.log ./program    # 输出到文件
strace -f ./program              # 跟踪子进程
strace -T ./program              # 显示每次调用耗时
strace -s 256 ./program          # 字符串显示长度

# ===== ltrace：跟踪库调用 =====
ltrace ./program                # 跟踪库函数调用
ltrace -p 1234                  # 附加到进程🔑
ltrace -c ./program             # 统计
ltrace -e malloc,free ./program # 只跟踪 malloc 和 free

# ===== ldd：查看动态库依赖 =====
ldd ./program                   # 程序依赖的共享库
ldd -v ./program                # 详细信息（含版本）
ldd -u ./program                # 未使用的依赖
```

---

## 附：优化后的提示词模板

以下是可复用的命令速查类知识查询提示词模板：

```markdown
# 角色
你是一名资深【系统/平台】专家，精通命令行、参数、案例、自动化与安全加固，
擅长按功能分类讲解命令。

# 任务
请系统介绍【平台/系统】的核心命令、参数与调用案例。

重要说明：命令数量庞大，无法全部穷举。请按功能分类列出核心命令，
并给出代表性案例。

内容分类（根据主题调整）：
1. 文件与目录操作
2. 文本处理（grep/sed/awk 等重点命令详解）
3. 查找与搜索
4. 进程与作业控制（含信号说明）
5. 用户与权限
6. 网络（配置/测试/抓包/远程/防火墙）
7. 磁盘与文件系统
8. 压缩与归档
9. 包管理（主流发行版对比）
10. 系统监控与日志
11. 服务管理
12. 开发与调试

# 输出要求
- 使用 Markdown
- 按大类、小类组织
- 关键内容用表格对比
- 每个命令附：语法、核心参数、至少一个调用案例
- 命令示例必须准确、可执行、可复制
- 重要术语中英文对照
- 面向：【系统管理员 + 运维工程师 + 安全工程师】
- 深度：操作参考 + 案例实战 + 安全加固
- 示例标注适用发行版/版本

# 约束
- 不声称列出全部命令，改为"核心命令 + 功能分类 + 代表性案例"
- 命令示例必须准确
- 高风险命令给出警告（rm -rf、dd、mkfs、kill -9、chmod 777 等）
- 对需要管理员/root 权限的命令进行标注
- 对可能影响系统稳定性的命令提示备份与测试环境验证
- 最后附"优化后的提示词模板"
```

**使用说明**：将【系统/平台】替换为"macOS""FreeBSD"等，或调整命令分类方向（如"网络命令专题""安全审计命令专题"），即可生成同等深度的命令速查文档。

---

> **总结**：Linux 命令虽多，但核心命令不过百余个。掌握文件与目录操作、文本处理三件套（grep/sed/awk）、进程与网络监控、用户权限管理、磁盘与包管理，再加上 systemd 服务和日志，就能胜任大部分日常运维工作。记住：命令不在多而在精，理解原理 + 熟练核心工具 + 知道查 man 手册的方法 > 死记硬背所有命令。
