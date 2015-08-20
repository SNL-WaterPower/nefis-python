from run_delft3D import run_delft3D
from post_proc import post_proc


casename = 'IFREMER8'

# define Delft3D locatio
D3Dexe = r'''C:\Users\ccchart\Desktop\delft3d-4.01.00.rc.12\win32\flow2d3d\bin\d_hydro.exe'''

# run delft3D
error = run_delft3D(D3Dexe,casename)

if not error == 0:
    print
    print 'D_hydro Failed'
    print
    exit()

post_proc(casename)
