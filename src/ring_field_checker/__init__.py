"""
ring_field_checker
-------------------
Classifies finite algebraic structures given by Cayley table(s):

    classify_single_operation(table)          -> magma/semigroup/monoid/(abelian) group
    classify_ring_like(add_table, mul_table)  -> ring / ring with unity / commutative
                                                  ring / integral domain / division ring / field

Every failed axiom comes with a concrete counterexample, not just a verdict.
"""

from .axioms import MalformedTableError
from .structure import classify_single_operation, SingleOperationReport
from .ring_field import classify_ring_like, RingFieldReport
from .constructions import (
    integers_mod_n,
    gf4,
    matrix_ring_2x2_f2,
    boolean_ring,
    broken_addition_table,
)

__all__ = [
    "MalformedTableError",
    "classify_single_operation",
    "SingleOperationReport",
    "classify_ring_like",
    "RingFieldReport",
    "integers_mod_n",
    "gf4",
    "matrix_ring_2x2_f2",
    "boolean_ring",
    "broken_addition_table",
]
