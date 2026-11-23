from project.problem import Problem
import argparse
import os
import re

class Hazi4(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--rgx', help='Regex feladat sorszáma (1-5)', type=int)

    def is_chosen_problem(self, args):
        return args.rgx is not None

    def run(self, args):
        if not os.path.exists(args.input):
            print("A bemeneti fájl nem található.")
            return

        with open(args.input, 'r', encoding='utf-8') as f:
            lines = [re.sub(r'[\r\n]+$', '', line) for line in f]

        if args.rgx == 1:
            patterns = [
                re.compile(r'^10-15 '),
                re.compile(r'^10-15 10:18:51\.'),
                re.compile(r'^[0-9-]+ [0-9]{2}:[0-9]{2}:51\.'),
                re.compile(r'^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ [IDVEFAW] lowmemorykiller\s*:'),
                re.compile(r'^[0-9-]+ 10:18:51\.[0-9]+ +221 +[0-9]+ '),
                re.compile(r'^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ E '),
                re.compile(r'^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ W PackageManager\s*:'),
                re.compile(r'^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ D [^:]*ExoPlayer[^:]*:'),
                re.compile(r'^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ [EW] .+?\.java:[0-9]+'),
                re.compile(r'^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ [IDVEFAW] .+?:.*\bThread\b')
            ]
            counts = [sum(1 for line in lines if p.search(line)) for p in patterns]
            with open(args.output, 'w', encoding='utf-8') as f:
                for c in counts:
                    f.write(f"{c}\n")

        elif args.rgx == 2:
            err_msg_re = re.compile(r'^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ E .+?: (.*)$')
            java_file_re = re.compile(r'([A-Za-z0-9_$]+\.java):[0-9]+')
            results = []
            for line in lines:
                m = err_msg_re.search(line)
                if m:
                    results.extend(java_file_re.findall(m.group(1)))
            with open(args.output, 'w', encoding='utf-8') as f:
                for res in results:
                    f.write(f"{res}\n")

        elif args.rgx == 3:
            pid_re = re.compile(r'^[0-9-]+ [0-9:.]+ +([0-9]+) +[0-9]+ [IDVEFAW] .+?:')
            seen = set()
            pids = []
            for line in lines:
                m = pid_re.search(line)
                if m:
                    pid = m.group(1)
                    if pid not in seen:
                        seen.add(pid)
                        pids.append(pid)
            with open(args.output, 'w', encoding='utf-8') as f:
                for pid in pids:
                    f.write(f"{pid}\n")

        elif args.rgx == 4:
            err_pid_re = re.compile(r'^[0-9-]+ [0-9:.]+ +([0-9]+) +[0-9]+ E ')
            error_counts = {}
            for line in lines:
                m = err_pid_re.search(line)
                if m:
                    pid = m.group(1)
                    error_counts[pid] = error_counts.get(pid, 0) + 1
            with open(args.output, 'w', encoding='utf-8') as f:
                if error_counts:
                    max_pid, max_count = max(error_counts.items(), key=lambda x: x[1])
                    f.write(f"PID={max_pid} ({max_count} errors)\n")

        elif args.rgx == 5:
            main_err_re = re.compile(r'^[0-9-]+ [0-9:.]+ +([0-9]+) +\1 E ')
            count = sum(1 for line in lines if main_err_re.search(line))
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(f"{count}\n")