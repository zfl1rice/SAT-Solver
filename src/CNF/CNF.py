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

    def __init__(self, CNFString: str):
        """
        Initialize the CNF object and immediately parse the input string.

        Args:
            CNFString (str): The CNF formula as a string using Unicode symbols
                (e.g., "(p ∨ q) ∧ (¬p ∨ r)").

        Attributes:
            CNFString (str): Stores the original CNF string.
            CNFList (list[list[str]]): Parsed CNF as a list of clauses, where each
                clause is a list of literal strings (e.g., "p", "¬p").

        Side Effects:
            Populates self.CNFList by calling convertToList().
        """
        self.CNFString = CNFString
        self.CNFList = []

        self.convertToList()

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


    def convertToList(self) -> None:
        """
        Parse the stored CNF string into a list-of-lists representation.

        Parsing rules:
          - Ignores spaces and the characters '∧', '∨', and '('.
          - When encountering ')', the current clause (if any) is appended to CNFList.
          - The negation marker '¬' applies to the next single-character variable only.
          - Variables are assumed to be single characters (e.g., 'p', 'q', 'r').

        Populates:
            self.CNFList (list[list[str]]): Updated in place with the parsed clauses.

        Example:
            For "(p ∨ q) ∧ (¬p ∨ r) ∧ (r ∨ q) ∧ (¬r)",
            self.CNFList becomes [['p', 'q'], ['¬p', 'r'], ['r', 'q'], ['¬r']]

        Limitations:
            - Multi-character variable names are not supported by this parser.
            - Missing or mismatched parentheses will lead to partial or incorrect parsing.
        """
        t = set(['∨', '∧', '(', ' '])
        out = []
        neg = False
        for i in self.CNFString:
            if i == ')':
                # End of a clause: append collected literals (if any) and reset.
                if out:
                    self.CNFList.append(out)
                out = []
            elif i not in t:
                if i == '¬':
                    # Mark next variable as negated.
                    neg = True
                else:
                    # Treat as a variable (single character).
                    if neg:
                        out.append('¬' + i)
                        neg = False
                    else:
                        out.append(i)
