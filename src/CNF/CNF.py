class CNF:
    """
    A simple parser for CNF (Conjunctive Normal Form) formulas written with Unicode logic symbols.

    The expected input format uses:
      - '∧' for AND between clauses
      - '∨' for OR within a clause
      - '¬' for negation
      - Parentheses to delimit each clause: e.g., (p ∨ q) ∧ (¬p ∨ r)

    Example:
        cnf = CNF("(p ∨ q) ∧ (¬p ∨ r) ∧ (r ∨ q) ∧ (¬r)")
        cnf.getCNFString()  # -> the original string
        cnf.getCNFList()    # -> [['p', 'q'], ['¬p', 'r'], ['r', 'q'], ['¬r']]

    Notes / limitations:
      - Variables are assumed to be single-character symbols (e.g., p, q, r).
      - Clauses are recognized when a closing parenthesis ')' is encountered.
      - Spaces are ignored; characters '∧', '∨', '(', and ' ' are treated as separators.
      - Negation '¬' applies only to the next single-character variable.
    """
    def __init__(self, dimacsFile: str):
        """
        Initialize the CNF object from a DIMACS CNF file.

        Args:
            dimacsFile (str): Path to a DIMACS CNF file. The file should
                follow the standard format:
                    c ...         (comments)
                    p cnf N M     (problem line: N vars, M clauses)
                    <lits> 0      (clauses, literals as ints ending with 0)

        Attributes:
            CNFList (list[list[str]]): Parsed CNF as a list of clauses, where each
                clause is a list of literal strings; positive literals are like
                "3", negative literals are like "¬3".
            numVars (int): Number of variables declared in the header.
            numClauses (int): Number of clauses declared in the header.

        Notes:
            - This assumes each clause is contained on a single line.
            - It ignores comment lines starting with 'c'.
        """
        self.CNFList = []
        self.numVars = 0
        self.numClauses = 0

        with open(dimacsFile, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue  # skip empty lines

                if line.startswith('c'):
                    continue  # comment

                if line.startswith('p'):
                    # Example: "p cnf 5 10"
                    header = line.split()
                    # header[0] = 'p', header[1] = 'cnf', header[2] = numVars, header[3] = numClauses
                    self.numVars = int(header[2])
                    self.numClauses = int(header[3])
                    continue

                # Clause line
                tokens = line.split()
                temp = []
                for tok in tokens:
                    if tok == '0':
                        break  # end of this clause
                    if tok.startswith('-'):
                        temp.append("¬" + tok[1:])
                    else:
                        temp.append(tok)
                if temp:
                    self.CNFList.append(temp)



    def getCNFString(self) -> str:
        """
        Return the original CNF string.

        Returns:
            str: The exact CNF string provided at initialization.
        """
        return self.CNFString

    def getCNFList(self) -> list[list[str]]:
        """
        Return the parsed CNF as a list of clauses.

        Each clause is represented as a list of literal strings, where a literal is either
        a variable like "p" or its negation like "¬p".

        Returns:
            list[list[str]]: The CNF as a list of clauses. Example:
                [['p', 'q'], ['¬p', 'r'], ['r', 'q'], ['¬r']]
        """
        return self.CNFList
    
    def setCNFList(self, newList):
        """
        Replace the internal CNF list with a new value.

        Args:
            newList (list[list[str]]): CNF as a list of clauses,
                where each clause is a list of literal strings
                (e.g., "p", "¬p").
        """
        self.CNFList = newList