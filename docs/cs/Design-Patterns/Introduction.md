---
comments: true
---

# 设计模式

## 一些C++的概念

### 奇异递归模板模式（CRTP）

   这个想法很简单：继承者将自己作为模板参数传递给它的基类：

   ``` cpp
   struct Foo : SomeBase<Foo>
   {
    ...
   }
   ```

   这么做的原因之一是，以便于能够访问基类实现中的类型化 this 指针。

### 混合继承

   在 C++ 中，类可以定义为继承自它自己的模板参数，例如：

   ```cpp
   template <typename T> struct Mixin : T
   {
    ...
   }
   ```

   这种方法被称为混合继承（mixin inheritance），并允许类型的分层组合。例如，您可以允许 `Foo<Bar<Baz>> x`; 声明一个实现所有三个类的特征的类型的变量，而不必实际构造一个全新的 FooBarBaz 类型。

### 属性

   一个属性（property，通常是私有的）仅仅是字段以及 getter 和 setter 的组合。在标准 C++ 中，一个属性如下所示：

   ```cpp
   class Person
   {
      int age;
   public:
      int get_age() const { return age; }
      void set_age(int value) { age = value; }
   };
   ```

   大量的编程语言（例如，C#）通过直接将其添加到编程语言中，将属性的概念内化。虽然 C++ 没有这样做（而且将来也不太可能这样做），但是有一个名为 property 的非标准声明说明符，可以在大多数编译器（MSVC、Clang、Intel）中使用：

   ```cpp
   class Person
   {
      int age_;
   public:
      int get_age() const { return age_; }
      void set_age(int value) { age_ = value; }
      __declspec(property(get=get_age, put=set_age)) int age;
   };
   ```

   这可以按如下所示使用：

   ```cpp
   Person person;
   p.age = 20;
   ```

## 设计模式六大原则

1. 开闭原则（Open Close Principle || OCP）

!!! note "主要思想"

    开闭原则的意思是：对扩展开放，对修改关闭。

    在程序需要进行拓展的时候，不能去修改原有的代码，实现一个热插拔的效果。简言之，是为了使程序的扩展性好，易于维护和升级。想要达到这样的效果，需要使用接口和抽象类。

    类模块应该是可扩展的，但是不可修改。

假设在数据库中，我们拥有一个（完全假设的）范围的产品。每种产品具有颜色和尺寸，并定义为：

   ```cpp
   enum class Color { Red, Green, Blue };
   enum class Size { Small, Medium, Large };

   struct Product
   {
       string name;
       Color color;
       Size size;
   };
   ```

 现在，我们需要过滤这些产品。我们可以创建一个过滤器，它接受一个产品集合并返回一个新的产品集合，如下所示：

   ```cpp
   struct ProductFilter
   {
      typedef vector<Product*> Items;
   };
   ```

现在，为了支持通过颜色过滤产品，我们定义了一个成员函数，以精确地执行以下操作：

   ```cpp
   ProductFilter::Items ProductFilter::by_color(Items items, Color color)
   {
       Items result;
       for (auto& i : items)
           if (i->color == color)
               result.push_back(i);
       return result;
   }
   ```

我们目前按颜色过滤项目的方法都很好，而且很好。我们的代码开始进入生产环节，但不幸的是，一段时间之后，老板进来并要求我们实现按尺寸大小进行过滤。因此，我们跳回 ProductFilter.cpp 添加以下代码并重新编译：

   ```cpp
   ProductFilter::Items ProductFilter::by_size(Items items, Size size)
   {
       Items result;
       for (auto& i : items)
           if (i->size == size)
               result.push_back(i);
       return result;
   }
   ```

这感觉像是彻底的复制，不是吗？为什么我们不直接编写一个接受谓词（一些函数）的通用方法呢？嗯，一个原因可能是不同形式的过滤可以以不同的方式进行：例如，某些记录类型可能被编入索引，需要以特定的方式进行搜索；某些数据类型可以在 GPU 上搜索，而其它数据类型则不适用。

我们的代码进入生成环节，但是，再次的，老板回来告诉我们，现在有一个需求需要按颜色和尺寸进行搜索。那么，我们要做什么呢，还是增加另一个函数？

从前面的场景中，我们想要的是实现“开放-关闭原则”（Open-Closed Principle），该原则声明类型是为了扩展而开放的，但为修改而关闭的。换句话说，我们希望过滤是可扩展的（可能在另一个编译单元中），而不必修改它（并且重新编译已经工作并可能已经发送给客户的内容）。

我们如何做到这一点？首先，我们从概念上（SRP!）将我们的过滤过程分为两部分：筛选器（接受所有项并且只返回某些项的过程）和规范（应用于数据元素的谓词的定义）。

我们可以对规范接口做一个非常简单地定义：

   ```cpp
   template <typename T> struct Specification
   {
       virtual bool is_satisfied(T* item) = 0;
   };
   ```

在前面的示例中，类型 T 是我们选择的任何类型：它当然可以是一个 Product，但也可以是其它东西。这使得整个方法可重复使用。

接下来，我们需要一种基于 Specification<T> 的过滤方法：你猜到的，这是通过定义完成，一个 Filter<T>：

   ```cpp
   template <typename T> struct Filter
   {
       virtual vector<T*> filter(
       	vector<T*> items,
       	Specification<T>& spec) = 0;
   };
   ```

同样的，我们所做的就是为一个名为 filter 的函数指定签名，该函数接受所有项目和一个规范，并返回符合规范的所有项目。假设这些项目被存储为 vector<T*>，但实际上，你可以向 filter() 传递，或者是一对迭代器，或者是一些专门为遍历集合而设计的定制接口。遗憾的是，C++ 语言未能标准化枚举或集合的概念，这是存在于其它编程语言（例如，.NET 的 IEnumerable）中的东西。