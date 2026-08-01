import pytest

from ring_field_checker import (
    classify_single_operation,
    classify_ring_like,
    integers_mod_n,
    gf4,
    matrix_ring_2x2_f2,
    boolean_ring,
    broken_addition_table,
    MalformedTableError,
)
from ring_field_checker.axioms import validate_table_shape


# ---------------------------------------------------------------------- #
# Table validation
# ---------------------------------------------------------------------- #

def test_valid_table_accepted():
    assert validate_table_shape([[0, 1], [1, 0]]) == 2


def test_non_square_table_rejected():
    with pytest.raises(MalformedTableError):
        validate_table_shape([[0, 1], [1, 0], [0, 1]])


def test_out_of_range_entry_rejected():
    with pytest.raises(MalformedTableError):
        validate_table_shape([[0, 2], [1, 0]])


def test_empty_table_rejected():
    with pytest.raises(MalformedTableError):
        validate_table_shape([])


# ---------------------------------------------------------------------- #
# Single-operation classification
# ---------------------------------------------------------------------- #

def test_cyclic_group_table_is_abelian_group():
    n = 6
    table = [[(i + j) % n for j in range(n)] for i in range(n)]
    r = classify_single_operation(table)
    assert r.classification == "Abelian group"
    assert r.associative and r.commutative
    assert r.identity == 0
    assert r.all_invertible


def test_non_associative_table_reports_counterexample():
    r = classify_single_operation(broken_addition_table())
    assert r.classification == "Magma (not associative)"
    assert not r.associative
    a, b, c = r.associativity_counterexample
    table = broken_addition_table()
    ab_c = table[table[a][b]][c]
    a_bc = table[a][table[b][c]]
    assert ab_c != a_bc  # the reported counterexample is a genuine one


def test_semigroup_without_identity():
    # {0,1} under table where nothing acts as identity but it's associative:
    # constant operation a*b = 0 is associative (both sides give 0) with no identity
    table = [[0, 0], [0, 0]]
    r = classify_single_operation(table)
    assert r.classification == "Semigroup (associative, no identity)"
    assert r.identity is None


def test_monoid_with_non_invertible_element():
    # {0,1} under multiplication mod 2-like table: 1 is identity, but 0 has no inverse
    table = [[0, 0], [0, 1]]
    r = classify_single_operation(table)
    assert r.identity == 1
    assert not r.all_invertible
    assert r.non_invertible_element == 0
    assert r.classification == "Monoid (identity, not all elements invertible)"


def test_nonabelian_group_s3_addition_style():
    # reuse S3's multiplication table structure via composition of a small
    # permutation set, just to get a genuine non-abelian group table
    from itertools import permutations
    perms = list(permutations(range(3)))
    index = {p: i for i, p in enumerate(perms)}

    def compose(f, g):
        return tuple(f[g[x]] for x in range(3))

    table = [[index[compose(perms[i], perms[j])] for j in range(6)] for i in range(6)]
    r = classify_single_operation(table)
    assert r.classification == "Group (non-abelian)"
    assert not r.commutative


# ---------------------------------------------------------------------- #
# Ring/field classification against known theory
# ---------------------------------------------------------------------- #

def test_z_prime_is_a_field():
    for p in [2, 3, 5, 7, 11]:
        add_t, mul_t = integers_mod_n(p)
        r = classify_ring_like(add_t, mul_t)
        assert r.classification == "Field", f"Z{p} should be a field"


def test_z_composite_is_not_a_field_and_has_zero_divisors():
    for n in [4, 6, 8, 9, 10, 12]:
        add_t, mul_t = integers_mod_n(n)
        r = classify_ring_like(add_t, mul_t)
        assert r.classification != "Field"
        assert r.zero_divisor_pair is not None
        a, b = r.zero_divisor_pair
        assert mul_t[a][b] == 0
        assert a != 0 and b != 0


def test_gf4_is_a_field_distinct_from_z4():
    add4, mul4 = gf4()
    r = classify_ring_like(add4, mul4)
    assert r.classification == "Field"

    # Z4 is NOT a field (2*2=0 is a zero divisor), confirming GF(4) != Z4
    add_z4, mul_z4 = integers_mod_n(4)
    r_z4 = classify_ring_like(add_z4, mul_z4)
    assert r_z4.classification != "Field"


def test_gf4_multiplicative_group_is_cyclic_of_order_3():
    # the nonzero elements of any finite field form a cyclic group;
    # for GF(4) that's a group of order 3
    add4, mul4 = gf4()
    zero = 0
    identity = 1
    nonzero = [x for x in range(4) if x != zero]
    # every nonzero element to the 3rd power should be the identity (order divides 3)
    for x in nonzero:
        cube = mul4[mul4[x][x]][x]
        assert cube == identity


def test_matrix_ring_2x2_f2_is_noncommutative_with_zero_divisors():
    add_m, mul_m = matrix_ring_2x2_f2()
    r = classify_ring_like(add_m, mul_m)
    assert r.n == 16
    assert not r.mult_commutative
    assert r.zero_divisor_pair is not None
    assert r.mult_identity is not None  # the identity matrix
    assert r.classification == "Ring with unity"  # not a division ring: singular matrices exist


def test_boolean_ring_elements_are_idempotent():
    # defining property of a Boolean ring: a*a = a for every element
    add_b, mul_b = boolean_ring(3)
    n = len(mul_b)
    for a in range(n):
        assert mul_b[a][a] == a


def test_boolean_ring_classification():
    for k in [1, 2, 3]:
        add_b, mul_b = boolean_ring(k)
        r = classify_ring_like(add_b, mul_b)
        assert r.mult_commutative
        assert r.mult_identity is not None
        if k >= 2:
            # power set of a >=2-element set has proper nonempty subsets
            # that multiply (intersect) to give zero divisors
            assert r.zero_divisor_pair is not None
            assert r.classification != "Field"


def test_broken_addition_makes_it_not_a_ring():
    broken = broken_addition_table()
    # use it as the addition table paired with a trivial multiplication table
    trivial_mul = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    r = classify_ring_like(broken, trivial_mul)
    assert not r.is_ring
    assert r.classification.startswith("Not a ring")


# ---------------------------------------------------------------------- #
# Wedderburn's little theorem, checked computationally
# ---------------------------------------------------------------------- #

def test_wedderburn_no_finite_noncommutative_division_ring_appears():
    """
    Wedderburn's little theorem: every finite division ring is a field.
    None of the constructed examples here should ever be classified as a
    non-commutative division ring -- if one did, either the classifier has
    a bug, or (impossibly) the theorem would be violated.
    """
    examples = [
        integers_mod_n(2), integers_mod_n(3), integers_mod_n(5), integers_mod_n(7),
        gf4(),
        matrix_ring_2x2_f2(),
        boolean_ring(1), boolean_ring(2), boolean_ring(3),
    ]
    for add_t, mul_t in examples:
        r = classify_ring_like(add_t, mul_t)
        assert r.classification != "Division ring (non-commutative)"
