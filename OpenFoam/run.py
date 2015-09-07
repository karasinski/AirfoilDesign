from __future__ import division, print_function
from subprocess import call
import argparse
import os
import time
import numpy as np


def run_case(foil, alpha):
    # Clean and run case
    call("./Allclean")
    call(["python",  "scripts/NACA2STL.py", foil, str(alpha)])
    call(["./Allrun"])

    # Save data
    output_dir = os.getcwd() + '/output/' + foil + '/' + str(alpha)
    data = os.getcwd() + '/airfoil_pimpleFoam/'
    os.makedirs(output_dir)
    time.sleep(1)
    cmds = ['cp', '-r', data, output_dir]
    call(cmds)


def param_sweep(foil, start, stop, step):
    alphas = np.arange(start, stop, step)

    for alpha in alphas:
        print("Running foil {}, alpha {}".format(foil, alpha))
        run_case(foil, alpha)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set the foil angle of attack and log results.")
    parser.add_argument("start", type=int, help="Start angle of sweep.")
    parser.add_argument("stop", type=int, help="End angle of sweep. The sweep \
                        does not include this value.")
    parser.add_argument("step", nargs='?', type=int, default=1,
                        help="Spacing between values.")
    parser.add_argument("--foil", "-f", default="0012", help="Foil")
    args = parser.parse_args()

    param_sweep(args.foil, args.start, args.stop, args.step)
