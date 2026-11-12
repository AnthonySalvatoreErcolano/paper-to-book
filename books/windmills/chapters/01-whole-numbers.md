---
title: Whole Numbers
node: [divisibility, division, parity, prime, square]
---

# Whole Numbers

The paper proves a theorem of Fermat about primes and squares, and turns the proof into
an algorithm. In the paper's own words:

::: {.quote ledger=C1-16}
:::

To follow it you need five ideas about whole numbers: when one number *divides*
another, *division with remainder*, *even and odd*, *primes*, and *squares*. This
chapter introduces each and proves the few facts about them that the paper uses.

Throughout, a *number* means a natural number $0, 1, 2, 3, \dots$, as in the paper:

::: {.quote ledger=C1-18}
:::

Some of the definitions quoted below are stated for all integers, negative ones
included; we only ever apply them to natural numbers.

## Divisibility

::: {.definition #def-divides ledger=L001 lean=Dvd.dvd}
A number $m$ is **divisible** by a nonzero number $d$ if $m = kd$ for some number $k$.
We then say $d$ *divides* $m$, and write $d \mid m$.
:::

::: {.quote ledger=L001}
:::

So $3 \mid 12$ because $12 = 4 \cdot 3$, but $3 \nmid 13$: no number $k$ has $3k = 13$.
Every number $m \geq 1$ is divisible by $1$ and by itself, since $m = m \cdot 1$. These
two are its *trivial* divisors:

::: {.quote ledger=C1-01}
:::

A number with a divisor other than these is called *composite* [@C1-02].

::: remark
The paper writes $n \mid m$ for "$n$ divides $m$", with $n$ as the divisor, and from
here on we use its letters (§1.3):

::: {.quote ledger=C1-17}
:::

Lean's mathlib, which checks the statements in this book, defines $d \mid m$ for every
$d$, including $d = 0$: there $0 \mid m$ holds only when $m = 0$. For $d \ne 0$ the two
definitions agree.
:::

## Division with remainder

Most numbers don't divide each other exactly; what is left over is the *remainder*.

::: {.theorem #thm-division ledger=L002 lean=Book.Windmills.Ch01.division,Book.Windmills.Ch01.division_unique}
**Division with remainder.** Given numbers $m$ and $n$ with $n \neq 0$, there are unique
numbers $q$ (the *quotient*) and $r$ (the *remainder*) such that
$$m = nq + r \qquad\text{and}\qquad 0 \le r < n.$$
:::

::: {.quote ledger=L002}
:::

::: example
Dividing $17$ by $3$: the quotient is $5$ and the remainder is $2$, since
$17 = 3 \cdot 5 + 2$ and $2 < 3$. [@C1-03]
:::

::: proof
*Existence.* Start with $r = m$ and $q = 0$, so that $m = nq + r$. While $r \ge n$,
replace $r$ by $r - n$ and $q$ by $q + 1$; the equation $m = nq + r$ still holds. Each
step makes $r$ smaller, and a number can only get smaller finitely many times, so the
process stops, with $r < n$.

*Uniqueness.* Suppose also $m = nq' + r'$ with $r' < n$, and say $r \le r'$ (otherwise
swap the two). Then $nq = nq' + (r' - r)$, so $q \ge q'$ and $r' - r = n(q - q')$. The
left side is less than $n$, and the only multiple of $n$ less than $n$ is $0$. So
$r' = r$, and then $q' = q$.
:::

The paper writes the quotient as $m \operatorname{div} n$ and the remainder as
$m \operatorname{mod} n$:

::: {.quote ledger=C1-05}
:::

For example, $17 \operatorname{div} 3 = 5$ and $17 \operatorname{mod} 3 = 2$. Dividing
leaves nothing over exactly when $n$ divides $m$:

::: {.proposition #prop-dvd-mod derived=L001,L002 lean=Book.Windmills.Ch01.dvd_iff_mod}
For $n \ne 0$: $\ n \mid m$ if and only if $m \operatorname{mod} n = 0$.
:::

::: proof
If $m = kn$, then $m = nk + 0$ with $0 < n$, so by uniqueness the remainder is $0$.
Conversely, if the remainder is $0$, then $m = nq$, so $n \mid m$.
:::

## Even and odd

::: {.definition #def-parity ledger=C1-06 lean=Even,Odd}
A number is **even** if it has the form $2k$, and **odd** if it has the form $2k + 1$,
for some number $k$. Whether a number is even or odd is called its **parity**.
:::

::: {.quote ledger=C1-06}
:::

::: {.theorem #thm-even-odd derived=L002,C1-06 lean=Book.Windmills.Ch01.even_or_odd,Book.Windmills.Ch01.not_even_and_odd,Book.Windmills.Ch01.even_iff_mod,Book.Windmills.Ch01.odd_iff_mod}
Every number is either even or odd, and not both. A number $n$ is even exactly when
$n \operatorname{mod} 2 = 0$, and odd exactly when $n \operatorname{mod} 2 = 1$.
:::

::: proof
Divide $n$ by $2$: $n = 2q + r$ with $r \in \{0, 1\}$. If $r = 0$ then $n = 2q$ is even;
if $r = 1$ then $n = 2q + 1$ is odd. So every number is one or the other.

Conversely, if $n = 2k$ then $n = 2k + 0$, and if $n = 2k + 1$ then that is already a
division by $2$ with remainder $1$. By uniqueness of the remainder, an even number has
remainder $0$ and an odd number has remainder $1$; in particular no number is both.
:::

Parity behaves simply under addition: even $+$ even and odd $+$ odd are even, while
even $+$ odd is odd (write the numbers as $2a$ or $2a + 1$ and add). Parity matters
throughout the paper, both of numbers and, from Chapter 5 on, of the *sizes of sets*:

::: {.quote ledger=C1-19}
:::

::: remark
mathlib phrases these definitions slightly differently: `Even n` says $n = r + r$ for
some $r$, and `Odd n` says $n = 2k + 1$. The first is the same as $n = 2r$.
:::

::: inpaper
The paper's notation section (§1.3) writes $\mathsf{even}\ n$ and
$\mathsf{odd}\ n$ for these two properties:

::: {.quote ledger=C1-08}
:::
:::

## Prime numbers

::: {.definition #def-prime ledger=L005 lean=Nat.Prime}
A **prime number** is a number greater than $1$ that is not a product of two smaller
numbers.
:::

::: {.quote ledger=L005}
:::

The *divisors* of $n$ are the numbers that divide it evenly [@C1-11]. Primes are
exactly the numbers with no divisors except the trivial ones:

::: {.proposition #prop-prime-divisors ledger=C1-09 lean=Nat.prime_def}
A number $p$ is prime if and only if it has exactly two positive divisors, $1$ and $p$
(so in particular $p \ge 2$).
:::

::: proof
If $p > 1$ is a product $ab$ of two numbers smaller than $p$, then $a \ne 1$ (else
$b = p$) and $a \ne p$, so $a$ is a third divisor. Conversely, if $p > 1$ has a divisor
$a$ other than $1$ and $p$, then $p = ab$ with $1 < a < p$, and then $1 < b < p$ too,
so $p$ is a product of two smaller numbers.
:::

In the same way, a number greater than $1$ is composite exactly when it is not prime.

::: example
$7$ is prime: none of $2, 3, 4, 5, 6$ divides it [@C1-10]. The primes below $30$ are
$2, 3, 5, 7, 11, 13, 17, 19, 23, 29$.
:::

Two facts about primes matter for the paper.

::: {.theorem #thm-only-even-prime ledger=C1-12 lean=Book.Windmills.Ch01.prime_even_eq_two}
The only even prime is $2$.
:::

::: {.quote ledger=C1-12}
:::

::: proof
An even number $n$ has $2 \mid n$. If $n$ is prime, its only divisors are $1$ and $n$,
so $n = 2$.
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
§2 opens with exactly these two facts: the only even prime is a sum of two squares, and
the odd primes split by their remainder on division by $4$.
:::

## Squares

::: {.definition #def-square ledger=L006 lean=IsSquare}
A **square number** (or perfect square) is the square $k^2 = k \cdot k$ of a number $k$.
:::

::: {.quote ledger=L006}
:::

The first few are $0, 1, 4, 9, 16, 25, 36, 49, 64$. A *sum of two squares* is a number
of the form $u^2 + v^2$; for instance $13 = 3^2 + 2^2$ and $29 = 5^2 + 2^2$, while no
choice of $u, v$ gives $3$, $7$ or $11$ (the squares up to $11$ are only $0, 1, 4, 9$,
and no two of them add up to $3$, $7$ or $11$). Chapter 2 explains why.

::: inpaper
The paper writes $\mathsf{square}\ n$ for "$n$ is a square" (§1.3):

::: {.quote ledger=C1-15}
:::
:::

## Exercises

::: exercise
Find the quotient and remainder when $29$ is divided by $4$, and when $61$ is divided by
$4$. Both are prime; which family of odd primes does each belong to?
:::

::: exercise
Show that if $n \mid a$ and $n \mid b$ then $n \mid a + b$.
:::

::: exercise
Show that the square of an odd number is odd. (Write the number as $2k + 1$.)
:::

::: exercise
Write each of $5, 13, 17, 29, 37, 41$ as a sum of two squares.
:::
