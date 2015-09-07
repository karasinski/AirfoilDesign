from __future__ import division, print_function
import argparse
import numpy as np


def gen_stl(foil="0012", alpha_deg=4):
    # ------------------------ START OF INPUT PARAMETER REGION ------------------- #

    # Foil geometry
    c = 1                           # Geometric chord length
    s = 2                           # Span (along y-axis)
    alpha = np.deg2rad(alpha_deg)   # Angle of attack (in radians)
    NACA = [int(d) for d in foil]   # NACA 4-digit designation as a row vector

    # Surface resolution parameters
    Ni = 1000                       # Number of interpolation points along the foil

    # ------------------------- END OF INPUT PARAMETER REGION -------------------- #

    # Create a vector with x-coordinates, camber and thickness
    beta = np.linspace(0, np.pi, Ni)
    x = c*(0.5*(1-np.cos(beta)))
    z_c = np.zeros(len(x))
    z_t = np.zeros(len(x))
    theta = np.zeros(len(x))

    # Values of m, p and t
    m = NACA[0]/100
    p = NACA[1]/10
    t = (NACA[2]*10 + NACA[3])/100

    # Calculate thickness
    # The upper expression will give the airfoil a finite thickness at the trailing
    # edge, witch might cause trouble. The lower expression is corrected to give
    # zero thickness at the trailing edge, but the foil is strictly speaking no
    # longer a proper NACA airfoil.
    #
    # See http://turbmodels.larc.nasa.gov/naca4412sep_val.html
    #     http://en.wikipedia.org/wiki/NACA_airfoil

    #z_t = (t*c/0.2) * (0.2969*(x/c)**0.5 - 0.1260*(x/c) - 0.3516*(x/c)**2 + 0.2843*(x/c)**3 - 0.1015*(x/c)**4);
    z_t = (t*c/0.2) * (0.2969*(x/c)**0.5 - 0.1260*(x/c) - 0.3516*(x/c)**2 + 0.2843*(x/c)**3 - 0.1036*(x/c)**4)

    # Calculate camber
    if p > 0:
        # Calculate camber
        z_c += (m*x/p**2) * (2*p - x/c) * (x < p*c)
        z_c += (m*(c-x)/(1-p)**2) * (1 + x/c - 2*p) * (x >= p*c)

        # Calculate theta-value
        theta += np.arctan((m/p**2) * (2*p - 2*x/c)) * (x < p*c)
        theta += np.arctan((m/(1-p)**2) * (-2*x/c + 2*p)) * (x >= p*c)

    # Calculate coordinates of upper surface
    Xu = x - z_t*np.sin(theta)
    Zu = z_c + z_t*np.cos(theta)

    # Calculate coordinates of lower surface
    Xl = x + z_t*np.sin(theta)
    Zl = z_c - z_t*np.cos(theta)

    # Rotate foil to specified angle of attack
    upper = np.matrix([[np.cos(alpha), np.sin(alpha)],
                       [-np.sin(alpha), np.cos(alpha)]])*np.vstack((Xu, Zu))
    lower = np.matrix([[np.cos(alpha), np.sin(alpha)],
                       [-np.sin(alpha), np.cos(alpha)]])*np.vstack((Xl, Zl))

    Xu = np.array(upper[0, :]).conj().transpose()
    Zu = np.array(upper[1, :]).conj().transpose()
    Xl = np.array(lower[0, :]).conj().transpose()
    Zl = np.array(lower[1, :]).conj().transpose()

    # Merge upper and lower surface (NB: Assume that the trailing edge is sharp)
    # (see comments w.r.t. thickness calculation above)
    X = Xu[:, 0].tolist() + Xl[:, 0].tolist()[-2:0:-1]
    Z = Zu[:, 0].tolist() + Zl[:, 0].tolist()[-2:0:-1]
    N = len(X)

    # Triangulate the end surface
    tri = [1, 2, N]
    for i in range(2, Ni):
        tri += [i, i+1, N-i+2]

    for i in range(Ni+1, N):
        tri += [i, i+1, N-i+2]
    tri = np.array(tri).reshape(-1, 3)

    # Make it 3D
    X += X
    Z += Z
    Y = [s/2] * N + [-s/2] * N

    # Triangulate the second end surface
    tri = np.vstack((tri, np.vstack((tri[:, 1], tri[:, 0], tri[:, 2])).T + N)).tolist()

    for i in range(1, N):
        tri += [[i, N+i, i+1]]
    tri += [[N, 2*N, 1]]

    for i in range(N+1, 2*N):
        tri += [[i, i+1, i-N+1]]
    tri += [[2*N, N+1, 1]]

    # Indexing is off by 1
    tri = (np.array(tri) - 1).tolist()

    # Open file
    with open('airfoil.stl', 'w') as f:
        f.write('solid airfoil\n')
        for i, _ in enumerate(tri):
            # Calculate normal vector
            AB = [X[tri[i][1]] - X[tri[i][0]], Y[tri[i][1]] - Y[tri[i][0]], Z[tri[i][1]] - Z[tri[i][0]]]
            AC = [X[tri[i][2]] - X[tri[i][0]], Y[tri[i][2]] - Y[tri[i][0]], Z[tri[i][2]] - Z[tri[i][0]]]
            n = np.cross(AB, AC) / np.linalg.norm(np.cross(AB, AC))

            # Write facet
            f.write('  facet normal {:.6e} {:.6e} {:.6e}\n'.format(*n))
            f.write('    outer loop\n')
            f.write('      vertex {:.6e} {:.6e} {:.6e}\n'.format(X[tri[i][0]], Y[tri[i][0]], Z[tri[i][0]]))
            f.write('      vertex {:.6e} {:.6e} {:.6e}\n'.format(X[tri[i][1]], Y[tri[i][1]], Z[tri[i][1]]))
            f.write('      vertex {:.6e} {:.6e} {:.6e}\n'.format(X[tri[i][2]], Y[tri[i][2]], Z[tri[i][2]]))
            f.write('    endloop\n')
            f.write('  endfacet\n')

        f.write('endsolid airfoil\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate unstructured grid for NACA airfoil at specified angle of attack.")
    parser.add_argument("foil", help="NACA foil digits")
    parser.add_argument("alpha_deg", type=float, help="Angle of attack (deg)")
    args = parser.parse_args()

    print("Generating stl for a NACA {} at {} degrees angle of attack.".format(args.foil, args.alpha_deg))

    gen_stl(args.foil, args.alpha_deg)
