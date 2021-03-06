#!/Users/sma/anaconda/bin/python
"""
name: pynergy.py
usage: pynergy.py [-h] -i INPUT [-o OUTPUT] [-c] -e ENERGY [-d DELTA] [-g]
author: Sean Anderson (https://github.com/roguephysicist)

This script calculates transition energies between energy bands using
eigen-energy files generated by ABINIT during a band structure calculation.
This script allows you to input a desired energy value and finds all the
upward transitions that can produce that value within a specified tolerance.

If the input file is an unformatted EIG file produced by ABINIT, you can run
the script with the '-c' flag and it will automatically format it to a
plottable file and calculate the transitions.

It can also output Gnuplot arrow codes for plotting or descriptive text
for each transition.
"""

import argparse, re
import numpy as np

OFFSET = 0                # Gnuplot offset

def eigenformat(inputfile, outputfile):
    """ formats ABINIT eig file for easy plotting """
    with open(inputfile, "r") as ifile:
        text = ifile.read().replace('\n', '').replace('kpt#', '\n')
    sub = re.sub(r',.*\)', "", text)
    final = '\n'.join(sub.split('\n')[1:])
    with open(outputfile, "w") as ofile:
        ofile.write(final)

def transitions(inputfile, outputfile):
    """
    loops over all values in input file and calculates upward transitions
    and selects only the ones that match the desired value.
    """
    eigen = np.loadtxt(inputfile)  # Creates a numpy array from input file
    kpts = len(eigen)               # max k-points = file length
    bands = len(eigen[0])           # max bands = columns

    scratch = open(outputfile, 'w')   # Opens output file for writing
    for kpt in range(0, kpts):                      # Loops over k-points
        for start in range(1, bands):               # Loops over all bands
            for finish in range(start + 1, bands):  # Loops over upward bands
                orig = eigen[kpt, start]            # Value at origin band
                targ = eigen[kpt, finish]           # Value at target band
                diff = abs(orig - targ)             # The difference
                # tests to see if diff is between desired value +/- delta
                if args.energy - args.delta <= diff <= args.energy + args.delta:
                    if args.gnuplot:    # For Gnuplot arrow codes
                        text = 'set arrow from {0},{1:.5f} '\
                               'to {0},{2:.5f}\n'\
                               .format(kpt + 1, orig - OFFSET, targ - OFFSET)
                    else:   # Nicely formated text
                        text = '{0:0>9.6f} eV | '\
                               'k-point: {1:0>3d} | '\
                               'bands: {2:0>2d} -> {3:0>2d}\n'\
                               .format(diff, kpt + 1, start, finish)
                    scratch.write(text)    # Writes each line that passed test
    scratch.close()    # Closes file

# Parses command line options
parser = argparse.ArgumentParser(description='This script calculates '\
                        'transition energies between energy bands '\
                        'using eigen-energy files generated by ABINIT '\
                        'during a band structure calculation. This script '\
                        'allows you to input a desired energy value and '\
                        'finds all the upward transitions that can produce '\
                        'that value within a specified tolerance.')

parser.add_argument('-i', '--input', help='Input file name', required=True)
parser.add_argument('-o', '--output', help='Output file name',
                    default='transitions.dat', required=False)
parser.add_argument('-c', '--convert',
                    help='Converts a raw ABINIT eigen-energy file for '\
                    'easier plotting. This step is required to use this '\
                    'script if you are starting with an unformatted file.',
                    action='store_true', required=False)
parser.add_argument('-e', '--energy', help='Energy value in eV',
                    type=float, required=True)
parser.add_argument('-d', '--delta',
                    help='Energy delta in eV (default = 0.001 eV)',
                    type=float, default=0.001, required=False)
parser.add_argument('-g', '--gnuplot', help='Generates Gnuplot arrow codes',
                    action='store_true', required=False)
args = parser.parse_args()

if args.convert:
    print 'Formatting {} and saving to eigen.dat'.format(args.input)
    eigenformat(args.input, "eigen.dat")
    print 'Calculating transitions for '\
          'eigen.dat around {1} eV and saving to {0}'\
          .format(args.output, args.energy)
    transitions("eigen.dat", args.output)
else:
    print 'Calculating transitions for '\
          '{0} around {2} eV and saving to {1}'\
          .format(args.input, args.output, args.energy)
    transitions(args.input, args.output)
