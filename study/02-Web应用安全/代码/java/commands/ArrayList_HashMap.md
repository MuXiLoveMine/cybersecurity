# ArrayList_HashMap

> **分类**：集合框架
> **说明**：Java 常用集合类

---

## 语法

```java
ArrayList<E> list = new ArrayList<>();\nHashMap<K,V> map = new HashMap<>();
```

## 常用集合

ArrayList / LinkedList / HashSet / HashMap / TreeMap / ArrayDeque

## 接口

Collection / List / Set / Map / Queue

## 示例代码

```java
import java.util.*;

// ===== ArrayList =====
ArrayList<String> list = new ArrayList<>();

// 添加
list.add("apple");
list.add("banana");
list.add("cherry");
list.add(1, "orange");  // 在指定位置插入

// 访问
String first = list.get(0);
int size = list.size();

// 修改
list.set(0, "grape");

// 删除
list.remove(0);          // 按索引删除
list.remove("banana");   // 按值删除

// 判断
boolean has = list.contains("apple");
boolean empty = list.isEmpty();

// 遍历
for (String item : list) {
    System.out.println(item);
}

// 排序
Collections.sort(list);

// 转数组
String[] arr = list.toArray(new String[0]);

// ===== HashMap =====
HashMap<String, Integer> map = new HashMap<>();

// 添加
map.put("apple", 10);
map.put("banana", 20);
map.put("cherry", 30);

// 获取
int count = map.get("apple");     // 10
int val = map.getOrDefault("orange", 0);  // 不存在返回默认值

// 删除
map.remove("apple");

// 判断
map.containsKey("banana");  // true
map.containsValue(20);      // true

// 遍历键
for (String key : map.keySet()) {
    System.out.println(key + ": " + map.get(key));
}

// 遍历值
for (Integer value : map.values()) {
    System.out.println(value);
}

// 遍历键值对
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + " -> " + entry.getValue());
}

// ===== HashSet =====
HashSet<String> set = new HashSet<>();
set.add("a");
set.add("b");
set.add("a");  // 重复，不会添加
System.out.println(set.size());  // 2

// ===== 常用工具方法 =====
Collections.max(list);
Collections.min(list);
Collections.reverse(list);
Collections.shuffle(list);
Collections.binarySearch(sortedList, "banana");
```
