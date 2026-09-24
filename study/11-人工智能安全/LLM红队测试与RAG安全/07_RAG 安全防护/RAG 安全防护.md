# RAG 安全防护

### 7.1 输入过滤

在检索前对用户查询进行过滤与清洗。

```python
class RAGInputFilter:
    """RAG 输入过滤器"""

    BLOCKED_PATTERNS = [
        r"ignore.{0,20}(instruction|prompt|rule)",
        r"system.{0,10}prompt",
        r"forget.{0,20}(previous|all)",
        r"you.{0,10}(are|act as).{0,10}(DAN|unlimited|jailbreak)",
    ]

    MAX_QUERY_LENGTH = 500

    def filter(self, query):
        # 1. 长度限制
        if len(query) > self.MAX_QUERY_LENGTH:
            return False, "查询过长"

        # 2. 注入模式检测
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return False, f"检测到注入模式: {pattern}"

        # 3. 语义有害性检测（使用分类模型）
        if self._is_harmful(query):
            return False, "查询含有害内容"

        return True, "通过"

    def _is_harmful(self, query):
        # 使用轻量分类模型判断有害性
        # 示例：调用 OpenAI moderation API
        return False
```

### 7.2 检索验证

对检索结果进行安全验证，防止恶意文档进入生成阶段。

```python
class RetrievalValidator:
    """检索结果安全验证"""

    def validate(self, retrieved_docs, user_query):
        """验证检索文档的安全性"""
        clean_docs = []

        for doc in retrieved_docs:
            # 1. 检测隐藏注入指令
            if self._contains_injection(doc):
                print(f"[!] 文档含注入指令，已过滤: {doc.id}")
                continue

            # 2. 访问控制检查
            if not self._check_access(doc, user_query):
                print(f"[!] 访问控制拒绝: {doc.id}")
                continue

            # 3. 文档完整性校验
            if not self._verify_integrity(doc):
                print(f"[!] 文档完整性校验失败: {doc.id}")
                continue

            # 4. 相关性阈值过滤
            if doc.similarity_score < 0.7:
                continue

            clean_docs.append(doc)

        return clean_docs

    def _contains_injection(self, doc):
        """检测文档中的注入指令"""
        injection_indicators = [
            "ignore previous", "ignore above", "forget previous",
            "new instruction", "system prompt", "you are now",
        ]
        text_lower = doc.content.lower()
        return any(ind in text_lower for ind in injection_indicators)

    def _check_access(self, doc, user_query):
        """检查用户是否有权访问该文档"""
        # 实现文档级 ACL
        user_role = user_query.user_role
        doc_roles = doc.allowed_roles
        return user_role in doc_roles

    def _verify_integrity(self, doc):
        """校验文档是否被篡改"""
        return doc.hash == compute_hash(doc.content)
```

### 7.3 输出审查

在 LLM 生成后、返回用户前，对输出进行审查。

```python
class OutputReviewer:
    """LLM 输出安全审查"""

    def review(self, generated_output, retrieved_context, user_query):
        """审查生成内容"""
        checks = [
            self._check_harmful_content(generated_output),
            self._check_injection_leak(generated_output),
            self._check_factual_grounding(generated_output, retrieved_context),
            self._check_private_info(generated_output),
        ]

        for check_name, passed, message in checks:
            if not passed:
                print(f"[!] 审查未通过: {check_name} - {message}")
                return False, f"输出被审查拦截: {message}"

        return True, "审查通过"

    def _check_harmful_content(self, output):
        """检测有害内容"""
        # 使用 moderation API 或分类模型
        return True, True, ""

    def _check_injection_leak(self, output):
        """检测是否泄露了注入指令"""
        leak_indicators = ["system prompt", "ignore previous"]
        for ind in leak_indicators:
            if ind in output.lower():
                return False, False, f"泄露指令: {ind}"
        return True, True, ""

    def _check_factual_grounding(self, output, context):
        """检查输出是否基于检索内容（防止幻觉）"""
        # 使用 NLI 模型判断输出是否被检索内容支持
        # 如使用 entailment 模型
        return True, True, ""

    def _check_private_info(self, output):
        """检测是否泄露隐私信息"""
        import re
        # 检测电话号码、身份证、邮箱等
        patterns = [
            r'\d{11}',  # 手机号
            r'\d{17}[\dXx]',  # 身份证
            r'[\w.]+@[\w.]+',  # 邮箱
        ]
        for pattern in patterns:
            if re.search(pattern, output):
                return False, False, "检测到隐私信息"
        return True, True, ""
```

### 7.4 RAG 安全架构

```text
用户查询
   |
   v
[输入过滤] --注入检测/有害检测-->
   |
   v
[访问控制] --用户身份/文档ACL-->
   |
   v
[向量检索] --Top-K 候选-->
   |
   v
[检索验证] --注入过滤/完整性/相关性-->
   |
   v
[提示构造] --安全模板/隔离标记-->
   |
   v
[LLM 生成]
   |
   v
[输出审查] --有害/幻觉/隐私检测-->
   |
   v
[日志审计] --全链路记录-->
   |
   v
返回用户
```

---

---

