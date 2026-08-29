"""
DataMorph Studio - Prime Number Generation & Cryptographic Sieve Algorithms
Implements Sieve of Eratosthenes, Miller-Rabin primality test, Extended Euclidean GCD, and Modular Exponentiation.
"""

import random
from typing import List, Tuple


class NumberTheoryEngine:
    """Provides fundamental number theoretic functions."""
    @classmethod
    def sieve_of_eratosthenes(cls, limit: int) -> List[int]:
        if limit < 2:
            return []
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False
        for p in range(2, int(limit ** 0.5) + 1):
            if is_prime[p]:
                for multiple in range(p * p, limit + 1, p):
                    is_prime[multiple] = False
        return [i for i, prime in enumerate(is_prime) if prime]

    @classmethod
    def miller_rabin_is_prime(cls, n: int, k: int = 5) -> bool:
        """Probabilistic Miller-Rabin Primality Test."""
        if n < 2: return False
        if n in (2, 3): return True
        if n % 2 == 0: return False

        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2

        for _ in range(k):
            a = random.randrange(2, n - 1)
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True

    @classmethod
    def extended_gcd(cls, a: int, b: int) -> Tuple[int, int, int]:
        """Extended Euclidean Algorithm: returns (gcd, x, y) such that a*x + b*y = gcd."""
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = cls.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
