def buildMap(all):
    res = {}
    idx = 1 
    for category in all:
        for value in category:
            for house in range(1, 6): 
                name = f"{value}_{house}"
                res[name] = idx
                idx += 1
    return res

def writePair(f, c1, c2):
    """Write clause: ¬c1 ∨ c2"""
    f.write(f"-{c1} {c2} 0\n")


def writeSolo(f, c1):
    """Write clause: c1"""
    f.write(f"{c1} 0\n")


def writeTriplet(f, c1, c2, c3):
    """Write clause: ¬c1 ∨ c2 ∨ c3"""
    f.write(f"-{c1} {c2} {c3} 0\n")


def writeNegSolo(f, c1):
    """Write clause: ¬c1"""
    f.write(f"-{c1} 0\n")


def writeNextTo(f, encoding, sym1, sym2):
    """
    Encode: sym1@i → sym2 at a neighboring house.
    """
    # House 1: sym1_1 → sym2_2
    writePair(f, encoding[f"{sym1}_1"], encoding[f"{sym2}_2"])

    # House 5: sym1_5 → sym2_4
    writePair(f, encoding[f"{sym1}_5"], encoding[f"{sym2}_4"])

    # Houses 2..4: sym1_i → (sym2_{i-1} ∨ sym2_{i+1})
    for i in range(2, 5):
        writeTriplet(
            f,
            encoding[f"{sym1}_{i}"],
            encoding[f"{sym2}_{i-1}"],
            encoding[f"{sym2}_{i+1}"],
        )

def writeHints(f, encoding):

    # independent hints
    writeSolo(f, encoding["norwegian_1"])
    writeSolo(f, encoding["milk_3"])

    # same-house hints
    for i in range(1, 6):
        writePair(f, encoding[f"brit_{i}"],        encoding[f"red_{i}"])
        writePair(f, encoding[f"swede_{i}"],       encoding[f"dog_{i}"])
        writePair(f, encoding[f"dane_{i}"],        encoding[f"tea_{i}"])
        writePair(f, encoding[f"green_{i}"],       encoding[f"coffee_{i}"])
        writePair(f, encoding[f"pallmall_{i}"],    encoding[f"birds_{i}"])
        writePair(f, encoding[f"yellow_{i}"],      encoding[f"dunhill_{i}"])
        writePair(f, encoding[f"bluemasters_{i}"], encoding[f"beer_{i}"])
        writePair(f, encoding[f"german_{i}"],      encoding[f"prince_{i}"])

    # positional: green immediately left of white
    for i in range(1, 5):
        writePair(f, encoding[f"green_{i}"], encoding[f"white_{i+1}"])
    writeNegSolo(f, encoding["green_5"])

    # lives-next-to hints
    writeNextTo(f, encoding, "blends",    "cats")
    writeNextTo(f, encoding, "horse",     "dunhill")
    writeNextTo(f, encoding, "norwegian", "blue")
    writeNextTo(f, encoding, "blends",    "water")


def writeExclusives(f, encoding, all):
    for house in range(1, 6):  # houses 1..5
        for category in all:
            lits = [encoding[f"{value}_{house}"] for value in category]

            f.write(" ".join(str(v) for v in lits) + " 0\n")

            for i in range(len(lits)):
                for j in range(i + 1, len(lits)):
                    f.write(f"-{lits[i]} -{lits[j]} 0\n")

    for category in all:
        for value in category:
            lits = [encoding[f"{value}_{house}"] for house in range(1, 6)]

            f.write(" ".join(str(v) for v in lits) + " 0\n")

            for i in range(len(lits)):
                for j in range(i + 1, len(lits)):
                    f.write(f"-{lits[i]} -{lits[j]} 0\n")



def main():
    file = "puzzle.txt"

    colors = ['red','green', 'white','blue', 'yellow']
    nats   = ['brit','swede','norwegian','dane','german']
    drinks = ['coffee','tea','beer','water','milk']
    cigars = ['pallmall','blends','dunhill','bluemasters','prince']
    pets   = ['cats','birds','horse','fish','dog']
    all_categories = [colors, nats, drinks, cigars, pets]

    encoding = buildMap(all_categories)
    numVars = len(encoding)

    # For now, we don't know numClauses ahead of time; you can either
    # count as you write, or write a dummy header and fix it later.
    with open(file, "w", encoding="utf-8") as f:
        # temporary header; you can update numClauses once you count them
        f.write(f"p cnf {numVars} 0\n")

        # write exclusives
        writeExclusives(f, encoding, all_categories)

        # write all hint clauses
        writeHints(f, encoding)

            
if __name__ == "__main__":
    main()