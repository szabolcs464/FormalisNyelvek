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
                    print(f"Hiba: Érvénytelen elem az átmenetben: '{line}'")
                    return
                transitions[src][sym] = dst

        # 1. Lépés: Elérhető állapotok kigyűjtése (ami nem elérhető, az kuka)
        reachable = {start_state}
        queue = [start_state]
        while queue:
            curr = queue.pop(0)
            for dst in transitions[curr].values():
                if dst not in reachable:
                    reachable.add(dst)
                    queue.append(dst)

        accept_states.intersection_update(reachable)

        # 1.5. Lépés: Részleges DFA kezelése egy virtuális TRAP (csapda) állapottal
        # Ez biztosítja, hogy a Table-filling algoritmus ne omoljon össze hiányzó átmeneteknél.
        has_missing = False
        for s in reachable:
            for sym in alphabet:
                if sym not in transitions[s]:
                    has_missing = True
                    break
        
        eval_states = set(reachable)
        if has_missing:
            eval_states.add("TRAP")
            transitions["TRAP"] = {sym: "TRAP" for sym in alphabet}
            for s in reachable:
                for sym in alphabet:
                    if sym not in transitions[s]:
                        transitions[s][sym] = "TRAP"

        # 2. Lépés: Table-filling algoritmus
        pairs = list(itertools.combinations(eval_states, 2))
        distinguishable = set()

        for p, q in pairs:
            # A TRAP sosem lehet végállapot
            if (p in accept_states) != (q in accept_states):
                distinguishable.add(frozenset([p, q]))

        changed = True
        while changed:
            changed = False
            for p, q in pairs:
                pair = frozenset([p, q])
                if pair not in distinguishable:
                    for sym in alphabet:
                        p_next = transitions[p][sym]
                        q_next = transitions[q][sym]
                        if p_next != q_next:
                            if frozenset([p_next, q_next]) in distinguishable:
                                distinguishable.add(pair)
                                changed = True
                                break

        # 3. Lépés: Ekvivalencia osztályok (összevonható állapotok) kinyerése
        def get_idx(st):
            # Kiszűri a számot a névből (pl. 'q1' -> 1). A TRAP magas értéket kap, hogy sose legyen névadó.
            if st == "TRAP":
                return 999999
            d = ''.join(filter(str.isdigit, st))
            return int(d) if d else 0

        eq_classes = []
        unassigned = set(eval_states)
        while unassigned:
            state = unassigned.pop()
            eq_class = {state}
            for other in list(unassigned):
                if frozenset([state, other]) not in distinguishable:
                    eq_class.add(other)
            unassigned.difference_update(eq_class)
            eq_classes.append(eq_class)

        # Új nevek kiosztása a legkisebb eredeti név alapján
        rep_map = {}
        for eq_class in eq_classes:
            if "TRAP" in eq_class:
                eq_class.remove("TRAP")
            if not eq_class:
                continue
            
            smallest = min(eq_class, key=get_idx)
            new_name = f"s{get_idx(smallest)}"
            for s in eq_class:
                rep_map[s] = new_name

        # 4. Lépés: Az új minimalizált automata felépítése
        out_states = set(rep_map.values())
        out_start = rep_map[start_state]
        out_accepts = set(rep_map[s] for s in accept_states if s in rep_map)
        
        out_transitions = set()
        for s in reachable:
            for sym in alphabet:
                target = transitions[s][sym]
                if target != "TRAP":
                    # Kiszűrjük a duplikációkat a set() használatával, és kihagyjuk az üres (TRAP) éleket.
                    out_transitions.add((rep_map[s], sym, rep_map[target]))

        # 5. Lépés: Szigorú rendezés és fájlba írás
        # Az állapotokat számszerűen rendezzük (s0, s1, s2...)
        sorted_states = sorted(list(out_states), key=get_idx)
        sorted_accepts = sorted(list(out_accepts), key=get_idx)
        
        # A kiírási szabályoknak megfelelően szigorú, szöveges ábécé sorrendbe rakjuk a teljes sort.
        trans_strs = [f"{src} {sym} {dst}" for src, sym, dst in out_transitions]
        trans_strs.sort()

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(" ".join(sorted_states) + "\n")
            f.write(" ".join(alphabet) + "\n")
            f.write(out_start + "\n")
            f.write(" ".join(sorted_accepts) + "\n")
            for t in trans_strs:
                f.write(t + "\n")