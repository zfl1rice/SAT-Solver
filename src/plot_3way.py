import re
import math
import matplotlib.pyplot as plt


LINE_RE = re.compile(
    r"N=(?P<N>\d+)\s+"
    r"r=(?P<r>\d+(?:\.\d+)?)\s+\|\s+"
    r"PAR10\s+"
    r"static=(?P<static>\d+(?:\.\d+)?)\s+"
    r"random=(?P<random>\d+(?:\.\d+)?)\s+"
    r"2cl=(?P<two>\d+(?:\.\d+)?)"
)

def parse_threeway_from_text(text: str):
    """
    Returns:
      data[N][r] = {"static": avg, "random": avg, "two": avg, "count": k}
    If the same (N,r) appears multiple times, values are averaged.
    """
    # temp accumulator: data[N][r] -> [sum_static, sum_random, sum_two, count]
    acc = {}

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = LINE_RE.search(line)
        if not m:
            continue

        N = int(m.group("N"))
        r = float(m.group("r"))
        s = float(m.group("static"))
        rnd = float(m.group("random"))
        two = float(m.group("two"))

        acc.setdefault(N, {})
        if r not in acc[N]:
            acc[N][r] = [0.0, 0.0, 0.0, 0]
        acc[N][r][0] += s
        acc[N][r][1] += rnd
        acc[N][r][2] += two
        acc[N][r][3] += 1

    # finalize averages
    data = {}
    for N in acc:
        data[N] = {}
        for r, (ss, rr, tt, k) in acc[N].items():
            data[N][r] = {
                "static": ss / k,
                "random": rr / k,
                "two": tt / k,
                "count": k,
            }

    return data


def plot_par10(data):
    """Plot PAR10 curves for static/random/2cl."""
    if not data:
        print("No lines parsed.")
        return

    N_vals = sorted(data.keys())
    ratios = sorted({r for N in data for r in data[N].keys()})

    plt.figure()
    for N in N_vals:
        ys = [data[N].get(r, {}).get("static", math.nan) for r in ratios]
        yr = [data[N].get(r, {}).get("random", math.nan) for r in ratios]
        y2 = [data[N].get(r, {}).get("two", math.nan) for r in ratios]

        plt.plot(ratios, ys, marker="o", label=f"N={N} static")
        plt.plot(ratios, yr, marker="o", label=f"N={N} random")
        plt.plot(ratios, y2, marker="o", label=f"N={N} 2cl")

    plt.xlabel("L/N")
    plt.ylabel("PAR-10 mean time [s]")
    plt.title("PAR-10 mean vs clause/variable ratio")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_ratio_curves(data):
    """
    Plot ratios:
      static/random and static/2cl vs L/N
    (Lower is better for static.)
    """
    if not data:
        print("No lines parsed.")
        return

    N_vals = sorted(data.keys())
    ratios = sorted({r for N in data for r in data[N].keys()})

    plt.figure()
    for N in N_vals:
        y_sr = []
        y_s2 = []
        for r in ratios:
            row = data[N].get(r)
            if row is None:
                y_sr.append(math.nan)
                y_s2.append(math.nan)
                continue

            s = row["static"]
            rnd = row["random"]
            two = row["two"]

            y_sr.append(s / rnd if rnd > 0 else math.nan)
            y_s2.append(s / two if two > 0 else math.nan)

        plt.plot(ratios, y_sr, marker="o", label=f"N={N}: static/random")
        plt.plot(ratios, y_s2, marker="o", label=f"N={N}: static/2cl")

    plt.axhline(1.0)
    plt.xlabel("L/N")
    plt.ylabel("PAR-10 ratio (lower = better)")
    plt.title("Performance ratios vs clause/variable ratio")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    text = r"""
N=85 r=3.0 | PAR10 static=0.0006 random=0.0063 2cl=0.0051 
N=85 r=3.2 | PAR10 static=0.0006 random=0.0332 2cl=0.0050 
N=85 r=3.4 | PAR10 static=0.0009 random=0.6955 2cl=0.0056 
N=85 r=3.6 | PAR10 static=0.0037 random=2.1531 2cl=0.0062 
N=85 r=3.8 | PAR10 static=0.0147 random=3.7554 2cl=0.0206 
N=85 r=4.0 | PAR10 static=0.0540 random=9.0567 2cl=0.0580 
N=85 r=4.2 | PAR10 static=0.2955 random=13.5789 2cl=0.0888 
N=85 r=4.4 | PAR10 static=0.1479 random=16.3210 2cl=0.1278 
N=85 r=4.6 | PAR10 static=0.1078 random=17.8753 2cl=0.1082 
N=85 r=4.8 | PAR10 static=0.0901 random=16.6572 2cl=0.0970 
N=85 r=5.0 | PAR10 static=0.0757 random=13.0895 2cl=0.0804 
N=85 r=5.2 | PAR10 static=0.0412 random=3.9340 2cl=0.0623 
N=85 r=5.4 | PAR10 static=0.0288 random=1.2163 2cl=0.0536 
N=85 r=5.6 | PAR10 static=0.0264 random=0.6092 2cl=0.0458 
N=85 r=5.8 | PAR10 static=0.0198 random=0.3528 2cl=0.0405 
N=85 r=6.0 | PAR10 static=0.0137 random=0.2395 2cl=0.0333 
N=110 r=3.0 | PAR10 static=0.0011 random=0.6578 2cl=0.0086 
N=110 r=3.2 | PAR10 static=0.0011 random=0.6974 2cl=0.0101 
N=110 r=3.4 | PAR10 static=0.0021 random=2.2265 2cl=0.0091 
N=110 r=3.6 | PAR10 static=0.0065 random=4.9765 2cl=0.0181 
N=85 r=5.0 | PAR10 static=0.0757 random=13.0895 2cl=0.0804 
N=85 r=5.2 | PAR10 static=0.0412 random=3.9340 2cl=0.0623 
N=85 r=5.4 | PAR10 static=0.0288 random=1.2163 2cl=0.0536 
N=85 r=5.6 | PAR10 static=0.0264 random=0.6092 2cl=0.0458 
N=85 r=5.8 | PAR10 static=0.0198 random=0.3528 2cl=0.0405 
N=85 r=6.0 | PAR10 static=0.0137 random=0.2395 2cl=0.0333 
N=110 r=3.0 | PAR10 static=0.0011 random=0.6578 2cl=0.0086 
N=110 r=3.2 | PAR10 static=0.0011 random=0.6974 2cl=0.0101 
N=110 r=3.4 | PAR10 static=0.0021 random=2.2265 2cl=0.0091 
N=110 r=3.6 | PAR10 static=0.0065 random=4.9765 2cl=0.0181 
N=110 r=3.8 | PAR10 static=0.2542 random=12.3316 2cl=0.0637 
N=110 r=4.0 | PAR10 static=2.3558 random=14.9436 2cl=1.3657 
N=85 r=5.4 | PAR10 static=0.0288 random=1.2163 2cl=0.0536 
N=85 r=5.6 | PAR10 static=0.0264 random=0.6092 2cl=0.0458 
N=85 r=5.8 | PAR10 static=0.0198 random=0.3528 2cl=0.0405 
N=85 r=6.0 | PAR10 static=0.0137 random=0.2395 2cl=0.0333 
N=110 r=3.0 | PAR10 static=0.0011 random=0.6578 2cl=0.0086 
N=110 r=3.2 | PAR10 static=0.0011 random=0.6974 2cl=0.0101 
N=110 r=3.4 | PAR10 static=0.0021 random=2.2265 2cl=0.0091 
N=110 r=3.6 | PAR10 static=0.0065 random=4.9765 2cl=0.0181 
N=110 r=3.8 | PAR10 static=0.2542 random=12.3316 2cl=0.0637 
N=110 r=4.0 | PAR10 static=2.3558 random=14.9436 2cl=1.3657 
N=85 r=5.8 | PAR10 static=0.0198 random=0.3528 2cl=0.0405 
N=85 r=6.0 | PAR10 static=0.0137 random=0.2395 2cl=0.0333 
N=110 r=3.0 | PAR10 static=0.0011 random=0.6578 2cl=0.0086 
N=110 r=3.2 | PAR10 static=0.0011 random=0.6974 2cl=0.0101 
N=110 r=3.4 | PAR10 static=0.0021 random=2.2265 2cl=0.0091 
N=110 r=3.6 | PAR10 static=0.0065 random=4.9765 2cl=0.0181 
N=110 r=3.8 | PAR10 static=0.2542 random=12.3316 2cl=0.0637 
N=110 r=4.0 | PAR10 static=2.3558 random=14.9436 2cl=1.3657 
N=110 r=4.2 | PAR10 static=7.7965 random=18.2544 2cl=2.8559 
N=110 r=4.4 | PAR10 static=7.9670 random=19.0280 2cl=3.9587 
N=110 r=3.0 | PAR10 static=0.0011 random=0.6578 2cl=0.0086 
N=110 r=3.2 | PAR10 static=0.0011 random=0.6974 2cl=0.0101 
N=110 r=3.4 | PAR10 static=0.0021 random=2.2265 2cl=0.0091 
N=110 r=3.6 | PAR10 static=0.0065 random=4.9765 2cl=0.0181 
N=110 r=3.8 | PAR10 static=0.2542 random=12.3316 2cl=0.0637 
N=110 r=4.0 | PAR10 static=2.3558 random=14.9436 2cl=1.3657 
N=110 r=4.2 | PAR10 static=7.7965 random=18.2544 2cl=2.8559 
N=110 r=4.4 | PAR10 static=7.9670 random=19.0280 2cl=3.9587 
N=110 r=3.4 | PAR10 static=0.0021 random=2.2265 2cl=0.0091 
N=110 r=3.6 | PAR10 static=0.0065 random=4.9765 2cl=0.0181 
N=110 r=3.8 | PAR10 static=0.2542 random=12.3316 2cl=0.0637 
N=110 r=4.0 | PAR10 static=2.3558 random=14.9436 2cl=1.3657 
N=110 r=4.2 | PAR10 static=7.7965 random=18.2544 2cl=2.8559 
N=110 r=4.4 | PAR10 static=7.9670 random=19.0280 2cl=3.9587 
N=110 r=4.6 | PAR10 static=6.4730 random=19.6179 2cl=2.9776 
N=110 r=3.8 | PAR10 static=0.2542 random=12.3316 2cl=0.0637 
N=110 r=4.0 | PAR10 static=2.3558 random=14.9436 2cl=1.3657 
N=110 r=4.2 | PAR10 static=7.7965 random=18.2544 2cl=2.8559 
N=110 r=4.4 | PAR10 static=7.9670 random=19.0280 2cl=3.9587 
N=110 r=4.6 | PAR10 static=6.4730 random=19.6179 2cl=2.9776 
N=110 r=4.2 | PAR10 static=7.7965 random=18.2544 2cl=2.8559 
N=110 r=4.4 | PAR10 static=7.9670 random=19.0280 2cl=3.9587 
N=110 r=4.6 | PAR10 static=6.4730 random=19.6179 2cl=2.9776 
N=110 r=4.8 | PAR10 static=4.5173 random=20.0000 2cl=1.1591 
N=110 r=4.6 | PAR10 static=6.4730 random=19.6179 2cl=2.9776 
N=110 r=4.8 | PAR10 static=4.5173 random=20.0000 2cl=1.1591 
N=110 r=5.0 | PAR10 static=1.7093 random=20.0000 2cl=0.4233 
N=110 r=4.8 | PAR10 static=4.5173 random=20.0000 2cl=1.1591 
N=110 r=5.0 | PAR10 static=1.7093 random=20.0000 2cl=0.4233 
N=110 r=5.2 | PAR10 static=0.7687 random=20.0000 2cl=0.4841 
N=110 r=5.4 | PAR10 static=0.5192 random=20.0000 2cl=0.2547 
N=110 r=5.0 | PAR10 static=1.7093 random=20.0000 2cl=0.4233 
N=110 r=5.2 | PAR10 static=0.7687 random=20.0000 2cl=0.4841 
N=110 r=5.4 | PAR10 static=0.5192 random=20.0000 2cl=0.2547 
N=110 r=5.6 | PAR10 static=0.2437 random=19.8158 2cl=0.2041 
N=110 r=5.2 | PAR10 static=0.7687 random=20.0000 2cl=0.4841 
N=110 r=5.4 | PAR10 static=0.5192 random=20.0000 2cl=0.2547 
N=110 r=5.6 | PAR10 static=0.2437 random=19.8158 2cl=0.2041 
N=110 r=5.4 | PAR10 static=0.5192 random=20.0000 2cl=0.2547 
N=110 r=5.6 | PAR10 static=0.2437 random=19.8158 2cl=0.2041 
N=110 r=5.6 | PAR10 static=0.2437 random=19.8158 2cl=0.2041 
N=110 r=5.8 | PAR10 static=0.1437 random=19.8160 2cl=0.1574 
N=110 r=6.0 | PAR10 static=0.1173 random=18.8859 2cl=0.1342
"""

    data = parse_threeway_from_text(text)

    print("Parsed Ns:", sorted(data.keys()))
    for N in sorted(data.keys()):
        rs = sorted(data[N].keys())
        print(f"N={N}: {len(rs)} unique ratios parsed")
        # show how many duplicates got averaged for a couple points
        for r in rs[:3]:
            print(f"  r={r:.1f} averaged over {data[N][r]['count']} lines")

    plot_par10(data)
    plot_ratio_curves(data)
