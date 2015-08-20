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

        # populate a list of all groups and elements
        self.grp_list()
        self.elm_list()


    def __del__(self):
        print("---------")
        error = nefis.clsnef(self.fp)
        print('NEFIS error code (clsnef): %d' % error)
        print("---------")



    def grp_list(self):
        #print('Group listing')
        self.grplist=[]
        self.grp={}
        ngrp=0
        while True :
            if ngrp == 0:
                error, grp_name, cel_name, grp_count_dimensions, grp_dimensions, grp_order = nefis.inqfgr(self.fp)
            else:
                error, grp_name, cel_name, grp_count_dimensions, grp_dimensions, grp_order = nefis.inqngr(self.fp)

            if error == -6028: # no more groups to read
                return self.grplist
            elif not error == 0:  # some other error
                print 'error numb',error
                error, err_string = nefis.neferr()
                print('    NEFIS error string       : "%s"' % err_string)
                print('    =========')
                break
            else:
                ngrp+=1

            #print('    "%s"' % grp_name)
            self.grplist.append(grp_name)

            error, ntimes = nefis.inqmxi (self.fp, grp_name)

            self.grp[grp_name]={}
            self.grp[grp_name]['ntimes'] = ntimes


    def elm_list(self):
        nelm=0
        self.elmlist=[]
        self.elm={}
        while True :
            if nelm == 0:
                error, elm_name, elm_type, elm_quantity, elm_unit, elm_description, elm_single_bytes, elm_bytes, elm_count, elm_dimensions = nefis.inqfel(self.fp)
            else:
                error, elm_name, elm_type, elm_quantity, elm_unit, elm_description, elm_single_bytes, elm_bytes, elm_count, elm_dimensions = nefis.inqnel(self.fp)

            if error == -6024: # no more elements to read
                return self.elmlist
            elif not error == 0:  # some other error
                print 'error numb',error
                error, err_string = nefis.neferr()
                print('    NEFIS error string       : "%s"' % err_string)
                print('    =========')
                break
            else:
                nelm+=1

            #print('    "%s"' % grp_name)
            self.elmlist.append(elm_name)

            # define dictionaries for each element name
            self.elm[elm_name]={}
            self.elm[elm_name]['info']={}

            info = self.elm[elm_name]['info']

            info['type'] = elm_type
            info['unit'] = elm_unit
            info['desc'] = elm_description
            info['bytesize'] = elm_single_bytes
            info['bytes'] = elm_bytes
            info['ndim'] = elm_count
            info['dims'] = elm_dimensions[::-1]  # reverse dimensions (C vs Fortran ??)

            elm_grp = self.find_elm(elm_name)[0]
            info['group'] = elm_grp

            error, ntimes = nefis.inqmxi (self.fp, elm_grp)

            info['ntimes'] = ntimes

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


    def load_data(self, elm_name):

        elm =self.elm[elm_name]
        info = elm['info']

        grp_name = info['group']

        #-----------------------------------------------------------
        # Retrieve number of available timesteps
        #
        error, ntimes = nefis.inqmxi (self.fp, grp_name)
        if not error == 0:
            print("=========")
            error, err_string = nefis.neferr()
            print('    NEFIS error string       : %s' % err_string)
            print("=========")


        usr_index = np.zeros(15,dtype=np.int32).reshape(5,3)

        #FIXME currently I only extract the last time step, add itime to input variables

        ntimes = info['ntimes']
        usr_index[0,0] = 1  # first timestep
        usr_index[0,1] = ntimes  # last time step
        usr_index[0,2] = 1   # increment
        np.ascontiguousarray(usr_index, dtype=np.int32)

        length = info['bytes']*ntimes

        usr_order = np.arange(1,6,dtype=np.int32).reshape(5)
        np.ascontiguousarray(usr_order, dtype=np.int32)

        ## stuff below is necessary to read in data corectly if dimensions in 'info' have been reordered
        #error, elm_type, elm_single_byte, elm_quantity, elm_unit, elm_description, elm_count, elm_dimensions = nefis.inqelm(self.fp, elm_name)
        #info['dims'] = elm_dimensions  # just in case it's been reorganized anywhere

        error, buffer_res = nefis.getelt(self.fp, grp_name, elm_name, usr_index, usr_order, length)

        if not error == 0:
            print("=========")
            print('NEFIS error code (getels): %d' % error)
            error, err_string = nefis.neferr()
            print('    NEFIS error string       : %s' % err_string)
            print("=========")

        if ntimes > 1:
            dims = np.append(ntimes,info['dims']) # add time as a dimension
        else:
            dims = info['dims']

        if info['type'].strip() == 'REAL':
            if info['bytesize'] == 4:
                fmt = "%df" % (length/4)
            if info['bytesize'] == 8:
                fmt = "%dd" % (length/8)
            elm['data'] = np.asarray(struct.unpack(fmt, buffer_res)).reshape( dims )  # unpack data into array
        elif info['type'].strip() == 'INTEGER':
            if info['bytesize'] == 4:
                fmt = "%di" % (length/4)
            if info['bytesize'] == 8:
                fmt = "%dl" % (length/8)
            elm['data'] = np.asarray(struct.unpack(fmt, buffer_res)).reshape( dims )  # unpack data into array
        elif info['type'].strip() == 'CHARACTE':
            elm['data'] = buffer_res

        ## TODO -- determine if it makes sense to reorganize data into t,i,j,k ordera -- could cause problems
        #data = elm['data']
        #
        #if info['ndim'] == 3:
        #    if ntimes > 1:
        #        # dimensions are (t, k, i, j)
        #        data = np.transpose(data,(0,2,3,1))   # now it's t,i,j,k
        #        info['dims'] = info['dims'][[0,2,3,1]]  # update dims to match
        #    else:
        #        # dimensions are (k, i, j)
        #        data = np.transpose(data,(1,2,0))  # now it's i,j,k
        #        info['dims'] = info['dims'][[1,2,0]]  # update dims to match

    def loadifnot(self,var):
        if not var in self.elm.keys():
            print 'ERROR: ',vars,' does not exist'
            return

        if not 'data' in self.elm[var].keys():
            self.load_data(var)

    def get_data(self, elm_name):

        self.loadifnot(elm_name)
        return self.elm[elm_name]['data']

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


