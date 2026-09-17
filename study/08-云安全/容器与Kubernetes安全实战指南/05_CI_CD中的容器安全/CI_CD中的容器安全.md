# CI/CD中的容器安全

### 5.1 流水线中的镜像扫描

```yaml
# GitLab CI 示例
stages:
  - build
  - scan
  - deploy

build_image:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

scan_image:
  stage: scan
  image: aquasec/trivy:latest
  script:
    - trivy image --exit-code 1 --severity CRITICAL,HIGH $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  allow_failure: false  # 发现高危漏洞则流水线失败

deploy:
  stage: deploy
  script:
    - kubectl apply -f k8s/
  only:
    - main
```

### 5.2 策略即代码

在流水线中注入 Kyverno/Gatekeeper 策略检查，确保部署前策略合规：

```bash
# 在 CI 中使用 kyverno CLI 验证策略
kyverno apply policies/ --resource k8s/deployment.yaml
```

### 5.3 Sigstore供应链签名验证

```bash
# 构建后签名镜像
cosign sign --key cosign.key $REGISTRY/$IMAGE:$TAG

# 在部署前验证签名
cosign verify --key cosign.pub $REGISTRY/$IMAGE:$TAG && \
  kubectl rollout restart deployment/myapp
```

---

---

## 📋 内容审核与补充建议

> 针对「CI/CD中的容器安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
