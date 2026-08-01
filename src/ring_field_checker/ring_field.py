"""
ring_field.py
--------------
Classifies a pair of binary operation tables (+, *) on the same finite set
along the ladder:

    (not a ring) -> ring -> ring with unity -> commutative ring with unity
        -> integral domain -> division ring -> field

Requirements, on top of everything below:
  ring:                       (S,+) is an abelian group; * is associative;
                               both distributive laws hold
  ring with unity:             ring + a multiplicative identity 1 != 0
  commutative ring (+unity):   ring (+unity) + * is commutative
  integral domain:             commutative ring with unity + no zero divisors
  division ring:                ring with unity + every nonzero element has
                               a multiplicative inverse (not necessarily
                               commutative)
  field:                       division ring + commutative

By Wedderburn's little theorem, every finite division ring is automatically
a field -- so for any *finite* example checked here, "division ring but not
a field" should never occur. `examples/wedderburn_check.py` verifies this
computationally against several constructed examples.
"""

from __future__ import annotations
from dataclasses import dataclass

from .axioms import (
    validate_table_shape,
    check_associative,
    check_commutative,
    find_identity,
    check_all_invertible,
    check_distributive,
    find_zero_divisors,
)
from .structure import classify_single_operation


@dataclass
class RingFieldReport:
    n: int
    additive_classification: str
    is_abelian_group_under_addition: bool
    mult_associative: bool
    mult_associativity_counterexample: tuple | None
    distributive: bool
    distributivity_counterexample: tuple | None
    is_ring: bool
    zero: int | None
    mult_identity: int | None
    mult_commutative: bool
    mult_commutativity_counterexample: tuple | None
    zero_divisor_pair: tuple | None
    all_nonzero_invertible: bool
    non_invertible_nonzero_element: int | None
    classification: str

    def summary(self) -> str:
        lines = [f"Classification: {self.classification}"]
        lines.append(f"  (S,+) is an abelian group: {self.is_abelian_group_under_addition} "
                      f"[{self.additive_classification}]")
        if self.is_abelian_group_under_addition:
            lines.append(f"  * associative: {self.mult_associative}" +
                          ("" if self.mult_associative else f"  (fails at {self.mult_associativity_counterexample})"))
            lines.append(f"  distributive: {self.distributive}" +
                          ("" if self.distributive else f"  (fails: {self.distributivity_counterexample})"))
        if self.is_ring:
            lines.append(f"  zero (additive identity): {self.zero}")
            lines.append(f"  multiplicative identity: {self.mult_identity}")
            lines.append(f"  * commutative: {self.mult_commutative}" +
                          ("" if self.mult_commutative else f"  (fails at {self.mult_commutativity_counterexample})"))
            lines.append(f"  zero divisors: {self.zero_divisor_pair}")
            if self.mult_identity is not None:
                lines.append(f"  all nonzero elements invertible: {self.all_nonzero_invertible}" +
                              ("" if self.all_nonzero_invertible
                               else f"  (no inverse for {self.non_invertible_nonzero_element})"))
        return "\n".join(lines)


def classify_ring_like(add_table: list[list[int]], mul_table: list[list[int]]) -> RingFieldReport:
    n = validate_table_shape(add_table)
    if validate_table_shape(mul_table) != n:
        raise ValueError("addition and multiplication tables must be the same size")

    additive_report = classify_single_operation(add_table)
    is_abelian_group = additive_report.classification == "Abelian group"

    if not is_abelian_group:
        return RingFieldReport(
            n=n,
            additive_classification=additive_report.classification,
            is_abelian_group_under_addition=False,
            mult_associative=False, mult_associativity_counterexample=None,
            distributive=False, distributivity_counterexample=None,
            is_ring=False,
            zero=None, mult_identity=None,
            mult_commutative=False, mult_commutativity_counterexample=None,
            zero_divisor_pair=None,
            all_nonzero_invertible=False, non_invertible_nonzero_element=None,
            classification="Not a ring: (S,+) is not an abelian group",
        )

    zero = additive_report.identity
    mult_assoc, mult_assoc_ce = check_associative(mul_table)
    distributive, dist_ce = check_distributive(add_table, mul_table)
    is_ring = mult_assoc and distributive

    if not is_ring:
        reason = "multiplication is not associative" if not mult_assoc else "distributive law fails"
        return RingFieldReport(
            n=n,
            additive_classification=additive_report.classification,
            is_abelian_group_under_addition=True,
            mult_associative=mult_assoc, mult_associativity_counterexample=mult_assoc_ce,
            distributive=distributive, distributivity_counterexample=dist_ce,
            is_ring=False,
            zero=zero, mult_identity=None,
            mult_commutative=False, mult_commutativity_counterexample=None,
            zero_divisor_pair=None,
            all_nonzero_invertible=False, non_invertible_nonzero_element=None,
            classification=f"Not a ring: {reason}",
        )

    mult_identity = find_identity(mul_table)
    mult_commutative, mult_comm_ce = check_commutative(mul_table)
    zero_divisor_pair = find_zero_divisors(mul_table, zero)

    all_nonzero_invertible, non_invertible = False, None
    if mult_identity is not None and n > 1:
        nonzero_table_ok = True
        for x in range(n):
            if x == zero:
                continue
            has_inverse = any(
                y != zero and mul_table[x][y] == mult_identity and mul_table[y][x] == mult_identity
                for y in range(n)
            )
            if not has_inverse:
                nonzero_table_ok = False
                non_invertible = x
                break
        all_nonzero_invertible = nonzero_table_ok

    has_unity = mult_identity is not None and mult_identity != zero
    is_integral_domain = (
        has_unity and mult_commutative and zero_divisor_pair is None and n > 1
    )
    is_division_ring = has_unity and all_nonzero_invertible and n > 1
    is_field = is_division_ring and mult_commutative

    if is_field:
        classification = "Field"
    elif is_division_ring:
        classification = "Division ring (non-commutative)"
    elif is_integral_domain:
        classification = "Integral domain"
    elif has_unity and mult_commutative:
        classification = "Commutative ring with unity"
    elif has_unity:
        classification = "Ring with unity"
    elif mult_commutative:
        classification = "Commutative ring (no multiplicative identity)"
    else:
        classification = "Ring"

    return RingFieldReport(
        n=n,
        additive_classification=additive_report.classification,
        is_abelian_group_under_addition=True,
        mult_associative=True, mult_associativity_counterexample=None,
        distributive=True, distributivity_counterexample=None,
        is_ring=True,
        zero=zero, mult_identity=mult_identity,
        mult_commutative=mult_commutative, mult_commutativity_counterexample=mult_comm_ce,
        zero_divisor_pair=zero_divisor_pair,
        all_nonzero_invertible=all_nonzero_invertible,
        non_invertible_nonzero_element=non_invertible,
        classification=classification,
    )
