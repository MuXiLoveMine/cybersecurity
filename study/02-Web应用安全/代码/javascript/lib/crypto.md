# crypto - Node.js 加密模块

> Node.js 内置加密模块，提供哈希、加密、签名等功能。

---

## 一、引入

```javascript
const crypto = require('crypto');
```

---

## 二、哈希算法

### 2.1 基本哈希

```javascript
// createHash - 创建哈希对象
const hash = crypto.createHash('sha256');

// 更新哈希内容
hash.update('Hello World');

// 获取哈希结果（hex 格式）
console.log(hash.digest('hex'));
// 7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069

// 一行写法
console.log(crypto.createHash('md5').update('hello').digest('hex'));
// 5d41402abc4b2a76b9719d911017c592

// 支持的算法: md5, sha1, sha256, sha384, sha512, sha3-256, ...
// digest 格式: hex, base64, base64url, latin1, Buffer
```

### 2.2 文件哈希

```javascript
const fs = require('fs');
const crypto = require('crypto');

// 流式计算大文件哈希
function hashFile(filepath, algorithm = 'sha256') {
    return new Promise((resolve, reject) => {
        const hash = crypto.createHash(algorithm);
        const stream = fs.createReadStream(filepath);
        
        stream.on('data', data => hash.update(data));
        stream.on('end', () => resolve(hash.digest('hex')));
        stream.on('error', reject);
    });
}

hashFile('file.txt').then(hash => console.log('文件哈希:', hash));
```

### 2.3 HMAC（带密钥的哈希）

```javascript
// createHmac - 基于密钥的消息认证码
const hmac = crypto.createHmac('sha256', 'secret-key');
hmac.update('message');
console.log(hmac.digest('hex'));

// 封装
function generateHMAC(message, secret, algorithm = 'sha256') {
    return crypto.createHmac(algorithm, secret)
        .update(message)
        .digest('hex');
}

function verifyHMAC(message, secret, signature, algorithm = 'sha256') {
    const expected = generateHMAC(message, secret, algorithm);
    // 使用 timingSafeEqual 防止时序攻击
    const a = Buffer.from(signature, 'hex');
    const b = Buffer.from(expected, 'hex');
    return a.length === b.length && crypto.timingSafeEqual(a, b);
}
```

---

## 三、对称加密

### 3.1 AES 加密/解密

```javascript
// AES-256-CBC 模式
const algorithm = 'aes-256-cbc';
const key = crypto.randomBytes(32);  // 256 位密钥
const iv = crypto.randomBytes(16);   // 初始化向量

// 加密
function encrypt(text, key, iv) {
    const cipher = crypto.createCipheriv(algorithm, key, iv);
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return encrypted;
}

// 解密
function decrypt(encrypted, key, iv) {
    const decipher = crypto.createDecipheriv(algorithm, key, iv);
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
}

// 使用
const message = 'Hello, this is a secret message';
const encrypted = encrypt(message, key, iv);
const decrypted = decrypt(encrypted, key, iv);

console.log('加密后:', encrypted);
console.log('解密后:', decrypted);
```

### 3.2 常用模式

```javascript
/*
    常见对称加密算法：
    
    - AES-128-CBC / AES-192-CBC / AES-256-CBC
      密码分组链接模式，需要 IV
      
    - AES-128-ECB / AES-192-ECB / AES-256-ECB
      电子密码本模式，不安全（不推荐）
      
    - AES-256-GCM
      认证加密模式，提供机密性和完整性（推荐）
      产生认证标签 (authTag)
      
    - AES-256-CTR
      计数器模式，流密码模式
*/

// ===== GCM 模式（推荐）=====
function encryptGCM(text, key) {
    const iv = crypto.randomBytes(12);  // GCM 推荐 12 字节 IV
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
    
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag().toString('hex');
    
    return {
        iv: iv.toString('hex'),
        encrypted,
        authTag
    };
}

function decryptGCM(encryptedData, key) {
    const iv = Buffer.from(encryptedData.iv, 'hex');
    const authTag = Buffer.from(encryptedData.authTag, 'hex');
    
    const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
    decipher.setAuthTag(authTag);
    
    let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
}
```

---

## 四、非对称加密

### 4.1 密钥生成

```javascript
// 生成 RSA 密钥对
const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 2048,  // 密钥长度（推荐 2048 或 4096）
    publicKeyEncoding: {
        type: 'spki',
        format: 'pem'
    },
    privateKeyEncoding: {
        type: 'pkcs8',
        format: 'pem',
        cipher: 'aes-256-cbc',  // 可选：加密私钥
        passphrase: 'passphrase' // 私钥密码
    }
});

console.log('公钥:', publicKey);
console.log('私钥:', privateKey);

// 从 PEM 加载密钥
const pubKey = crypto.createPublicKey(publicKeyPem);
const privKey = crypto.createPrivateKey({
    key: privateKeyPem,
    passphrase: 'passphrase'  // 如果私钥加密了
});
```

### 4.2 公钥加密 / 私钥解密

```javascript
// 公钥加密（任何人都可以用公钥加密，只有私钥能解密）
function publicEncrypt(publicKey, text) {
    const encrypted = crypto.publicEncrypt(
        publicKey,
        Buffer.from(text, 'utf8')
    );
    return encrypted.toString('base64');
}

// 私钥解密
function privateDecrypt(privateKey, encryptedBase64) {
    const decrypted = crypto.privateDecrypt(
        privateKey,
        Buffer.from(encryptedBase64, 'base64')
    );
    return decrypted.toString('utf8');
}

// 使用
const encrypted = publicEncrypt(publicKey, '秘密消息');
const decrypted = privateDecrypt(privateKey, encrypted);
```

### 4.3 签名与验证

```javascript
// 私钥签名（只有私钥持有者能签名，任何人可用公钥验证）
function sign(privateKey, data) {
    const sign = crypto.createSign('SHA256');
    sign.update(data);
    sign.end();
    return sign.sign(privateKey, 'hex');
}

// 公钥验证
function verify(publicKey, data, signature) {
    const verify = crypto.createVerify('SHA256');
    verify.update(data);
    verify.end();
    return verify.verify(publicKey, signature, 'hex');
}

// 使用
const message = 'Hello, I am Alice';
const signature = sign(privateKey, message);
const isValid = verify(publicKey, message, signature);
console.log('签名有效:', isValid);
```

---

## 五、安全相关内容

### 5.1 密码哈希（bcrypt/PBKDF2）

```javascript
// ===== PBKDF2（推荐用于密码哈希）=====

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const iterations = 100000;
    const keylen = 64;
    const digest = 'sha512';
    
    const derivedKey = crypto.pbkdf2Sync(
        password, salt, iterations, keylen, digest
    ).toString('hex');
    
    return `pbkdf2_${digest}$${iterations}$${salt}$${derivedKey}`;
}

function verifyPassword(password, storedHash) {
    const [algorithm, iterationsStr, salt, key] = storedHash.split('$');
    const iterations = parseInt(iterationsStr);
    const digest = algorithm.split('_')[1];
    const keylen = key.length / 2;
    
    const derivedKey = crypto.pbkdf2Sync(
        password, salt, iterations, keylen, digest
    ).toString('hex');
    
    // 防止时序攻击
    const a = Buffer.from(key, 'hex');
    const b = Buffer.from(derivedKey, 'hex');
    return a.length === b.length && crypto.timingSafeEqual(a, b);
}

// 使用
const hash = hashPassword('myPassword123');
console.log('哈希:', hash);
console.log('验证正确:', verifyPassword('myPassword123', hash));
console.log('验证错误:', verifyPassword('wrongPassword', hash));

/*
    注意：
    - 生产环境推荐使用 bcrypt 或 scrypt 库（专门为密码设计）
    - PBKDF2 可以调整迭代次数，越慢越安全
    - 永远不要用 md5/sha1 直接哈希密码（太快了）
*/
```

### 5.2 随机数与安全令牌

```javascript
// 加密安全的随机数
crypto.randomBytes(16).toString('hex');  // 32 字符十六进制
crypto.randomBytes(32).toString('base64');

// 生成 UUID（v4）
crypto.randomUUID();  // Node.js 14.17+

// 生成安全的令牌
function generateToken(length = 32) {
    return crypto.randomBytes(length).toString('hex');
}

// 生成数字验证码
function generateNumericCode(length = 6) {
    const bytes = crypto.randomBytes(length);
    let code = '';
    for (let i = 0; i < length; i++) {
        code += bytes[i] % 10;  // 取模得到 0-9（有偏差，不推荐用于高安全场景）
    }
    return code;
}

// 更均匀的数字验证码
function generateSecureCode(length = 6) {
    const max = Math.pow(10, length);
    let num;
    // 使用拒绝采样确保均匀分布
    const bytes = crypto.randomBytes(4);
    num = bytes.readUInt32BE(0) % max;
    return num.toString().padStart(length, '0');
}

/*
    Math.random() vs crypto.randomBytes()
    
    - Math.random() 不是加密安全的伪随机数
    - 不要用 Math.random() 生成密码、令牌、密钥等
    - crypto.randomBytes() 使用操作系统的 CSPRNG
*/
```

### 5.3 时序攻击防护

```javascript
/*
    时序攻击 (Timing Attack):
    通过测量比较操作的时间差异来推断信息
    
    例如：比较两个字符串时，通常从第一个字符开始比较，
    遇到不相等就返回。攻击者可以通过测量响应时间
    来推断正确字符串的每一位。
*/

// ❌ 不安全：普通字符串比较（可能被时序攻击）
function insecureCompare(a, b) {
    return a === b;  // JS 中 === 也是逐个字符比较
}

// ✅ 安全：使用 timingSafeEqual
function secureCompare(a, b) {
    const bufA = Buffer.from(a);
    const bufB = Buffer.from(b);
    if (bufA.length !== bufB.length) {
        return false;  // 长度不同直接返回（但注意：这也泄露了长度信息）
    }
    return crypto.timingSafeEqual(bufA, bufB);
}

// 恒定时间比较（即使长度不同也不泄露）
function constantTimeCompare(a, b) {
    const bufA = Buffer.from(a);
    const bufB = Buffer.from(b);
    
    // 取较短的长度
    const len = Math.min(bufA.length, bufB.length);
    let diff = bufA.length ^ bufB.length;  // 长度差异
    
    for (let i = 0; i < len; i++) {
        diff |= bufA[i] ^ bufB[i];
    }
    
    return diff === 0;
}
```

### 5.4 CSRF Token 生成

```javascript
// 生成 CSRF Token
function generateCsrfToken() {
    return crypto.randomBytes(32).toString('hex');
}

// 验证 CSRF Token
function verifyCsrfToken(token, expected) {
    if (!token || !expected) return false;
    const a = Buffer.from(token, 'hex');
    const b = Buffer.from(expected, 'hex');
    return a.length === b.length && crypto.timingSafeEqual(a, b);
}
```

---

## 六、安全注意事项

| 注意点 | 说明 |
|-------|------|
| 密码哈希 | 用 bcrypt/scrypt/PBKDF2，不要用 md5/sha1 |
| 随机数 | 安全相关用 crypto.randomBytes，不要用 Math.random |
| 字符串比较 | 用 timingSafeEqual 防止时序攻击 |
| 对称加密 | 推荐 AES-256-GCM（认证加密） |
| IV/Nonce | 必须随机且唯一，不能重复使用 |
| 密钥管理 | 不要硬编码密钥，使用密钥管理服务 |
| 填充攻击 | CBC 模式可能受 Padding Oracle 攻击，用 GCM |
| 哈希长度 | SHA-1 不再安全，用 SHA-256 及以上 |
| RSA 密钥长度 | 至少 2048 位，推荐 4096 位 |
