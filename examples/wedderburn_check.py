"""
wedderburn_check.py
----------------------
Wedderburn's little theorem: every finite division ring is a field -- i.e.
there is no finite ring where multiplication is associative, has an
identity, every nonzero element is invertible, but multiplication is NOT
commutative. This script checks that claim against every division-ring-like
construction available here: none of them should ever come back classified
as "Division ring (non-commutative)".
"""

from ring_field_checker import (
    classify_ring_like,
    integers_mod_n,
    gf4,
    matrix_ring_2x2_f2,
    boolean_ring,
)


if __name__ == "__main__":
    examples = {
        "Z2": integers_mod_n(2),
        "Z3": integers_mod_n(3),
        "Z5": integers_mod_n(5),
        "Z7": integers_mod_n(7),
        "Z11": integers_mod_n(11),
        "GF(4)": gf4(),
        "M2(F2)": matrix_ring_2x2_f2(),
        "Boolean ring (k=1)": boolean_ring(1),
        "Boolean ring (k=2)": boolean_ring(2),
        "Boolean ring (k=3)": boolean_ring(3),
    }

    print("Checking Wedderburn's little theorem against every example:\n")
    violation_found = False
    for name, (add_t, mul_t) in examples.items():
        r = classify_ring_like(add_t, mul_t)
        flag = " <-- WOULD VIOLATE WEDDERBURN" if r.classification == "Division ring (non-commutative)" else ""
        print(f"  {name:20s} n={r.n:3d}  ->  {r.classification}{flag}")
        if flag:
            violation_found = True

    print()
    if violation_found:
        print("Unexpected: found a finite non-commutative division ring. "
              "This would either be a bug in the classifier or a major result.")
    else:
        print("As guaranteed by Wedderburn's little theorem: no finite "
              "non-commutative division ring appears among these examples. "
              "Every finite division ring found here is a field.")
