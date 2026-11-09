from project.problem import Problem
import argparse
import os
import itertools

class Hazi3(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--mini', action='store_true', help='Automatát minimalizál')

    def is_chosen_problem(self, args):
        return args.mini

    def run(self, args):
        if not os.path.exists(args.input):
            print("A bemeneti fájl nem található.")
            return

        with open(args.input, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 4:
            print("Érvénytelen bemeneti formátum.")
            return

        states = set(lines[0].split())
        alphabet = lines[1].split()
        start_state = lines[2]
        accept_states = set(lines[3].split())

        transitions = {s: {} for s in states}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                src, sym, dst = parts
                if src not in states or sym not in alphabet or dst not in states:
                    print(f"Hiba: Érvénytelen elem: '{line}'")
                    return
                transitions[src][sym] = dst

        # 1. Elérhető állapotok meghatározása (felesleg kiszűrése)
        reachable = {start_state}
        queue = [start_state]
        while queue:
            curr = queue.pop(0)
            for dst in transitions[curr].values():
                if dst not in reachable:
                    reachable.add(dst)
                    queue.append(dst)

        states = reachable
        accept_states.intersection_update(states)

        # 2. Table-filling algoritmus (megkülönböztethető állapotok keresése)
        pairs = list(itertools.combinations(states, 2))
        distinguishable = set()

        for p, q in pairs:
            if (p in accept_states) != (q in accept_states):
                distinguishable.add(frozenset([p, q]))

        changed = True
        while changed:
            changed = False
            for p, q in pairs:
                pair = frozenset([p, q])
                if pair not in distinguishable:
                    for sym in alphabet:
                        p_next = transitions[p].get(sym)
                        q_next = transitions[q].get(sym)
                        
                        if p_next and q_next and p_next != q_next:
                            if frozenset([p_next, q_next]) in distinguishable:
                                distinguishable.add(pair)
                                changed = True
                                break
                        elif (p_next is None) != (q_next is None):
                            distinguishable.add(pair)
                            changed = True
                            break

        # 3. Összevonható állapotok csoportosítása és átnevezése
        def get_idx(st):
            d = ''.join(filter(str.isdigit, st))
            return int(d) if d else 0

        eq_classes = []
        unassigned = set(states)
        while unassigned:
            state = unassigned.pop()
            eq_class = {state}
            for other in list(unassigned):
                if frozenset([state, other]) not in distinguishable:
                    eq_class.add(other)
            unassigned.difference_update(eq_class)
            eq_classes.append(eq_class)

        rep_map = {}
        for eq_class in eq_classes:
            smallest = min(eq_class, key=get_idx)
            new_name = f"s{get_idx(smallest)}"
            for s in eq_class:
                rep_map[s] = new_name

        # 4. Új automata összeállítása
        out_states = set(rep_map.values())
        out_start = rep_map[start_state]
        out_accepts = set(rep_map[s] for s in accept_states)
        out_transitions = set()

        for s in states:
            for sym in alphabet:
                if sym in transitions[s]:
                    out_transitions.add((rep_map[s], sym, rep_map[transitions[s][sym]]))

        # 5. Rendezés és kiírás
        sorted_states = sorted(list(out_states), key=get_idx)
        sorted_accepts = sorted(list(out_accepts), key=get_idx)
        sorted_trans = sorted(list(out_transitions), key=lambda t: (t[0], t[1], t[2]))

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(" ".join(sorted_states) + "\n")
            f.write(" ".join(alphabet) + "\n")
            f.write(out_start + "\n")
            f.write(" ".join(sorted_accepts) + "\n")
            for src, sym, dst in sorted_trans:
                f.write(f"{src} {sym} {dst}\n")