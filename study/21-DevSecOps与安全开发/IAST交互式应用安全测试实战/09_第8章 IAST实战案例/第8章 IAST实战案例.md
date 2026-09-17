# 第8章 IAST实战案例

本章通过四个真实场景的实战案例，展示IAST在不同场景下的部署和应用方式，帮助读者将理论知识转化为实际操作能力。

### 8.1 案例1：Java Web应用IAST部署与漏洞检测

#### 8.1.1 案例背景

某电商平台的用户中心系统（Java + Spring Boot + MyBatis）需要进行安全测试。传统的DAST扫描覆盖率低，SAST误报多，安全团队决定引入IAST进行安全测试。

**应用信息：**
- 技术栈：Java 8 + Spring Boot 2.3 + MyBatis + MySQL
- 部署方式：Docker容器化部署
- 规模：约50个接口，核心业务包括用户注册、登录、个人信息管理、订单查询
- 测试环境：独立的测试集群，1个应用实例 + 1个MySQL实例

#### 8.1.2 部署方案

**Step 1: 部署OpenRASP管理后台**

```bash
# 使用Docker Compose部署管理后台
cd /opt
git clone https://github.com/baidu-security/openrasp-cloud-deploy.git
cd openrasp-cloud-deploy

# 修改默认密码
cp .env.example .env
sed -i 's/OPENRASP_PASSWORD=.*/OPENRASP_PASSWORD=SecurePass123/' .env

# 启动服务
docker-compose up -d

# 验证服务启动
docker-compose ps
```

**Step 2: 添加应用并获取配置**

1. 登录管理后台 `http://<服务器IP>:8086`
2. 进入"应用管理" → "添加应用"
3. 应用名称：`用户中心系统`
4. 语言：Java
5. 应用类型：IAST
6. 提交后获取 `app_id` 和 `app_secret`

**Step 3: 修改Dockerfile集成Agent**

```dockerfile
# Dockerfile
FROM openjdk:8-jre-alpine

# 创建工作目录
WORKDIR /app

# 复制应用jar包
COPY target/user-center.jar /app/app.jar

# 复制OpenRASP Agent
COPY rasp/ /app/rasp/

# 配置环境变量
ENV JAVA_OPTS="-javaagent:/app/rasp/rasp.jar"
ENV RASP_APP_ID="your_app_id"
ENV RASP_APP_SECRET="your_app_secret"
ENV RASP_BACKEND_URL="http://iast-server:8086/"
ENV RASP_IAST_ENABLED="true"

EXPOSE 8080

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -Drasp.app_id=$RASP_APP_ID -Drasp.app_secret=$RASP_APP_SECRET -Drasp.backend_url=$RASP_BACKEND_URL -Drasp.iast.enabled=$RASP_IAST_ENABLED -jar /app/app.jar"]
```

**Step 4: 构建并部署测试环境**

```bash
# 构建镜像
docker build -t user-center:iast-test .

# 启动应用
docker run -d --name user-center-test -p 8080:8080 user-center:iast-test

# 查看启动日志
docker logs -f user-center-test
```

**Step 5: 验证Agent连接**

1. 登录OpenRASP管理后台
2. 进入"应用管理" → "主机列表"
3. 确认Agent已注册并显示"在线"状态

#### 8.1.3 测试执行与漏洞发现

**准备测试用例：**

```python
# test_user_center_iast.py
import requests
import pytest

BASE_URL = "http://test-server:8080"

class TestUserCenterSecurity:
    """用户中心安全测试 - IAST模式"""
    
    def test_sql_injection_login(self):
        """登录接口SQL注入"""
        payloads = [
            {"username": "admin'--", "password": "any"},
            {"username": "admin' OR '1'='1", "password": "any"},
            {"username": "admin' UNION SELECT 1,2,3--", "password": "any"},
        ]
        for payload in payloads:
            response = requests.post(f"{BASE_URL}/api/login", json=payload)
            # IAST会检测SQL是否被污染
            assert response.status_code in [200, 401]
    
    def test_xss_profile(self):
        """个人信息XSS"""
        payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
        ]
        for payload in payloads:
            response = requests.post(f"{BASE_URL}/api/profile", 
                json={"nickname": payload},
                headers={"Authorization": "Bearer test-token"})
            # IAST会检测输出到响应的污点数据
            assert response.status_code == 200
    
    def test_command_injection_ping(self):
        """连通性测试命令注入"""
        payloads = [
            "127.0.0.1; id",
            "127.0.0.1 && whoami",
            "127.0.0.1|ls /etc",
        ]
        for payload in payloads:
            response = requests.get(f"{BASE_URL}/api/health/ping", 
                params={"host": payload})
            assert response.status_code == 200
    
    def test_path_traversal_avatar(self):
        """头像下载路径遍历"""
        payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "/etc/passwd",
        ]
        for payload in payloads:
            response = requests.get(f"{BASE_URL}/api/avatar", 
                params={"file": payload})
            assert response.status_code in [200, 400, 404]
    
    def test_ssrf_image_upload(self):
        """图片上传SSRF"""
        payloads = [
            "http://127.0.0.1:8080/admin",
            "http://internal-service:8080/secret",
            "file:///etc/passwd",
        ]
        for payload in payloads:
            response = requests.post(f"{BASE_URL}/api/image/fetch", 
                json={"url": payload})
            assert response.status_code in [200, 400]
```

**运行测试：**

```bash
pytest test_user_center_iast.py -v
```

#### 8.1.4 漏洞结果分析

测试完成后，在IAST管理后台查看发现的漏洞：

**典型漏洞1：SQL注入**
- 位置：登录接口 `/api/login`
- 参数：`username`
- 严重程度：高危
- 调用栈：`UserController.login() → UserDao.findByUsername() → Statement.executeQuery()`
- 污点传播：HTTP参数 → username变量 → SQL拼接 → 数据库执行
- 修复建议：使用PreparedStatement参数化查询或MyBatis #{}语法

**典型漏洞2：反射型XSS**
- 位置：搜索接口 `/api/search`
- 参数：`keyword`
- 严重程度：中危
- 污点传播：HTTP参数 → keyword变量 → 返回JSON响应
- 修复建议：输出时进行HTML转义

**典型漏洞3：路径遍历**
- 位置：文件下载接口 `/api/download`
- 参数：`filename`
- 严重程度：高危
- 污点传播：HTTP参数 → filename变量 → FileInputStream构造 → 文件读取
- 修复建议：对文件名进行规范化处理，限制在指定目录内

#### 8.1.5 修复与验证

**漏洞修复流程：**

1. 安全团队将漏洞导出为Jira工单
2. 分配给对应的开发人员
3. 开发人员根据IAST提供的调用栈和修复建议修复代码
4. 修复后重新部署到测试环境
5. 重新运行IAST测试，验证漏洞是否消除
6. 漏洞状态更新为"已修复"

### 8.2 案例2：微服务架构下的IAST部署方案

#### 8.2.1 案例背景

某互联网公司采用微服务架构，共有30+个微服务，技术栈以Java Spring Cloud为主。安全团队需要在测试环境对所有微服务进行IAST检测，同时尽量减少部署和维护成本。

**架构特点：**
- 服务数量：30+个微服务
- 技术栈：Java 11 + Spring Cloud + Kubernetes
- 部署方式：K8s容器化部署
- 服务间通信：Feign + REST
- API网关：Spring Cloud Gateway

#### 8.2.2 部署架构设计

**方案：K8s DaemonSet + InitContainer模式**

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes 集群                            │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Namespace: test (测试环境)                          │    │
│  │                                                      │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │    │
│  │  │ Service-A │  │ Service-B │  │ Service-C │  ...    │    │
│  │  │ +IAST    │  │ +IAST    │  │ +IAST    │           │    │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘           │    │
│  │       │              │              │                  │    │
│  └───────┼──────────────┼──────────────┼──────────────────┘    │
│          │              │              │                        │
│          └──────────────┴──────────────┘                        │
│                         │                                       │
│                         ▼                                       │
│                ┌─────────────────┐                             │
│                │ OpenRASP 管理后台 │                             │
│                │ (单独部署)        │                             │
│                └─────────────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

#### 8.2.3 具体实施

**Step 1: 准备IAST Agent镜像**

创建一个包含IAST Agent的共享镜像，供所有微服务挂载使用。

```dockerfile
# rasp-agent/Dockerfile
FROM busybox:latest

# 创建目录
RUN mkdir -p /opt/rasp

# 复制Agent文件
COPY rasp.jar /opt/rasp/rasp.jar
COPY rasp/ /opt/rasp/rasp/

# 设置权限
RUN chmod -R 755 /opt/rasp

VOLUME ["/opt/rasp"]

CMD ["cp", "-r", "/opt/rasp/.", "/rasp-volume/"]
```

**Step 2: 通过K8s Admission Webhook自动注入**

使用MutatingAdmissionWebhook在Pod创建时自动注入IAST Agent。

```yaml
# iast-injector-config.yaml
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: iast-injector-webhook
webhooks:
  - name: iast-injector.example.com
    admissionReviewVersions: ["v1"]
    sideEffects: None
    rules:
      - operations: ["CREATE"]
        apiGroups: [""]
        apiVersions: ["v1"]
        resources: ["pods"]
    namespaceSelector:
      matchLabels:
        iast-inject: "true"
    clientConfig:
      service:
        name: iast-injector
        namespace: iast-system
        path: "/mutate"
      caBundle: <CA_BUNDLE>
```

**注入逻辑（简化版）：**

```python
# injector.py - 简化的注入逻辑
def inject_iast(pod_spec):
    """向Pod中注入IAST Agent"""
    
    # 1. 添加Init Container来复制Agent文件
    init_container = {
        "name": "iast-agent-init",
        "image": "registry.example.com/iast/rasp-agent:latest",
        "volumeMounts": [{
            "name": "rasp-volume",
            "mountPath": "/rasp-volume"
        }],
        "command": ["cp", "-r", "/opt/rasp/.", "/rasp-volume/"]
    }
    pod_spec["initContainers"] = pod_spec.get("initContainers", [])
    pod_spec["initContainers"].append(init_container)
    
    # 2. 为每个容器添加环境变量和Volume挂载
    for container in pod_spec.get("containers", []):
        # 添加JVM参数
        java_opts = container.get("env", {}).get("JAVA_OPTS", "")
        java_opts += " -javaagent:/rasp/rasp.jar"
        
        # 添加环境变量
        env = container.get("env", [])
        env.extend([
            {"name": "JAVA_OPTS", "value": java_opts},
            {"name": "RASP_APP_ID", "valueFrom": {
                "fieldRef": {"fieldPath": "metadata.labels['app']"}
            }},
            {"name": "RASP_APP_SECRET", "valueFrom": {
                "secretKeyRef": {
                    "name": "iast-secret",
                    "key": "app-secret"
                }
            }},
            {"name": "RASP_BACKEND_URL", 
             "value": "http://iast-cloud.iast-system:8086/"},
            {"name": "RASP_IAST_ENABLED", "value": "true"},
        ])
        container["env"] = env
        
        # 添加Volume挂载
        volume_mounts = container.get("volumeMounts", [])
        volume_mounts.append({
            "name": "rasp-volume",
            "mountPath": "/rasp"
        })
        container["volumeMounts"] = volume_mounts
    
    # 3. 添加共享Volume
    pod_spec["volumes"] = pod_spec.get("volumes", [])
    pod_spec["volumes"].append({
        "name": "rasp-volume",
        "emptyDir": {}
    })
    
    return pod_spec
```

**Step 3: 为测试环境命名空间打标签**

```bash
# 启用IAST自动注入
kubectl label namespace test iast-inject=true
```

**Step 4: 部署验证**

```bash
# 查看测试环境的Pod是否被注入了Init Container
kubectl get pods -n test -o jsonpath='{.items[*].spec.initContainers[*].name}'

# 查看Pod内是否有rasp目录
kubectl exec -n test <pod-name> -- ls /rasp
```

#### 8.2.4 流量统一入口

为了更好地触发所有微服务的IAST检测，通过API网关统一进行自动化测试流量注入。

```
自动化测试脚本 → API Gateway → 各微服务 → IAST Agent检测
```

**测试策略：**
- 基于API文档（Swagger/OpenAPI）生成接口测试用例
- 每个接口构造正常请求和安全测试Payload
- 通过网关访问，覆盖所有微服务
- 结合链路追踪（SkyWalking等）分析覆盖情况

### 8.3 案例3：IAST与自动化测试结合实现DevSecOps

#### 8.3.1 案例背景

某金融科技公司推行DevSecOps，要求将安全测试完全融入CI/CD流水线。安全团队选择将IAST与自动化测试结合，实现"测试即安全"的目标。

**目标：**
1. 每个MR（Merge Request）自动运行IAST检测
2. 高危漏洞阻断合入
3. 漏洞自动创建Jira工单
4. 安全结果与代码关联

#### 8.3.2 流水线设计

```
代码提交 → MR → CI流水线
                    ├── SAST扫描（代码提交阶段）
                    ├── 构建镜像
                    ├── 部署测试环境（带IAST Agent）
                    ├── 单元测试
                    ├── 接口自动化测试
                    ├── IAST漏洞检测（后台并行）
                    ├── 安全门禁检查
                    ├── 结果通知
                    └── 通过 → 允许合入 / 不通过 → 阻断+告警
```

#### 8.3.3 GitLab CI完整配置

```yaml
# .gitlab-ci.yml
variables:
  APP_NAME: "payment-service"
  IAST_CLOUD_URL: "http://iast-cloud.internal.com"
  DOCKER_REGISTRY: "registry.internal.com"

stages:
  - sast
  - build
  - deploy-test
  - test
  - security-gate
  - notify

sast-scan:
  stage: sast
  image: checkmarx/cxflow
  script:
    - cx-flow scan --spring.config.location=cxflow.yml
  artifacts:
    reports:
      sast: gl-sast-report.json
  only:
    - merge_requests

build-image:
  stage: build
  script:
    - docker build -t $DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHA .
    - docker push $DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHA
  only:
    - merge_requests

deploy-iast-env:
  stage: deploy-test
  image: bitnami/kubectl
  script:
    # 部署带有IAST的测试环境
    - |
      cat <<EOF | kubectl apply -f -
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: $APP_NAME-iast-$CI_MERGE_REQUEST_IID
        namespace: iast-test
      spec:
        replicas: 1
        selector:
          matchLabels:
            app: $APP_NAME-iast
            mr-id: "$CI_MERGE_REQUEST_IID"
        template:
          metadata:
            labels:
              app: $APP_NAME-iast
              mr-id: "$CI_MERGE_REQUEST_IID"
          spec:
            initContainers:
              - name: rasp-init
                image: $DOCKER_REGISTRY/iast/rasp-agent:latest
                volumeMounts:
                  - name: rasp-volume
                    mountPath: /rasp-volume
            containers:
              - name: app
                image: $DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHA
                ports:
                  - containerPort: 8080
                env:
                  - name: JAVA_OPTS
                    value: "-javaagent:/rasp/rasp.jar"
                  - name: RASP_APP_ID
                    value: "$APP_NAME-mr$CI_MERGE_REQUEST_IID"
                  - name: RASP_APP_SECRET
                    valueFrom:
                      secretKeyRef:
                        name: iast-secret
                        key: app-secret
                  - name: RASP_BACKEND_URL
                    value: "$IAST_CLOUD_URL"
                  - name: RASP_IAST_ENABLED
                    value: "true"
                volumeMounts:
                  - name: rasp-volume
                    mountPath: /rasp
            volumes:
              - name: rasp-volume
                emptyDir: {}
      EOF
    
    # 等待应用就绪
    - kubectl wait --for=condition=available deployment/$APP_NAME-iast-$CI_MERGE_REQUEST_IID -n iast-test --timeout=120s
    
    # 创建Service
    - kubectl expose deployment $APP_NAME-iast-$CI_MERGE_REQUEST_IID --name=$APP_NAME-iast-$CI_MERGE_REQUEST_IID -n iast-test --port=8080 --target-port=8080
  only:
    - merge_requests

automated-test:
  stage: test
  image: python:3.9
  script:
    - pip install pytest requests
    - export TEST_BASE_URL="http://$APP_NAME-iast-$CI_MERGE_REQUEST_IID.iast-test.svc.cluster.local:8080"
    - pytest tests/ -v --junitxml=test-results.xml
  artifacts:
    reports:
      junit: test-results.xml
  only:
    - merge_requests

iast-security-gate:
  stage: security-gate
  image: curlimages/curl
  script:
    - |
      # 等待IAST分析完成
      sleep 30
      
      # 调用IAST API获取该次构建的漏洞
      VULN_RESULT=$(curl -s "$IAST_CLOUD_URL/api/v1/vulnerabilities" \
        -H "X-App-Id: $APP_NAME-mr$CI_MERGE_REQUEST_IID" \
        -H "X-App-Secret: $IAST_APP_SECRET")
      
      echo "$VULN_RESULT" > iast-result.json
      
      # 统计各等级漏洞数量
      HIGH_COUNT=$(echo $VULN_RESULT | jq '[.[] | select(.severity=="high")] | length')
      MEDIUM_COUNT=$(echo $VULN_RESULT | jq '[.[] | select(.severity=="medium")] | length')
      LOW_COUNT=$(echo $VULN_RESULT | jq '[.[] | select(.severity=="low")] | length')
      
      echo "=== IAST安全检测结果 ==="
      echo "高危漏洞: $HIGH_COUNT"
      echo "中危漏洞: $MEDIUM_COUNT"
      echo "低危漏洞: $LOW_COUNT"
      
      # 安全门禁：高危漏洞阻断
      if [ "$HIGH_COUNT" -gt 0 ]; then
        echo "❌ 安全门禁未通过：存在 $HIGH_COUNT 个高危漏洞"
        exit 1
      fi
      
      echo "✅ 安全门禁通过"
  artifacts:
    when: always
    paths:
      - iast-result.json
  only:
    - merge_requests

notify-result:
  stage: notify
  script:
    - |
      # 发送通知到企业微信/钉钉
      if [ "$HIGH_COUNT" -gt 0 ]; then
        MESSAGE="❌ IAST检测发现高危漏洞，请及时处理\n项目：$APP_NAME\nMR：$CI_MERGE_REQUEST_IID\n高危：$HIGH_COUNT，中危：$MEDIUM_COUNT，低危：$LOW_COUNT"
      else
        MESSAGE="✅ IAST安全检测通过\n项目：$APP_NAME\nMR：$CI_MERGE_REQUEST_IID\n中危：$MEDIUM_COUNT，低危：$LOW_COUNT"
      fi
      
      curl -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"msgtype\": \"text\", \"text\": {\"content\": \"$MESSAGE\"}}"
  when: always
  only:
    - merge_requests

cleanup:
  stage: .post
  image: bitnami/kubectl
  script:
    # 清理测试环境
    - kubectl delete deployment $APP_NAME-iast-$CI_MERGE_REQUEST_IID -n iast-test --ignore-not-found=true
    - kubectl delete svc $APP_NAME-iast-$CI_MERGE_REQUEST_IID -n iast-test --ignore-not-found=true
  when: always
  only:
    - merge_requests
```

#### 8.3.4 实施效果

**效果指标：**
- 安全测试覆盖率：从30%提升到85%
- 漏洞发现时间：从上线后发现变为MR阶段发现
- 漏洞修复周期：从平均15天缩短到3天
- 误报率：从SAST的45%降低到IAST的8%
- 开发接受度：从抵触变为主动配合

### 8.4 案例4：从发现漏洞到修复闭环流程

#### 8.4.1 闭环流程设计

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ 漏洞发现 │───▶│漏洞审核 │───▶│ 漏洞修复 │───▶│ 修复验证 │
│ IAST检测 │    │安全团队  │    │开发团队  │    │ IAST重测 │
└─────────┘    └────┬────┘    └────┬────┘    └────┬────┘
                     │              │              │
                     ▼              ▼              ▼
              ┌──────────────────────────────────────┐
              │          漏洞管理平台（Jira）          │
              └──────────────────────────────────────┘
```

#### 8.4.2 流程详解

**阶段1：漏洞发现**
- IAST Agent在自动化测试过程中检测到漏洞
- 漏洞数据实时上报到管理后台
- 管理后台进行漏洞去重、聚合、风险评级
- 自动创建漏洞工单

**阶段2：漏洞审核**
- 安全工程师审核IAST发现的漏洞
- 确认是否为误报（误报则关闭并记录原因）
- 确认漏洞严重等级是否准确
- 补充漏洞描述和修复建议
- 分配给对应的开发负责人

**阶段3：漏洞修复**
- 开发人员收到Jira工单通知
- 根据IAST提供的调用栈定位问题代码
- 参考修复建议进行修复
- 提交代码，发起MR
- MR重新运行IAST检测

**阶段4：修复验证**
- CI流水线运行IAST检测
- 检测该漏洞是否仍然存在
- 如漏洞消失，状态自动更新为"已验证"
- 安全团队进行最终确认
- Jira工单关闭

#### 8.4.3 度量指标

**关键指标：**
- **漏洞发现率**：IAST发现的漏洞数 / 总漏洞数
- **误报率**：误报漏洞数 / 总报告漏洞数
- **平均修复时间（MTTR）**：从发现到关闭的平均时长
- **漏洞修复率**：已修复漏洞数 / 总漏洞数
- **复发率**：已修复漏洞再次出现的比例

---

---

## 📋 内容审核与补充建议

> 针对「第8章 IAST实战案例」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
