import time
from ..CNF.CNF import CNF


class DPLL:
    """
    Simple DPLL solver using:
      - immutable CNF with integer literals
      - assignment array: var -> True/False/None
      - a trail for backtracking
      - plain unit propagation (no watched literals yet)

    Instrumentation:
      - self.split_count: number of splitting rule applications
      - self.solve_time: total wall-clock time (seconds) for last solve()
    """

    def __init__(self, dimacs_file: str):
        # Load CNF
        self.cnf = CNF(dimacs_file)
        self.clauses = self.cnf.getCNFList()
        self.num_vars = self.cnf.numVars

        # assignment[var] in {True, False, None}; index 0 unused
        self.assignment = [None] * (self.num_vars + 1)
        # trail of (var, value) in order of assignment
        self.trail = []

        # Optional: static variable frequency heuristic
        self.var_freq = [0] * (self.num_vars + 1)
        for clause in self.clauses:
            for lit in clause:
                self.var_freq[abs(lit)] += 1

        # --- Instrumentation fields ---
        self.split_count = 0   # number of times we branch on a variable
        self.solve_time = 0.0  # wall-clock time of last solve()

    # --------- Low-level assignment & undo ---------

    def assign_literal(self, lit: int) -> bool:
        """
        Assign a literal. Returns False if this creates a conflict
        with an existing assignment, True otherwise.
        """
        var = abs(lit)
        val = (lit > 0)  # True if positive literal, False if negative

        current = self.assignment[var]
        if current is not None:
            # If already assigned differently -> conflict
            if current != val:
                return False
            return True

        # New assignment
        self.assignment[var] = val
        self.trail.append((var, val))
        return True

    def undo_to(self, trail_len: int) -> None:
        """
        Undo assignments back to a given trail length.
        """
        while len(self.trail) > trail_len:
            var, _ = self.trail.pop()
            self.assignment[var] = None

    # --------- Propagation & status checking ---------

    def propagate(self) -> bool:
        """
        Perform unit propagation under the current assignment.

        Returns:
            True  if no conflict.
            False if a clause becomes unsatisfiable (all literals false).
        """
        changed = True
        while changed:
            changed = False

            for clause in self.clauses:
                clause_value = False      # has any literal True?
                unassigned_lits = []      # collect unassigned literals

                for lit in clause:
                    var = abs(lit)
                    val = self.assignment[var]

                    if val is None:
                        unassigned_lits.append(lit)
                    else:
                        # literal value under assignment
                        if (lit > 0 and val) or (lit < 0 and not val):
                            clause_value = True
                            break

                if clause_value:
                    # clause already satisfied
                    continue

                if not unassigned_lits:
                    # no literal is True and no unassigned: all False -> conflict
                    return False

                if len(unassigned_lits) == 1:
                    # unit clause: force that literal
                    unit_lit = unassigned_lits[0]
                    if not self.assign_literal(unit_lit):
                        return False
                    changed = True

        return True

    def check_status(self):
        """
        Check if the formula is already SAT, UNSAT, or unknown
        under the current assignment.

        Returns:
            True   if all clauses are satisfied (SAT).
            False  if any clause is unsatisfiable (UNSAT).
            None   if still undecided.
        """
        any_undecided = False

        for clause in self.clauses:
            clause_value = False
            clause_undecided = False

            for lit in clause:
                var = abs(lit)
                val = self.assignment[var]

                if val is None:
                    clause_undecided = True
                else:
                    if (lit > 0 and val) or (lit < 0 and not val):
                        clause_value = True
                        break

            if clause_value:
                continue

            if not clause_undecided:
                # all assigned and clause not satisfied -> UNSAT
                return False

            any_undecided = True

        if any_undecided:
            return None
        else:
            return True

    # --------- Branching heuristic ---------

    def choose_var(self) -> int | None:
        """
        Choose the next unassigned variable to branch on.
        Uses a simple 'most frequent' heuristic.
        """
        best_var = None
        best_score = -1

        for v in range(1, self.num_vars + 1):
            if self.assignment[v] is None:
                score = self.var_freq[v]
                if score > best_score:
                    best_score = score
                    best_var = v

        return best_var

    # --------- Public API ---------

    def solve(self):
        """
        Solve the CNF via DPLL.

        Returns:
            dict[int, bool] | None:
                - dict mapping var -> bool if SAT,
                - None if UNSAT.

        Side effects:
            - Updates self.split_count with the number of branching decisions.
            - Updates self.solve_time with elapsed wall-clock time (seconds).
        """
        # reset instrumentation for this run
        self.split_count = 0
        self.solve_time = 0.0

        start = time.perf_counter()

        # initial propagation
        if not self.propagate():
            self.solve_time = time.perf_counter() - start
            return None  # immediate conflict

        model = self._solve_rec()

        self.solve_time = time.perf_counter() - start
        return model

    # --------- Core recursive DPLL ---------

    def _solve_rec(self):
        """
        Recursive DPLL on current state.

        Returns:
            dict[int, bool] | None:
                - model if SAT
                - None if UNSAT
        """
        status = self.check_status()
        if status is True:
            # build and return model
            return {v: bool(self.assignment[v]) for v in range(1, self.num_vars + 1)}
        elif status is False:
            return None

        # Need to branch
        var = self.choose_var()
        if var is None:
            # No variable left unassigned; treat as SAT with current assignment
            return {v: bool(self.assignment[v]) for v in range(1, self.num_vars + 1)}

        # --- splitting rule applied here ---
        self.split_count += 1

        # Try var = True
        mark = len(self.trail)
        if self.assign_literal(+var) and self.propagate():
            model = self._solve_rec()
            if model is not None:
                return model
        self.undo_to(mark)

        # Try var = False
        mark = len(self.trail)
        if self.assign_literal(-var) and self.propagate():
            model = self._solve_rec()
            if model is not None:
                return model
        self.undo_to(mark)

        # Both branches UNSAT
        return None
