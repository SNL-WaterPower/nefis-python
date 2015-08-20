import nefis
import numpy as np

def test_nefis_get_headers():
    #-------------------------------------------------------------------------------
    error, version = nefis.getnfv()
    print('')
    print('Library version: %s' % version[4:])
    print('')
    #-------------------------------------------------------------------------------
    #dat_file = 'trim-f34.dat'
    #def_file = 'trim-f34.def'
    dat_file = 'attributes.dat'
    def_file = 'attributes.def'
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
    if not error == 0:
        error, err_string = nefis.neferr()
        print('    NEFIS error string       : %s' % err_string)
        print("=========")
    #-------------------------------------------------------------------------------
    error, def_header = nefis.gethdf(fp)
    if not error == 0:
        error, err_string = nefis.neferr()
        print('    NEFIS error string       : %s' % err_string)
        print("=========")
    #-------------------------------------------------------------------------------
    error, dat_header = nefis.gethdt(fp)
    if not error == 0:
        error, err_string = nefis.neferr()
        print('    NEFIS error string       : %s' % err_string)
        print("=========")
    #-------------------------------------------------------------------------------
    print(def_header)
    print(dat_header)
    #-------------------------------------------------------------------------------
    print("---------")
    error = nefis.clsnef(fp)
    print('NEFIS error code (clsnef): %d' % error)
    print("---------")


if __name__ == "__main__":
    test_nefis_get_headers()
