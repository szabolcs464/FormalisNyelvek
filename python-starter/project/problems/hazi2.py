from project.problem import Problem
import argparse
import os

class Hazi2(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        # A --det flag hozzáadása a feladatkiírás szerint
        parser.add_argument('--det', action='store_true', help='Automatát determinizál')

    def is_chosen_problem(self, args):
        # Akkor fut le ez a feladat, ha a --det kapcsoló be van kapcsolva
        return args.det

    def run(self, args):
        if not os.path.exists(args.input):
            print("A bemeneti fájl nem található.")
            return

        with open(args.input, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 4:
            print("Érvénytelen bemeneti formátum.")
            return

        # 1. Bemenet feldolgozása
        states = set(lines[0].split())
        alphabet_list = lines[1].split()
        start_state = lines[2]
        accept_states = set(lines[3].split())

        # NFA átmenetek tárolója
        nfa = {s: {a: set() for a in alphabet_list} for s in states}

        # 2. Alapvető hibakezelés és átmenetek beolvasása
        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                src, sym, dst = parts
                # Ellenőrizzük, hogy a megadott állapotok és jelek érvényesek-e
                if src not in states or sym not in alphabet_list or dst not in states:
                    print(f"Hiba: Érvénytelen elem az átmenetben: '{line}'")
                    return
                nfa[src][sym].add(dst)

        # 3. Determinizálás (Részhalmaz konstrukció BFS algoritmussal)
        start_subset = tuple(sorted([start_state]))
        
        dfa_states = [start_subset]  # A felfedezett új állapotok (list of tuples)
        queue = [start_subset]       # A még feldolgozásra váró állapotok
        dfa_transitions = []         # Tároló az (src_idx, sym, dst_idx) átmeneteknek

        while queue:
            curr_subset = queue.pop(0)
            src_idx = dfa_states.index(curr_subset)

            for sym in alphabet_list:
                next_states = set()
                # Összeszedjük, hogy a jelenlegi halmazból adott szimbólummal hova juthatunk
                for q in curr_subset:
                    next_states.update(nfa[q][sym])

                if not next_states:
                    continue  # Ahol nincs átmenet, ott nem listázzuk

                dst_subset = tuple(sorted(list(next_states)))
                
                # Ha új részhalmazt találtunk, felvesszük a listába és a várólistába
                if dst_subset not in dfa_states:
                    dfa_states.append(dst_subset)
                    queue.append(dst_subset)

                dst_idx = dfa_states.index(dst_subset)
                dfa_transitions.append((src_idx, sym, dst_idx))

        # 4. Kimeneti formázás és sorba rendezés
        # Sorrend: csomópontok szerint, él címkéje szerint, célállomás szerint
        dfa_transitions.sort(key=lambda t: (t[0], t[1], t[2]))

        out_states = [f"s{i}" for i in range(len(dfa_states))]
        out_start = "s0"
        
        # Egy új állapot akkor elfogadó, ha tartalmaz legalább egy eredeti elfogadó állapotot
        out_accepts = []
        for i, subset in enumerate(dfa_states):
            if any(q in accept_states for q in subset):
                out_accepts.append(f"s{i}")

        # 5. Fájlba írás
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(" ".join(out_states) + "\n")
            f.write(" ".join(alphabet_list) + "\n")
            f.write(out_start + "\n")
            f.write(" ".join(out_accepts) + "\n")
            for src, sym, dst in dfa_transitions:
                f.write(f"s{src} {sym} s{dst}\n")