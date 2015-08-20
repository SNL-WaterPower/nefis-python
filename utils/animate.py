def animate(casename):
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

    # get coordinate information
    X1 = nefdat.get_data('XZ')  # cell center values
    Y1 = nefdat.get_data('YZ')

    # trim ghost cells off X and Y
    xvals = X1[ 1:-1, 1:-1]
    yvals = Y1[ 1:-1, 1:-1]

    # get X and Y velocity
    #  ***** u,v, velocities returned with ghost cells trimed
    uvel, vvel = nefdat.get_xyvel()

    ntimes = len(uvel[:,0,0,0])
    kmax = len(uvel[0,:,0,0])
    imax = len(uvel[0,0,:,0])
    jmax = len(uvel[0,0,0,:])

    ########################################################################################
    #
    #  example of animating centerline deficit with time
    #
    ########################################################################################

    print "  Making some plots..."
    from matplotlib import pyplot as plt
    from matplotlib import animation

    fig = plt.figure()
    ax = plt.axes(xlim=(0,18),ylim=(0,1))

    line, = ax.plot([], [], lw=2)
    annotation = plt.annotate('', xy=(0.5, 0.5))

    def init():
        line.set_data([], [])
        annotation = plt.annotate('', xy=(0.5, 0.5))
        return line, annotation

    def animate(itime):
        x = xvals[:,jmax/2]
        y = uvel[itime,kmax/2,:,jmax/2]
        line.set_data(x, y)
        annotation = plt.annotate('Time Step = {}'.format(itime), xy=(0.5, 0.5))
        return line, annotation
        
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=ntimes, interval=500, blit=True)

    # can't save without ffmpeg installed
    #anim.save('example.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

    plt.title('Velocity Deficit Convergence')
    plt.show()

    ########################################################################################
    #
    # clean up -- close file and delete nefdat object
    #
    ########################################################################################
    del nefdat
