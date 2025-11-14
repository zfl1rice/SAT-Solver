from ..CNF.CNF import CNF
from collections import Counter
import heapq
from copy import deepcopy

class DPLL:
    def __init__(self, dimacsFile):
        """
        Initialize a DPLL instance from a DIMACS CNF file.

        Args:
            dimacs_path (str): Path to a DIMACS file.
        """
        self.cnf = CNF(dimacsFile)

        self.unitClauses = []

        self.varFreqs = Counter()   # var -> count
        self._heap = []             # max-heap via (-freq, var)
        self.assigned = set()       # vars that have been set True/False

        # Initialize varFreqs and heap from the starting CNF
        for clause in self.getCNFList():
            for lit in clause:
                var = lit[1:] if lit.startswith("¬") else lit
                self._inc_var_freq(var)
            if len(clause) == 1:
                self.unitClauses.append(clause)

        pos = set()
        neg = set()
        for clause in self.getCNFList():
            for lit in clause:
                if lit.startswith("¬"):
                    neg.add(lit[1:])
                else:
                    pos.add(lit)

        self.pures = []
        for v in pos ^ neg:  # variables that appear in exactly one of pos/neg
            # add the actual literal, not the var name:
            if v in pos and v not in neg:
                self.pures.append(v)        # pure positive
            elif v in neg and v not in pos:
                self.pures.append("¬" + v)  # pure negative


    def _inc_var_freq(self, var, amount=1):
        """Increase frequency of var and push updated entry into heap."""
        self.varFreqs[var] += amount
        heapq.heappush(self._heap, (-self.varFreqs[var], var))

    def _dec_var_freq(self, var, amount=1):
        """Decrease frequency of var and push updated entry into heap."""
        self.varFreqs[var] -= amount
        if self.varFreqs[var] < 0:
            self.varFreqs[var] = 0
        # Push new (freq, var); old entries become 'stale' and will be skipped.
        heapq.heappush(self._heap, (-self.varFreqs[var], var))

    def choose_most_frequent_var(self):
        """
        Return the currently most frequent unassigned variable using a max-heap.

        Uses lazy updates: the heap may contain stale entries, which are
        skipped until we find one whose frequency matches varFreqs[var]
        and is not already assigned.

        Returns:
            str | None: variable name like "p", or None if no candidate exists.
        """
        while self._heap:
            neg_freq, var = heapq.heappop(self._heap)
            current_freq = self.varFreqs.get(var, 0)

            # Skip stale entries or vars with freq 0 or already assigned
            if current_freq == 0 or var in self.assigned or -neg_freq != current_freq:
                continue

            return var

        return None  # no unassigned vars left

    def getCNFList(self):
        return self.cnf.getCNFList()
    
    def checkSat(self):
        cnf_list = self.getCNFList()

        if not cnf_list:
            return True  # SAT

        for clause in cnf_list:
            if not clause:
                return False  # UNSAT

        return None
    
    def simplify(self, prop, value):
        """
        Returns:
            bool: False if UNSAT was detected (empty clause),
                True otherwise (keep going).
        """
        self.assigned.add(prop)
        curr = self.getCNFList()

        full_prop = prop if value else f'¬{prop}'
        opp = f'¬{prop}' if value else prop

        new = []
        for clause in curr:
            if full_prop in clause:
                for lit in clause:
                    var = lit[1:] if lit.startswith("¬") else lit
                    self._dec_var_freq(var, 1)
                continue

            reduced = []
            for lit in clause:
                if lit == opp:
                    var = lit[1:] if lit.startswith("¬") else lit
                    self._dec_var_freq(var, 1)
                else:
                    reduced.append(lit)

            if not reduced:
                return False

            if len(reduced) == 1:
                self.unitClauses.append(reduced)

            new.append(reduced)

        # Don't detect SAT here; just update CNF
        self.cnf.setCNFList(new)
        return True
    
    def solve(self):
        """
        Run the DPLL algorithm on this CNF instance.

        Returns:
            bool: True if the formula is satisfiable, False otherwise.
        """
        return self._solve_from_state()

    # ---------- Core recursive DPLL ----------

    def _solve_from_state(self):
        """
        Recursive DPLL solver working on the current internal state.

        Returns:
            bool: True if SAT from this state, False if UNSAT.
        """

        # --- Unit propagation ---
        u = self.unitClauses
        while u:
            curr_lit = u.pop()[0]   # ["p"] or ["¬p"] -> "p"/"¬p"

            if curr_lit.startswith("¬"):
                var = curr_lit[1:]
                val = False
            else:
                var = curr_lit
                val = True

            sat = self.simplify(var, val)
            if not sat:
                # simplify already found UNSAT
                return False

        # --- Pure literal elimination ---
        for pure in self.pures:
            if pure.startswith("¬"):
                var = pure[1:]
                val = False
            else:
                var = pure
                val = True

            sat = self.simplify(var, val)
            if not sat:
                return False

        # --- Check SAT/UNSAT at this node ---
        status = self.checkSat()
        if status is True:
            return True
        elif status is False:
            return False
        # else: unknown, need to branch

        # --- Choose branching variable ---
        next_var = self.choose_most_frequent_var()

        if next_var is None:
            # No variables left; if we got here, be defensive and say SAT
            print("SAT")
            return True

        # --- Branch: next_var = True ---
        left = deepcopy(self)
        if left.simplify(next_var, True):
            if left._solve_from_state():
                return True

        # --- Branch: next_var = False ---
        right = deepcopy(self)
        if right.simplify(next_var, False):
            if right._solve_from_state():
                return True

        # Both branches failed => UNSAT under current path
        return False

    

def main():
    cnf_str = "(p ∨ q) ∧ (¬p ∨ r)"
    solver = DPLL(cnf_str)
    is_sat = solver.solve()
    print("Result:", "SAT" if is_sat else "UNSAT")
    
            
if __name__ == "__main__":
    main()



"""
DPLL(F):
  F := simplify(F)            // remove satisfied clauses, delete false literals
  if F has an empty clause: return UNSAT
  if F has no clauses: return SAT

  // Unit propagation
  while F has a unit clause (ℓ):
    assign(ℓ); F := simplify(F)
    if F has an empty clause: return UNSAT

  // Pure literal elimination
  for each variable v that is pure in F:
    assign(pure literal of v); F := simplify(F)

  if F has no clauses: return SAT
  if all vars assigned: return SAT

  // Branch
  x := choose_unassigned_variable(F)
  return DPLL(F ∧ x) OR DPLL(F ∧ ¬x)
"""