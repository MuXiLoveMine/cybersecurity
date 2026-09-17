# ContentProvider安全

### 5.1 ContentProvider基础

ContentProvider是Android中跨应用共享数据的标准机制，基于URI进行数据访问：

```xml
<provider
    android:name=".UserDataProvider"
    android:authorities="com.example.provider.userdata"
    android:exported="true"
    android:permission="com.example.permission.READ_USER_DATA"
    android:readPermission="com.example.permission.READ_USER_DATA"
    android:writePermission="com.example.permission.WRITE_USER_DATA"
    android:grantUriPermissions="false"
    android:pathPermission="/secret"
    android:android:multiprocess="false">
</provider>
```

ContentProvider通过URI标识数据：

```
content://com.example.provider.userdata/users/123/profile
        |--------- authority ---------| |-- path --|
```

### 5.2 数据泄露

**未保护的ContentProvider**

```xml
<!-- 危险：暴露的ContentProvider无权限保护 -->
<provider
    android:name=".ContactsProvider"
    android:authorities="com.example.provider.contacts"
    android:exported="true" />
```

攻击者直接查询敏感数据：

```java
// 攻击者代码
Cursor cursor = getContentResolver().query(
    Uri.parse("content://com.example.provider.contacts/users"),
    null, null, null, null
);
while (cursor.moveToNext()) {
    String name = cursor.getString(cursor.getColumnIndex("name"));
    String phone = cursor.getString(cursor.getColumnIndex("phone"));
    String email = cursor.getString(cursor.getColumnIndex("email"));
    // 窃取所有联系人信息
}
```

**防御措施**

```xml
<!-- 正确配置权限 -->
<provider
    android:name=".ContactsProvider"
    android:authorities="com.example.provider.contacts"
    android:exported="true"
    android:readPermission="com.example.permission.READ_CONTACTS"
    android:writePermission="com.example.permission.WRITE_CONTACTS" />
```

### 5.3 SQL注入

ContentProvider的query方法如果未正确处理用户输入，可能存在SQL注入：

```java
// 不安全的实现
@Override
public Cursor query(Uri uri, String[] projection, String selection,
                    String[] selectionArgs, String sortOrder) {
    // 直接拼接selection，存在SQL注入
    String sql = "SELECT * FROM users WHERE name = '" + selection + "'";
    return db.rawQuery(sql, null);
}

// 攻击者利用
// selection = "' OR '1'='1"
// 实际查询: SELECT * FROM users WHERE name = '' OR '1'='1'
// 返回所有用户数据
```

**安全实现**

```java
@Override
public Cursor query(Uri uri, String[] projection, String selection,
                    String[] selectionArgs, String sortOrder) {
    // 使用参数化查询
    // selection使用占位符，selectionArgs提供参数值
    String safeSelection = "name = ?";
    String[] safeArgs = selectionArgs;

    // 验证projection，防止读取敏感列
    if (projection != null) {
        List<String> allowedColumns = Arrays.asList("name", "avatar");
        for (String col : projection) {
            if (!allowedColumns.contains(col)) {
                throw new IllegalArgumentException("Column not allowed: " + col);
            }
        }
    }

    // 使用SQLiteDatabase的query方法（自动转义）
    return db.query("users", projection, safeSelection,
                     safeArgs, null, null, sortOrder);
}
```

### 5.4 路径遍历

ContentProvider的openFile方法如果未正确处理路径，可能存在路径遍历漏洞：

```java
// 不安全的实现
@Override
public ParcelFileDescriptor openFile(Uri uri, String mode) {
    String path = uri.getLastPathSegment();
    // 未验证路径，可被遍历
    File file = new File(getContext().getFilesDir(), path);
    return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY);
}

// 攻击者利用
// content://com.example.provider/files/../../../../data/data/com.example/shared_prefs/secrets.xml
```

**安全实现**

```java
@Override
public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
    // 验证路径
    String path = uri.getLastPathSegment();
    if (path == null || path.contains("..") || path.contains("/")) {
        throw new IllegalArgumentException("Invalid path");
    }

    // 限制在指定目录内
    File baseDir = getContext().getFilesDir();
    File file = new File(baseDir, path);

    // 二次验证：确保最终路径在baseDir内
    try {
        String canonicalPath = file.getCanonicalPath();
        String canonicalBase = baseDir.getCanonicalPath();
        if (!canonicalPath.startsWith(canonicalBase)) {
            throw new SecurityException("Path traversal detected");
        }
    } catch (IOException e) {
        throw new SecurityException("Path validation failed", e);
    }

    // 验证文件模式
    int modeFlags = validateMode(mode);
    return ParcelFileDescriptor.open(file, modeFlags);
}
```

### 5.5 URI权限授予

`grantUriPermission`允许临时授予其他应用访问特定URI的权限。这可能导致权限提升：

```java
// 危险：过度授予权限
Intent shareIntent = new Intent(Intent.ACTION_SEND);
shareIntent.setData(Uri.parse("content://com.example.provider/all_data"));
shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
// 将授予接收方对整个provider的读取权限！
```

**安全实践**

```xml
<!-- 限制URI权限授予范围 -->
<provider
    android:name=".SecureProvider"
    android:authorities="com.example.secure"
    android:exported="false"
    android:grantUriPermissions="true">
    <!-- 只允许特定路径授予权限 -->
    <grant-uri-permission android:pathPattern="/share/.*" />
    <!-- 其他路径不允许授权 -->
</provider>
```

```java
// 精确授权
Intent shareIntent = new Intent(Intent.ACTION_SEND);
// 只授予特定URI的权限
shareIntent.setData(Uri.parse("content://com.example.secure/share/photo_123.jpg"));
shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
// 设置精确的目标包名
shareIntent.setPackage("com.example.target");
startActivity(shareIntent);
```

### 5.6 实战漏洞案例

**案例1：CVE-2019-2xxx ContentProvider泄露**

某应用通过暴露的ContentProvider泄露用户位置历史数据，攻击者无需任何权限即可获取。

**案例2：Android Contacts Provider注入**

通过构造特定的selection参数，攻击者可以从系统联系人Provider中获取超出预期范围的数据。

---

---

## 📋 内容审核与补充建议

> 针对「ContentProvider安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
