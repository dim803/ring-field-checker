"""
classify_examples_demo.py
----------------------------
Runs the classifier over every constructed example, printing the full
axiom-by-axiom report for each -- a tour of the whole ladder from magma up
to field, using genuinely different examples rather than variations on Z_n.
"""

from ring_field_checker import (
    classify_single_operation,
    classify_ring_like,
    integers_mod_n,
    gf4,
    matrix_ring_2x2_f2,
    boolean_ring,
    broken_addition_table,
)


def section(title):
    print(f"\n{'=' * len(title)}\n{title}\n{'=' * len(title)}")


if __name__ == "__main__":
    section("Single-operation ladder: a non-associative magma")
    print(classify_single_operation(broken_addition_table()).summary())

    section("Z6 under addition alone (should be an abelian group)")
    add6, _ = integers_mod_n(6)
    print(classify_single_operation(add6).summary())

    section("Z5 (prime modulus): field")
    add5, mul5 = integers_mod_n(5)
    print(classify_ring_like(add5, mul5).summary())

    section("Z6 (composite modulus): commutative ring with unity, has zero divisors")
    add6, mul6 = integers_mod_n(6)
    print(classify_ring_like(add6, mul6).summary())

    section("GF(4) = F2[x]/(x^2+x+1): a field with 4 elements, not Z4")
    add4, mul4 = gf4()
    print(classify_ring_like(add4, mul4).summary())

    section("M2(F2): 2x2 matrices over F2 -- noncommutative ring with unity")
    addm, mulm = matrix_ring_2x2_f2()
    print(classify_ring_like(addm, mulm).summary())

    section("Boolean ring on a 3-element set: commutative, idempotent multiplication")
    addb, mulb = boolean_ring(3)
    print(classify_ring_like(addb, mulb).summary())
