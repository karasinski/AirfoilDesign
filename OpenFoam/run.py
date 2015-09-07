from __future__ import division, print_function
from subprocess import call
import argparse


def run_case(foil, alpha):
    call("./Allclean")
    call(["python scripts/NACA2STL.py", foil, alpha])
    call(["./Allrun", foil, alpha])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set the foil angle of attack and log results.")
    parser.add_argument("alpha", type=int, help="Start angle of sweep.")
    parser.add_argument("--foil", "-f", type=str, default="0012", help="Foil")
    args = parser.parse_args()

    run_case(args.foil, args.alpha)
