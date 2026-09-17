/*
 * ============================================================
 * 文件名：string_encrypt.cpp
 * 功能描述：常见加密算法实现（XOR、Base64、MD5、SHA1）
 * 作者：网络安全学习笔记
 * 日期：2026-09-10
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译方式（Windows + MinGW）：
 *    g++ string_encrypt.cpp -o string_encrypt.exe
 * 2. 编译方式（Visual Studio）：
 *    cl string_encrypt.cpp
 * 3. 命令行参数：
 *    参数1：操作类型（xor/base64_encode/base64_decode/md5/sha1）
 *    参数2：输入文本
 *    参数3：XOR 密钥（仅 XOR 操作时需要）
 *
 * 【示例】
 *   string_encrypt.exe xor "Hello World" "key123"
 *   string_encrypt.exe base64_encode "Hello World"
 *   string_encrypt.exe base64_decode "SGVsbG8gV29ybGQ="
 *   string_encrypt.exe md5 "password"
 *   string_encrypt.exe sha1 "password"
 *
 * 【算法说明】
 *   - XOR 加密：对称加密，使用密钥对每个字节进行异或运算
 *   - Base64：编码方式，将二进制数据转换为可打印字符
 *   - MD5：消息摘要算法，产生 128 位（16 字节）哈希值
 *   - SHA1：安全哈希算法，产生 160 位（20 字节）哈希值
 *
 * 【免责声明】
 *   本代码仅供密码学学习和安全研究使用。
 *   MD5 和 SHA1 已被证明存在碰撞漏洞，不应用于安全场景。
 *   XOR 加密安全性较低，仅用于学习原理。
 *   使用本工具请遵守当地法律法规。
 * ============================================================
 */

// 引入必要的头文件
#include <iostream>    // 标准输入输出
#include <string>      // 字符串处理
#include <cstring>     // C 风格字符串
#include <cstdint>     // 标准整数类型
#include <cstdio>      // C 标准输入输出

using namespace std;

// ============================================================
// XOR 加解密
// XOR 是一种对称加密，加密和解密使用相同的算法和密钥
// 原理：对每个字节与密钥字节进行异或运算
// ============================================================

// XOR 加密/解密函数（加密和解密是同一个操作）
// 参数：
//   input - 输入字符串
//   key - 密钥字符串
// 返回：加密/解密后的字符串
string xorEncrypt(const string& input, const string& key) {
    string output = input;
    int keyLen = key.length();

    if (keyLen == 0) {
        return input;  // 密钥为空，直接返回原文
    }

    // 对每个字符进行异或运算
    // 密钥循环使用（如果明文比密钥长）
    for (size_t i = 0; i < input.length(); i++) {
        output[i] = input[i] ^ key[i % keyLen];
    }

    return output;
}

// 将字符串转换为十六进制表示
// 用于显示 XOR 加密后的二进制数据
string stringToHex(const string& input) {
    string hexStr;
    char buf[3];
    for (size_t i = 0; i < input.length(); i++) {
        sprintf(buf, "%02x", (unsigned char)input[i]);
        hexStr += buf;
    }
    return hexStr;
}

// 将十六进制字符串转换回普通字符串
string hexToString(const string& hexStr) {
    string result;
    for (size_t i = 0; i < hexStr.length(); i += 2) {
        string byteStr = hexStr.substr(i, 2);
        unsigned char byte = (unsigned char)strtol(byteStr.c_str(), NULL, 16);
        result += (char)byte;
    }
    return result;
}

// ============================================================
// Base64 编解码
// Base64 是一种编码方式，将 3 字节数据编码为 4 个可打印字符
// 字符集：A-Z, a-z, 0-9, +, /（共 64 个字符）
// ============================================================

// Base64 字符表
static const string base64Chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789+/";

// 判断字符是否为 Base64 字符
static inline bool isBase64(unsigned char c) {
    return (isalnum(c) || (c == '+') || (c == '/'));
}

// Base64 编码
// 参数：input - 输入字符串
// 返回：Base64 编码后的字符串
string base64Encode(const string& input) {
    string output;
    int i = 0;
    int j = 0;
    unsigned char charArray3[3];  // 3 个 8 位字节
    unsigned char charArray4[4];  // 4 个 6 位值

    const unsigned char* bytes = (const unsigned char*)input.c_str();
    int len = input.length();

    while (len--) {
        // 每次取 3 个字节
        charArray3[i++] = *(bytes++);
        if (i == 3) {
            // 将 3 个 8 位字节转换为 4 个 6 位值
            charArray4[0] = (charArray3[0] & 0xfc) >> 2;
            charArray4[1] = ((charArray3[0] & 0x03) << 4) + ((charArray3[1] & 0xf0) >> 4);
            charArray4[2] = ((charArray3[1] & 0x0f) << 2) + ((charArray3[2] & 0xc0) >> 6);
            charArray4[3] = charArray3[2] & 0x3f;

            // 查找对应的 Base64 字符并添加到输出
            for (i = 0; i < 4; i++) {
                output += base64Chars[charArray4[i]];
            }
            i = 0;
        }
    }

    // 处理剩余字节（不足 3 个的情况）
    if (i) {
        // 将剩余的字节填充到 charArray3 中
        for (j = i; j < 3; j++) {
            charArray3[j] = '\0';
        }

        charArray4[0] = (charArray3[0] & 0xfc) >> 2;
        charArray4[1] = ((charArray3[0] & 0x03) << 4) + ((charArray3[1] & 0xf0) >> 4);
        charArray4[2] = ((charArray3[1] & 0x0f) << 2) + ((charArray3[2] & 0xc0) >> 6);
        charArray4[3] = charArray3[2] & 0x3f;

        // 添加有效字符
        for (j = 0; j < i + 1; j++) {
            output += base64Chars[charArray4[j]];
        }

        // 用 = 填充
        while (i++ < 3) {
            output += '=';
        }
    }

    return output;
}

// Base64 解码
// 参数：input - Base64 编码的字符串
// 返回：解码后的原始字符串
string base64Decode(const string& input) {
    int inLen = input.length();
    int i = 0;
    int j = 0;
    int inIdx = 0;
    unsigned char charArray4[4];
    unsigned char charArray3[3];
    string output;

    // 逐个字符处理
    while (inLen-- && (input[inIdx] != '=') && isBase64(input[inIdx])) {
        charArray4[i++] = input[inIdx];
        inIdx++;
        if (i == 4) {
            // 将 4 个 Base64 字符转换回 3 个字节
            // 先将字符映射回 6 位值
            for (i = 0; i < 4; i++) {
                charArray4[i] = base64Chars.find(charArray4[i]);
            }

            charArray3[0] = (charArray4[0] << 2) + ((charArray4[1] & 0x30) >> 4);
            charArray3[1] = ((charArray4[1] & 0xf) << 4) + ((charArray4[2] & 0x3c) >> 2);
            charArray3[2] = ((charArray4[2] & 0x3) << 6) + charArray4[3];

            for (i = 0; i < 3; i++) {
                output += charArray3[i];
            }
            i = 0;
        }
    }

    // 处理剩余的字符（如果有填充 = 的情况）
    if (i) {
        for (j = i; j < 4; j++) {
            charArray4[j] = 0;
        }

        for (j = 0; j < 4; j++) {
            charArray4[j] = base64Chars.find(charArray4[j]);
        }

        charArray3[0] = (charArray4[0] << 2) + ((charArray4[1] & 0x30) >> 4);
        charArray3[1] = ((charArray4[1] & 0xf) << 4) + ((charArray4[2] & 0x3c) >> 2);
        charArray3[2] = ((charArray4[2] & 0x3) << 6) + charArray4[3];

        for (j = 0; j < i - 1; j++) {
            output += charArray3[j];
        }
    }

    return output;
}

// ============================================================
// MD5 消息摘要算法
// MD5 输出 128 位（16 字节）的哈希值
// 注意：MD5 已被证明不安全，仅用于学习和兼容旧系统
// ============================================================

// MD5 上下文结构体
struct MD5Context {
    uint32_t state[4];      // 状态寄存器（A, B, C, D）
    uint32_t count[2];      // 位数计数（低 32 位，高 32 位）
    unsigned char buffer[64];  // 输入缓冲区
};

// MD5 基本函数宏
#define F(x, y, z) (((x) & (y)) | ((~x) & (z)))
#define G(x, y, z) (((x) & (z)) | ((y) & (~z)))
#define H(x, y, z) ((x) ^ (y) ^ (z))
#define I(x, y, z) ((y) ^ ((x) | (~z)))

// 循环左移
#define ROTATE_LEFT(x, n) (((x) << (n)) | ((x) >> (32 - (n))))

// 各轮操作
#define FF(a, b, c, d, x, s, ac) { \
    (a) += F((b), (c), (d)) + (x) + (uint32_t)(ac); \
    (a) = ROTATE_LEFT((a), (s)); \
    (a) += (b); \
}
#define GG(a, b, c, d, x, s, ac) { \
    (a) += G((b), (c), (d)) + (x) + (uint32_t)(ac); \
    (a) = ROTATE_LEFT((a), (s)); \
    (a) += (b); \
}
#define HH(a, b, c, d, x, s, ac) { \
    (a) += H((b), (c), (d)) + (x) + (uint32_t)(ac); \
    (a) = ROTATE_LEFT((a), (s)); \
    (a) += (b); \
}
#define II(a, b, c, d, x, s, ac) { \
    (a) += I((b), (c), (d)) + (x) + (uint32_t)(ac); \
    (a) = ROTATE_LEFT((a), (s)); \
    (a) += (b); \
}

// MD5 变换函数（处理一个 512 位分组）
static void md5Transform(uint32_t state[4], const unsigned char block[64]) {
    uint32_t a = state[0], b = state[1], c = state[2], d = state[3];
    uint32_t x[16];

    // 将字节数组转换为 32 位整数数组（小端序）
    for (int i = 0, j = 0; i < 16; i++, j += 4) {
        x[i] = ((uint32_t)block[j]) |
               (((uint32_t)block[j + 1]) << 8) |
               (((uint32_t)block[j + 2]) << 16) |
               (((uint32_t)block[j + 3]) << 24);
    }

    // 第 1 轮
    FF(a, b, c, d, x[0], 7, 0xd76aa478);
    FF(d, a, b, c, x[1], 12, 0xe8c7b756);
    FF(c, d, a, b, x[2], 17, 0x242070db);
    FF(b, c, d, a, x[3], 22, 0xc1bdceee);
    FF(a, b, c, d, x[4], 7, 0xf57c0faf);
    FF(d, a, b, c, x[5], 12, 0x4787c62a);
    FF(c, d, a, b, x[6], 17, 0xa8304613);
    FF(b, c, d, a, x[7], 22, 0xfd469501);
    FF(a, b, c, d, x[8], 7, 0x698098d8);
    FF(d, a, b, c, x[9], 12, 0x8b44f7af);
    FF(c, d, a, b, x[10], 17, 0xffff5bb1);
    FF(b, c, d, a, x[11], 22, 0x895cd7be);
    FF(a, b, c, d, x[12], 7, 0x6b901122);
    FF(d, a, b, c, x[13], 12, 0xfd987193);
    FF(c, d, a, b, x[14], 17, 0xa679438e);
    FF(b, c, d, a, x[15], 22, 0x49b40821);

    // 第 2 轮
    GG(a, b, c, d, x[1], 5, 0xf61e2562);
    GG(d, a, b, c, x[6], 9, 0xc040b340);
    GG(c, d, a, b, x[11], 14, 0x265e5a51);
    GG(b, c, d, a, x[0], 20, 0xe9b6c7aa);
    GG(a, b, c, d, x[5], 5, 0xd62f105d);
    GG(d, a, b, c, x[10], 9, 0x02441453);
    GG(c, d, a, b, x[15], 14, 0xd8a1e681);
    GG(b, c, d, a, x[4], 20, 0xe7d3fbc8);
    GG(a, b, c, d, x[9], 5, 0x21e1cde6);
    GG(d, a, b, c, x[14], 9, 0xc33707d6);
    GG(c, d, a, b, x[3], 14, 0xf4d50d87);
    GG(b, c, d, a, x[8], 20, 0x455a14ed);
    GG(a, b, c, d, x[13], 5, 0xa9e3e905);
    GG(d, a, b, c, x[2], 9, 0xfcefa3f8);
    GG(c, d, a, b, x[7], 14, 0x676f02d9);
    GG(b, c, d, a, x[12], 20, 0x8d2a4c8a);

    // 第 3 轮
    HH(a, b, c, d, x[5], 4, 0xfffa3942);
    HH(d, a, b, c, x[8], 11, 0x8771f681);
    HH(c, d, a, b, x[11], 16, 0x6d9d6122);
    HH(b, c, d, a, x[14], 23, 0xfde5380c);
    HH(a, b, c, d, x[1], 4, 0xa4beea44);
    HH(d, a, b, c, x[4], 11, 0x4bdecfa9);
    HH(c, d, a, b, x[7], 16, 0xf6bb4b60);
    HH(b, c, d, a, x[10], 23, 0xbebfbc70);
    HH(a, b, c, d, x[13], 4, 0x289b7ec6);
    HH(d, a, b, c, x[0], 11, 0xeaa127fa);
    HH(c, d, a, b, x[3], 16, 0xd4ef3085);
    HH(b, c, d, a, x[6], 23, 0x04881d05);
    HH(a, b, c, d, x[9], 4, 0xd9d4d039);
    HH(d, a, b, c, x[12], 11, 0xe6db99e5);
    HH(c, d, a, b, x[15], 16, 0x1fa27cf8);
    HH(b, c, d, a, x[2], 23, 0xc4ac5665);

    // 第 4 轮
    II(a, b, c, d, x[0], 6, 0xf4292244);
    II(d, a, b, c, x[7], 10, 0x432aff97);
    II(c, d, a, b, x[14], 15, 0xab9423a7);
    II(b, c, d, a, x[5], 21, 0xfc93a039);
    II(a, b, c, d, x[12], 6, 0x655b59c3);
    II(d, a, b, c, x[3], 10, 0x8f0ccc92);
    II(c, d, a, b, x[10], 15, 0xffeff47d);
    II(b, c, d, a, x[1], 21, 0x85845dd1);
    II(a, b, c, d, x[8], 6, 0x6fa87e4f);
    II(d, a, b, c, x[15], 10, 0xfe2ce6e0);
    II(c, d, a, b, x[6], 15, 0xa3014314);
    II(b, c, d, a, x[13], 21, 0x4e0811a1);
    II(a, b, c, d, x[4], 6, 0xf7537e82);
    II(d, a, b, c, x[11], 10, 0xbd3af235);
    II(c, d, a, b, x[2], 15, 0x2ad7d2bb);
    II(b, c, d, a, x[9], 21, 0xeb86d391);

    // 将结果加到初始状态上
    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;
}

// 初始化 MD5 上下文
static void md5Init(MD5Context* ctx) {
    ctx->count[0] = 0;
    ctx->count[1] = 0;
    // MD5 初始向量（IV）
    ctx->state[0] = 0x67452301;
    ctx->state[1] = 0xefcdab89;
    ctx->state[2] = 0x98badcfe;
    ctx->state[3] = 0x10325476;
}

// MD5 更新（输入数据）
static void md5Update(MD5Context* ctx, const unsigned char* input, unsigned int inputLen) {
    unsigned int index = (unsigned int)((ctx->count[0] >> 3) & 0x3F);
    ctx->count[0] += ((uint32_t)inputLen) << 3;
    if (ctx->count[0] < (((uint32_t)inputLen) << 3)) {
        ctx->count[1]++;
    }
    ctx->count[1] += ((uint32_t)inputLen) >> 29;

    unsigned int partLen = 64 - index;
    unsigned int i = 0;

    if (inputLen >= partLen) {
        memcpy(&ctx->buffer[index], input, partLen);
        md5Transform(ctx->state, ctx->buffer);
        for (i = partLen; i + 63 < inputLen; i += 64) {
            md5Transform(ctx->state, &input[i]);
        }
        index = 0;
    }

    memcpy(&ctx->buffer[index], &input[i], inputLen - i);
}

// MD5 最终结果生成
static void md5Final(unsigned char digest[16], MD5Context* ctx) {
    unsigned char bits[8];
    unsigned int index = (unsigned int)((ctx->count[0] >> 3) & 0x3f);
    unsigned int padLen = (index < 56) ? (56 - index) : (120 - index);

    // 保存位数
    for (int i = 0; i < 4; i++) {
        bits[i] = (unsigned char)((ctx->count[0] >> (i * 8)) & 0xff);
    }
    for (int i = 0; i < 4; i++) {
        bits[4 + i] = (unsigned char)((ctx->count[1] >> (i * 8)) & 0xff);
    }

    // 填充：先填 0x80，再填 0，最后填长度
    static unsigned char PADDING[64] = {
        0x80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    };
    md5Update(ctx, PADDING, padLen);
    md5Update(ctx, bits, 8);

    // 将结果输出到 digest（小端序）
    for (int i = 0; i < 4; i++) {
        digest[i] = (unsigned char)((ctx->state[0] >> (i * 8)) & 0xff);
    }
    for (int i = 0; i < 4; i++) {
        digest[4 + i] = (unsigned char)((ctx->state[1] >> (i * 8)) & 0xff);
    }
    for (int i = 0; i < 4; i++) {
        digest[8 + i] = (unsigned char)((ctx->state[2] >> (i * 8)) & 0xff);
    }
    for (int i = 0; i < 4; i++) {
        digest[12 + i] = (unsigned char)((ctx->state[3] >> (i * 8)) & 0xff);
    }
}

// MD5 计算封装函数
// 参数：input - 输入字符串
// 返回：32 位十六进制 MD5 值字符串
string md5Hash(const string& input) {
    unsigned char digest[16];
    MD5Context ctx;
    md5Init(&ctx);
    md5Update(&ctx, (const unsigned char*)input.c_str(), (unsigned int)input.length());
    md5Final(digest, &ctx);

    // 转换为十六进制字符串
    char hexStr[33];
    for (int i = 0; i < 16; i++) {
        sprintf(hexStr + i * 2, "%02x", digest[i]);
    }
    hexStr[32] = '\0';

    return string(hexStr);
}

// ============================================================
// SHA1 安全哈希算法
// SHA1 输出 160 位（20 字节）的哈希值
// 注意：SHA1 也已被证明存在碰撞风险，不推荐用于高安全场景
// ============================================================

// SHA1 上下文结构体
struct SHA1Context {
    uint32_t state[5];      // 状态寄存器（A, B, C, D, E）
    uint32_t count[2];      // 位数计数
    unsigned char buffer[64];  // 输入缓冲区
};

// SHA1 循环左移
#define SHA1_ROTATE_LEFT(value, bits) (((value) << (bits)) | ((value) >> (32 - (bits))))

// SHA1 变换函数（处理一个 512 位分组）
static void sha1Transform(uint32_t state[5], const unsigned char buffer[64]) {
    uint32_t a = state[0], b = state[1], c = state[2], d = state[3], e = state[4];
    uint32_t w[80];

    // 将字节数组转换为 16 个 32 位整数（大端序）
    for (int i = 0, j = 0; i < 16; i++, j += 4) {
        w[i] = ((uint32_t)buffer[j] << 24) |
               ((uint32_t)buffer[j + 1] << 16) |
               ((uint32_t)buffer[j + 2] << 8) |
               ((uint32_t)buffer[j + 3]);
    }

    // 扩展到 80 个 32 位整数
    for (int i = 16; i < 80; i++) {
        w[i] = SHA1_ROTATE_LEFT(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1);
    }

    // 4 轮运算，每轮 20 次
    for (int i = 0; i < 80; i++) {
        uint32_t f, k;
        if (i < 20) {
            f = (b & c) | ((~b) & d);
            k = 0x5A827999;
        } else if (i < 40) {
            f = b ^ c ^ d;
            k = 0x6ED9EBA1;
        } else if (i < 60) {
            f = (b & c) | (b & d) | (c & d);
            k = 0x8F1BBCDC;
        } else {
            f = b ^ c ^ d;
            k = 0xCA62C1D6;
        }

        uint32_t temp = SHA1_ROTATE_LEFT(a, 5) + f + e + k + w[i];
        e = d;
        d = c;
        c = SHA1_ROTATE_LEFT(b, 30);
        b = a;
        a = temp;
    }

    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;
    state[4] += e;
}

// 初始化 SHA1 上下文
static void sha1Init(SHA1Context* ctx) {
    ctx->count[0] = 0;
    ctx->count[1] = 0;
    // SHA1 初始向量
    ctx->state[0] = 0x67452301;
    ctx->state[1] = 0xEFCDAB89;
    ctx->state[2] = 0x98BADCFE;
    ctx->state[3] = 0x10325476;
    ctx->state[4] = 0xC3D2E1F0;
}

// SHA1 更新
static void sha1Update(SHA1Context* ctx, const unsigned char* data, unsigned int len) {
    unsigned int index = (unsigned int)((ctx->count[0] >> 3) & 0x3F);
    ctx->count[0] += len << 3;
    if (ctx->count[0] < (len << 3)) {
        ctx->count[1]++;
    }
    ctx->count[1] += len >> 29;

    unsigned int partLen = 64 - index;
    unsigned int i = 0;

    if (len >= partLen) {
        memcpy(&ctx->buffer[index], data, partLen);
        sha1Transform(ctx->state, ctx->buffer);
        for (i = partLen; i + 63 < len; i += 64) {
            sha1Transform(ctx->state, &data[i]);
        }
        index = 0;
    }

    memcpy(&ctx->buffer[index], &data[i], len - i);
}

// SHA1 最终结果
static void sha1Final(unsigned char digest[20], SHA1Context* ctx) {
    unsigned char bits[8];

    // 保存位数（大端序）
    for (int i = 0; i < 4; i++) {
        bits[i] = (unsigned char)((ctx->count[1] >> ((3 - i) * 8)) & 0xff);
    }
    for (int i = 0; i < 4; i++) {
        bits[4 + i] = (unsigned char)((ctx->count[0] >> ((3 - i) * 8)) & 0xff);
    }

    // 填充
    static unsigned char PADDING[64] = {
        0x80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    };

    unsigned int index = (unsigned int)((ctx->count[0] >> 3) & 0x3f);
    unsigned int padLen = (index < 56) ? (56 - index) : (120 - index);
    sha1Update(ctx, PADDING, padLen);
    sha1Update(ctx, bits, 8);

    // 输出结果（大端序）
    for (int i = 0; i < 5; i++) {
        digest[i * 4] = (unsigned char)((ctx->state[i] >> 24) & 0xff);
        digest[i * 4 + 1] = (unsigned char)((ctx->state[i] >> 16) & 0xff);
        digest[i * 4 + 2] = (unsigned char)((ctx->state[i] >> 8) & 0xff);
        digest[i * 4 + 3] = (unsigned char)(ctx->state[i] & 0xff);
    }
}

// SHA1 计算封装函数
// 参数：input - 输入字符串
// 返回：40 位十六进制 SHA1 值字符串
string sha1Hash(const string& input) {
    unsigned char digest[20];
    SHA1Context ctx;
    sha1Init(&ctx);
    sha1Update(&ctx, (const unsigned char*)input.c_str(), (unsigned int)input.length());
    sha1Final(digest, &ctx);

    char hexStr[41];
    for (int i = 0; i < 20; i++) {
        sprintf(hexStr + i * 2, "%02x", digest[i]);
    }
    hexStr[40] = '\0';

    return string(hexStr);
}

// ============================================================
// 主函数
// ============================================================

int main(int argc, char* argv[]) {
    cout << "========================================" << endl;
    cout << "   常见加密算法实现（C++ 学习版）" << endl;
    cout << "========================================" << endl;

    if (argc < 3) {
        cout << "用法: string_encrypt.exe <操作> <输入文本> [密钥]" << endl;
        cout << "操作类型:" << endl;
        cout << "  xor             - XOR 加解密（需密钥）" << endl;
        cout << "  base64_encode   - Base64 编码" << endl;
        cout << "  base64_decode   - Base64 解码" << endl;
        cout << "  md5             - MD5 哈希" << endl;
        cout << "  sha1            - SHA1 哈希" << endl;
        cout << endl;
        cout << "示例:" << endl;
        cout << "  string_encrypt.exe xor \"Hello\" \"key\"" << endl;
        cout << "  string_encrypt.exe md5 \"password\"" << endl;
        return 1;
    }

    string op = argv[1];       // 操作类型
    string input = argv[2];    // 输入文本

    cout << "输入文本: " << input << endl;
    cout << "----------------------------------------" << endl;

    // 根据操作类型执行相应算法
    if (op == "xor") {
        // XOR 加解密
        if (argc < 4) {
            cout << "[错误] XOR 操作需要指定密钥" << endl;
            return 1;
        }
        string key = argv[3];
        cout << "密钥: " << key << endl;
        cout << endl;

        string encrypted = xorEncrypt(input, key);
        cout << "[XOR 加密结果（十六进制）]" << endl;
        cout << stringToHex(encrypted) << endl;
        cout << endl;

        string decrypted = xorEncrypt(encrypted, key);
        cout << "[XOR 解密结果]" << endl;
        cout << decrypted << endl;

    } else if (op == "base64_encode") {
        // Base64 编码
        string encoded = base64Encode(input);
        cout << "[Base64 编码结果]" << endl;
        cout << encoded << endl;

    } else if (op == "base64_decode") {
        // Base64 解码
        string decoded = base64Decode(input);
        cout << "[Base64 解码结果]" << endl;
        cout << decoded << endl;

    } else if (op == "md5") {
        // MD5 哈希
        string hash = md5Hash(input);
        cout << "[MD5 哈希值（32位小写）]" << endl;
        cout << hash << endl;
        cout << endl;
        cout << "[MD5 哈希值（32位大写）]" << endl;
        string upperHash = hash;
        for (size_t i = 0; i < upperHash.length(); i++) {
            upperHash[i] = toupper(upperHash[i]);
        }
        cout << upperHash << endl;

    } else if (op == "sha1") {
        // SHA1 哈希
        string hash = sha1Hash(input);
        cout << "[SHA1 哈希值（40位小写）]" << endl;
        cout << hash << endl;
        cout << endl;
        cout << "[SHA1 哈希值（40位大写）]" << endl;
        string upperHash = hash;
        for (size_t i = 0; i < upperHash.length(); i++) {
            upperHash[i] = toupper(upperHash[i]);
        }
        cout << upperHash << endl;

    } else {
        cout << "[错误] 不支持的操作类型: " << op << endl;
        return 1;
    }

    cout << endl;
    cout << "========================================" << endl;
    cout << "            操作完成" << endl;
    cout << "========================================" << endl;

    return 0;
}
