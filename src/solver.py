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
    model = solver.solve()
    if model is None:
        print("UNSAT")
    else:
        print("SAT with assignment:")
        for var, val in sorted(model.items(), key=lambda x: int(x[0])):
            print(f"{var} = {val}")
            
if __name__ == "__main__":
    main()


        