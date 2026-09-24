// ============================================================
// 07_file_io.c —— 文件操作
// 编译命令：gcc 07_file_io.c -o 07_file_io
// ============================================================

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    // ---------- 1. 文件打开与关闭 ----------
    printf("========== 文件打开与关闭 ==========\n");

    // fopen 打开文件
    // 模式：r 读, w 写（覆盖）, a 追加, r+ 读写, wb 二进制写, 等
    FILE *fp;

    // 写入文件
    fp = fopen("test.txt", "w");
    if (fp == NULL) {
        printf("文件打开失败！\n");
        return 1;
    }

    printf("文件打开成功，开始写入...\n");
    fclose(fp);  // 关闭文件
    printf("文件已关闭\n");


    // ---------- 2. 字符读写 ----------
    printf("\n========== 字符读写 ==========\n");

    // fputc - 写入字符
    fp = fopen("char_test.txt", "w");
    if (fp != NULL) {
        fputc('H', fp);
        fputc('e', fp);
        fputc('l', fp);
        fputc('l', fp);
        fputc('o', fp);
        fputc('\n', fp);
        fclose(fp);
        printf("字符写入完成\n");
    }

    // fgetc - 读取字符
    fp = fopen("char_test.txt", "r");
    if (fp != NULL) {
        printf("读取的内容：");
        int ch;  // 注意：用 int 接收，因为 EOF 是 -1
        while ((ch = fgetc(fp)) != EOF) {
            printf("%c", ch);
        }
        fclose(fp);
    }


    // ---------- 3. 字符串读写 ----------
    printf("\n========== 字符串读写 ==========\n");

    // fputs - 写入字符串
    fp = fopen("string_test.txt", "w");
    if (fp != NULL) {
        fputs("Hello, World!\n", fp);
        fputs("这是第二行\n", fp);
        fputs("C语言文件操作学习\n", fp);
        fclose(fp);
        printf("字符串写入完成\n");
    }

    // fgets - 读取一行
    fp = fopen("string_test.txt", "r");
    if (fp != NULL) {
        printf("逐行读取：\n");
        char line[100];
        int line_num = 1;
        while (fgets(line, sizeof(line), fp) != NULL) {
            printf("  第%d行：%s", line_num, line);
            line_num++;
        }
        fclose(fp);
    }


    // ---------- 4. 格式化读写 ----------
    printf("\n========== 格式化读写 ==========\n");

    // fprintf - 格式化写入
    fp = fopen("format_test.txt", "w");
    if (fp != NULL) {
        fprintf(fp, "姓名：%s\n", "张三");
        fprintf(fp, "年龄：%d\n", 25);
        fprintf(fp, "分数：%.1f\n", 95.5);
        fprintf(fp, "编号：%04d\n", 123);
        fclose(fp);
        printf("格式化写入完成\n");
    }

    // fscanf - 格式化读取
    fp = fopen("data.txt", "w");
    if (fp != NULL) {
        fprintf(fp, "Alice 20 90.5\n");
        fprintf(fp, "Bob 21 85.0\n");
        fprintf(fp, "Charlie 19 92.5\n");
        fclose(fp);
    }

    fp = fopen("data.txt", "r");
    if (fp != NULL) {
        printf("格式化读取学生数据：\n");
        char name[50];
        int age;
        float score;
        while (fscanf(fp, "%s %d %f", name, &age, &score) == 3) {
            printf("  %s，%d岁，%.1f分\n", name, age, score);
        }
        fclose(fp);
    }


    // ---------- 5. 二进制文件读写 ----------
    printf("\n========== 二进制文件读写 ==========\n");

    // 定义一个结构体用于二进制读写
    typedef struct {
        char name[50];
        int age;
        float score;
    } Student;

    // fwrite - 二进制写入
    Student students[3] = {
        {"小明", 18, 90.0f},
        {"小红", 19, 92.5f},
        {"小刚", 18, 85.0f}
    };

    fp = fopen("students.dat", "wb");  // 二进制写模式
    if (fp != NULL) {
        size_t written = fwrite(students, sizeof(Student), 3, fp);
        printf("写入了 %zu 条记录\n", written);
        fclose(fp);
    }

    // fread - 二进制读取
    Student read_students[3];
    fp = fopen("students.dat", "rb");  // 二进制读模式
    if (fp != NULL) {
        size_t read_count = fread(read_students, sizeof(Student), 3, fp);
        printf("读取了 %zu 条记录：\n", read_count);
        for (size_t i = 0; i < read_count; i++) {
            printf("  %s，%d岁，%.1f分\n",
                   read_students[i].name,
                   read_students[i].age,
                   read_students[i].score);
        }
        fclose(fp);
    }


    // ---------- 6. 文件定位 ----------
    printf("\n========== 文件定位 ==========\n");

    fp = fopen("string_test.txt", "r");
    if (fp != NULL) {
        // ftell - 获取当前文件位置指针
        long pos = ftell(fp);
        printf("初始位置：%ld\n", pos);

        // fseek - 移动文件指针
        fseek(fp, 7, SEEK_SET);  // 从文件开头移动 7 字节
        pos = ftell(fp);
        printf("fseek 后位置：%ld\n", pos);

        char buf[50];
        fgets(buf, sizeof(buf), fp);
        printf("从位置 %ld 读取：%s", pos, buf);

        // rewind - 回到文件开头
        rewind(fp);
        printf("rewind 后位置：%ld\n", ftell(fp));

        fclose(fp);
    }


    // ---------- 7. 文件状态检查 ----------
    printf("\n========== 文件状态检查 ==========\n");

    fp = fopen("string_test.txt", "r");
    if (fp != NULL) {
        // feof - 检查是否到达文件末尾
        while (!feof(fp)) {
            char ch = fgetc(fp);
            if (ch == EOF) break;
            // 处理字符...
        }
        printf("已到达文件末尾\n");

        // ferror - 检查文件操作是否出错
        if (ferror(fp)) {
            printf("文件读取出错\n");
        } else {
            printf("文件读取正常\n");
        }

        fclose(fp);
    }


    // ---------- 8. 文件重命名与删除 ----------
    printf("\n========== 文件重命名与删除 ==========\n");

    // rename - 重命名文件
    if (rename("test.txt", "renamed_test.txt") == 0) {
        printf("文件重命名成功\n");
    } else {
        printf("文件重命名失败\n");
    }

    // remove - 删除文件
    if (remove("char_test.txt") == 0) {
        printf("文件删除成功\n");
    } else {
        printf("文件删除失败\n");
    }

    // 清理临时文件
    remove("string_test.txt");
    remove("format_test.txt");
    remove("data.txt");
    remove("students.dat");
    remove("renamed_test.txt");


    // ---------- 安全小贴士 ----------
    printf("\n========== 安全小贴士 ==========\n");
    printf("1. 打开文件后一定要检查返回值是否为 NULL\n");
    printf("2. 文件使用完毕必须 fclose，否则会资源泄漏\n");
    printf("3. 读取文件时注意缓冲区大小，防止溢出\n");
    printf("4. 路径遍历漏洞：不要直接使用用户输入作为文件路径\n");
    printf("5. 注意文件权限，敏感数据不要明文存储\n");

    return 0;
}
