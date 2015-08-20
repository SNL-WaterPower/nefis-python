import nefis
import numpy as np
import struct
import os, sys

class nef_data(object):
    def __init__(self,filebase, ac_type='r', coding=' '):

        #error, version = nefis.getnfv()
        #print('Library version: %s' % version[4:])
        #print('')

        print filebase
        self.dat_file=filebase+'.dat' 
        self.def_file=filebase+'.def' 

        if not os.path.isfile(self.dat_file):
            print
            print 'ERROR:  ' + self.dat_file + ' does not exist'
            print
            sys.exit(1)
            #exit()
        if not os.path.isfile(self.def_file):
            print
            print 'ERROR:  ' + self.def_file + ' does not exist'
            print
            sys.exit(1)
            #exit()
        
        print("---------")
        print(self.dat_file)
        print(self.def_file)
        print(coding)
        print(ac_type)
        print("---------")
        #-------------------------------------------------------------------------------
        self.fp = -1
        error, self.fp = nefis.crenef(self.dat_file, self.def_file, coding, ac_type)
        print('File set (should be zero): %d' % self.fp)
        print('NEFIS error code (crenef): %d' % error)
        print("---------")

    def __del__(self):
        print("---------")
        error = nefis.clsnef(self.fp)
        print('NEFIS error code (clsnef): %d' % error)
        print("---------")

    def grp_list(self):
        print('Group listing')
        ngrp=0
        while True :
            if ngrp == 0:
                error, grp_name, cel_name, grp_count_dimensions, grp_dimensions, grp_order = nefis.inqfgr(self.fp)
            else:
                error, grp_name, cel_name, grp_count_dimensions, grp_dimensions, grp_order = nefis.inqngr(self.fp)

            if error == -6028: # no more groups to read
                return
            elif not error == 0:  # some other error
                print 'error numb',error
                error, err_string = nefis.neferr()
                print('    NEFIS error string       : "%s"' % err_string)
                print('    =========')
                break
            else:
                ngrp+=1

            print('    "%s"' % grp_name)

    def grp_info(self,grp_name):
        error, cel_name, grp_count_dimensions, grp_dimensions, grp_order = nefis.inqgrp(self.fp, grp_name)
        if not error == 0:
            print 'error numb',error
            error, err_string = nefis.neferr()
            print('    NEFIS error string       : "%s"' % err_string)
            print('    =========')

        print('Grp defined    : "%s"' % grp_name)
        print('    Grp count  : "%d"' % grp_count_dimensions)
        print('    Dimensions : "%s"' % grp_dimensions)
        print('    Grp order  : "%s"' % grp_order)

        error, ntimes = nefis.inqmxi (self.fp, grp_name)
        print('    ntimes     : "%d"' % ntimes)
        self.cell_info(cel_name)

    def cell_info(self,cel_name):
        error, count, elm_names = nefis.inqcel(self.fp, cel_name)
        if not error == 0:
            print 'error numb',error
            error, err_string = nefis.neferr()
            print('    NEFIS error string       : "%s"' % err_string)
            print('    =========')

        print('    Cell name  : "%s"' % cel_name)
        print('        Elm Count    : "%d"' % count)

        for i in range(count):
            elm_name = elm_names[17*i:17*(i+1)]
            #print('Name %d: "%s"' % ( i, elm_name) )
            self.elm_info(elm_name)

    def elm_info(self,elm_name):

        error, elm_type, elm_single_byte, elm_quantity, elm_unit, elm_description, elm_count, elm_dimensions = nefis.inqelm(self.fp, elm_name)

        print '             Element    : ',elm_name
        print '                 description: ',elm_description
        print '                    type    : ',elm_type
        print '                 byte size  : ',elm_single_byte
        print '                 quantity   : ',elm_quantity
        print '                 units      : ',elm_unit
        print '                 dimensions : ',elm_dimensions
        print '                    size    : ',elm_count


    def file_info(self):
        ngrp=0
        while True :
            if ngrp == 0:
                error, grp_name, cel_name, grp_count_dimensions, grp_dimensions, grp_order = nefis.inqfgr(self.fp)
            else:
                error, grp_name, cel_name, grp_count_dimensions, grp_dimensions, grp_order = nefis.inqngr(self.fp)

            if error == -6028: # no more groups to read
                return
            elif not error == 0:  # some other error
                print 'error numb',error
                error, err_string = nefis.neferr()
                print('    NEFIS error string       : "%s"' % err_string)
                print('    =========')
                break
            else:
                ngrp+=1

            error, ntimes = nefis.inqmxi (self.fp, grp_name)

            print('Grp defined: "%s"' % grp_name)
            print('    Grp count  : "%d"' % grp_count_dimensions)
            print('    Dimensions : "%s"' % grp_dimensions)
            print('    Grp order  : "%s"' % grp_order)
            print('    ntimes     : "%d"' % ntimes)
            self.cell_info(cel_name)
       
    def find_elm(self,search_elm_name):
        ngrp=0
        while True :
            if ngrp == 0:
                error, grp_name, cel_name, grp_count_dimensions, grp_dimensions, grp_order = nefis.inqfgr(self.fp)
            else:
                error, grp_name, cel_name, grp_count_dimensions, grp_dimensions, grp_order = nefis.inqngr(self.fp)
            ngrp+=1

            if error == -6028: # no more groups to read
                return '', -1   # element not found

            error, count, elm_names = nefis.inqcel(self.fp, cel_name)
            for i in range(count):
                if search_elm_name.strip() == elm_names[17*i:17*(i+1)].strip():
                    return grp_name, i    # return group and element number

    def get_data(self, elm_name, grp_name=None, verbose=False):

        if grp_name == None :
            grp_name = self.find_elm(elm_name)[0]

        #-----------------------------------------------------------
        # Retrieve number of available timesteps
        #
        error, ntimes = nefis.inqmxi (self.fp, grp_name)
        if not error == 0:
            print("=========")
            error, err_string = nefis.neferr()
            print('    NEFIS error string       : %s' % err_string)
            print("=========")

        error, elm_type, elm_single_byte, elm_quantity, elm_unit, elm_description, elm_count, elm_dimensions = nefis.inqelm(self.fp, elm_name)

        if verbose:
            print elm_name,' description: ',elm_name
            print elm_name,'    type    : ',elm_type
            print elm_name,' byte size  : ',elm_single_byte
            print elm_name,' quantity   : ',elm_quantity
            print elm_name,' units      : ',elm_unit
            print elm_name,' dimensions : ',elm_dimensions
            print elm_name,'    size    : ',elm_count
            print elm_name,'  ntimes    : ',ntimes


        usr_index = np.zeros(15,dtype=np.int32).reshape(5,3)

        #FIXME currently I only extract the last time step, add itime to input variables

        usr_index[0,0] = ntimes  # first timestep
        usr_index[0,1] = ntimes  # last time step
        usr_index[0,2] = 1   # increment
        np.ascontiguousarray(usr_index, dtype=np.int32)

        length = elm_single_byte*(usr_index[0,1]-usr_index[0,0]+1)
        for dim in elm_dimensions:
            length *= dim

        usr_order = np.arange(1,6,dtype=np.int32).reshape(5)
        np.ascontiguousarray(usr_order, dtype=np.int32)

        error, buffer_res = nefis.getelt(self.fp, grp_name, elm_name, usr_index, usr_order, length)

        if not error == 0:
            print("=========")
            print('NEFIS error code (getels): %d' % error)
            error, err_string = nefis.neferr()
            print('    NEFIS error string       : %s' % err_string)
            print("=========")

        fmt = "%df" % (length/4)

        dims2 = elm_dimensions[0:elm_count][::-1]  # reverse dimensions (C vs Fortran ??)
        numbers = np.asarray(struct.unpack(fmt, buffer_res)).reshape( dims2 )  # unpack data into array

        #print
        #print np.shape(numbers)
        #print
        #-------------------------------------------------------------------------------

        # indices are in i,j,k
        #print numbers[:,13,13]

        #print numbers[1,1,:]
        #print
        #print numbers[1,:,1]
        #print
        #print numbers[:,1,1]

        return numbers

    def TreeInit(self,xvals,yvals,zvals):
        from scipy import spatial

        kmax=len(zvals[:,0,0])

        # copy x and y values to each k-layer
        xvals2=np.tile(xvals,(kmax,1,1))
        yvals2=np.tile(yvals,(kmax,1,1))

        self.tree = spatial.KDTree(zip(xvals2.ravel(), yvals2.ravel(),zvals.ravel()))
        self.idxshape = np.shape(zvals)

    def TreeLookup(self,pts):
        if not hasattr(self,'tree'):
            print 'tree not initialized'
            return

        dists, idxs = self.tree.query(pts)

        ijkdx = [np.unravel_index(ind,self.idxshape) for ind in idxs]

        return dists, ijkdx


def mnvel2xyvel(mvel,nvel,alpha):

    # convert alpha from degrees to radians
    rad = alpha[1:-1, 1:-1]*np.pi/180.0

    utilde = ( mvel[:, :-1, 1:-1] + mvel[:, 1:, 1:-1] ) / 2.0
    vtilde = ( nvel[:, 1:-1, :-1] + nvel[:, 1:-1, 1:] ) / 2.0

    uvel = utilde[:, :-1, :]*np.cos(rad) - vtilde[:, :, :-1]*np.sin(rad)
    vvel = utilde[:, :-1, :]*np.sin(rad) + vtilde[:, :, :-1]*np.cos(rad)

    return uvel, vvel
