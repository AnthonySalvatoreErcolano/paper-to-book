/-
Chapter 1 — Whole Numbers.
Each theorem here is the formal counterpart of a numbered statement in the chapter; the
chapter's `lean=` attributes point at these names. Everything is proved from mathlib.
-/
import Mathlib

namespace Book.Windmills.Ch01

/-- Division with remainder (Theorem "Division with remainder"): `a = b * (a / b) + a % b`
with `a % b < b`, for `b ≠ 0`. -/
theorem division (a b : ℕ) (hb : 0 < b) : a = b * (a / b) + a % b ∧ a % b < b :=
  ⟨(Nat.div_add_mod a b).symm, Nat.mod_lt a hb⟩

/-- Uniqueness of quotient and remainder. -/
theorem division_unique (a b q r : ℕ) (hr : r < b) (h : a = b * q + r) :
    q = a / b ∧ r = a % b := by
  subst h
  have hb : 0 < b := lt_of_le_of_lt (Nat.zero_le r) hr
  constructor
  · rw [Nat.add_comm, Nat.add_mul_div_left _ _ hb, Nat.div_eq_of_lt hr, Nat.zero_add]
  · rw [Nat.add_comm, Nat.add_mul_mod_self_left, Nat.mod_eq_of_lt hr]

/-- Every number is even or odd. -/
theorem even_or_odd (n : ℕ) : Even n ∨ Odd n := Nat.even_or_odd n

/-- Even exactly when the remainder on division by 2 is 0. -/
theorem even_iff_mod (n : ℕ) : Even n ↔ n % 2 = 0 := Nat.even_iff

/-- Odd exactly when the remainder on division by 2 is 1. -/
theorem odd_iff_mod (n : ℕ) : Odd n ↔ n % 2 = 1 := Nat.odd_iff

/-- Not both even and odd. -/
theorem not_even_and_odd (n : ℕ) : ¬ (Even n ∧ Odd n) := by
  rintro ⟨he, ho⟩
  rw [Nat.even_iff] at he
  rw [Nat.odd_iff] at ho
  omega

/-- The only even prime is 2. -/
theorem prime_even_eq_two {p : ℕ} (hp : p.Prime) (he : Even p) : p = 2 := by
  rcases hp.eq_two_or_odd with h | h
  · exact h
  · rw [Nat.even_iff] at he
    omega

/-- An odd prime leaves remainder 1 or 3 on division by 4. -/
theorem odd_prime_mod_four {p : ℕ} (hp : p.Prime) (h2 : p ≠ 2) :
    p % 4 = 1 ∨ p % 4 = 3 := by
  have h := hp.mod_two_eq_one_iff_ne_two.mpr h2
  omega

/-- The worked examples of the chapter. -/
example : 17 = 3 * 5 + 2 ∧ 17 / 3 = 5 ∧ 17 % 3 = 2 := by norm_num
example : Nat.Prime 7 ∧ Nat.Prime 29 := by norm_num
example : 13 = 3 ^ 2 + 2 ^ 2 ∧ 29 = 5 ^ 2 + 2 ^ 2 := by norm_num

end Book.Windmills.Ch01
