# Ring/Field Axiom Checker

Given one or two Cayley tables on a finite set, classifies exactly which algebraic structure
they form — walking the ladder **magma → semigroup → monoid → group → abelian group** for a
single operation, and **ring → ring with unity → commutative ring with unity → integral
domain → division ring → field** for a pair of operations $(+, \times)$. Every failed axiom
comes back with a concrete counterexample, not just a verdict.

## Installation

```bash
cd ring-field-checker
pip install -e .
pytest tests/        # 18 tests, checked against known theory (Z_p is a field, Z_n isn't for
                      # composite n, GF(4) != Z4, Wedderburn's theorem holds, ...)
```

## Single operation: the group ladder

```python
from ring_field_checker import classify_single_operation, integers_mod_n

add6, _ = integers_mod_n(6)
report = classify_single_operation(add6)
print(report.classification)   # "Abelian group"
```

Each rung requires everything below it plus one more axiom — associativity, then an identity,
then inverses for every element, then commutativity — and a failure at any rung stops the
ladder there rather than being silently skipped:

```python
from ring_field_checker import classify_single_operation, broken_addition_table

report = classify_single_operation(broken_addition_table())
print(report.classification)                    # "Magma (not associative)"
print(report.associativity_counterexample)       # e.g. (1, 1, 2)
```

## Two operations: the ring ladder

```python
from ring_field_checker import classify_ring_like, integers_mod_n

add5, mul5 = integers_mod_n(5)
print(classify_ring_like(add5, mul5).classification)   # "Field" -- 5 is prime

add6, mul6 = integers_mod_n(6)
print(classify_ring_like(add6, mul6).classification)   # "Commutative ring with unity"
                                                          # -- 6 is composite: 2*3=0 mod 6
```

The full `RingFieldReport` includes the zero element, the multiplicative identity (if any), a
concrete zero-divisor pair (if any), and which nonzero element fails to be invertible (if the
ring isn't a division ring) — `report.summary()` prints all of it.

## Beyond $\mathbb{Z}_n$: genuinely different examples

It's easy for a "field checker" to only ever be tested against $\mathbb{Z}_p$. This project
deliberately includes structures that are *not* just modular integers:

- **`gf4()`** — the field $GF(4) = \mathbb{F}_2[x] / (x^2+x+1)$, a field with 4 elements that
  is **not** $\mathbb{Z}_4$ (which isn't even a field — $\mathbb{Z}_4$ has the zero divisor
  $2 \times 2 = 0$). Confirmed distinct in the test suite, and its nonzero elements are
  checked to form a cyclic group of order 3, as guaranteed for any finite field.
- **`matrix_ring_2x2_f2()`** — $M_2(\mathbb{F}_2)$, the ring of $2\times 2$ matrices over
  $\mathbb{F}_2$ (16 elements). Noncommutative, has zero divisors (singular matrices), has a
  multiplicative identity (the identity matrix) — a genuine ring with unity that is not a
  division ring, since not every nonzero matrix is invertible.
- **`boolean_ring(k)`** — the power set of a $k$-element set, with symmetric difference as $+$
  and intersection as $\times$. Every element satisfies $a \times a = a$ (idempotent
  multiplication), the defining property of a Boolean ring. Commutative, has unity (the full
  set), but has zero divisors for $k \geq 2$.

## Wedderburn's little theorem, checked computationally

**Every finite division ring is a field** — there is no finite ring where multiplication is
associative, has an identity, every nonzero element is invertible, but multiplication fails
to be commutative. `examples/wedderburn_check.py` runs every constructed example through the
classifier and confirms none of them are ever reported as "Division ring (non-commutative)" —
and `tests/test_ring_field_checker.py` asserts this as an explicit invariant. This is a case
where a classifier finding *nothing* unusual is itself a nontrivial confirmation of a real
theorem, not just an absence of bugs.

```
$ python examples/wedderburn_check.py
  Z2                   n=  2  ->  Field
  Z3                   n=  3  ->  Field
  Z5                   n=  5  ->  Field
  GF(4)                n=  4  ->  Field
  M2(F2)               n= 16  ->  Ring with unity
  Boolean ring (k=2)   n=  4  ->  Commutative ring with unity
  ...
As guaranteed by Wedderburn's little theorem: no finite non-commutative
division ring appears among these examples.
```

## Project layout

```
ring-field-checker/
├── pyproject.toml
├── conftest.py
├── src/ring_field_checker/
│   ├── __init__.py
│   ├── axioms.py           (low-level checks: associativity, identity, inverses,
│   │                        commutativity, distributivity, zero divisors -- each
│   │                        returning a counterexample on failure)
│   ├── structure.py        (classify_single_operation: magma -> abelian group)
│   ├── ring_field.py       (classify_ring_like: ring -> field)
│   └── constructions.py    (Z_n, GF(4), M2(F2), Boolean rings, a broken example)
├── examples/
│   ├── classify_examples_demo.py
│   └── wedderburn_check.py
└── tests/
```

## Known limitations

- Classification assumes the *same* multiplicative identity check applies globally; it does
  not attempt to find a subring or handle a table where identity-like behavior only holds on
  a subset of elements.
- `boolean_ring(k)` and `matrix_ring_2x2_f2()` both scale as $2^k$ / $2^4=16$ respectively;
  the axiom checks here are $O(n^3)$ (associativity, distributivity), so this stays fast for
  the sizes used here but would need a smarter approach for much larger structures.
- The checker classifies structures given a *complete* table; it does not attempt to
  reconstruct or validate a partially-specified operation.

## Possible extensions

- Vector space / module axiom checking, given a ring and an abelian group with a scalar
  action
- A search mode: given a partial table, find completions that satisfy a target structure
  (e.g. "complete this into a group")
- Ideal detection in a given ring (subsets closed under addition and absorbing multiplication)
