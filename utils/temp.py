from d3d_nefis import d3d_data
import numpy as np
from post_proc import post_proc
from animate import animate

#nefdat = d3d_data('trim-IFREMER_Turbine1b')
#nefdat.load_data('U1')
#nefdat.load_data('V1')
#nefdat.load_data('KFU')
#nefdat.load_data('KFV')
#nefdat.load_data('KCU')
#nefdat.load_data('KCV')
#nefdat.load_data('FLOW-RUNTXT')
#
#del nefdat

# plots at last time step
post_proc('IFREMER_Turbine1b')

# plots at itime=1
#post_proc('IFREMER_Turbine1b',1)

#animate('IFREMER_Turbine1b')
