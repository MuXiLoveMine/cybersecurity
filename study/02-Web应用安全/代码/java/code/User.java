// User.java
// 类与对象示例

// 父类：Person
class Person {
    // 成员变量（属性）
    private String name;
    private int age;

    // 无参构造方法
    public Person() {
    }

    // 有参构造方法
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // 成员方法
    public void greet() {
        System.out.println("你好，我是" + name);
    }

    public void introduce() {
        System.out.println("我叫" + name + "，今年" + age + "岁");
    }

    // Getter 和 Setter
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }
}

// 子类：Student，继承自 Person
class Student extends Person {
    private String school;
    private String studentId;

    public Student(String name, int age, String school, String studentId) {
        super(name, age);  // 调用父类构造方法
        this.school = school;
        this.studentId = studentId;
    }

    // 方法重写（Override）
    @Override
    public void greet() {
        System.out.println("你好，我是学生" + getName());
    }

    // 子类特有的方法
    public void study() {
        System.out.println(getName() + "正在" + school + "学习");
    }

    public String getSchool() {
        return school;
    }

    public String getStudentId() {
        return studentId;
    }
}

// 接口
interface Animal {
    void eat();
    void sleep();
}

// 实现接口
class Dog implements Animal {
    private String name;

    public Dog(String name) {
        this.name = name;
    }

    @Override
    public void eat() {
        System.out.println(name + "在吃骨头");
    }

    @Override
    public void sleep() {
        System.out.println(name + "在睡觉");
    }

    public void bark() {
        System.out.println(name + "汪汪叫");
    }
}

// 主类
public class User {
    public static void main(String[] args) {
        System.out.println("===== 1. 基本使用 =====");
        Person p = new Person("张三", 25);
        p.greet();
        p.introduce();

        // 使用 Setter 修改属性
        p.setAge(26);
        System.out.println("修改年龄后: " + p.getAge() + "岁");

        System.out.println("\n===== 2. 继承 =====");
        Student s = new Student("李四", 20, "清华大学", "2024001");
        s.greet();            // 重写后的方法
        s.introduce();        // 继承自父类的方法
        s.study();            // 子类特有的方法
        System.out.println("学号: " + s.getStudentId());

        // 多态：父类引用指向子类对象
        Person p2 = new Student("王五", 22, "北京大学", "2023001");
        p2.greet();           // 调用的是子类的 greet 方法（多态）

        System.out.println("\n===== 3. 接口 =====");
        Animal dog = new Dog("旺财");
        dog.eat();
        dog.sleep();

        // 向下转型，调用子类特有方法
        if (dog instanceof Dog) {
            ((Dog) dog).bark();
        }

        System.out.println("\n===== 4. 集合 =====");

        // ArrayList
        java.util.List<String> list = new java.util.ArrayList<>();
        list.add("苹果");
        list.add("香蕉");
        list.add("樱桃");
        System.out.println("列表大小: " + list.size());
        System.out.println("第一个元素: " + list.get(0));
        System.out.println("包含香蕉? " + list.contains("香蕉"));

        System.out.print("遍历列表: ");
        for (String fruit : list) {
            System.out.print(fruit + " ");
        }
        System.out.println();

        // HashMap
        java.util.Map<String, Integer> map = new java.util.HashMap<>();
        map.put("张三", 25);
        map.put("李四", 30);
        map.put("王五", 28);
        System.out.println("\nMap 大小: " + map.size());
        System.out.println("张三的年龄: " + map.get("张三"));

        System.out.println("遍历 Map:");
        for (java.util.Map.Entry<String, Integer> entry : map.entrySet()) {
            System.out.println("  " + entry.getKey() + ": " + entry.getValue() + "岁");
        }
    }
}
