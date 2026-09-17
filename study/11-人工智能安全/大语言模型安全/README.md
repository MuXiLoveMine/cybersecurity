# 大语言模型安全

> 本文档整理自：`大语言模型安全.md`

---

## 目录

### [01. LLM 安全概述](./01_LLM 安全概述/LLM 安全概述.md)
  - LLM 安全的重要性
  - LLM 安全风险全景
  - LLM 安全的独特挑战

### [02. Prompt 注入攻击（Prompt Injection）](./02_Prompt 注入攻击（Prompt Injection）/Prompt 注入攻击（Prompt Injection）.md)
  - 什么是提示注入
  - 提示注入的类型
  - 高级提示注入技术
  - 真实案例

### [03. 越狱攻击（Jailbreak）](./03_越狱攻击（Jailbreak）/越狱攻击（Jailbreak）.md)
  - 什么是越狱攻击
  - 常见越狱方法
  - 越狱攻击的发展趋势

### [04. 数据泄露与隐私](./04_数据泄露与隐私/数据泄露与隐私.md)
  - 训练数据泄露
  - 成员推断攻击（Membership Inference）
  - 对话数据隐私
  - 属性推断攻击

### [05. 模型窃取（Model Stealing）](./05_模型窃取（Model Stealing）/模型窃取（Model Stealing）.md)
  - 什么是模型窃取
  - 模型窃取方法
  - LLM 模型窃取
  - 模型窃取的防御

### [06. 模型投毒（Model Poisoning）](./06_模型投毒（Model Poisoning）/模型投毒（Model Poisoning）.md)
  - 什么是模型投毒
  - 投毒攻击类型
  - LLM 的投毒攻击
  - 投毒防御

### [07. 输出安全（有害内容生成）](./07_输出安全（有害内容生成）/输出安全（有害内容生成）.md)
  - 有害内容类型
  - 幻觉问题（Hallucination）

### [08. 对齐与 RLHF](./08_对齐与 RLHF/对齐与 RLHF.md)
  - 什么是对齐
  - RLHF（基于人类反馈的强化学习）
  - RLHF 的替代与改进
  - 红队测试（Red Teaming）

### [09. LLM 安全评测方法](./09_LLM 安全评测方法/LLM 安全评测方法.md)
  - 安全评测的重要性
  - 安全评测维度
  - 常见安全评测基准
  - 评测方法
  - 评测中的挑战

### [10. LLM 应用安全最佳实践](./10_LLM 应用安全最佳实践/LLM 应用安全最佳实践.md)
  - 输入防护
  - 输出防护
  - 系统防护
  - 运营防护

### [11. 学习资源与工具](./11_学习资源与工具/学习资源与工具.md)
  - 安全评测工具
  - 推荐论文
  - 在线资源

---

## 📊 内容审核总览

- 总章节数：11
- 待完善章节：11

### 各章节审核状态
- **LLM 安全概述**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **Prompt 注入攻击（Prompt Injection）**：⚠️ 需补充 1 项
  - 缺少：commands
- **越狱攻击（Jailbreak）**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：references
- **数据泄露与隐私**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
- **模型窃取（Model Stealing）**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **模型投毒（Model Poisoning）**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **输出安全（有害内容生成）**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
- **对齐与 RLHF**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **LLM 安全评测方法**：⚠️ 需补充 7 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **LLM 应用安全最佳实践**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **学习资源与工具**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
