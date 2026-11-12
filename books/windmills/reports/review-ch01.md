# Review: Chapter 1, "Whole Numbers"

## Third pass

Checked only the changed passages and ledger entries. Ledger: 111 entries, 111 verified, 0 failing.

- **N1: resolved.** The sentence now reads "Primes are exactly the numbers greater than $1$ with
  no divisors except the trivial ones." This is correct, and it matches the proposition.
- **N2: resolved.** The sentence now reads "A number greater than $1$ with a divisor other than
  these is called *composite*". This excludes $0$ and $1$, and for natural numbers it agrees
  with C1-02 ("A nonzero integer with at least one non-trivial divisor").
- **N3: resolved.** The proof of `#prop-prime-divisors` now covers both missing pieces:
  - The cases $0$ and $1$: every positive number divides $0$, and $1$ has a single positive
    divisor.
  - The step $a \le p$, via $b \ge 1$ as $p \ne 0$, followed by $1 < a < p$ and $1 < b < p$.

  The forward direction leaves "$a$ is positive" implicit, which is immediate since $p = ab \ne 0$.
  The proof is complete at the stated level.
- **N4: resolved.** C1-14 has been removed from `ledger.jsonl`, and no chapter references it.
  `build/status.json` still lists it, but that file is a stale build artefact and is regenerated
  at build.
- **Item 16: resolved.** C1-20 ("parity is the property of an integer of whether it is even or
  odd", wp-parity lead) matches the source text and covers the word "parity". `#def-parity` now
  carries `ledger=C1-06,C1-20`. `book.lua`'s `ledger_tag` splits on commas, so both entries
  render. The extra quote block is fine.
- **New issues:** none found in the changed passages.

Third-pass verdict: pass (pending the Lean and checks reports from CI)

---


## Second pass

Re-reviewed: the revised `chapters/01-whole-numbers.md`, `ledger.jsonl` (new entries C1-16 to
C1-19, and C1-05, C1-12, C1-15 re-copied with their HOL macros), `Ch01.lean`,
`checks/ch01_examples.py`, the new `derived=` rule in CLAUDE.md, and the HOL macro definitions in
`pipeline/pandoc/book.tex` and `book.lua`.

Gates:
- `p2b.py ledger windmills`: 111 entries, 111 verified, 0 failing.
- Checks: 15 of 15 pass, run locally with a pure-Python stand-in for sympy. They have not run in
  CI yet.
- Lean: excluded from this pass at the coordinator's request.
- Quote rendering: I passed C1-05, C1-12, C1-15 and C1-17 through `pandoc -f markdown+tex_math_dollars -t latex`
  and compiled them with the macros in `book.tex` lines 43-59. They compile without errors and
  print in full ("... written as m div n and m mod n, respectively."; "The only even prime is 2 =
  1² + 1², a sum of two squares."; "square n means it is a square: ∃k. n = k²"; "We write n | m
  ... when n ≠ 0.").

### First-pass items

1. **resolved.** The sentence now reads "Every number $m \geq 1$ is divisible by $1$ and by
   itself". This is consistent with the nonzero-divisor definition.
2. **resolved.** `lean=Nat.prime_def` (`Prime p ↔ 2 ≤ p ∧ ∀ m, m ∣ p → m = 1 ∨ m = p`) matches "p
   is prime iff its positive divisors are exactly $1$ and $p$ (so $p \ge 2$)". The `0 ∣ p` case
   is excluded by `2 ≤ p`.
3. **not assessed** (Lean results come from CI).
4. **resolved.** The opening now describes the paper as a theorem of Fermat about primes and
   squares, backed by C1-16 (§1: "states that a prime $n$ that is one more than a multiple of
   $4$ can be uniquely expressed as a sum of odd and even squares"). "Turns the proof into an
   algorithm" is not covered by C1-16, but the abstract states it ("This gives an algorithm to
   compute the two squares", already L086). Suggestion: cite it.
5. **resolved.** The claim is now `#prop-dvd-mod`, with the hypothesis $n \ne 0$, `derived=L001,L002`,
   a proof, and `lean=...dvd_iff_mod`. See the derived-use assessment below. The Lean statement
   holds for all `n`, so it is stronger than the chapter's statement and implies it.
6. **resolved.** The new remark explains that mathlib allows divisor $0$, with $0 \mid m \iff m = 0$
   (matches mathlib `zero_dvd_iff : 0 ∣ a ↔ a = 0`), and that the definitions agree for $d \ne 0$.
7. **resolved.** `lean=` now lists both `division` and `division_unique`.
8. **resolved.** `#thm-even-odd` now uses `derived=L002,C1-06` instead of the unsupporting C1-07
   quote, has a complete proof (below), and lists all four Lean names.
9. **resolved.** `odd_prime_mod_four` now takes `(ho : Odd p)`, matching "odd prime". The `p ≠ 2`
   form is kept as a separate name and is not attached.
10. **resolved.** C1-05, C1-12 and C1-15 now quote the full sentences, including the HOL parts,
    and they render (see Gates). C1-12 is now also shown as a quote block under
    `#thm-only-even-prime`.
11. **resolved.** "Number" is now defined as "a natural number $0, 1, 2, 3, \dots$, as in the
    paper", backed by C1-18. "Changes nothing" became "we only ever apply them to natural
    numbers", and the division theorem is now proved directly in the naturals, so the
    specialisation from integers is no longer needed.
12. **resolved, with a new issue (N2).** "In the same way, a number greater than $1$ is composite
    exactly when it is not prime" follows from the proof of `#prop-prime-divisors`.
13. **resolved.** The remark adopts the paper's letters ($n \mid m$, divisor $n$). The theorem
    uses $m = nq + r$ and the paper's $m \operatorname{div} n$. Exercise 2 uses $n \mid a$. Only
    the definition keeps $d \mid m$, and the remark says so explicitly.
14. **resolved.** Existence is now proved by repeated subtraction. It stays in the naturals
    ($r - n$ is taken only when $r \ge n$), and termination ("a number can only get smaller
    finitely many times") is at the stated level. Uniqueness is done in the naturals with
    $r \le r'$ WLOG. Each step checks: $nq = nq' + (r'-r) \Rightarrow q \ge q'$ (as $n > 0$),
    $r' - r = n(q-q')$, $r' - r \le r' < n$, so $r' = r$, then $q = q'$ by cancelling $n \ne 0$.
    No negative numbers are used.
15. **resolved.** The second paragraph of the proof gives the converse directions explicitly.
16. **partly resolved.** The "Equivalently ... [@L003]" sentence has been removed, which is fine:
    its one later use, "an even number has $2 \mid n$", is immediate from $n = 2k = k \cdot 2$.
    However, "Whether a number is even or odd is called its **parity**" in `#def-parity` is
    still not in the C1-06 quote. **suggestion:** add the wp-parity lead ("parity is the
    property of an integer of whether it is even or odd") as a ledger entry.
17. **resolved.** Backed by C1-19 (abstract: "especially the parity of the number of fixed points
    in the involutions"). "From Chapter 5 on" matches map.json (`involution-parity` → chapter 5).
18. **resolved.** The exercise now says "Both are prime", and the check `isprime(29) and isprime(61)`
    was added.
19. **resolved for `Even`/`Odd`** (new remark, accurate: mathlib `Even n := ∃ r, n = r + r`,
    `Odd n := ∃ k, n = 2*k+1`). There is still no note for `Nat.Prime := Irreducible p`, but
    `#prop-prime-divisors` now points to `Nat.prime_def`, which bridges the two definitions.
    Acceptable.

### Derived results (`derived=`)

- **`#prop-dvd-mod` (derived=L001,L002): genuine and complete.** The forward direction is
  $m = kn = nk + 0$ with $0 < n$, so the remainder is $0$ by uniqueness (L002). The converse is
  that $r = 0$ gives $m = nq$, so $n \mid m$ by L001. No source states this with `mod`: C1-17
  states it with congruence, which is a different notion not yet introduced, so `derived=` is
  appropriate.
- **`#thm-even-odd` (derived=L002,C1-06): genuine and complete.** Existence: division by $2$
  gives $r \in \{0,1\}$. Converse: $2k = 2k + 0$ and $2k+1$ are already divisions by 2, so the
  remainder is determined by uniqueness. This gives both "exactly when" claims and "not both".
  No source states "not both".

### New issues introduced by the revision

N1. **error**, prose before `#prop-prime-divisors`: "Primes are exactly the numbers with no
    divisors except the trivial ones." This is false for $1$. The trivial divisors of $1$ are $1$
    and $1$, so $1$ has no other divisors, yet it is not prime. (For $0$, trivial divisors are now
    defined only for $m \ge 1$.) The proposition itself is stated correctly ("exactly two positive
    divisors ... so $p \ge 2$"). Fix: "Primes are exactly the numbers greater than $1$ with no
    divisors except the trivial ones."

N2. **should-fix**, *Divisibility*: "A number with a divisor other than these is called
    *composite* [@C1-02]." Since the first pass, the "greater than 1" qualifier has gone and the
    source's "nonzero" was never carried over. Read literally, $0$ qualifies, because every
    nonzero number divides $0$. The source excludes it: C1-02 says "A nonzero integer with at
    least one non-trivial divisor is known as a composite number". Also, "these" (the trivial
    divisors) are defined only for $m \ge 1$ in the previous sentence. Fix: "A number $m \ge 1$
    with a divisor other than these ...".

N3. **should-fix**, `proof` of `#prop-prime-divisors`: the proposition is stated for every number $p$,
    but the proof assumes $p > 1$ in both directions. Two things are missing:
    (a) The cases $p \in \{0, 1\}$. Neither is prime by definition, and neither has exactly two
        positive divisors: $1$ has one, and $0$ has infinitely many, since every nonzero number
        divides $0$. One sentence covers both.
    (b) In the converse, the step "$p = ab$ with $1 < a < p$" needs $a \le p$, which holds because
        $b \ge 1$ since $p \ne 0$. It also needs $a \ne 0$, which holds because divisors are
        nonzero. Neither is said.
    The proposition is sourced (C1-09), so this is a proof-completeness issue, not a sourcing one.

N4. **suggestion**, ledger: C1-14 ("For a natural number $n \in \mathbb{N}$,") is no longer used by
    the chapter and supports nothing on its own. C1-15 now contains it. Consider removing it.

No other new problems found. The numbers added or changed (none beyond the 61 primality check)
are correct and covered by the script. `dvd_iff_mod` (`Nat.mod_eq_zero_of_dvd`,
`Nat.dvd_of_mod_eq_zero`) and the new `odd_prime_mod_four` (`Nat.odd_iff` + `omega`) state the
same as, or more than, the chapter. Notation is now consistent with paper §1.3.

Second-pass verdict: pass after fixes (N1, N2, N3; then the chapter can go to the user once Lean
and checks report from CI)

---

# First pass


Reviewer: independent agent (did not see the writing session). Files reviewed:
`chapters/01-whole-numbers.md`, `ledger.jsonl` (entries L001-L006, C1-01 to C1-15) with their
sources, `lean/Books/Windmills/Ch01.lean`, `checks/ch01_examples.py`, paper §1.3 and §2
(`sources/paper/src/windmills.tex`, `text.txt`), and mathlib at the local copy.

State of the gates as of this review:
- `p2b.py ledger windmills`: 107 entries, 107 verified, 0 failing.
- `checks/ch01_examples.py`: run locally with a pure-Python stand-in for `sympy.isprime`/`primerange`;
  all 14 checks pass. There is no `reports/checks.json` yet, so the check has not run in CI.
- `reports/lean.json` (12:04:49) is older than `Ch01.lean` (12:16:51) and lists only `Names.lean`.
  No `Book.Windmills.Ch01.*` name has been verified (see item 3).

## Findings

1. **error**, *Divisibility*, prose after `#def-divides`.
   Problem: "Every number $n$ is divisible by $1$ and by itself" is false for $n = 0$ under the
   chapter's own definition, which requires the divisor to be nonzero, and the chapter has just
   said "number" includes $0$.
   Evidence: the definition says "divisible by a nonzero number $m$" (L001: "An integer n is
   divisible by a nonzero integer m ..."). Line 29: "Every number $n$ is divisible by $1$ and by
   itself, since $n = n \cdot 1 = 1 \cdot n$." Fix: say "every nonzero number", or drop the nonzero
   condition from the definition (see item 6).

2. **error**, *Prime numbers*, the `.proposition ledger=C1-09 lean=Nat.Prime.eq_one_or_self_of_dvd` block.
   Problem: the Lean name states something different from the proposition. The chapter says "The
   primes are exactly the numbers with exactly two positive divisors", which is an iff about a
   count. The mathlib lemma covers one direction only and says nothing about there being two
   divisors.
   Evidence (mathlib `Data/Nat/Prime/Defs.lean:87`):
   `theorem Prime.eq_one_or_self_of_dvd {p : ℕ} (pp : p.Prime) (m : ℕ) (hm : m ∣ p) : m = 1 ∨ m = p`.
   Better targets: `Nat.prime_def : Prime p ↔ 2 ≤ p ∧ ∀ m, m ∣ p → m = 1 ∨ m = p` (an iff that
   matches the sentence before the block), or `Nat.Prime.divisors : divisors p = {1, p}`. This name
   is also absent from `reports/lean.json`.

3. **should-fix (blocks showing the chapter)**, `Ch01.lean` / all `lean=Book.Windmills.Ch01.*` attributes.
   Problem: Ch01.lean has not been checked by CI. Under rule 5, none of
   `division`, `even_or_odd`, `even_iff_mod`, `prime_even_eq_two` or `odd_prime_mod_four` may be shown
   as verified yet. Rule 5 also requires CI checks to pass before a chapter is shown, and there is
   no `reports/checks.json`.
   Evidence: `reports/lean.json` has `"files": {"Names.lean": ...}` only, and its `names` list
   contains no `Book.Windmills.Ch01.*` entry. Reading the proofs by eye: all mathlib lemmas they use
   exist with matching statements (`Nat.div_add_mod`, `Nat.mod_lt`, `Nat.add_mul_div_left`,
   `Nat.add_mul_mod_self_left`, `Nat.even_iff`, `Nat.odd_iff`, `Nat.even_or_odd`,
   `Nat.Prime.eq_two_or_odd`, `Nat.Prime.mod_two_eq_one_iff_ne_two`), and I see no obvious failure.
   They still need to be pushed and built.

4. **should-fix**, opening paragraph.
   Problem: "The paper is about one question: which whole numbers can be written as a sum of two
   squares?" misdescribes the paper and has no source. The paper is about primes of the form
   $4k+1$ (Fermat's two squares theorem), a formalisation of Zagier's proof, and an algorithm. It
   does not cover all whole numbers.
   Evidence: the abstract says "The two squares theorem of Fermat ... Here is a formalisation of
   this proof ... This gives an algorithm to compute the two squares". §1 says "states that a prime
   𝑛 that is one more than a multiple of 4 can be uniquely expressed as a sum of odd and even squares".

5. **should-fix**, *Division with remainder*, the sentence "Notice that $m \mid n$ exactly when $n \operatorname{mod} m = 0$".
   Problem: the sentence is missing the hypothesis $m \neq 0$. For $m = 0$, $n \operatorname{mod} 0$ is
   undefined, because the division theorem requires $b \neq 0$. The paper states the condition
   explicitly. The claim also has no ledger entry, although one is available.
   Evidence: paper §1.3: "We write n| m when 𝑛 divides 𝑚, which is equivalent to m ≡ 0(mod n) when n ≠ 0."

6. **should-fix**, `#def-divides lean=Dvd.dvd`.
   Problem: the hypotheses differ. The chapter requires a nonzero divisor, but mathlib's `∣` on ℕ has
   no such condition, so `0 ∣ 0` holds in Lean while the chapter's definition excludes it. The
   paper's HOL `divides` also appears to allow a zero divisor: it attaches "when n ≠ 0" only to the
   mod equivalence, not to the definition of `|`. A reader of the paper could trip on this.
   Evidence: L001 says "divisible by a nonzero integer m". Mathlib defines `a ∣ b ↔ ∃ c, b = a * c` with
   no nonzero condition. Fix: add a remark on the difference, or define $m \mid n$ without the
   nonzero condition and note the $0$ case.

7. **should-fix**, `#thm-division lean=Book.Windmills.Ch01.division`.
   Problem: the chapter theorem claims existence and uniqueness, but the `lean=` name proves
   existence only. `division_unique` exists in Ch01.lean but is not attached.
   Evidence: `theorem division (a b : ℕ) (hb : 0 < b) : a = b * (a / b) + a % b ∧ a % b < b`.
   Fix: `lean=Book.Windmills.Ch01.division,Book.Windmills.Ch01.division_unique`. The `0 < b` here
   versus the chapter's $b \neq 0$ is equivalent on ℕ and is fine.

8. **should-fix**, `#thm-even-odd` (`ledger=C1-07`, `lean=...even_or_odd,...even_iff_mod`).
   (a) The ledger quote does not support the statement. It says nothing about "either ... and not
   both", it speaks of congruence modulo 2 (not introduced until Chapter 2), and it does not use
   $n \operatorname{mod} 2$. Evidence, C1-07: "in other words if it is congruent to 0 modulo 2, and
   odd if it is congruent to 1 modulo 2". The proof given is sound, so the theorem stands on its
   proof. The `ledger=` should either point to something that matches or be justified as a
   proved result.
   (b) The `lean=` list leaves out half the statement. "Not both" (`not_even_and_odd`) and "odd
   exactly when $n \operatorname{mod} 2 = 1$" (`odd_iff_mod`) are in Ch01.lean but not attached.

9. **should-fix**, `#thm-odd-prime-mod-4 lean=...odd_prime_mod_four`.
   Problem: the hypotheses differ. The chapter says "odd prime", while Lean assumes `p ≠ 2`. These
   are equivalent only via `#thm-only-even-prime` plus even/odd.
   Evidence: `theorem odd_prime_mod_four {p : ℕ} (hp : p.Prime) (h2 : p ≠ 2)`. Fix: state it with
   `(ho : Odd p)`, or add a remark.

10. **should-fix**, quote blocks C1-05 and C1-15, and ledger C1-12 on `#thm-only-even-prime`.
    Problem: the quotes are truncated before the content they are cited for. C1-05 renders as the
    dangling fragment "The integer quotient and remainder of $m$ divided by $n$ are written as", with
    no `div`/`mod`. C1-12 ("The only even prime is") does not contain "2". C1-15 ("means it is a
    square") does not contain "$n = k^2$ for some $k$", which the chapter attributes to §1.3.
    Evidence: `text.txt` contains the full text: "... are written as m div n and m mod n,
    respectively." and "The only even prime is 2 = 12+ 12". The latter can be quoted as "The only
    even prime is 2". wp-parity also has "All prime numbers are odd, with one exception: the prime
    number 2." as a second source.

11. **should-fix**, paragraph "Throughout, 'number' means a whole number ...".
    Problem: (a) "The paper works with the natural numbers $0, 1, 2, 3, \dots$" has no ledger entry,
    although one is available: paper §1.3 has "The set of natural numbers is denoted byN, counting
    from 0". (b) "Whole number" is ambiguous: some readers include negatives, others exclude 0. The
    next clause mentions negative integers. State plainly that "number" means $0, 1, 2, \dots$
    (c) "which changes nothing we need" is unargued. It is true for the definitions used, but the
    rendered C1-01 quote ("1, −1, n and − n are known as the trivial divisors") and L002 (with
    $|b|$) immediately show integer material the prose then ignores. One sentence explaining the
    specialisation would help.

12. **should-fix**, *Divisibility*, "Composite numbers are exactly the ones that are not prime, as we will see in a moment."
    Problem: this is never shown explicitly. The reader has to combine the composite definition
    with the later unproved sentence "a number $p > 1$ is prime exactly when its only divisors are
    $1$ and $p$" and with C1-09. It also needs the qualifier "greater than 1" ($0$ and $1$ are
    neither). The composite definition is restated from "nonzero integer" (C1-02) to "greater than
    $1$". This is correct for naturals, because $1$ has no non-trivial divisor, but it is not said.

13. **suggestion**, *Division with remainder* / notation vs paper §1.3.
    The chapter uses $m$ as the divisor in $m \mid n$ two lines after quoting the paper's
    $m \operatorname{div} n$, where $m$ is the dividend. The paper writes $n \mid m$ with $n$ the
    divisor ("We write n| m when 𝑛 divides 𝑚"). Using the paper's letter roles throughout
    (dividend $m$, divisor $n$, $n \mid m$) would avoid a swap that a reader moving to §1.3 will
    notice.

14. **suggestion**, `proof` of `#thm-division`.
    The existence step uses the well-ordering principle ("take the smallest"). The baseline lists
    induction, not well-ordering, so one sentence linking them would help. The proof should also
    say the list is non-empty ($a$ itself is $\ge 0$). Both the existence and the uniqueness steps
    use integer subtraction ($a - 2b$, $r' - r$ may be negative). The book treats numbers as
    naturals, and the paper's HOL subtraction on ℕ truncates. A one-line note that the proof works
    in the integers would prevent confusion later, for example in the Zagier map.

15. **suggestion**, `#thm-even-odd` proof.
    The proof shows $r = 0 \Rightarrow$ even and $r = 1 \Rightarrow$ odd. The converse directions
    of the two "exactly when" claims (even $\Rightarrow n \operatorname{mod} 2 = 0$) follow from
    uniqueness, but they are only covered by the "not both" sentence. Spell them out in one line.

16. **suggestion**, *Even and odd*, "Equivalently, a number is even when $2$ divides it and odd when it does not [@L003]".
    L003 states this as a definition, not as an equivalence with the $2k$ / $2k+1$ form. wp-parity
    has the exact sentence: "An equivalent definition is that an even number is divisible by 2: 2 |
    x and an odd number is not". Also, "Whether a number is even or odd is called its **parity**"
    (in `#def-parity`) is not in the C1-06 quote. wp-parity's lead has "parity is the property of an
    integer of whether it is even or odd".

17. **suggestion**, *Even and odd*, "The paper uses parity constantly, both of numbers and, later, of the *sizes of sets*."
    This is a claim about the paper with no citation. The abstract supports it: "especially the
    parity of the number of fixed points in the involutions".

18. **suggestion**, `checks/ch01_examples.py` / Exercise 1.
    Exercise 1 asks which family of odd primes 29 and 61 belong to, which presupposes that 61 is
    prime. The script checks `divmod(61, 4)` but not `isprime(61)`. (61 is prime; I checked it
    locally.) Add it. Every other number in the chapter is covered by the script and correct: 17 =
    3·5+2; 3∣12, 3∤13; primes below 30; 7 prime; the 4k+1 and 4k+3 lists; first squares; 13, 29, 2
    as sums of squares; 3, 7, 11 not sums of two squares; Exercise 4 values.

19. **suggestion**, `#def-parity lean=Even,Odd` and `#def-prime lean=Nat.Prime`.
    These match up to an obvious rewriting: mathlib `Even n := ∃ r, n = r + r` rather than $2k$, and
    `Nat.Prime p := Irreducible p` rather than "not a product of two smaller numbers". This is
    acceptable. A footnote would help a reader who opens the Lean.

Checked and found correct: `#def-square` vs L006 and `IsSquare` (`∃ r, a = r * r`); the
division-theorem specialisation from integers ($|b| = b$, $q \ge 0$ for natural $a, b$); the
uniqueness argument; the proofs of `#thm-only-even-prime` and `#thm-odd-prime-mod-4`; the inpaper
note on §2, which matches "The only even prime is 2 = 1²+1² ... An odd prime, upon division by 4,
leaves a remainder of either 1 or 3"; the paper's notation for even/odd/square/div/mod; and the
forward reference "Chapter 2 explains why" (Chapter 2 holds `squares-mod-4` in map.json).

Verdict: pass after fixes
