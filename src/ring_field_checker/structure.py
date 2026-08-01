"""
structure.py
------------
Classifies a single binary operation table along the ladder:

    magma -> semigroup -> monoid -> group -> abelian group

Each rung requires everything below it plus one more axiom:
  semigroup:      associative
  monoid:         semigroup + two-sided identity
  group:          monoid + every element has a two-sided inverse
  abelian group:  group + commutative

Every step is checked directly (not assumed), and a failure at any rung
stops the ladder there -- e.g. a non-associative table is reported as a
"magma", never silently treated as a semigroup.
"""

from __future__ import annotations
from dataclasses import dataclass

from .axioms import (
    validate_table_shape,
    check_associative,
    check_commutative,
    find_identity,
    check_all_invertible,
)


@dataclass
class SingleOperationReport:
    n: int
    associative: bool
    associativity_counterexample: tuple | None
    identity: int | None
    all_invertible: bool
    non_invertible_element: int | None
    commutative: bool
    commutativity_counterexample: tuple | None
    classification: str

    def summary(self) -> str:
        lines = [f"Classification: {self.classification}"]
        lines.append(f"  associative: {self.associative}" +
                      ("" if self.associative else f"  (fails at {self.associativity_counterexample})"))
        lines.append(f"  identity: {self.identity}")
        if self.identity is not None:
            lines.append(f"  all elements invertible: {self.all_invertible}" +
                          ("" if self.all_invertible else f"  (no inverse for element {self.non_invertible_element})"))
        lines.append(f"  commutative: {self.commutative}" +
                      ("" if self.commutative else f"  (fails at {self.commutativity_counterexample})"))
        return "\n".join(lines)


def classify_single_operation(table: list[list[int]]) -> SingleOperationReport:
    n = validate_table_shape(table)

    associative, assoc_ce = check_associative(table)
    commutative, comm_ce = check_commutative(table)
    identity = find_identity(table) if associative else None

    all_invertible, non_invertible = (False, None)
    if identity is not None:
        all_invertible, non_invertible = check_all_invertible(table, identity)

    if not associative:
        classification = "Magma (not associative)"
    elif identity is None:
        classification = "Semigroup (associative, no identity)"
    elif not all_invertible:
        classification = "Monoid (identity, not all elements invertible)"
    elif commutative:
        classification = "Abelian group"
    else:
        classification = "Group (non-abelian)"

    return SingleOperationReport(
        n=n,
        associative=associative,
        associativity_counterexample=assoc_ce,
        identity=identity,
        all_invertible=all_invertible,
        non_invertible_element=non_invertible,
        commutative=commutative,
        commutativity_counterexample=comm_ce,
        classification=classification,
    )
