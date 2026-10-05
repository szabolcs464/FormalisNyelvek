from project.problem import Problem
import argparse
import os

class Hazi1(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--check', help='Ellenőrizendő szavak vesszővel elválasztva', type=str)

    def is_chosen_problem(self, args):
        return args.check is not None

    def run(self, args):
        if not os.path.exists(args.input):
            print("A bemeneti fájl nem található.")
            return

        with open(args.input, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 4:
            print("A bemeneti fájl formátuma érvénytelen.")
            return

        alphabet = set(lines[1].split())
        start_state = lines[2]
        accept_states = set(lines[3].split())

        transitions = {}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                src, sym, dst = parts
                transitions.setdefault(src, {})[sym] = dst

        def evaluate_word(word):
            current_state = start_state
            for char in word:
                if char not in alphabet or char not in transitions.get(current_state, {}):
                    return "NEM"
                current_state = transitions[current_state][char]
            
            return "IGEN" if current_state in accept_states else "NEM"

        with open(args.output, 'w', encoding='utf-8') as f:
            for word in args.check.split(','):
                res = evaluate_word(word)
                f.write(f"{res}\n")