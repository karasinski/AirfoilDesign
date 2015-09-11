import argparse
import os


# Chord length
c = 1

def set_initial_conditions(U=1, pressure=0, turbulentKE=1e-3, turbulentOmega=1.0):
    values = {'flowVelocity': '(' + "{:.4e}".format(U) + ' 0 0)',
              'pressure': str(pressure),
              'turbulentKE': str(turbulentKE),
              'turbulentOmega': str(turbulentOmega)}

    path = os.getcwd() + '/airfoil_simpleFoam/0.org/include/initialConditions'
    template_path = path + '.template'
    print("Setting initial conditions.")
    with open(template_path) as f:
        txt = f.read()
    with open(path, "w") as f:
        f.write(txt.format(**values))

def set_Re(U, Re):
    """
    Set Reynolds number (to five significant digits) via kinematic viscosity in
    the input files.
    """
    path = os.getcwd() + '/airfoil_simpleFoam/constant/transportProperties'
    template_path = path + '.template'

    nu = U*c/Re
    print("Settings:\nReynolds={:.4e}\nVelocity={:.4e}\nnu={:.4e}".format(Re, U, nu))
    nu = "{:.4e}".format(nu)

    with open(template_path) as f:
        txt = f.read()
    with open(path, "w") as f:
        f.write(txt.format(nu=nu))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set the initial conditions.")
    parser.add_argument("--Reynolds", "-R", type=float, default=6e6)
    parser.add_argument("--U", "-U", type=float, default=1)
    args = parser.parse_args()

    set_initial_conditions(U=args.U)
    set_Re(args.U, args.Reynolds)
