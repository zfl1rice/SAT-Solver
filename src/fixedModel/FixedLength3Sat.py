# src/fixedModel/FixedModel.py (or wherever you put it)
import random

class FixedLength3SAT:
    """
    Random 3-SAT formula generator.

    Variables: 1..N
    Literals:  +k for var k, -k for ¬k
    Clauses:   list of 3 distinct variables, each negated with prob 0.5
    """

    def __init__(self, L: int, N: int, seed: int | None = None):
        if N < 3:
            raise ValueError("Need at least 3 variables for 3-literal clauses.")
        if L <= 0:
            raise ValueError("Number of clauses L must be positive.")

        self.L = L
        self.N = N
        self.seed = seed

        self.clauses: list[list[int]] = []
        self._generate()

    def _generate(self) -> None:
        rng = random.Random(self.seed)

        for _ in range(self.L):
            # 3 distinct vars from 1..N
            vars_in_clause = rng.sample(range(1, self.N + 1), 3)
            clause = []
            for v in vars_in_clause:
                lit = -v if rng.random() < 0.5 else v
                clause.append(lit)
            self.clauses.append(clause)

    def getCNFList(self) -> list[list[int]]:
        """Return CNF as list of 3-literal clauses."""
        return self.clauses
