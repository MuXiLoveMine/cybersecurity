---

## 四、高级实战案例

### 4.1 安全 Web 服务开发

使用 Rust 构建安全的 Web 服务，利用 Rust 的内存安全特性。

```rust
use axum::{
    extract::{Path, State, Json},
    http::StatusCode,
    routing::{get, post},
    Router,
    response::IntoResponse,
};
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};
use jsonwebtoken::{encode, decode, Header, Validation, EncodingKey, DecodingKey};
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};
use uuid::Uuid;
use bcrypt::{hash, verify, DEFAULT_COST};

// ===== 安全配置 =====
#[derive(Clone)]
struct AppState {
    jwt_secret: String,
    db_pool: sqlx::SqlitePool,
}

// ===== 用户数据结构 =====
#[derive(Debug, Serialize, Deserialize)]
struct User {
    id: Uuid,
    username: String,
    #[serde(skip_serializing)]  // 不序列化密码哈希
    password_hash: String,
    role: String,
    created_at: chrono::NaiveDateTime,
}

#[derive(Debug, Deserialize)]
struct RegisterRequest {
    username: String,
    password: String,
}

#[derive(Debug, Deserialize)]
struct LoginRequest {
    username: String,
    password: String,
}

#[derive(Debug, Serialize)]
struct LoginResponse {
    token: String,
    user: UserInfo,
}

#[derive(Debug, Serialize)]
struct UserInfo {
    id: Uuid,
    username: String,
    role: String,
}

// ===== JWT Claims =====
#[derive(Debug, Serialize, Deserialize)]
struct Claims {
    sub: String,     // 用户 ID
    username: String,
    role: String,
    exp: usize,      // 过期时间
    iat: usize,      // 签发时间
}

// ===== 输入验证 =====
fn validate_username(username: &str) -> Result<(), String> {
    if username.len() < 3 || username.len() > 32 {
        return Err("用户名长度必须在 3-32 之间".into());
    }
    if !username.chars().all(|c| c.is_alphanumeric() || c == '_' || c == '-') {
        return Err("用户名只能包含字母、数字、下划线和连字符".into());
    }
    Ok(())
}

fn validate_password(password: &str) -> Result<(), String> {
    if password.len() < 8 {
        return Err("密码至少 8 位".into());
    }
    if !password.chars().any(|c| c.is_uppercase()) {
        return Err("密码必须包含大写字母".into());
    }
    if !password.chars().any(|c| c.is_lowercase()) {
        return Err("密码必须包含小写字母".into());
    }
    if !password.chars().any(|c| c.is_numeric()) {
        return Err("密码必须包含数字".into());
    }
    Ok(())
}

// ===== 密码哈希 =====
fn hash_password(password: &str) -> Result<String, String> {
    hash(password, DEFAULT_COST).map_err(|e| format!("密码哈希失败: {}", e))
}

fn verify_password(password: &str, hash: &str) -> Result<bool, String> {
    verify(password, hash).map_err(|e| format!("密码验证失败: {}", e))
}

// ===== JWT 工具 =====
fn generate_token(user: &User, secret: &str) -> Result<String, String> {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs() as usize;
    
    let claims = Claims {
        sub: user.id.to_string(),
        username: user.username.clone(),
        role: user.role.clone(),
        exp: now + 3600,  // 1 小时过期
        iat: now,
    };
    
    encode(
        &Header::default(),
        &claims,
        &EncodingKey::from_secret(secret.as_bytes()),
    ).map_err(|e| format!("JWT 生成失败: {}", e))
}

fn validate_token(token: &str, secret: &str) -> Result<Claims, String> {
    let token_data = decode::<Claims>(
        token,
        &DecodingKey::from_secret(secret.as_bytes()),
        &Validation::default(),
    ).map_err(|e| format!("JWT 验证失败: {}", e))?;
    
    Ok(token_data.claims)
}

// ===== API 处理函数 =====

// 用户注册
async fn register(
    State(state): State<Arc<AppState>>,
    Json(req): Json<RegisterRequest>,
) -> Result<impl IntoResponse, (StatusCode, String)> {
    // 输入验证
    validate_username(&req.username)
        .map_err(|e| (StatusCode::BAD_REQUEST, e))?;
    validate_password(&req.password)
        .map_err(|e| (StatusCode::BAD_REQUEST, e))?;
    
    // 检查用户名是否已存在
    let exists: Option<i64> = sqlx::query_scalar(
        "SELECT COUNT(*) FROM users WHERE username = ?"
    )
    .bind(&req.username)
    .fetch_one(&state.db_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("数据库错误: {}", e)))?;
    
    if exists.unwrap_or(0) > 0 {
        return Err((StatusCode::CONFLICT, "用户名已存在".into()));
    }
    
    // 密码哈希
    let password_hash = hash_password(&req.password)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e))?;
    
    // 创建用户
    let user_id = Uuid::new_v4();
    sqlx::query(
        "INSERT INTO users (id, username, password_hash, role) VALUES (?, ?, ?, 'user')"
    )
    .bind(user_id)
    .bind(&req.username)
    .bind(&password_hash)
    .execute(&state.db_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("数据库错误: {}", e)))?;
    
    Ok((StatusCode::CREATED, Json(serde_json::json!({
        "message": "注册成功",
        "user_id": user_id
    }))))
}

// 用户登录
async fn login(
    State(state): State<Arc<AppState>>,
    Json(req): Json<LoginRequest>,
) -> Result<impl IntoResponse, (StatusCode, String)> {
    // 查找用户
    let row: Option<(String, String, String)> = sqlx::query_as(
        "SELECT id, username, password_hash FROM users WHERE username = ?"
    )
    .bind(&req.username)
    .fetch_optional(&state.db_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, format!("数据库错误: {}", e)))?;
    
    let (id_str, username, password_hash) = match row {
        Some(r) => r,
        None => {
            // 防止用户名枚举，返回相同错误信息
            return Err((StatusCode::UNAUTHORIZED, "用户名或密码错误".into()));
        }
    };
    
    // 验证密码
    let valid = verify_password(&req.password, &password_hash)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e))?;
    
    if !valid {
        return Err((StatusCode::UNAUTHORIZED, "用户名或密码错误".into()));
    }
    
    let user_id = Uuid::parse_str(&id_str).unwrap();
    
    // 生成 JWT
    let user = User {
        id: user_id,
        username: username.clone(),
        password_hash,
        role: "user".into(),
        created_at: chrono::Utc::now().naive_utc(),
    };
    
    let token = generate_token(&user, &state.jwt_secret)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e))?;
    
    Ok(Json(LoginResponse {
        token,
        user: UserInfo {
            id: user.id,
            username: user.username,
            role: user.role,
        },
    }))
}

// 受保护的路由
async fn protected_route(
    State(state): State<Arc<AppState>>,
    headers: axum::http::HeaderMap,
) -> Result<impl IntoResponse, (StatusCode, String)> {
    // 从 header 提取 token
    let auth_header = headers.get("Authorization")
        .and_then(|h| h.to_str().ok())
        .ok_or((StatusCode::UNAUTHORIZED, "缺少 Authorization header".to_string()))?;
    
    let token = auth_header.strip_prefix("Bearer ")
        .ok_or((StatusCode::UNAUTHORIZED, "无效的 Authorization 格式".to_string()))?;
    
    // 验证 token
    let claims = validate_token(token, &state.jwt_secret)
        .map_err(|e| (StatusCode::UNAUTHORIZED, e))?;
    
    Ok(Json(serde_json::json!({
        "message": "访问成功",
        "user_id": claims.sub,
        "username": claims.username,
        "role": claims.role
    })))
}

// ===== 主函数 =====
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 初始化数据库
    let db_pool = sqlx::SqlitePool::connect("sqlite:./app.db").await?;
    
    sqlx::query(
        r#"CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )"#
    ).execute(&db_pool).await?;
    
    let state = Arc::new(AppState {
        jwt_secret: std::env::var("JWT_SECRET")
            .unwrap_or_else(|_| "your-secret-key-change-in-production".into()),
        db_pool,
    });
    
    // 构建路由
    let app = Router::new()
        .route("/api/register", post(register))
        .route("/api/login", post(login))
        .route("/api/protected", get(protected_route))
        .with_state(state);
    
    // 启动服务
    let listener = tokio::net::TcpListener::bind("127.0.0.1:8080").await?;
    println!("服务器运行在 http://127.0.0.1:8080");
    axum::serve(listener, app).await?;
    
    Ok(())
}
```

### 4.2 加密工具库

Rust 加密库高级用法。

```rust
use aes_gcm::{
    aead::{Aead, KeyInit, generic_array::GenericArray},
    Aes256Gcm, Nonce,
};
use rand::RngCore;
use rand::rngs::OsRng;
use sha2::{Sha256, Digest};
use hmac::{Hmac, Mac};
use ed25519_dalek::{Signature, Signer, Verifier, SigningKey, VerifyingKey};
use argon2::{Argon2, PasswordHasher, PasswordVerifier, password_hash::{SaltString, PasswordHash}};
use base64::{Engine as _, engine::general_purpose};
use zeroize::Zeroize;

type HmacSha256 = Hmac<Sha256>;

// ===== AES-GCM 对称加密 =====
pub struct AesEncryptor {
    cipher: Aes256Gcm,
}

impl AesEncryptor {
    pub fn new(key: &[u8; 32]) -> Self {
        let key = GenericArray::from_slice(key);
        Self {
            cipher: Aes256Gcm::new(key),
        }
    }
    
    pub fn encrypt(&self, plaintext: &[u8], associated_data: &[u8]) -> Result<Vec<u8>, String> {
        // 生成随机 nonce (12 bytes)
        let mut nonce_bytes = [0u8; 12];
        OsRng.fill_bytes(&mut nonce_bytes);
        let nonce = Nonce::from_slice(&nonce_bytes);
        
        // 加密
        let ciphertext = self.cipher
            .encrypt(nonce, plaintext)
            .map_err(|e| format!("加密失败: {}", e))?;
        
        // 返回 nonce + ciphertext
        let mut result = Vec::with_capacity(nonce_bytes.len() + ciphertext.len());
        result.extend_from_slice(&nonce_bytes);
        result.extend_from_slice(&ciphertext);
        Ok(result)
    }
    
    pub fn decrypt(&self, data: &[u8], associated_data: &[u8]) -> Result<Vec<u8>, String> {
        if data.len() < 12 {
            return Err("数据太短".into());
        }
        
        // 分离 nonce 和密文
        let (nonce_bytes, ciphertext) = data.split_at(12);
        let nonce = Nonce::from_slice(nonce_bytes);
        
        // 解密
        self.cipher
            .decrypt(nonce, ciphertext)
            .map_err(|e| format!("解密失败: {}", e))
    }
}

// ===== 哈希函数 =====
pub fn sha256_hash(data: &[u8]) -> Vec<u8> {
    let mut hasher = Sha256::new();
    hasher.update(data);
    hasher.finalize().to_vec()
}

pub fn sha256_hex(data: &[u8]) -> String {
    let hash = sha256_hash(data);
    hash.iter().map(|b| format!("{:02x}", b)).collect()
}

// ===== HMAC =====
pub fn hmac_sha256(key: &[u8], data: &[u8]) -> Result<Vec<u8>, String> {
    let mut mac = HmacSha256::new_from_slice(key)
        .map_err(|e| format!("HMAC 初始化失败: {}", e))?;
    mac.update(data);
    Ok(mac.finalize().into_bytes().to_vec())
}

pub fn hmac_verify(key: &[u8], data: &[u8], expected: &[u8]) -> Result<bool, String> {
    let mut mac = HmacSha256::new_from_slice(key)
        .map_err(|e| format!("HMAC 初始化失败: {}", e))?;
    mac.update(data);
    Ok(mac.verify_slice(expected).is_ok())
}

// ===== 密码哈希 (Argon2id) =====
pub fn hash_password(password: &str) -> Result<String, String> {
    let salt = SaltString::generate(&mut OsRng);
    let argon2 = Argon2::default();
    
    let password_hash = argon2
        .hash_password(password.as_bytes(), &salt)
        .map_err(|e| format!("密码哈希失败: {}", e))?;
    
    Ok(password_hash.to_string())
}

pub fn verify_password(password: &str, hash: &str) -> Result<bool, String> {
    let parsed_hash = PasswordHash::new(hash)
        .map_err(|e| format!("解析哈希失败: {}", e))?;
    
    Ok(Argon2::default()
        .verify_password(password.as_bytes(), &parsed_hash)
        .is_ok())
}

// ===== Ed25519 数字签名 =====
pub struct Ed25519KeyPair {
    signing_key: SigningKey,
}

impl Ed25519KeyPair {
    pub fn generate() -> Self {
        let mut csprng = OsRng;
        let signing_key = SigningKey::generate(&mut csprng);
        Self { signing_key }
    }
    
    pub fn from_seed(seed: &[u8; 32]) -> Self {
        Self {
            signing_key: SigningKey::from_bytes(seed),
        }
    }
    
    pub fn public_key_bytes(&self) -> [u8; 32] {
        self.signing_key.verifying_key().to_bytes()
    }
    
    pub fn sign(&self, message: &[u8]) -> Vec<u8> {
        let signature = self.signing_key.sign(message);
        signature.to_bytes().to_vec()
    }
}

pub fn verify_ed25519(public_key_bytes: &[u8; 32], message: &[u8], signature_bytes: &[u8; 64]) -> bool {
    let verifying_key = match VerifyingKey::from_bytes(public_key_bytes.into()) {
        Ok(k) => k,
        Err(_) => return false,
    };
    
    let signature = Signature::from_bytes(signature_bytes.into());
    verifying_key.verify(message, &signature).is_ok()
}

// ===== 安全内存处理 =====
pub struct SecureBuffer {
    data: Vec<u8>,
}

impl SecureBuffer {
    pub fn new(data: Vec<u8>) -> Self {
        Self { data }
    }
    
    pub fn as_slice(&self) -> &[u8] {
        &self.data
    }
}

impl Drop for SecureBuffer {
    fn drop(&mut self) {
        // 安全清零敏感数据
        self.data.zeroize();
    }
}

// ===== 测试 =====
fn main() {
    // AES 加密测试
    let mut key = [0u8; 32];
    OsRng.fill_bytes(&mut key);
    let encryptor = AesEncryptor::new(&key);
    
    let plaintext = b"Hello, Rust!";
    let encrypted = encryptor.encrypt(plaintext, b"additional-data").unwrap();
    let decrypted = encryptor.decrypt(&encrypted, b"additional-data").unwrap();
    
    println!("AES 加密测试: {}", plaintext == decrypted.as_slice());
    println!("密文 (Base64): {}", general_purpose::STANDARD.encode(&encrypted));
    
    // 哈希测试
    println!("SHA256: {}", sha256_hex(b"test"));
    
    // 密码哈希测试
    let pw_hash = hash_password("MySecurePass123!").unwrap();
    println!("密码哈希验证: {}", verify_password("MySecurePass123!", &pw_hash).unwrap());
    
    // Ed25519 测试
    let keypair = Ed25519KeyPair::generate();
    let message = b"Important message";
    let signature = keypair.sign(message);
    let pub_key = keypair.public_key_bytes();
    
    let mut sig_array = [0u8; 64];
    sig_array.copy_from_slice(&signature);
    println!("Ed25519 验证: {}", verify_ed25519(&pub_key, message, &sig_array));
}
```

---

## 五、进阶学习资源

### 5.1 Rust 安全资源

- **Rust 官方安全指南**：https://www.rust-lang.org/security
- **Rust 安全代码指南**：https://rust-secure-code.github.io/
- **Rust API 指南**：https://rust-lang.github.io/api-guidelines/
- **Rust 异步编程**：https://rust-lang.github.io/async-book/

### 5.2 安全工具与库

- **加密库**：
  - RustCrypto — Rust 加密生态：https://github.com/RustCrypto
  - ring — 加密库：https://github.com/briansmith/ring
  - rustls — 现代 TLS 库：https://github.com/rustls/rustls
  - orion — 易用加密库

- **Web 框架**：
  - Actix Web — 高性能 Web 框架
  - Axum — Tokio 生态 Web 框架
  - Rocket — 声明式 Web 框架
  - Warp — 组合式 Web 框架

- **安全审计工具**：
  - cargo-audit — 依赖漏洞扫描
  - cargo-deny — 依赖许可证检查
  - cargo-outdated — 依赖过期检查
  - clippy — 代码检查（包含安全建议）
  - cargo-geiger — unsafe 代码检测

### 5.3 Rust 安全审计

常见 Rust 安全问题：
- unsafe 代码使用不当
- 整数溢出（debug 模式检测，release 不检测）
- 竞争条件（Rust 防止数据竞争但不防止竞态条件）
- 内存泄漏（Rc 循环引用）
- unwrap/expect 滥用导致 panic
- 不安全的 FFI 调用
- 逻辑漏洞（类型系统无法防止）

审计工具：
- **cargo-audit**：https://github.com/RustSec/rustsec/tree/main/cargo-audit
- **cargo-geiger**：https://github.com/geiger-rs/cargo-geiger
- **cargo-clippy**：https://github.com/rust-lang/rust-clippy

### 5.4 CTF 与练习平台

- **Rust Playground**：https://play.rust-lang.org/
- **Rust by Example**：https://doc.rust-lang.org/rust-by-example/
- **Rustlings**：https://github.com/rust-lang/rustlings
- **Hack The Box**：https://www.hackthebox.com/
- **TryHackMe**：https://tryhackme.com/

### 5.5 推荐书籍

- **Rust 编程**：
  - 《Rust 程序设计》（The Rust Programming Language）
  - 《Rust 权威指南》
  - 《Rust 编程之道》
  - 《深入浅出 Rust》

- **系统安全**：
  - 《Rust 编程实战》
  - 《Black Hat Rust》
  - 《Rust for Rustaceans》

### 5.6 社区与博客

- **Rust 官方博客**：https://blog.rust-lang.org/
- **Rust Security Working Group**：https://github.com/rust-secure-code
- **RustSec**：https://rustsec.org/
- **FreeBuf**：https://www.freebuf.com/
- **安全客**：https://www.anquanke.com/

### 5.7 进阶学习路线

**第 1 阶段：Rust 精通（2-3月）**
- 所有权与借用
- 生命周期与 trait
- 异步编程
- 宏与元编程

**第 2 阶段：系统编程（2-3月）**
- 内存布局与 unsafe
- FFI 与 C 互操作
- 并发与并行
- 网络编程

**第 3 阶段：安全开发（2-3月）**
- 加密库使用
- Web 安全开发
- 安全审计方法
- 漏洞模式识别

**第 4 阶段：工具开发（2-3月）**
- 安全工具开发
- 静态分析工具
- 模糊测试工具
- 逆向工具

**第 5 阶段：深入研究（持续）**
- Rust 编译器安全
- Rust 漏洞研究
- 参与开源项目
- 安全工具开发
