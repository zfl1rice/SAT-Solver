import time
from array import array
from collections import defaultdict
import random

from src.dpll_cy.core import propagate_watched


class DPLLFast:
    """
    Flat CNF + offsets + watched literals, with Cython propagation.
    Iterative DFS (no recursion).
    """

    def __init__(self, lits: array, offsets: array, num_vars: int):
        self.lits = lits
        self.offsets = offsets
        self.num_vars = num_vars
        self.num_clauses = len(offsets) - 1

        # assignment: 0 unassigned, +1 true, -1 false
        self.assign = array('b', [0]) * (self.num_vars + 1)
        self.trail = array('i')  # stack of assigned vars
        self.trail_start = 0

        # watched literal positions: absolute indices into self.lits
        self.wpos1 = array('i', [0]) * self.num_clauses
        self.wpos2 = array('i', [0]) * self.num_clauses

        # watchlists as linked lists over nodes (lazy)
        # literal index in [0..2n] via lit + n
        self.head = array('i', [-1]) * (2 * self.num_vars + 1)
        self.node_clause = array('i')
        self.node_next = array('i')
        self.node_lit = array('i')

        self._init_watches()

        # stats
        self.split_count = 0
        self.solve_time = 0.0

        # static literal count heuristic (cheap)
        self.lit_count = defaultdict(int)
        for L in self.lits:
            self.lit_count[L] += 1
        self._all_lits = list(self.lit_count.keys())

    def _lit_index(self, lit: int) -> int:
        return lit + self.num_vars

    def _add_watch_node(self, lit: int, ci: int):
        node_id = len(self.node_clause)
        self.node_clause.append(ci)
        self.node_lit.append(lit)
        self.node_next.append(self.head[self._lit_index(lit)])
        self.head[self._lit_index(lit)] = node_id

    def _init_watches(self):
        for ci in range(self.num_clauses):
            s = self.offsets[ci]
            e = self.offsets[ci + 1]
            if e - s <= 0:
                self.wpos1[ci] = s
                self.wpos2[ci] = s
                continue
            if e - s == 1:
                self.wpos1[ci] = s
                self.wpos2[ci] = s
                lit = self.lits[s]
                self._add_watch_node(lit, ci)
                self._add_watch_node(lit, ci)
            else:
                self.wpos1[ci] = s
                self.wpos2[ci] = s + 1
                self._add_watch_node(self.lits[s], ci)
                self._add_watch_node(self.lits[s + 1], ci)

    def _choose_branch_lit(self, mode: str, rng: random.Random) -> int | None:
        if mode == "random":
            return self._choose_branch_lit_random(rng)
        if mode == "2clause":
            lit = self._choose_branch_lit_2clause()
            if lit is not None:
                return lit
            # fallback if no 2-clauses exist right now
            return self._choose_branch_lit_static()
        # default: your current heuristic
        return self._choose_branch_lit_static()

    def _choose_branch_lit_static(self) -> int | None:
        """Your existing cheap static literal-count heuristic."""
        best_lit = None
        best = -1
        a = self.assign
        for lit in self._all_lits:
            v = lit if lit > 0 else -lit
            if a[v] != 0:
                continue
            c = self.lit_count[lit]
            if c > best:
                best = c
                best_lit = lit
        return best_lit

    def _choose_branch_lit_random(self, rng: random.Random) -> int | None:
        """Pick an unassigned variable uniformly at random, then random polarity."""
        unassigned_vars = []
        a = self.assign
        for v in range(1, self.num_vars + 1):
            if a[v] == 0:
                unassigned_vars.append(v)
        if not unassigned_vars:
            return None
        v = rng.choice(unassigned_vars)
        # random polarity
        return v if rng.random() < 0.5 else -v

    def _choose_branch_lit_2clause(self) -> int | None:
        """
        2-clause heuristic:
        Find any clause that is not yet satisfied and has exactly 2 unassigned literals.
        Choose a literal from those (tie-break using your lit_count).
        """
        a = self.assign
        best_lit = None
        best_score = -1

        # scan all clauses in flat representation
        for ci in range(self.num_clauses):
            s = self.offsets[ci]
            e = self.offsets[ci + 1]

            # check if clause is already satisfied, and count unassigned lits
            unassigned = []
            satisfied = False

            for k in range(s, e):
                lit = self.lits[k]
                v = lit if lit > 0 else -lit
                av = a[v]

                if av == 0:
                    unassigned.append(lit)
                    # small early stop: if >2, not a 2-clause candidate
                    if len(unassigned) > 2:
                        break
                else:
                    # is lit true?
                    if (lit > 0 and av == 1) or (lit < 0 and av == -1):
                        satisfied = True
                        break

            if satisfied:
                continue
            if len(unassigned) != 2:
                continue

            # choose between the two literals using static literal count as a proxy score
            for lit in unassigned:
                score = self.lit_count.get(lit, 0)
                if score > best_score:
                    best_score = score
                    best_lit = lit

        return best_lit

    def _assign_lit(self, lit: int) -> bool:
        v = lit if lit > 0 else -lit
        want = 1 if lit > 0 else -1
        cur = self.assign[v]
        if cur != 0:
            return cur == want
        self.assign[v] = want
        self.trail.append(v)
        return True

    def _undo_to(self, mark: int):
        while len(self.trail) > mark:
            v = self.trail.pop()
            self.assign[v] = 0
        if self.trail_start > mark:
            self.trail_start = mark

    def solve(self, time_limit: float | None = None, branch_mode: str = "static", seed: int | None = None):

        """
        Solve with an optional time limit.

        Args:
            time_limit (float | None): Maximum wall-clock seconds to spend on this instance.
                If None, no time limit is enforced.

        Returns:
            dict[int, bool] | None:
                - model if SAT
                - None if UNSAT or TIMEOUT (you can track timeout separately if desired)
        """
        self.split_count = 0
        self.solve_time = 0.0
        self.assign = array('b', [0]) * (self.num_vars + 1)
        self.trail = array('i')
        self.trail_start = 0
        rng = random.Random(seed)
        start = time.perf_counter()
        next_check = 1024  # check time every ~1024 loop iterations (cheap)

        stack = []  # (branch_lit, trail_mark, flipped)
        steps = 0

        while True:
            steps += 1

            # --- time limit check (amortized) ---
            if time_limit is not None and steps >= next_check:
                next_check += 1024
                if (time.perf_counter() - start) > time_limit:
                    self.solve_time = time.perf_counter() - start
                    return None  # TIMEOUT

            ok, new_ts = propagate_watched(
                self.num_vars,
                self.lits, self.offsets,
                self.wpos1, self.wpos2,
                self.head,
                self.node_clause, self.node_next, self.node_lit,
                self.assign,
                self.trail,
                self.trail_start
            )
            self.trail_start = new_ts

            if not ok:
                # backtrack
                while stack:
                    branch_lit, mark, flipped = stack.pop()
                    self._undo_to(mark)

                    if not flipped:
                        # try opposite branch
                        stack.append((branch_lit, mark, True))
                        if self._assign_lit(-branch_lit):
                            break
                else:
                    # UNSAT
                    self.solve_time = time.perf_counter() - start
                    return None

                continue

            # --- optional cheap SAT stop: all vars assigned ---
            # (This is cheaper than scanning all clauses each loop.)
            # If you prefer, keep your clause-scan SAT check instead.
            #
            # If all variables are assigned, it's SAT (no conflict so far).
            all_assigned = True
            for v in range(1, self.num_vars + 1):
                if self.assign[v] == 0:
                    all_assigned = False
                    break

            if all_assigned:
                self.solve_time = time.perf_counter() - start
                return {v: (self.assign[v] == 1) for v in range(1, self.num_vars + 1)}

            # choose branch
            branch_lit = self._choose_branch_lit(branch_mode, rng)
            if branch_lit is None:
                # No branchable literal -> treat as SAT
                self.solve_time = time.perf_counter() - start
                return {v: (self.assign[v] == 1) for v in range(1, self.num_vars + 1)}

            self.split_count += 1
            mark = len(self.trail)
            stack.append((branch_lit, mark, False))

            # first branch
            self._assign_lit(branch_lit)
