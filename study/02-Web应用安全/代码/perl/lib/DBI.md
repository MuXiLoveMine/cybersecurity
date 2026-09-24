# DBI - Perl 数据库接口

> Perl 的数据库接口模块（DBI），提供统一的数据库访问方式。

---

## 一、安装与连接

### 1.1 安装

```bash
# CPAN 安装
cpan DBI
cpan DBD::mysql      # MySQL 驱动
cpan DBD::Pg         # PostgreSQL 驱动
cpan DBD::SQLite     # SQLite 驱动

# 或 cpanm
cpanm DBI DBD::mysql
```

### 1.2 连接数据库

```perl
use strict;
use warnings;
use DBI;

# MySQL 连接
my $dsn = "DBI:mysql:database=testdb;host=localhost;port=3306";
my $username = "user";
my $password = "password";

my $dbh = DBI->connect($dsn, $username, $password, {
    RaiseError => 1,        # 出错自动 die
    AutoCommit => 1,        # 自动提交
    mysql_enable_utf8 => 1, # UTF-8 支持
}) or die "连接失败: " . DBI->errstr;

print "连接成功\n";

# 断开连接
$dbh->disconnect();
```

### 1.3 不同数据库的 DSN

```perl
# MySQL
my $dsn = "DBI:mysql:database=$db;host=$host;port=$port";

# PostgreSQL
my $dsn = "DBI:Pg:dbname=$db;host=$host;port=$port";

# SQLite
my $dsn = "DBI:SQLite:dbname=$dbfile";

# Oracle
my $dsn = "DBI:Oracle:$db";

# ODBC
my $dsn = "DBI:ODBC:$dsn_name";
```

### 1.4 连接属性

```perl
my %attr = (
    RaiseError       => 1,   # 错误时抛出异常（推荐）
    PrintError       => 0,   # 错误时打印警告
    AutoCommit       => 1,   # 自动提交事务
    ChopBlanks       => 0,   # 去除字符串尾部空格
    LongReadLen      => 8192, # BLOB/TEXT 最大读取长度
    LongTruncOk      => 0,   # 截断长字段是否 OK
    FetchHashKeyName => 'NAME_lc',  # 列名转小写
);

my $dbh = DBI->connect($dsn, $user, $pass, \%attr);
```

---

## 二、基本查询

### 2.1 SELECT 查询

```perl
# 简单查询
my $sth = $dbh->prepare("SELECT * FROM users");
$sth->execute();

# 逐行获取（数组引用）
while (my $row = $sth->fetchrow_arrayref) {
    print "ID: $row->[0], Name: $row->[1]\n";
}

# 逐行获取（哈希引用）
$sth = $dbh->prepare("SELECT id, name, email FROM users");
$sth->execute();

while (my $row = $sth->fetchrow_hashref) {
    print "ID: $row->{id}, Name: $row->{name}\n";
}

# 获取所有行
my $all_rows = $dbh->selectall_arrayref("SELECT * FROM users");
foreach my $row (@$all_rows) {
    print join(', ', @$row) . "\n";
}

# 获取所有行（哈希）
my $all = $dbh->selectall_arrayref(
    "SELECT id, name FROM users",
    { Slice => {} }
);
foreach my $row (@$all) {
    print "$row->{id}: $row->{name}\n";
}

# 获取一列
my @names = $dbh->selectrow_array("SELECT name FROM users");

# 获取一行
my ($id, $name) = $dbh->selectrow_array(
    "SELECT id, name FROM users WHERE id = ?",
    undef,
    $user_id
);

# 获取一行哈希
my $row = $dbh->selectrow_hashref(
    "SELECT * FROM users WHERE id = ?",
    undef,
    $user_id
);

$sth->finish();  # 释放语句句柄
```

### 2.2 INSERT / UPDATE / DELETE

```perl
# INSERT
my $rows_affected = $dbh->do(
    "INSERT INTO users (name, email) VALUES (?, ?)",
    undef,
    'John', 'john@example.com'
);

print "插入了 $rows_affected 行\n";
print "新记录 ID: " . $dbh->{mysql_insertid} . "\n";  # MySQL
# 或
my $new_id = $dbh->last_insert_id(undef, undef, 'users', 'id');

# UPDATE
my $updated = $dbh->do(
    "UPDATE users SET email = ? WHERE id = ?",
    undef,
    'new@example.com', 1
);
print "更新了 $updated 行\n";

# DELETE
my $deleted = $dbh->do(
    "DELETE FROM users WHERE id = ?",
    undef,
    1
);
print "删除了 $deleted 行\n";
```

### 2.3 预处理语句

```perl
# prepare + execute 多次执行
my $sth = $dbh->prepare("INSERT INTO users (name, age) VALUES (?, ?)");

my @users = (
    ['Alice', 25],
    ['Bob', 30],
    ['Charlie', 35],
);

foreach my $user (@users) {
    $sth->execute($user->[0], $user->[1]);
}

$sth->finish();
```

---

## 三、安全相关内容

### 3.1 SQL 注入防护

```perl
# ===== 危险：直接拼接 SQL（SQL 注入）=====
my $username = $ARGV[0];  # 用户输入
my $sql = "SELECT * FROM users WHERE username = '$username'";
my $sth = $dbh->prepare($sql);
$sth->execute();
# 攻击: ' OR '1'='1
# 结果: SELECT * FROM users WHERE username = '' OR '1'='1'

# ===== 安全：占位符（参数化查询）=====
my $sth = $dbh->prepare("SELECT * FROM users WHERE username = ?");
$sth->execute($username);  # ✅ 安全！

# 多个参数
my $sth = $dbh->prepare(
    "SELECT * FROM users WHERE name = ? AND age > ?"
);
$sth->execute($name, $min_age);

# ===== 不能用占位符的情况 =====
# 表名、列名、ORDER BY 等不能用占位符
# 需要用白名单验证

# 白名单验证列名
my %allowed_columns = (
    id => 1,
    name => 1,
    email => 1,
    created_at => 1,
);

my $sort_by = $param{sort} || 'id';
unless ($allowed_columns{$sort_by}) {
    $sort_by = 'id';  # 默认值
}

# 注意：列名直接拼接，所以必须白名单验证！
my $sql = "SELECT * FROM users ORDER BY $sort_by";
my $sth = $dbh->prepare($sql);
$sth->execute();

# LIKE 查询的正确处理
my $pattern = "%$search%";  # 先构造带通配符的字符串
my $sth = $dbh->prepare("SELECT * FROM users WHERE name LIKE ?");
$sth->execute($pattern);  # 作为参数传入
```

### 3.2 事务处理

```perl
use strict;
use warnings;
use DBI;

my $dbh = DBI->connect($dsn, $user, $pass, {
    RaiseError => 1,
    AutoCommit => 1,  # 默认自动提交
}) or die DBI->errstr;

# 开始事务
$dbh->begin_work();

eval {
    # 操作 1：扣钱
    $dbh->do(
        "UPDATE accounts SET balance = balance - ? WHERE id = ?",
        undef,
        100, 1
    );
    
    # 检查是否成功
    if ($dbh->do(
        "UPDATE accounts SET balance = balance - ? WHERE id = ?",
        undef,
        100, 1
    ) < 1) {
        die "扣款失败或余额不足";
    }
    
    # 操作 2：加钱
    $dbh->do(
        "UPDATE accounts SET balance = balance + ? WHERE id = ?",
        undef,
        100, 2
    );
    
    # 提交事务
    $dbh->commit();
    print "转账成功\n";
};

if ($@) {
    # 出错，回滚
    warn "转账失败: $@";
    eval { $dbh->rollback() };
}
```

### 3.3 密码存储安全

```perl
use strict;
use warnings;
use DBI;
use Digest::SHA qw(sha512_hex);
use Crypt::Eksblowfish::Bcrypt qw(bcrypt_hash);  # 推荐 bcrypt

# ===== 不推荐：SHA + 盐 =====
sub hash_password_sha {
    my ($password, $salt) = @_;
    return sha512_hex($salt . $password);
}

# ===== 推荐：bcrypt =====
# 需要安装 Crypt::Eksblowfish::Bcrypt
sub hash_password_bcrypt {
    my ($password) = @_;
    
    # 生成随机盐（16 字节 base64 编码）
    my $salt = generate_salt();
    
    # bcrypt 哈希
    my $hash = bcrypt_hash({
        key_nul => 1,
        cost => 12,
        salt => $salt,
    }, $password);
    
    # 返回格式化字符串
    return sprintf('$2a$%02d$%s%s', 12, $salt, $hash);
}

sub verify_password_bcrypt {
    my ($password, $stored_hash) = @_;
    
    # 解析存储的哈希
    if ($stored_hash =~ /^\$2a\$(\d{2})\$([A-Za-z0-9.\/]{22})(.+)$/) {
        my ($cost, $salt, $hash) = ($1, $2, $3);
        
        my $new_hash = bcrypt_hash({
            key_nul => 1,
            cost => $cost,
            salt => $salt,
        }, $password);
        
        return $new_hash eq $hash;
    }
    
    return 0;
}

sub generate_salt {
    # 生成 16 字节随机盐，转为 base64
    my @chars = ('A'..'Z', 'a'..'z', '0'..'9', '.', '/');
    my $salt = '';
    $salt .= $chars[rand @chars] for 1..22;
    return $salt;
}

# ===== 正确的验证流程 =====
sub login {
    my ($dbh, $username, $password) = @_;
    
    my $sth = $dbh->prepare(
        "SELECT password_hash FROM users WHERE username = ?"
    );
    $sth->execute($username);
    
    my ($stored_hash) = $sth->fetchrow_array;
    
    if ($stored_hash && verify_password_bcrypt($password, $stored_hash)) {
        return 1;  # 登录成功
    }
    
    return 0;  # 登录失败
}
```

### 3.4 错误处理

```perl
use strict;
use warnings;
use DBI;

# 方法1：RaiseError（推荐，出错自动 die）
my $dbh = DBI->connect($dsn, $user, $pass, { RaiseError => 1 });
eval {
    $dbh->do("SOME BAD SQL");
};
if ($@) {
    # 处理错误
    log_error("数据库错误: $@");
    # 不要把详细错误信息返回给用户
    print "数据库操作失败，请稍后重试\n";
}

# 方法2：手动检查错误
my $dbh = DBI->connect($dsn, $user, $pass, { RaiseError => 0, PrintError => 0 });
my $sth = $dbh->prepare($sql);
unless ($sth) {
    my $error = $dbh->errstr;
    log_error("Prepare 失败: $error");
    die "操作失败";
}

my $result = $sth->execute(@params);
if (!defined $result) {
    my $error = $sth->errstr;
    log_error("Execute 失败: $error");
    die "操作失败";
}

# 错误信息
$dbh->err;       # 错误码
$dbh->errstr;    # 错误信息
$dbh->state;     # SQLSTATE
$sth->err;       # 语句级错误码
$sth->errstr;    # 语句级错误信息
```

---

## 四、常用方法速查

| 方法 | 说明 |
|------|------|
| `DBI->connect()` | 连接数据库 |
| `$dbh->disconnect()` | 断开连接 |
| `$dbh->prepare()` | 预处理 SQL |
| `$dbh->do()` | 执行非 SELECT |
| `$dbh->selectrow_array()` | 获取一行（数组） |
| `$dbh->selectrow_hashref()` | 获取一行（哈希） |
| `$dbh->selectall_arrayref()` | 获取所有行 |
| `$dbh->begin_work()` | 开始事务 |
| `$dbh->commit()` | 提交事务 |
| `$dbh->rollback()` | 回滚事务 |
| `$sth->execute()` | 执行预处理 |
| `$sth->fetchrow_arrayref()` | 获取行（数组引用） |
| `$sth->fetchrow_hashref()` | 获取行（哈希引用） |
| `$sth->finish()` | 释放语句句柄 |
| `$sth->rows()` | 受影响行数 |
