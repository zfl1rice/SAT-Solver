# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True

from array import array
cimport cython

@cython.cfunc
@cython.inline
cdef int lit_index(int lit, int nvars) nogil:
    # map literal in [-n..-1, 1..n] to [0..2n]
    # index = lit + nvars  (works because lit != 0)
    return lit + nvars

@cython.cfunc
@cython.inline
cdef bint lit_is_false(int lit, signed char[:] assign) nogil:
    cdef int v = lit if lit > 0 else -lit
    cdef signed char a = assign[v]
    if a == 0:
        return False
    if lit > 0:
        return a == -1
    else:
        return a == 1

@cython.cfunc
@cython.inline
cdef bint lit_is_true(int lit, signed char[:] assign) nogil:
    cdef int v = lit if lit > 0 else -lit
    cdef signed char a = assign[v]
    if a == 0:
        return False
    if lit > 0:
        return a == 1
    else:
        return a == -1

@cython.cfunc
@cython.inline
cdef int lit_var(int lit) nogil:
    return lit if lit > 0 else -lit

@cython.cfunc
@cython.inline
cdef signed char lit_value(int lit) nogil:
    # desired assignment for var to make lit true:
    # lit>0 -> +1, lit<0 -> -1
    return 1 if lit > 0 else -1


def propagate_watched(
    int nvars,
    int[:] lits,           # flat literals
    unsigned int[:] off,   # offsets length m+1

    int[:] wpos1,          # watched positions (absolute indices into lits)
    int[:] wpos2,

    int[:] head,           # head per literal index (size 2*nvars+1), -1 if empty

    object node_clause,    # Python array('i'): node -> clause id
    object node_next,      # Python array('i'): node -> next node
    object node_lit,       # Python array('i'): node -> watched literal value

    signed char[:] assign, # 0 unassigned, +1 true, -1 false
    object trail,          # Python array('i'): stack of assigned vars (var ids)
    int trail_start        # start index in trail to propagate from
):
    """
    Watched-literal unit propagation with *lazy* watchlists.

    Returns:
      (ok: bool, new_trail_start: int)
    """
    cdef int qhead = 0
    cdef int qtail = 0
    cdef int tlen = len(trail)
    cdef int qcap = (tlen - trail_start) + 8

    # queue as Python array, plus fast memoryview over it
    cdef object py_queue = array('i', [0]) * qcap
    cdef int[:] q = py_queue

    cdef int ti, v, false_lit, idx
    cdef int node, ci
    cdef unsigned int s, e
    cdef int p1, p2, lit1, lit2, other_pos, other_lit, false_pos
    cdef int k, L, newpos
    cdef bint moved
    cdef signed char need
    cdef int node_id

    # enqueue false literals from new assignments
    for ti in range(trail_start, tlen):
        v = trail[ti]
        if assign[v] == 1:
            false_lit = -v
        else:
            false_lit = v
        q[qtail] = false_lit
        qtail += 1

    # process queue
    while qhead < qtail:
        false_lit = q[qhead]
        qhead += 1

        idx = lit_index(false_lit, nvars)
        node = head[idx]
        while node != -1:
            ci = node_clause[node]

            # skip stale watch nodes
            if node_lit[node] != false_lit:
                node = node_next[node]
                continue

            # fetch watched positions and literals
            p1 = wpos1[ci]
            p2 = wpos2[ci]
            lit1 = lits[p1]
            lit2 = lits[p2]

            # determine which watch is the false one
            if lit1 == false_lit:
                false_pos = p1
                other_pos = p2
                other_lit = lit2
            elif lit2 == false_lit:
                false_pos = p2
                other_pos = p1
                other_lit = lit1
            else:
                # stale node
                node = node_next[node]
                continue

            # If other watch is already true, clause satisfied
            if lit_is_true(other_lit, assign):
                node = node_next[node]
                continue

            # Try to find replacement literal not false
            s = off[ci]
            e = off[ci + 1]
            moved = False
            for k in range(s, e):
                if k == other_pos or k == false_pos:
                    continue
                L = lits[k]
                if not lit_is_false(L, assign):
                    newpos = k
                    if false_pos == p1:
                        wpos1[ci] = newpos
                    else:
                        wpos2[ci] = newpos

                    # append NEW watch node for L (lazy)
                    node_clause.append(ci)
                    node_lit.append(L)
                    node_next.append(head[lit_index(L, nvars)])

                    node_id = len(node_clause) - 1
                    head[lit_index(L, nvars)] = node_id

                    moved = True
                    break

            if moved:
                node = node_next[node]
                continue

            # no replacement => unit or conflict based on other_lit
            if lit_is_false(other_lit, assign):
                return (False, len(trail))  # conflict

            # If other_lit unassigned, force it
            v = lit_var(other_lit)
            if assign[v] == 0:
                need = lit_value(other_lit)
                assign[v] = need
                trail.append(v)

                # enqueue its false literal
                if need == 1:
                    q[qtail] = -v
                else:
                    q[qtail] = v
                qtail += 1

            node = node_next[node]

    return (True, len(trail))