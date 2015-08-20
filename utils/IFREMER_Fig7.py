
from d3d_nefis import d3d_data, mnvel2xyvel
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate

cases=['IFREMER_Turbine1b']

for case in cases:
    basename = 'trim-'+case
    
    # open output file
    nefdat = d3d_data(basename)
    
    # print some variable information
    #nefdat.file_info()
    
    # get data
    # note variables come in k,i,j
    mvel = nefdat.get_data('U1','map-series')
    nvel = nefdat.get_data('V1','map-series')
    wvel = nefdat.get_data('WPHY','map-series')    

    # trim ghost cells off k velocity
    wvel = wvel[:, 1:-1, 1:-1]
    

    # calculate U and V velocity
    #  ***** m,n velocities go in with ghost cells
    #  ***** u,v, velocities returned with ghost cells trimmed
    alpha = nefdat.get_data('ALFAS','map-const')
    uvel, vvel = mnvel2xyvel(mvel,nvel,alpha)
    
    
    umag = np.sqrt(uvel**2+vvel**2+wvel**2)
    
    # trim ghost cells off m and n velocity
    mvel = mvel[:, 1:-1, 1:-1]
    nvel = nvel[:, 1:-1, 1:-1]

    
    # variables come in k,i,j order, rearrange to i,j,k
    #U = np.transpose(U,(1,2,0))
    
    X1 = nefdat.get_data('XZ','map-const')  # cell center values
    Y1 = nefdat.get_data('YZ','map-const')
    #X2 = nefdat.get_data('XCOR','map-const')  # node values
    #Y2 = nefdat.get_data('YCOR','map-const')
    
    # trim ghost cells off X and Y
    xvals = X1[    1:-1, 1:-1]
    yvals = Y1[    1:-1, 1:-1]
    
    
    imax=len(mvel[0,:,0])
    jmax=len(mvel[0,0,:])
    kmax=len(mvel[:,0,0])
    
#Find z-values  
thick = nefdat.get_data('THICK','map-const') #percent of each layer 
depth = nefdat.get_data('DP0','map-const')   #location of water bed base
height =  nefdat.get_data('S1','map-series') #water height  

imax=len(xvals[:,0])
jmax=len(xvals[0,:])
kmax=len(thick)

total_thick = 0.0
frac=[]
# go through thickness from bottom to top
for val in thick[::-1]:
    # increment the total thickness (% should add to 100)
    total_thick += val
    # save the running total height fraction
    frac.append(total_thick) #append adds this number to the end of the list
# reverse the fraction to go from top to bottom
frac = frac[::-1]

# trim ghost cells
height = height[1:-1,1:-1]
depth = depth[1:-1,1:-1]

# Create z values
zvals = np.multiply.outer(frac,(height+depth)) - np.tile(depth,(kmax,1,1))

#---------------------------------
# start plotting stuff
#---------------------------------

#  KDTree lookup
def linspace2d(loc1,loc2,nx):   # create a line of points
    nd = len(loc1)
    list = [ np.linspace(loc1[i],loc2[i],nx) for i in range(nd)]
    pts = np.array( list )
    return pts.transpose()

#  # Probe locations (can be any collection/line of points)
 

#  # get distance and index of nearest (cell center) points
#  dists, idxs = nefdat.TreeLookup(pts)

#  # locations of nearest points to probe points
#  locs = [ [xvals[ijk[1:]], yvals[ijk[1:]], zvals[ijk]]  for ijk in idxs ]

#  # velocities at nearest locations
#  vels = [ [uvel[ijk], vvel[ijk]]  for ijk in idxs ]

#  print "probe locations :  ", pts
#  print "used idices     :  ", idxs
#  print "used locations  :  ", locs
#  print "velocities      :  ", vels

#zlocs = np.linspace(-0.84, -1.16, 5)
zlocs = [21,23,25,27,29]
i=0
for ztemp in zlocs:
    i=i+1
    ## xmin = 11.0 #in meters
    ## xmax = 11.0
    ## ymin = yvals.min()
    ## ymax = yvals.max()
    ## zmin = ztemp
    ## zmax = ztemp

    ## loc1 = [xmin, ymin, zmin]
    ## loc2 = [xmax, ymax, zmax]

    ## print "  Interpolating line data from:"
    ## print loc1
    ## print "  to:"
    ## print loc2

    ## npts = 50
    ## # a line of (npts) points going from loc1 to loc2
    ## pts = linspace2d(loc1, loc2, npts)

    ## nn = 1

    ## #zint, uint, vint = nefdat.TreeInterp(pts,nn,[zvals,uvel,vvel])
    ## #yint, uint, vint = nefdat.TreeInterp(pts,nn,[np.tile(yvals,(kmax,1,1)),uvel,vvel])
    ## yint, uint, vint = nefdat.TreeInterp_bar(pts,[np.tile(yvals,(kmax,1,1)),uvel,vvel])

    ## #flatlocs = np.transpose([np.tile(xvals,(kmax,1,1)).ravel(),  np.tile(yvals,(kmax,1,1)).ravel(),  zvals.ravel()])
    ## #print np.shape(flatlocs)
    ## #print np.shape(uvel.ravel())
    ## #uint = scipy.interpolate.griddata(flatlocs, uvel.ravel(), pts, rescale='True')
    ## #uint = scipy.interpolate.LinearNDInterpolator(flatlocs, uvel.ravel(), pts)

    ## idxshape = np.shape(zvals)
    ## dists, idxs = nefdat.tree.query(pts,1)
    ## ijkdx = [np.unravel_index(ind,idxshape) for ind in idxs]
    ## print ijkdx

    ## tmp1 = pts[:,1]
    ## tmp2 = np.asarray(yint)

    plt.subplot(6,1,i)

    #plt.plot(pts[:,1]-3.0, uint, c='black',   linewidth=2, label='Delft3D IFREMER') 
    plt.plot(yvals[67,:]-3.0, uvel[ztemp,67,:], c='black',   linewidth=2, label='Delft3D IFREMER') 
    #plt.plot(np.asarray(yint)-3.0, uint, c='black',   linewidth=2, label='Delft3D IFREMER') 
    #plt.plot(yint, uint, c='black',   linewidth=2, label='Delft3D IFREMER') 

    plt.title('IFREMER Lateral Wake Velocity (Fig 7)')
    plt.xlabel('Lateral Width(D)')
    plt.ylabel('Velocity (m/s)')
    plt.legend(loc='lower right')






#plt.tight_layout()  # fix spacing between plots


#
# write out some data to a file
#
iwrt = 0
if iwrt == 1:
    import csv
    clinefile = basename+'-cline.csv'
    with open(clinefile,'w') as fin:
        csv.writer(fin).writerows(zip(dist[idx2], umag[idx1,idx2,idx3].ravel()))


# clean up -- close file and delete nefdat object
del nefdat




with open('Myers_fig7_Data.txt') as fin:
    fin.readline()
    data=fin.readlines()
a=[val.split() for val in data]
x = [float(val[0]) for val in a]

lables = ['-0.2D', '-0.1D', '0D', '0.1D', '0.2D']
colors = ['r', 'b', 'g', 'c', 'b']

for i in range(5):
    y = [float(val[i+1]) for val in a]
    
    plt.subplot(6,1,i+1)
    plt.plot(x,y,'o', markersize=6, label=lables[i])
    plt.legend(loc='lower right')
plt.savefig(basename+'-plots.png')
plt.show() 
