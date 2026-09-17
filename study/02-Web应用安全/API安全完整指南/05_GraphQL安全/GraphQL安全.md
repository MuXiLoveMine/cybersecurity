# GraphQL安全

### 4.1 内省攻击与防护

```graphql
# 内省查询 - 暴露完整Schema
{
  __schema {
    types {
      name
      fields {
        name
        type {
          name
          kind
          ofType { name kind }
        }
      }
    }
  }
}

# 攻击者可获取:
# - 所有Type定义
# - 所有Query/Mutation入口
# - 字段类型和关系
# - 内部数据模型（可能暴露隐藏端点）
```

**防护方案：**

```python
from graphql import parse, validate
from graphql.language.ast import IntrospectionQuery

# 生产环境禁用内省
def disable_introspection(query):
    """检测并阻止内省查询"""
    try:
        document = parse(query)
        for node in document.definitions:
            if isinstance(node, IntrospectionQuery):
                raise Exception("Introspection disabled in production")
    except Exception:
        return False
    return True

# Flask-GraphQL配置
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=False,  # 生产环境关闭IDE
        introspection=False,  # 关闭内省
    )
)

# 按角色控制内省权限
def conditional_introspection(query, user_role):
    if user_role == 'developer':
        return True  # 开发者可内省
    return disable_introspection(query)
```

### 4.2 批量查询攻击

```graphql
# 批量查询 - 单请求发送多个查询
[
  {"query": "mutation { login(username:\"admin\", password:\"pass1\") { token } }"},
  {"query": "mutation { login(username:\"admin\", password:\"pass2\") { token } }"},
  {"query": "mutation { login(username:\"admin\", password:\"pass3\") { token } }"},
  # ... 数千个查询
  # 单请求绕过速率限制，实现批量暴力破解
]

# 别名攻击 - 利用别名批量请求
{
  a1: user(id: 1) { email }
  a2: user(id: 2) { email }
  a3: user(id: 3) { email }
  # ...
  a10000: user(id: 10000) { email }
  # 单查询枚举所有用户
}
```

**防护方案：**

```python
# 查询复杂度分析
from graphql.analysis import QueryComplexityAnalyzer

class ComplexityValidator:
    MAX_DEPTH = 7        # 最大查询深度
    MAX_COMPLEXITY = 1000 # 最大复杂度
    MAX_ALIASES = 10     # 最大别名数

    @classmethod
    def validate(cls, query: str) -> tuple[bool, str]:
        document = parse(query)

        # 深度检查
        depth = cls._calculate_depth(document)
        if depth > cls.MAX_DEPTH:
            return False, f"Query depth {depth} exceeds max {cls.MAX_DEPTH}"

        # 复杂度检查
        complexity = cls._calculate_complexity(document)
        if complexity > cls.MAX_COMPLEXITY:
            return False, f"Complexity {complexity} exceeds max {cls.MAX_COMPLEXITY}"

        # 别名数量检查
        alias_count = cls._count_aliases(document)
        if alias_count > cls.MAX_ALIASES:
            return False, f"Aliases {alias_count} exceeds max {cls.MAX_ALIASES}"

        return True, "OK"

    @staticmethod
    def _calculate_depth(node, current_depth=0):
        max_depth = current_depth
        if hasattr(node, 'selection_set') and node.selection_set:
            for selection in node.selection_set.selections:
                max_depth = max(max_depth,
                               ComplexityValidator._calculate_depth(
                                   selection, current_depth + 1))
        return max_depth

    @staticmethod
    def _count_aliases(document):
        count = 0
        for definition in document.definitions:
            if hasattr(definition, 'selection_set'):
                for field in definition.selection_set.selections:
                    if field.alias:
                        count += 1
        return count

# 在GraphQL中间件中使用
@app.route('/graphql', methods=['POST'])
def graphql_endpoint():
    query = request.json.get('query', '')
    valid, message = ComplexityValidator.validate(query)
    if not valid:
        return jsonify({"errors": [{"message": message}]}), 400
    # ... 执行查询
```

### 4.3 深度嵌套攻击

```graphql
# 递归深度嵌套 - 导致无限递归或资源耗尽
{
  user(id: 1) {
    friends {
      friends {
        friends {
          friends {
            friends {
              # ... 无限嵌套
              # N层嵌套 = N^关系数 次数据库查询
            }
          }
        }
      }
    }
  }
}

# 如果User.friends返回User列表
# 深度5 → 每层N个朋友 → N^5次查询
```

**防护方案：**

```python
# 查询深度限制中间件
from graphql import GraphQLObjectType

def depth_limit_validator(max_depth=7):
    """GraphQL深度限制中间件"""
    def middleware(next_, root, info, **args):
        context = info.context
        if not hasattr(context, '_depth'):
            context._depth = 0
        context._depth += 1
        if context._depth > max_depth:
            raise Exception(f"Query depth exceeds limit of {max_depth}")
        result = next_(root, info, **args)
        context._depth -= 1
        return result
    return middleware

# 成本分析器 - 为每个字段分配成本
FIELD_COSTS = {
    'user': 1,
    'users': 10,      # 列表查询成本高
    'friends': 5,
    'orders': 3,
    'search': 50,     # 搜索成本最高
}

class CostAnalyzer:
    MAX_COST = 1000

    @classmethod
    def calculate_cost(cls, document) -> int:
        total = 0
        for definition in document.definitions:
            if hasattr(definition, 'selection_set'):
                total += cls._selection_cost(definition.selection_set)
        return total

    @classmethod
    def _selection_cost(cls, selection_set, multiplier=1) -> int:
        cost = 0
        for field in selection_set.selections:
            field_name = field.name.value
            field_cost = FIELD_COSTS.get(field_name, 1)
            cost += field_cost * multiplier
            if hasattr(field, 'selection_set') and field.selection_set:
                cost += cls._selection_cost(
                    field.selection_set, multiplier * field_cost)
        return cost
```

### 4.4 GraphQL认证与授权

```python
# GraphQL字段级授权
from graphene import ObjectType, String, List, Field

class UserType(ObjectType):
    id = String()
    name = String()
    email = String()
    role = String()
    salary = String()  # 敏感字段
    api_key = String()  # 极敏感字段

    # 字段级授权
    @staticmethod
    def resolve_email(parent, info):
        user = info.context.get('user')
        if not user:
            raise Exception("Authentication required")
        # 仅自己或管理员可查看email
        if user.id != parent.id and user.role != 'admin':
            raise Exception("Not authorized to view email")
        return parent.email

    @staticmethod
    def resolve_salary(parent, info):
        user = info.context.get('user')
        # 仅HR和管理员可查看薪资
        if not user or user.role not in ('hr', 'admin'):
            raise Exception("Not authorized")
        return parent.salary

    @staticmethod
    def resolve_api_key(parent, info):
        # 永远不通过GraphQL暴露
        raise Exception("Field not accessible")

# 查询级授权
class Query(ObjectType):
    users = List(UserType)
    user = Field(UserType, id=String(required=True))

    @staticmethod
    def resolve_users(root, info):
        user = info.context.get('user')
        if not user or user.role not in ('admin', 'hr'):
            raise Exception("Admin access required")
        return User.query.all()

    @staticmethod
    def resolve_user(root, info, id):
        user = info.context.get('user')
        if not user:
            raise Exception("Authentication required")
        target = User.query.get(id)
        # BOLA防护
        if user.id != int(id) and user.role not in ('admin', 'hr'):
            raise Exception("Not authorized")
        return target
```

---

---

## 📋 内容审核与补充建议

> 针对「GraphQL安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
