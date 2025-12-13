import re
import math
import matplotlib.pyplot as plt

LINE_RE = re.compile(
    r"N=(?P<N>\d+),\s*r=(?P<r>\d+(?:\.\d+)?),\s*L=(?P<L>\d+),\s*tl=(?P<tl>\d+(?:\.\d+)?)s\s*\|\s*"
    r"median\(solved\)=(?P<median>\d+(?:\.\d+)?)s,\s*"
    r"PAR10_mean=(?P<par10>\d+(?:\.\d+)?)s,\s*"
    r"timeout_rate=(?P<to>\d+(?:\.\d+)?),\s*"
    r"solved_rate=(?P<solved>\d+(?:\.\d+)?),\s*"
    r"SAT\|solved=(?P<sat>\d+(?:\.\d+)?)"
)

def parse_results_from_text(text: str):
    """
    Parse printed solver output into results[N][r] dict.
    """
    results = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = LINE_RE.search(line)
        if not m:
            continue

        N = int(m.group("N"))
        r = float(m.group("r"))

        results.setdefault(N, {})
        results[N][r] = {
            "L": int(m.group("L")),
            "time_limit": float(m.group("tl")),
            "median_time_solved": float(m.group("median")),
            "par10_mean": float(m.group("par10")),
            "timeout_rate": float(m.group("to")),
            "solved_rate": float(m.group("solved")),
            "sat_rate_among_solved": float(m.group("sat")),
        }
    return results


def plot_results(results):
    N_vals = sorted(results.keys())
    ratios = sorted({r for N in results for r in results[N].keys()})

    def series(N, key):
        return [results[N].get(r, {}).get(key, math.nan) for r in ratios]

    # Median solved runtime
    plt.figure()
    for N in N_vals:
        plt.plot(ratios, series(N, "median_time_solved"), marker="o", label=f"N={N}")
    plt.xlabel("L/N")
    plt.ylabel("Median runtime (solved only) [s]")
    plt.title("Median solved runtime vs clause/variable ratio")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # PAR10 mean
    plt.figure()
    for N in N_vals:
        plt.plot(ratios, series(N, "par10_mean"), marker="o", label=f"N={N}")
    plt.xlabel("L/N")
    plt.ylabel("PAR-10 mean [s]")
    plt.title("PAR-10 mean vs clause/variable ratio")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Timeout rate
    plt.figure()
    for N in N_vals:
        plt.plot(ratios, series(N, "timeout_rate"), marker="o", label=f"N={N}")
    plt.xlabel("L/N")
    plt.ylabel("Timeout rate")
    plt.ylim(-0.05, 1.05)
    plt.title("Timeout rate vs clause/variable ratio")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Solved rate
    plt.figure()
    for N in N_vals:
        plt.plot(ratios, series(N, "solved_rate"), marker="o", label=f"N={N}")
    plt.xlabel("L/N")
    plt.ylabel("Solved rate")
    plt.ylim(-0.05, 1.05)
    plt.title("Solved rate vs clause/variable ratio")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # SAT among solved
    plt.figure()
    for N in N_vals:
        plt.plot(ratios, series(N, "sat_rate_among_solved"), marker="o", label=f"N={N}")
    plt.xlabel("L/N")
    plt.ylabel("SAT fraction among solved")
    plt.ylim(-0.05, 1.05)
    plt.title("SAT fraction among solved vs clause/variable ratio")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Time limit used
    plt.figure()
    for N in N_vals:
        plt.plot(ratios, series(N, "time_limit"), marker="o", linestyle="--", label=f"N={N}")
    plt.xlabel("L/N")
    plt.ylabel("Time limit used [s]")
    plt.title("Time limit vs ratio")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    text = r"""
N=100, r=3.0, L=300, tl=5.00s | median(solved)=0.0007s, PAR10_mean=0.0007s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=1.00
N=100, r=3.2, L=320, tl=5.00s | median(solved)=0.0007s, PAR10_mean=0.0007s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=1.00
N=100, r=3.4, L=340, tl=5.00s | median(solved)=0.0007s, PAR10_mean=0.0041s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=1.00
N=100, r=3.6, L=360, tl=5.00s | median(solved)=0.0007s, PAR10_mean=0.0034s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=1.00
N=100, r=3.8, L=380, tl=5.00s | median(solved)=0.0011s, PAR10_mean=0.0192s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=1.00
N=100, r=4.0, L=400, tl=5.00s | median(solved)=0.0038s, PAR10_mean=0.7047s, timeout_rate=0.01, solved_rate=0.99, SAT|solved=0.93
N=100, r=4.2, L=420, tl=5.00s | median(solved)=0.0372s, PAR10_mean=1.8327s, timeout_rate=0.03, solved_rate=0.97, SAT|solved=0.69
N=100, r=4.4, L=440, tl=5.00s | median(solved)=0.4790s, PAR10_mean=1.7579s, timeout_rate=0.02, solved_rate=0.98, SAT|solved=0.34
N=100, r=4.6, L=459, tl=5.00s | median(solved)=0.3299s, PAR10_mean=1.6298s, timeout_rate=0.02, solved_rate=0.98, SAT|solved=0.14
N=100, r=4.8, L=480, tl=5.00s | median(solved)=0.2827s, PAR10_mean=0.9968s, timeout_rate=0.01, solved_rate=0.99, SAT|solved=0.04
N=100, r=5.0, L=500, tl=5.00s | median(solved)=0.2647s, PAR10_mean=0.4163s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=0.01
N=100, r=5.2, L=520, tl=5.00s | median(solved)=0.1888s, PAR10_mean=0.3130s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=0.00
N=100, r=5.4, L=540, tl=5.00s | median(solved)=0.1009s, PAR10_mean=0.1603s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=0.00
N=100, r=5.6, L=560, tl=5.00s | median(solved)=0.0866s, PAR10_mean=0.1413s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=0.00
N=100, r=5.8, L=580, tl=5.00s | median(solved)=0.0594s, PAR10_mean=0.0813s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=0.00
N=100, r=6.0, L=600, tl=5.00s | median(solved)=0.0358s, PAR10_mean=0.0567s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=0.00
N=125, r=3.0, L=375, tl=5.00s | median(solved)=0.0017s, PAR10_mean=0.0019s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=1.00
N=125, r=3.2, L=400, tl=5.00s | median(solved)=0.0013s, PAR10_mean=0.0016s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=1.00
N=125, r=3.4, L=425, tl=5.00s | median(solved)=0.0014s, PAR10_mean=0.0019s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=1.00
N=125, r=3.6, L=450, tl=5.00s | median(solved)=0.0015s, PAR10_mean=0.0162s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=1.00
N=125, r=3.8, L=475, tl=5.00s | median(solved)=0.0034s, PAR10_mean=1.6150s, timeout_rate=0.03, solved_rate=0.97, SAT|solved=1.00
N=125, r=4.0, L=500, tl=5.00s | median(solved)=0.0234s, PAR10_mean=9.7219s, timeout_rate=0.17, solved_rate=0.83, SAT|solved=1.00
N=125, r=4.2, L=525, tl=5.00s | median(solved)=0.0367s, PAR10_mean=22.7184s, timeout_rate=0.44, solved_rate=0.56, SAT|solved=0.96
N=125, r=4.4, L=550, tl=5.00s | median(solved)=0.2271s, PAR10_mean=33.3534s, timeout_rate=0.66, solved_rate=0.34, SAT|solved=0.68
N=125, r=4.6, L=575, tl=5.00s | median(solved)=1.6433s, PAR10_mean=27.4251s, timeout_rate=0.53, solved_rate=0.47, SAT|solved=0.13
N=125, r=4.8, L=600, tl=5.00s | median(solved)=1.8532s, PAR10_mean=24.6342s, timeout_rate=0.47, solved_rate=0.53, SAT|solved=0.02
N=125, r=5.0, L=625, tl=5.00s | median(solved)=1.9060s, PAR10_mean=10.6401s, timeout_rate=0.18, solved_rate=0.82, SAT|solved=0.00
N=125, r=5.2, L=650, tl=5.00s | median(solved)=1.1776s, PAR10_mean=5.8553s, timeout_rate=0.09, solved_rate=0.91, SAT|solved=0.00
N=125, r=5.4, L=675, tl=5.00s | median(solved)=0.9131s, PAR10_mean=5.0931s, timeout_rate=0.08, solved_rate=0.92, SAT|solved=0.00
N=125, r=5.6, L=700, tl=5.00s | median(solved)=0.4657s, PAR10_mean=1.7476s, timeout_rate=0.02, solved_rate=0.98, SAT|solved=0.00
N=125, r=5.8, L=725, tl=5.00s | median(solved)=0.2656s, PAR10_mean=0.4565s, timeout_rate=0.00, solved_rate=1.00, SAT|solved=0.00
N=125, r=6.0, L=750, tl=5.00s | median(solved)=0.2636s, PAR10_mean=0.9351s, timeout_rate=0.01, solved_rate=0.99, SAT|solved=0.00
"""

    results = parse_results_from_text(text)
    print("Parsed Ns:", sorted(results.keys()))
    for N in sorted(results.keys()):
        print(f"N={N}: parsed {len(results[N])} ratios")

    plot_results(results)
