def post_proc(casename,itime=-1):
    from d3d_nefis import d3d_data
    import numpy as np

    ########################################################################################
    #
    # grab the data from d3d results file
    #
    ########################################################################################

    basename = 'trim-'+casename

    print "  Opening "+basename

    # open output file
    nefdat = d3d_data(basename)

    ## print some results file information
    #nefdat.file_info()
    ## print list of all variable available
    #print nefdat.elmlist

    # get x,y coordinate information (at cell centers)
    xvals, yvals = nefdat.get_cell_locs()

    # zvals come out with ghosts trimmed
    zvals = nefdat.get_zvals()
    # only using itime step
    zvals = zvals[itime,:,:,:]

    # store some dimension sizes
    #              k,i,j
    kmax=len(zvals[:,0,0])
    imax=len(zvals[0,:,0])
    jmax=len(zvals[0,0,:])


    # get X and Y velocity
    #  ***** u,v, velocities returned with ghost cells trimed
    uvel, vvel, wvel = nefdat.get_xyzvel()
    # only using itime step
    uvel = uvel[itime,:,:,:]
    vvel = vvel[itime,:,:,:]
    wvel = wvel[itime,:,:,:]

    # get turbulence data at itime (returned with ghost cells trimmed)
    tke, eps = nefdat.get_turb()
    tke = tke[itime,:,:,:]
    eps = eps[itime,:,:,:]

    ########################################################################################
    #
    #  example of plotting points along a constant i,k line
    #
    ########################################################################################

    print "  Making some plots..."
    # import plotting utilities
    from matplotlib import pyplot as plt

    # setup a 2x2 subplot layout -- activate subplot 1
    plt.subplot (2,2,1)

    # define i and k locations of plotting line
    ival = 80
    klayer = kmax/2

    umag = np.sqrt(uvel**2+vvel**2+wvel**2)

    #plot y vs umag
    plt.plot(yvals[ival,:],umag[klayer,ival,:], 'g-', linewidth=2)

    # labels
    plt.title('Velocity')
    plt.xlabel('Y(m)')
    plt.ylabel('U(m/s)')

    ########################################################################################
    #
    #  Example of plotting points along an interpolated centerline xyz = (0, 3, -1.06) to (18, 3, -1.06)
    #
    ########################################################################################

    # 2x2 plot layout -- activate plot 2
    plt.subplot (2,2,2)

    def linspace2d(loc1,loc2,nx):   # create a line of nx points between loc1 and loc2
        nd = len(loc1)
        list = [ np.linspace(loc1[i],loc2[i],nx) for i in range(nd)]
        pts = np.array( list )
        return pts.transpose()

    # define endpoints
    xmin = 0.0
    xmax = 18.0
    ymin = 3.0
    ymax = 3.0
    zmin = -1.06
    zmax = -1.06
    loc1 = [xmin, ymin, zmin]
    loc2 = [xmax, ymax, zmax]

    print "  Interpolating line data from:"
    print loc1
    print "  to:"
    print loc2

    # create the points along the line
    npts = 150
    pts = linspace2d(loc1, loc2, npts)

    # barycentric linear interpolation -- good for structured grids.
    # interpolate u and v onto out line
    uint,vint = np.asarray(nefdat.TreeInterp_bar(pts,[uvel,vvel],itime))  # itime is to setup the tree setup at the correct time in the moving grid 

    # calculate velocity deficit
    udef = 1.0-np.asarray(uint)/0.8

    # plot x along centerline vs velocity deficit
    plot = plt.plot(pts[:,0], udef.ravel(), 'b-',    linewidth=2)

    plt.title('Centerline Velocity Defecit')
    plt.xlabel('X(m)')
    plt.ylabel('Vel(m/s)')

    ########################################################################################
    #
    #  Example of plotting contours of veloctiy
    #
    ########################################################################################

    # define contour/colorbar limits
    vmin= 0.5
    vmax= 1.0
    cvalues = np.linspace(vmin,vmax,256)
    tvalues = np.linspace(vmin,vmax,11)

    plt.subplot (2,2,3)

    ## plot contour field of velocity magnitude
    #plt.contourf(xvals, yvals, umag[klayer,:,:], 256)
    #plt.contourf(xvals, yvals, umag[klayer,:,:], 256, vmin=vmin, vmax=vmax, extend='neither')
    plt.contourf(xvals, yvals, uvel[klayer,:,:], cvalues, extend='both')

    #cb = plt.colorbar()                # Automatic tick levels
    cb = plt.colorbar(ticks=tvalues)   # defined ticks
    cb.ax.set_ylabel('Velocity (m/s)')  # default rotation is 90

    plt.axis('equal')  # same scale for x and y axes
    plt.title('Velocity')
    plt.xlabel('X(m)')
    plt.ylabel('Y(m)')

    ########################################################################################
    #
    #  Example of plotting contours Turbulent Intensity
    #
    ########################################################################################

    plt.subplot (2,2,4)

    ## calculate turbulent intensity
    TI = np.sqrt(2.0/3.0*tke)/umag
    plt.contourf(xvals, yvals, TI[klayer,:,:], 256)

    cb = plt.colorbar()
    #ax = cb.ax.get_xaxis()
    #cb.ax.get_xaxis().tick_top()
    cb.ax.get_xaxis().labelpad = 15
    cb.ax.set_xlabel('TI (-)')

    plt.axis('equal')
    plt.title('Turbulent Intensity')
    plt.xlabel('X(m)')
    plt.ylabel('Y(m)')


    plt.tight_layout()  # fix spacing between plots

    # save the created image
    plt.savefig(casename+'-4plots.png')
    # display on screen
    #plt.show() 

    ########################################################################################
    #
    #  Example of making aditional plot images -- centerline plot by itself
    #
    ########################################################################################

    # clear figure and start a fresh plot
    plt.clf()

    # 1x1 plot layout -- activate plot 1
    plt.subplot (1,1,1)

    # replot centerline
    plot = plt.plot((pts[:,0]-7.0)/0.8, udef.ravel(), 'b-',    linewidth=2)

    plt.title('Centerline Velocity Defecit')
    plt.xlabel('X(m)')
    plt.ylabel('Vel(m/s)')

    # read in experimetnal data
    with open('IFREMER.dat','r') as fin:
        line=fin.readline()
        data=fin.readlines()
    xin = [val.split()[0] for val in data]
    yin = [val.split()[1] for val in data]

    plt.plot(xin,yin,'ro')

    # save the created image
    plt.savefig(casename+'-centerline.png')
    # display on screen
    plt.show() 

    ########################################################################################
    #
    # write out some data to a file
    #
    ########################################################################################
    iwrt = 0
    if iwrt == 1:
        import csv
        clinefile = casename+'-centerline.csv'
        with open(clinefile,'w') as fin:
          csv.writer(fin).writerows(zip(pts[:,0], udef.ravel()))
            

    ########################################################################################
    #
    # clean up -- close file and delete nefdat object
    #
    ########################################################################################
    del nefdat
