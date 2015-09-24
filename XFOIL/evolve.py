import pandas as pd
import numpy as np


def wiggle_foil(foil, w=1E-4):
    # Load data
    df = pd.read_csv(foil, skiprows=1, header=None, delim_whitespace=True).as_matrix()

    # Foil is symmetric, and we're going to leave x alone, grab first half of y
    # coordinates.
    pos = d[:len(df)/2][:, 1]

    # Add some small wiggle
    wiggle = w * (2 * np.random.random(len(df)/2) - 1)
    result = pos + wiggle

    # Create full list of ys by mirroring the positive half
    full = np.concatenate((result, -result[::-1]))

    # Build the new dataframe
    output = pd.DataFrame([df[:, 0], full]).T

    # Increment the version number
    try:
        version = foil.split('_')[1].split('.foil')[0]
        version = '_' + str(int(version) + 1)
    except IndexError:
        version = '_1'

    # Save the new foil
    name = foil.split('.foil')[0].split('_')[0] + version
    with open(name + '.foil', 'w') as f:
        f.write(name.split('/')[-1] + '\n')
        output.to_csv(f, float_format='%.7e', sep=' ', header=False, index=False)
