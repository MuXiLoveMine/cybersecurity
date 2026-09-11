/*
 * ============================================================
 * 文件名：password_cracker.cpp
 * 功能描述：简单密码破解工具（字典攻击，MD5/SHA1 哈希爆破）
 * 作者：网络安全学习笔记
 * 日期：2026-09-10
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译方式（Windows + MinGW）：
 *    g++ password_cracker.cpp -o password_cracker.exe
 * 2. 编译方式（Visual Studio）：
 *    cl password_cracker.cpp
 * 3. 命令行参数：
 *    参数1：哈希类型（md5 或 sha1）
 *    参数2：目标哈希值
 *    参数3：字典文件路径
 *
 * 【示例】
 *   password_cracker.exe md5 5f4dcc3b5aa765d61d8327deb882cf99 wordlist.txt
 *   password_cracker.exe sha1 5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8 wordlist.txt
 *
 * 【内置字典】
 *   如果不指定字典文件，将使用内置的弱口令字典
 *   包含常见弱密码（如 123456、password、admin 等）
 *
 * 【工作原理】
 *   1. 读取字典中的每个密码
 *   2. 对密码进行 MD5 或 SHA1 哈希计算
 *   3. 将计算结果与目标哈希值比较
 *   4. 如果匹配，则找到原始密码
 *
 * 【免责声明】
 *   本工具仅供密码学学习和安全研究使用。
 *   用于测试自己系统的密码强度，了解弱口令的危害。
 *   禁止用于破解他人密码或进行未授权的活动。
 *   使用本工具请遵守当地法律法规。
 * ============================================================
 */

// 引入必要的头文件
#include <iostream>     // 标准输入输出
#include <string>       // 字符串处理
#include <fstream>      // 文件操作
#include <vector>       // 动态数组
#include <cstring>      // C 字符串
#include <cstdint>      // 标准整数类型
#include <cstdio>       // C 标准输入输出
#include <ctime>        // 时间统计
#include <algorithm>    // 算法

using namespace std;

// ============================================================
// MD5 算法实现（同 string_encrypt.cpp 中的 MD5）
// ============================================================

struct MD5Context {
    uint32_t state[4];
    uint32_t count[2];
    unsigned char buffer[64];
};

#define F(x, y, z) (((x) & (y)) | ((~x) & (z)))
#define G(x, y, z) (((x) & (z)) | ((y) & (~z)))
#define H(x, y, z) ((x) ^ (y) ^ (z))
#define I(x, y, z) ((y) ^ ((x) | (~z)))
#define ROTATE_LEFT(x, n) (((x) << (n)) | ((x) >> (32 - (n))))

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

static void md5Transform(uint32_t state[4], const unsigned char block[64]) {
    uint32_t a = state[0], b = state[1], c = state[2], d = state[3];
    uint32_t x[16];

    for (int i = 0, j = 0; i < 16; i++, j += 4) {
        x[i] = ((uint32_t)block[j]) |
               (((uint32_t)block[j + 1]) << 8) |
               (((uint32_t)block[j + 2]) << 16) |
               (((uint32_t)block[j + 3]) << 24);
    }

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

    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;
}

static void md5Init(MD5Context* ctx) {
    ctx->count[0] = 0;
    ctx->count[1] = 0;
    ctx->state[0] = 0x67452301;
    ctx->state[1] = 0xefcdab89;
    ctx->state[2] = 0x98badcfe;
    ctx->state[3] = 0x10325476;
}

static void md5Update(MD5Context* ctx, const unsigned char* input, unsigned int inputLen) {
    unsigned int index = (unsigned int)((ctx->count[0] >> 3) & 0x3F);
    ctx->count[0] += ((uint32_t)inputLen) << 3;
    if (ctx->count[0] < (((uint32_t)inputLen) << 3)) ctx->count[1]++;
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

static void md5Final(unsigned char digest[16], MD5Context* ctx) {
    unsigned char bits[8];
    unsigned int index = (unsigned int)((ctx->count[0] >> 3) & 0x3f);
    unsigned int padLen = (index < 56) ? (56 - index) : (120 - index);

    for (int i = 0; i < 4; i++)
        bits[i] = (unsigned char)((ctx->count[0] >> (i * 8)) & 0xff);
    for (int i = 0; i < 4; i++)
        bits[4 + i] = (unsigned char)((ctx->count[1] >> (i * 8)) & 0xff);

    static unsigned char PADDING[64] = {
        0x80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    };
    md5Update(ctx, PADDING, padLen);
    md5Update(ctx, bits, 8);

    for (int i = 0; i < 4; i++) digest[i] = (unsigned char)((ctx->state[0] >> (i * 8)) & 0xff);
    for (int i = 0; i < 4; i++) digest[4 + i] = (unsigned char)((ctx->state[1] >> (i * 8)) & 0xff);
    for (int i = 0; i < 4; i++) digest[8 + i] = (unsigned char)((ctx->state[2] >> (i * 8)) & 0xff);
    for (int i = 0; i < 4; i++) digest[12 + i] = (unsigned char)((ctx->state[3] >> (i * 8)) & 0xff);
}

string md5Hash(const string& input) {
    unsigned char digest[16];
    MD5Context ctx;
    md5Init(&ctx);
    md5Update(&ctx, (const unsigned char*)input.c_str(), (unsigned int)input.length());
    md5Final(digest, &ctx);

    char hexStr[33];
    for (int i = 0; i < 16; i++) sprintf(hexStr + i * 2, "%02x", digest[i]);
    hexStr[32] = '\0';
    return string(hexStr);
}

// ============================================================
// SHA1 算法实现
// ============================================================

struct SHA1Context {
    uint32_t state[5];
    uint32_t count[2];
    unsigned char buffer[64];
};

#define SHA1_ROTATE_LEFT(value, bits) (((value) << (bits)) | ((value) >> (32 - (bits))))

static void sha1Transform(uint32_t state[5], const unsigned char buffer[64]) {
    uint32_t a = state[0], b = state[1], c = state[2], d = state[3], e = state[4];
    uint32_t w[80];

    for (int i = 0, j = 0; i < 16; i++, j += 4) {
        w[i] = ((uint32_t)buffer[j] << 24) |
               ((uint32_t)buffer[j + 1] << 16) |
               ((uint32_t)buffer[j + 2] << 8) |
               ((uint32_t)buffer[j + 3]);
    }
    for (int i = 16; i < 80; i++) {
        w[i] = SHA1_ROTATE_LEFT(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1);
    }
    for (int i = 0; i < 80; i++) {
        uint32_t f, k;
        if (i < 20) { f = (b & c) | ((~b) & d); k = 0x5A827999; }
        else if (i < 40) { f = b ^ c ^ d; k = 0x6ED9EBA1; }
        else if (i < 60) { f = (b & c) | (b & d) | (c & d); k = 0x8F1BBCDC; }
        else { f = b ^ c ^ d; k = 0xCA62C1D6; }
        uint32_t temp = SHA1_ROTATE_LEFT(a, 5) + f + e + k + w[i];
        e = d; d = c; c = SHA1_ROTATE_LEFT(b, 30); b = a; a = temp;
    }
    state[0] += a; state[1] += b; state[2] += c; state[3] += d; state[4] += e;
}

static void sha1Init(SHA1Context* ctx) {
    ctx->count[0] = 0; ctx->count[1] = 0;
    ctx->state[0] = 0x67452301;
    ctx->state[1] = 0xEFCDAB89;
    ctx->state[2] = 0x98BADCFE;
    ctx->state[3] = 0x10325476;
    ctx->state[4] = 0xC3D2E1F0;
}

static void sha1Update(SHA1Context* ctx, const unsigned char* data, unsigned int len) {
    unsigned int index = (unsigned int)((ctx->count[0] >> 3) & 0x3F);
    ctx->count[0] += len << 3;
    if (ctx->count[0] < (len << 3)) ctx->count[1]++;
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

static void sha1Final(unsigned char digest[20], SHA1Context* ctx) {
    unsigned char bits[8];
    for (int i = 0; i < 4; i++) bits[i] = (unsigned char)((ctx->count[1] >> ((3 - i) * 8)) & 0xff);
    for (int i = 0; i < 4; i++) bits[4 + i] = (unsigned char)((ctx->count[0] >> ((3 - i) * 8)) & 0xff);

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

    for (int i = 0; i < 5; i++) {
        digest[i * 4] = (unsigned char)((ctx->state[i] >> 24) & 0xff);
        digest[i * 4 + 1] = (unsigned char)((ctx->state[i] >> 16) & 0xff);
        digest[i * 4 + 2] = (unsigned char)((ctx->state[i] >> 8) & 0xff);
        digest[i * 4 + 3] = (unsigned char)(ctx->state[i] & 0xff);
    }
}

string sha1Hash(const string& input) {
    unsigned char digest[20];
    SHA1Context ctx;
    sha1Init(&ctx);
    sha1Update(&ctx, (const unsigned char*)input.c_str(), (unsigned int)input.length());
    sha1Final(digest, &ctx);

    char hexStr[41];
    for (int i = 0; i < 20; i++) sprintf(hexStr + i * 2, "%02x", digest[i]);
    hexStr[40] = '\0';
    return string(hexStr);
}

// ============================================================
// 字符串转小写（用于哈希比较时忽略大小写）
// ============================================================
string toLower(const string& str) {
    string result = str;
    for (size_t i = 0; i < result.length(); i++) {
        result[i] = tolower(result[i]);
    }
    return result;
}

// ============================================================
// 内置弱口令字典
// 包含常见的弱密码，用于测试和学习
// ============================================================
vector<string> getBuiltinWordlist() {
    vector<string> wordlist;

    // 常见弱密码 Top 50
    const char* passwords[] = {
        "123456", "password", "12345678", "qwerty", "123456789",
        "12345", "1234", "111111", "1234567", "dragon",
        "123123", "baseball", "iloveyou", "trustno1", "sunshine",
        "princess", "admin", "welcome", "shadow", "superman",
        "michael", "football", "abc123", "monkey", "letmein",
        "696969", "master", "login", "mustang", "batman",
        "access", "hello", "charlie", "donald", "qwertyuiop",
        "passw0rd", "000000", "123321", "654321", "qazwsx",
        "123qwe", "password1", "123456a", "a123456", "1234567890",
        "test", "root", "toor", "administrator", "guest",
        NULL
    };

    for (int i = 0; passwords[i] != NULL; i++) {
        wordlist.push_back(passwords[i]);
    }

    return wordlist;
}

// ============================================================
// 从文件加载字典
// ============================================================
vector<string> loadWordlistFromFile(const string& filename) {
    vector<string> wordlist;
    ifstream file(filename.c_str());

    if (!file.is_open()) {
        cerr << "[错误] 无法打开字典文件: " << filename << endl;
        return wordlist;
    }

    string line;
    while (getline(file, line)) {
        // 去除首尾空白字符
        size_t start = line.find_first_not_of(" \t\r\n");
        size_t end = line.find_last_not_of(" \t\r\n");
        if (start != string::npos && end != string::npos) {
            line = line.substr(start, end - start + 1);
        } else {
            line = "";
        }

        // 跳过空行和注释行
        if (line.empty() || line[0] == '#') {
            continue;
        }

        wordlist.push_back(line);
    }

    file.close();
    return wordlist;
}

// ============================================================
// 破解结果结构体
// ============================================================
struct CrackResult {
    bool found;       // 是否找到密码
    string password;  // 找到的密码
    int attempts;     // 尝试次数
    double timeUsed;  // 用时（秒）
};

// ============================================================
// MD5 字典攻击
// ============================================================
CrackResult crackMD5(const string& targetHash, const vector<string>& wordlist) {
    CrackResult result;
    result.found = false;
    result.attempts = 0;

    string targetLower = toLower(targetHash);

    clock_t startTime = clock();

    for (size_t i = 0; i < wordlist.size(); i++) {
        result.attempts++;
        string hash = md5Hash(wordlist[i]);

        if (hash == targetLower) {
            result.found = true;
            result.password = wordlist[i];
            break;
        }

        // 每尝试 1000 个显示进度
        if (result.attempts % 1000 == 0) {
            cout << "  ... 已尝试 " << result.attempts << " 个密码" << endl;
        }
    }

    clock_t endTime = clock();
    result.timeUsed = (double)(endTime - startTime) / CLOCKS_PER_SEC;

    return result;
}

// ============================================================
// SHA1 字典攻击
// ============================================================
CrackResult crackSHA1(const string& targetHash, const vector<string>& wordlist) {
    CrackResult result;
    result.found = false;
    result.attempts = 0;

    string targetLower = toLower(targetHash);

    clock_t startTime = clock();

    for (size_t i = 0; i < wordlist.size(); i++) {
        result.attempts++;
        string hash = sha1Hash(wordlist[i]);

        if (hash == targetLower) {
            result.found = true;
            result.password = wordlist[i];
            break;
        }

        if (result.attempts % 1000 == 0) {
            cout << "  ... 已尝试 " << result.attempts << " 个密码" << endl;
        }
    }

    clock_t endTime = clock();
    result.timeUsed = (double)(endTime - startTime) / CLOCKS_PER_SEC;

    return result;
}

// ============================================================
// 主函数
// ============================================================
int main(int argc, char* argv[]) {
    cout << "========================================" << endl;
    cout << "   密码破解工具（C++ 字典攻击版）" << endl;
    cout << "========================================" << endl;

    if (argc < 3) {
        cout << "用法: password_cracker.exe <哈希类型> <目标哈希> [字典文件]" << endl;
        cout << "哈希类型: md5 或 sha1" << endl;
        cout << endl;
        cout << "示例:" << endl;
        cout << "  password_cracker.exe md5 5f4dcc3b5aa765d61d8327deb882cf99" << endl;
        cout << "  password_cracker.exe sha1 <hash> wordlist.txt" << endl;
        cout << endl;
        cout << "测试用例（密码是 password）:" << endl;
        cout << "  MD5:  5f4dcc3b5aa765d61d8327deb882cf99" << endl;
        cout << "  SHA1: 5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8" << endl;
        return 1;
    }

    string hashType = toLower(argv[1]);  // 哈希类型
    string targetHash = argv[2];          // 目标哈希值

    // 校验哈希类型
    if (hashType != "md5" && hashType != "sha1") {
        cerr << "[错误] 不支持的哈希类型: " << hashType << "（仅支持 md5 或 sha1）" << endl;
        return 1;
    }

    // 校验哈希长度
    if (hashType == "md5" && targetHash.length() != 32) {
        cerr << "[错误] MD5 哈希长度应为 32 位" << endl;
        return 1;
    }
    if (hashType == "sha1" && targetHash.length() != 40) {
        cerr << "[错误] SHA1 哈希长度应为 40 位" << endl;
        return 1;
    }

    // ===================== 加载字典 =====================
    vector<string> wordlist;

    if (argc >= 4) {
        // 使用用户指定的字典文件
        wordlist = loadWordlistFromFile(argv[3]);
        cout << "[*] 已加载字典文件: " << argv[3] << endl;
    } else {
        // 使用内置字典
        wordlist = getBuiltinWordlist();
        cout << "[*] 使用内置弱口令字典" << endl;
    }

    if (wordlist.empty()) {
        cerr << "[错误] 字典为空" << endl;
        return 1;
    }

    // ===================== 打印信息 =====================
    cout << "----------------------------------------" << endl;
    cout << "哈希类型: " << hashType << endl;
    cout << "目标哈希: " << targetHash << endl;
    cout << "字典大小: " << wordlist.size() << " 条" << endl;
    cout << "========================================" << endl;
    cout << "[*] 开始破解..." << endl;
    cout << "----------------------------------------" << endl;

    // ===================== 执行破解 =====================
    CrackResult result;

    if (hashType == "md5") {
        result = crackMD5(targetHash, wordlist);
    } else {
        result = crackSHA1(targetHash, wordlist);
    }

    // ===================== 输出结果 =====================
    cout << "----------------------------------------" << endl;
    cout << endl;
    cout << "========================================" << endl;
    cout << "            破解结果" << endl;
    cout << "========================================" << endl;

    if (result.found) {
        cout << "[成功] 密码已找到！" << endl;
        cout << "----------------------------------------" << endl;
        cout << "原始密码: " << result.password << endl;
        cout << "目标哈希: " << targetHash << endl;
        cout << "尝试次数: " << result.attempts << endl;
        cout << "用时: " << result.timeUsed << " 秒" << endl;
        if (result.timeUsed > 0) {
            cout << "速度: " << (int)(result.attempts / result.timeUsed) << " 次/秒" << endl;
        }
    } else {
        cout << "[失败] 未在字典中找到匹配的密码" << endl;
        cout << "----------------------------------------" << endl;
        cout << "尝试次数: " << result.attempts << endl;
        cout << "用时: " << result.timeUsed << " 秒" << endl;
        cout << endl;
        cout << "[提示] 可能的原因:" << endl;
        cout << "  1. 密码不在字典中" << endl;
        cout << "  2. 哈希值不正确" << endl;
        cout << "  3. 使用了其他哈希算法" << endl;
    }

    cout << "========================================" << endl;

    return 0;
}
