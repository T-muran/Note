---
date: 2025-01-21T17:50:35
publish: true
comments: true
permalink: Blending
name: 混合
---

# 混合

## 透明度

OpenGL中，混合(Blending)通常是实现物体透明度(Transparency)的一种技术。透明就是说一个物体（或者其中的一部分）不是纯色(Solid Color)的，它的颜色是物体本身的颜色和它背后其它物体的颜色的不同强度结合。一个有色玻璃窗是一个透明的物体，玻璃有它自己的颜色，但它最终的颜色还包含了玻璃之后所有物体的颜色。这也是混合这一名字的出处，我们混合(Blend)（不同物体的）多种颜色为一种颜色。所以透明度能让我们看穿物体。

透明的物体可以是完全透明的（让所有的颜色穿过），或者是半透明的（它让颜色通过，同时也会显示自身的颜色）。一个物体的透明度是通过它颜色的alpha值来决定的。Alpha颜色值是颜色向量的第四个分量，你可能已经看到过它很多遍了。在这个教程之前我们都将这个第四个分量设置为1.0，让这个物体的透明度为0.0，而当alpha值为0.0时物体将会是完全透明的。当alpha值为0.5时，物体的颜色有50%是来自物体自身的颜色，50%来自背后物体的颜色。

!!! tip "透明度"
    我们目前一直使用的纹理有三个颜色分量：红、绿、蓝。但一些材质会有一个内嵌的alpha通道，对每个纹素(Texel)都包含了一个alpha值。这个alpha值精确地告诉我们纹理各个部分的透明度。比如说，下面这个窗户纹理中的玻璃部分的alpha值为0.25（它在一般情况下是完全的红色，但由于它有75%的透明度，能让很大一部分的网站背景颜色穿过，让它看起来不那么红了），角落的alpha值是0.0。

    ![[blending1.png|透明纹理]]

## 丢弃片段

!!! note ""

    有些图片并不需要半透明，只需要根据纹理颜色值，显示一部分，或者不显示一部分，没有中间情况。比如说草，如果想不太费劲地创建草这种东西，你需要将一个草的纹理贴在一个2D四边形(Quad)上，然后将这个四边形放到场景中。然而，草的形状和2D四边形的形状并不完全相同，所以你只想显示草纹理的某些部分，而忽略剩下的部分。

要想加载有alpha值的纹理，我们并不需要改很多东西，stb_image在纹理有alpha通道的时候会自动加载，但我们仍要在纹理生成过程中告诉OpenGL，我们的纹理现在使用alpha通道了：

```c++
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data);
```

同样，保证你在片段着色器中获取了纹理的全部4个颜色分量，而不仅仅是RGB分量：

```c++
void main()
{
    // FragColor = vec4(vec3(texture(texture1, TexCoords)), 1.0);
    FragColor = texture(texture1, TexCoords);
}
```
但是因为OpenGL默认是不知道怎么处理alpha值的，更不知道什么时候应该丢弃片段。我们需要自己手动来弄。幸运的是，有了着色器，这还是非常容易的。

GLSL给了我们discard命令，一旦被调用，它就会保证片段不会被进一步处理，所以就不会进入颜色缓冲。有了这个指令，我们就能够在片段着色器中检测一个片段的alpha值是否低于某个阈值，如果是的话，则丢弃这个片段，就好像它不存在一样：

```glsl
#version 330 core
out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D texture1;

void main()
{             
    vec4 texColor = texture(texture1, TexCoords);
    if(texColor.a < 0.1)
        discard;
    FragColor = texColor;
}
```

这里，我们检测被采样的纹理颜色的alpha值是否低于0.1的阈值，如果是的话，则丢弃这个片段。

!!! tip "注意"

    当采样纹理的边缘的时候，OpenGL会对边缘的值和纹理下一个重复的值进行插值（因为我们将它的环绕方式设置为了GL_REPEAT。这通常是没问题的，但是由于我们使用了透明值，纹理图像的顶部将会与底部边缘的纯色值进行插值。这样的结果是一个半透明的有色边框，你可能会看见它环绕着你的纹理四边形。要想避免这个，每当你alpha纹理的时候，请将纹理的环绕方式设置为GL_CLAMP_TO_EDGE：
    
    ```c++
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    ```

## 混合

虽然直接丢弃片段很好，但它不能让我们渲染半透明的图像。我们要么渲染一个片段，要么完全丢弃它。要想渲染有多个透明度级别的图像，我们需要启用混合(Blending)。和OpenGL大多数的功能一样，我们可以启用GL_BLEND来启用混合：

```c++
glEnable(GL_BLEND);
```

启用了混合之后，我们需要告诉OpenGL它该如何混合。

OpenGL中的混合是通过下面这个方程来实现的：

$$
    \bar{C}_{\text {result }}=\bar{C}_{\text {source }} * F_{\text {source }}+\bar{C}_{\text {destination }} * F_{\text {destination }}
$$

* $\bar{C}_{\text {source }}$: 源颜色向量。这是源自纹理的颜色向量。
* $\bar{C}_{\text {destination }}$: 目标颜色向量。这是当前储存在颜色缓冲中的颜色向量
* $F_{\text {source }}$: 源因子值。指定了alpha值对源颜色的影响。
* $F_{\text {destination }}$: 目标因子值。指定了alpha值对目标颜色的影响。

片段着色器运行完成后，并且所有的测试都通过之后，这个混合方程(Blend Equation)才会应用到片段颜色输出与当前颜色缓冲中的值（当前片段之前储存的之前片段的颜色）上。源颜色和目标颜色将会由OpenGL自动设定，但源因子和目标因子的值可以由我们来决定。

我们先来看一个简单的例子：

![半透明纹理](/assets/images/CG/blending2.png)

我们有两个方形，我们希望将这个半透明的绿色方形绘制在红色方形之上。红色的方形将会是目标颜色（所以它应该先在颜色缓冲中），我们将要在这个红色方形之上绘制这个绿色方形。

问题来了：我们将因子值设置为什么？嘛，我们至少想让绿色方形乘以它的alpha值，所以我们想要将$F_{\text {src }}$设置为源颜色向量的alpha值，也就是0.6。接下来就应该清楚了，目标方形的贡献应该为剩下的alpha值。如果绿色方形对最终颜色贡献了60%，那么红色方块应该对最终颜色贡献了40%，即1.0 - 0.6。所以我们将$F_{\text {destination }}$设置为1减去源颜色向量的alpha值。这个方程变成了：

$$
    \bar{C}_{\text{result}} = \begin{pmatrix} 0.0 \\ 1.0 \\ 0.0 \\ 0.6 \end{pmatrix} \times 0.6 + \begin{pmatrix} 1.0 \\ 0.0 \\ 0.0 \\ 1.0 \end{pmatrix} \times (1 - 0.6)
$$

结果就是重叠方形的片段包含了一个60%绿色，40%红色。
最终的颜色将会被储存到颜色缓冲中，替代之前的颜色。

这样子很不错，但我们该如何让OpenGL使用这样的因子呢？正好有一个专门的函数，叫做glBlendFunc。

glBlendFunc(GLenum sfactor, GLenum dfactor)函数接受两个参数，来设置源和目标因子。OpenGL为我们定义了很多个选项，我们将在下面列出大部分最常用的选项。注意常数颜色向量$\bar{C}_{\text{constant}}$可以通过glBlendColor函数来另外设置。

| 选项                          | 值                                                      |
| ----------------------------- | ------------------------------------------------------- |
| `GL_ZERO`                     | 因子等于$0$                                              |
| `GL_ONE`                      | 因子等于$1$                                              |
| `GL_SRC_COLOR`                | 因子等于源颜色向量$\bar{C}_{\text{source}}$                  |
| `GL_ONE_MINUS_SRC_COLOR`      | 因子等于$1−\bar{C}_{\text{source}}$                        |
| `GL_DST_COLOR`                | 因子等于目标颜色向量$\bar{C}_{\text{destination}}$         |
| `GL_ONE_MINUS_DST_COLOR`      | 因子等于$1−\bar{C}_{\text{destination}}$                   |
| `GL_SRC_ALPHA`                | 因子等于$\bar{C}_{\text{source}}$ 的$alpha$分量                |
| `GL_ONE_MINUS_SRC_ALPHA`      | 因子等于$1−\bar{C}_{\text{source}}$ 的$alpha$分量           |
| `GL_DST_ALPHA`                | 因子等于$\bar{C}_{\text{destination}}$ 的$alpha$分量      |
| `GL_ONE_MINUS_DST_ALPHA`      | 因子等于$1−\bar{C}_{\text{destination}}$ 的$alpha$分量 |
| `GL_CONSTANT_COLOR`           | 因子等于常数颜色向量$\bar{C}_{\text{constant}}$              |
| `GL_ONE_MINUS_CONSTANT_COLOR` | 因子等于$1−\bar{C}_{\text{constant}}$                       |
| `GL_CONSTANT_ALPHA`           | 因子等于$\bar{C}_{\text{constant}}$的$alpha$分量            |
| `GL_ONE_MINUS_CONSTANT_ALPHA` | 因子等于$1−\bar{C}_{\text{constant}}$的$alpha$分量       |

为了获得之前两个方形的混合结果，我们需要使用源颜色向量的$alpha$
作为源因子，使用$1−alpha$
作为目标因子。这将会产生以下的glBlendFunc：

```c++
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
```

也可以使用glBlendFuncSeparate为RGB和$alpha$通道分别设置不同的选项：

```c++
glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ZERO);
```

这个函数和我们之前设置的那样设置了RGB分量，但这样只能让最终的$alpha$分量被源颜色向量的$alpha$值所影响到。

OpenGL甚至给了我们更多的灵活性，允许我们改变方程中源和目标部分的运算符。当前源和目标是相加的，但如果愿意的话，我们也可以让它们相减。glBlendEquation(GLenum mode)允许我们设置运算符，它提供了三个选项：

* GL_FUNC_ADD：默认选项，将两个分量相加：$\bar{C}_{\text{result}}=Src+Dst$

* GL_FUNC_SUBTRACT：将两个分量相减： $\bar{C}_{\text{result}}=Src-Dst$

* GL_FUNC_REVERSE_SUBTRACT：将两个分量相减，但顺序相反：$\bar{C}_{\text{result}}=Dst-Src$

通常我们都可以省略调用glBlendEquation，因为GL_FUNC_ADD对大部分的操作来说都是我们希望的混合方程，但如果你真的想打破主流，其它的方程也可能符合你的要求。

## 渲染半透明纹理

首先，在初始化时我们启用混合，并设定相应的混合函数：

```c++
glEnable(GL_BLEND);
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
```

由于启用了混合，我们就不需要丢弃片段了，所以我们把片段着色器还原：

```glsl
#version 330 core
out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D texture1;

void main()
{             
    FragColor = texture(texture1, TexCoords);
}
```
现在（每当OpenGL渲染了一个片段时）它都会将当前片段的颜色和当前颜色缓冲中的片段颜色根据alpha值来进行混合。

但是深度测试和混合一起使用的话会产生一些麻烦。当写入深度缓冲时，深度缓冲不会检查片段是否是透明的，所以透明的部分会和其它值一样写入到深度缓冲中。结果就是物体不论透明度都会进行深度测试。即使透明的部分应该显示背后的物品，深度测试仍然丢弃了它们。

所以我们不能随意地决定如何渲染，让深度缓冲解决所有的问题了。这也是混合变得有些麻烦的部分。要想保证能够显示它们背后的物体，我们需要首先绘制背后的物体。这也就是说在绘制的时候，我们必须先手动将物体按照最远到最近来排序，再按照顺序渲染。

!!! warning "不要打乱绘制顺序"

    要想让混合在多个物体上工作，我们需要最先绘制最远的物体，最后绘制最近的物体。普通不需要混合的物体仍然可以使用深度缓冲正常绘制，所以它们不需要排序。但我们仍要保证它们在绘制（排序的）透明物体之前已经绘制完毕了。当绘制一个有不透明和透明物体的场景的时候，大体的原则如下：

    1. 先绘制所有不透明的物体。
    2. 对所有透明的物体排序。
    3. 按顺序绘制所有透明的物体。

    排序透明物体的一种方法是，从观察者视角获取物体的距离。这可以通过计算摄像机位置向量和物体的位置向量之间的距离所获得。接下来我们把距离和它对应的位置向量存储到一个STL库的map数据结构中。map会自动根据键值(Key)对它的值排序，所以只要我们添加了所有的位置，并以它的距离作为键，它们就会自动根据距离值排序了。

在场景中排序物体是一个很困难的技术，很大程度上由你场景的类型所决定，更别说它额外需要消耗的处理能力了。完整渲染一个包含不透明和透明物体的场景并不是那么容易。更高级的技术还有次序无关透明度(Order Independent Transparency, OIT)
