"""Chapter 1: every number the chapter states, recomputed."""
from sympy import isprime, primerange

fails = []
def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        fails.append(name)

check("17 = 3*5 + 2, quotient 5, remainder 2", 17 == 3 * 5 + 2 and divmod(17, 3) == (5, 2))
check("12 = 4*3 so 3 | 12; 3 does not divide 13", 12 % 3 == 0 and 13 % 3 != 0)
check("primes below 30", list(primerange(2, 30)) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
check("7 prime, none of 2..6 divides it", isprime(7) and all(7 % d for d in range(2, 7)))
check("5,13,17,29 are 4k+1 primes", all(isprime(p) and p % 4 == 1 for p in (5, 13, 17, 29)))
check("3,7,11,19,23 are 4k+3 primes", all(isprime(p) and p % 4 == 3 for p in (3, 7, 11, 19, 23)))
check("every odd prime below 10^5 is 1 or 3 mod 4", all(p % 4 in (1, 3) for p in primerange(3, 10**5)))
check("first squares", [k * k for k in range(9)] == [0, 1, 4, 9, 16, 25, 36, 49, 64])
check("13 = 3^2+2^2, 29 = 5^2+2^2, 2 = 1^2+1^2", 13 == 9 + 4 and 29 == 25 + 4 and 2 == 1 + 1)
sums = {u * u + v * v for u in range(12) for v in range(12)}
check("3, 7, 11 are not sums of two squares", not ({3, 7, 11} & sums))
check("squares up to 11 are 0,1,4,9", [k * k for k in range(12) if k * k <= 11] == [0, 1, 4, 9])
# exercises (answers checked so the exercise statements are sound)
check("29 and 61 are prime", isprime(29) and isprime(61))
check("29 = 4*7+1, 61 = 4*15+1", divmod(29, 4) == (7, 1) and divmod(61, 4) == (15, 1))
check("5,13,17,29,37,41 are sums of two squares", all(p in sums for p in (5, 13, 17, 29, 37, 41)))
check("odd squares are odd (k < 10^4)", all(((2 * k + 1) ** 2) % 2 == 1 for k in range(10**4)))
raise SystemExit(1 if fails else 0)
