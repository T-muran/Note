---
date: 2025-03-01T00:00:00
publish: true
comments: true
permalink: Introduction
name: 设计模式1111
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

## 设计模式SOLID原则

### 开闭原则（Open Close Principle || OCP）

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

接下来，我们需要一种基于 `Specification<T>` 的过滤方法：你猜到的，这是通过定义完成，一个 `Filter<T>`：

   ```cpp
   template <typename T> struct Filter
   {
      virtual vector<T*> filter(
      vector<T*> items,
      Specification<T>& spec) = 0;
   };
   ```

同样的，我们所做的就是为一个名为 filter 的函数指定签名，该函数接受所有项目和一个规范，并返回符合规范的所有项目。假设这些项目被存储为 vector<T*>，但实际上，你可以向 filter() 传递一对迭代器，或者是一些专门为遍历集合而设计的定制接口。遗憾的是，C++ 语言未能标准化枚举或集合的概念，这是存在于其它编程语言（例如，.NET 的 IEnumerable）中的东西。

基于前述，改进的过滤器的实现非常的简单：

   ```cpp
   struct BetterFilter : Filter<Product>
   {
      vector<Product*> filter(
         vector<Product*> items,
         Specification<Product>& spec) override
      {
         vector<Product*> result;
         for (auto& p : items)
            if (spec.is_satisfied(p))
               result.push_back(p);
         return result;
      }
   };
   ```

可以看到 `Specification<T>`，该规范被传入作为 std::function 的强类型化等效项，该函数仅约束到一定数量的可能的筛选规格。

现在，我们可以定义规范，制作一个颜色过滤器，例如：

   ```cpp
   struct ColorSpecification : Specification<Product>
   {
      Color color;
      explicit ColorSpecification(const Color color)
         : color{color}
      {
      }
      bool is_satisfied(Product* item) override
      {
         return item->color == color;
      }
   };
   ```

为了添加一个按尺寸过滤的功能，我们需要一个复合规范:

   ```cpp
   template <typename T> struct AndSpecification :
   Specification<T>
   {
   Specification<T>& first;
   Specification<T>& second;

   AndSpecification(Specification<T>& first,Specification<T>& second)
   : first{first}, second{second} {}

   bool is_satisfied(T* item) override
   {
   return first.is_satisfied(item) && second.is_satisfied(item);
   }
   };
   ```

这里有很多代码！但是请记住，由于 C++ 的强大功能，你可以简单地引入一个 operator && 用于两个 `Specification<T>` 对象，从而使得过滤过程由两个（或更多！）标准，极为简单：

   ```cpp
   template <typename T> struct Specification
   {
      virtual bool is_satisfied(T* item) = 0;
      
      AndSpecification<T> operator &&(Specification&& other)
      {
         return AndSpecification<T>(*this, other);
      }
   };
   ```

如果你现在避免为尺寸/颜色规范设置额外的变量，则可以将复合规范简化为一行：

   ```cpp
   auto green_and_big =ColorSpecification(Color::Green)&& SizeSpecification(Size::Large);
   ```

因此，让我们回顾以下 OCP 原则是声明，以及前面的示例是如何执行它的。基本上，OCP 声明你不需要返回你已经编写和测试过的代码，并对其进行更改。这正是这里发生的！我们制定了 `Specification<T>` 和 `Filter<T>`，从那时起，我们所要做的就是实现任何一个接口（不需要修改接口本身）来实现新的过滤机制。这就是“开放供扩展，封闭供修改”的意思。

### 单一职责原则（Single Responsibility Principle || SRP）

!!! note "主要思想"

    单一职责原则表示一个模块的组成元素之间的功能相关性。从软件变化的角度来看，就一个类而言，应该仅有一个让它变化的原因；通俗地说，即一个类只负责一项职责。

假设您决定把您最私密的想法记在日记里。日记具有一个标题和多个条目。您可以按如下方式对其进行建模：

   ```cpp
   struct Journal
   {
      string title;
      vector<string> entries;
      
      explicit Journal(const string& title) : title{title} {}
   };
   ```

现在，您可以添加用于将添加到日志中的功能，并以日记中的条目序号为前缀。这很容易：

   ```cpp
   void Journal::add(const string& entry)
   {
      static int count = 1;
      entries.push_back(boost::lexical_cast<string>(count++)
         + ": " + entry);
   }
   ```

因为添加一条日记条目是日记实际上需要做的事情，所以将此函数作为 Journal 类的一部分是有意义的。这是日记的责任来保持条目，所以，与这相关的任何事情都是公平的游戏。

现在，假设您决定通过将日记保存在文件中而保留该日记。您需要将此代码添加到 Journal 类：

```cpp
void Journal::save(const string& filename)
{
    ofstream ofs(filename);
    for (auto& s : entries)
        ofs << s << endl;
}
```

这种方法是有问题的。日志的责任是保存日志条目，而不是把它们写道磁盘上。如果您将磁盘写入功能添加到 Journal 和类似类中，持久化方法中的任何更改（例如，您决定向云写入而不是磁盘），都将在每个受影响的类中需要进行大量的微小的更改。

!!! warning "注意"

    在一个架构中，不得不在大量的类中做很多微小的更改，无论是否相关，通常都是一种代码气味(code smell)，这意味着这个设计可能不够好。

因此，持久化是一个单独的问题，最好在一个单独的类别中表达，例如：

   ```cpp
   struct PersistenceManager
   {
      static void save(const Journal& j, const string& filename)
      {
         ofstream ofs(filename);
         for (auto& s: j.entries)
               ofs << s << endl;
      }
   };
   ```

这正是单一责任（Single Responsibility）的含义：每个类只有一个责任，因此，只有一个改变的理由。只有在需要对条目的存储做更多工作的情况下，Journal 才需要更改。例如，你可能希望每个条目都以时间戳为前缀，因此，你将更改 add() 函数来实现这一点。从另一方面来说，如果你要更改持久化机制，这将在 PersistenceManager 中进行更改。

### 里氏替换原则（Liskov Substitution Principle || LSP）

!!! note "主要思想"

    子类对象能够替换程序中任何地方出现的父类对象，并且保证原来程序的逻辑行为不变(正确性不被破坏),即所有引用基类的地方必须能透明地使用其子类的对象。

里氏替换原则指出，如果一个接口可以接受类型为 Parent 的对象，那么它应该同样地可以接受类型为 Child 的对象，而不会有任何破坏。让我们来看看 LSP 被破坏的情况。

下面是一个矩形；它有宽度（width）和高度（height），以及一组计算面积的 getters 和 setters：

   ```cpp
   class Rectangle
   {
   protected:
      int width, height;
   public:
      Rectangle(const int width, const int height)
         : width{width}, height{height} { }
      
      int get_width() const { return width; }
      virtual void set_width(const int width) { this->width = width; }
      int get_height() const { return height; }
      virtual void set_height(const int height) { this->height = height; }
      
      int area() const { return width * height; }
   };
   ```

现在，假设我们有一种特殊的矩形，称为正方形。此对象将重写 setters，以设置宽度和高度：

   ```cpp
   class Square : public Rectangle
   {
   public:
      Square(int size) : Rectangle(size, size) {}
      void set_width(const int width) override {
         this->width = height = width;
      }
      void set_height(const int height) override {
         this->height = width = height;
      }
   };
   ```

这种做法是邪恶的。你还看不到它，因为它确实是无辜的：setters 简单地设置了两个维度，可能会发生什么错误呢？好吧，如果我们采用前面的方法，我们可以很容易地构建一个函数，该函数以 Rectangle 类型变量为参数，当传入 Square 类型变量时，它会爆炸：

   ```cpp
   void process(Rectangle& r)
   {
      int w = r.get_width();
      r.set_height(10);
      
      cout << "expected area = " << (w * 10)
         << ", got " << r.area() << endl;
   }
   ```

前面的函数以公式 Area = Width * Height 作为不变量。它得到宽度，设置高度，并正确地期望乘积等于计算的面积。但是使用 Square 调用前面的函数会产生不匹配：

   ```cpp
   Square s{5};
   process(s); // 期望 area = 50, 实际获得 100
   ```

这个例子中，process() 完全不能接受派生类型 Square 而不是基类型 Rectangle，从而破坏了 LSP 原则。如果你给它一个 Rectangle，一切都很好，所以它可能需要一些时间才能出现在你的测试（或者生产，希望不是！）。

解决办法是什么呢？嗯，有很多。就我个人而言，我认为类型 Square 甚至不应该存在：相反，我们可以创建一个工厂来创建矩形和正方形：

   ```cpp
   struct RectangleFactory
   {
      static Rectangle create_rectangle(int w, int h);
      static Rectangle create_square(int size);
   };
   ```

### 依赖倒置原则（Dependency Inversion Principle || DIP）

!!! note "主要思想"

    依赖倒置原则是指高层模块不应该依赖于底层模块，二者都应该依赖于抽象；抽象不应该依赖于细节，细节应该依赖于抽象。

例如，如果你对日志记录感兴趣，你的报告组件不应该依赖于具体的 ConsoleLogger，而是可以依赖于 ILogger 接口。在这种情况下，我们认为报告组件是高级别的（更接近业务领域），而日志记录则是一个基本的关注点（类似于文件 I/O 或线程，但不是），被认为是一个低级别的模块。

其次接口或基类上的依赖比依赖于具体的类型更好。希望这个语句的真实性是显而易见的，因为这种方法支持更好的可配置性和可测试性——前提是你使用了一个良好的框架来处理这些依赖关系。

所以，现在的主要问题是：你是如何真正实现上述所有的？这确实需要更多的工作，因为现在你需要明确说明，例如，Reporting 依赖于 ILogger。如下所示：

   ```cpp
   class Reporting
   {
      ILogger& logger;
   public:
      Reporting(const ILogger& logger) : logger{logger} {}
      void prepare_report()
      {
         logger.log_info("Preparing the report");
         ...
      }
   };
   ```

要初始化前面的类，你需要显式地调用 `Reporting{ConsoleLogger{}}` 或类似地东西。如果 Reporting 依赖于五个不同的接口呢？如果 ConsoleLogger 有自己的依赖项，又怎么办？你可以通过编写大量的代码来管理这个问题，但是这里有一个更好的方法。

针对前面的现代、流行、时尚的做法是使用依赖注入（Dependency Injection）：这基本上意味着你要使用诸如 Boost.DI之类的库自动满足特定组件的依赖关系的要求。

### 接口隔离原则（Interface Segregation Principle || ISP）

!!! note "主要思想"

    接口隔离原则是指客户端不应该被迫依赖于它们不使用的接口。这意味着一个类应该有尽可能少的接口，而不是一个类应该有尽可能多的接口。

假设你决定定义一个多功能打印机：该设备可以打印、扫描和传真文档。因此，你可以定义如下：

   ```cpp
   struct MyFavouritePrinter /* : IMachine */
   {
      void print(vector<Document*> docs) override;
      void fax(vector<Document*> docs) override;
      void scan(vector<Document*> docs) override;
   };
   ```

这很好。现在，假设你决定定义一个需要由所有计划制造多功能打印机的人实现的接口。因此，你可以在你最喜欢的 IDE 中使用提取接口函数功能，你可以得到如下内容：

   ```cpp
   struct IMachine
   {
      virtual void print(vector<Document*> docs) = 0;
      virtual void fax(vector<Document*> docs) = 0;
      virtual void scan(vector<Document*> docs) = 0;
   };
   ```

这里有一个问题。原因是这个接口的一些实现者可能不需要扫描或传真，只需要打印。然而，你强迫他们实现这些额外的功能：当然，它们可以都是无操作的，但为什么要这么做呢？

因此，ISP 的建议是将接口分开，以便于实现者可以根据他们的需求进行挑选和选择。由于打印和扫描是不同的操作（例如，扫描仪不能打印），我们为这些操作定义了不同的接口：

   ```cpp
   struct IPrinter
   {
      virtual void print(vector<Document*> docs) = 0;
   };

   struct IScanner
   {
      virtual void scan(vector<Document*> docs) = 0;
   };
   ```

现在，如果我们真的想要一个 IMachine 接口，我们可以将它定义为上述接口的组合：

   ```cpp
   struct IMachine : IPrinter, IScanner /* IFax and so on */
   {  
   };
   ```

当你在具体的多功能设备中实现这个接口时，这就是要使用的接口。例如，你可以使用简单的委托来确保 Machine 重用特定 IPrinter 和 IScanner 提供的功能：

   ```cpp
   struct Machine : IMachine
   {
      IPrinter& printer;
      IScanner& scanner;
      
      Machine(IPrinter& printer, IScanner& scanner)
         : printer{printer},
         scanner{scanner}
      {
      }
      
      void print(vector<Document*> docs) override
      {
         printer.print(docs);
      }
      
      void scan(vector<Document*> docs) override
      {
         scanner.scan(docs);
      }
   };
   ```

因此，简单地说，这里的想法是将复杂接口的部分分隔成单独的接口，以避免迫使实现者实现他们并不真正需要的功能。当为某些复杂的应用程序编写插件时，如果你得到一个具有 20 个令人困惑的函数的接口，用于实现各种 no-ops 和 return nullptr 时，说不定是 API 作者违反了 ISP 原则。
