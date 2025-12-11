import statistics as stats
import matplotlib.pyplot as plt

from src.fixedModel.FixedLength3Sat import FixedLength3SAT  # adjust path if needed
from src.DPLL.DPLL import DPLL


def run_experiment():
    N_vals = [150, 250]
    ratios = [i / 10 for i in range(30, 62, 2)]  # 3.0, 3.2, ..., 6.0
    num_trials = 100

    # store results as: results[N][ratio] = dict(...)
    results = {N: {} for N in N_vals}

    for N in N_vals:
        for r in ratios:
            L = int(N * r)  # make sure it's an integer

            compute_times = []
            num_splits = []
            failures = 0  # UNSAT count (or however you define "failure")

            for _ in range(num_trials):
                # generate random 3-SAT instance
                generator = FixedLength3SAT(L=L, N=N)
                generator.write_dimacs("random_3sat.cnf")

                # solve
                solver = DPLL("random_3sat.cnf")
                model = solver.solve()

                num_splits.append(solver.split_count)
                compute_times.append(solver.solve_time)

                if model is None:
                    failures += 1

            successes = num_trials - failures
            success_rate = successes / num_trials

            median_time = stats.median(compute_times)
            median_splits = stats.median(num_splits)

            results[N][r] = {
                "median_time": median_time,
                "median_splits": median_splits,
                "success_rate": success_rate,
            }

            print(
                f"N={N}, ratio={r:.1f}: "
                f"median_time={median_time:.6f}s, "
                f"median_splits={median_splits:.1f}, "
                f"success_rate={success_rate:.2f}"
            )

    return results, ratios


def plot_results(results, ratios):
    N_vals = sorted(results.keys())

    # --- 1) Median runtime vs ratio ---
    plt.figure()
    for N in N_vals:
        y = [results[N][r]["median_time"] for r in ratios]
        plt.plot(ratios, y, marker="o", label=f"N={N}")
    plt.xlabel("Clause/Variable ratio (L/N)")
    plt.ylabel("Median runtime (s)")
    plt.title("Median runtime vs clause/variable ratio")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # --- 2) Success rate vs ratio ---
    plt.figure()
    for N in N_vals:
        y = [results[N][r]["success_rate"] for r in ratios]
        plt.plot(ratios, y, marker="o", label=f"N={N}")
    plt.xlabel("Clause/Variable ratio (L/N)")
    plt.ylabel("Success rate (SAT fraction)")
    plt.title("Success rate vs clause/variable ratio")
    plt.legend()
    plt.ylim(-0.05, 1.05)
    plt.grid(True)
    plt.tight_layout()

    # --- 3) Median splits vs ratio ---
    plt.figure()
    for N in N_vals:
        y = [results[N][r]["median_splits"] for r in ratios]
        plt.plot(ratios, y, marker="o", label=f"N={N}")
    plt.xlabel("Clause/Variable ratio (L/N)")
    plt.ylabel("Median number of splits")
    plt.title("Median splitting rule applications vs ratio")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.show()


def main():
    results, ratios = run_experiment()
    plot_results(results, ratios)


if __name__ == "__main__":
    main()
