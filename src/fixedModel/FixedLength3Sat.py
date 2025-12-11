import random

class FixedLength3SAT:
    """
    Random 3-SAT formula generator.

    Parameters:
        L (int): Number of clauses.
        N (int): Number of distinct propositional variables (1..N).
        seed (int | None): Optional RNG seed for reproducibility.

    Representation:
        - Variables are 1..N.
        - Literals are ints:
            +k means variable k
            -k means ¬k
        - Clauses are lists of exactly 3 literals.
        - self.clauses is a list[list[int]].
    """

    def __init__(self, L: int, N: int, seed: int | None = None):
        if N < 3:
            raise ValueError("Need at least 3 variables to build 3-literal clauses.")
        if L <= 0:
            raise ValueError("Number of clauses L must be positive.")

        self.L = L
        self.N = N
        self.seed = seed

        self.clauses: list[list[int]] = []
        self._generate()

    def _generate(self) -> None:
        """
        Generate L random 3-literal clauses over N variables.
        Each clause uses 3 distinct variables.
        Each literal is negated independently with probability 0.5.
        """
        rng = random.Random(self.seed)

        for _ in range(self.L):
            in_use_vars = rng.sample(range(1, self.N + 1), 3)

            clause = []

            for var in in_use_vars:
                if rng.random() < 0.5:
                    clause.append(-1 * var)
                else:
                    clause.append(var)
            self.clauses.append(clause)

    # ---------- Public API ----------

    def getCNFList(self) -> list[list[int]]:
        """
        Return the generated CNF as a list of 3-literal clauses.
        """
        return self.clauses

    def write_dimacs(self, path: str) -> None:
        """
        Write the generated 3-SAT instance to a DIMACS CNF file.

        Args:
            path (str): Output file path, e.g. "random_3sat.cnf".
        """
        with open(path, "w", encoding="utf-8") as f:
            # Header: p cnf <numVars> <numClauses>
            f.write(f"p cnf {self.N} {self.L}\n")
            for clause in self.clauses:
                line = " ".join(str(lit) for lit in clause) + " 0\n"
                f.write(line)
