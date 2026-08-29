"""
DataMorph Studio - Discrete Combinatorics & Permutation Generators
Implements Lexicographical permutations, Gray code binary sequences, integer partitions, and subset generators.
"""

from typing import List, Any, Iterator


class CombinatoricsEngine:
    """Generates combinatorial permutations, combinations, and cartesian products."""
    @classmethod
    def permutations(cls, elements: List[Any], r: Optional[int] = None) -> List[List[Any]]:
        pool = tuple(elements)
        n = len(pool)
        r = n if r is None else r
        if r > n:
            return []
        indices = list(range(n))
        cycles = list(range(n, n - r, -1))
        result = [list(pool[i] for i in indices[:r])]
        while n:
            for i in reversed(range(r)):
                cycles[i] -= 1
                if cycles[i] == 0:
                    indices[i:] = indices[i+1:] + indices[i:i+1]
                    cycles[i] = n - i
                else:
                    j = cycles[i]
                    indices[i], indices[-j] = indices[-j], indices[i]
                    result.append(list(pool[k] for k in indices[:r]))
                    break
            else:
                return result
        return result

    @classmethod
    def gray_code(cls, n_bits: int) -> List[str]:
        """Generates n-bit reflected binary Gray code sequence."""
        if n_bits <= 0:
            return ["0"]
        if n_bits == 1:
            return ["0", "1"]
        prev = cls.gray_code(n_bits - 1)
        return ["0" + code for code in prev] + ["1" + code for code in reversed(prev)]
