// ============================================================
// 06_struct.c —— 结构体、联合体、枚举
// 编译命令：gcc 06_struct.c -o 06_struct
// ============================================================

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// ---------- 1. 结构体定义 ----------
// 结构体是用户自定义的数据类型，可以包含多个不同类型的成员

// 定义一个学生结构体
struct Student {
    char name[50];    // 姓名
    int age;          // 年龄
    float score;      // 分数
    int id;           // 学号
};

// 使用 typedef 简化类型名
typedef struct {
    char name[50];
    int age;
    float salary;
    char department[30];
} Employee;

// 嵌套结构体
typedef struct {
    int year;
    int month;
    int day;
} Date;

typedef struct {
    char name[50];
    Date birthday;    // 嵌套结构体成员
    char address[100];
} Person;


// ---------- 2. 联合体定义 ----------
// 联合体的所有成员共享同一块内存空间，大小为最大成员的大小
typedef union {
    int i;
    float f;
    char c;
    double d;
} DataUnion;


// ---------- 3. 枚举定义 ----------
// 枚举是一组命名的整型常量
typedef enum {
    RED,        // 0
    GREEN,      // 1
    BLUE,       // 2
    YELLOW,     // 3
    PURPLE      // 4
} Color;

// 也可以指定枚举值
typedef enum {
    MONDAY = 1,
    TUESDAY,
    WEDNESDAY,
    THURSDAY,
    FRIDAY,
    SATURDAY,
    SUNDAY
} Weekday;


// ---------- 4. 结构体指针与函数 ----------
void print_student(struct Student s);
void print_student_ptr(struct Student *s);
void set_student_score(struct Student *s, float score);


// ---------- 主函数 ----------
int main() {
    // ---------- 1. 结构体基础 ----------
    printf("========== 结构体基础 ==========\n");

    // 声明并初始化结构体变量
    struct Student s1;
    strcpy(s1.name, "张三");
    s1.age = 20;
    s1.score = 95.5f;
    s1.id = 1001;

    printf("学生信息：\n");
    printf("  姓名：%s\n", s1.name);
    printf("  年龄：%d\n", s1.age);
    printf("  分数：%.1f\n", s1.score);
    printf("  学号：%d\n", s1.id);

    // 另一种初始化方式
    struct Student s2 = {"李四", 21, 88.0f, 1002};
    printf("\n学生2：%s，年龄 %d，分数 %.1f\n", s2.name, s2.age, s2.score);

    // 结构体大小
    printf("\nstruct Student 大小 = %zu 字节\n", sizeof(struct Student));


    // ---------- 2. typedef 结构体 ----------
    printf("\n========== typedef 结构体 ==========\n");

    Employee emp1;
    strcpy(emp1.name, "王五");
    emp1.age = 30;
    emp1.salary = 15000.0f;
    strcpy(emp1.department, "安全部");

    printf("员工：%s，部门：%s，薪资：%.1f\n",
           emp1.name, emp1.department, emp1.salary);


    // ---------- 3. 嵌套结构体 ----------
    printf("\n========== 嵌套结构体 ==========\n");

    Person p1;
    strcpy(p1.name, "赵六");
    p1.birthday.year = 1995;
    p1.birthday.month = 6;
    p1.birthday.day = 15;
    strcpy(p1.address, "北京市朝阳区");

    printf("个人信息：\n");
    printf("  姓名：%s\n", p1.name);
    printf("  生日：%d-%02d-%02d\n",
           p1.birthday.year, p1.birthday.month, p1.birthday.day);
    printf("  地址：%s\n", p1.address);


    // ---------- 4. 结构体数组 ----------
    printf("\n========== 结构体数组 ==========\n");

    struct Student class[3] = {
        {"小明", 18, 90.0f, 2001},
        {"小红", 19, 92.5f, 2002},
        {"小刚", 18, 85.0f, 2003}
    };

    printf("班级学生列表：\n");
    for (int i = 0; i < 3; i++) {
        printf("  %d. %s - %.1f 分\n",
               class[i].id, class[i].name, class[i].score);
    }


    // ---------- 5. 结构体指针 ----------
    printf("\n========== 结构体指针 ==========\n");

    struct Student s3 = {"小七", 22, 78.5f, 1003};
    struct Student *p_s = &s3;

    // 使用 -> 运算符访问结构体指针的成员
    printf("通过指针访问：\n");
    printf("  姓名：%s\n", p_s->name);
    printf("  年龄：%d\n", p_s->age);
    printf("  分数：%.1f\n", p_s->score);

    // 三种等价的访问方式
    printf("\n三种等价访问方式：\n");
    printf("  s3.name     = %s\n", s3.name);
    printf("  (*p_s).name = %s\n", (*p_s).name);
    printf("  p_s->name   = %s\n", p_s->name);


    // ---------- 6. 结构体作为函数参数 ----------
    printf("\n========== 结构体函数参数 ==========\n");

    printf("值传递：\n");
    print_student(s1);

    printf("\n指针传递（更高效，可修改原值）：\n");
    print_student_ptr(&s1);

    // 通过指针对结构体成员赋值
    set_student_score(&s1, 99.0f);
    printf("修改分数后：%s 的分数 = %.1f\n", s1.name, s1.score);


    // ---------- 7. 联合体 ----------
    printf("\n========== 联合体 ==========\n");

    DataUnion data;
    printf("DataUnion 大小 = %zu 字节\n", sizeof(DataUnion));

    data.i = 100;
    printf("存 int 后：data.i = %d\n", data.i);

    data.f = 3.14f;
    printf("存 float 后：data.f = %f\n", data.f);
    printf("  此时 data.i = %d（值已被覆盖）\n", data.i);

    data.c = 'A';
    printf("存 char 后：data.c = %c\n", data.c);

    // 联合体的应用：判断系统字节序
    printf("\n判断字节序：\n");
    union {
        int num;
        char bytes[4];
    } endian_test;

    endian_test.num = 0x12345678;
    if (endian_test.bytes[0] == 0x78) {
        printf("  小端序（Little Endian）：低字节存低地址\n");
    } else {
        printf("  大端序（Big Endian）：高字节存低地址\n");
    }


    // ---------- 8. 枚举 ----------
    printf("\n========== 枚举 ==========\n");

    Color my_color = GREEN;
    printf("my_color = %d\n", my_color);

    Weekday today = FRIDAY;
    printf("今天是星期 %d\n", today);

    switch (today) {
        case MONDAY:
        case TUESDAY:
        case WEDNESDAY:
        case THURSDAY:
        case FRIDAY:
            printf("工作日\n");
            break;
        case SATURDAY:
        case SUNDAY:
            printf("周末\n");
            break;
    }


    // ---------- 9. 结构体与动态内存 ----------
    printf("\n========== 结构体动态内存 ==========\n");

    // 动态分配一个结构体
    struct Student *dyn_s = (struct Student *)malloc(sizeof(struct Student));
    if (dyn_s != NULL) {
        strcpy(dyn_s->name, "动态学生");
        dyn_s->age = 25;
        dyn_s->score = 88.5f;
        dyn_s->id = 9999;

        printf("动态分配的学生：%s，学号 %d\n", dyn_s->name, dyn_s->id);

        free(dyn_s);  // 释放内存
        dyn_s = NULL; // 避免野指针
    }

    // 动态分配结构体数组
    int n = 3;
    struct Student *students = (struct Student *)malloc(n * sizeof(struct Student));
    if (students != NULL) {
        for (int i = 0; i < n; i++) {
            sprintf(students[i].name, "学生%d", i + 1);
            students[i].age = 18 + i;
            students[i].score = 80.0f + i * 5;
            students[i].id = 3001 + i;
        }

        printf("动态学生数组：\n");
        for (int i = 0; i < n; i++) {
            printf("  %s - %.1f 分\n", students[i].name, students[i].score);
        }

        free(students);
        students = NULL;
    }


    // ---------- 安全小贴士 ----------
    printf("\n========== 安全小贴士 ==========\n");
    printf("1. 结构体存在内存对齐，实际大小可能大于成员大小之和\n");
    printf("2. 联合体所有成员共享内存，修改一个会影响其他\n");
    printf("3. 结构体指针使用前检查 NULL\n");
    printf("4. 动态分配的结构体要记得 free，避免内存泄漏\n");
    printf("5. 字节序在网络编程和逆向分析中非常重要\n");

    return 0;
}


// 值传递结构体（会复制整个结构体，效率低）
void print_student(struct Student s) {
    printf("  姓名：%s，年龄：%d，分数：%.1f\n", s.name, s.age, s.score);
}

// 指针传递结构体（高效，只传地址）
void print_student_ptr(struct Student *s) {
    printf("  姓名：%s，年龄：%d，分数：%.1f\n", s->name, s->age, s->score);
}

// 通过指针对结构体成员赋值
void set_student_score(struct Student *s, float score) {
    if (s != NULL) {
        s->score = score;
    }
}
