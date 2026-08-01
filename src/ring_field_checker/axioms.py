"""
axioms.py
---------
Low-level axiom checks against a raw Cayley table (a list of lists of
element indices). Each check returns not just a boolean but, when it fails,
a concrete counterexample -- consistent with the idea that "this isn't a
group" should come with a reason, not just a verdict.

A table is a well-formed binary operation on {0, ..., n-1} if it is n x n
and every entry is a valid index; that is validated separately
(MalformedTableError) from whether it satisfies any *algebraic* axiom.
"""

from __future__ import annotations


class MalformedTableError(ValueError):
    """Raised when a table isn't even a valid binary operation (wrong shape,
    or an entry outside the element range) -- a data-integrity problem, not
    an algebraic one."""


def validate_table_shape(table: list[list[int]]) -> int:
    n = len(table)
    if n == 0:
        raise MalformedTableError("a table must have at least one element")
    for row in table:
        if len(row) != n:
            raise MalformedTableError("table must be square")
        for v in row:
            if not (0 <= v < n):
                raise MalformedTableError(f"entry {v} is not a valid element index for n={n}")
    return n


def check_associative(table: list[list[int]]):
    """(a*b)*c == a*(b*c) for all a,b,c. Returns (bool, counterexample or None)."""
    n = len(table)
    for a in range(n):
        for b in range(n):
            ab = table[a][b]
            for c in range(n):
                if table[ab][c] != table[a][table[b][c]]:
                    return False, (a, b, c)
    return True, None


def check_commutative(table: list[list[int]]):
    """a*b == b*a for all a,b. Returns (bool, counterexample pair or None)."""
    n = len(table)
    for a in range(n):
        for b in range(a + 1, n):
            if table[a][b] != table[b][a]:
                return False, (a, b)
    return True, None


def find_identity(table: list[list[int]]):
    """The two-sided identity element, or None if none exists."""
    n = len(table)
    for e in range(n):
        if all(table[e][x] == x and table[x][e] == x for x in range(n)):
            return e
    return None


def check_all_invertible(table: list[list[int]], identity: int):
    """
    True iff every element has a two-sided inverse w.r.t. `identity`.
    Returns (bool, element_without_inverse or None).
    """
    n = len(table)
    for x in range(n):
        if not any(table[x][y] == identity and table[y][x] == identity for y in range(n)):
            return False, x
    return True, None


def check_distributive(add_table: list[list[int]], mul_table: list[list[int]]):
    """
    Both distributive laws: a*(b+c) == a*b + a*c  and  (b+c)*a == b*a + c*a,
    for all a,b,c. Returns (bool, (side, (a,b,c)) or None) where side is
    'left' or 'right'.
    """
    n = len(add_table)
    for a in range(n):
        for b in range(n):
            for c in range(n):
                b_plus_c = add_table[b][c]
                # left distributivity: a*(b+c) == a*b + a*c
                lhs = mul_table[a][b_plus_c]
                rhs = add_table[mul_table[a][b]][mul_table[a][c]]
                if lhs != rhs:
                    return False, ("left", (a, b, c))
                # right distributivity: (b+c)*a == b*a + c*a
                lhs = mul_table[b_plus_c][a]
                rhs = add_table[mul_table[b][a]][mul_table[c][a]]
                if lhs != rhs:
                    return False, ("right", (a, b, c))
    return True, None


def find_zero_divisors(mul_table: list[list[int]], zero: int):
    """
    A pair (a, b) with a != zero, b != zero, but a*b == zero -- or None if
    no such pair exists (i.e. the ring has no zero divisors).
    """
    n = len(mul_table)
    for a in range(n):
        if a == zero:
            continue
        for b in range(n):
            if b == zero:
                continue
            if mul_table[a][b] == zero:
                return (a, b)
    return None
