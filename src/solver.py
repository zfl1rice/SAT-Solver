from src.DPLL.DPLL import DPLL


# class randomBenchmark:
#     def __init__(self, CNF, seed = None):
#         self.seed = None
#         if seed:
#             self.seed = seed
#         self.CNF = CNF
   
# Assuming that CNF is stored in a string following formula rules


def main():

    solver = DPLL("input.txt")
    is_sat = solver.solve()
    print("Result:", "SAT" if is_sat else "UNSAT")
            
if __name__ == "__main__":
    main()


        