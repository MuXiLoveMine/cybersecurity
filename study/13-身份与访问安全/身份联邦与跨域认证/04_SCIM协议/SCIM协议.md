# SCIM协议

### 4.1 SCIM概述

**SCIM (System for Cross-domain Identity Management)** 是跨域身份管理的标准协议，用于自动化用户身份的生命周期管理。

```text
SCIM 2.0 核心概念

目标:
  自动化用户/组的管理
  减少手动配置
  跨系统身份同步

SCIM端点:
├── /Users: 用户管理
│   ├── POST: 创建用户
│   ├── GET: 查询用户
│   ├── PUT: 替换用户
│   ├── PATCH: 修改用户属性
│   └── DELETE: 删除用户
├── /Groups: 组管理
│   ├── POST: 创建组
│   ├── GET: 查询组
│   ├── PUT: 替换组
│   ├── PATCH: 修改组成员
│   └── DELETE: 删除组
└── /Bulk: 批量操作

SCIM用户对象:
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "id": "12345",
  "userName": "john.doe@example.com",
  "name": {
    "givenName": "John",
    "familyName": "Doe"
  },
  "emails": [
    {"value": "john@example.com", "type": "work", "primary": true}
  ],
  "active": true,
  "groups": [
    {"value": "group-001", "display": "Engineering"}
  ],
  "meta": {
    "resourceType": "User",
    "created": "2026-09-13T10:00:00Z",
    "lastModified": "2026-09-13T10:00:00Z"
  }
}
```

### 4.2 用户生命周期管理

```python
class SCIMUserManager:
    """SCIM用户生命周期管理"""

    SCIM_USER_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:User"
    SCIM_ENTERPRISE_SCHEMA = "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"

    def __init__(self, base_url, auth_token):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/scim+json',
            'Accept': 'application/scim+json'
        }

    def create_user(self, user_data):
        """创建用户 (SCIM POST /Users)"""
        import requests

        scim_user = {
            'schemas': [self.SCIM_USER_SCHEMA],
            'userName': user_data['username'],
            'name': {
                'givenName': user_data.get('first_name', ''),
                'familyName': user_data.get('last_name', '')
            },
            'emails': [{
                'value': user_data['email'],
                'type': 'work',
                'primary': True
            }],
            'active': True,
            'password': user_data.get('temporary_password', ''),
            'displayName': f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        }

        # 企业扩展属性
        if 'department' in user_data or 'title' in user_data:
            scim_user[self.SCIM_ENTERPRISE_SCHEMA] = {
                'department': user_data.get('department', ''),
                'title': user_data.get('title', '')
            }

        response = requests.post(
            f'{self.base_url}/Users',
            json=scim_user,
            headers=self.headers
        )

        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"创建用户失败: {response.status_code} {response.text}")

    def get_user(self, user_id):
        """获取用户 (SCIM GET /Users/{id})"""
        import requests
        response = requests.get(
            f'{self.base_url}/Users/{user_id}',
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json()
        return None

    def search_users(self, filter_expr=None, start_index=1, count=100):
        """搜索用户 (SCIM GET /Users?filter=...)"""
        import requests
        params = {
            'startIndex': start_index,
            'count': count
        }
        if filter_expr:
            params['filter'] = filter_expr

        response = requests.get(
            f'{self.base_url}/Users',
            params=params,
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json()
        return None

    def update_user(self, user_id, updates):
        """更新用户 (SCIM PATCH /Users/{id})"""
        import requests

        operations = []
        for path, value in updates.items():
            operations.append({
                'op': 'replace',
                'path': path,
                'value': value
            })

        patch_request = {
            'schemas': ['urn:ietf:params:scim:api:messages:2.0:PatchOp'],
            'Operations': operations
        }

        response = requests.patch(
            f'{self.base_url}/Users/{user_id}',
            json=patch_request,
            headers=self.headers
        )
        return response.status_code == 200

    def deactivate_user(self, user_id):
        """停用用户"""
        return self.update_user(user_id, {'active': False})

    def delete_user(self, user_id):
        """删除用户 (SCIM DELETE /Users/{id})"""
        import requests
        response = requests.delete(
            f'{self.base_url}/Users/{user_id}',
            headers=self.headers
        )
        return response.status_code == 204

    def sync_user(self, user_data):
        """同步用户（创建或更新）"""
        # 先查找用户
        filter_expr = f'userName eq "{user_data["username"]}"'
        results = self.search_users(filter_expr)

        if results and results.get('totalResults', 0) > 0:
            # 用户已存在，更新
            user = results['Resources'][0]
            return self.update_user(user['id'], {
                'name.givenName': user_data.get('first_name', ''),
                'name.familyName': user_data.get('last_name', ''),
                'emails[type eq "work"].value': user_data.get('email', '')
            })
        else:
            # 用户不存在，创建
            return self.create_user(user_data)
```

---

---

