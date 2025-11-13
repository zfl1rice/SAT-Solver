from CNF.CNF import CNF

class DPLL:
    """
    A thin wrapper around a CNF parser/object that exposes minimal
    DPLL-style operations. Currently this class stores a CNF instance,
    can read/replace it, and provides a very simple "simplify" step.

    Expected CNF format (delegated to CNF class):
      - Unicode logic symbols: '∧' (AND), '∨' (OR), '¬' (NOT)
      - Clauses delimited by parentheses, e.g. (p ∨ q)
      - Parsed CNF list shape: List[List[str]], each literal is like "p" or "¬p"

    Example:
        dpll = DPLL("(p ∨ q) ∧ (¬p ∨ r)")
        clauses = dpll.getCNFList()
        dpll.simplify("p", True)
    """

    def __init__(self, CNFString):
        """
        Initialize a DPLL instance with a CNF string.

        Args:
            CNFString (str): A CNF formula string using Unicode symbols,
                e.g. "(p ∨ q) ∧ (¬p ∨ r)".

        Side Effects:
            - Constructs and stores a CNF object parsed from the given string.
        """
        self.cnf = CNF(CNFString)

    def getCNFList(self):
        """
        Return the underlying CNF as a list of clauses.

        Returns:
            list[list[str]]: The parsed CNF representation, where each clause
            is a list of literal strings (e.g., ["p", "¬q"]).

        Notes:
            - This simply forwards to CNF.getCNFList().
        """
        out = self.cnf.getCNFList()
        return out
    
    def setCNFString(self, new_CNF):
        """
        Replace the current CNF with a new one, given as a string.

        Args:
            new_CNF (str): A CNF formula string using Unicode symbols,
                e.g. "(p ∨ q) ∧ (¬p ∨ r)".

        Side Effects:
            - Replaces the internal CNF object by parsing the new string.

        Notes:
            - This discards any previous CNF list state and reparses from scratch.
        """
        self.cnf = CNF(new_CNF)

    def setCNFList(self, new_CNF):
        """
        Replace the current CNF with a new list-of-clauses representation.

        Args:
            new_CNF (list[list[str]]): CNF as list of clauses, where each clause
                is a list of literals like "p" or "¬p".

        Side Effects:
            - Assigns the provided list into the underlying CNF object.
        """
        self.cnf.setCNFList(new_CNF)

    def simplify(self, prop, value):
        """
        Simplify the CNF under the assignment prop = value.

        - Clauses containing the satisfied literal are removed.
        - The opposite literal is removed from remaining clauses.
        - If any clause becomes empty, the formula is UNSAT.

        Args:
            prop (str): Variable name without negation, e.g. "p".
            value (bool): Assigned truth value for `prop`.
                        True  -> satisfied literal is "p", opposite is "¬p"
                        False -> satisfied literal is "¬p", opposite is "p"
        """
        curr = self.getCNFList()

        full_prop = prop if value else f'¬{prop}'   # satisfied literal
        opp = f'¬{prop}' if value else prop         # opposite literal to remove

        new = []
        for clause in curr:
            # If clause is satisfied by the assignment, drop it
            if full_prop in clause:
                continue

            # Otherwise, remove the opposite literal from the clause
            reduced = [lit for lit in clause if lit != opp]

            # Empty clause => contradiction under this assignment
            if not reduced:
                print("UNSAT")
                return False

            new.append(reduced)

        print("Successfully simplified")
        print(new)
        self.cnf.setCNFList(new)
        return True

