from d3d_nefis import d3d_data
import numpy as np

#
# open a trim file    
#


#basename = 'trim-T7'
basename = 'trim-IFREMER_Turbine1b'

print "  Opening "+basename


nefdat = d3d_data(basename)

# print some variable information
nefdat.file_info()

# get data
# note variables come in in k,i,j
mvel = nefdat.get_data('U1','map-series')
nvel = nefdat.get_data('V1','map-series')

# trim ghost cells off m and n velocity
mvel = mvel[:, 1:-1, 1:-1]
nvel = nvel[:, 1:-1, 1:-1]

# get U and V velocity
#  ***** u,v, velocities returned with ghost cells trimed
uvel, vvel = nefdat.get_xyvel()

# variables come in in k,i,j order, rearrange to i,j,k
#U = np.transpose(U,(1,2,0))

X1 = nefdat.get_data('XZ','map-const')  # cell center values
Y1 = nefdat.get_data('YZ','map-const')
#X2 = nefdat.get_data('XCOR','map-const')  # node values
#Y2 = nefdat.get_data('YCOR','map-const')

# trim ghost cells off X and Y
xvals = X1[    1:-1, 1:-1]
yvals = Y1[    1:-1, 1:-1]

# zvals come out with ghosts trimmed
zvals = nefdat.get_zvals()

imax=len(xvals[:,0])
jmax=len(xvals[0,:])
kmax=len(zvals[:,0,0])


#
#  KDTree lookup
#

def linspace2d(loc1,loc2,nx):
    nd = len(loc1)
    list = [ np.linspace(loc1[i],loc2[i],nx) for i in range(nd)]
    pts = np.array( list )
    return pts.transpose()

iplt = 1

if iplt == 1:

    print "  Making some plots..."

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

#    # plot u-velocity
#    plt.subplot(2,2,1)
#    #CSF = plt.contourf(xvals, yvals, uvel[klayer,:,:], cvalues, extend='both')
#    CSF = plt.contourf(xvals, yvals, uvel[klayer,:,:], 256, extend='neither')
#    plt.axis('equal')
#    #plt.colorbar()
#    plt.colorbar(ticks=tvalues)
#
#    # plot m-velocity
#    plt.subplot(2,2,2)
#    #CSF = plt.contourf(xvals, yvals, mvel[klayer,:,:], cvalues, extend='both')
#    CSF = plt.contourf(xvals, yvals, mvel[klayer,:,:], 256, extend='neither')
#    plt.axis('equal')
#    plt.colorbar(ticks=tvalues)
#
#    umag = np.sqrt(uvel**2+vvel**2)
#  
#    # plot velocity magnitude
#    plt.subplot(2,2,3)
#    #CSF = plt.contourf(xvals, yvals, umag[klayer,:,:], cvalues, extend='both')
#    CSF = plt.contourf(xvals, yvals, umag[klayer,:,:], 256, extend='neither')
#    plt.axis('equal')
#    plt.colorbar(ticks=tvalues)


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

#    plt.subplot(2,2,4)
    #plot = plt.plot(dist[idx2], umag[idx1,idx2,idx3].ravel(), 'b-',    linewidth=2)
    #plot = plt.plot(umag[idx1,idx2,idx3].ravel(), 'b-',    linewidth=2)

    xmin = 11.0
    xmax = 11.0
    ymin = yvals.min()
    ymax = yvals.max()
    for zloc in np.linspace(-0.84,-1.16,5):
        zmin = zloc
        zmax = zloc

        print 'min/max'
        print xvals.min()
        print xvals.max()
        print yvals.min()
        print yvals.max()
        print zvals.min()
        print zvals.max()

        loc1 = [xmin, ymin, zmin]
        loc2 = [xmax, ymax, zmax]

        print "  Interpolating line data from:"
        print loc1
        print "  to:"
        print loc2

        npts = 50
        # a line of (npts) points going from loc1 to loc2
        pts = linspace2d(loc1, loc2, npts)

        nn = 1
        # Inverse distance interpolated values from (nn) nearest negihbors
        #InterpVals = nefdat.TreeInterp(pts,nn,[zvals,uvel,vvel])
        #zint, uint, vint = nefdat.TreeInterp(pts,nn,[zvals,uvel,vvel])

        yint, uint, vint = nefdat.TreeInterp(pts,nn,[np.tile(yvals,(kmax,1,1)),uvel,vvel])



        plot = plt.plot(yint, uint, 'b-',    linewidth=2)     # interpolated line using KDTree

    plt.show() 

#
# write out some data to a file
#
iwrt = 1
if iwrt == 1:
    import csv
    clinefile = basename+'-cline.dat'

    print "  Saving data to "+clinefile

    with open(clinefile,'w') as fin:
        csv.writer(fin).writerows(zip(dist[idx2], umag[idx1,idx2,idx3].ravel()))
        

# clean up -- close file and delete nefdat object
#del nefdat
