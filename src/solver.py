import statistics as stats
import math
import matplotlib.pyplot as plt

from src.cnf_flat import random_3sat_flat
from src.DPLL.DPLLFast import DPLLFast


def pilot_time_limit(N, r, pilot_trials=30, start_limit=0.5, max_limit=30.0, grow=2.0):
    """
    Pick a time limit so that fewer than 50% of pilot instances time out.
    This helps ensure the *median of solved times* isn't dominated by timeouts,
    and avoids the median being clipped to the timeout value.

    Returns:
        float: chosen time limit in seconds
    """
    limit = start_limit
    L = int(N * r)

    while limit <= max_limit:
        timeouts = 0
        times = []

        for _ in range(pilot_trials):
            lits, offsets = random_3sat_flat(L=L, N=N, seed=None)
            solver = DPLLFast(lits, offsets, num_vars=N)
            solver.solve(time_limit=limit)
            times.append(solver.solve_time)
            if solver.solve_time >= limit:
                timeouts += 1

        timeout_rate = timeouts / pilot_trials

        # Condition: fewer than half time out
        if timeout_rate < 0.5:
            return limit

        limit *= grow

    return max_limit


def run_experiment():
    N_vals = [100, 125]
    ratios = [i / 10 for i in range(30, 62, 2)]  # 3.0..6.0 step 0.2
    num_trials = 100
    tl = 5.0
    results = {N: {} for N in N_vals}

    for N in N_vals:

        for r in ratios:
            # tl = pilot_time_limit(N, r, pilot_trials=30, start_limit=0.5, max_limit=30.0, grow=2.0)
            L = int(N * r)

            sats = 0
            unsats = 0
            timeouts = 0

            solved_times = []
            solved_splits = []

            par10_times = []

            for t in range(num_trials):
                lits, offsets = random_3sat_flat(L=L, N=N, seed=None)

                solver = DPLLFast(lits, offsets, num_vars=N)
                model = solver.solve(time_limit=tl)

                # PAR-10 accounting
                if solver.solve_time >= tl:
                    par10_times.append(10.0 * tl)
                else:
                    par10_times.append(solver.solve_time)

                if model is None and solver.solve_time >= tl:
                    timeouts += 1
                elif model is None:
                    unsats += 1
                    solved_times.append(solver.solve_time)
                    solved_splits.append(solver.split_count)
                else:
                    sats += 1
                    solved_times.append(solver.solve_time)
                    solved_splits.append(solver.split_count)

                # if (t + 1) % 10 == 0:
                #     print(f"  r={r:.1f} trial {t+1}/{num_trials}", flush=True)

            solved = sats + unsats
            solved_rate = solved / num_trials
            timeout_rate = timeouts / num_trials
            sat_rate_among_solved = (sats / solved) if solved > 0 else float("nan")

            median_time_solved = stats.median(solved_times) if solved_times else float("nan")
            median_splits_solved = stats.median(solved_splits) if solved_splits else float("nan")
            par10_mean = (sum(par10_times) / len(par10_times)) if par10_times else float("nan")

            results[N][r] = {
                "time_limit": tl,
                "median_time_solved": median_time_solved,
                "median_splits_solved": median_splits_solved,
                "solved_rate": solved_rate,
                "timeout_rate": timeout_rate,
                "sat_rate_among_solved": sat_rate_among_solved,
                "par10_mean": par10_mean,
                "sats": sats,
                "unsats": unsats,
                "timeouts": timeouts,
            }

            print(
                f"N={N}, r={r:.1f}, L={L}, tl={tl:.2f}s | "
                f"median(solved)={median_time_solved:.4f}s, "
                f"PAR10_mean={par10_mean:.4f}s, "
                f"timeout_rate={timeout_rate:.2f}, solved_rate={solved_rate:.2f}, "
                f"SAT|solved={sat_rate_among_solved:.2f}",
                flush=True
            )

    return results, ratios


def plot_results(results, ratios):
    N_vals = sorted(results.keys())

    # Median solved runtime
    plt.figure()
    for N in N_vals:
        y = [results[N][r]["median_time_solved"] for r in ratios]
        plt.plot(ratios, y, marker="o", label=f"N={N}")
    plt.xlabel("L/N")
    plt.ylabel("Median runtime (solved only) [s]")
    plt.title("Median solved runtime vs clause/variable ratio")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Timeout rate
    plt.figure()
    for N in N_vals:
        y = [results[N][r]["timeout_rate"] for r in ratios]
        plt.plot(ratios, y, marker="o", label=f"N={N}")
    plt.xlabel("L/N")
    plt.ylabel("Timeout rate")
    plt.title("Timeout rate vs clause/variable ratio")
    plt.ylim(-0.05, 1.05)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # PAR-10 mean
    plt.figure()
    for N in N_vals:
        y = [results[N][r]["par10_mean"] for r in ratios]
        plt.plot(ratios, y, marker="o", label=f"N={N}")
    plt.xlabel("L/N")
    plt.ylabel("PAR-10 mean time [s]")
    plt.title("PAR-10 mean vs clause/variable ratio")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.show()


def main():
    results, ratios = run_experiment()
    plot_results(results, ratios)


if __name__ == "__main__":
    main()
