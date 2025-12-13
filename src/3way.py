import statistics as stats
import matplotlib.pyplot as plt

from src.cnf_flat import random_3sat_flat
from src.DPLL.DPLLFast import DPLLFast


def par10_time(solve_time: float, time_limit: float) -> float:
    return 10.0 * time_limit if solve_time >= time_limit else solve_time


def run_3way_experiment(N_vals, ratios, num_trials=100, time_limit=0.5, base_seed=12345):
    """
    Returns:
      perf[N][r][mode] = PAR10 mean
      aux stats also included
    """
    modes = ["static", "random", "2clause"]
    perf = {N: {r: {} for r in ratios} for N in N_vals}

    for N in N_vals:
        for r in ratios:
            L = int(N * r)

            # per mode accumulators
            par10_sums = {m: 0.0 for m in modes}
            timeouts = {m: 0 for m in modes}

            for t in range(num_trials):
                # fixed seed so each mode sees *exactly* the same instance
                seed = base_seed + (N * 10_000) + int(r * 100) * 1000 + t
                lits, offsets = random_3sat_flat(L=L, N=N, seed=seed)

                for mode in modes:
                    solver = DPLLFast(lits, offsets, num_vars=N)
                    model = solver.solve(time_limit=time_limit, branch_mode=mode, seed=seed + 999)

                    par10_sums[mode] += par10_time(solver.solve_time, time_limit)
                    if solver.solve_time >= time_limit:
                        timeouts[mode] += 1

            for mode in modes:
                perf[N][r][mode] = {
                    "par10_mean": par10_sums[mode] / num_trials,
                    "timeout_rate": timeouts[mode] / num_trials,
                    "L": L,
                }

            print(
                f"N={N} r={r:.1f} | "
                f"PAR10 static={perf[N][r]['static']['par10_mean']:.4f} "
                f"random={perf[N][r]['random']['par10_mean']:.4f} "
                f"2cl={perf[N][r]['2clause']['par10_mean']:.4f}",
                flush=True
            )

    return perf


def plot_ratio_curves(perf, N_vals, ratios):
    """
    Plots:
      (static/random) and (static/2clause) ratio vs L/N
    Lower is better (static faster).
    """
    plt.figure()
    for N in N_vals:
        y_sr = []
        y_s2 = []
        for r in ratios:
            s = perf[N][r]["static"]["par10_mean"]
            rnd = perf[N][r]["random"]["par10_mean"]
            two = perf[N][r]["2clause"]["par10_mean"]
            y_sr.append(s / rnd if rnd > 0 else float("nan"))
            y_s2.append(s / two if two > 0 else float("nan"))

        plt.plot(ratios, y_sr, marker="o", label=f"N={N}: static/random")
        plt.plot(ratios, y_s2, marker="o", label=f"N={N}: static/2clause")

    plt.axhline(1.0)  # equal performance reference
    plt.xlabel("L/N")
    plt.ylabel("PAR-10 ratio (lower = better)")
    plt.title("Performance ratio vs clause/variable ratio")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    N_vals = [85, 110]               # or whatever you want
    ratios = [i / 10 for i in range(30, 62, 2)]  # 3.0..6.0 step 0.2

    perf = run_3way_experiment(
        N_vals=N_vals,
        ratios=ratios,
        num_trials=100,
        time_limit=2,
        base_seed=12345
    )

    plot_ratio_curves(perf, N_vals, ratios)


if __name__ == "__main__":
    main()
