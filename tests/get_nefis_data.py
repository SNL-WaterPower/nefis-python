from nefis_utils import nef_data, mnvel2xyvel
import numpy as np

#
# open a trim file    
#

#basename = 'trim-T7'
basename = 'trim-IFREMER'


nefdat = nef_data(basename)

# print some variable information
nefdat.file_info()

# get data
# note variables come in in k,i,j
mvel = nefdat.get_data('U1','map-series')
nvel = nefdat.get_data('V1','map-series')

# calculate U and V velocity
#  ***** m,n velocityies go in with ghost cells
#  ***** u,v, velocities returned with ghost cells trimed
alpha = nefdat.get_data('ALFAS','map-const')
uvel, vvel = mnvel2xyvel(mvel,nvel,alpha)

# trim ghost cells off m and n velocity
mvel = mvel[:, 1:-1, 1:-1]
nvel = nvel[:, 1:-1, 1:-1]

# variables come in in k,i,j order, rearrange to i,j,k
#U = np.transpose(U,(1,2,0))

X1 = nefdat.get_data('XZ','map-const')  # cell center values
Y1 = nefdat.get_data('YZ','map-const')
#X2 = nefdat.get_data('XCOR','map-const')  # node values
#Y2 = nefdat.get_data('YCOR','map-const')

# trim ghost cells off X and Y
xvals = X1[    1:-1, 1:-1]
yvals = Y1[    1:-1, 1:-1]


thick = nefdat.get_data('THICK','map-const')
depth = nefdat.get_data('DP0','map-const')
height =  nefdat.get_data('S1','map-series')

imax=len(xvals[:,0])
jmax=len(xvals[0,:])
kmax=len(thick)

total_thick = 0.0
frac=[]
# go through thickness from bottom to top
for val in thick[::-1]:
    # increment the total thickness
    total_thick += val
    # save the running total height fraction
    frac.append(total_thick)
# reverse the fraction to go from top to bottom
frac = frac[::-1]

# trim ghost cells
height = height[1:-1,1:-1]
depth = depth[1:-1,1:-1]

# I "think" this is correct -- TODO check this
zvals = np.multiply.outer(frac,(height+depth)) - np.tile(depth,(kmax,1,1))

#
#  KDTree lookup
#

ikdt = 0

if ikdt == 1:
    # Probe locations (can be any collection/line of points)
    # currently hard coded, should be an input
    pts = [[692150.8, 5174660.0, -3.2],[692145.0, 5174630.0, -3.2]] 

    # create a kdtree
    nefdat.TreeInit(xvals,yvals,zvals)

    # get distance and index of nearest (cell center) points
    dists, idxs = nefdat.TreeLookup(pts)

    # locations of nearest points to probe points
    locs = [ [xvals[ijk[1:]], yvals[ijk[1:]], zvals[ijk]]  for ijk in idxs ]

    # velocities at nearest locations
    vels = [ [uvel[ijk], vvel[ijk]]  for ijk in idxs ]

    # TODO update the search to grab the 4 nearest values and perform a barycentric interpolation

    print "probe locations :  ", pts
    print "used idices     :  ", idxs
    print "used locations  :  ", locs
    print "velocities      :  ", vels


iplt = 1
if iplt == 1:
    # start plotting stuff

    # chose a k (sigma) layer to look at
    #klayer = 4
    klayer = kmax/2

    import pylab as plt

    vmin=-2.0
    vmax= 2.0
    tvalues = np.linspace(vmin,vmax,11)
    cvalues = np.linspace(vmin,vmax,256)

    #CSF = plt.contourf(xvals, yvals, uvals, cvalues, extend='both')
    #CSF = plt.contourf(xvals, yvals, uvals, 256, vmin=vmin, vmax=vmax, extend='neither')

    # plot u-velocity
    plt.subplot(2,2,1)
    #CSF = plt.contourf(xvals, yvals, uvel[klayer,:,:], cvalues, extend='both')
    CSF = plt.contourf(xvals, yvals, uvel[klayer,:,:], 256, extend='neither')
    plt.axis('equal')
    #plt.colorbar()
    plt.colorbar(ticks=tvalues)

    # plot m-velocity
    plt.subplot(2,2,2)
    #CSF = plt.contourf(xvals, yvals, mvel[klayer,:,:], cvalues, extend='both')
    CSF = plt.contourf(xvals, yvals, mvel[klayer,:,:], 256, extend='neither')
    plt.axis('equal')
    plt.colorbar(ticks=tvalues)

    umag = np.sqrt(uvel**2+vvel**2)
  
    # plot velocity magnitude
    plt.subplot(2,2,3)
    #CSF = plt.contourf(xvals, yvals, umag[klayer,:,:], cvalues, extend='both')
    CSF = plt.contourf(xvals, yvals, umag[klayer,:,:], 256, extend='neither')
    plt.axis('equal')
    plt.colorbar(ticks=tvalues)


    # make a centerline plot of velocity magnitude
    #i1=225          # irange
    #i2=290
    i1=0          # irange
    i2=imax
    j1=jmax/2-1       # jrange
    j2=jmax/2
    k1=klayer-1       # krange
    k2=klayer

    idx1=slice(k1,k2)  # k-index range
    idx2=slice(i1,i2)  # i=index range
    idx3=slice(j1,j2)  # j-index range

    #cline_idx = [idx1,idx2,idx3]

    # integrate distance along centerline j=jmax/2
    dist=[0.0]
    total_dist=0.0
    j=jmax/2
    for i in range(1,imax):
        total_dist += np.sqrt((xvals[i,j]-xvals[i-1,j])**2+(yvals[i,j]-yvals[i-1,j])**2)
        dist.append(total_dist)

    plt.subplot(2,2,4)
    plot = plt.plot(dist[idx2], umag[idx1,idx2,idx3].ravel(), 'b-',    linewidth=2)
    #plot = plt.plot(umag[idx1,idx2,idx3].ravel(), 'b-',    linewidth=2)

    plt.show() 

#
# write out some data to a file
#
iwrt = 0
if iwrt == 1:
    import csv
    clinefile = basename+'-cline.dat'
    with open(clinefile,'w') as fin:
        csv.writer(fin).writerows(zip(dist[idx2], umag[idx1,idx2,idx3].ravel()))
        

# clean up -- close file and delete nefdat object
del nefdat