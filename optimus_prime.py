#!/usr/bin/env python

# Fortran + MPI numerical simulation experiments automated validation tool.
# authors
#     Ricardo Frantz <ricadro.frantz@acad.pucrs.br> and
#     Filipi Vianna <filipi.vianna@pucrs.br>
#     Trying to meet Tulio's quality standards ;-)
# September, 2017

import argparse  # https://docs.python.org/2/library/argparse.html
import fileinput
import importlib
import os
import re
import shutil
from subprocess import call

## a small function that prints a string without breaking the line at the end
## https://stackoverflow.com/questions/493386/how-to-print-without-newline-or-space
def printNNL(string):
    import sys
    sys.stdout.write(string)
    sys.stdout.flush()

def checkFile(filename, error):
    printNNL('Filename: ' + filename)
    if os.path.isfile(filename):
        print(' [  OK  ]')
    else:
        print(' [MISSED]')
        error = True
    return error

## TODO
# Add an option to automatically generate an example case file.
# Add an option to control the volume of output (verbose)
# Add a function to check if more than one replacement was done

rules = {1:{}, 2:{}, 3:{}, 4:{}}
rules[1]['pattern'] = '\'(\d.|\d.\.).*\#\' + j + \'\s\''
rules[1]['replace'] = 'str(c.file[i][j]) + \'.\t#\' + j + \' \''
rules[2]['pattern'] = 'j + \'=\d.*?(\\n)\''
rules[2]['replace'] = 'j + \'=\' + str(c.file[i][j]) + \'\\n\''
rules[3]['pattern'] = 'j + \'=\d.*?(,)\''
rules[3]['replace'] = 'j + \'=\' + str(c.file[i][j])'
rules[4]['pattern'] = 'j + \'=\w.*?(\\n)\''
rules[4]['replace'] = 'j + \'=\' + str(c.file[i][j]) + \'\\n\''

# First checks if all files are present in source_dir
# Copy source_dir for each case in cases
# replace vars in case.file[]

parser = argparse.ArgumentParser(
    description='Fortran + MPI numerical simulation experiments automated validation tool.')
parser.add_argument('-c', '--cases', metavar='case', nargs='+',
                    help='<Required> case names without .py extension', required=True)
parser.add_argument('--src', metavar='source_dir', type=str,
                    help='Path for the template simulation (default ./src/)')
parser.add_argument('--path', metavar='path', type=str,
                    help='Path were to run the experiments (default .)')

## ./optimus_prime.py -c channel cylinder tgv
args = parser.parse_args()
if args.path is None:
    args.path = '.'
if args.src is None:
    args.src = './src'

#print('path: ' + args.path)
#print('source_dir: ' + args.src)

error = False;
for case in args.cases:

    # First check if all the files exist
    print('#######################################################################')
    print('Checking files for case: ' + case)
    error = checkFile(case + '.py', error)

    if not error:
        c = importlib.import_module(case)
        for i in c.file:
            if c.file[i]['name']:
                error = checkFile(args.src + '/' + c.file[i]['name'], error)
if error:
    print('-----------------------------------------------------------------------')
    print('ABORTED! No action was taken on your files.')
    print('Please check any reported missing file before replacing the parameters.')
    quit()

print('-----------------------------------------------------------------------')
print('Replacing parameters...')
for case in args.cases:
    path = 'case_' + case
    #print(path)
    try:
        shutil.copytree(args.src, path)
#    except OSError, e:
    except OSError:
        pass

    os.chdir(path)
    for i in c.file:
        print(path + '/' + c.file[i]['name'])
        filename = c.file[i]['name']
        origin = open(filename, 'r')
        content = origin.read()
        #print(content)
        #quit()
        origin.close()
        for j in c.file[i]:
            if j != 'name':
                for k in rules:                    
                    pattern = eval(rules[k]['pattern'])
                    replace = eval(rules[k]['replace'])
                    content_new = re.subn(pattern, replace,  content)
                    re.purge()
                    if (content_new[1] > 1):
                        print('Waring! More than one line replaced')
                        print (c.file[i]['name'])
                        print (j)            
                    if (content_new[1] != 0):
                        break
                if (content_new[1] == 0):
                    print ('Warning! Parameter not found')
                    print (c.file[i]['name'])
                    print (j)                                              
                
                content = content_new[0]
                destiny = open(filename, 'w')
                destiny.write(content_new[0])
                destiny.close
    os.chdir('..')
# ##call(["make", ""])
#     ##call(["mpi_rum", ""])

# mkdir case_1 &&
# cp -Rf src case_1 &&
# cd case_1 &&
# sed -ie 's/(\d.\d.*?)\#re/3000\t\#re/g' hello.txt
# make &&
# mpi_run .. &&
