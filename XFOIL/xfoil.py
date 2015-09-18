import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

import subprocess
import glob
import os


delete = True

# XFOIL commands to run
cmd_template = '''
$$$NACA_NAME$$$
PLOP
G

SAVE
data/$$$NACA_NAME$$$.foil
OPER
ITER
50
VPAR
N 9

VISC 2E5
PACC
data/$$$NACA_NAME$$$.dat

ASEQ 0 15 1

QUIT
'''

# The foils
# foils = ['0001', '0006', '0009', '0010', '0012', '0015', '0018', '0021', '0025',
#         '2206', '2209', '2212', '2215', '2218', '2221',
#         '2306', '2309', '2312', '2315', '2318', '2321',
#         '2406', '2409', '2412', '2415', '2418', '2421',
#         '2506', '2509', '2512', '2515', '2518', '2521',
#         '2606', '2609', '2612', '2615', '2618', '2621',
#         '2706', '2709', '2712', '2715', '2718', '2721',
#         '4206', '4209', '4212', '4215', '4218', '4221',
#         '4306', '4309', '4312', '4315', '4318', '4321',
#         '4406', '4409', '4412', '4415', '4418', '4421',
#         '4506', '4509', '4512', '4515', '4518', '4521',
#         '4606', '4609', '4612', '4615', '4618', '4621',
#         '4706', '4709', '4712', '4715', '4718', '4721',
#         '6206', '6209', '6212', '6215', '6218', '6221',
#         '6306', '6309', '6312', '6315', '6318', '6321',
#         '6406', '6409', '6412', '6415', '6418', '6421',
#         '6506', '6509', '6512', '6515', '6518', '6521',
#         '6606', '6609', '6612', '6615', '6618', '6621',
#         '6706', '6709', '6712', '6715', '6718', '6721']

foils = ['00' + str(i).zfill(2) for i in range(1, 100)]
#foils = ['0012']

# Make folder or delete files that exist
for folder in ['logs', 'data', 'imgs']:
    try:
        os.makedirs(folder)
    except:
        if delete:
            filelist = glob.glob(folder + '/*')
            for f in filelist:
                os.remove(f)

# If we're not deleting logs then we're continuing with the solutions
# Find the remaining airfoils to be run
if not delete:
    last_log = max(glob.iglob(os.path.join('logs', '*')), key=os.path.getctime)
    number = last_log.split('/')[1].split('.')[0]
    foils = foils[foils.index(number) + 1:]

# Run each foil and output log file
for foil in foils:
    with open('logs/' + foil + '.log', "a+") as stdout:
        p = subprocess.Popen('xfoil',
                             stdin=subprocess.PIPE,
                             stdout=stdout)

        print(foil)
        commands = cmd_template.replace('$$$NACA_NAME$$$', 'NACA ' + foil)
        p.stdin.write(bytes(commands, 'UTF-8'))
        p.communicate()[0]
        p.stdin.close()

# Load our data
files = glob.glob('data/*.dat')


def load_df(file):
    with open(file) as f:
        if len(f.readlines()) < 13:
            return pd.DataFrame()
    print(file)
    df = pd.read_csv(file, header=10, delim_whitespace=True)[1:]
    airfoil = file.split(' ')[1].split('.dat')[0]
    max_camber = airfoil[0]
    max_camber_position = airfoil[1]
    thickness = airfoil[2:4]

    df['M'] = max_camber
    df['P'] = max_camber_position
    df['XX'] = thickness
    df['Airfoil'] = airfoil
    return df

data = [load_df(file) for file in files]
df = pd.concat(data).reset_index(
    drop=True).convert_objects(convert_numeric=True)

# Find the airfoils with all 15 alpha data points
full = (df.groupby('Airfoil').count().alpha == 15).reset_index().query('alpha == True').Airfoil.tolist()
d = df.query("Airfoil in @full")

# Some styling
# sns.set_style('ticks')

# Load data, plot airfoils
#filelist = glob.glob('data/*.dat')
# for file in filelist:
#    f, ax = plt.subplots(figsize=(5, 5))
#    df = pd.read_csv(file, header=None, skiprows=1, index_col=None, delim_whitespace=True)
#    name = file.split('.dat')[0]
#    df.plot(kind='line', x=0, y=1, legend=False)
#    plt.title(name)
#    plt.ylim(-0.55, 0.55)
#    plt.xlim(-0.05, 1.05)
#    plt.xlabel('')
#    plt.savefig('imgs/' + name + '.png')
#    plt.close('all')
#    plt.clf()
