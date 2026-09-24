# qsort

> **分类**：算法
> **说明**：快速排序，对数组进行排序
> **头文件**：`<stdlib.h>`

---

## 语法

```c
void qsort(void *base, size_t nitems, size_t size, int (*compar)(const void *, const void *));
```

## 示例代码

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 比较函数：升序
int compare_int(const void *a, const void *b) {
    return (*(int *)a - *(int *)b);
}

// 比较函数：降序
int compare_int_desc(const void *a, const void *b) {
    return (*(int *)b - *(int *)a);
}

// 字符串比较
int compare_string(const void *a, const void *b) {
    return strcmp(*(const char **)a, *(const char **)b);
}

// 结构体比较
typedef struct {
    char name[50];
    int score;
} Student;

int compare_student(const void *a, const void *b) {
    const Student *sa = (const Student *)a;
    const Student *sb = (const Student *)b;
    return sb->score - sa->score;  // 按分数降序
}

int main() {
    // 整数排序
    int nums[] = {5, 2, 8, 1, 9, 3, 7, 4, 6};
    int n = sizeof(nums) / sizeof(nums[0]);

    qsort(nums, n, sizeof(int), compare_int);

    printf("升序: ");
    for (int i = 0; i < n; i++) printf("%d ", nums[i]);
    printf("\n");

    qsort(nums, n, sizeof(int), compare_int_desc);
    printf("降序: ");
    for (int i = 0; i < n; i++) printf("%d ", nums[i]);
    printf("\n");

    // 字符串排序
    char *fruits[] = {"banana", "apple", "cherry", "date"};
    int m = sizeof(fruits) / sizeof(fruits[0]);
    qsort(fruits, m, sizeof(char *), compare_string);

    printf("水果: ");
    for (int i = 0; i < m; i++) printf("%s ", fruits[i]);
    printf("\n");

    // 结构体排序
    Student students[] = {
        {"Alice", 85},
        {"Bob", 92},
        {"Charlie", 78}
    };
    int s = sizeof(students) / sizeof(students[0]);
    qsort(students, s, sizeof(Student), compare_student);

    printf("排名:\n");
    for (int i = 0; i < s; i++) {
        printf("  %d. %s (%d分)\n", i+1, students[i].name, students[i].score);
    }

    return 0;
}
```
