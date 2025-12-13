import random
from array import array
from typing import Iterable, List, Tuple


def flatten_clauses(clauses: List[List[int]]) -> Tuple[array, array]:
    """
    Convert list-of-clauses into flat storage.

    Returns:
        lits: array('i') of all literals concatenated
        offsets: array('I') where clause i is lits[offsets[i]:offsets[i+1]]
    """
    lits = array('i')
    offsets = array('I', [0])

    for c in clauses:
        lits.extend(c)
        offsets.append(len(lits))

    return lits, offsets

def random_3sat_flat(L: int, N: int, seed: int | None = None) -> Tuple[array, array]:
    """
    Generate random 3-SAT in flat form.

    Returns:
        lits: array('i') length 3*L
        offsets: array('I') length L+1, offsets[i] = 3*i
    """
    if N < 3:
        raise ValueError("Need N>=3")
    if L <= 0:
        raise ValueError("Need L>0")

    rng = random.Random(seed)
    lits = array('i')
    offsets = array('I', [0])

    for _ in range(L):
        v1, v2, v3 = rng.sample(range(1, N + 1), 3)
        c = [
            -v1 if rng.random() < 0.5 else v1,
            -v2 if rng.random() < 0.5 else v2,
            -v3 if rng.random() < 0.5 else v3,
        ]
        lits.extend(c)
        offsets.append(len(lits))

    return lits, offsets