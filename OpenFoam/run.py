from __future__ import division, print_function
from subprocess import call
import argparse
import os
import time
import numpy as np


def run_case(foil, alpha, Reynolds, U):
    # Clean and run case
    print("Cleaning...")
    call(["./Allclean"])
    call(["python", "scripts/NACA2STL.py", foil, str(alpha)])
    call(["python", "scripts/initial_conditions.py",
          "--Reynolds", str(Reynolds),
          "--U", str(U)])
    print("Running solution...")
    call(["./Allrun"])

    # Save data
    output_dir = os.getcwd() + '/output/' + foil + '/' + str(alpha)
    data = os.getcwd() + '/airfoil_pimpleFoam/'
    call(["rm", "-rf", output_dir])
    os.makedirs(output_dir)
    time.sleep(1)
    call(['cp', '-r', data, output_dir])


def param_sweep(foil, start, stop, step, Reynolds, U):
    alphas = np.arange(start, stop, step)
    print("Running foil {}, alphas {}.".format(foil, alphas))

    for alpha in alphas:
        print("Running alpha {}.".format(alpha))
        run_case(foil, alpha, Reynolds, U)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set the foil angle of attack and log results.")
    parser.add_argument("start", type=int, help="Start angle of sweep.")
    parser.add_argument("stop", nargs='?', type=int, default=None,
                        help="End angle of sweep. The sweep does not include this value.")
    parser.add_argument("step", nargs='?', type=int, default=1,
                        help="Spacing between values.")
    parser.add_argument("--foil", "-f", default="0012", help="Foil")
    parser.add_argument("--Reynolds", "-R", type=float, default=6e6,
                        help="Reynolds number")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--U", "-U", type=float, default=None, help="Velocity in m/s")
    group.add_argument("--Mach", "-M", type=float, default=None, help="Mach number")
    args = parser.parse_args()

    # If neither U nor Mach specified, set default velocity of 1 m/s
    if args.U is None and args.Mach is None:
        args.U = 1
    # If U is not set and Mach is, set U to the appropriate velocity
    if args.U is None and args.Mach is not None:
        args.U = args.Mach * 332

    if args.stop is None:
        args.stop = args.start + 1
    param_sweep(args.foil, args.start, args.stop, args.step, args.Reynolds, args.U)
