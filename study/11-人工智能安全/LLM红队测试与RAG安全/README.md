# LLM红队测试与RAG安全

> 本文档整理自：`LLM红队测试与RAG安全.md`

---

## 目录

### [01. LLM 红队测试方法论](./01_LLM 红队测试方法论/LLM 红队测试方法论.md)
  - 为什么需要 LLM 红队测试
  - 测试目标
  - 测试维度
  - 评估指标

### [02. LLM 攻击技术分类](./02_LLM 攻击技术分类/LLM 攻击技术分类.md)
  - 提示注入
  - 越狱攻击
  - 幻觉利用
  - 数据投毒
  - 供应链攻击
  - 侧信道攻击

### [03. LLM 红队测试框架](./03_LLM 红队测试框架/LLM 红队测试框架.md)
  - PyRIT
  - Garak
  - Promptfoo

### [04. LLM 安全评估基准](./04_LLM 安全评估基准/LLM 安全评估基准.md)
  - HarmBench
  - AdvBench
  - JailbreakBench
  - 基准对比

### [05. RAG 安全概述](./05_RAG 安全概述/RAG 安全概述.md)
  - RAG 架构
  - RAG 安全挑战

### [06. RAG 攻击面](./06_RAG 攻击面/RAG 攻击面.md)
  - 知识库投毒
  - 检索劫持
  - 注入检索（间接注入）
  - 访问控制缺失

### [07. RAG 安全防护](./07_RAG 安全防护/RAG 安全防护.md)
  - 输入过滤
  - 检索验证
  - 输出审查
  - RAG 安全架构

### [08. LLM 安全防护体系](./08_LLM 安全防护体系/LLM 安全防护体系.md)
  - 输入过滤
  - 输出审查
  - RLHF 对齐
  - Constitutional AI
  - 系统提示加固

### [09. AI 安全监测与告警](./09_AI 安全监测与告警/AI 安全监测与告警.md)
  - 监测维度
  - 告警机制

### [10. 实战案例：LLM 应用红队测试全流程](./10_实战案例：LLM 应用红队测试全流程/实战案例：LLM 应用红队测试全流程.md)
  - 场景
  - 步骤1：资产梳理与威胁建模
  - 步骤2：自动化扫描
  - 步骤3：人工越狱测试
  - 步骤4：报告与修复建议

### [11. 安全最佳实践](./11_安全最佳实践/安全最佳实践.md)
  - 模型层
  - 应用层
  - RAG 层
  - 运营层
  - 架构层

### [12. 总结](./12_总结/总结.md)

---

## 📊 内容审核总览

- 总章节数：12
- 待完善章节：12

### 各章节审核状态
- **LLM 红队测试方法论**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **LLM 攻击技术分类**：⚠️ 需补充 1 项
  - 缺少：practice
- **LLM 红队测试框架**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **LLM 安全评估基准**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **RAG 安全概述**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **RAG 攻击面**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **RAG 安全防护**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **LLM 安全防护体系**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **AI 安全监测与告警**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **实战案例：LLM 应用红队测试全流程**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **安全最佳实践**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：references
- **总结**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
