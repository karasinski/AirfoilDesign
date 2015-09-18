import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd
import subprocess
import glob
import os
import argparse


def clean(foil):
    # Make folder or delete files that exist
    for folder in ['logs', 'data', 'imgs']:
        try:
            os.makedirs(folder)
        except:
            filelist = glob.glob(folder + '/*' + foil + '*')
            for f in filelist:
                os.remove(f)


def main(foil, **kwds):
    # If data from this foil already exists, delete it
    clean(foil)

    # Run each foil and output log file
    with open('logs/NACA ' + foil + '.log', 'w') as stdout:
        p = subprocess.Popen('xfoil',
                             stdin=subprocess.PIPE,
                             stdout=stdout)

        print(foil)
        commands = cmd_template.format(NACA_NAME='NACA ' + foil, **kwds)
        p.stdin.write(bytes(commands, 'UTF-8'))
        p.communicate()[0]
        p.stdin.close()

    return load_data()


def load_df(file):
    # If no data was logged, return an empty DataFrame
    with open(file) as f:
        if len(f.readlines()) < 13:
            return pd.DataFrame()

    df = pd.read_csv(file, header=10, delim_whitespace=True)[1:]
    airfoil = file.split(' ')[1].split('.dat')[0]
    max_camber = airfoil[0]
    max_camber_position = airfoil[1]
    thickness = airfoil[2:4]

    df['M'] = max_camber
    df['P'] = max_camber_position
    df['XX'] = thickness

    df = df.convert_objects(convert_numeric=True)
    df['Airfoil'] = airfoil
    return df


def load_data():
    # Load our data
    files = glob.glob('data/*.dat')
    data = [load_df(file) for file in files]
    df = pd.concat(data).reset_index(drop=True)#.convert_objects(convert_numeric=True)
    return df


def plot(foil, df):
    # Load data, plot airfoil
    sns.set(style='ticks', context='notebook', font_scale=1.5)

    # Just plot a single foil
    d = df.query('Airfoil == @foil')

    # If we just ran a single data point, don't plot
    if len(d) == 1:
        return

    f, ax = plt.subplots(figsize=(5, 5))
    d.plot(kind='line', x='CL', y='CD', legend=False)
    plt.title('NACA ' + foil)
    plt.xlabel('$C_L$')
    plt.ylabel('$C_D$')
    plt.tight_layout()
    plt.savefig('imgs/NACA ' + foil + '_CL_vs_CD.png')
    plt.close('all')
    plt.clf()

    f, ax = plt.subplots(figsize=(5, 5))
    d.plot(kind='line', x='alpha', y='CL', legend=False)
    plt.title('NACA ' + foil)
    plt.ylabel('$C_L$')
    plt.xlabel('$\\alpha$ (degrees)')
    plt.tight_layout()
    plt.savefig('imgs/NACA ' + foil + '_alpha_vs_CL.png')
    plt.close('all')
    plt.clf()


# XFOIL commands to run
cmd_template = '''
{NACA_NAME}
PLOP
G

SAVE
data/{NACA_NAME}.foil
OPER
VPAR
N 9

VISC {Reynolds}
PACC
data/{NACA_NAME}.dat

ASEQ {start} {stop} {step}

QUIT
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Set the foil angle of attack and log results.')
    parser.add_argument('start', type=int, help='Start angle of sweep.')
    parser.add_argument('stop', nargs='?', type=int, default=None,
                        help='End angle of sweep. The sweep does not include this value.')
    parser.add_argument('step', nargs='?', type=int, default=1,
                        help='Spacing between values.')
    parser.add_argument('--foil', '-f', default='0012', help='NACA XXXX foil')
    parser.add_argument('--Reynolds', '-R', type=float, default=6e6,
                        help='Reynolds number')
    parser.add_argument('--plot', '-p', action='store_true',
                        default=False, help='Plot time results')
    args = parser.parse_args()
    if args.stop is None:
        args.stop = args.start

    # Run main script and optional plot
    df = main(args.foil,
              Reynolds=args.Reynolds,
              start=args.start, stop=args.stop, step=args.step)

    if args.plot:
        plot(args.foil, df)
