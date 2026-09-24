# 附录：SCA 工具速查表

```
┌─────────────────┬──────────────────────────────────────────┐
│ 场景            │ 推荐工具                                  │
├─────────────────┼──────────────────────────────────────────┤
│ 通用 SCA        │ Trivy / Grype / OWASP Dependency-Check   │
│ SBOM 生成       │ syft / cyclonedx-bom / trivy              │
│ 漏洞监控        │ Snyk / Dependabot                        │
│ 许可证扫描      │ scancode-toolkit / license-checker       │
│ 供应链签名      │ cosign (Sigstore)                         │
│ 策略验证        │ OPA / conftest                           │
│ Python 专用     │ pip-audit / safety                       │
│ Node.js 专用    │ npm audit / snyk                         │
│ Java 专用       │ dependency-check-maven                   │
│ Go 专用         │ govulncheck                              │
│ Rust 专用       │ cargo audit                              │
└─────────────────┴──────────────────────────────────────────┘
```

---

> **声明**：本文档仅用于安全教育与防御目的。所有工具和脚本用于帮助组织发现和修复依赖中的已知漏洞，提升供应链安全水位。请遵循所在地区的法律法规。

---

