---
title: Whole Numbers
node: [divisibility, division, parity, prime, square]
---

# Whole Numbers

The paper is about one question: which whole numbers can be written as a sum of two
squares? To follow it you need five ideas about whole numbers: when one number
*divides* another, *division with remainder*, *even and odd*, *primes*, and
*squares*. This chapter introduces each and works out the few facts the paper uses
about them.

Throughout, "number" means a whole number. The paper works with the natural numbers
$0, 1, 2, 3, \dots$; Wikipedia's definitions below are stated for all integers
(negative ones too), which changes nothing we need.

## Divisibility

::: {.definition #def-divides ledger=L001 lean=Dvd.dvd}
A number $n$ is **divisible** by a nonzero number $m$ if $n = km$ for some whole
number $k$. We then say $m$ *divides* $n$, and write $m \mid n$.
:::

::: {.quote ledger=L001}
:::

So $3 \mid 12$ because $12 = 4 \cdot 3$, but $3 \nmid 13$: no whole number $k$ has
$3k = 13$. Every number $n$ is divisible by $1$ and by itself, since $n = n \cdot 1 =
1 \cdot n$. Those divisors are called trivial:

::: {.quote ledger=C1-01}
:::

A number greater than $1$ that has a divisor other than these is *composite*
[@C1-02]. Composite numbers are exactly the ones that are not prime, as we will see
in a moment.

## Division with remainder

Most numbers don't divide each other exactly; what is left over is the *remainder*.

::: {.theorem #thm-division ledger=L002 lean=Book.Windmills.Ch01.division}
**Division with remainder.** Given whole numbers $a$ and $b$ with $b \neq 0$, there
are unique whole numbers $q$ (the *quotient*) and $r$ (the *remainder*) such that
$$a = bq + r \qquad\text{and}\qquad 0 \le r < b.$$
:::

::: {.quote ledger=L002}
:::

::: example
Dividing $17$ by $3$: the quotient is $5$ and the remainder is $2$, since
$17 = 3 \cdot 5 + 2$ and $2 < 3$. [@C1-03]
:::

::: proof
*Existence.* Among the numbers $a, a - b, a - 2b, \dots$ that are still $\ge 0$, take
the smallest; call it $r = a - qb$. Then $r \ge 0$, and $r < b$, because otherwise
$r - b$ would be a smaller one that is still $\ge 0$.

*Uniqueness.* If also $a = bq' + r'$ with $0 \le r' < b$, then $b(q - q') = r' - r$.
The right-hand side lies strictly between $-b$ and $b$, and the only multiple of $b$
there is $0$. So $r' = r$, and then $q' = q$.
:::

The remainder depends only on $a$ and $b$, so it deserves a name of its own. The
paper writes the quotient as $m \operatorname{div} n$ and the remainder as
$m \operatorname{mod} n$:

::: {.quote ledger=C1-05}
:::

For example, $17 \operatorname{div} 3 = 5$ and $17 \operatorname{mod} 3 = 2$. Notice
that $m \mid n$ exactly when $n \operatorname{mod} m = 0$: dividing leaves nothing
over.

## Even and odd

::: {.definition #def-parity ledger=C1-06 lean=Even,Odd}
A number is **even** if it has the form $2k$, and **odd** if it has the form $2k + 1$,
for some whole number $k$. Whether a number is even or odd is called its **parity**.
:::

::: {.quote ledger=C1-06}
:::

Equivalently, a number is even when $2$ divides it and odd when it does not
[@L003].

::: {.theorem #thm-even-odd ledger=C1-07 lean=Book.Windmills.Ch01.even_or_odd,Book.Windmills.Ch01.even_iff_mod}
Every number is either even or odd, and not both. A number $n$ is even exactly when
$n \operatorname{mod} 2 = 0$, and odd exactly when $n \operatorname{mod} 2 = 1$.
:::

::: proof
Divide $n$ by $2$: $n = 2q + r$ with $r \in \{0, 1\}$. If $r = 0$ then $n = 2q$ is even;
if $r = 1$ then $n = 2q + 1$ is odd. It can't be both, because the remainder is
unique.
:::

Parity behaves simply under addition: even $+$ even and odd $+$ odd are even, while
even $+$ odd is odd. (Write the numbers as $2a$ or $2a + 1$ and add.) The paper uses
parity constantly, both of numbers and, later, of the *sizes of sets*.

::: inpaper
The paper's notation section (§1.3) writes $\mathsf{even}\ n$ and
$\mathsf{odd}\ n$ for these two properties:

::: {.quote ledger=C1-08}
:::
:::

## Prime numbers

::: {.definition #def-prime ledger=L005 lean=Nat.Prime}
A **prime number** is a whole number greater than $1$ that is not a product of two
smaller whole numbers.
:::

::: {.quote ledger=L005}
:::

The *divisors* of $n$ are the numbers that divide it evenly [@C1-11], and a number
$p > 1$ is prime exactly when its only divisors are $1$ and $p$:

::: {.proposition ledger=C1-09 lean=Nat.Prime.eq_one_or_self_of_dvd}
The primes are exactly the numbers with exactly two positive divisors.
:::

::: example
$7$ is prime: none of $2, 3, 4, 5, 6$ divides it [@C1-10]. The primes below $30$ are
$2, 3, 5, 7, 11, 13, 17, 19, 23, 29$.
:::

Two facts about primes matter for the paper.

::: {.theorem #thm-only-even-prime ledger=C1-12 lean=Book.Windmills.Ch01.prime_even_eq_two}
The only even prime is $2$.
:::

::: proof
An even number $n$ has $2 \mid n$. If $n$ is prime, its only divisors are $1$ and $n$,
so $2 = n$.
:::

::: {.theorem #thm-odd-prime-mod-4 ledger=C1-13 lean=Book.Windmills.Ch01.odd_prime_mod_four}
An odd prime leaves a remainder of $1$ or $3$ when divided by $4$.
:::

::: proof
Divide the prime $p$ by $4$: $p = 4q + r$ with $r \in \{0, 1, 2, 3\}$. If $r$ were $0$ or
$2$, then $p = 2(2q)$ or $p = 2(2q + 1)$ would be even. Since $p$ is odd, $r$ is $1$ or $3$.
:::

So the odd primes fall into two families: those of the form $4k + 1$
($5, 13, 17, 29, \dots$) and those of the form $4k + 3$ ($3, 7, 11, 19, 23, \dots$). The
paper's theorem is about the first family.

::: inpaper
§2 opens with exactly these two facts: the only even prime, $2 = 1^2 + 1^2$, is a sum
of two squares, and the odd primes split by their remainder on division by $4$.
:::

## Squares

::: {.definition #def-square ledger=L006 lean=IsSquare}
A **square number** (or perfect square) is the square $k^2 = k \cdot k$ of a whole
number $k$.
:::

::: {.quote ledger=L006}
:::

The first few are $0, 1, 4, 9, 16, 25, 36, 49, 64$. A *sum of two squares* is a number
of the form $u^2 + v^2$; for instance $13 = 3^2 + 2^2$ and $29 = 5^2 + 2^2$, while no
choice of $u, v$ gives $3$, $7$ or $11$ (try them: the squares up to $11$ are only $0, 1,
4, 9$). Chapter 2 explains why.

::: inpaper
The paper writes $\mathsf{square}\ n$ for "$n$ is a square", meaning that
$n = k^2$ for some $k$ (§1.3):

::: {.quote ledger=C1-15}
:::
:::

## Exercises

::: exercise
Find the quotient and remainder when $29$ is divided by $4$, and when $61$ is divided by
$4$. Which family of odd primes does each belong to?
:::

::: exercise
Show that if $m \mid a$ and $m \mid b$ then $m \mid a + b$.
:::

::: exercise
Show that the square of an odd number is odd. (Write the number as $2k + 1$.)
:::

::: exercise
Write each of $5, 13, 17, 29, 37, 41$ as a sum of two squares.
:::
