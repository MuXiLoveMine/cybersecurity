# try_catch_java

> **分类**：异常处理
> **说明**：Java 异常处理机制

---

## 语法

```java
try { ... } catch (ExceptionType e) { ... } finally { ... }
```

## 异常分类

Error: 系统级错误\nException: 程序级异常\n  RuntimeException: 运行时异常（非受检）\n  其他Exception: 受检异常

## 关键字

try / catch / finally / throw / throws

## 示例代码

```java
// 基本 try/catch
try {
    int result = 10 / 0;
} catch (ArithmeticException e) {
    System.out.println("除以零: " + e.getMessage());
    e.printStackTrace();
}

// 多个 catch
try {
    String str = null;
    str.length();
} catch (NullPointerException e) {
    System.out.println("空指针异常");
} catch (Exception e) {
    System.out.println("其他异常");
}

// finally 子句（总是执行）
FileInputStream fis = null;
try {
    fis = new FileInputStream("file.txt");
    // 读取文件
} catch (IOException e) {
    e.printStackTrace();
} finally {
    try {
        if (fis != null) fis.close();
    } catch (IOException e) {
        e.printStackTrace();
    }
}

// try-with-resources (Java 7+)，自动关闭资源
try (FileInputStream fis = new FileInputStream("file.txt")) {
    // 读取文件
} catch (IOException e) {
    e.printStackTrace();
}

// 抛出异常
public void validateAge(int age) throws IllegalArgumentException {
    if (age < 0) {
        throw new IllegalArgumentException("年龄不能为负");
    }
}

// 自定义异常
class MyException extends Exception {
    public MyException(String message) {
        super(message);
    }
}

// throws 声明（受检异常必须声明或捕获）
public void readFile(String path) throws IOException {
    FileInputStream fis = new FileInputStream(path);
    // ...
}

// 捕获多个异常类型 (Java 7+)
try {
    // ...
} catch (IOException | SQLException e) {
    e.printStackTrace();
}

// 运行时异常 vs 受检异常
// RuntimeException: 不需要声明，如 NullPointerException, ArrayIndexOutOfBoundsException
// 受检异常: 必须声明或捕获，如 IOException, SQLException
```
