#!/usr/bin/env python

from run_delft3D import run_delft3D
from post_proc import post_proc
import sys, platform

os = platform.system()

if len(sys.argv) < 2:
    print
    print 'Usage: python run_case.py <casename>'
    print
    exit(1)

#casename = 'IFREMER8'
casename = sys.argv[1]

# define Delft3D location
if os == 'Linux':
    D3Dexe = r'''/home/ccchart/opt/delft3d/lnx/flow2d3d/bin/d_hydro.exe'''
elif os == 'Windows':
    D3Dexe = r'''C:\Users\ccchart\Desktop\delft3d-4.01.00.rc.12\win32\flow2d3d\bin\d_hydro.exe'''

# run delft3D
error = run_delft3D(D3Dexe,casename)

if not error == 0:
    print
    print 'D_hydro Failed'
    print
    exit(1)

post_proc(casename)
