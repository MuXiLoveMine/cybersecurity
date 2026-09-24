/*
 * ============================================================
 * 文件名：hash_cracker.c
 * 功能描述：哈希破解工具（支持 MD5、SHA1 字典破解）
 * 作者：网络安全学习笔记
 * 日期：2026-09-21
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译方式：
 *    gcc hash_cracker.c -o hash_cracker -lssl -lcrypto (Linux, 需要 OpenSSL)
 *    gcc hash_cracker.c -o hash_canner.exe (Windows, 内置 MD5)
 * 2. 命令行参数：
 *    参数1：哈希值（待破解）
 *    参数2：字典文件路径
 *    参数3：哈希类型（md5/sha1，默认 md5）
 *
 * 【示例】
 *   hash_cracker 5f4dcc3b5aa765d61d8327deb882cf99 rockyou.txt md5
 *   hash_cracker e10adc3949ba59abbe56e057f20f883e wordlist.txt
 *
 * 【原理说明】
 *   读取字典文件中的每个密码，计算其哈希值，
 *   与目标哈希对比，匹配成功则找到明文密码。
 *
 * 【免责声明】
 *   本工具仅供网络安全学习和授权测试使用。
 *   禁止用于非法用途，违者后果自负。
 * ============================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAX_PASSWORD_LEN 128
#define MAX_HASH_LEN 64
#define MD5_LEN 32
#define SHA1_LEN 40

// ==================== MD5 实现 ====================

typedef struct {
    uint32_t state[4];
    uint32_t count[2];
    unsigned char buffer[64];
} MD5_CTX;

#define F(x, y, z) (((x) & (y)) | ((~x) & (z)))
#define G(x, y, z) (((x) & (z)) | ((y) & (~z)))
#define H(x, y, z) ((x) ^ (y) ^ (z))
#define I(x, y, z) ((y) ^ ((x) | (~z)))
#define ROTATE_LEFT(x, n) (((x) << (n)) | ((x) >> (32 - (n))))
#define FF(a, b, c, d, x, s, ac) { (a) += F((b), (c), (d)) + (x) + (uint32_t)(ac); (a) = ROTATE_LEFT((a), (s)); (a) += (b); }
#define GG(a, b, c, d, x, s, ac) { (a) += G((b), (c), (d)) + (x) + (uint32_t)(ac); (a) = ROTATE_LEFT((a), (s)); (a) += (b); }
#define HH(a, b, c, d, x, s, ac) { (a) += H((b), (c), (d)) + (x) + (uint32_t)(ac); (a) = ROTATE_LEFT((a), (s)); (a) += (b); }
#define II(a, b, c, d, x, s, ac) { (a) += I((b), (c), (d)) + (x) + (uint32_t)(ac); (a) = ROTATE_LEFT((a), (s)); (a) += (b); }

static void MD5Transform(uint32_t state[4], unsigned char block[64]);
static void Encode(unsigned char *output, uint32_t *input, unsigned int len);
static void Decode(uint32_t *output, unsigned char *input, unsigned int len);

void MD5Init(MD5_CTX *context) {
    context->count[0] = context->count[1] = 0;
    context->state[0] = 0x67452301;
    context->state[1] = 0xefcdab89;
    context->state[2] = 0x98badcfe;
    context->state[3] = 0x10325476;
}

void MD5Update(MD5_CTX *context, unsigned char *input, unsigned int inputLen) {
    unsigned int i, index, partLen;
    index = (unsigned int)((context->count[0] >> 3) & 0x3F);
    if ((context->count[0] += ((uint32_t)inputLen << 3)) < ((uint32_t)inputLen << 3))
        context->count[1]++;
    context->count[1] += ((uint32_t)inputLen >> 29);
    partLen = 64 - index;
    if (inputLen >= partLen) {
        memcpy((unsigned char *)&context->buffer[index], (unsigned char *)input, partLen);
        MD5Transform(context->state, context->buffer);
        for (i = partLen; i + 63 < inputLen; i += 64)
            MD5Transform(context->state, &input[i]);
        index = 0;
    } else {
        i = 0;
    }
    memcpy((unsigned char *)&context->buffer[index], (unsigned char *)&input[i], inputLen - i);
}

void MD5Final(unsigned char digest[16], MD5_CTX *context) {
    unsigned char bits[8];
    unsigned int index, padLen;
    static unsigned char PADDING[64] = {
        0x80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    };
    Encode(bits, context->count, 8);
    index = (unsigned int)((context->count[0] >> 3) & 0x3f);
    padLen = (index < 56) ? (56 - index) : (120 - index);
    MD5Update(context, PADDING, padLen);
    MD5Update(context, bits, 8);
    Encode(digest, context->state, 16);
    memset((unsigned char *)context, 0, sizeof(*context));
}

static void MD5Transform(uint32_t state[4], unsigned char block[64]) {
    uint32_t a = state[0], b = state[1], c = state[2], d = state[3], x[16];
    Decode(x, block, 64);
    FF(a, b, c, d, x[ 0],  7, 0xd76aa478); FF(d, a, b, c, x[ 1], 12, 0xe8c7b756);
    FF(c, d, a, b, x[ 2], 17, 0x242070db); FF(b, c, d, a, x[ 3], 22, 0xc1bdceee);
    FF(a, b, c, d, x[ 4],  7, 0xf57c0faf); FF(d, a, b, c, x[ 5], 12, 0x4787c62a);
    FF(c, d, a, b, x[ 6], 17, 0xa8304613); FF(b, c, d, a, x[ 7], 22, 0xfd469501);
    FF(a, b, c, d, x[ 8],  7, 0x698098d8); FF(d, a, b, c, x[ 9], 12, 0x8b44f7af);
    FF(c, d, a, b, x[10], 17, 0xffff5bb1); FF(b, c, d, a, x[11], 22, 0x895cd7be);
    FF(a, b, c, d, x[12],  7, 0x6b901122); FF(d, a, b, c, x[13], 12, 0xfd987193);
    FF(c, d, a, b, x[14], 17, 0xa679438e); FF(b, c, d, a, x[15], 22, 0x49b40821);
    GG(a, b, c, d, x[ 1],  5, 0xf61e2562); GG(d, a, b, c, x[ 6],  9, 0xc040b340);
    GG(c, d, a, b, x[11], 14, 0x265e5a51); GG(b, c, d, a, x[ 0], 20, 0xe9b6c7aa);
    GG(a, b, c, d, x[ 5],  5, 0xd62f105d); GG(d, a, b, c, x[10],  9, 0x02441453);
    GG(c, d, a, b, x[15], 14, 0xd8a1e681); GG(b, c, d, a, x[ 4], 20, 0xe7d3fbc8);
    GG(a, b, c, d, x[ 9],  5, 0x21e1cde6); GG(d, a, b, c, x[14],  9, 0xc33707d6);
    GG(c, d, a, b, x[ 3], 14, 0xf4d50d87); GG(b, c, d, a, x[ 8], 20, 0x455a14ed);
    GG(a, b, c, d, x[13],  5, 0xa9e3e905); GG(d, a, b, c, x[ 2],  9, 0xfcefa3f8);
    GG(c, d, a, b, x[ 7], 14, 0x676f02d9); GG(b, c, d, a, x[12], 20, 0x8d2a4c8a);
    HH(a, b, c, d, x[ 5],  4, 0xfffa3942); HH(d, a, b, c, x[ 8], 11, 0x8771f681);
    HH(c, d, a, b, x[11], 16, 0x6d9d6122); HH(b, c, d, a, x[14], 23, 0xfde5380c);
    HH(a, b, c, d, x[ 1],  4, 0xa4beea44); HH(d, a, b, c, x[ 4], 11, 0x4bdecfa9);
    HH(c, d, a, b, x[ 7], 16, 0xf6bb4b60); HH(b, c, d, a, x[10], 23, 0xbebfbc70);
    HH(a, b, c, d, x[13],  4, 0x289b7ec6); HH(d, a, b, c, x[ 0], 11, 0xeaa127fa);
    HH(c, d, a, b, x[ 3], 16, 0xd4ef3085); HH(b, c, d, a, x[ 6], 23, 0x04881d05);
    HH(a, b, c, d, x[ 9],  4, 0xd9d4d039); HH(d, a, b, c, x[12], 11, 0xe6db99e5);
    HH(c, d, a, b, x[15], 16, 0x1fa27cf8); HH(b, c, d, a, x[ 2], 23, 0xc4ac5665);
    II(a, b, c, d, x[ 0],  6, 0xf4292244); II(d, a, b, c, x[ 7], 10, 0x432aff97);
    II(c, d, a, b, x[14], 15, 0xab9423a7); II(b, c, d, a, x[ 5], 21, 0xfc93a039);
    II(a, b, c, d, x[12],  6, 0x655b59c3); II(d, a, b, c, x[ 3], 10, 0x8f0ccc92);
    II(c, d, a, b, x[10], 15, 0xffeff47d); II(b, c, d, a, x[ 1], 21, 0x85845dd1);
    II(a, b, c, d, x[ 8],  6, 0x6fa87e4f); II(d, a, b, c, x[15], 10, 0xfe2ce6e0);
    II(c, d, a, b, x[ 6], 15, 0xa3014314); II(b, c, d, a, x[13], 21, 0x4e0811a1);
    II(a, b, c, d, x[ 4],  6, 0xf7537e82); II(d, a, b, c, x[11], 10, 0xbd3af235);
    II(c, d, a, b, x[ 2], 15, 0x2ad7d2bb); II(b, c, d, a, x[ 9], 21, 0xeb86d391);
    state[0] += a; state[1] += b; state[2] += c; state[3] += d;
    memset((unsigned char *)x, 0, sizeof(x));
}

static void Encode(unsigned char *output, uint32_t *input, unsigned int len) {
    unsigned int i, j;
    for (i = 0, j = 0; j < len; i++, j += 4) {
        output[j] = (unsigned char)(input[i] & 0xff);
        output[j+1] = (unsigned char)((input[i] >> 8) & 0xff);
        output[j+2] = (unsigned char)((input[i] >> 16) & 0xff);
        output[j+3] = (unsigned char)((input[i] >> 24) & 0xff);
    }
}

static void Decode(uint32_t *output, unsigned char *input, unsigned int len) {
    unsigned int i, j;
    for (i = 0, j = 0; j < len; i++, j += 4) {
        output[i] = ((uint32_t)input[j]) | (((uint32_t)input[j+1]) << 8) |
                    (((uint32_t)input[j+2]) << 16) | (((uint32_t)input[j+3]) << 24);
    }
}

// 计算字符串的 MD5 哈希，返回十六进制字符串
void md5_hex(const char *input, char *output) {
    MD5_CTX ctx;
    unsigned char digest[16];
    MD5Init(&ctx);
    MD5Update(&ctx, (unsigned char *)input, (unsigned int)strlen(input));
    MD5Final(digest, &ctx);
    for (int i = 0; i < 16; i++) {
        sprintf(output + i * 2, "%02x", digest[i]);
    }
    output[32] = '\0';
}

// ==================== SHA1 实现 ====================

typedef struct {
    uint32_t state[5];
    uint32_t count[2];
    unsigned char buffer[64];
} SHA1_CTX;

#define SHA1_ROTATE_LEFT(value, bits) (((value) << (bits)) | ((value) >> (32 - (bits))))

#define SHA1_BLKSIZE 64
#define SHA1_DIGESTSIZE 20

static void SHA1Transform(uint32_t state[5], unsigned char buffer[64]) {
    uint32_t a, b, c, d, e;
    uint32_t w[80];
    int t;
    uint32_t tmp;

    for (t = 0; t < 16; t++) {
        w[t] = ((uint32_t)buffer[t*4] << 24) | ((uint32_t)buffer[t*4+1] << 16) |
               ((uint32_t)buffer[t*4+2] << 8) | ((uint32_t)buffer[t*4+3]);
    }
    for (t = 16; t < 80; t++) {
        tmp = w[t-3] ^ w[t-8] ^ w[t-14] ^ w[t-16];
        w[t] = SHA1_ROTATE_LEFT(tmp, 1);
    }

    a = state[0]; b = state[1]; c = state[2]; d = state[3]; e = state[4];

    for (t = 0; t < 20; t++) {
        tmp = SHA1_ROTATE_LEFT(a, 5) + ((b & c) | ((~b) & d)) + e + w[t] + 0x5A827999;
        e = d; d = c; c = SHA1_ROTATE_LEFT(b, 30); b = a; a = tmp;
    }
    for (t = 20; t < 40; t++) {
        tmp = SHA1_ROTATE_LEFT(a, 5) + (b ^ c ^ d) + e + w[t] + 0x6ED9EBA1;
        e = d; d = c; c = SHA1_ROTATE_LEFT(b, 30); b = a; a = tmp;
    }
    for (t = 40; t < 60; t++) {
        tmp = SHA1_ROTATE_LEFT(a, 5) + ((b & c) | (b & d) | (c & d)) + e + w[t] + 0x8F1BBCDC;
        e = d; d = c; c = SHA1_ROTATE_LEFT(b, 30); b = a; a = tmp;
    }
    for (t = 60; t < 80; t++) {
        tmp = SHA1_ROTATE_LEFT(a, 5) + (b ^ c ^ d) + e + w[t] + 0xCA62C1D6;
        e = d; d = c; c = SHA1_ROTATE_LEFT(b, 30); b = a; a = tmp;
    }

    state[0] += a; state[1] += b; state[2] += c; state[3] += d; state[4] += e;
}

void SHA1Init(SHA1_CTX *context) {
    context->count[0] = context->count[1] = 0;
    context->state[0] = 0x67452301;
    context->state[1] = 0xEFCDAB89;
    context->state[2] = 0x98BADCFE;
    context->state[3] = 0x10325476;
    context->state[4] = 0xC3D2E1F0;
}

void SHA1Update(SHA1_CTX *context, unsigned char *data, unsigned int len) {
    unsigned int i, j;
    j = (unsigned int)((context->count[0] >> 3) & 63);
    if ((context->count[0] += len << 3) < (len << 3)) context->count[1]++;
    context->count[1] += (len >> 29);
    if ((j + len) > 63) {
        memcpy(&context->buffer[j], data, (i = 64 - j));
        SHA1Transform(context->state, context->buffer);
        for (; i + 63 < len; i += 64) SHA1Transform(context->state, &data[i]);
        j = 0;
    } else {
        i = 0;
    }
    memcpy(&context->buffer[j], &data[i], len - i);
}

void SHA1Final(unsigned char digest[20], SHA1_CTX *context) {
    unsigned i;
    unsigned char finalcount[8];
    unsigned char c;

    for (i = 0; i < 8; i++) {
        finalcount[i] = (unsigned char)((context->count[(i >= 4 ? 0 : 1)] >> ((3 - (i & 3)) * 8)) & 255);
    }
    c = 0200;
    SHA1Update(context, &c, 1);
    while ((context->count[0] & 504) != 448) {
        c = 0;
        SHA1Update(context, &c, 1);
    }
    SHA1Update(context, finalcount, 8);
    for (i = 0; i < 20; i++) {
        digest[i] = (unsigned char)((context->state[i >> 2] >> ((3 - (i & 3)) * 8)) & 255);
    }
    memset(context, 0, sizeof(*context));
}

void sha1_hex(const char *input, char *output) {
    SHA1_CTX ctx;
    unsigned char digest[20];
    SHA1Init(&ctx);
    SHA1Update(&ctx, (unsigned char *)input, (unsigned int)strlen(input));
    SHA1Final(digest, &ctx);
    for (int i = 0; i < 20; i++) {
        sprintf(output + i * 2, "%02x", digest[i]);
    }
    output[40] = '\0';
}

// ==================== 主程序 ====================

void toLowerCase(char *str) {
    for (int i = 0; str[i]; i++) {
        if (str[i] >= 'A' && str[i] <= 'Z') {
            str[i] = str[i] + 32;
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("用法: %s <目标哈希> <字典文件> [哈希类型]\n", argv[0]);
        printf("  哈希类型: md5 (默认), sha1\n");
        printf("\n示例:\n");
        printf("  %s 5f4dcc3b5aa765d61d8327deb882cf99 wordlist.txt md5\n", argv[0]);
        return 1;
    }

    char targetHash[MAX_HASH_LEN];
    strncpy(targetHash, argv[1], MAX_HASH_LEN - 1);
    targetHash[MAX_HASH_LEN - 1] = '\0';
    toLowerCase(targetHash);

    const char *dictFile = argv[2];

    char hashType[16] = "md5";
    if (argc >= 4) {
        strncpy(hashType, argv[3], sizeof(hashType) - 1);
        hashType[sizeof(hashType) - 1] = '\0';
        toLowerCase(hashType);
    }

    // 验证哈希类型和长度
    int hashLen = (int)strlen(targetHash);
    if (strcmp(hashType, "md5") == 0 && hashLen != MD5_LEN) {
        fprintf(stderr, "[错误] MD5 哈希长度应为 32 个字符，当前: %d\n", hashLen);
        return 1;
    }
    if (strcmp(hashType, "sha1") == 0 && hashLen != SHA1_LEN) {
        fprintf(stderr, "[错误] SHA1 哈希长度应为 40 个字符，当前: %d\n", hashLen);
        return 1;
    }

    // 打开字典文件
    FILE *fp = fopen(dictFile, "r");
    if (fp == NULL) {
        fprintf(stderr, "[错误] 无法打开字典文件: %s\n", dictFile);
        return 1;
    }

    // 打印信息
    printf("========================================\n");
    printf("       哈希破解工具（C 语言版）\n");
    printf("========================================\n");
    printf("目标哈希: %s\n", targetHash);
    printf("哈希类型: %s\n", hashType);
    printf("字典文件: %s\n", dictFile);
    printf("========================================\n");
    printf("[*] 开始破解...\n");
    printf("----------------------------------------\n");

    // 开始计时
    clock_t startTime = clock();

    char password[MAX_PASSWORD_LEN];
    char computedHash[MAX_HASH_LEN];
    int count = 0;
    int found = 0;

    while (fgets(password, sizeof(password), fp) != NULL) {
        // 去掉换行符
        int len = (int)strlen(password);
        while (len > 0 && (password[len-1] == '\n' || password[len-1] == '\r')) {
            password[len-1] = '\0';
            len--;
        }
        if (len == 0) continue;

        count++;

        // 计算哈希
        if (strcmp(hashType, "md5") == 0) {
            md5_hex(password, computedHash);
        } else if (strcmp(hashType, "sha1") == 0) {
            sha1_hex(password, computedHash);
        }

        // 对比
        if (strcmp(computedHash, targetHash) == 0) {
            found = 1;
            printf("\n[+] 破解成功！\n");
            printf("    哈希: %s\n", targetHash);
            printf("    明文: %s\n", password);
            break;
        }

        // 进度显示
        if (count % 10000 == 0) {
            printf("  ... 已尝试 %d 个密码\n", count);
        }
    }

    fclose(fp);

    // 计算耗时
    clock_t endTime = clock();
    double elapsed = (double)(endTime - startTime) / CLOCKS_PER_SEC;

    // 输出结果
    printf("----------------------------------------\n\n");
    printf("========================================\n");
    printf("            破解结果\n");
    printf("========================================\n");
    printf("尝试密码数: %d\n", count);
    printf("耗时: %.2f 秒\n", elapsed);
    if (elapsed > 0) {
        printf("速度: %.0f 密码/秒\n", count / elapsed);
    }

    if (!found) {
        printf("\n[-] 破解失败，字典中未找到匹配的密码\n");
    }

    printf("========================================\n");
    printf("            破解完成\n");
    printf("========================================\n");

    return found ? 0 : 2;
}
