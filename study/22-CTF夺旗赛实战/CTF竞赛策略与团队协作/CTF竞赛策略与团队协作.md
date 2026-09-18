# CTF竞赛策略与团队协作

> 本文档对应审计报告模块22缺口，系统讲解CTF竞赛的竞赛模式、策略方法、团队分工、赛前准备、赛中技巧、赛后复盘与实战经验，旨在帮助CTF选手从个人技能提升走向团队协作竞技。

---

## 1. CTF竞赛模式详解

### 1.1 解题模式（Jeopardy）

解题模式是最常见的CTF竞赛形式，以一系列独立的安全挑战题目组成，选手通过解题获取flag。

**规则与特点：**

- 题目按方向分类：Web、Pwn、Reverse、Crypto、Misc、Forensics
- 每题有固定分值，通常按难度分低/中/高三档
- 首次解出（First Blood / 一血）通常有额外加分
- 题目可能有动态分值（解题人数越多分值越低）
- 比赛时长通常24-48小时
- 允许组队参赛（通常3-5人）
- 排名按总积分排序

**动态分值计算公式（常见）：**

```
Score = max_points × (1 - (solve_count / total_teams) × decay_rate)
```

例如：初始500分，每有1%的队伍解出，分值下降5分，最低100分。

**解题模式特点总结：**

| 优点 | 缺点 |
|------|------|
| 适合大规模参赛 | 缺乏实时对抗感 |
| 题目覆盖面广 | 偏重个人能力 |
| 参赛门槛较低 | 时间管理要求高 |
| 公平性较好 | 高分题差异不大 |

### 1.2 攻防模式（Attack-Defense）

攻防模式是最激烈的CTF竞赛形式，每支队伍同时运行相同的一组服务，既要攻击其他队伍获取flag，又要防守自己的服务。

**规则与策略：**

- 每队获得相同的一组服务（通常4-8个）
- 每个服务有一个或多个flag，flag定期轮换（通常每5-10分钟）
- 攻击：利用漏洞攻入对方服务，读取flag并提交到评分系统得分
- 防守：修补自己服务的漏洞，防止被攻击
- 运维：保持服务可用性，服务不可用会被扣分

**攻防模式计分体系：**

```
每轮得分 = 攻击得分 - 防守失分 - 运维扣分

攻击得分 = 成功攻击队伍数 × 单次攻击分值
防守失分 = 被攻击成功次数 × 单次被攻分值
运维扣分 = 服务不可用时间 × 扣分率
```

**攻防模式特点：**

| 优点 | 缺点 |
|------|------|
| 实时对抗激烈 | 需要全面能力 |
| 综合考察安全技能 | 服务器运维压力大 |
| 考验团队配合 | 参赛门槛高 |
| 观赏性强 | 0day策略可能决定胜负 |

### 1.3 King of the Hill（KotH）模式

KotH模式是一种持续的攻防对抗，目标是控制目标机器并保持控制时间最长。

**规则与特点：**

- 比赛中有一台或多台目标机器
- 各队通过攻击获取目标机器的控制权
- 控制方在机器上放置自己的flag（"占领"机器）
- 占领时间越长得分越高
- 其他队伍可以攻击占领者夺取控制权
- 通常是2-8小时的短时竞赛

**KotH策略要点：**
- 快速攻入是第一步（速度优先）
- 加固防守保住阵地是第二步（持久化优先）
- 持续监控入侵者是第三步（检测优先）
- 准备反制手段是第四步（对抗优先）

### 1.4 解题+攻防混合模式

越来越多的比赛采用混合模式，先通过解题阶段筛选，再进入攻防阶段决赛。

**典型混合赛制：**

```
预赛（线上解题） → 选拔TOP N队伍
    ↓
半决赛（线上攻防） → 选拔TOP M队伍
    ↓
决赛（线下攻防） → 最终排名
```

**混合模式的优势：**
- 解题阶段考察面广，攻防阶段考察深度
- 降低了纯攻防模式中0day决定一切的不确定性
- 更全面地评估队伍综合实力

---

## 2. 解题模式比赛策略

### 2.1 比赛前期准备

**赛前1小时Checklist：**

- [ ] 确认比赛平台可访问，账号可登录
- [ ] 测试网络连接和VPN（如需）
- [ ] 准备好工具库（Burp Suite、IDA、GDB、pwntools等）
- [ ] 确认环境配置（Python版本、依赖包、Docker镜像）
- [ ] 建立团队沟通群组（Discord/Slack/微信）
- [ ] 约定flag提交规则（谁提交、怎么记录）
- [ | 约定信息共享方式（共享文档/频道分工）
- [ ] 安排休息轮班计划（24小时以上比赛）
- [ ] 准备食物和饮料
- [ ] 确认比赛规则（特别是动态分值、一血规则）

### 2.2 选题策略

**选题优先级决策矩阵：**

| 因素 | 权重 | 说明 |
|------|------|------|
| 难度/分值比 | 30% | 优先解分值高且难度适中的题 |
| 团队擅长方向 | 25% | 优先选择团队强项方向 |
| 解题人数 | 20% | 动态分值题参考解题人数 |
| 题目新颖度 | 15% | 新颖题目可能一战封神 |
| 一血可能性 | 10% | 首解有额外加分 |

**选题流程建议：**

1. **开局扫描（5-10分钟）**：快速浏览所有题目，建立初步印象。
2. **分方向领取（5-15分钟）**：各方向负责人领取自己擅长的题目。
3. **快速试做（15-30分钟）**：每人快速尝试1-2题，评估难度。
4. **动态调整**：根据试做结果调整选题，难则换题，易则深攻。
5. **灵活流转**：卡题超过30分钟考虑流转给其他队员或暂时搁置。

### 2.3 时间管理与优先级排序

**24小时比赛时间规划参考：**

| 时间段 | 任务 | 目标 |
|--------|------|------|
| 0:00-0:30 | 全题扫描+选题分配 | 建立全局认知 |
| 0:30-3:00 | Easy题集中攻克 | 快速积累基础分 |
| 3:00-8:00 | Medium题攻克 | 稳步提分 |
| 8:00-8:30 | 中场休息+策略调整 | 评估进度，调整方向 |
| 8:30-14:00 | Hard题攻坚+中难题补漏 | 冲刺中高难度 |
| 14:00-18:00 | 难题突破+团队协作解题 | 协同攻关最难题目 |
| 18:00-20:00 | 查漏补缺+放弃题目确认 | 确认可放弃的题目 |
| 20:00-23:00 | 最后冲刺+高分题攻坚 | 最大化得分 |
| 23:00-24:00 | 最终检查+flag提交确认 | 确保所有flag已提交 |

### 2.4 解题流程

**标准解题流程（5步法）：**

```
读题 → 分析 → 利用 → 验证 → 提交

1. 读题：仔细阅读题目描述，提取关键信息
   - 查看附件（源码、二进制、流量包）
   - 查看提示（Hint）
   - 查看题目类型和分值

2. 分析：分析漏洞/加密/逆向逻辑
   - 确定攻击面（Web:参数/头部/Payload; Pwn:溢出/格式化字符串/堆; Crypto:算法/密钥/模式）
   - 编写分析笔记，记录关键发现

3. 利用：编写Exploit/解密脚本
   - 快速原型 → 验证可行性
   - 完善脚本 → 获取flag

4. 验证：确认flag格式正确
   - 检查flag格式（如flag{...}, CTF{...}）
   - 本地验证（如Pwn题先本地测试）

5. 提交：提交flag到评分系统
   - 确认提交结果
   - 记录到团队共享文档
```

### 2.5 卡题时的应对策略

**卡题应对决策树：**

```
卡题超过30分钟
    │
    ├─ 有思路但实现困难 → 请队友协助
    │
    ├─ 有思路但工具限制 → 搜索替代方案/工具
    │
    ├─ 无思路 → 
    │    ├─ 查看是否有Hint → 使用Hint
    │    ├─ 查看解题人数 → 
    │    │    ├─ 很多人解出 → 重新审视，可能方向有误
    │    │    └─ 很少人解出 → 可能确实难，考虑放弃
    │    └─ 无Hint且少人解出 → 暂时搁置，转做其他题
    │
    └─ 卡题超过2小时 → 
         ├─ 做其他题目换换思路
         ├─ 在群里讨论（不泄露具体题目细节）
         └─ 最终决定是否放弃
```

### 2.6 比赛最后冲刺策略

**最后2小时冲刺策略：**

1. **清点未解题**：列出所有未解题及当前进度
2. **优先级重排**：选择最有可能在剩余时间内解决的题目
3. **团队集中**：将多人力集中到1-2道关键题上
4. **快速提交**：发现flag立即提交，不要等到"完美"再提交
5. **检查已提交**：确认所有已解题的flag都已正确提交
6. **利用Hint**：如果有剩余的Hint积分，最后时间大胆使用

---

## 3. 攻防模式比赛策略

### 3.1 攻防模式核心规则理解

**攻防模式关键规则要点：**

- **Flag轮换**：每轮（5-10分钟）flag自动更换，需重新攻击
- **攻击得分**：提交对方flag到评分系统得分
- **防守扣分**：自己服务的flag被读取会扣分
- **SLA扣分**：服务不可用（宕机/超时）会扣分
- **流量重放检测**：提交与上一轮相同的flag会被判定为重放，可能扣分
- **Patch提交**：部分比赛允许提交二进制Patch进行防守

### 3.2 防守策略

**防守优先级：**

```
1. 服务可用性（SLA） → 最高优先，不可用直接扣分
2. 漏洞修复（Patch） → 修补漏洞，阻止攻击
3. 入侵检测（IDS） → 发现谁在攻击自己
4. 流量分析 → 分析攻击Payload
5. 反制措施 → 主动阻断攻击者
```

**加固Checklist：**

- [ ] 比赛开始第一时间备份所有原始服务二进制和配置
- [ ] 为每个服务编写健康检查脚本
- [ ] 设置服务自动重启（systemd/Supervisor）
- [ ] 部署WAF规则（Web服务）
- [ ] 限制出站流量（防止flag外泄）
- [ ] 文件完整性监控（防止后门）
- [ ] 进程监控（防止未授权进程）
- [ ] 日志集中收集（方便分析攻击）

**Patch策略：**

```python
# 常见Patch方法
# 1. 二进制Patch（直接修改汇编指令）
#    - 将有漏洞的函数返回前加return
#    - 将危险的system()调用替换为exit()
#    - 修改条件跳转绕过漏洞路径

# 2. 配置加固
#    - 修改配置文件关闭危险功能
#    - 增加输入验证规则
#    - 设置访问控制列表

# 3. Wrapper脚本
#    - 用脚本包装原始服务，增加过滤层
#    #!/bin/bash
#    # wrapper.sh - 过滤危险输入
#    INPUT=$(cat)
#    if echo "$INPUT" | grep -q "rm\|cat flag\|/bin/sh"; then
#        exit 1
#    fi
#    echo "$INPUT" | ./original_service
```

### 3.3 攻击策略

**攻击自动化框架流程：**

```
1. 漏洞分析 → 确定漏洞类型和利用方法
2. Exploit编写 → 编写可重复利用的攻击脚本
3. 批量攻击 → 自动遍历所有对手IP进行攻击
4. Flag提取 → 自动从攻击结果中提取flag
5. Flag提交 → 自动提交到评分系统
6. 循环执行 → 每轮flag轮换后自动重新攻击
```

**攻击自动化脚本模板（Python）：**

```python
import requests
import re
from concurrent.futures import ThreadPoolExecutor

# 比赛配置
GAMEBOX_IPS = [f"10.10.{i}.1" for i in range(1, 100)]
SUBMIT_URL = "http://scoreboard.example.com/api/submit"
TEAM_TOKEN = "your_team_token"

def exploit(target_ip):
    """单个目标的攻击函数"""
    try:
        # 根据具体漏洞编写利用代码
        s = requests.Session()
        # 示例：SQL注入获取flag
        payload = "' UNION SELECT flag FROM flags--"
        r = s.post(f"http://{target_ip}/login", data={"user": payload})
        flag = re.search(r'flag\{[^}]+\}', r.text)
        return flag.group(0) if flag else None
    except Exception as e:
        return None

def submit_flag(flag):
    """提交flag到评分系统"""
    r = requests.post(SUBMIT_URL, json={
        "token": TEAM_TOKEN,
        "flag": flag
    })
    return r.json()

def main():
    while True:
        # 并发攻击所有目标
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = executor.map(exploit, GAMEBOX_IPS)
        
        # 提交所有获取到的flag
        for flag in results:
            if flag:
                result = submit_flag(flag)
                print(f"Submitted {flag}: {result}")
        
        # 等待下一轮
        import time
        time.sleep(60)  # 根据flag轮换周期调整

if __name__ == "__main__":
    main()
```

### 3.4 运维策略

**运维核心任务：**

| 任务 | 频率 | 优先级 | 工具 |
|------|------|--------|------|
| 服务健康检查 | 每轮 | 高 | 自定义脚本 |
| Flag提取（自己的flag） | 每轮 | 高 | 脚本自动提取 |
| 服务恢复 | 故障时 | 紧急 | 重启脚本/备份恢复 |
| Patch部署 | 发现漏洞时 | 高 | 自动化Patch脚本 |
| 流量监控 | 持续 | 中 | tcpdump/Wireshark |
| 日志分析 | 持续 | 中 | ELK/自定义脚本 |
| 对手IP收集 | 持续 | 中 | 攻击日志分析 |

**服务恢复脚本模板：**

```bash
#!/bin/bash
# service_monitor.sh - 服务监控与自动恢复

SERVICES=("service1" "service2" "service3")
CHECK_INTERVAL=10

while true; do
    for svc in "${SERVICES[@]}"; do
        if ! pgrep "$svc" > /dev/null; then
            echo "[$(date)] $svc is down, restarting..."
            cd /home/ctf/$svc
            ./start.sh &
            sleep 2
            if pgrep "$svc" > /dev/null; then
                echo "[$(date)] $svc restarted successfully"
            else
                echo "[$(date)] $svc restart failed!"
                # 尝试从备份恢复
                cp -r /backup/$svc/* .
                ./start.sh &
            fi
        fi
    done
    sleep $CHECK_INTERVAL
done
```

### 3.5 攻防平衡与资源分配

**人员分配建议（5人队伍）：**

| 角色 | 人数 | 核心任务 | 时间占比 |
|------|------|----------|----------|
| 攻击手 | 2 | 漏洞利用+Exploit编写+批量攻击 | 60%攻击/40%防守 |
| 防守手 | 1 | 漏洞修补+服务加固+入侵检测 | 80%防守/20%攻击 |
| 运维手 | 1 | 服务监控+恢复+流量分析 | 70%运维/30%防守 |
| 机动手 | 1 | 灵活支援攻击/防守/运维 | 动态分配 |

**攻防资源平衡原则：**
- 比赛前1/3时间：防守优先（确保SLA不丢分）
- 比赛中1/3时间：攻防平衡（防守稳定后加强攻击）
- 比赛后1/3时间：攻击优先（防守已稳定，全力冲刺攻击得分）

### 3.6 自动化框架搭建

**攻防自动化框架架构：**

```
┌─────────────────────────────────────┐
│          中央调度器（Master）        │
│  - 比赛状态监控（轮次/时间/排名）    │
│  - 任务调度与分配                    │
│  - 策略决策引擎                      │
└──────────┬──────────────────────────┘
           │
    ┌──────┼──────┐
    │      │      │
  攻击模块 防守模块 运维模块
  │  │  │   │  │   │  │
  Exploit Patch 监控
  模块 模块 模块
  │  │  │   │  │   │  │
  Flag 提交 告警
  提取 模块 分析
```

**框架核心功能Checklist：**

- [ ] 自动读取比赛轮次和时间
- [ ] 自动获取所有对手IP列表
- [ ] 并发执行攻击Exploit
- [ ] 自动提取并提交flag
- [ ] 自动监控服务健康状态
- [ ] 自动恢复故障服务
- [ ] 自动部署Patch
- [ ] 流量实时分析
- [ ] 攻击日志记录
- [ ] 排名实时跟踪
- [ ] Discord/Slack告警推送

---

## 4. 团队分工与协作

### 4.1 团队角色分配

**标准CTF战队角色配置（5人制）：**

| 角色 | 职责 | 核心技能 | 性格特质 |
|------|------|----------|----------|
| 队长/方向总协调 | 全局决策、方向分配、时间管理 | 全方向了解、沟通能力强 | 冷静、决断 |
| Web手 | Web安全题目 | SQL注入、XSS、SSRF、反序列化 | 细致、有耐心 |
| Pwn手 | 二进制利用 | 栈溢出、堆利用、格式化字符串 | 逻辑严密、抗压 |
| 逆向手 | 逆向工程 | IDA/Ghidra、汇编、脱壳 | 耐心、分析力强 |
| 密码学手 | 密码学题目 | RSA、AES、数论、格密码 | 数学功底好 |
| Misc手 | 杂项题目 | 流量分析、隐写、取证 | 知识面广、灵活 |

**角色分配原则：**
1. 每人至少精通1个方向，了解1-2个辅助方向
2. Web和Pwn是主力方向，确保2人以上
3. 密码学和Misc可由其他方向兼任
4. 队长不一定是最强的选手，但必须是最了解团队的人
5. 赛前明确每个人的主攻和辅攻方向

### 4.2 各方向的协作流程

**协作场景示例：**

**场景1：Web+Pwn协作**
```
Web手发现Web服务有命令执行漏洞 → 
执行命令发现后端有二进制服务 → 
将二进制交给Pwn手分析 → 
Pwn手发现堆溢出漏洞 → 
Web手通过Web接口触发Pwn利用 → 
联合获取flag
```

**场景2：逆向+密码学协作**
```
逆向手分析加密程序 → 
发现使用自定义加密算法 → 
提取加密逻辑和密钥 → 
密码学手分析算法弱点 → 
编写解密脚本 → 
获取flag
```

**场景3：Misc+Forensics协作**
```
Misc手分析流量包 → 
发现加密通信 → 
提取密文和密钥交换数据 → 
密码学手解密通信内容 → 
获取flag
```

### 4.3 信息共享机制

**信息共享平台配置：**

| 共享内容 | 工具 | 说明 |
|----------|------|------|
| Flag记录 | 共享文档（腾讯文档/飞书） | 实时更新已获取的flag |
| 漏洞分析 | 团队Wiki（GitLab Wiki） | 记录漏洞分析和利用方法 |
| 工具脚本 | Git仓库 | 共享Exploit脚本和工具 |
| 实时沟通 | Discord/Slack | 按方向分频道，实时讨论 |
| 截图共享 | 共享相册/网盘 | 分享题目界面和分析截图 |
| 环境配置 | Docker镜像仓库 | 共享解题环境 |

**Flag共享文档模板：**

```
| 题目 | 分值 | 方向 | 状态 | Flag | 解题人 | 备注 |
|------|------|------|------|------|--------|------|
| Web1 | 100 | Web | 已解 | flag{xxx} | 张三 | SQL注入 |
| Pwn2 | 300 | Pwn | 已解 | flag{yyy} | 李四 | 堆溢出 |
| Crypto1| 200 | Crypto | 攻坚中 | - | 王五 | RSA |
| Misc3 | 150 | Misc | 未开始 | - | - | - |
```

### 4.4 比赛中沟通工具与平台

**推荐沟通工具栈：**

```
实时沟通层：Discord（分频道）
    ├─ #general（通用讨论）
    ├─ #web（Web方向）
    ├─ #pwn（Pwn方向）
    ├─ #crypto（密码学）
    ├─ #misc（杂项）
    ├─ #reverse（逆向）
    ├─ #flags（flag记录）
    └─ #alert（紧急通知）

信息共享层：腾讯文档/飞书文档
    ├─ Flag追踪表
    ├─ 题目分析笔记
    └─ 时间规划表

代码共享层：GitHub/GitLab私有仓库
    ├─ exploit/（攻击脚本）
    ├─ tools/（通用工具）
    └─ writeup/（解题报告）

文件共享层：网盘/共享文件夹
    ├─ 题目附件
    ├─ 分析截图
    └─ 环境镜像
```

### 4.5 团队规模与方向配置建议

**不同规模的团队配置：**

| 团队规模 | 方向配置 | 策略建议 |
|----------|----------|----------|
| 1-2人（个人/小队） | 全能型 | 放弃高难度题目，专攻Easy+Medium |
| 3人 | Web+Pwn+Misc | 覆盖3大方向，放弃1-2个方向 |
| 4-5人 | Web×2+Pwn+Crypto+Misc | 标准配置，覆盖全方向 |
| 6-8人 | 每方向1-2人 | 充分覆盖，深度并行 |
| 10人+ | 每方向2人+1协调 | 大队作战，注意协调成本 |

---

## 5. 赛前准备

### 5.1 知识储备与技能树

**CTF技能树总览：**

```
CTF技能树
├── Web安全
│   ├── SQL注入（联合/盲注/堆叠/二次）
│   ├── XSS（反射/存储/DOM）
│   ├── SSRF（基础/进阶/利用链）
│   ├── 文件上传/下载/包含
│   ├── 反序列化（PHP/Java/Python）
│   ├── 模板注入（SSTI）
│   └── 命令注入/代码执行
├── 二进制安全（Pwn）
│   ├── 栈溢出（ret2text/ret2shellcode/ret2libc）
│   ├── 格式化字符串
│   ├── 堆利用（fastbin/tcache/unsorted bin）
│   ├── 整数溢出
│   ├── 沙箱逃逸（seccomp）
│   └── 内核利用（Kernel Pwn）
├── 逆向工程
│   ├── 静态分析（IDA/Ghidra）
│   ├── 动态调试（GDB/x64dbg）
│   ├── 反混淆/脱壳
│   ├── VM逆向
│   └── Android/iOS逆向
├── 密码学
│   ├── 古典密码
│   ├── RSA（共模/低指数/Wiener/Coppersmith）
│   ├── AES（ECB/CBC/Padding Oracle）
│   ├── 椭圆曲线（ECC）
│   ├── 格密码（LLL/BJLK）
│   └── 哈希碰撞
└── 杂项（Misc）
    ├── 流量分析（PCAP/Wireshark）
    ├── 隐写术（图片/音频/视频/文档）
    ├── 取证（磁盘/内存/注册表）
    ├── 编码解码（Base/Hex/XXencode/UUencode）
    └── 脑洞题
```

### 5.2 工具库搭建

**工具库分类清单：**

**Web工具：**
```
- Burp Suite Pro（代理/扫描/Intruder）
- sqlmap（SQL注入自动化）
- dirsearch/gobuster（目录扫描）
- nuclei（漏洞模板扫描）
- CyberChef（编码解码全能工具）
- Browser DevTools
- Postman（API测试）
```

**Pwn工具：**
```
- pwntools（Python利用框架）
- pwndbg/gef（GDB增强插件）
- ROPgadget（ROP链构造）
- one_gadget（libc one-shot gadget）
- LibcSearcher（libc版本识别）
- checksec（安全机制检查）
- angr（符号执行框架）
```

**逆向工具：**
```
- IDA Pro / Ghidra（反编译）
- x64dbg / OllyDbg（Windows调试）
- gdb（Linux调试）
- z3（SMT求解器）
- uncompyle6（Python反编译）
- jadx（Java/Android反编译）
- upx（脱壳工具）
```

**密码学工具：**
```
- SageMath（数学计算环境）
- pycryptodome（Python加密库）
- RsaCtfTool（RSA攻击工具集）
- yafu（大数分解）
- Hashcat/john（哈希破解）
- Cipher-identification（密码识别）
```

**Misc工具：**
```
- Wireshark/tshark（流量分析）
- binwalk（文件分析/提取）
- steghide/stegsolve（图片隐写）
- foremost/scalpel（文件恢复）
- Volatility（内存取证）
- Autopsy（磁盘取证）
- Audacity（音频分析）
- 010 Editor（十六进制编辑）
```

### 5.3 常用脚本与自动化工具

**通用解题脚本模板：**

```python
#!/usr/bin/env python3
# CTF通用解题模板
from pwn import *
import sys

def connect(target, port, mode='remote'):
    """连接目标"""
    if mode == 'remote':
        return remote(target, port)
    elif mode == 'local':
        return process('./target')
    
def solve():
    """解题逻辑"""
    # 1. 连接
    io = connect('target.com', 9999)
    
    # 2. 交互
    io.sendlineafter(b'> ', b'payload')
    
    # 3. 获取flag
    flag = io.recvline()
    print(f"Flag: {flag}")
    
    io.close()

if __name__ == '__main__':
    solve()
```

### 5.4 Docker化环境准备

**赛前Docker环境模板：**

```dockerfile
# Dockerfile - CTF解题环境
FROM ubuntu:22.04

# 基础工具
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    gdb gdb-multiarch \
    git wget curl vim \
    lib32z1 libc6-dev-i386 \
    && rm -rf /var/lib/apt/lists/*

# Python工具
RUN pip3 install \
    pwntools \
    pycryptodome \
    requests \
    beautifulsoup4 \
    angr \
    z3-solver

# 逆向工具
RUN apt-get update && apt-get install -y \
    radare2 \
    && rm -rf /var/lib/apt/lists/*

# 工作目录
WORKDIR /ctf
VOLUME ["/ctf"]

# GDB配置
COPY .gdbinit /root/.gdbinit

CMD ["/bin/bash"]
```

**环境管理脚本：**

```bash
#!/bin/bash
# ctf_env.sh - CTF环境快速启动
docker run -it --rm \
  -v $(pwd):/ctf \
  -v /tmp/ctf_tools:/tools \
  --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  ctf-solver:latest
```

### 5.5 赛前模拟训练方法

**模拟训练计划：**

1. **历史赛题训练**：选取过去3个月的CTF赛题，限时模拟
2. **团队内部赛**：由队员出题，组织内部对抗
3. **攻防模拟**：搭建靶场，模拟攻防模式比赛
4. **限时训练**：设定2小时，从零开始解题，锻炼速度
5. **复盘分析**：每周复盘，分析失误和提升点

### 5.6 赛前一月训练计划

**赛前一个月训练安排：**

| 周次 | 训练内容 | 目标 | 每日时长 |
|------|----------|------|----------|
| 第1周 | 各方向基础巩固 | 确保基础题无障碍 | 3-4小时 |
| 第2周 | 中等难度赛题练习 | 提升Medium题通过率 | 3-4小时 |
| 第3周 | 高难度赛题+团队协作模拟 | 提升Hard题能力和团队配合 | 4-5小时 |
| 第4周 | 模拟赛+工具检查+环境部署 | 全面模拟，查漏补缺 | 模拟赛+3小时 |

**赛前一周Daily Plan：**

```
Day -7: 全队模拟赛（历史赛题，8小时）
Day -6: 模拟赛复盘 + 各方向查漏补缺
Day -5: 工具库检查 + 环境部署验证
Day -4: 各方向薄弱点专项突破
Day -3: 团队协作流程演练
Day -2: 轻度练习 + 策略讨论 + 休息
Day -1: 环境最终检查 + 比赛规则确认 + 充足休息
```

---

## 6. 赛中工具与技巧

### 6.1 比赛平台使用技巧

**常见平台操作技巧：**

- 使用浏览器多标签页，每个题目一个标签
- 利用平台Hint系统（如果有的话），低成本获取关键信息
- 注意查看平台公告（题目修正/补充说明）
- 关注排行榜变化，了解其他队伍解题进度
- 注意比赛剩余时间，合理安排冲刺

### 6.2 解题工具快速调用

**一键启动工具脚本：**

```bash
#!/bin/bash
# ctf_quick_start.sh - 一键启动CTF工具集
echo "Starting CTF tool environment..."

# 启动Burp Suite
burpsuite &

# 启动浏览器（代理配置好）
firefox --proxy-server="127.0.0.1:8080" &

# 启动Docker解题环境
docker start ctf-solver

# 启动Wireshark
wireshark &

# 启动Python交互环境
cd /ctf && python3 -i -c "from pwn import *; context.log_level='debug'"

echo "All tools started. Good luck!"
```

### 6.3 自动化flag提交脚本

**通用flag提交脚本：**

```python
#!/usr/bin/env python3
"""自动flag提交脚本"""
import requests
import sys
import re

class CTFSubmit:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def submit(self, flag, challenge_id=None):
        """提交flag"""
        data = {"flag": flag}
        if challenge_id:
            data["challenge_id"] = challenge_id
        
        r = self.session.post(f"{self.base_url}/api/submit", json=data)
        result = r.json()
        
        if result.get("correct"):
            print(f"[+] CORRECT! Flag: {flag}")
        else:
            print(f"[-] WRONG. Flag: {flag}")
            print(f"    Response: {result}")
        
        return result
    
    def batch_submit(self, flags):
        """批量提交"""
        for flag in flags:
            self.submit(flag)

# 使用示例
if __name__ == "__main__":
    ctf = CTFSubmit(
        base_url="https://ctf.example.com",
        token="your_token_here"
    )
    
    # 从命令行参数获取flag
    if len(sys.argv) > 1:
        flag = sys.argv[1]
        ctf.submit(flag)
    else:
        # 从剪贴板获取
        import subprocess
        flag = subprocess.check_output(["xclip", "-o"]).decode().strip()
        if re.match(r'flag\{[^}]+\}', flag):
            ctf.submit(flag)
```

### 6.4 攻防模式自动化框架

**攻防自动化框架核心代码：**

```python
#!/usr/bin/env python3
"""
Attack-Defense CTF Automation Framework
"""
import threading
import time
import subprocess
import requests
from typing import List, Optional

class ADCTFFramework:
    def __init__(self, config):
        self.game_api = config['game_api']
        self.team_token = config['team_token']
        self.flag_pattern = config.get('flag_pattern', r'flag\{[^}]+\}')
        self.attack_interval = config.get('attack_interval', 30)
        self.targets = []
        self.attacks = {}  # exploit_id -> exploit_func
        self.running = False
    
    def register_attack(self, name, func):
        """注册攻击模块"""
        self.attacks[name] = func
    
    def get_targets(self):
        """获取所有对手IP"""
        r = requests.get(f"{self.game_api}/targets",
                         headers={"X-Team-Token": self.team_token})
        self.targets = r.json().get('targets', [])
        return self.targets
    
    def submit_flag(self, flag):
        """提交flag"""
        r = requests.post(f"{self.game_api}/submit",
                         headers={"X-Team-Token": self.team_token},
                         json={"flag": flag})
        return r.json()
    
    def attack_loop(self):
        """攻击循环"""
        while self.running:
            targets = self.get_targets()
            for target in targets:
                for name, exploit_func in self.attacks.items():
                    try:
                        result = exploit_func(target)
                        if result:
                            import re
                            flags = re.findall(self.flag_pattern, result)
                            for flag in flags:
                                res = self.submit_flag(flag)
                                print(f"[{name}] {target}: {flag} -> {res}")
                    except Exception as e:
                        print(f"[{name}] {target}: Error - {e}")
            time.sleep(self.attack_interval)
    
    def start(self):
        """启动框架"""
        self.running = True
        # 启动攻击线程
        attack_thread = threading.Thread(target=self.attack_loop)
        attack_thread.daemon = True
        attack_thread.start()
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=self.monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("Framework started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            print("Framework stopped.")
    
    def monitor_loop(self):
        """监控循环"""
        while self.running:
            # 检查服务健康状态
            # 检查排名变化
            # 发送Discord通知
            time.sleep(10)

# 使用示例
if __name__ == "__main__":
    config = {
        'game_api': 'https://adctf.example.com/api',
        'team_token': 'YOUR_TOKEN',
        'attack_interval': 30,
    }
    
    framework = ADCTFFramework(config)
    
    # 注册攻击模块
    def exploit_web(target):
        import requests
        r = requests.get(f"http://{target}/api/debug")
        return r.text
    
    def exploit_pwn(target):
        from pwn import *
        io = remote(target, 9999)
        io.sendline(b'overflow_payload')
        return io.recvall().decode()
    
    framework.register_attack("web_debug", exploit_web)
    framework.register_attack("pwn_overflow", exploit_pwn)
    
    framework.start()
```

### 6.5 流量分析与攻防情报

**攻防模式流量分析策略：**

```python
#!/usr/bin/env python3
"""
攻防模式流量分析工具
- 捕获自己服务的流量
- 分析对手攻击Payload
- 提取对手Exploit特征
- 自动生成防御规则
"""
from scapy.all import *
import re
from collections import defaultdict

class TrafficAnalyzer:
    def __init__(self, interface, flag_pattern=r'flag\{[^}]+\}'):
        self.interface = interface
        self.flag_pattern = flag_pattern
        self.attack_sources = defaultdict(list)
        self.payloads = []
    
    def analyze_packet(self, packet):
        """分析单个数据包"""
        if packet.haslayer(TCP) and packet.haslayer(Raw):
            payload = packet[Raw].load.decode('utf-8', errors='ignore')
            src_ip = packet[IP].src
            
            # 检测攻击特征
            attack_indicators = [
                (r"select.*from", "SQL注入"),
                (r"<script", "XSS"),
                (r"\.\.\/", "目录遍历"),
                (r"system\(|exec\(|eval\(", "命令执行"),
                (r"flag\{", "Flag泄露"),
                (r"/bin/sh|/bin/bash", "Shell执行"),
            ]
            
            for pattern, attack_type in attack_indicators:
                if re.search(pattern, payload, re.IGNORECASE):
                    self.attack_sources[src_ip].append({
                        'type': attack_type,
                        'payload': payload[:200],
                        'timestamp': packet.time
                    })
                    print(f"[!] {attack_type} from {src_ip}")
                    
                    # 提取攻击Payload供防守参考
                    self.payloads.append({
                        'src_ip': src_ip,
                        'type': attack_type,
                        'payload': payload
                    })
    
    def start(self):
        """开始抓包分析"""
        print(f"[*] Starting traffic analysis on {self.interface}")
        sniff(iface=self.interface, prn=self.analyze_packet, store=0)
    
    def get_attack_summary(self):
        """获取攻击摘要"""
        for ip, attacks in self.attack_sources.items():
            print(f"\n{ip}: {len(attacks)} attacks")
            for a in attacks:
                print(f"  - {a['type']}: {a['payload'][:50]}...")
```

---

## 7. 赛后复盘与提升

### 7.1 Writeup撰写规范与方法

**Writeup标准结构：**

```
# [题目名称] Writeup

## 基本信息
- 比赛名称：
- 题目方向：
- 难度/分值：
- 解题人数：
- 解题用时：

## 题目描述
（题目原文+附件说明）

## 解题过程

### 步骤1：信息收集
- 描述观察到什么
- 描述初始分析过程

### 步骤2：漏洞/加密分析
- 详细描述漏洞原理或加密弱点
- 包含关键代码片段

### 步骤3：利用/解密
- 完整利用过程
- Exploit代码（完整可运行）

### 步骤4：获取Flag
- 最终flag

## 总结
- 知识点总结
- 可改进的地方
- 参考链接

## 完整代码
（完整可运行的脚本）
```

### 7.2 赛后复盘流程

**赛后复盘Checklist：**

- [ ] 收集所有题目的Writeup（已解和未解）
- [ ] 统计各方向解题率和得分占比
- [ ] 分析未解题目的原因（时间不够/能力不足/方向错误）
- [ ] 对比其他队伍的解题情况（特别是排名相近的队伍）
- [ ] 总结团队协作中的问题
- [ ] 评估工具库的有效性
- [ ] 制定改进计划
- [ ] 更新团队Wiki和工具库

### 7.3 知识沉淀与工具库更新

**知识沉淀体系：**

```
团队知识库
├── Writeup库
│   ├── 按比赛分类
│   └── 按方向分类
├── 技术笔记
│   ├── 漏洞利用技术
│   ├── 加密算法分析
│   └── 工具使用技巧
├── 工具库
│   ├── Exploit模板
│   ├── 自动化脚本
│   └── 环境镜像
├── 题目库
│   ├── 历年赛题
│   └── 分类标签
└── 团队SOP
    ├── 赛前准备流程
    ├── 赛中协作流程
    └── 赛后复盘流程
```

### 7.4 团队成长策略

**团队成长阶段规划：**

| 阶段 | 时间 | 目标 | 训练频率 |
|------|------|------|----------|
| 组建期 | 0-3月 | 建立基础能力，熟悉各方向 | 每周1-2次练习 |
| 成长期 | 3-6月 | 中等难度题稳定通过，参加小型比赛 | 每周2-3次+月赛 |
| 成熟期 | 6-12月 | 高难度题突破，参加大型比赛 | 每周3次+双月大赛 |
| 精英期 | 12月+ | 国际赛事竞争，自研工具 | 持续训练+国际赛 |

### 7.5 持续学习资源

**推荐学习资源：**

| 类型 | 资源 | 说明 |
|------|------|------|
| 在线练习 | BUUCTF | 国内最大CTF练习平台 |
| 在线练习 | 攻防世界 | XCTF官方练习平台 |
| 在线练习 | CTFHub | 按技能树组织练习 |
| 在线练习 | Hacker101 CTF | HackerOne官方 |
| 视频教程 | B站CTF频道 | 中文教程资源 |
| 书籍 | 《CTF特训营》 | 国内权威CTF教材 |
| 书籍 | 《密码学CTF》 | 密码学方向专项 |
| 社区 | CTFtime.org | 全球CTF赛事与排名 |
| 社区 | 安全客/先知社区 | 技术文章与Writeup |

---

## 8. 常见CTF平台与赛事

### 8.1 国内CTF赛事

| 赛事 | 主办方 | 级别 | 特点 |
|------|--------|------|------|
| XCTF联赛 | XCTF社区 | 国际级 | 国内最高水平联赛 |
| 强网杯 | 信息工程大学 | 国家级 | 规模大，奖金高 |
| 网鼎杯 | 国家网信办 | 国家级 | 参赛队伍最多的赛事之一 |
| DEFCON CN | DEFCON | 国际级 | DEFCON中国分站 |
| 全国大学生安全竞赛（CISCN） | 教育部 | 国家级 | 高校最权威赛事 |
| 红明杯/西湖论剑 | 各安全公司 | 省级 | 区域性高水平赛事 |
| De1CTF/HCTF/0CTF | 各高校/战队 | 国际级 | 高校组织的高水平国际赛 |

### 8.2 国际CTF赛事

| 赛事 | 级别 | 特点 |
|------|------|------|
| DEF CON CTF | 最高级 | CTF界的"世界杯" |
| PlaidCTF | 最高级 | PPP战队主办，难度极高 |
| Google CTF | 高级 | Google主办，奖金丰厚 |
| HITCON CTF | 高级 | 台湾HITCON主办，Pwn难度大 |
| hxp CTF | 高级 | 德国战队主办 |
| SECCON CTF | 高级 | 日本最大CTF赛事 |
| Real World CTF | 高级 | 长亭科技主办，真实场景题 |
| 0CTF/TCTF | 高级 | 上海交大/腾讯合办 |

### 8.3 CTF平台

**练习平台对比：**

| 平台 | 题目量 | 方向覆盖 | 特点 | 费用 |
|------|--------|----------|------|------|
| BUUCTF | 2000+ | 全方向 | 题量大，分类清晰 | 免费 |
| 攻防世界 | 1500+ | 全方向 | XCTF官方 | 免费 |
| CTFHub | 800+ | 全方向 | 技能树体系 | 部分收费 |
| Hacker101 | 100+ | Web为主 | HackerOne官方 | 免费 |
| HackTheBox | 500+ | 渗透为主 | 偏实战渗透 | 部分收费 |
| picoCTF | 200+ | 入门级 | 适合初学者 | 免费 |
| Root-Me | 500+ | 全方向 | 法国平台，法语/英语 | 部分收费 |

### 8.4 赛事日历与参赛建议

**年度赛事时间参考：**

| 月份 | 赛事 | 建议 |
|------|------|------|
| 1-2月 | Real World CTF、picoCTF | 新年热身 |
| 3-4月 | XCTF分站赛、网鼎杯 | 春季赛事密集期 |
| 5-6月 | DEF CON CTF Quals、Google CTF | 国际顶级赛事 |
| 7-8月 | CISCN、强网杯 | 暑期国内大赛 |
| 9-10月 | HITCON CTF、HXP CTF | 秋季国际赛事 |
| 11-12月 | SECCON、年底总结 | 年终冲刺 |

**参赛建议：**
1. 每月至少参加1-2场比赛
2. 每季度参加1次大型比赛
3. 每年至少参加1次国际比赛
4. 优先参加有Writeup公开的比赛（学习价值高）
5. 国际赛事可作为衡量团队水平的标杆
6. 国内赛事可积累排名和知名度

---

## 9. 实战经验分享

### 经验1：解题模式逆转时间管理

**背景**：某次24小时解题模式CTF比赛中，某队伍在前18小时仅排名第15位，最终6小时逆转到第3名。

**策略复盘：**

**前18小时（排名15）的问题：**
- 一开始全员扎堆做Easy题，浪费了时间
- 中期分散做不同方向的Medium题，但都没有做完
- 缺乏全局时间管理，没有及时放弃难题

**后6小时（逆转到第3）的调整：**
1. **集中兵力**：全员放下手中题目，集中攻4道有思路但未做完的Medium题
2. **分工明确**：1人负责写Exploit，1人负责调试，1人负责查资料，1人负责测试flag
3. **快速迭代**：每题设定30分钟限时，到期换题
4. **利用Hint**：消耗所有Hint积分获取关键提示
5. **最后1小时**：全员检查flag提交情况，发现2个已解但未提交的flag

**关键经验：**
- 解题赛不要贪多，集中力量逐题攻克比分散并行更高效
- 最后阶段"清仓"策略（集中攻克所有有进展的题）效果显著
- flag提交管理不能疏忽，已解的flag必须立即提交
- 时间管理比单纯的技术能力更重要

### 经验2：攻防模式自动化框架搭建

**背景**：某攻防模式比赛中，一支5人队伍通过高效的自动化框架以50%的服务漏洞覆盖率实现了80%的攻击得分。

**框架搭建经验：**

**赛前准备阶段：**
1. 提前搭建了通用攻防框架（基于Python），包含攻击/防守/运维/监控四大模块
2. 编写了模块化的Exploit注册接口，新漏洞利用只需注册一个函数即可自动批量攻击
3. 部署了服务健康检查和自动恢复脚本
4. 配置了Discord告警，实时推送攻击成功/服务异常通知

**赛中操作：**
1. 比赛开始后10分钟内完成所有服务备份和健康检查部署
2. 第一个漏洞在30分钟内被分析完成，注册到框架，自动开始批量攻击
3. 后续每个新漏洞从分析到注册平均20分钟
4. 运维手全程监控系统状态，服务SLA达到99%+
5. 防守手通过分析对手攻击流量，3次发现0day并完成修补

**关键经验：**
- 自动化框架是攻防模式的胜负手，手动操作完全无法竞争
- 模块化设计是关键，新漏洞利用应该能"即插即用"
- 服务SLA管理容易被忽视但至关重要
- 流量分析是防守的"情报来源"，帮助发现未知漏洞
- 框架稳定性比功能丰富更重要，赛中崩溃是灾难性的

### 经验3：从0到1组建CTF战队

**背景**：一个零基础的大学生团队从组建到参加首个全国性CTF比赛的经历。

**组建过程：**

**第1阶段：人员招募（第1-2周）**
- 在校内技术社团发布招募信息
- 通过简单的入门题目筛选有基础的成员
- 最终招募到6人（2人有初级基础，4人零基础）

**第2阶段：基础培训（第3-8周）**
- 每周2次集中培训（Web基础、Linux基础、Python编程）
- 使用picoCTF作为入门练习平台
- 每人选择1-2个主攻方向开始深入学习
- 方向分配：Web×2、Pwn×1、Reverse×1、Crypto×1、Misc×1

**第3阶段：实战练习（第9-16周）**
- 开始做BUUCTF上的Easy题
- 每周组织内部模拟赛（2-4小时）
- 开始写Writeup，建立团队知识库
- 参加了2次小型线上CTF比赛（未上榜但积累了经验）

**第4阶段：首次大赛（第17-20周）**
- 报名参加CISCN（全国大学生信息安全竞赛）
- 赛前集中训练2周
- 比赛结果：解题3道（2 Easy + 1 Medium），排名200+/500
- 赛后全面复盘，记录了30+页的改进笔记

**关键经验：**
1. **零基础不是借口**：4个月内从零到参加全国赛是完全可行的
2. **方向分工要早**：越早确定每人主攻方向，学习越高效
3. **Writeup是最好的学习方式**：写Writeup比做题本身收获更大
4. **参加比赛是最好的训练**：比赛中的高压环境比日常练习提升更快
5. **不要怕输**：前几场比赛排名低是正常的，重在积累经验
6. **团队氛围是核心**：保持积极、互助、不抱怨的团队文化
7. **持续比爆发重要**：每周稳定训练2-3次比赛前突击更有效

---

## 总结

CTF竞赛是网络安全领域最有效的实践学习方式之一。它不仅是技能竞技的舞台，更是知识体系构建、团队协作锻炼、实战能力提升的综合训练场。

**CTF成长核心原则：**

1. **以赛代练**：参加比赛是最好的学习方式，不要等到"准备好"才参赛。
2. **深度复盘**：赛后Writeup和复盘比赛中解题更有价值。
3. **团队协作**：CTF是团队运动，个人能力有上限，团队协作无上限。
4. **工具自动化**：在攻防模式中，自动化能力决定了竞争力的上限。
5. **持续积累**：建立个人/团队的知识库和工具库，每次比赛都在上一次的基础上提升。
6. **享受过程**：CTF的乐趣在于解题的"顿悟"时刻和团队协作的默契感。

**行动Checklist：**

- [ ] 确定个人CTF主攻方向
- [ ] 在BUUCTF/攻防世界完成至少20道Easy题
- [ ] 组建或加入一支CTF战队
- [ ] 建立团队沟通和知识共享平台
- [ ] 搭建个人/团队工具库
- [ ] 参加至少1次线上CTF比赛
- [ ] 赛后撰写至少5篇Writeup
- [ ] 建立赛后复盘流程
- [ ] 制定年度参赛计划
- [ ] 持续更新知识库和工具库

> **核心理念**：CTF不是为了赢比赛，而是为了在竞技中成长为更强的安全从业者。每一道题、每一次比赛、每一次失败都是通向专业安全专家道路上的基石。坚持下去，你终将成为顶尖选手。
