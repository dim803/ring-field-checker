"""
constructions.py
-----------------
Concrete example structures to run through the classifier:

  integers_mod_n(n)     -- Z/nZ under addition and multiplication mod n
  gf4()                 -- the field with 4 elements, F2[x]/(x^2+x+1)
  matrix_ring_2x2_f2()  -- 2x2 matrices over F2 under matrix +, * (a
                           noncommutative ring with zero divisors)
  boolean_ring(k)       -- the power set of a k-element set, with symmetric
                           difference as + and intersection as *
  broken_addition_table -- a deliberately non-associative table, for
                           demonstrating what a classifier failure looks like
"""

from __future__ import annotations
from itertools import product


def integers_mod_n(n: int):
    """Z/nZ: returns (add_table, mul_table)."""
    add_table = [[(i + j) % n for j in range(n)] for i in range(n)]
    mul_table = [[(i * j) % n for j in range(n)] for i in range(n)]
    return add_table, mul_table


def gf4():
    """
    GF(4) = F2[x] / (x^2 + x + 1), the field with 4 elements. Elements are
    represented as pairs (a, b) meaning a + b*x, a,b in F2, indexed as
    0 -> 0, 1 -> 1, 2 -> x, 3 -> x+1. Addition is componentwise mod 2;
    multiplication reduces modulo x^2+x+1 (i.e. x^2 = x+1).
    """
    elements = [(0, 0), (1, 0), (0, 1), (1, 1)]  # 0, 1, x, x+1
    index = {e: i for i, e in enumerate(elements)}

    def add(e1, e2):
        return ((e1[0] + e2[0]) % 2, (e1[1] + e2[1]) % 2)

    def mul(e1, e2):
        # (a1 + b1*x)(a2 + b2*x) = a1a2 + (a1b2+a2b1)x + b1b2*x^2
        # x^2 = x + 1, so substitute:
        a1, b1 = e1
        a2, b2 = e2
        const = (a1 * a2 + b1 * b2) % 2         # a1a2 + b1b2*1 (from x^2's constant part)
        lin = (a1 * b2 + a2 * b1 + b1 * b2) % 2  # a1b2+a2b1 + b1b2*1 (from x^2's x part)
        return (const, lin)

    n = 4
    add_table = [[index[add(elements[i], elements[j])] for j in range(n)] for i in range(n)]
    mul_table = [[index[mul(elements[i], elements[j])] for j in range(n)] for i in range(n)]
    return add_table, mul_table


def matrix_ring_2x2_f2():
    """
    M_2(F2): all 2x2 matrices with entries in F2, under matrix addition and
    multiplication mod 2. 16 elements. Noncommutative, has zero divisors,
    has a multiplicative identity (the identity matrix) -- a ring with
    unity that is not a division ring, since not every nonzero matrix is
    invertible (e.g. matrices with determinant 0 mod 2).
    """
    entries = list(product([0, 1], repeat=4))  # (a,b,c,d) meaning [[a,b],[c,d]]
    index = {e: i for i, e in enumerate(entries)}
    n = len(entries)

    def add(m1, m2):
        return tuple((x + y) % 2 for x, y in zip(m1, m2))

    def mul(m1, m2):
        a1, b1, c1, d1 = m1
        a2, b2, c2, d2 = m2
        return (
            (a1 * a2 + b1 * c2) % 2,
            (a1 * b2 + b1 * d2) % 2,
            (c1 * a2 + d1 * c2) % 2,
            (c1 * b2 + d1 * d2) % 2,
        )

    add_table = [[index[add(entries[i], entries[j])] for j in range(n)] for i in range(n)]
    mul_table = [[index[mul(entries[i], entries[j])] for j in range(n)] for i in range(n)]
    return add_table, mul_table


def boolean_ring(k: int):
    """
    The power set of a k-element set as a ring: + is symmetric difference,
    * is intersection. Every element is idempotent under * (a*a = a) -- the
    defining property of a Boolean ring. Commutative, has a multiplicative
    identity (the full set), but has zero divisors whenever k >= 2 (so it's
    never a field except in the degenerate k=... case), and is never an
    integral domain for k >= 2.
    """
    subsets = list(product([0, 1], repeat=k))  # bitmask tuples
    index = {s: i for i, s in enumerate(subsets)}
    n = len(subsets)

    def sym_diff(s1, s2):
        return tuple(a ^ b for a, b in zip(s1, s2))

    def intersect(s1, s2):
        return tuple(a & b for a, b in zip(s1, s2))

    add_table = [[index[sym_diff(subsets[i], subsets[j])] for j in range(n)] for i in range(n)]
    mul_table = [[index[intersect(subsets[i], subsets[j])] for j in range(n)] for i in range(n)]
    return add_table, mul_table


def broken_addition_table():
    """
    A deliberately non-associative table on 3 elements (a Latin square that
    fails associativity), used to demonstrate the "Magma" classification and
    the associativity counterexample it reports.
    """
    return [
        [0, 1, 2],
        [1, 2, 0],
        [2, 0, 2],  # breaks the Latin-square/associativity structure
    ]
