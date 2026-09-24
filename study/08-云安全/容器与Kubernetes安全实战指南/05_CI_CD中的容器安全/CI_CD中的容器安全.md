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

