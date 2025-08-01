---
comments: true
---

# 极限与连续

## 常见导数公式

=== "初等函数求导"

    1. $(\sec x)^{\prime}=\sec x \tan x$
    2. $(\tan x)^{\prime}=\sec^{2} x$  
    3. $(\cot x)^{\prime}=-\csc^{2} x$
    4. $(\csc x)^{\prime}=-\csc x \cot x$
    5. $(a^{x})^{\prime}=a^{x}\ln_{}{a}$
    6. $(\log_{a}{x})^{\prime}=\frac{1}{x \ln_{}{a} }$
    7. $(\arcsin x)^{\prime}=\frac{1}{\sqrt{1-x^2} }$
    8. $(\arccos x)^{\prime}=-\frac{1}{\sqrt{1-x^2} }$
    9. $(\arctan x)^{\prime}=\frac{1}{1+x^2}$
    10. $(\operatorname{arccot}  x)^{\prime}=-\frac{1}{1+x^2}$
=== "反函数求导"
    若函数 $x=\varphi (y)$在某区间$I_y$内可导、单调且$\varphi ^{\prime} (y)\neq 0$，则其反函数 $y=\varphi ^{-1} (x)$在对应区间$I_x$内也可导，且有

    $$
        \left(\varphi ^{-1} (x)\right)^{\prime}=\frac{1}{\varphi ^{\prime} (y)}
    $$

## 等价无穷小

=== "一阶"
    1. $x\sim\sin x\sim\tan x\sim\arcsin x\sim\arctan x\sim\ln_{}{1+x}\sim e^x-1$
    2. $a^x-1\sim x\ln_{}{a}$
    3. $(1+x)^{\alpha}-1\sim \alpha x$
=== "二阶"
    1. $1-\cos x\sim \frac{1}{2}x^2$
    2. $x-\ln_{}{1+x}\sim\frac{1}{2}x^2$
=== "三阶"
    1. $x-\sin x\sim\frac{1}{6}x^3$
    2. $\arcsin x - x \sim\frac{1}{6}x^3$
    3. $x-\tan x\sim\frac{1}{3}x^3$
    4. $\arctan x - x \sim\frac{1}{3}x^3$

!!! warning "等价无穷小使用"
    * 乘除关系可以代换

        简而言之，在严格的乘除$(\lim\frac{f\cdot g}{h})$中，可以使用无穷小代换。

    * 加减关系在一定条件下可以代换

        若$\alpha \sim \alpha_1,\beta \sim \beta_1$，且$\lim \frac{\alpha_1}{\beta_1}=A\neq 1$,则$\alpha - \beta \sim \alpha_1 - \beta_1$

        本质是泰勒的简略写法，建议使用泰勒。

## 两个重要极限

1. $\lim\limits_{x \to 0} \frac{\sin x}{x}=1$
2. $\lim\limits_{x \to \infty} (1+\frac{1}{x})^x=e$

