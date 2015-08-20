import nefis
import numpy as np
import struct

def test_nefis_getelt_floats():
    #-------------------------------------------------------------------------------
    error, version = nefis.getnfv()
    print('Library version: %s' % version[4:])
    print('')
    #-------------------------------------------------------------------------------
    #dat_file = 'trim-f34.dat'
    #def_file = 'trim-f34.def'
    dat_file = 'trim-IFREMER.dat'
    def_file = 'trim-IFREMER.def'
    import os.path
    if not os.path.isfile(dat_file):
        print
        print 'ERROR:  ' + dat_file + ' does not exist'
        print
        exit(1)
    if not os.path.isfile(def_file):
        print
        print 'ERROR:  ' + def_file + ' does not exist'
        print
        exit(1)

    coding = ' '
    ac_type = 'r'
    fp = -1
    print("---------")
    print(dat_file)
    print(def_file)
    print(coding)
    print(ac_type)
    print("---------")
    #-------------------------------------------------------------------------------
    error, fp = nefis.crenef(dat_file, def_file, coding, ac_type)
    print('File set (should be zero): %d' % fp)
    print('NEFIS error code (crenef): %d' % error)
    print("---------")
    #-------------------------------------------------------------------------------
    elm_name='U1'
    error, elm_type, elm_single_byte, elm_quantity, elm_unit, elm_description, elm_count, elm_dimensions = nefis.inqelm(fp, elm_name)
    print elm_name,' dimensions : ',elm_dimensions
    print elm_name,'    size    : ',elm_count

    #-----------------------------------------------------------
    # Retrieve number of available timesteps
    #
    error, ntimes = nefis.inqmxi (fp, 'map-series')
    if not error == 0:
        print("=========")
        error, err_string = nefis.neferr()
        print('    NEFIS error string       : %s' % err_string)
        print("=========")

    #
    # Retrieve last timestep
    #
    usr_index = np.zeros(15,dtype=np.int32).reshape(5,3)
    usr_index[0,0] = ntimes  # first timestep
    usr_index[0,1] = ntimes  # last time step
    #usr_index[0,0] = 1  # first timestep
    #usr_index[0,1] = 1  # last time step
    usr_index[0,2] = 1   # increment

    print 'number of timesteps=', ntimes

    #usr_index[0,0] = 1
    #usr_index[0,1] = 1
    #usr_index[0,2] = 1
    #usr_index[1,0] = 1
    #usr_index[1,1] = 1
    #usr_index[1,2] = 1
    #usr_index[2,0] = 1
    #usr_index[2,1] = 1
    #usr_index[2,2] = 1
    #usr_index[3,0] = 1
    #usr_index[3,1] = 1
    #usr_index[3,2] = 1
    #usr_index[4,0] = 1
    #usr_index[4,1] = 1
    #usr_index[4,2] = 1

    np.ascontiguousarray(usr_index, dtype=np.int32)

    usr_order = np.arange(0,6,dtype=np.int32).reshape(5)
    np.ascontiguousarray(usr_order, dtype=np.int32)

    #grp_name = 'map-const'
    #elm_name = 'THICK'
    grp_name = 'map-series'
    elm_name = 'U1'
    length = 302400

    error, buffer_res = nefis.getelt(fp, grp_name, elm_name, usr_index, usr_order, length)

    print('NEFIS error code (getels): %d' % error)
    if not error == 0:
        print("=========")
        error, err_string = nefis.neferr()
        print('    NEFIS error string       : %s' % err_string)
        print("=========")

    fmt = "%df" % (length/4)

    dims2 = elm_dimensions[0:elm_count][::-1]  # reverse dimensions (C vs Fortran ??)
    numbers = np.asarray(struct.unpack(fmt, buffer_res)).reshape( dims2 )  # unpack data into array
    # I don't know why, but variables come in in k,i,j order.  So fix this here
    numbers=np.transpose(numbers,(1,2,0))
    numbers = numbers[1:-1,1:-1,:] # trim ghost cells

    print
    print np.shape(numbers)
    print
    #-------------------------------------------------------------------------------
    print("---------")
    error = nefis.clsnef(fp)
    print('NEFIS error code (clsnef): %d' % error)
    print("---------")


    # indices are in i,j,k
    #print numbers[:,13,13]

    #print numbers[1,1,:]
    #print
    #print numbers[1,:,1]
    #print
    #print numbers[:,1,1]

    iplt=1
    if iplt == 1:
        import pylab as plt

        pltdata = np.transpose(numbers[:,:,12])
        cline = numbers[:,13,13]

        plt.subplot(211)
        plt.imshow(pltdata)

        plt.subplot(212)
        plt.plot(cline)

        plt.show()

if __name__ == "__main__":
    test_nefis_getelt_floats()

