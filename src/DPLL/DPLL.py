# src/DPLL/DPLL.py
import time
from collections import defaultdict, deque
from ..CNF.CNF import CNF


class DPLL:
    """
    DPLL with:
      - immutable CNF (integer literals)
      - assignment + trail for backtracking
      - watched literals for efficient unit propagation
      - instrumentation: split_count, solve_time

    You can build it from:
      - a DIMACS file: DPLL(dimacs_file="foo.cnf")
      - in-memory CNF: DPLL(clauses=..., num_vars=N)
    """

    def __init__(self,
                 dimacs_file: str | None = None,
                 clauses: list[list[int]] | None = None,
                 num_vars: int | None = None):

        if dimacs_file is None and clauses is None:
            raise ValueError("Provide either dimacs_file or clauses.")
        if dimacs_file is not None and clauses is not None:
            raise ValueError("Provide only one of dimacs_file or clauses, not both.")

        if clauses is not None:
            # in-memory mode
            self.clauses = clauses
            if num_vars is not None:
                self.num_vars = num_vars
            else:
                self.num_vars = max(abs(l) for c in clauses for l in c)
        else:
            # file-based mode
            base = CNF(dimacs_file)
            self.clauses = base.getCNFList()
            self.num_vars = base.numVars

        # assignment[var] in {True, False, None}; index 0 unused
        self.assignment = [None] * (self.num_vars + 1)
        # trail of (var, value)
        self.trail: list[tuple[int, bool]] = []

        # simple static frequency heuristic
        self.var_freq = [0] * (self.num_vars + 1)
        for clause in self.clauses:
            for lit in clause:
                self.var_freq[abs(lit)] += 1

        # watched-literal structures
        self.watch_pos: list[tuple[int, int]] = []
        self.watchlist: dict[int, list[int]] = defaultdict(list)
        self._init_watches()

        # pointer into trail for propagation
        self.last_propagated = 0

        # instrumentation
        self.split_count = 0
        self.solve_time = 0.0

    # ---------- watched-literal initialization ----------

    def _init_watches(self) -> None:
        """
        For each clause, choose two watched literals and
        populate watch_pos and watchlist.
        """
        for ci, clause in enumerate(self.clauses):
            if len(clause) == 0:
                self.watch_pos.append((0, 0))
                continue
            elif len(clause) == 1:
                self.watch_pos.append((0, 0))
                lit = clause[0]
                self.watchlist[lit].append(ci)
            else:
                self.watch_pos.append((0, 1))
                lit1, lit2 = clause[0], clause[1]
                self.watchlist[lit1].append(ci)
                self.watchlist[lit2].append(ci)

    # ---------- assignment & backtracking ----------

    def assign_literal(self, lit: int) -> bool:
        """
        Assign a literal. Returns False if this conflicts with an existing assignment,
        True otherwise.
        """
        var = abs(lit)
        val = lit > 0  # True if positive, False if negative

        current = self.assignment[var]
        if current is not None:
            return current == val

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

        if self.last_propagated > trail_len:
            self.last_propagated = trail_len

    # ---------- watched-literal propagation ----------

    def propagate(self) -> bool:
        """
        Perform unit propagation using watched literals.

        Returns:
            True  if no conflict.
            False if a conflict (empty clause) is found.
        """
        queue = deque()

        # New assignments since last propagation
        for idx in range(self.last_propagated, len(self.trail)):
            var, val = self.trail[idx]
            false_lit = -var if val else var
            queue.append(false_lit)

        self.last_propagated = len(self.trail)

        while queue:
            false_lit = queue.popleft()
            clauses_watching = self.watchlist.get(false_lit)
            if not clauses_watching:
                continue

            # iterate over a snapshot because we'll mutate the list
            for ci in clauses_watching[:]:
                clause = self.clauses[ci]
                w1_idx, w2_idx = self.watch_pos[ci]
                w1_lit = clause[w1_idx]
                w2_lit = clause[w2_idx]

                # Identify which watch is actually false_lit (could be stale)
                if w1_lit == false_lit:
                    false_idx, other_idx = w1_idx, w2_idx
                    other_lit = w2_lit
                elif w2_lit == false_lit:
                    false_idx, other_idx = w2_idx, w1_idx
                    other_lit = w1_lit
                else:
                    # clause no longer actually watches false_lit
                    continue

                # Try to find a replacement literal to watch that is not known-false
                found_replacement = False
                for k, L in enumerate(clause):
                    if k == w1_idx or k == w2_idx:
                        continue
                    var = abs(L)
                    val = self.assignment[var]
                    is_false = (val is not None) and (
                        (L > 0 and not val) or (L < 0 and val)
                    )
                    if not is_false:
                        # move watch from false_lit to L
                        if false_idx == w1_idx:
                            self.watch_pos[ci] = (k, other_idx)
                        else:
                            self.watch_pos[ci] = (other_idx, k)

                        self.watchlist[false_lit].remove(ci)
                        self.watchlist[L].append(ci)

                        found_replacement = True
                        break

                if found_replacement:
                    continue

                # No replacement found: other_lit is only candidate
                var = abs(other_lit)
                val = self.assignment[var]

                if val is not None:
                    is_false = (other_lit > 0 and not val) or (other_lit < 0 and val)
                    if is_false:
                        # both watched literals false: conflict
                        return False
                    else:
                        # clause is satisfied by other_lit
                        continue
                else:
                    # Unit clause: force other_lit to True
                    if not self.assign_literal(other_lit):
                        return False
                    false2 = -var if other_lit > 0 else var
                    queue.append(false2)

        return True

    # ---------- status & branching ----------

    def check_status(self):
        """
        Check if the formula is SAT, UNSAT, or unknown.
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
                return False  # UNSAT

            any_undecided = True

        if any_undecided:
            return None
        else:
            return True

    def choose_branch_literal(self) -> int | None:
        """
        DSJ heuristic:
        For each *literal* ℓ, compute:

            score(ℓ) = sum_{ℓ in C, C unsatisfied} 1 / 2^{|C|}

        over clauses C that are not yet satisfied and where ℓ's variable is unassigned.
        Return the literal with the highest score, or None if no candidate.
        """
        scores = defaultdict(float)
        assignment = self.assignment

        for clause in self.clauses:
            # Check if clause is already satisfied or completely dead
            clause_satisfied = False
            clause_has_unassigned = False

            for lit in clause:
                var = abs(lit)
                val = assignment[var]

                if val is None:
                    clause_has_unassigned = True
                else:
                    # literal is true under assignment?
                    if (lit > 0 and val) or (lit < 0 and not val):
                        clause_satisfied = True
                        break

            if clause_satisfied or not clause_has_unassigned:
                # Skip clauses that are already satisfied or already impossible
                continue

            # Clause is unsatisfied but has at least one unassigned literal.
            weight = 1.0 / (2 ** len(clause))

            # Add weight to all unassigned literals in this clause
            for lit in clause:
                var = abs(lit)
                val = assignment[var]
                if val is None:
                    scores[lit] += weight

        if not scores:
            return None

        # Pick literal with maximum DSJ score
        best_lit, _ = max(scores.items(), key=lambda kv: kv[1])
        return best_lit

    # ---------- public solve() with instrumentation ----------

    def solve(self):
        """
        Solve the CNF via DPLL.

        Returns:
            dict[int, bool] | None:
                - dict mapping var -> bool if SAT,
                - None if UNSAT.

        Side effects:
            - self.split_count: # of splitting rule applications
            - self.solve_time: elapsed seconds
        """
        # reset per-run state
        self.split_count = 0
        self.solve_time = 0.0
        self.last_propagated = 0
        self.trail.clear()
        self.assignment = [None] * (self.num_vars + 1)

        start = time.perf_counter()

        if not self.propagate():
            self.solve_time = time.perf_counter() - start
            return None

        model = self._solve_rec()

        self.solve_time = time.perf_counter() - start
        return model

    def _solve_rec(self):
        status = self.check_status()
        if status is True:
            return {v: bool(self.assignment[v]) for v in range(1, self.num_vars + 1)}
        elif status is False:
            return None

        # --- DSJ branching: choose best literal ---
        branch_lit = self.choose_branch_literal()
        if branch_lit is None:
            # No unassigned literals but not caught by check_status yet:
            return {v: bool(self.assignment[v]) for v in range(1, self.num_vars + 1)}

        self.split_count += 1  # one splitting rule application here

        # First branch: assign chosen literal to True
        mark = len(self.trail)
        if self.assign_literal(branch_lit) and self.propagate():
            model = self._solve_rec()
            if model is not None:
                return model
        self.undo_to(mark)

        # Second branch: assign its negation
        mark = len(self.trail)
        if self.assign_literal(-branch_lit) and self.propagate():
            model = self._solve_rec()
            if model is not None:
                return model
        self.undo_to(mark)

        return None
