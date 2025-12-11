class CNF:
    def __init__(self, dimacs_file: str):
        """
        Load a DIMACS CNF file.

        - Literals are stored as ints:
            +k means variable k, -k means ¬k.
        - Clauses are lists of ints.
        """
        self.clauses = []
        self.numVars = 0
        self.numClauses = 0

        with open(dimacs_file, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                if line.startswith("c"):
                    continue
                if line.startswith("p"):
                    parts = line.split()
                    # p cnf <numVars> <numClauses>
                    self.numVars = int(parts[2])
                    self.numClauses = int(parts[3])
                    continue

                # Clause line: ints ending with 0
                lits = []
                for tok in line.split():
                    lit = int(tok)
                    if lit == 0:
                        break
                    lits.append(lit)
                if lits:
                    self.clauses.append(lits)

        # Fallback if header didn't set numVars
        if self.numVars == 0 and self.clauses:
            self.numVars = max(abs(l) for c in self.clauses for l in c)
        if self.numClauses == 0:
            self.numClauses = len(self.clauses)

    def getCNFList(self):
        return self.clauses
