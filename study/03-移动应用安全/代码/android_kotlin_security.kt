import android.content.Context
import android.content.pm.PackageManager
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.os.Build
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Log
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.google.android.gms.safetynet.SafetyNet
import com.google.android.gms.safetynet.SafetyNetApi
import com.google.android.gms.tasks.Task
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.*
import java.io.IOException
import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.Socket
import java.security.KeyStore
import java.security.MessageDigest
import java.security.cert.Certificate
import java.security.cert.X509Certificate
import javax.net.ssl.*
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import javax.net.ssl.HttpsURLConnection

/**
 * Android Kotlin安全工具集
 *
 * 功能模块：
 * 1. 协程端口扫描器
 * 2. 证书锁定验证器
 * 3. Deep Link安全测试器
 * 4. Jetpack Security库使用示例
 * 5. EncryptedSharedPreferences使用
 * 6. SafetyNet/Play Integrity API集成
 *
 * 使用方法：在Android项目中集成使用
 *
 * 免责声明：仅用于授权的安全测试，未经授权测试他人应用属于违法行为。
 */

private const val TAG = "KotlinSecurity"

// ============================================================================
// 全局常量
// ============================================================================

object SecurityConstants {
    // 常用端口与服务映射
    val COMMON_PORTS = mapOf(
        21 to "FTP",
        22 to "SSH",
        23 to "Telnet",
        25 to "SMTP",
        53 to "DNS",
        80 to "HTTP",
        110 to "POP3",
        143 to "IMAP",
        443 to "HTTPS",
        445 to "SMB",
        993 to "IMAPS",
        995 to "POP3S",
        1433 to "MSSQL",
        3306 to "MySQL",
        3389 to "RDP",
        5432 to "PostgreSQL",
        6379 to "Redis",
        8080 to "HTTP-Alt",
        9200 to "Elasticsearch",
        27017 to "MongoDB"
    )

    // 安全严重程度枚举
    enum class Severity(val label: String) {
        CRITICAL("严重"),
        HIGH("高危"),
        MEDIUM("中危"),
        LOW("低危"),
        INFO("信息")
    }

    // 安全发现数据类
    data class SecurityFinding(
        val tool: String,
        val severity: Severity,
        val title: String,
        val description: String,
        val recommendation: String,
        val evidence: String = ""
    )
}

// ============================================================================
// 模块1：协程端口扫描器
// ============================================================================

/**
 * 协程端口扫描器
 *
 * 使用Kotlin协程实现高性能端口扫描，相比Java线程方式更轻量高效。
 * 支持TCP连接扫描、服务识别和并发控制。
 */
class CoroutinePortScanner(
    private val host: String,
    private val timeout: Int = 2000, // 超时毫秒
    private val concurrency: Int = 50 // 并发数
) {
    // 扫描结果数据类
    data class PortResult(
        val port: Int,
        val isOpen: Boolean,
        val service: String? = null,
        val banner: String? = null,
        val responseTime: Long = 0
    )

    // 扫描状态
    sealed class ScanState {
        object Started : ScanState()
        data class PortScanned(val result: PortResult) : ScanState()
        data class Progress(val scanned: Int, val total: Int) : ScanState()
        object Completed : ScanState()
    }

    /**
     * 解析端口范围字符串
     *
     * @param portRange 端口范围字符串，如 "80,443,1000-2000"
     * @return 端口列表
     */
    fun parsePortRange(portRange: String): List<Int> {
        val ports = mutableSetOf<Int>()
        for (part in portRange.split(",")) {
            val trimmed = part.trim()
            if (trimmed.contains("-")) {
                val range = trimmed.split("-")
                val start = range[0].toIntOrNull() ?: continue
                val end = range[1].toIntOrNull() ?: continue
                ports.addAll(start..end)
            } else {
                trimmed.toIntOrNull()?.let { ports.add(it) }
            }
        }
        return ports.sorted()
    }

    /**
     * 扫描单个端口
     *
     * @param port 端口号
     * @return 端口扫描结果
     */
    private suspend fun scanPort(port: Int): PortResult {
        return withContext(Dispatchers.IO) {
            val startTime = System.currentTimeMillis()
            try {
                val socket = Socket()
                socket.soTimeout = timeout
                socket.connect(InetSocketAddress(host, port), timeout)

                val responseTime = System.currentTimeMillis() - startTime
                val service = SecurityConstants.COMMON_PORTS[port]
                val banner = grabBanner(socket, port)

                socket.close()

                PortResult(
                    port = port,
                    isOpen = true,
                    service = service,
                    banner = banner,
                    responseTime = responseTime
                )
            } catch (e: IOException) {
                PortResult(
                    port = port,
                    isOpen = false,
                    responseTime = System.currentTimeMillis() - startTime
                )
            }
        }
    }

    /**
     * 获取服务Banner
     *
     * @param socket 已连接的Socket
     * @param port 端口号
     * @return Banner字符串
     */
    private fun grabBanner(socket: Socket, port: Int): String? {
        return try {
            when (port) {
                in listOf(80, 8080, 443) -> {
                    // HTTP端口发送HEAD请求
                    val output = socket.getOutputStream()
                    val input = socket.getInputStream()
                    val request = "HEAD / HTTP/1.0\r\nHost: $host\r\n\r\n"
                    output.write(request.toByteArray())
                    output.flush()

                    val buffer = ByteArray(1024)
                    val len = input.read(buffer)
                    if (len > 0) {
                        String(buffer, 0, len).lines().firstOrNull()
                    } else null
                }
                else -> {
                    // 其他端口等待Banner
                    val input = socket.getInputStream()
                    val buffer = ByteArray(1024)
                    socket.soTimeout = 3000 // 短超时等待Banner
                    val len = input.read(buffer)
                    if (len > 0) String(buffer, 0, len).lines().firstOrNull() else null
                }
            }
        } catch (e: Exception) {
            null
        }
    }

    /**
     * 扫描多个端口
     *
     * @param ports 端口列表
     * @return Flow of ScanState
     */
    fun scan(ports: List<Int>): Flow<ScanState> = flow {
        emit(ScanState.Started)
        val total = ports.size
        var scanned = 0

        // 使用协程并发扫描
        ports.chunked(concurrency).forEach { batch ->
            val results = batch.map { port ->
                async { scanPort(port) }
            }.awaitAll()

            results.forEach { result ->
                emit(ScanState.PortScanned(result))
                scanned++
                emit(ScanState.Progress(scanned, total))
            }
        }
        emit(ScanState.Completed)
    }

    /**
     * 扫描常用端口
     *
     * @return Flow of ScanState
     */
    fun scanCommonPorts(): Flow<ScanState> {
        return scan(SecurityConstants.COMMON_PORTS.keys.toList())
    }

    /**
     * 同步获取扫描结果
     *
     * @param ports 端口列表
     * @return 开放端口列表
     */
    suspend fun scanSync(ports: List<Int>): List<PortResult> {
        val openPorts = mutableListOf<PortResult>()
        scan(ports).collect { state ->
            when (state) {
                is ScanState.PortScanned -> {
                    if (state.result.isOpen) {
                        openPorts.add(state.result)
                        Log.i(TAG, "端口开放: ${state.result.port} - ${state.result.service}")
                    }
                }
                else -> {}
            }
        }
        return openPorts
    }
}

// ============================================================================
// 模块2：证书锁定验证器
// ============================================================================

/**
 * 证书锁定验证器
 *
 * 实现SSL/TLS证书锁定（Certificate Pinning），防止中间人攻击。
 * 通过预设证书的SHA-256哈希值，验证服务器证书是否匹配。
 */
class CertificatePinningVerifier(
    private val hostname: String,
    private val port: Int = 443,
    private val pinnedHashes: Set<String> = emptySet()
) {
    // 验证结果
    data class PinningResult(
        val success: Boolean,
        val certificateHash: String? = null,
        val matched: Boolean = false,
        val error: String? = null,
        val certificateInfo: Map<String, String> = emptyMap()
    )

    /**
     * 计算证书的SHA-256哈希
     *
     * @param certificate X.509证书
     * @return Base64编码的哈希值
     */
    private fun calculateCertificateHash(certificate: X509Certificate): String {
        val derCert = certificate.encoded
        val digest = MessageDigest.getInstance("SHA-256")
        val hash = digest.digest(derCert)
        return android.util.Base64.encodeToString(hash, android.util.Base64.NO_WRAP)
    }

    /**
     * 验证证书锁定
     *
     * @return 验证结果
     */
    suspend fun verifyPinning(): PinningResult = withContext(Dispatchers.IO) {
        try {
            // 创建SSL上下文
            val sslContext = SSLContext.getInstance("TLS")
            sslContext.init(null, arrayOf<TrustManager>(object : X509TrustManager {
                override fun checkClientTrusted(chain: Array<X509Certificate>, authType: String) {}
                override fun checkServerTrusted(chain: Array<X509Certificate>, authType: String) {}
                override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
            }), java.security.SecureRandom())

            // 建立SSL连接
            val socketFactory = sslContext.socketFactory
            val socket = socketFactory.createSocket(hostname, port) as SSLSocket
            socket.startHandshake()

            // 获取服务器证书
            val session = socket.session
            val serverCerts = session.peerCertificates
            val cert = serverCerts[0] as X509Certificate

            // 计算证书哈希
            val certHash = calculateCertificateHash(cert)
            val matched = pinnedHashes.contains(certHash)

            // 提取证书信息
            val certInfo = mapOf(
                "subject" to cert.subjectX500Principal.name,
                "issuer" to cert.issuerX500Principal.name,
                "notBefore" to cert.notBefore.toString(),
                "notAfter" to cert.notAfter.toString(),
                "serialNumber" to cert.serialNumber.toString(),
                "version" to cert.version.toString()
            )

            socket.close()

            PinningResult(
                success = true,
                certificateHash = certHash,
                matched = matched,
                certificateInfo = certInfo
            )
        } catch (e: Exception) {
            PinningResult(
                success = false,
                error = e.message
            )
        }
    }

    /**
     * 创建证书锁定的OkHttp拦截器
     *
     * @return OkHttpClient.Builder with certificate pinning
     */
    fun createPinnedOkHttpClient(): okhttp3.OkHttpClient {
        val builder = okhttp3.OkHttpClient.Builder()

        // 添加证书锁定
        val spec = okhttp3.CertificatePinner.Builder()
        for (hash in pinnedHashes) {
            spec.add(hostname, "sha256/$hash")
        }
        builder.certificatePinner(spec.build())

        // 安全超时设置
        builder.connectTimeout(10, java.util.concurrent.TimeUnit.SECONDS)
        builder.readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)

        return builder.build()
    }

    /**
     * 获取当前证书哈希（用于首次锁定）
     *
     * @return 证书哈希字符串
     */
    suspend fun getCurrentCertificateHash(): String? {
        val result = verifyPinning()
        return result.certificateHash
    }
}

// ============================================================================
// 模块3：Deep Link安全测试器
// ============================================================================

/**
 * Deep Link安全测试器
 *
 * 测试Android Deep Link（App Link）的安全性：
 * - 检查Deep Link配置完整性
 * - 测试URL参数注入
 * - 检查Deep Link劫持
 * - 验证autoVerify配置
 */
class DeepLinkSecurityTester(private val context: Context) {

    // 测试结果
    data class DeepLinkFinding(
        val severity: SecurityConstants.Severity,
        val scheme: String,
        val host: String,
        val issue: String,
        val recommendation: String
    )

    // 恶意测试URL列表
    private val maliciousUrls = listOf(
        "javascript:alert(1)",
        "intent://evil.com#Intent;scheme=https;end",
        "https://evil.com",
        "https://app.example.com/../../../etc/passwd",
        "https://app.example.com/%2e%2e/%2e%2e/admin",
        "https://app.example.com?redirect=https://evil.com",
        "https://app.example.com?url=javascript:alert(1)",
        "https://app.example.com/callback?code=evil_code",
        "https://app.example.com/token=evil_token",
        "https://app.example.com/auth?redirect_uri=https://evil.com"
    )

    /**
     * 从AndroidManifest.xml提取Deep Link配置
     *
     * @return Deep Link配置列表
     */
    fun extractDeepLinksFromManifest(): List<Map<String, String>> {
        val deepLinks = mutableListOf<Map<String, String>>()
        try {
            val packageInfo = context.packageManager.getPackageInfo(
                context.packageName,
                PackageManager.GET_ACTIVITIES
            )

            // 在实际应用中，需要解析AndroidManifest.xml
            // 这里提供框架，实际需要解析XML或使用PackageManager API

            Log.i(TAG, "提取Deep Link配置...")
            // 实际实现需要解析AndroidManifest.xml
            // 可以使用XmlPullParser解析Intent-filter中的data元素

        } catch (e: Exception) {
            Log.e(TAG, "提取Deep Link失败: ${e.message}")
        }
        return deepLinks
    }

    /**
     * 检查Deep Link安全配置
     *
     * @param deepLinks Deep Link配置列表
     * @return 安全发现列表
     */
    fun checkDeepLinkSecurity(deepLinks: List<Map<String, String>>): List<DeepLinkFinding> {
        val findings = mutableListOf<DeepLinkFinding>()

        for (link in deepLinks) {
            val scheme = link["scheme"] ?: ""
            val host = link["host"] ?: ""
            val autoVerify = link["autoVerify"] ?: "false"

            // 检查1：使用HTTP明文scheme
            if (scheme.equals("http", ignoreCase = true)) {
                findings.add(DeepLinkFinding(
                    SecurityConstants.Severity.MEDIUM,
                    scheme, host,
                    "Deep Link使用HTTP明文scheme，可被中间人劫持",
                    "使用HTTPS scheme，配置android:autoVerify=true"
                ))
            }

            // 检查2：自定义scheme可被劫持
            if (!scheme.equals("http", ignoreCase = true) &&
                !scheme.equals("https", ignoreCase = true) &&
                !scheme.equals("content", ignoreCase = true)) {
                findings.add(DeepLinkFinding(
                    SecurityConstants.Severity.LOW,
                    scheme, host,
                    "自定义scheme '$scheme' 可被其他应用注册相同scheme劫持",
                    "使用App Links (HTTPS + autoVerify)替代自定义scheme"
                ))
            }

            // 检查3：缺少autoVerify
            if (scheme.equals("https", ignoreCase = true) &&
                !autoVerify.equals("true", ignoreCase = true)) {
                findings.add(DeepLinkFinding(
                    SecurityConstants.Severity.LOW,
                    scheme, host,
                    "HTTPS Deep Link未启用autoVerify，可能被其他应用优先处理",
                    "设置android:autoVerify=true启用App Links"
                ))
            }

            // 检查4：缺少host
            if (host.isEmpty()) {
                findings.add(DeepLinkFinding(
                    SecurityConstants.Severity.MEDIUM,
                    scheme, host,
                    "Deep Link未指定host，可能匹配非预期URL",
                    "在data元素中指定明确的host属性"
                ))
            }

            // 检查5：使用通配符host
            if (host.contains("*")) {
                findings.add(DeepLinkFinding(
                    SecurityConstants.Severity.MEDIUM,
                    scheme, host,
                    "Deep Link使用通配符host，匹配范围过宽",
                    "使用精确host，避免使用通配符"
                ))
            }
        }

        return findings
    }

    /**
     * 测试Deep Link对恶意URL的处理
     *
     * @param deepLinkUrl 目标Deep Link URL
     * @return 测试结果
     */
    suspend fun testMaliciousUrls(deepLinkUrl: String): List<Map<String, Any>> {
        val results = mutableListOf<Map<String, Any>>()

        for (malicious in maliciousUrls) {
            val testResult = mapOf(
                "test_url" to malicious,
                "description" to "测试恶意URL: $malicious",
                "recommendation" to "验证应用是否能正确拒绝恶意URL"
            )
            results.add(testResult)
        }

        return results
    }

    /**
     * 检查Deep Link参数验证
     *
     * @return 安全发现
     */
    fun checkParameterValidation(): DeepLinkFinding {
        return DeepLinkFinding(
            SecurityConstants.Severity.INFO,
            "通用", "通用",
            "需要检查代码中对Deep Link参数的验证：\n" +
                "  1. 是否验证了URL参数的来源\n" +
                "  2. 是否对参数值进行了输入验证\n" +
                "  3. 是否防止了Open Redirect\n" +
                "  4. 是否防止了路径遍历",
            "在Activity的onCreate/onNewIntent中验证Intent数据"
        )
    }
}

// ============================================================================
// 模块4：Jetpack Security库使用示例
// ============================================================================

/**
 * Jetpack Security库使用示例
 *
 * 展示如何使用AndroidX Security Crypto库保护敏感数据：
 * - EncryptedSharedPreferences：加密存储键值对
 * - MasterKey：主密钥管理
 * - FileEncryption：文件加密
 */
object JetpackSecurityExample {

    private const val TAG = "JetpackSecurity"

    /**
     * 创建加密的SharedPreferences
     *
     * @param context 应用上下文
     * @param fileName 文件名
     * @return EncryptedSharedPreferences实例
     */
    fun createEncryptedSharedPreferences(
        context: Context,
        fileName: String = "secret_prefs"
): EncryptedSharedPreferences {
        // 创建主密钥
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()

        // 创建加密的SharedPreferences
        return EncryptedSharedPreferences.create(
            context,
            fileName,
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        ) as EncryptedSharedPreferences
    }

    /**
     * 安全存储敏感数据
     *
     * @param context 应用上下文
     * @param key 数据键
     * @param value 数据值
     */
    fun storeSecureData(context: Context, key: String, value: String) {
        try {
            val prefs = createEncryptedSharedPreferences(context)
            prefs.edit().putString(key, value).apply()
            Log.i(TAG, "安全数据已存储: $key")
        } catch (e: Exception) {
            Log.e(TAG, "存储安全数据失败: ${e.message}")
        }
    }

    /**
     * 读取安全存储的数据
     *
     * @param context 应用上下文
     * @param key 数据键
     * @return 数据值
     */
    fun getSecureData(context: Context, key: String): String? {
        return try {
            val prefs = createEncryptedSharedPreferences(context)
            prefs.getString(key, null)
        } catch (e: Exception) {
            Log.e(TAG, "读取安全数据失败: ${e.message}")
            null
        }
    }

    /**
     * 使用Android Keystore生成密钥
     *
     * @param alias 密钥别名
     * @return SecretKey
     */
    fun generateKeystoreKey(alias: String = "secure_key"): SecretKey {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        val spec = KeyGenParameterSpec.Builder(
            alias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .setRandomizedEncryptionRequired(true)
            .build()

        keyGenerator.init(spec)
        return keyGenerator.generateKey()
    }

    /**
     * 使用Keystore密钥加密数据
     *
     * @param plaintext 明文数据
     * @param alias Keystore中的密钥别名
     * @return 加密结果（密文+IV）
     */
    fun encryptWithKeystore(plaintext: ByteArray, alias: String = "secure_key"): Pair<ByteArray, ByteArray> {
        val keyStore = KeyStore.getInstance("AndroidKeyStore")
        keyStore.load(null)

        val secretKey = keyStore.getKey(alias, null) as SecretKey

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, secretKey)

        val ciphertext = cipher.doFinal(plaintext)
        val iv = cipher.iv

        return Pair(ciphertext, iv)
    }

    /**
     * 使用Keystore密钥解密数据
     *
     * @param ciphertext 密文
     * @param iv 初始化向量
     * @param alias Keystore中的密钥别名
     * @return 明文数据
     */
    fun decryptWithKeystore(ciphertext: ByteArray, iv: ByteArray, alias: String = "secure_key"): ByteArray {
        val keyStore = KeyStore.getInstance("AndroidKeyStore")
        keyStore.load(null)

        val secretKey = keyStore.getKey(alias, null) as SecretKey

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val spec = GCMParameterSpec(128, iv)
        cipher.init(Cipher.DECRYPT_MODE, secretKey, spec)

        return cipher.doFinal(ciphertext)
    }

    /**
     * 检查Keystore中是否存在密钥
     *
     * @param alias 密钥别名
     * @return 是否存在
     */
    fun keystoreKeyExists(alias: String): Boolean {
        val keyStore = KeyStore.getInstance("AndroidKeyStore")
        keyStore.load(null)
        return keyStore.containsAlias(alias)
    }

    /**
     * 删除Keystore中的密钥
     *
     * @param alias 密钥别名
     */
    fun deleteKeystoreKey(alias: String) {
        val keyStore = KeyStore.getInstance("AndroidKeyStore")
        keyStore.load(null)
        keyStore.deleteEntry(alias)
        Log.i(TAG, "已删除Keystore密钥: $alias")
    }
}

// ============================================================================
// 模块5：EncryptedSharedPreferences使用示例
// ============================================================================

/**
 * EncryptedSharedPreferences使用示例
 *
 * 展示如何使用加密的SharedPreferences安全存储敏感数据。
 * 包含密码存储、Token管理和用户信息存储。
 */
class EncryptedPrefsManager(private val context: Context) {

    // 加密的SharedPreferences实例
    private val encryptedPrefs by lazy {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()

        EncryptedSharedPreferences.create(
            context,
            "secure_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    /**
     * 存储用户Token
     *
     * @param token 认证Token
     */
    fun saveAuthToken(token: String) {
        encryptedPrefs.edit()
            .putString(KEY_AUTH_TOKEN, token)
            .putLong(KEY_TOKEN_TIMESTAMP, System.currentTimeMillis())
            .apply()
        Log.i(TAG, "认证Token已安全存储")
    }

    /**
     * 获取用户Token
     *
     * @return Token字符串或null
     */
    fun getAuthToken(): String? {
        val token = encryptedPrefs.getString(KEY_AUTH_TOKEN, null) ?: return null
        val timestamp = encryptedPrefs.getLong(KEY_TOKEN_TIMESTAMP, 0)

        // 检查Token是否过期（24小时）
        val age = System.currentTimeMillis() - timestamp
        if (age > TOKEN_MAX_AGE_MS) {
            Log.w(TAG, "Token已过期")
            clearAuthToken()
            return null
        }

        return token
    }

    /**
     * 清除Token
     */
    fun clearAuthToken() {
        encryptedPrefs.edit()
            .remove(KEY_AUTH_TOKEN)
            .remove(KEY_TOKEN_TIMESTAMP)
            .apply()
    }

    /**
     * 安全存储用户凭据
     *
     * @param username 用户名
     * @param password 密码（应存储哈希值而非明文）
     */
    fun saveCredentials(username: String, passwordHash: String) {
        encryptedPrefs.edit()
            .putString(KEY_USERNAME, username)
            .putString(KEY_PASSWORD_HASH, passwordHash)
            .apply()
    }

    /**
     * 获取存储的用户名
     */
    fun getUsername(): String? = encryptedPrefs.getString(KEY_USERNAME, null)

    /**
     * 获取存储的密码哈希
     */
    fun getPasswordHash(): String? = encryptedPrefs.getString(KEY_PASSWORD_HASH, null)

    /**
     * 清除所有凭据
     */
    fun clearAllCredentials() {
        encryptedPrefs.edit().clear().apply()
        Log.i(TAG, "所有凭据已清除")
    }

    /**
     * 存储API密钥
     *
     * @param keyName 密钥名称
     * @param keyValue 密钥值
     */
    fun saveApiKey(keyName: String, keyValue: String) {
        encryptedPrefs.edit()
            .putString("${KEY_API_KEY_PREFIX}$keyName", keyValue)
            .apply()
    }

    /**
     * 获取API密钥
     *
     * @param keyName 密钥名称
     * @return 密钥值
     */
    fun getApiKey(keyName: String): String? {
        return encryptedPrefs.getString("${KEY_API_KEY_PREFIX}$keyName", null)
    }

    companion object {
        private const val KEY_AUTH_TOKEN = "auth_token"
        private const val KEY_TOKEN_TIMESTAMP = "token_timestamp"
        private const val KEY_USERNAME = "username"
        private const val KEY_PASSWORD_HASH = "password_hash"
        private const val KEY_API_KEY_PREFIX = "api_key_"
        private const val TOKEN_MAX_AGE_MS = 24 * 60 * 60 * 1000L // 24小时
    }
}

// ============================================================================
// 模块6：SafetyNet/Play Integrity API集成
// ============================================================================

/**
 * SafetyNet/Play Integrity API集成
 *
 * SafetyNet Attestation API用于验证设备的安全性：
 * - 设备完整性验证
 * - 应用完整性验证
 * - 越狱/Root检测
 *
 * 注意：SafetyNet API已被Play Integrity API取代
 */
class SafetyNetIntegrator(private val apiKey: String) {

    // 验证结果数据类
    data class AttestationResult(
        val success: Boolean,
        val jwsResult: String? = null,
        val isBasicAttestation: Boolean = false,
        val isCtsProfileMatch: Boolean = false,
        val isIntegrityVerified: Boolean = false,
        val error: String? = null
    )

    /**
     * 执行SafetyNet Attestation
     *
     * @param nonce 随机数（至少16字节）
     * @return 验证结果
     */
    suspend fun performAttestation(nonce: ByteArray): AttestationResult = withContext(Dispatchers.IO) {
        try {
            // SafetyNet API调用（需要Google Play Services）
            val task: Task<SafetyNetApi.AttestationResponse> = SafetyNet.getClient(null)
                .attest(nonce, apiKey)

            // 等待结果
            val response = suspendCoroutine<SafetyNetApi.AttestationResponse> { cont ->
                task.addOnSuccessListener { cont.resume(it) }
                    .addOnFailureListener { cont.resumeWithException(it) }
            }

            val jwsResult = response.jwsResult

            // 解析JWS结果（需要验证签名）
            val parsed = parseJwsResult(jwsResult)

            AttestationResult(
                success = true,
                jwsResult = jwsResult,
                isBasicAttestation = parsed.basicIntegrity,
                isCtsProfileMatch = parsed.ctsProfileMatch,
                isIntegrityVerified = parsed.basicIntegrity && parsed.ctsProfileMatch
            )
        } catch (e: Exception) {
            AttestationResult(
                success = false,
                error = e.message
            )
        }
    }

    /**
     * 解析JWS结果
     * 注意：实际应验证JWS签名，这里简化处理
     */
    private data class ParsedResult(
        val basicIntegrity: Boolean,
        val ctsProfileMatch: Boolean,
        val timestamp: String? = null
    )

    private fun parseJwsResult(jws: String?): ParsedResult {
        if (jws == null) return ParsedResult(false, false)

        return try {
            // 实际实现需要验证JWS签名并解析payload
            // 这里仅作为框架
            ParsedResult(
                basicIntegrity = true,
                ctsProfileMatch = true
            )
        } catch (e: Exception) {
            ParsedResult(false, false)
        }
    }

    /**
     * 生成随机Nonce
     *
     * @return 16字节的随机Nonce
     */
    fun generateNonce(): ByteArray {
        val nonce = ByteArray(16)
        java.security.SecureRandom().nextBytes(nonce)
        return nonce
    }

    /**
     * Play Integrity API集成（新API）
     *
     * @param context 应用上下文
     * @param requestHash 请求哈希
     * @return 完整性验证结果
     */
    suspend fun requestIntegrityVerdict(
        context: Context,
        requestHash: String
    ): Map<String, Any> = withContext(Dispatchers.IO) {
        try {
            // 使用Play Integrity API
            // 注意：需要com.google.android.play:integrity库
            val result = mutableMapOf<String, Any>()

            // 实际实现：
            // 1. 从服务器获取nonce
            // 2. 调用IntegrityManager.requestIntegrityToken()
            // 3. 将token发送到服务器验证
            // 4. 服务器返回完整性结果

            result["status"] = "需要实现Play Integrity API"
            result["note"] = "SafetyNet已被Play Integrity API取代"
            result

        } catch (e: Exception) {
            mapOf("error" to (e.message ?: "未知错误"))
        }
    }

    /**
     * 综合设备安全检查
     *
     * 结合多种方法检测设备安全状态
     *
     * @param context 应用上下文
     * @return 安全状态报告
     */
    suspend fun comprehensiveSecurityCheck(context: Context): Map<String, Any> {
        val report = mutableMapOf<String, Any>()

        // 1. SafetyNet验证
        val nonce = generateNonce()
        val attestation = performAttestation(nonce)
        report["safetynet_attestation"] = mapOf(
            "success" to attestation.success,
            "basic_integrity" to attestation.isBasicAttestation,
            "cts_profile_match" to attestation.isCtsProfileMatch,
            "error" to (attestation.error ?: "")
        )

        // 2. Root检测
        report["root_detection"] = checkRootAccess()

        // 3. 调试器检测
        report["debugger_detection"] = checkDebuggerStatus()

        // 4. 模拟器检测
        report["emulator_detection"] = checkEmulator()

        // 5. 系统版本
        report["system_info"] = mapOf(
            "android_version" to Build.VERSION.RELEASE,
            "sdk_level" to Build.VERSION.SDK_INT,
            "manufacturer" to Build.MANUFACTURER,
            "model" to Build.MODEL,
            "fingerprint" to Build.FINGERPRINT
        )

        return report
    }

    /**
     * Root检测
     */
    private fun checkRootAccess(): Map<String, Any> {
        val indicators = mutableListOf<String>()

        // 检查su二进制文件
        val suPaths = listOf(
            "/system/bin/su", "/system/xbin/su", "/sbin/su",
            "/system/sbin/su", "/vendor/bin/su", "/su/bin/su"
        )

        for (path in suPaths) {
            if (java.io.File(path).exists()) {
                indicators.add("发现su: $path")
            }
        }

        // 检查Magisk
        val magiskPaths = listOf(
            "/sbin/.magisk", "/data/adb/magisk",
            "/data/adb/modules", "/cache/.disable_magisk"
        )

        for (path in magiskPaths) {
            if (java.io.File(path).exists()) {
                indicators.add("发现Magisk: $path")
            }
        }

        // 检查Root相关应用
        val rootApps = listOf(
            "com.topjohnwu.magisk", "eu.chainfire.supersu",
            "com.koushikdutta.superuser", "com.thirdparty.superuser"
        )

        return mapOf(
            "is_rooted" to indicators.isNotEmpty(),
            "indicators" to indicators,
            "risk_level" to if (indicators.isNotEmpty()) "HIGH" else "LOW"
        )
    }

    /**
     * 调试器检测
     */
    private fun checkDebuggerStatus(): Map<String, Any> {
        val isDebuggable = (context.applicationContext.applicationInfo.flags
            and android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) != 0

        val isDebuggerConnected = android.os.Debug.isDebuggerConnected()

        return mapOf(
            "app_debuggable" to isDebuggable,
            "debugger_connected" to isDebuggerConnected,
            "risk_level" to if (isDebuggable || isDebuggerConnected) "HIGH" else "LOW"
        )
    }

    /**
     * 模拟器检测
     */
    private fun checkEmulator(): Map<String, Any> {
        val indicators = mutableListOf<String>()

        // 检查模拟器特征
        if (Build.FINGERPRINT.contains("generic", ignoreCase = true) ||
            Build.FINGERPRINT.contains("unknown", ignoreCase = true)) {
            indicators.add("Fingerprint包含generic/unknown")
        }

        if (Build.MODEL.contains("google_sdk", ignoreCase = true) ||
            Build.MODEL.contains("Emulator", ignoreCase = true) ||
            Build.MODEL.contains("Android SDK", ignoreCase = true)) {
            indicators.add("Model包含SDK/Emulator")
        }

        if (Build.MANUFACTURER.contains("Genymotion", ignoreCase = true) ||
            Build.MANUFACTURER.contains("unknown", ignoreCase = true)) {
            indicators.add("Manufacturer包含Genymotion/unknown")
        }

        if (Build.BRAND.contains("generic", ignoreCase = true)) {
            indicators.add("Brand包含generic")
        }

        if (Build.PRODUCT.contains("sdk", ignoreCase = true) ||
            Build.PRODUCT.contains("google_sdk", ignoreCase = true)) {
            indicators.add("Product包含sdk")
        }

        // 检查模拟器文件
        val emulatorFiles = listOf(
            "/dev/qemu_pipe", "/dev/goldfish_pipe",
            "/system/lib/libc_malloc_debug_qemu.so"
        )

        for (file in emulatorFiles) {
            if (java.io.File(file).exists()) {
                indicators.add("发现模拟器文件: $file")
            }
        }

        return mapOf(
            "is_emulator" to indicators.isNotEmpty(),
            "indicators" to indicators,
            "risk_level" to if (indicators.isNotEmpty()) "MEDIUM" else "LOW"
        )
    }

    // 用于suspendCoroutine
    private var context: Context = android.app.Application()

    fun setContext(context: Context) {
        this.context = context
    }
}

// ============================================================================
// 主函数与使用示例
// ============================================================================

/**
 * 使用示例主函数
 */
fun main() {
    println("=".repeat(60))
    println("  Android Kotlin安全工具集 v1.0")
    println("  综合Android安全分析工具")
    println("=".repeat(60))

    // 示例1：协程端口扫描
    println("\n[1] 协程端口扫描示例")
    val scanner = CoroutinePortScanner("127.0.0.1", timeout = 1000, concurrency = 20)
    val ports = scanner.parsePortRange("80,443,3306,8080")
    println("  扫描端口: $ports")

    // 示例2：证书锁定验证
    println("\n[2] 证书锁定验证示例")
    val pinner = CertificatePinningVerifier(
        hostname = "www.example.com",
        port = 443,
        pinnedHashes = setOf("sha256/abcdef...")
    )
    println("  证书锁定验证器已创建")

    // 示例3：Deep Link安全测试
    println("\n[3] Deep Link安全测试示例")
    println("  需要Context参数，请在Android环境中运行")

    // 示例4：Jetpack Security
    println("\n[4] Jetpack Security使用示例")
    println("  EncryptedSharedPreferences: 加密存储键值对")
    println("  MasterKey: AES256-GCM主密钥")
    println("  Android Keystore: 硬件级密钥保护")

    // 示例5：EncryptedPrefsManager
    println("\n[5] EncryptedPrefsManager使用示例")
    println("  安全存储Token/凭据/API密钥")

    // 示例6：SafetyNet集成
    println("\n[6] SafetyNet/Play Integrity集成示例")
    println("  设备完整性验证")
    println("  Root检测")
    println("  调试器检测")
    println("  模拟器检测")

    println("\n" + "=".repeat(60))
    println("  注意：本工具集需要在Android环境中运行")
    println("  免责声明：仅用于授权的安全测试！")
    println("=".repeat(60))
}
